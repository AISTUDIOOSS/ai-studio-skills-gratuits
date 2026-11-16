#!/bin/bash
# Étape 1 : préparer un dossier de travail à partir des rushs.
# usage : preparer.sh <dossier de travail> <rush1> [rush2 …]
# Fait : mise au format 30 i/s (sources/), son (audio/), transcription ElevenLabs Scribe + zones oubliées (transcription/),
# alignement des mots, liste de mots numérotés (transcription/LISTE-MOTS.txt).
# Ensuite : écrire montage/<rush>.txt (passages gardés), puis lancer couper.py, verifier.py et exporter_cuts.py.
set -euo pipefail
I=$(cd "$(dirname "$0")" && pwd); PY=${PYTHON:-python3}; export PYTHONUTF8=1
D=$1; shift; mkdir -p "$D"; D=$(cd "$D" && pwd); export MONTAGE_DOSSIER=$D
mkdir -p "$D"/{sources,audio,transcription,montage,controle}
CLIPS=()
for f in "$@"; do
  b=$(basename "$f"); b=${b%.*}; CLIPS+=("$b")
  [ -f "$D/sources/$b.mov" ] || "$I/normaliser.sh" "$f" "$D/sources/$b.mov"
  [ -f "$D/audio/$b-48k.wav" ] || { ffmpeg -nostdin -v error -y -i "$D/sources/$b.mov" -map 0:a:0 -ac 1 -ar 16000 "$D/audio/$b-16k.wav"
                                    ffmpeg -nostdin -v error -y -i "$D/sources/$b.mov" -map 0:a:0 -ac 2 -c:a pcm_s16le "$D/audio/$b-48k.wav"; }
done
cd "$D/transcription"
"$PY" "$I/transcrire_scribe.py" "${CLIPS[@]}"                # ElevenLabs Scribe, vidéo entière
"$PY" "$I/aligner.py" "${CLIPS[@]}"
"$PY" "$I/completer.py" "${CLIPS[@]}"                          # zones parlées restées sans mot
"$PY" "$I/aligner.py" "${CLIPS[@]}"                            # réaligner avec les mots ajoutés
"$PY" "$I/completer.py" --signaler-seulement "${CLIPS[@]}" # audit après le dernier alignement
: > "$D/transcription/LISTE-MOTS.txt"
for c in "${CLIPS[@]}"; do { echo "=== $c"; "$PY" "$I/lister.py" "$c"; } >> "$D/transcription/LISTE-MOTS.txt"; done
echo "Prêt : lire $D/transcription/LISTE-MOTS.txt puis écrire $D/montage/<rush>.txt (passages gardés)."
