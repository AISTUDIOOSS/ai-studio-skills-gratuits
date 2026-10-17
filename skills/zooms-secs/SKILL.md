---
name: zooms-secs
description: "Ajouter des recadrages instantanés sur les coupes d’une vidéo, à partir de la logique du preset Steve, sans mouvement progressif."
---

# Zooms secs — Steve

## Réglage issu du preset Steve

Le générateur Steve classique v4 (`preset-steve/outil-habillage/habiller.py`, tableau `zooms`) alterne les échelles 1,30 et 1,12 à chaque plan. Il ajoute aussi une dérive progressive de 2,5 % : ce skill isole seulement les changements secs, sans cette dérive. L’échelle s’applique après le cadrage de base qui remplit le format de sortie.

Sur chaque intervalle [début, fin), maintenir une échelle constante ; changer exactement à la première image du plan suivant. Point de départ fidèle : 1,30, puis 1,12, puis 1,30. Si un zoom coupe le visage ou manque de définition, diminuer les valeurs pour cette source et documenter l’adaptation. Ne pas présenter ces valeurs comme imposées à toutes les vidéos.

## Application

Lire le montage final et ses coupes ; ne pas recalculer les cuts ou modifier l’audio. Placer l’ancrage au centre ou sur un point fixe du sujet selon son cadrage. Limiter le recadrage au rush, sans agrandir les sous-titres ni les éléments UI. Aucun fondu, flou, interpolation ou accélération de la vidéo.

Dans un éditeur à images clés, utiliser des clés de maintien (hold/step). Dans un rendu calculé, pour une image f du plan i, scale(f) = scales[i]. Garder les intervalles en images entières, début inclus et fin exclue, à la cadence du montage. Le calcul doit être déterministe à toute position de lecture.

Enregistrer un plan éditable : cadence, début/fin en images, échelle et ancrage de chaque plan. Vérifier les images f−1 et f à chaque raccord, les bords du cadre, la tête et le regard. Ne pas cumuler ce zoom avec celui d’un preset déjà appliqué ; remplacer la couche caméra existante dans la copie de travail.

Créer une nouvelle version de travail. Produire un export seulement si demandé ; livrer le projet et les réglages. Une inspection de la courbe seule ne vaut pas vérification du rendu.
