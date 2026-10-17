# Transcription mot à mot (verbatim) des rushes : on veut garder les "euh", les répétitions et les reprises.
import mlx_whisper, json, sys, os
PROMPT = ("Euh, alors, euh... je, je vais, enfin, bref. Hum, du coup, en fait, voilà. "
          "Tu vois, euh, c'est, c'est vraiment... non, attends, je reprends.")
W = os.path.abspath(os.path.expanduser(os.environ.get('MONTAGE_DOSSIER', '.')))
for clip in sys.argv[1:]:
    out = f'{W}/transcription/{clip}.json'
    if os.path.exists(out):
        print('déjà fait', clip, flush=True); continue
    tr = mlx_whisper.transcribe(f'{W}/audio/{clip}-16k.wav',
                                path_or_hf_repo='mlx-community/whisper-large-v3-mlx',
                                language='fr', word_timestamps=True,
                                condition_on_previous_text=False,
                                initial_prompt=PROMPT,
                                no_speech_threshold=0.3)
    json.dump(tr['segments'], open(out, 'w'), ensure_ascii=False, indent=1)
    with open(f'{W}/transcription/{clip}.txt', 'w') as f:
        for s in tr['segments']:
            f.write(f"[{s['start']:7.2f} → {s['end']:7.2f}] {s['text'].strip()}\n")
    print('fini', clip, flush=True)
