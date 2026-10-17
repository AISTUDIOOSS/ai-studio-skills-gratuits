# Transcription verbatim par morceaux de parole (coupés aux blancs) : sur de petits morceaux, Whisper garde
# les reprises (« arrêtez de rêver parce que cette… Eh bien, arrêtez de rêver… ») qu'il fusionne sur la vidéo entière.
import json, sys, os, numpy as np, scipy.io.wavfile as wf, mlx_whisper
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
PROMPT = ("Euh, alors, euh... je, je vais, enfin, bref. Hum, du coup, en fait, voilà. "
          "Tu vois, euh, c'est, c'est vraiment... non, attends, je reprends.")
SEUIL_DB, PAUSE = -50.0, 0.45

def regions(db):
    parle = db > SEUIL_DB
    regs, i, n = [], 0, len(parle)
    while i < n:
        if parle[i]:
            j = i
            while j < n and parle[j]: j += 1
            regs.append([i * 0.005, j * 0.005]); i = j
        else:
            i += 1
    # fusion des trous courts, suppression des clics isolés
    out = []
    for r in regs:
        if out and r[0] - out[-1][1] < PAUSE: out[-1][1] = r[1]
        else: out.append(r)
    return [r for r in out if r[1] - r[0] > 0.12]

def decouper_long(r, db, maxi=14.0):
    if r[1] - r[0] <= maxi: return [r]
    a, b = int(r[0] / 0.005), int(r[1] / 0.005)
    mil = int((a + b) / 2); fen = int(4 / 0.005)
    zone = db[mil - fen:mil + fen]
    k = mil - fen + int(np.argmin(np.convolve(zone, np.ones(30) / 30, mode='same')))
    return decouper_long([r[0], k * 0.005], db, maxi) + decouper_long([k * 0.005, r[1]], db, maxi)

for clip in sys.argv[1:]:
    db = np.load(f'{W}/audio/{clip}-env.npy') if os.path.exists(f'{W}/audio/{clip}-env.npy') else None
    if db is None:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from couper import enveloppe; db = enveloppe(clip)
    sr, a = wf.read(f'{W}/audio/{clip}-16k.wav'); a = a.astype(np.float32) / 32768
    morceaux = [m for r in regions(db) for m in decouper_long(r, db)]
    segs = []
    for t0, t1 in morceaux:
        d, f = max(0, t0 - 0.2), min(len(a) / sr, t1 + 0.25)
        x = a[int(d * sr):int(f * sr)]
        r = mlx_whisper.transcribe(x, path_or_hf_repo='mlx-community/whisper-large-v3-mlx', language='fr',
                                   word_timestamps=True, initial_prompt=PROMPT,
                                   condition_on_previous_text=False, no_speech_threshold=0.5)
        for s in r['segments']:
            ws = [dict(w, start=round(d + w['start'], 3), end=round(d + w['end'], 3)) for w in s.get('words', [])]
            if not ws: continue
            texte = s['text'].strip()
            if texte and texte in PROMPT: continue          # Whisper qui recopie la consigne
            segs.append({'start': ws[0]['start'], 'end': ws[-1]['end'], 'text': texte, 'words': ws})
    json.dump(segs, open(f'{W}/transcription/{clip}.json', 'w'), ensure_ascii=False, indent=1)
    with open(f'{W}/transcription/{clip}.txt', 'w') as fo:
        for s in segs: fo.write(f"[{s['start']:7.2f} → {s['end']:7.2f}] {s['text']}\n")
    print('fini', clip, len(morceaux), 'morceaux', flush=True)
