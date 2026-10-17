#!/bin/bash
# Mise au format AVANT toute transcription : vertical 1080x1920, 30 images/s constantes, couleurs SDR bt709, son PCM 48 kHz.
# Tous les temps et numéros d'images du skill se réfèrent à ce fichier (c'est aussi la source attendue par `from-source`).
# usage : normaliser.sh <rush d'origine> <sortie.mov>
set -euo pipefail
in=$1; out=$2
trc=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$in" || true)
case "$trc" in
  smpte2084|arib-std-b67)  # HDR (téléphone) -> SDR ; demande un ffmpeg compilé avec zimg (zscale)
    vf="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,";;
  *) vf="";;
esac
vf="${vf}scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
ffmpeg -nostdin -v error -y -i "$in" -map 0:v:0 -map 0:a:0 -vf "$vf" -af "aresample=48000:async=1:first_pts=0" \
  -c:v libx264 -preset fast -crf 16 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a pcm_s16le -ar 48000 -ac 2 -fps_mode cfr -r 30 -map_metadata -1 "$out"
