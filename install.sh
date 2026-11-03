#!/bin/bash
# Installe le pack montage d'AI Studio pour Claude Code : skills dans ~/.claude/skills, outils (ffmpeg, node, python 3.12),
# environnement Python ~/.venv-velvet, puis vérification. Sans Homebrew ni mot de passe. Relançable sans risque : il met à jour ce qui existe déjà.
# usage : bash install.sh            (depuis le dossier du pack)
set -euo pipefail
SRC=$(cd "$(dirname "$0")" && pwd)
SKILLS="$HOME/.claude/skills"; VENV="$HOME/.venv-velvet"
ok() { printf '  ✓ %s\n' "$1"; }
stop() { printf '\n✗ %s\n' "$1"; exit "${2:-1}"; }

echo "1/6 Machine"
[ "$(uname -s)" = Darwin ] || stop "Ce pack tourne sur Mac uniquement."
[ "$(uname -m)" = arm64 ] || stop "Il faut un Mac Apple Silicon (M1, M2, M3, M4…). Les Mac Intel ne sont pas pris en charge."
ok "Mac Apple Silicon"

echo "2/6 Outils (ffmpeg, node, uv) — sans Homebrew ni mot de passe"
# Tout va dans ~/.local/bin ; un outil déjà présent sur la machine est gardé tel quel.
BIN="$HOME/.local/bin"; OUTILS="$HOME/.ai-studio-montage-outils"; mkdir -p "$BIN" "$OUTILS"
export PATH="$BIN:$PATH"
for f in "$HOME/.zprofile" "$HOME/.zshrc"; do
  grep -q 'ai-studio-montage' "$f" 2>/dev/null || printf '\nexport PATH="$HOME/.local/bin:$PATH"  # ai-studio-montage\n' >> "$f"
done
TMPD=$(mktemp -d)
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then ok "ffmpeg déjà là"; else
  for t in ffmpeg ffprobe; do
    curl -fsSL -o "$TMPD/$t.zip" "https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/release/$t.zip"
    unzip -o -q "$TMPD/$t.zip" -d "$BIN"; chmod +x "$BIN/$t"
  done; ok "ffmpeg installé"
fi
if command -v node >/dev/null && command -v npx >/dev/null; then ok "node déjà là"; else
  NODE=$(curl -fsSL https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt | grep 'darwin-arm64.tar.gz' | head -1)
  curl -fsSL -o "$TMPD/node.tgz" "https://nodejs.org/dist/latest-v22.x/${NODE##* }"
  [ "$(shasum -a 256 "$TMPD/node.tgz" | cut -d' ' -f1)" = "${NODE%% *}" ] || stop "Téléchargement de node abîmé, relance l'installation."
  rm -rf "$OUTILS/node"; mkdir -p "$OUTILS/node"; tar -xzf "$TMPD/node.tgz" -C "$OUTILS/node" --strip-components 1
  for t in node npm npx; do ln -sf "$OUTILS/node/bin/$t" "$BIN/$t"; done; ok "node installé"
fi
if command -v uv >/dev/null; then ok "uv déjà là"; else
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$BIN" UV_NO_MODIFY_PATH=1 sh >/dev/null; ok "uv installé"
fi
rm -rf "$TMPD"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] && ok "Google Chrome" || stop "Google Chrome manque : installe-le depuis google.com/chrome, puis relance l'installation." 3

echo "3/6 Environnement Python ($VENV)"
[ -x "$VENV/bin/python" ] || uv venv -q --python 3.12 "$VENV"
uv pip install -q --python "$VENV/bin/python" -r "$SRC/skills/qualitycut/requirements.txt" pillow numpy
ok "dépendances Python"

echo "4/6 Skills dans $SKILLS"
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

echo "5/6 Outils de rendu"
npm i -s --no-save --no-package-lock --prefix "$SKILLS/velvet/preset" puppeteer-core >/dev/null && ok "contrôle des zones sûres"
npx --yes hyperframes@0.8.162 --version >/dev/null 2>&1 && ok "HyperFrames" || echo "  HyperFrames sera téléchargé au premier rendu"

echo "6/6 Vérification"
ffmpeg -version >/dev/null && ffprobe -version >/dev/null && ok "ffmpeg $(ffmpeg -version | head -1 | cut -d' ' -f3)"
ok "node $(node -v)"
"$VENV/bin/python" -c "import numpy, scipy, mlx_whisper, torch, torchaudio, num2words, PIL" && ok "Python : whisper, torch, pillow"
"$VENV/bin/python" -m py_compile "$SKILLS"/qualitycut/scripts/*.py "$SKILLS"/velvet/preset/*.py "$SKILLS"/preset-steve/outil-habillage/habiller.py && ok "scripts lisibles"
"$VENV/bin/python" "$SKILLS/velvet/preset/habiller.py" --help >/dev/null && ok "moteur VELVET"
node -e "require(require.resolve('puppeteer-core',{paths:['$SKILLS/velvet/preset']}))" && ok "puppeteer"
for n in "$SRC"/skills/*/; do [ -f "$SKILLS/$(basename "$n")/SKILL.md" ] || stop "skill $(basename "$n") manquant"; done
echo
echo "INSTALLATION OK — skills : $(cd "$SRC/skills" && ls | tr '\n' ' ')"
echo "Dans Claude Code : /velvet chemin/de/ton-rush.mp4"
