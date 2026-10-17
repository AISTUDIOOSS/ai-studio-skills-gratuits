#!/usr/bin/env python3
"""Sorties de la coupe pour la suite de la chaîne (à lancer après couper.py, à 30 i/s).
  montage/<rush>-plans.txt     : plans gardés en secondes (début, fin, durée, texte)
  montage/<rush>-cuts.json     : contrat `cuts` du moteur Steve 01 (images entières à 30 i/s, début inclus, fin exclue)
  montage/<rush>-analysis-minimale.json : contrat `analysis` minimal (mots + un sous-titre simple par bloc de 2 mots) pour
                                 enchaîner tout de suite avec `from-source` ; le vrai plan de sous-titres reste à faire
  montage/<rush>-rapport.md    : durée avant/après, nombre de coupes, blancs aux coupes, points à écouter
Règle : la COUPE ne bouge jamais. Si un bord tombe dans la fin alignée d'un mot, c'est le mot qui est recalé dans son plan
(le moteur refuse un mot traversé) et il est listé dans le rapport.
usage : MONTAGE_DOSSIER=<dossier> python3 exporter_cuts.py <rush>"""
import json, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from couper import enveloppe, W
rush = sys.argv[1]
cp = json.load(open(f'{W}/montage/{rush}-coupes.json'))
if abs(cp['fps'] - 30) > 1e-6: sys.exit('Les coupes ne sont pas à 30 i/s : relancer couper.py avec MONTAGE_FPS=30 sur la source mise au format.')
segs = cp['segments']; mots = json.load(open(f'{W}/transcription/{rush}-aligne.json')); db = enveloppe(rush); PAS = 0.005
corr = {}
if os.path.exists(f'{W}/montage/{rush}-texte.json'): corr = {int(k): v for k, v in json.load(open(f'{W}/montage/{rush}-texte.json')).items()}
src = f'{W}/sources/{rush}.mov'; n_src = None
if os.path.exists(src):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip()
    n_src = int(r) if r.isdigit() else None
if n_src is None: n_src = int(round(len(db) * PAS * 30))
for s in segs: s['out'] = min(s['out'], n_src)
i_ = lambda t: max(0, int(round(t / PAS)))
# 1. mots en images, recalés (gardé -> dans son plan ; retiré -> dehors)
W_, recales = [], []
for k, m in enumerate(mots):
    s0 = int(round(m['debut'] * 30)); e0 = max(s0 + 1, int(round(m['fin'] * 30)))
    seg = next((g for g in segs if g['mots'][0] <= k <= g['mots'][1]), None); s1, e1 = s0, e0
    if seg:
        s1, e1 = max(s0, seg['in']), min(e0, seg['out'])
        if e1 <= s1: s1 = min(max(s0, seg['in']), seg['out'] - 1); e1 = s1 + 1
        if (s1, e1) != (s0, e0): recales.append((k, m['texte'], (s1 - s0) + (e0 - e1), seg['in'] / 30))
    else:
        for g in segs:
            if s1 < g['out'] and e1 > g['in']:
                if s1 < g['in']: e1 = min(e1, g['in'])
                else: s1 = max(s1, g['out'])
        if e1 <= s1: e1 = s1 + 1
    W_.append({'k': k, 'brut': corr.get(k, m['texte']), 's': s1, 'e': e1, 'seg': seg})
for i in range(1, len(W_)):
    if W_[i]['s'] <= W_[i - 1]['s']: W_[i]['s'] = W_[i - 1]['s'] + 1
    if W_[i]['e'] <= W_[i]['s']: W_[i]['e'] = W_[i]['s'] + 1
for i in range(len(W_) - 1):
    if W_[i]['e'] > W_[i + 1]['s']: W_[i]['e'] = max(W_[i]['s'] + 1, W_[i + 1]['s'])
def affiche(t):
    t = t.replace("'", '’').replace('...', ' ').lower()
    t = re.sub(r'[^\w’\- ]', '', t).strip(' -’')
    return re.sub(r'\b(\d{1,3})(\d{3})\b', '\\1\u202f\\2', t)
words = []
for w in W_:
    b = w['brut']
    if not b: continue
    if words and (b.startswith("'") or b.startswith('-')) and words[-1]['seg'] is w['seg']:
        words[-1]['brut'] += b; words[-1]['endFrame'] = w['e']
    else: words.append({'brut': b, 'startFrame': w['s'], 'endFrame': w['e'], 'seg': w['seg']})
words = [w for w in words if affiche(w['brut'])]
for i, w in enumerate(words): w['id'] = f'w{i}'; w['text'] = affiche(w['brut'])
# contrôle identique à la règle du moteur : aucun mot traversé par une coupe
for w in words:
    for g in segs:
        if w['startFrame'] < g['out'] and w['endFrame'] > g['in'] and (w['startFrame'] < g['in'] or w['endFrame'] > g['out']):
            sys.exit(f"mot traversé (ne devrait pas arriver) : {w['text']} {w['startFrame']}-{w['endFrame']} / plan {g['in']}-{g['out']}")
# 2. sous-titres minimaux : blocs de 2 mots au plus, un groupe « small-white » par bloc, jamais à cheval sur deux plans
groups, cur = [], []
def ferme():
    global cur
    if cur: groups.append({'id': f'g{len(groups)}', 'template': 'small-white', 'parts': [{'wordIds': [x['id'] for x in cur]}]}); cur = []
for w in words:
    fin = bool(re.search(r'[.,;:!?…]$', w['brut']))
    if cur and (cur[-1]['seg'] is not w['seg'] or len(cur) >= 2 or len(' '.join(x['text'] for x in cur + [w]).split()) > 2): ferme()
    cur.append(w)
    if fin: ferme()
ferme()
M = f'{W}/montage/{rush}'
json.dump({'segments': [{'startFrame': s['in'], 'endFrame': s['out']} for s in segs]}, open(f'{M}-cuts.json', 'w'), indent=1)
json.dump({'sourceFrames': n_src, 'fps': 30, 'words': [{k: w[k] for k in ('id', 'text', 'startFrame', 'endFrame')} for w in words], 'groups': groups},
          open(f'{M}-analysis-minimale.json', 'w'), ensure_ascii=False, indent=1)
with open(f'{M}-plans.txt', 'w') as f:
    f.write(f'# {rush} — plans gardés (secondes dans la source mise au format, 30 i/s)\n# n°   début     fin    durée  texte\n')
    for n, s in enumerate(segs, 1):
        f.write(f"{n:3d} {s['in']/30:8.3f} {s['out']/30:8.3f} {(s['out']-s['in'])/30:6.2f}  {s.get('texte', '')}\n")
# 3. mesures
blancs, sur_son = [], []
for a, b in zip(segs, segs[1:]):
    k = i_(a['out'] / 30); j = k
    while j > i_(a['in'] / 30) and db[j - 1] <= -45: j -= 1
    fin = (k - j) * PAS; k = i_(b['in'] / 30); j = k
    while j < i_(b['out'] / 30) and db[j] <= -50: j += 1
    blancs.append(fin + (j - k) * PAS)
    v1 = float(db[max(0, i_(a['out'] / 30) - 2):i_(a['out'] / 30)].max()); v2 = float(db[i_(b['in'] / 30):i_(b['in'] / 30) + 2].max())
    if max(v1, v2) > -45: sur_son.append((a['out'] / 30, b['in'] / 30, v1, v2, a.get('texte', '')[-30:], b.get('texte', '')[:30]))
total = sum(s['out'] - s['in'] for s in segs) / 30; courts = [s for s in segs if (s['out'] - s['in']) / 30 < 0.45]
with open(f'{M}-rapport.md', 'w') as f:
    f.write(f"# Rapport de coupe — {rush}\n\n")
    f.write(f"- Durée : {n_src/30:.1f} s → **{total:.1f} s** ; {len(segs)} plans, {len(segs)-1} coupes (une toutes les {total/max(1,len(segs)-1):.1f} s).\n")
    if blancs: f.write(f"- Blanc à une coupe : moyenne **{np.mean(blancs):.3f} s**, maximum **{max(blancs):.3f} s** ; coupes au-dessus de 0,18 s : {sum(1 for x in blancs if x > 0.18)} (repère : ~0,09 s en moyenne avant resserrage, ~0,05 s après ; jamais plus de 0,18 s).\n")
    f.write(f"- Plans de moins de 0,45 s : {len(courts)}.\n- Mots recalés dans leur plan pour le moteur (la coupe n'a pas bougé) : {len(recales)}.\n")
    f.write("\n## Points à écouter\n")
    for o, i2, v1, v2, t1, t2 in sur_son: f.write(f"- raccord {o:.2f} s → {i2:.2f} s posé sur du son ({v1:.0f} / {v2:.0f} dB) : « …{t1} » | « {t2}… »\n")
    for k, t, n, t0 in recales:
        if n >= 2: f.write(f"- « {t} » (mot n° {k}) : le bord coupe {n} images dans sa fin ou son début alignés — vérifier que le mot est entier.\n")
    for s in courts: f.write(f"- plan très court ({(s['out']-s['in'])/30:.2f} s) à {s['in']/30:.2f} s : « {s.get('texte','')} »\n")
    if not (sur_son or courts or any(n >= 2 for _, _, n, _ in recales)): f.write("- aucun point mesuré ; l'écoute de chaque raccord reste à faire.\n")
    f.write("\nRappel : ces mesures ne valent pas une écoute. Lancer verifier.py (re-transcription du montage) puis écouter chaque raccord.\n")
print(f"{rush} : {len(segs)} plans, {total:.1f} s ; blanc moyen {np.mean(blancs):.3f} s, max {max(blancs):.3f} s ; cuts.json, analysis-minimale.json, plans.txt, rapport.md écrits dans {W}/montage/")
