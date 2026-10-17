# Inspecte une zone d'un rush : profil du son (une colonne = 20 ms) + transcription de la zone seule.
import sys, os, numpy as np, scipy.io.wavfile as wf, mlx_whisper, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from couper import enveloppe, W
clip = sys.argv[1]; zones = [(float(a), float(b)) for a, b in (z.split('-') for z in sys.argv[2:])]
db = enveloppe(clip); sr, a = wf.read(f'{W}/audio/{clip}-16k.wav'); a = a.astype(np.float32) / 32768
mots = json.load(open(f'{W}/transcription/{clip}-aligne.json'))
for t0, t1 in zones:
    prof = ''.join(' .:-=+*#%@'[min(9, max(0, int((np.mean(db[int(t/0.005):int(t/0.005)+4]) + 65) / 5)))]
                   for t in np.arange(t0, t1, 0.02))
    print(f'--- {t0:.2f}-{t1:.2f}  |{prof}|')
    print('   mots alignés :', ' '.join(f"{m['texte']}@{m['debut']:.2f}-{m['fin']:.2f}" for m in mots if m['fin'] > t0 and m['debut'] < t1))
    r = mlx_whisper.transcribe(a[int(t0*sr):int(t1*sr)], path_or_hf_repo='mlx-community/whisper-large-v3-mlx', language='fr',
                               word_timestamps=True, initial_prompt="Euh, alors, euh... je, je vais, enfin, bref.",
                               condition_on_previous_text=False)
    print('   whisper zone :', ' '.join(f"{w['word'].strip()}@{t0+w['start']:.2f}" for s in r['segments'] for w in s.get('words', [])))
