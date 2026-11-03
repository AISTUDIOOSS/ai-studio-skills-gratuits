# Le pack montage d'AI Studio, pour Claude Code

Monte tes vidéos face cam avec Claude Code, en une commande : `/velvet ton-rush.mp4`. Claude choisit les meilleures prises, coupe, ajoute les sous-titres, les gros mots, les écrans rouges, les zooms et les sons, puis te livre le MP4.

## Installation en un copier-coller

Ouvre Claude Code et colle ce message :

```
Installe le pack montage d'AI Studio : https://github.com/AISTUDIOOSS/ai-studio-skills-gratuits — lis INSTALL.md et fais tout.
```

Claude installe tout. Quand c'est fini, ferme Claude Code, rouvre-le, et tape `/velvet` suivi du chemin de ton rush.

Il faut un **Mac Apple Silicon** (M1, M2, M3, M4…), **Claude Code** et quelques Go d'espace libre. et Google Chrome. La première installation prend plusieurs minutes. Pas de mot de passe à donner, aucune clé ni abonnement.

## Ce que tu reçois

| Skill | Ce qu'il fait |
|---|---|
| [velvet](skills/velvet/SKILL.md) | `/velvet` : monte un rush de bout en bout au style VELVET (écrans rouges, gros mots, zooms secs, CTA, sons). |
| [qualitycut](skills/qualitycut/SKILL.md) | Choisit les bonnes prises et coupe les hésitations, au mot près. |
| [preset-steve](skills/preset-steve/SKILL.md) | Le style Steve : sous-titres, accents rouges, rythme. |
| [preset-melvyn](skills/preset-melvyn/SKILL.md) | Écran divisé, face caméra, schémas, pastilles de sous-titres. |
| [zooms-secs](skills/zooms-secs/SKILL.md) | Changements de cadrage instantanés. |
| [zooms-progressifs](skills/zooms-progressifs/SKILL.md) | Zooms avant et arrière fluides. |
| [analyze-editing-inspiration](skills/analyze-editing-inspiration/SKILL.md) | Transforme une vidéo qui t'inspire en règles de montage. |
| [animations-html](skills/animations-html/SKILL.md) | Rejoue les animations d'une vidéo analysée. |

Le guide pas à pas : [GUIDE-MONTAGE.md](GUIDE-MONTAGE.md).

## Limites

- Mac Apple Silicon uniquement. Les Mac Intel et Windows ne sont pas pris en charge.
- Frame (l'application de montage d'AI Studio) n'est pas inclus.
- L'outil d'alignement utilisé par QualityCut (MMS_FA) a une licence non commerciale : voir [les précisions](skills/qualitycut/references/pipeline-local.md#portée-de-laligneur) avant tout usage commercial.
- Composants tiers : [THIRD-PARTY.md](THIRD-PARTY.md).

Installation manuelle, sans Claude : `git clone` de ce dépôt, puis `bash install.sh`.
