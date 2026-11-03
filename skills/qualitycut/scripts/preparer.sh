#!/bin/bash
# Étape 1 : préparer un dossier de travail à partir des rushs.
# usage : preparer.sh <dossier de travail> <rush1> [rush2 …]
# Fait : mise au format 30 i/s (sources/), son (audio/), transcription en deux passes + recollage (transcription/),
# alignement des mots, liste de mots numérotés (transcription/LISTE-MOTS.txt).
# Ensuite : écrire montage/<rush>.txt (passages gardés), puis lancer couper.py, verifier.py et exporter_cuts.py.
set -euo pipefail
I=$(cd "$(dirname "$0")" && pwd); PY=${PYTHON:-python3}
D=$1; shift; mkdir -p "$D"; D=$(cd "$D" && pwd); export MONTAGE_DOSSIER=$D
mkdir -p "$D"/{sources,audio,transcription/v1,montage,controle}
CLIPS=()
for f in "$@"; do
  b=$(basename "$f"); b=${b%.*}; CLIPS+=("$b")
  [ -f "$D/sources/$b.mov" ] || "$I/normaliser.sh" "$f" "$D/sources/$b.mov"
  [ -f "$D/audio/$b-48k.wav" ] || { ffmpeg -nostdin -v error -y -i "$D/sources/$b.mov" -map 0:a:0 -ac 1 -ar 16000 "$D/audio/$b-16k.wav"
                                    ffmpeg -nostdin -v error -y -i "$D/sources/$b.mov" -map 0:a:0 -ac 2 -c:a pcm_s16le "$D/audio/$b-48k.wav"; }
done
cd "$D/transcription"
if [ "${QUALITYCUT_SCRIBE:-1}" != 0 ] && "$PY" "$I/transcrire_scribe.py" "${CLIPS[@]}"; then
  # 1re passe Scribe (ElevenLabs) = texte de base ; la passe Whisper par morceaux devient la source de rattrapage (v1/)
  for c in "${CLIPS[@]}"; do cp "$c.json" "v1/$c-scribe.json"; cp "$c.txt" "v1/$c-scribe.txt"; done
  "$PY" "$I/transcrire_morceaux.py" "${CLIPS[@]}"              # Whisper par morceaux de parole (garde les reprises)
  for c in "${CLIPS[@]}"; do mv "$c.json" v1/; mv "$c.txt" v1/; cp "v1/$c-scribe.json" "$c.json"; cp "v1/$c-scribe.txt" "$c.txt"; done
else
  "$PY" "$I/transcrire.py" "${CLIPS[@]}"                       # repli : 1re passe Whisper, vidéo entière
  for c in "${CLIPS[@]}"; do cp "$c.json" v1/; cp "$c.txt" v1/; rm -f "$c.json"; done
  "$PY" "$I/transcrire_morceaux.py" "${CLIPS[@]}"              # 2e passe : par morceaux de parole (garde les reprises)
fi
"$PY" "$I/aligner.py" "${CLIPS[@]}"
"$PY" "$I/completer.py" "${CLIPS[@]}"                          # zones parlées restées sans mot
"$PY" "$I/fusion_v1.py" "${CLIPS[@]}"                          # passages perdus, repris de la 1re passe
"$PY" "$I/aligner.py" "${CLIPS[@]}"
"$PY" "$I/completer.py" --signaler-seulement "${CLIPS[@]}" # audit après le dernier alignement
: > "$D/transcription/LISTE-MOTS.txt"
for c in "${CLIPS[@]}"; do { echo "=== $c"; "$PY" "$I/lister.py" "$c"; } >> "$D/transcription/LISTE-MOTS.txt"; done
echo "Prêt : lire $D/transcription/LISTE-MOTS.txt puis écrire $D/montage/<rush>.txt (passages gardés)."
