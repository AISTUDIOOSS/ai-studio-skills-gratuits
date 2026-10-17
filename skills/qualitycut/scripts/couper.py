# Transforme le choix des passages gardés (montage/<rush>.txt) en coupes précises à l'image près (MONTAGE_FPS, 30 i/s par défaut : source mise au format).
# Règles : chaque passage démarre juste avant l'attaque du premier mot (aucun blanc), finit juste après la
# retombée du dernier mot ; tout blanc > SEUIL à l'intérieur d'un passage est retiré (coupe franche, comme
# dans les montages de Steeve du 04/10 : une coupe toutes les ~3 s, aucun blanc gardé).
import json, sys, os, re, math
import numpy as np, scipy.io.wavfile as wf

W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
FPS = float(os.environ.get("MONTAGE_FPS", 30))
IMG = 1 / FPS
SEUIL_BLANC = 0.22      # blanc retiré à l'intérieur d'un passage
AVANT = 0.010           # marge minimale avant l'attaque (0,020 jusqu'au 05/10)
APRES = 0.010           # marge après la retombée de la voix (0,045 jusqu'au 05/10)
SEUIL_DB = -50.0        # au-dessus = on parle (bruit de fond ~ -65 dB)
# Fin de phrase (Steeve, 05/10 : « un poil trop d'attente sur la coupure des fins de phrases ») : la voix est finie
# quand elle reste sous SEUIL_FIN pendant TENUE ; la traîne et le souffle de fin de mot en dessous sont coupés.
# TENUE évite de couper dans l'occlusion d'un « p » ou d'un « t » final, avant son explosion.
SEUIL_FIN = -45.0
TENUE = 0.060
# Prise de son bruyante (07/10 : C0218 au micro de la caméra, bruit des pauses à -32 dB ; C0219 à -42 dB) : sous les
# seuils fixes, la voix ne « retombe » jamais et les coupes se font au jugé. Les seuils remontent alors juste au-dessus
# du bruit mesuré dans les pauses (80e centile + 1 dB / + 2 dB) ; une prise propre (-58 dB) garde -50 / -45 dB.
SEUILS_FIXES = (SEUIL_DB, SEUIL_FIN)

def seuils_adaptes(clip, db):
    mots = json.load(open(f'{W}/transcription/{clip}-aligne.json'))
    pauses = [db[_i(m['fin'] + 0.12):_i(n['debut'] - 0.12)] for m, n in zip(mots, mots[1:]) if n['debut'] - m['fin'] > 0.54]
    if not pauses:
        return SEUILS_FIXES
    bruit = float(np.percentile(np.concatenate(pauses), 80))
    return max(SEUILS_FIXES[0], bruit + 1.0), max(SEUILS_FIXES[1], bruit + 2.0)

def enveloppe(clip):
    cache = f'{W}/audio/{clip}-env.npy'
    if os.path.exists(cache):
        return np.load(cache)
    sr, a = wf.read(f'{W}/audio/{clip}-48k.wav')
    x = a[:, 0].astype(np.float32) / 32768
    hop, win = int(0.005 * sr), int(0.010 * sr)
    n = (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    db = 20 * np.log10(np.sqrt(np.mean(x[idx] ** 2, axis=1) + 1e-12))
    np.save(cache, db)
    return db

def t2i(t): return max(0, int(round(t / 0.005)))

def _i(t): return max(0, int(round(t / 0.005)))

def _i(t): return max(0, int(round(t / 0.005)))

def attaque(db, t_mot, t_min):
    """Début de la parole pour un mot aligné à t_mot : dernier passage sous le seuil avant le mot (fenêtre
    [t_min, t_mot]) ; si la parole est continue, le creux d'énergie juste avant le mot."""
    # fenêtre arrêtée au début aligné (et non +0,05 s, jusqu'au 07/10) : sur une prise bruyante, l'occlusion d'un « t »
    # juste après l'attaque (« Steeve ») passe sous le seuil et faisait démarrer le plan dans le mot.
    a, b = _i(max(t_min, t_mot - 0.30)), _i(t_mot)
    bas = [k for k in range(a, b) if db[k] <= SEUIL_DB]
    if bas:
        k = bas[-1] + 1
        return min(k, _i(t_mot)) * 0.005 if k <= b else t_mot
    c, d = _i(max(t_min, t_mot - 0.12)), _i(t_mot + 0.02)
    lis = np.convolve(db, np.ones(3) / 3, mode='same')
    return (c + int(np.argmin(lis[c:d + 1]))) * 0.005 if d > c else t_mot

def retombee(db, t_mot, t_max, t_debut=None, seuil=None, tenue=TENUE):
    """Fin de la parole pour un mot qui finit à t_mot : premier instant après le mot (fenêtre [t_mot-0,05, t_max])
    où le son reste sous le seuil pendant `tenue` ; si l'alignement déborde déjà sur le silence (fin de mot
    alignée trop tard), on recule jusqu'à la vraie fin de la voix, sans entrer dans les 0,06 s du début du mot ;
    si la parole continue (mot suivant collé), le creux d'énergie juste après le mot."""
    seuil = SEUIL_FIN if seuil is None else seuil
    n = max(1, round(tenue / 0.005))
    a, b = _i(t_mot - 0.05), _i(min(t_max, t_mot + 0.30))
    for k in range(a, b):
        if db[k:k + n].max() <= seuil:
            if k == a and t_debut is not None:
                plancher, j = _i(t_debut + 0.06), k
                while j > plancher and db[j - 1] <= seuil: j -= 1
                if j > plancher:
                    return j * 0.005
            return max(k, _i(t_mot - 0.02)) * 0.005
    c, d = _i(t_mot - 0.02), _i(min(t_max, t_mot + 0.12))
    lis = np.convolve(db, np.ones(3) / 3, mode='same')
    return (c + int(np.argmin(lis[c:d + 1]))) * 0.005 if d > c else t_mot

def lire_choix(clip):
    gardes = []
    for ligne in open(f'{W}/montage/{clip}.txt'):
        ligne = ligne.split('#')[0].strip()
        m = re.match(r'(\d+)\s*-\s*(\d+)', ligne)
        if m:
            gardes.append((int(m.group(1)), int(m.group(2))))
    return gardes

def son_suivant(db, t, maxi=1.0, seuil=None):
    """Instant où le son repasse au-dessus du seuil après t (début du prochain bruit/mot)."""
    seuil = SEUIL_DB if seuil is None else seuil
    k = _i(t)
    while k < min(len(db) - 1, _i(t + maxi)) and db[k] <= seuil: k += 1
    return k * 0.005

def son_precedent(db, t, maxi=1.0):
    """Instant où le son est passé sous le seuil avant t (fin du bruit/mot précédent)."""
    k = _i(t)
    while k > max(0, _i(t - maxi)) and db[k - 1] <= SEUIL_DB: k -= 1
    return k * 0.005

def borne_sortie(db, off):
    """Image de sortie : off + marge, sans mordre sur le son suivant ; creux trop court → image la plus proche."""
    if db[min(len(db) - 1, _i(off))] > SEUIL_FIN:         # parole continue : on coupe dans le creux
        return round(off / IMG)
    z1 = son_suivant(db, off, seuil=SEUIL_FIN)
    i = math.ceil((off + APRES) / IMG)
    if i * IMG > z1 - 0.005:
        i = math.floor((z1 - 0.005) / IMG)
        if i * IMG < off - 0.01:
            i = round(((off + z1) / 2) / IMG)
    return i

def borne_entree(db, on):
    """Image d'entrée : on - marge, sans reprendre la fin du son précédent ; creux trop court → image la plus proche."""
    if db[max(0, _i(on) - 1)] > SEUIL_DB:                 # parole continue : on coupe dans le creux
        return round(on / IMG)
    y0 = son_precedent(db, on)
    i = math.floor((on - AVANT) / IMG)
    if i * IMG < y0 + 0.005:
        i = math.ceil((y0 + 0.005) / IMG)
        if i * IMG > on + 0.01:
            i = round(((y0 + on) / 2) / IMG)
    return i

def couper(clip):
    mots = json.load(open(f'{W}/transcription/{clip}-aligne.json'))
    db = enveloppe(clip)
    global SEUIL_DB, SEUIL_FIN
    SEUIL_DB, SEUIL_FIN = seuils_adaptes(clip, db)
    if (SEUIL_DB, SEUIL_FIN) != SEUILS_FIXES:
        print(f'{clip} : prise bruyante, seuils {SEUIL_DB:.1f} / {SEUIL_FIN:.1f} dB')
    duree = len(db) * 0.005
    segments = []
    for a, b in lire_choix(clip):
        morceaux, cur = [], [a]
        for i in range(a + 1, b + 1):
            if mots[i]['debut'] - mots[i - 1]['fin'] > SEUIL_BLANC:
                cur.append(i - 1); morceaux.append(cur); cur = [i]
        cur.append(b); morceaux.append(cur)
        for d, f in morceaux:
            t_avant = mots[d - 1]['fin'] if d > 0 else 0.0
            t_apres = mots[f + 1]['debut'] if f + 1 < len(mots) else duree
            on = attaque(db, mots[d]['debut'], t_avant)
            off = retombee(db, mots[f]['fin'], t_apres, t_debut=mots[f]['debut'])
            segments.append({'in': borne_entree(db, on), 'out': borne_sortie(db, off), 'mots': [d, f],
                             'texte': ' '.join(m['texte'] for m in mots[d:f + 1])})
    # Dernier plan : même fin acoustique que les autres, sans rallonge.
    # La revue du résultat doit aussi vérifier le geste de fin de prise à l'image.
    # deux morceaux qui se touchent ou se chevauchent dans le rush = un seul
    fus = []
    for s in segments:
        if fus and s['in'] <= fus[-1]['out'] and s['mots'][0] == fus[-1]['mots'][1] + 1:
            fus[-1]['out'] = max(fus[-1]['out'], s['out']); fus[-1]['mots'][1] = s['mots'][1]
            fus[-1]['texte'] += ' ' + s['texte']
        else:
            fus.append(s)
    total = sum(s['out'] - s['in'] for s in fus) / FPS
    json.dump({'rush': clip, 'fps': FPS, 'seuils': [round(SEUIL_DB, 1), round(SEUIL_FIN, 1)], 'segments': fus}, open(f'{W}/montage/{clip}-coupes.json', 'w'),
              ensure_ascii=False, indent=1)
    print(f'{clip} : {len(fus)} plans, durée {total:.1f} s')
    return fus

if __name__ == '__main__':
    for c in sys.argv[1:]:
        couper(c)
