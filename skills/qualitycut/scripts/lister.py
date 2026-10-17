# Liste lisible des mots alignés d'un rush : « n°:mot@début » ; une nouvelle ligne à chaque blanc > 0,35 s.
import json, sys, os
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
clip = sys.argv[1]
mots = json.load(open(f'{W}/transcription/{clip}-aligne.json'))
ligne, prev = [], None
for i, m in enumerate(mots):
    if prev is not None:
        blanc = m['debut'] - prev
        if blanc > 0.35:
            print(' '.join(ligne)); print(f'      ── blanc {blanc:.2f} s ──'); ligne = []
        elif blanc > 0.12:
            ligne.append(f'·{blanc:.2f}·')
    ligne.append(f"{i}:{m['texte']}@{m['debut']:.2f}")
    prev = m['fin']
print(' '.join(ligne))
