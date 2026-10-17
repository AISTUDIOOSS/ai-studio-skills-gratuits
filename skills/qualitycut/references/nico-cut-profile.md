# Profil de cut Nico

## Référence mesurée

Référence issue de `REEL 5 NICO`, timeline finale analysée à 48 fps :

- Source : 226,6 s ; final : 52,21 s ; environ 23 % conservés.
- 26 clips et 25 raccords, sans gap ni overlap.
- Durée médiane d’un clip : 1,95 s ; moyenne : 2,01 s.
- Plage observée : 27 à 200 images, soit 0,56 à 4,17 s.
- Niveau RMS médian sur les 20 premières ms : -15,9 dBFS.
- Niveau RMS médian sur les 20 dernières ms : -43,2 dBFS.
- Discontinuité médiane aux raccords : -22,2 dBFS ; cas les plus abrupts autour de -8 à -10 dBFS.
- Distance médiane au passage par zéro le plus proche : 0,25 ms en entrée, 0,60 ms en sortie.
- Aucun fondu audio automatique dans la sélection de référence.

Ces valeurs décrivent le résultat ; ce ne sont pas des seuils absolus.

## Signature éditoriale

- Débit reconstruit, beaucoup plus dense que le débit réel.
- Suppression agressive des attentes, préparations, reprises et fins de prise.
- Entrée au plus près de la première consonne utile, parfois avec une voix déjà énergique.
- Sortie après la dernière syllabe intelligible, généralement lorsque l’énergie a fortement chuté.
- Aucune respiration ou marge conservée par principe.
- Décision locale, à l’écoute et dans la forme d’onde, jamais par padding fixe.
- Hard cuts pendant la sélection ; finition audio séparée.

## Erreurs interdites

- Laisser des blancs simplement parce qu’ils se trouvent à l’intérieur d’un clip.
- Garder systématiquement quelques images « de sécurité ».
- Supprimer une fin de mot faible en la confondant avec un souffle.
- Faire confiance à la transcription seule pour les bords acoustiques.
- Faire confiance au niveau sonore seul pour l’intelligibilité.
- Déclarer le montage propre sans relire la transcription après les trims.

## Ordre de priorité

1. Mot entier et intelligibilité.
2. Absence de temps mort.
3. Naturel du raccord vocal.
4. Densité et rythme.
5. Continuité visuelle.
