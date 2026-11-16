# Transcription de base avec ElevenLabs Scribe (vidéo entière) : texte verbatim, temps de chaque mot.
# Sortie : transcription/RUSH.json + .txt (segments) ; événements sonores à part (RUSH-evenements.json).
import json, os, sys
import scipy.io.wavfile as wf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scribe
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))

scribe.cle()
for clip in sys.argv[1:]:
    sr, a = wf.read(f'{W}/audio/{clip}-16k.wav')
    data = scribe.brut(a, sr, evenements=True)
    ms = scribe.mots(data)
    ev = [{'texte': w['text'].strip(), 'debut': w['start'], 'fin': w['end']} for w in data.get('words', []) if w.get('type') == 'audio_event']
    segs = [dict(s, scribe=True) for s in scribe.segments(ms)]
    out = f'{W}/transcription/{clip}'
    json.dump(segs, open(f'{out}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(f'{out}.txt', 'w', encoding='utf-8') as f:
        for s in segs: f.write(f"[{s['start']:7.2f} → {s['end']:7.2f}] {s['text']}\n")
    json.dump(ev, open(f'{out}-evenements.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('fini', clip, len(ms), 'mots', len(ev), 'événement(s) sonore(s)', flush=True)
