# Steve classique — preset v4

Référence : C0208 · Steve · V3 — dosage allégé, version 3.

## Réutilisation dans Codex

Lire preset.json puis source/index.html, source/hyperframes.json et les compositions, styles, scripts et documents du dossier source. Ces sources figent les animations, typographies, placements et règles de rythme de la version de référence.

Créer un nouveau projet séparé pour la vidéo demandée. Adapter les textes, scènes, timecodes, sous-titres et durées au nouveau contenu, en conservant le langage visuel et les mouvements du modèle. Ne pas réutiliser les propos, chiffres ou médias du montage exemple sans demande explicite. Ne pas exécuter les scripts de correction historiques automatiquement.

Les médias d’exemple ne sont pas dupliqués : les références machine ont été retirées du pack public. Fournir les nouveaux rushes ; vérifier les éventuelles dépendances externes du code avant rendu. Les polices et composants locaux sont copiés dans source. Ne jamais modifier cette archive ; une mise à jour crée une version supplémentaire.

Après montage, vérifier le rendu avec les outils de lecture disponibles et livrer le projet éditable et l’export demandé. Si un outil de review est installé, l’utiliser ; Frame ne fait pas partie de ce pack. Ce preset est une recette source archivée, pas un modèle automatique déjà validé sur une autre vidéo.

## Règles du preset (dictées par Nicolas)

Obligatoires pour chaque nouveau montage avec ce preset, prioritaires sur la vidéo de référence et sur les choix par défaut. Vérifier chacune sur l’export avant livraison. Ne pas ajouter de règle sans demande écrite de Nicolas.

1. Hook : la phrase d'accroche (environ les 3 premières secondes) contient toujours 1 à 2 surlignages rouges, posés sur les mots les plus importants — jamais aucun, jamais plus de 2. _(v2)_
2. Jamais de chevauchement de sous-titres : un seul groupe à l'écran à la fois, et dans un escalier aucune ligne ne touche une autre, même pendant les montées — au repos, au moins 18 px d'encre entre deux lignes et 24 px au contact d'une capsule rouge (habiller.py --ecart 18). _(v2, révisée en v4)_
3. Gros mots blancs (oblique 110 px) plus présents : environ un toutes les 5 à 7 secondes, sur des mots forts ou émotionnels, en alternance avec les surlignages rouges. Chacun reste lisible au moins 0,5 s ; si le mot est trop bref, le mettre en escalier avec les mots qui suivent. _(v2)_
4. Pas plus de 4 mots par ligne de sous-titre. _(v2)_

Détail machine : preset.json → rules[].
