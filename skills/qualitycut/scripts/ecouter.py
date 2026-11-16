# Réécoute (transcription) des blancs suspects : que dit-on dans un blanc où le son est actif ?
import json, sys, os, numpy as np, scipy.io.wavfile as wf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from couper import enveloppe, lire_choix, SEUIL_DB, SEUIL_BLANC, W
import scribe
clip = sys.argv[1]
mots = json.load(open(f'{W}/transcription/{clip}-aligne.json')); db = enveloppe(clip)
sr, a = wf.read(f'{W}/audio/{clip}-16k.wav'); a = a.astype(np.float32) / 32768
for d, f in lire_choix(clip):
    for i in range(d + 1, f + 1):
        g0, g1 = mots[i - 1]['fin'], mots[i]['debut']
        if g1 - g0 <= SEUIL_BLANC: continue
        seg = db[int(g0 / 0.005):int(g1 / 0.005)]
        if not len(seg) or np.mean(seg > SEUIL_DB) <= 0.35: continue
        t0, t1 = max(0, mots[i - 1]['debut'] - 0.6), mots[i]['fin'] + 0.6
        x = a[int(t0 * sr):int(t1 * sr)]
        ws = [f"{w['word'].strip()}@{w['start']:.2f}" for s in scribe.transcrire(x, sr, decalage=t0) for w in s['words']]
        print(f"[{i-1}:{mots[i-1]['texte']} → {i}:{mots[i]['texte']}] blanc {g0:.2f}-{g1:.2f} : {' '.join(ws)}")
