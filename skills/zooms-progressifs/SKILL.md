---
name: zooms-progressifs
description: "Ajouter un rapprochement ou un éloignement fluide sur une vidéo, avec échelles, ancrage et durée contrôlés."
---

# Zooms progressifs

## Paramètres

Travailler sur le montage final sans toucher à ses coupes, sa vitesse ni son audio. Choisir un début, une fin, une échelle de départ et une échelle d’arrivée ; l’ancrage reste fixe sur le sujet. Partir d’un cadrage remplissant déjà le format. Les sous-titres et éléments graphiques restent hors du conteneur caméra.

Point de départ discret tiré de la composante progressive Steve : multiplier l’échelle de départ par 1,025 sur la durée du plan, interpolation linéaire (ease none). Exemple : 1,12 → 1,148. Ce n’est pas une règle d’intensité universelle : adapter selon la durée, la définition et la marge autour du visage. Un éloignement inverse les bornes, sans descendre sous l’échelle qui remplit le cadre.

## Interpolation reproductible

Pour l’intervalle d’images [a,b), poser n=b−a. Si n<2, conserver l’échelle de départ : un plan d’une seule image ne peut montrer une progression. Sinon u=clamp((f−a)/(n−1),0,1) et scale(f)=s0+(s1−s0)×u. La dernière image atteint exactement s1. En lecture interactive, calculer depuis la position temporelle, pas en cumulant un incrément à chaque rafraîchissement.

Utiliser par défaut une progression linéaire. Pour une demande d’entrée/sortie douce, remplacer u par u²×(3−2u). Sans coupe entre deux segments, la fin du premier égale le début du suivant pour éviter un saut involontaire. Aux coupes, autoriser un nouveau cadrage seulement si le plan le prévoit. Ne pas ajouter automatiquement un zoom sec.

Conserver un plan éditable : cadence, bornes en images, s0, s1, ancrage, courbe. Vérifier début/milieu/fin, lecture à vitesse normale, raccords et bords sans bandes vides. Ne pas appliquer une seconde progression si un preset anime déjà le même conteneur caméra.

Créer une nouvelle version de travail. Produire un export seulement si demandé ; livrer le projet et les réglages. Une inspection de la courbe seule ne vaut pas vérification du rendu.
