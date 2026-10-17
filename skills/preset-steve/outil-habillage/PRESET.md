# Steve classique — preset de formation

Dérivé de Steve classique v1 (ID b309b30d-b39e-405a-aab7-49e57a9498b7, version 1) ; l’archive d’origine n’est pas modifiée.

- `habiller.py` : habillage sur des coupes QualityCut validées (`--job`, `--rush`, `--out`, `--groupes`). Il génère `composition/` (rendu HyperFrames) et `editable/` (aperçu à calques Frame). Il refuse d’écraser une version existante.
- Styles :
  - `w` : petit blanc CaptionHeavy 49 px ;
  - `r` : capsule rouge CaptionLightOblique 110 px, une seule ligne ;
  - `o` : grand blanc CaptionOblique 110 px.
- Mise en page : escaliers compacts. Les groupes comptent 1 à 3 mots et s’enchaînent sans flash vide. Le zoom alterne par plan (1,30 / 1,12), avec une légère poussée.
- Révisions Frame appliquées par calque :
  - `data-dx` / `data-dy` : décalage par rapport à la mise en page originale ;
  - `data-anim` : `cut`, `rise`, `fade`, `slide-up`, `slide-left`, `pop` ou `none` ;
  - `data-anim-dur` : durée de l’animation.
- `editable/theme.js` et `theme-panel.html` : panneau Personnaliser (palettes, polices par rôle, espacement).
- `assets/` : GSAP et polices. Les polices sont locales et hors Git, car leur licence de redistribution n’a pas été vérifiée.

Contrôle : régénéré sur les coupes C0210, ce script reproduit à l’identique les 141 calques de la v1 livrée (texte, style, images de début et de fin, animation). La vidéo coupée atteint un PSNR minimal de 49,6 dB face à l’original.
- `--preset <version>` : applique les règles par type (`styleTypes`) d’une version de preset enregistrée depuis Frame → Personnaliser → Types d’animation. Sans cette option : valeurs de Steve classique v1. Les sous-titres portent `data-style-label` et la composition déclare `<meta name="frame-preset">`, ce qui permet à Frame de proposer « Mettre à jour le preset ».

## Types d’animation
| Type | Classe | Rôle |
|---|---|---|
| Sous-titres simples | `cap s-w` | sous-titre blanc courant (heavy) |
| Gros mots blancs | `cap s-o` | mot fort en grand oblique blanc |
| Surlignage | `cap s-r` | mot surligné dans une capsule (`.box` rouge + `.tx`) |
