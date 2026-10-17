# Workflow Premiere enregistré de Nico

Cette procédure vient de la démonstration utilisateur enregistrée le 4 septembre 2026 dans Adobe Premiere Pro 26. Elle décrit l’intention et l’ordre des actions, pas des coordonnées d’écran rejouables.

## Préconditions

- Confirmer que la bonne séquence est active et que le panneau Montage a le focus.
- Garder « Sélection liée » active afin que l’audio et la vidéo soient traités ensemble.
- Ouvrir `Texte > Transcription`, puis cliquer `Transcrire` si la séquence n’a pas encore de transcription.
- Limiter la passe à la plage demandée par l’utilisateur.
- Identifier dans la transcription la meilleure prise conforme au script avant de supprimer quoi que ce soit.

## Boucle de coupe démontrée

1. Utiliser `L` pour lire vers l’avant et `Espace` pour arrêter au voisinage d’un raccord.
2. Affiner visuellement et à l’écoute la position de la tête de lecture.
3. Appuyer sur `S` pour activer l’outil Cutter, puis cliquer exactement sur le clip à la tête de lecture. Vérifier que les parties audio et vidéo liées sont coupées ensemble.
4. Appuyer sur `A` pour revenir à l’outil Sélection.
5. Cliquer le segment de faux départ, reprise, silence, respiration ou déchet à retirer.
6. Appuyer sur `D`, raccourci personnalisé observé dans la démonstration, pour supprimer le segment avec ripple.
7. Vérifier immédiatement que le plan suivant s’est refermé sans gap et que l’audio reste lié à la vidéo.
8. Reprendre la lecture et répéter la boucle. Utiliser `Commande-Z` dès qu’une coupe mord un mot, vise le mauvais segment ou produit un raccord incorrect.

## Interprétation des raccourcis

- `S` : outil Cutter dans la configuration Premiere française observée.
- `A` : outil Sélection.
- `D` : suppression ripple personnalisée de Nico. Ne pas supposer que ce raccourci existe dans une autre configuration ; vérifier son effet après la première suppression.
- `L` : lecture avant, éventuellement répétée pour accélérer.
- `Espace` : lecture/pause.
- `Commande-Z` : annulation.

## Règles d’automatisation Computer Use

- Piloter l’interface à partir des libellés accessibles, de la position courante de la tête de lecture et de l’état visible des outils.
- Ne pas rejouer les coordonnées de la démonstration : elles dépendent de l’écran, du zoom et de la disposition des panneaux.
- Avancer par petites suppressions vérifiables. Après chaque `D`, confirmer visuellement la fermeture du gap avant de continuer.
- Si `D` ne fait pas une suppression ripple dans le projet courant, arrêter avant toute autre suppression et demander à l’utilisateur de rétablir son mapping.
- Ne jamais dissocier volontairement l’audio et la vidéo pour cette passe.

## Contrôle final Premiere

1. Rejouer toute la plage montée depuis quelques images avant son début jusqu’à quelques images après sa fin.
2. Vérifier l’absence de faux départs, répétitions, respirations gênantes, mots mangés, gaps et désynchronisations.
3. Vérifier la conformité au script dans le panneau Transcription.
4. Sauvegarder avec `Commande-S` seulement après cette vérification complète.
