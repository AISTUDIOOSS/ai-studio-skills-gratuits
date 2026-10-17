# Contrôle d'un montage par le son : on assemble le son des plans, on le retranscrit (par morceaux, comme pour
# les rushes) et on compare au texte attendu. Écarts = reprise restée, mot coupé, « euh » oublié.
import json, sys, os, re, difflib, unicodedata, numpy as np, scipy.io.wavfile as wf, mlx_whisper
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PROMPT = "Euh, alors, euh... je, je vais, enfin, bref. Hum, du coup, en fait, voilà."

def norm(t):
    t = unicodedata.normalize('NFKD', t.lower()); t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", t.replace('’', "'"))

clip = sys.argv[1]
cp = json.load(open(f'{W}/montage/{clip}-coupes.json')); fps = cp['fps']
mots = json.load(open(f'{W}/transcription/{clip}-aligne.json'))
sr, a = wf.read(f'{W}/audio/{clip}-48k.wav'); a = a[:, 0].astype(np.float32) / 32768
parts, jonctions, t = [], [], 0.0
for s in cp['segments']:
    x = a[int(s['in'] / fps * sr):int(s['out'] / fps * sr)].copy()
    parts.append(x); t += len(x) / sr; jonctions.append(t)
y = np.concatenate(parts)
os.makedirs(f'{W}/controle', exist_ok=True)
wf.write(f'{W}/controle/{clip}-montage.wav', sr, (y * 32767).astype(np.int16))
# saut d'amplitude aux jonctions (risque de clic)
sauts = []
for k, s in enumerate(cp['segments'][:-1]):
    o = int(s['out'] / fps * sr); i2 = int(cp['segments'][k + 1]['in'] / fps * sr)
    r1 = np.sqrt(np.mean(a[o - 240:o] ** 2)); r2 = np.sqrt(np.mean(a[i2:i2 + 240] ** 2))
    sauts.append((k, 20 * np.log10(r1 + 1e-9), 20 * np.log10(r2 + 1e-9)))
# retranscription par morceaux de 20 s environ, coupés dans les jonctions
y16 = y[::3]
bornes, debut = [], 0.0
for j in jonctions:
    if j - debut > 9: bornes.append((debut, j)); debut = j
bornes.append((debut, len(y16) / 16000))
texte = []
for d, f in bornes:
    x = y16[int(d * 16000):int(f * 16000)]
    r = mlx_whisper.transcribe(x, path_or_hf_repo='mlx-community/whisper-large-v3-mlx',
                               language='fr', initial_prompt=PROMPT, condition_on_previous_text=False)
    tx = r['text'].strip(); ws = tx.split()
    if ws and len(set(ws)) < 0.4 * len(ws):          # boucle de Whisper (« Ah Ah Ah… ») : on refait sans consigne
        tx = mlx_whisper.transcribe(x, path_or_hf_repo='mlx-community/whisper-large-v3-mlx', language='fr',
                                    condition_on_previous_text=False)['text'].strip()
    texte.append(tx)
entendu = ' '.join(texte)
attendu = ' '.join(m['texte'] for s in cp['segments'] for m in mots[s['mots'][0]:s['mots'][1] + 1])
A, E = norm(attendu), norm(entendu)
print('DURÉE', round(len(y) / sr, 1), 's —', len(cp['segments']), 'plans')
print('ENTENDU :', entendu)
print('ÉCARTS (attendu → entendu) :')
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, E, autojunk=False).get_opcodes():
    if op != 'equal':
        print(f"  {op:8s} « {' '.join(A[i1:i2])} » → « {' '.join(E[j1:j2])} »")
print('JONCTIONS SUR DU SON (clic possible) :')
for k, p, q in sauts:
    if max(p, q) > -45:
        s1, s2 = cp['segments'][k], cp['segments'][k + 1]
        print(f"  plan {k}: fin {s1['out']/fps:.2f}s ({p:.0f} dB) « …{s1['texte'][-40:]} » | début {s2['in']/fps:.2f}s ({q:.0f} dB) « {s2['texte'][:40]}… »")
