# Règles du preset VELVET

Ces règles sont obligatoires. Elles viennent de 14 versions de retours sur la vidéo de référence C0209 : la version entre parenthèses est celle qui a introduit la règle. Ne pas en « améliorer » une sans demande.

## Polices
- Gros mots : Anton, 140 px, interlettrage -0.025em. (v8 : -0.1 était illisible sur Anton, les lettres se touchaient)
- Tout le reste : IBM Plex Sans Regular 400 Italic, 68 px, interlettrage -0.03em. (v8)
- Jamais de Roboto ni d'autre police. (v8)

## Sous-titres
- Aucune animation d'apparition : chaque mot se pose quand il est dit. (v8)
- 3 mots maximum par ligne.
- Une ligne dite en moins de 0,8 s s'affiche d'un coup.
- Une ligne, puis le gros mot dessous, décalé à droite : marche 137 px, écart 102 px, centre à y 1195. (v8, modèle : FOUTRE)
- Sous-titre seul : y 1244. Pendant le CTA, les sous-titres remontent à y 1130. (v12)
- Pas de ponctuation à l'écran. Montants écrits `5 000 €`, majuscules (`France`) via le champ `textes`.
- Pas de surcharge. (v6 : « trop de mot » à 1,35 s, 21,36 s et 58 s : on allège le type d'animation)
- Pas d'escalier en fenêtre glissante. (v11)

## Gros mots
- Un seul gros mot par écran.
- Hors rouge, un gros mot sur trois est entouré à la main : trait fin de 5 px, tracé en 8 images. (v10)
- Un trait fini reste visible au moins 6 images. S'il n'a pas le temps, le rond passe au gros mot suivant.
- Gros mot = mot important : nom, chiffre, mot fort. Jamais un mot faible. (v8 : SOUS retiré, BOUTON et MILLIERS D'EUROS ajoutés)

## Écran rouge
- 3 lignes maximum + 1 gros mot.
- Fond #730419, grille et texture.
- Gros mot pile au milieu, lignes centrées, bloc centré en hauteur (y 960). Les petites lignes sont décalées en marches. (v14 : les décalages de la v13 ont été rejetés ; v12 : écrans « trop à gauche »)
- Jamais deux fois de suite la même composition : le moteur alterne droite, miroir, centre.
- Un seul trait de 9 px sous le gros mot, jamais de rond. (v10)
- Entrée : flash blanc de 3 images (1 ; 0,55 ; 0,2). Sortie : coupe sèche. (v13)

## Hook
- Mot par mot, un gros mot par écran. (v10)

## Zooms
- Zooms secs, sans glissement, sur les coupes, les sorties d'écran rouge et les débuts de phrase. (v8)
- Cycle ×1, ×1,25, ×1, ×1,35, entre 36 et 66 images.
- Jamais sur un écran rouge.

## CTA
- « CLIQUE SOUS LA VIDÉO » en Anton sur plaque blanche. (v12)
- « Y ACCÉDER » (#730419, bordure blanche) posé sur la bordure de la plaque.
- 2 flèches au trait.
- Tout arrive ensemble, sur le mot choisi (« sous » dans la référence).

## Son
- Un SFX par type : hook, gros mot, gros mot rouge, flash, CTA. (v13)
- Pas de musique.
- Voix normalisée à -16 LUFS, limiteur 0,84.

## Zones sûres Instagram
- Côtés 65 px, haut 270 px, bas 1500 px, 140 px libres à droite sous y 1150. (v13)

## Coupes
- Ne jamais couper la fin d'un mot. (v12 : fin du « etc » coupée, +7 images pour la rendre audible)

## Déplacements
- Toujours appliqués depuis la disposition d'origine, sans les cumuler de version en version.
