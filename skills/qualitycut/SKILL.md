---
name: qualitycut
description: "Dérusher et resserrer les vidéos parlées selon le style de Nico : choix des prises, double transcription, alignement des mots, coupes calculées sur le son et contrôle des raccords. Utiliser pour QualityCut, des coupes facecam, un Reel parlé ou une interview ; produire les coupes pour Steve 01 ou intervenir dans la timeline demandée."
---

# QualityCut — fusion UpTrainer

Version révisée du 13 octobre 2026 : contrôle obligatoire avant présentation du résultat. Associer le jugement éditorial QualityCut à la préparation et aux scripts de coupes UpTrainer. Le résultat C0210 de 62,7 s a été jugé propre par Nico ; il constitue une référence, pas une durée cible pour les autres rushs.

## Choisir le flux

- Rush français, une voix, fichier local destiné à Steve 01 : lire [pipeline-local.md](references/pipeline-local.md), puis utiliser les scripts fournis. La préparation, la sélection et le calcul de coupes sont des étapes distinctes : les scripts ne choisissent pas seuls les prises.
- Timeline Premiere ou Palmier explicitement demandée : lire [timeline.md](references/timeline.md). Appliquer les mêmes priorités éditoriales dans la cadence et le projet existants. Ne pas substituer une livraison JSON à une modification de timeline demandée.
- Autre langue, plusieurs voix : les scripts UpTrainer ne couvrent pas ce cas ; employer les outils adaptés à la source et garder les principes QualityCut. Ne pas présenter ce pipeline français comme validé dans ces conditions.

## Choisir les prises

Lire la transcription complète avant de sélectionner ; pour le flux local, lire LISTE-MOTS.txt en entier après le dernier alignement.

- Par défaut, garder la dernière prise complète d'une phrase. Préférer une prise antérieure si la dernière contient une erreur, un mot écorché ou si l'écoute montre une meilleure formulation naturelle et complète ; noter le motif.
- Privilégier une prise continue. Assembler plusieurs prises seulement pour sauver une formulation utile indisponible en prise complète, avec mots entiers, sens conservé et raccord vérifié. Ne pas le faire automatiquement pour gagner quelques images.
- Retirer faux départs, hésitations, reprises, autocorrections, commentaires hors contenu et préparations. Conserver répétitions voulues, négations, réserves, chiffres et étapes du raisonnement.
- Une ouverture suivie de plus de 3 s de silence puis d'une autre ouverture peut être abandonnée. Une continuation (« Et… ») ne constitue pas à elle seule une autre ouverture.
- Dans le doute, examiner le son avec son contexte et identifier le contenu : mot utile, reprise abandonnée, respiration ou bruit. Un mot absent de la transcription peut être une reprise. Ne pas choisir automatiquement de le conserver ou de le supprimer ; consigner et résoudre le doute avant livraison.

## Poser les bords

Priorité : mots entiers et sens, absence de temps mort, naturel vocal, rythme, puis continuité visuelle. Voir [nico-cut-profile.md](references/nico-cut-profile.md) pour les mesures de référence.

Sur une source locale normalisée à 30 i/s, le calcul UpTrainer est le réglage initial : attaque avec marge technique de 10 ms, fin de voix sous -45 dB tenue 60 ms, seuil de voix -50 dB, retrait des blancs alignés de plus de 0,22 s dans les passages retenus. Les scripts adaptent les seuils au bruit mesuré. Ces calculs proposent des bords ; ils ne prouvent pas l'intégrité phonétique.

- Ne pas ajouter de padding arbitraire après le calcul. Une correction locale motivée prime sur le seuil ; ne pas considérer chaque intervalle sans mot aligné comme du silence réel.
- Contrôler les zones supprimées qui contiennent du son, y compris les événements courts absents du texte. Réunir des plans uniquement après identification et écoute réelle du contenu réintroduit, avec justification dans appliquer_revue.py. Une concordance des indices de mots ne protège pas contre un mot non transcrit.
- Repères facecam UpTrainer : environ 0,05–0,09 s de blanc au raccord, maximum visé 0,18 s ; plans souvent de 2–3 s. Le profil historique QualityCut observe souvent 1–2 s. Aucun de ces chiffres n'impose de couper une phrase fluide.
- Fin de vidéo : terminer après la dernière syllabe entière, sur sa retombée acoustique, sans rallonge automatique. Examiner les dernières images pour exclure le relâchement de fin de prise ou le geste vers la caméra ; un mouvement silencieux échappe au contrôle audio. Si le geste commence pendant la parole utile, préserver la parole et résoudre ce cas localement.
- Coupes franches, audio/vidéo liés, vitesse inchangée. Pas de fondu automatique ; finition audio séparée si nécessaire.

## Vérifier avant de présenter le résultat

L’export est une étape interne. Le cycle obligatoire est : montage → export interne → revue du fichier exporté → corrections → nouvel export → nouvelle vérification → livraison. Pour une demande limitée à une timeline, revoir intégralement la lecture de la version sauvegardée avant de la présenter. Lire [revue-avant-livraison.md](references/revue-avant-livraison.md).

- Effectuer une écoute et un visionnage complets à vitesse normale, puis examiner chaque raccord et chaque zone réintroduite. Rechercher reprises, mots doublés ou coupés, hésitations, temps morts et gestes de fin de prise.
- Utiliser la retranscription et les mesures comme contrôles complémentaires. Le même modèle peut omettre la même reprise dans le rush et le montage ; une seconde transcription ne remplace pas l’écoute.
- Corriger les anomalies et contrôler la version effectivement livrée. Toute correction invalide la validation précédente du fichier ; garder les décisions et le statut de revue associés à cette version.
- Si aucune capacité d’écoute réelle ou de visionnage n’est disponible, terminer le travail réalisable, expliquer précisément ce qui empêche la validation et ne pas présenter l’export non vérifié comme le résultat. Un aperçu provisoire n’est transmis que si l’utilisateur le demande explicitement. Ne pas simuler une écoute par ASR ou par simple lancement d’un lecteur.
- Après validation, livrer coupes, source de référence, rapport et vidéo si demandée. Aucun sous-titre stylistique, zoom ou accent à ajouter sans demande ; transmettre ensuite au moteur Steve 01 lorsque demandé.

Le moteur ne charge pas ce SKILL.md tout seul : l’agent doit suivre le flux et lui fournir les fichiers. Ne pas annoncer une intégration automatique tant que l’appelant du moteur n’a pas été branché.
