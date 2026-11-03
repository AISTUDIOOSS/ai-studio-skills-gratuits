---
name: velvet
description: Monte un rush face cam vertical de bout en bout au style VELVET (coupes QualityCut, sous-titres, gros mots, écrans rouges, zooms secs, CTA, SFX) et livre le MP4. Utiliser sur /velvet, « monte ce rush en VELVET », « style écran rouge ».
argument-hint: "<chemin du rush .mp4/.mov>"
---

# /velvet — monter un rush au style VELVET

L'utilisateur donne un rush face cam vertical (une voix, en français). Tu fais tout, dans l'ordre, sans lui poser de question technique. Il n'est pas forcément technique : parle simple, et à la fin dis-lui où est sa vidéo.

Chemins :
- `PKG` = `~/.claude/skills/velvet` (ce skill : moteur dans `preset/`, règles, guide).
- `QC` = `~/.claude/skills/qualitycut` (le skill de coupe).
- `PY` = `~/.venv-velvet/bin/python`.
- `PROJET` = un dossier neuf à côté du rush : `<dossier du rush>/<RUSH>-velvet/`. `RUSH` = nom du fichier sans extension.

Avant de commencer, lis en entier [references/regles.md](references/regles.md) (obligatoires) et [references/guide.md](references/guide.md) (comment écrire le plan, le son, les retours). Regarde `PKG/exemple/C0209-v14-planche.png` : c'est le rendu attendu. `PKG/preset/habillage-exemple-C0209.json` est un vrai plan complet, à prendre comme modèle de forme, jamais de contenu.

Commence chaque commande du terminal par `export PATH="$HOME/.local/bin:$PATH";` (l'installation y met ffmpeg et node).

Si `PY` n'existe pas ou que `ffmpeg`, `node` ou Google Chrome manquent : l'installation n'est pas faite. Lance `bash ~/.ai-studio-montage/install.sh` s'il existe, sinon suis `https://github.com/AISTUDIOOSS/ai-studio-skills-gratuits/blob/main/INSTALL.md`.

## 1. Coupes (QualityCut, obligatoire)
Lis `QC/SKILL.md` et `QC/references/pipeline-local.md`, et suis-les à la lettre. Jamais de coupe maison.
```bash
PYTHON=~/.venv-velvet/bin/python bash ~/.claude/skills/qualitycut/scripts/preparer.sh PROJET/job /chemin/RUSH.mp4
```
Puis choisis les prises, écris `montage/RUSH.txt` et lance couper, verifier, exporter_cuts comme décrit dans pipeline-local.md. Sortie : `PROJET/job/montage/RUSH-cuts.json` et `RUSH-analysis-minimale.json`. On ne touche plus jamais aux bords de ces coupes. Le premier lancement télécharge les modèles de transcription (quelques minutes).

## 2. Lire les mots
```bash
cd PROJET && ~/.venv-velvet/bin/python ~/.claude/skills/velvet/preset/habiller.py --job job --rush RUSH --liste
```
Lis tout. Repère le hook et ses mots forts, les mots importants (noms, chiffres, mots forts), 3 à 5 phrases fortes pour les écrans rouges, le mot qui déclenche le CTA.

## 3. Écrire `PROJET/v1/habillage.json`
Champ par champ : section 4 de `references/guide.md`. Tout le texte vient du nouveau rush.

## 4. Générer la composition
```bash
cd PROJET && ~/.venv-velvet/bin/python ~/.claude/skills/velvet/preset/habiller.py \
  --job job --rush RUSH --out v1 --plan v1/habillage.json --titre "RUSH · VELVET"
```
Corrige le plan (jamais le moteur) jusqu'à ne plus avoir de « À REVOIR ».

## 5. Mesurer
```bash
cd PROJET && ~/.venv-velvet/bin/python ~/.claude/skills/velvet/preset/mesurer.py v1
cd PROJET && node ~/.claude/skills/velvet/preset/zones.cjs v1
```
`zones.cjs` doit finir par `0 hors zone`. Les lignes brèves de `mesurer.py` sont à regarder, pas à corriger d'office (la référence en a 17).

## 6. Rendre (plusieurs minutes)
Le rendu tourne détaché, pour survivre si ta commande est coupée :
```bash
cd PROJET/v1/composition && mkdir -p ../export && nohup sh -c \
'npx --yes hyperframes@0.8.162 render . -o ../export/RUSH-velvet-v1-rendu.mp4 > ../render.log 2>&1; echo "FIN $?" >> ../render.log' >/dev/null 2>&1 &
```
Puis attends la fin sans terminer ton tour, avec le délai maximum ; si l'attente est coupée, relance-la (pas le rendu) :
```bash
until grep -q '^FIN' PROJET/v1/render.log 2>/dev/null; do sleep 20; done; tail -5 PROJET/v1/render.log
```
`FIN 0` = réussi. Autre chiffre : lis `render.log`, corrige, relance le rendu.

## 7. Poser le son
```bash
cd PROJET && ~/.venv-velvet/bin/python ~/.claude/skills/velvet/preset/mixer.py v1 \
  v1/export/RUSH-velvet-v1-rendu.mp4 v1/export/RUSH-velvet-v1.mp4
```

## 8. Vérifier l'export (le vrai MP4, pas l'aperçu)
- Images : sors une planche (hook, un gros mot, un rond, chaque écran rouge, le CTA) avec ffmpeg et regarde-la vraiment. Compare à la planche de référence : rien ne se touche, écrans rouges centrés, 3 mots max, aucune ponctuation, € présents.
- Zooms : sur les coupes et débuts de phrase, aucun sur écran rouge, visage jamais coupé.
- Son : vérifie un pic dans le mix à chaque entrée de `v1/sfx-plan.json`. Tu n'as pas écouté : dis « mesuré dans le mix », jamais « écouté ».

## 9. Livrer
Écris `PROJET/v1/journal.md` (ce qui a été fait, les choix). Donne à l'utilisateur le chemin du MP4 final, ce qui a été fait et ce qui n'est pas vérifié. Pour l'ouvrir : `open PROJET/v1/export/RUSH-velvet-v1.mp4`.

## Retours
Chaque retour = un nouveau dossier `v2`, `v3`… avec une copie modifiée de `habillage.json`, puis étapes 4 à 9. Change le minimum. Détails : section 7 de `references/guide.md`.
