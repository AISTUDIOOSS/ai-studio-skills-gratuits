---
name: preset-steve
description: "Monter une vidéo dans le style du preset Steve classique v4 : typographies, sous-titres, composition et rythme de la référence, adaptés au nouveau contenu."
---

# Steve classique v4

Lire [PRESET.md](PRESET.md), [preset.json](preset.json), puis les sources pertinentes dans `source/`. Les règles du preset priment sur les exemples historiques. Créer un projet distinct ; ne pas modifier le pack installé.

Pour le flux QualityCut Fusion, utiliser `outil-habillage/habiller.py --help` puis fournir le job, le rush, une sortie nouvelle, `--preset` pointant sur ce dossier et `--ecart 18`. Préparer les choix de groupes selon les règles v4 : le générateur ne choisit pas seul les emphases. Ne pas utiliser ses anciens espacements par défaut.

Les fichiers source sont des recettes et exemples éditables, pas un MP4 prêt à lire. Remplacer les textes et les médias d’exemple par ceux de l’utilisateur, reconstruire les durées et recaler les sous-titres sur le montage final. Les fichiers vidéo et images d’exemple ne sont pas fournis. Identifier les chemins src/url manquants avant de lancer le rendu et les remplacer dans la copie de travail.

Préserver mots entiers et sens. Vérifier tout l’export : synchronisation, lisibilité, absence de collisions, cadrage et audio. Ne pas annoncer un contrôle sonore si aucune écoute réelle n’a été possible. Livrer les sources éditables et l’export demandé ; indiquer les limites restantes. Frame n’est pas requis ni fourni.
