# 1re passe avec ElevenLabs Scribe (vidéo entière) : mots plus justes que Whisper et pas d'hallucination de fin.
# Sortie au format des segments Whisper (transcription/RUSH.json + .txt) ; événements sonores à part (RUSH-evenements.json).
# Clé : variable ELEVENLABS_API_KEY ou fichier ~/.config/elevenlabs/key (jamais affichée).
# Tout ou rien : si la clé manque ou qu'un rush échoue, rien n'est laissé et le code de sortie vaut 1 → preparer.sh repasse sur Whisper.
import json, math, os, subprocess, sys
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
FIN_PHRASE, PAUSE, MAX_MOTS = '.?!…', 1.0, 30

def cle():
    k = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    f = os.path.expanduser('~/.config/elevenlabs/key')
    if not k and os.path.exists(f): k = open(f).read().strip()
    return k

def scribe(wav, k):
    for model in ('scribe_v2', 'scribe_v1'):
        r = subprocess.run(['curl', '-sS', '--max-time', '600', '-w', '\n%{http_code}', 'https://api.elevenlabs.io/v1/speech-to-text',
                            '-H', f'xi-api-key: {k}', '-F', f'file=@{wav}', '-F', f'model_id={model}',
                            '-F', 'language_code=fra', '-F', 'tag_audio_events=true',
                            '-F', 'timestamps_granularity=word', '-F', 'diarize=false'], capture_output=True, text=True)
        corps, _, code = r.stdout.rpartition('\n')
        if code == '200': return model, json.loads(corps)
        print(f'  {model} : HTTP {code or "?"} {corps[:200]} {r.stderr[:200]}', file=sys.stderr, flush=True)
    return None, None

def segments(mots):
    segs, cur = [], []
    for w in mots:
        if cur and (w['start'] - cur[-1]['end'] > PAUSE or len(cur) >= MAX_MOTS):
            segs.append(cur); cur = []
        cur.append(w)
        if w['word'].strip()[-1:] in FIN_PHRASE: segs.append(cur); cur = []
    if cur: segs.append(cur)
    return [{'start': s[0]['start'], 'end': s[-1]['end'], 'text': ' '.join(w['word'].strip() for w in s), 'words': s, 'scribe': True}
            for s in segs]

k = cle()
if not k: sys.exit('Scribe : pas de clé ElevenLabs, repli sur Whisper.')
faits = []
for clip in sys.argv[1:]:
    model, data = scribe(f'{W}/audio/{clip}-16k.wav', k)
    if not data:
        for f in faits: os.remove(f)
        sys.exit(f'Scribe a échoué sur {clip}, repli sur Whisper.')
    mots = [{'word': ' ' + w['text'].strip(), 'start': round(w['start'], 3), 'end': round(w['end'], 3),
             'probability': round(math.exp(w['logprob']), 3) if 'logprob' in w else 1.0}
            for w in data['words'] if w.get('type') == 'word' and w['text'].strip()]
    ev = [{'texte': w['text'].strip(), 'debut': w['start'], 'fin': w['end']} for w in data['words'] if w.get('type') == 'audio_event']
    segs = segments(mots)
    out = f'{W}/transcription/{clip}'
    json.dump(segs, open(f'{out}.json', 'w'), ensure_ascii=False, indent=1)
    with open(f'{out}.txt', 'w') as f:
        for s in segs: f.write(f"[{s['start']:7.2f} → {s['end']:7.2f}] {s['text']}\n")
    json.dump(ev, open(f'{out}-evenements.json', 'w'), ensure_ascii=False, indent=1)
    faits += [f'{out}.json', f'{out}.txt', f'{out}-evenements.json']
    print('fini', clip, model, len(mots), 'mots', len(ev), 'événement(s) sonore(s)', flush=True)
