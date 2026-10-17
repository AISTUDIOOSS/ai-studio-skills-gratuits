# Les skills montage vidéo d’AI Studio

Six ressources gratuites à télécharger et à donner à ton agent IA.

**[Télécharger tout le pack en ZIP](https://github.com/AISTUDIOOSS/ai-studio-skills-gratuits/archive/refs/heads/main.zip)** — aucun compte ni invitation nécessaire.

| Ressource | Contenu |
|---|---|
| [Cut Fusion](skills/qualitycut/SKILL.md) | QualityCut fusion UpTrainer : préparation, transcription, alignement, sélection et coupes. |
| [Analyse du style vidéo](skills/analyze-editing-inspiration/SKILL.md) | Décomposer une référence en règles de montage réutilisables. |
| [Preset Steve classique v4](skills/preset-steve/SKILL.md) | Sous-titres, accents rouges, typographies et rythme ; sources et outil d’habillage. |
| [Preset Melvyn v3](skills/preset-melvyn/SKILL.md) | Composition divisée, face caméra, schémas et pastilles de sous-titres. |
| [Zooms secs](skills/zooms-secs/SKILL.md) | Changements de cadrage instantanés inspirés du preset Steve. |
| [Zooms progressifs](skills/zooms-progressifs/SKILL.md) | Rapprochements et éloignements fluides, réglables et reproductibles. |

## Utilisation

1. Télécharge et décompresse le ZIP.
2. Donne à ton agent le dossier complet de la ressource choisie, avec ses sous-dossiers. Demande-lui de lire `SKILL.md` avant de travailler.
3. Fournis ta vidéo et ta demande. Exemple : « Lis le skill zooms-secs et applique ses recadrages à ce montage, en conservant l’audio. »

Pour une installation locale persistante : copie les dossiers choisis de `skills/` dans `~/.claude/skills/` pour Claude Code ou `~/.codex/skills/` pour Codex. Ne remplace pas une installation existante sans en conserver une copie. Ces ressources nécessitent un agent capable de lire les fichiers et, pour exécuter les scripts, d’utiliser un terminal local. Le téléchargement ne lance aucun programme.

## Prérequis et limites

- Cut Fusion : Mac Apple Silicon, Python 3.9–3.12, FFmpeg/ffprobe. Installer `skills/qualitycut/requirements.txt` dans un environnement Python isolé ; les modèles sont téléchargés au premier usage. Aucun secret API n’est fourni ou requis par les scripts locaux.
- L’aligneur MMS_FA utilisé par Cut Fusion est soumis à une licence non commerciale : lire [les précisions](skills/qualitycut/references/pipeline-local.md#portée-de-laligneur) avant usage commercial.
- Les presets contiennent des recettes éditables et leurs règles, pas les rushes ou médias des anciennes vidéos. L’agent doit remplacer les médias d’exemple, adapter les textes et reconstruire les durées. Les scripts de rendu HyperFrames sont indiqués dans les `package.json` sources.
- Les deux skills de zoom sont des instructions de montage, pas des extensions exécutables d’un logiciel.
- Frame n’est pas inclus. Aucun abonnement à AI Studio n’est nécessaire pour télécharger ; les outils et services choisis peuvent avoir leurs propres coûts et conditions.
- Les vérifications de ce dépôt portent sur le packaging, la syntaxe et la recherche de secrets. Aucun nouveau rendu vidéo de validation n’a été produit pour cette publication.

Les visiteurs peuvent lire et télécharger ce dépôt. Le téléchargement ne donne aucun droit d’écriture sur le dépôt d’origine.

Voir [THIRD-PARTY.md](THIRD-PARTY.md) pour les composants tiers.
