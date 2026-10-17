# Complète la transcription : toute zone où l'on parle (énergie) sans mot reconnu est retranscrite en petites
# fenêtres, puis ajoutée aux segments (il faut ensuite réaligner avec moteur/aligner.py).
import json, sys, os, numpy as np, scipy.io.wavfile as wf, mlx_whisper
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from couper import enveloppe, SEUIL_DB
PROMPT = "Euh, alors, euh... je, je vais, enfin, bref. Hum, du coup, en fait, voilà."

def zones_oubliees(clip):
    mots = json.load(open(f'{W}/transcription/{clip}-aligne.json')); db = enveloppe(clip)
    bornes = [(0.0, mots[0]['debut'])] + [(mots[i]['fin'], mots[i + 1]['debut']) for i in range(len(mots) - 1)] \
             + [(mots[-1]['fin'], len(db) * 0.005)]
    out = []
    for a, b in bornes:
        if b - a < 0.8: continue
        seg = db[int(a / 0.005):int(b / 0.005)]
        if np.mean(seg > SEUIL_DB) > 0.30 and np.sum(seg > SEUIL_DB) * 0.005 > 0.5:
            out.append((a, b))
    return out

def fenetres(a, b, db, maxi=6.0):
    if b - a <= maxi: return [(a, b)]
    i0, i1 = int((a + 2) / 0.005), int((b - 2) / 0.005)
    lis = np.convolve(db, np.ones(20) / 20, mode='same')
    k = i0 + int(np.argmin(lis[i0:i1])); m = k * 0.005
    return fenetres(a, m, db, maxi) + fenetres(m, b, db, maxi)

def signaler_candidats(clip):
    """Signaler aussi les sons courts sans les insérer automatiquement dans le texte."""
    mots = json.load(open(f'{W}/transcription/{clip}-aligne.json'))
    db = enveloppe(clip)
    bornes = [(0.0, mots[0]['debut'])] + [(a['fin'], b['debut']) for a, b in zip(mots, mots[1:])] + [(mots[-1]['fin'], len(db)*0.005)]
    candidats = []
    for a, b in bornes:
        if b-a < 0.12:
            continue
        seg = db[int(a/0.005):int(b/0.005)]
        actif = float(np.sum(seg > SEUIL_DB)*0.005)
        ratio = float(np.mean(seg > SEUIL_DB)) if len(seg) else 0.0
        if actif >= 0.06 and ratio >= 0.20:
            candidats.append({'debut': a, 'fin': b, 'sonActifSecondes': round(actif, 3),
                              'ratioActif': round(ratio, 3), 'statut': 'a_examiner'})
    dest = f'{W}/transcription/{clip}-zones-a-revoir.json'
    json.dump(candidats, open(dest, 'w'), ensure_ascii=False, indent=2)
    print(clip, len(candidats), 'zones sonores à examiner (pas une détection certaine de parole)', flush=True)
    return candidats


def main():
    signal_only = '--signaler-seulement' in sys.argv[1:]
    for clip in (arg for arg in sys.argv[1:] if arg != '--signaler-seulement'):
        signaler_candidats(clip)
        if signal_only:
            continue
        db = enveloppe(clip)
        sr, x = wf.read(f'{W}/audio/{clip}-16k.wav'); x = x.astype(np.float32) / 32768
        segs = json.load(open(f'{W}/transcription/{clip}.json'))
        ajout = 0
        for a, b in zones_oubliees(clip):
            for d, f in fenetres(a, b, db):
                d0, f0 = max(0, d - 0.15), min(len(x) / sr, f + 0.15)
                r = mlx_whisper.transcribe(x[int(d0 * sr):int(f0 * sr)], path_or_hf_repo='mlx-community/whisper-large-v3-mlx',
                                           language='fr', word_timestamps=True, initial_prompt=PROMPT,
                                           condition_on_previous_text=False)
                for s in r['segments']:
                    ws = [dict(w, start=round(d0 + w['start'], 3), end=round(d0 + w['end'], 3)) for w in s.get('words', [])
                          if d - 0.1 <= d0 + w['start'] <= f + 0.1]
                    if not ws or s['text'].strip() in PROMPT: continue
                    segs.append({'start': ws[0]['start'], 'end': ws[-1]['end'], 'text': ' '.join(w['word'].strip() for w in ws),
                                 'words': ws, 'complement': True})
                    ajout += len(ws)
                    print(f"  {clip} {d0:6.2f}-{f0:6.2f} : {' '.join(w['word'].strip() for w in ws)}", flush=True)
        segs.sort(key=lambda s: s['start'])
        json.dump(segs, open(f'{W}/transcription/{clip}.json', 'w'), ensure_ascii=False, indent=1)
        print(clip, 'mots ajoutés :', ajout, flush=True)


if __name__ == '__main__':
    main()
