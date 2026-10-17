# Contrôle : dans chaque passage gardé, les blancs retirés contiennent-ils de la parole non transcrite ?
import json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from couper import enveloppe, lire_choix, SEUIL_DB, SEUIL_BLANC, W
clip = sys.argv[1]
mots = json.load(open(f'{W}/transcription/{clip}-aligne.json')); db = enveloppe(clip)
for a, b in lire_choix(clip):
    for i in range(a + 1, b + 1):
        g0, g1 = mots[i - 1]['fin'], mots[i]['debut']
        if g1 - g0 > SEUIL_BLANC:
            seg = db[int(g0 / 0.005):int(g1 / 0.005)]
            actif = float(np.mean(seg > SEUIL_DB)) if len(seg) else 0
            flag = '  <<< parole ?' if actif > 0.35 else ''
            print(f"{i-1}:{mots[i-1]['texte']} | {i}:{mots[i]['texte']}  blanc {g1-g0:.2f}s  actif {actif:.0%}{flag}")
