#!/bin/bash
# Installe le pack montage d'AI Studio pour Claude Code : skills dans ~/.claude/skills, outils (ffmpeg, node, python 3.12),
# environnement Python ~/.venv-velvet, puis vérification. Sans Homebrew ni mot de passe. Relançable sans risque : il met à jour ce qui existe déjà.
# Mac Apple Silicon (Terminal) ou Windows 10/11 (Git Bash, le terminal qu'utilise Claude Code sur Windows).
# usage : bash install.sh            (depuis le dossier du pack)
set -euo pipefail
SRC=$(cd "$(dirname "$0")" && pwd)
SKILLS="$HOME/.claude/skills"; VENV="$HOME/.venv-velvet"
ok() { printf '  ✓ %s\n' "$1"; }
stop() { printf '\n✗ %s\n' "$1"; exit "${2:-1}"; }

echo "1/7 Machine"
case "$(uname -s)" in
  Darwin) OS=mac
          [ "$(uname -m)" = arm64 ] || stop "Il faut un Mac Apple Silicon (M1, M2, M3, M4…). Les Mac Intel ne sont pas pris en charge."
          ok "Mac Apple Silicon" ;;
  MINGW*|MSYS*|CYGWIN*) OS=win; ok "Windows" ;;
  Linux) stop "Linux et WSL ne sont pas pris en charge : sur Windows, lance Claude Code directement dans Windows (pas dans WSL)." ;;
  *) stop "Système non pris en charge : il faut un Mac Apple Silicon ou Windows 10/11." ;;
esac
natif() { if [ "$OS" = win ]; then cygpath -m "$1"; else printf '%s' "$1"; fi; }   # chemin lisible par node/python sous Windows
dezip() { if command -v unzip >/dev/null; then unzip -o -q "$1" -d "$2"; else
  powershell.exe -NoProfile -Command "Expand-Archive -Force -LiteralPath '$(cygpath -w "$1")' -DestinationPath '$(cygpath -w "$2")'"; fi; }
sha() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }
# petit lanceur : sous Windows, ~/.local/bin/node appelle le vrai node.exe (un lien copié casserait npm et npx)
lanceur() { printf '#!/bin/sh\nexec "%s" "$@"\n' "$2" > "$BIN/$1"; chmod +x "$BIN/$1"; }

echo "2/7 Outils (ffmpeg, node, uv) — sans Homebrew ni mot de passe"
# Tout va dans ~/.local/bin ; un outil déjà présent sur la machine est gardé tel quel.
BIN="$HOME/.local/bin"; OUTILS="$HOME/.ai-studio-montage-outils"; mkdir -p "$BIN" "$OUTILS"
export PATH="$BIN:$PATH"
if [ "$OS" = mac ]; then PROFILS="$HOME/.zprofile $HOME/.zshrc"; else PROFILS="$HOME/.bashrc"; [ -f "$HOME/.bash_profile" ] && PROFILS="$PROFILS $HOME/.bash_profile"; fi
for f in $PROFILS; do
  grep -q 'ai-studio-montage' "$f" 2>/dev/null || printf '\nexport PATH="$HOME/.local/bin:$PATH"  # ai-studio-montage\n' >> "$f"
done
TMPD=$(mktemp -d)
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then ok "ffmpeg déjà là"
elif [ "$OS" = mac ]; then
  for t in ffmpeg ffprobe; do
    curl -fsSL -o "$TMPD/$t.zip" "https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/$t.zip"
    unzip -o -q "$TMPD/$t.zip" -d "$BIN"; chmod +x "$BIN/$t"
  done; ok "ffmpeg installé"
else
  curl -fsSL -o "$TMPD/ffmpeg.zip" "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
  dezip "$TMPD/ffmpeg.zip" "$TMPD/ffmpeg"
  cp "$TMPD"/ffmpeg/*/bin/ffmpeg.exe "$TMPD"/ffmpeg/*/bin/ffprobe.exe "$BIN/"; ok "ffmpeg installé"
fi
if command -v node >/dev/null && command -v npx >/dev/null; then ok "node déjà là"
elif [ "$OS" = mac ]; then
  NODE=$(curl -fsSL https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt | grep 'darwin-arm64.tar.gz' | head -1)
  curl -fsSL -o "$TMPD/node.tgz" "https://nodejs.org/dist/latest-v22.x/${NODE##* }"
  [ "$(sha "$TMPD/node.tgz")" = "${NODE%% *}" ] || stop "Téléchargement de node abîmé, relance l'installation."
  rm -rf "$OUTILS/node"; mkdir -p "$OUTILS/node"; tar -xzf "$TMPD/node.tgz" -C "$OUTILS/node" --strip-components 1
  for t in node npm npx; do ln -sf "$OUTILS/node/bin/$t" "$BIN/$t"; done; ok "node installé"
else
  NODE=$(curl -fsSL https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt | grep 'win-x64.zip' | head -1)
  curl -fsSL -o "$TMPD/node.zip" "https://nodejs.org/dist/latest-v22.x/${NODE##* }"
  [ "$(sha "$TMPD/node.zip")" = "${NODE%% *}" ] || stop "Téléchargement de node abîmé, relance l'installation."
  rm -rf "$OUTILS/node"; dezip "$TMPD/node.zip" "$TMPD/node"; mv "$TMPD"/node/node-* "$OUTILS/node"
  lanceur node "$OUTILS/node/node.exe"; lanceur npm "$OUTILS/node/npm"; lanceur npx "$OUTILS/node/npx"; ok "node installé"
fi
if command -v uv >/dev/null; then ok "uv déjà là"
elif [ "$OS" = mac ]; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$BIN" UV_NO_MODIFY_PATH=1 sh >/dev/null; ok "uv installé"
else
  curl -fsSL -o "$TMPD/uv.zip" "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
  dezip "$TMPD/uv.zip" "$TMPD/uv"; cp "$TMPD"/uv/uv.exe "$BIN/"; ok "uv installé"
fi
rm -rf "$TMPD"
if [ "$OS" = mac ]; then CHROMES="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else CHROMES="/c/Program Files/Google/Chrome/Application/chrome.exe
/c/Program Files (x86)/Google/Chrome/Application/chrome.exe
$(cygpath -u "${LOCALAPPDATA:-C:/x}")/Google/Chrome/Application/chrome.exe"; fi
CHROME=""; while IFS= read -r c; do [ -f "$c" ] && { CHROME=$c; break; }; done <<< "$CHROMES"
[ -n "$CHROME" ] && ok "Google Chrome" || stop "Google Chrome manque : installe-le depuis google.com/chrome, puis relance l'installation." 3

echo "3/7 Environnement Python ($VENV)"
if [ "$OS" = win ]; then
  [ -x "$VENV/Scripts/python.exe" ] || uv venv -q --python 3.12 "$VENV"
  # même chemin que sur Mac (~/.venv-velvet/bin/python) pour les skills ; UTF-8 forcé pour les accents
  mkdir -p "$VENV/bin"; printf '#!/bin/sh\nexport PYTHONUTF8=1\nexec "%s" "$@"\n' "$VENV/Scripts/python.exe" > "$VENV/bin/python"; chmod +x "$VENV/bin/python"
else
  [ -x "$VENV/bin/python" ] || uv venv -q --python 3.12 "$VENV"
fi
PYVRAI="$VENV/bin/python"; [ "$OS" = win ] && PYVRAI="$VENV/Scripts/python.exe"
uv pip install -q --python "$(natif "$PYVRAI")" -r "$SRC/skills/qualitycut/requirements.txt" pillow numpy
ok "dépendances Python"

echo "4/7 Skills dans $SKILLS"
mkdir -p "$SKILLS"; SAUVE="$HOME/.ai-studio-montage-sauvegarde/$(date +%Y%m%d-%H%M%S)"
for d in "$SRC"/skills/*/; do
  n=$(basename "$d"); cible="$SKILLS/$n"
  if [ -e "$cible" ] && ! diff -rq -x node_modules -x __pycache__ "$d" "$cible" >/dev/null 2>&1; then
    mkdir -p "$SAUVE"; mv "$cible" "$SAUVE/$n"; echo "  ancienne version de $n mise de côté dans $SAUVE"
  fi
  mkdir -p "$cible"; cp -R "$d". "$cible/"; ok "$n"
done
chmod +x "$SKILLS"/qualitycut/scripts/*.sh "$SKILLS"/velvet/preset/*.py
if [ "$SRC" != "$HOME/.ai-studio-montage" ]; then
  [ -e "$HOME/.ai-studio-montage" ] && { mkdir -p "$SAUVE"; mv "$HOME/.ai-studio-montage" "$SAUVE/pack"; }
  cp -R "$SRC" "$HOME/.ai-studio-montage"
fi

echo "5/7 Outils de rendu"
npm i -s --no-save --no-package-lock --prefix "$SKILLS/velvet/preset" puppeteer-core >/dev/null && ok "contrôle des zones sûres"
npx --yes hyperframes@0.8.162 --version >/dev/null 2>&1 && ok "HyperFrames" || echo "  HyperFrames sera téléchargé au premier rendu"

echo "6/7 Clé ElevenLabs (transcription)"
CLE="$HOME/.config/elevenlabs/key"
if [ ! -s "$CLE" ] && [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  mkdir -p "$(dirname "$CLE")"; printf '%s' "$ELEVENLABS_API_KEY" > "$CLE"; chmod 600 "$CLE"
fi
[ -s "$CLE" ] || stop "Clé ElevenLabs manquante : crée-la sur elevenlabs.io (Developers → API Keys), enregistre-la dans $CLE, puis relance l'installation." 4
"$VENV/bin/python" "$SKILLS/qualitycut/scripts/scribe.py" --tester >/dev/null || stop "La clé ElevenLabs ne marche pas (refusée ou plus de crédits). Vérifie-la sur elevenlabs.io, puis relance l'installation." 5
ok "clé ElevenLabs"

echo "7/7 Vérification"
ffmpeg -version >/dev/null && ffprobe -version >/dev/null && ok "ffmpeg $(ffmpeg -version | head -1 | cut -d' ' -f3)"
ok "node $(node -v)"
"$VENV/bin/python" -c "import numpy, scipy, torch, torchaudio, num2words, PIL" && ok "Python : torch, pillow"
"$VENV/bin/python" -m py_compile "$SKILLS"/qualitycut/scripts/*.py "$SKILLS"/velvet/preset/*.py "$SKILLS"/preset-steve/outil-habillage/habiller.py && ok "scripts lisibles"
"$VENV/bin/python" "$SKILLS/velvet/preset/habiller.py" --help >/dev/null && ok "moteur VELVET"
node -e "require(require.resolve('puppeteer-core',{paths:['$(natif "$SKILLS/velvet/preset")']}))" && ok "puppeteer"
for n in "$SRC"/skills/*/; do [ -f "$SKILLS/$(basename "$n")/SKILL.md" ] || stop "skill $(basename "$n") manquant"; done
echo
echo "INSTALLATION OK — skills : $(cd "$SRC/skills" && ls | tr '\n' ' ')"
echo "Dans Claude Code : /velvet chemin/de/ton-rush.mp4"
