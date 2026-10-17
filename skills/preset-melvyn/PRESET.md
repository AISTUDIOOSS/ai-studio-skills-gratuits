# MELVYNX V2 — preset v3

Référence : 5 skills Claude — split V3 (bleu), version 3.

## Réutilisation avec Claude Code

Lire preset.json et source/preset-customizations.json si présent : ces réglages personnalisés sont prioritaires sur les anciens exemples et la vidéo de référence. Le fichier source/index.html les intègrent déjà. Puis lire source/index.html, source/hyperframes.json et les compositions, styles, scripts et documents du dossier source. Les valeurs elements[].animation et animationDuration dans preset-customizations.json doivent être appliquées aux timelines sources avant rendu, en conservant les déclenchements par mot ; elles ne sont pas cuites dans le MP4 de référence. Ces sources figent les animations, typographies, placements et règles de rythme de la version de référence.

Créer un nouveau projet séparé pour la vidéo demandée. Adapter les textes, scènes, timecodes, sous-titres et durées au nouveau contenu, en conservant le langage visuel et les mouvements du modèle. Ne pas réutiliser les propos, chiffres ou médias du montage exemple sans demande explicite. Ne pas exécuter les scripts de correction historiques automatiquement.

Les médias d’exemple ne sont pas dupliqués : les références machine ont été retirées du pack public. Fournir les nouveaux rushes ; vérifier les éventuelles dépendances externes du code avant rendu. Les polices et composants locaux sont copiés dans source. Ne jamais modifier cette archive ; une mise à jour crée une version supplémentaire.

Après montage, vérifier le rendu avec les outils de lecture disponibles et livrer le projet éditable et l’export demandé. Si un outil de review est installé, l’utiliser ; Frame ne fait pas partie de ce pack. Ce preset est une recette source archivée, pas un modèle automatique déjà validé sur une autre vidéo.

## Types de texte et animations

Règles par type, prioritaires sur les valeurs d’origine du modèle. Appliquer chaque règle à tous les calques portant ces classes dans le nouveau montage (styles et timelines), puis vérifier la mise en page avec l’espacement et la taille modifiés.

- **Pastille sous-titre** (classes `cap st-cap`, 55 calques dans la référence) : taille (px vidéo) 46, espacement des lettres (em) -0.02, police Frame Inter-700.
- **Pastille d'étape** (classes `pill st-step`, 5 calques dans la référence) : couleur du texte #000000.
- **Chip UI** (classes `chipui st-chip`, 3 calques dans la référence) : inchangé.
- **Chip accroche** (classes `abs chipui s3c st-chip`, 3 calques dans la référence) : inchangé.
- **Chip noir** (classes `chipui dark st-chip`, 1 calques dans la référence) : inchangé.

Détail machine : source/preset-customizations.json → styleTypes.

## Règles du preset (dictées par Nicolas)

Obligatoires pour chaque nouveau montage avec ce preset, prioritaires sur la vidéo de référence et sur les choix par défaut. Vérifier chacune sur l’export avant livraison. Ne pas ajouter de règle sans demande écrite de Nicolas.

1. Jamais de chevauchement de sous-titres : une seule pastille de sous-titre à l’écran à la fois, et aucun texte (pastille, chip, en-tête d’étape, schéma) ne se superpose à un autre. _(v3)_
2. Pas plus de 3 mots par ligne de sous-titre — jamais 4. Si la phrase est plus longue, la découper en plusieurs pastilles successives. _(v3)_
3. Schéma cohérent avec ce qui se dit : la moitié haute illustre exactement la phrase en cours (mêmes mots, mêmes chiffres, même étape) et change pile quand le propos change. Une seule idée centrée par scène. _(v3)_
4. Pas de cut brut : aucune coupe ne tranche une phrase, un mot ou un élan en plein milieu. Laisser finir la fin de phrase et la respiration avant de couper (retours Melvyn une prise V2 : 10 × « cut trop brut »). _(v3)_
5. Écran coupé en deux : schéma en haut sur papier (zone utile y 270–870, sous la safe zone Instagram), face cam en bas, pastille de sous-titre sur la frontière. Les listes ont une pastille d’étape numérotée centrée en en-tête. _(v3)_
6. Scènes, zooms et sous-titres commencent et finissent pile sur la ligne de coupe ; jamais de passage sans sous-titre ; jamais assombrir la face cam (ni dégradé, ni fondu noir). _(v3)_

Détail machine : preset.json → rules[].
