---
name: preset-melvyn
description: "Monter une vidéo dans le style du preset Melvyn v3 : typographies, sous-titres, composition et rythme de la référence, adaptés au nouveau contenu."
---

# Melvyn v3

Lire [PRESET.md](PRESET.md), [preset.json](preset.json), puis les sources pertinentes dans `source/`. Les règles du preset priment sur les exemples historiques. Créer un projet distinct ; ne pas modifier le pack installé.

Les règles v3 de `PRESET.md` priment sur l’exemple : trois mots maximum par ligne. `source/captions.py` est un générateur historique à texte fixe ; ne pas l’exécuter tel quel sur un nouveau montage. Adapter texte, limite de mots et timecodes avant usage. Appliquer aussi `source/preset-customizations.json` aux nouveaux calques.

Les fichiers source sont des recettes et exemples éditables, pas un MP4 prêt à lire. Remplacer les textes et les médias d’exemple par ceux de l’utilisateur, reconstruire les durées et recaler les sous-titres sur le montage final. Les fichiers vidéo et images d’exemple ne sont pas fournis. Identifier les chemins src/url manquants avant de lancer le rendu et les remplacer dans la copie de travail.

Préserver mots entiers et sens. Vérifier tout l’export : synchronisation, lisibilité, absence de collisions, cadrage et audio. Ne pas annoncer un contrôle sonore si aucune écoute réelle n’a été possible. Livrer les sources éditables et l’export demandé ; indiquer les limites restantes. Frame n’est pas requis ni fourni.
