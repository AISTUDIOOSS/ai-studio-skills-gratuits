---
name: coupes-uptrainer
description: Couper un rush face caméra (pub, facecam) à la manière validée par UpTrainer le 04/10/2026 — une seule prise par phrase, aucun faux départ, aucun blanc, chaque mot entier, bords posés au son à l'image près. Produit la liste des plans gardés, un cuts.json prêt pour le moteur Steve 01 (30 i/s) et un rapport des points à écouter. Utiliser quand on demande de « faire les coupes », « dérusher », « nettoyer les reprises » d'un rush parlé en français. Ne fait PAS l'habillage (sous-titres, zooms, son, export).
---

# Coupes UpTrainer (v1.0.0, 13/10/2026)

Ce skill reproduit la coupe des pubs C0208-C0213 de Steeve (04/10/2026, resserrée le 05/10). Il ne fait que les coupes :
quels passages garder, et où poser chaque bord. L'habillage (sous-titres, cadrage, son, export) est le travail du moteur
Steve 01 de Nico, qui reprend le `cuts.json` produit ici.

Ce qu'il ne fait pas : choisir un B-roll, réécrire le texte, monter plusieurs caméras, traiter deux voix ou une autre
langue que le français. Il ne remplace jamais l'écoute : il prépare les raccords et dit lesquels écouter en premier.

## 1. Choix des prises (le jugement, fait par l'IA ou le monteur)
On lit `transcription/LISTE-MOTS.txt` EN ENTIER avant de choisir, puis on écrit `montage/<rush>.txt`.
- **Une prise par phrase : la dernière prise COMPLÈTE.** Pas un collage de morceaux de plusieurs prises. Exception : une prise
  plus ancienne quand la dernière contient une erreur (chiffre faux, mot écorché).
- **Retirés** : faux départs (« On a, on aide » → « on aide »), reprises, mots répétés par hésitation, autocorrections
  (« comme toi, comme vous » → « comme vous »), « euh », jurons et commentaires hors pub (« ah merde », « c'est dur de
  réfléchir »), ce qui est dit avant le vrai départ et après la fin (« merci »).
- **Accroche abandonnée** : une phrase d'ouverture suivie d'un long silence (plus de 3 s) puis d'une AUTRE ouverture a été
  laissée tomber : on ne la garde pas, et on le signale en une ligne.
- **On ne réécrit rien.** Le sens reste celui de la personne : aucune négation, réserve ou étape de raisonnement retirée ;
  jamais deux phrases recollées pour dire autre chose. Une répétition voulue (« de tes 5 000, de tes 10 000 ») reste.
- Dans le doute sur un passage : `zone.py` (réécoute de la zone), puis on garde plutôt qu'on ne coupe.

Format de `montage/<rush>.txt` : une ligne par passage gardé, `premier_mot-dernier_mot  # commentaire`, dans l'ordre.
Les numéros sont ceux de LISTE-MOTS.txt (ils changent si on retranscrit : ne jamais réutiliser une vieille sélection).
Corrections de texte facultatives : `montage/<rush>-texte.json` (`{"n° du mot": "texte corrigé"}`, `""` pour masquer).

## 2. Règles de bord (appliquées par `couper.py`, chiffres validés)
- Un plan **démarre au plus une image avant la parole** : marge de 10 ms avant l'attaque, jamais de blanc devant.
- Un plan **s'arrête quand la voix est retombée** : son sous **-45 dB tenu 60 ms** ; la traîne et le souffle de fin sont
  coupés ; marge de 10 ms. Si l'alignement place la fin du mot trop tard, on recule jusqu'à la vraie fin de voix.
- **Tout blanc de plus de 0,22 s** entre deux mots d'un passage gardé est retiré (coupe franche), respiration comprise.
- Repères à retrouver dans le rapport : blanc à une coupe **~0,09 s en moyenne** (~0,05 s depuis le resserrage du 05/10),
  **jamais plus de 0,18 s** ; une coupe toutes les 2 à 3 s ; **0,4 s** de respiration après le dernier mot.
- Seuil de voix -50 dB ; prise bruyante : les seuils remontent seuls juste au-dessus du bruit mesuré dans les pauses.
- Coupes franches, pas de fondu systématique. Un plan très court (0,4 s) est normal (« comme vous. »).
- Jamais de marge fixe ajoutée à la main, jamais de suppression automatique des silences sur tout le fichier.

## 3. Déroulé pas à pas
Dossier de travail = n'importe quel dossier vide, hors d'un dossier synchronisé. Toutes les commandes lisent
`MONTAGE_DOSSIER` (sinon le dossier courant). `PYTHON` peut désigner le python de l'environnement virtuel.
1. **Préparer** : `scripts/preparer.sh <dossier> <rush.mp4> [autres rushs]`
   - mise au format : vertical 1080 × 1920, **30 images/s constantes**, couleurs normales (`sources/<rush>.mov`). Tout le
     reste se mesure sur ce fichier : c'est aussi la source à donner à `from-source` ;
   - son 16 kHz et 48 kHz (`audio/`) ;
   - **transcription en deux passes et recollage** : vidéo entière, puis par morceaux de parole coupés aux blancs (c'est elle
     qui fait apparaître les reprises), compléments des zones parlées sans mot, recollage des passages perdus ;
   - alignement des mots (début et fin à ~20 ms) ;
   - `transcription/LISTE-MOTS.txt` : `n°:mot@début`, les blancs marqués.
2. **Choisir** : lire LISTE-MOTS.txt, écrire `montage/<rush>.txt` (règles du § 1).
3. **Couper** : `MONTAGE_DOSSIER=<dossier> python3 scripts/couper.py <rush>` → `montage/<rush>-coupes.json`.
4. **Vérifier** : `python3 scripts/verifier.py <rush>` assemble le son des plans, le retranscrit par morceaux et compare au
   texte attendu. Écart = reprise restée, mot coupé ou « euh » oublié (les écritures de nombres « 5000 / 5 000 » sont
   normales). Il liste aussi les raccords posés sur du son. Puis `blancs.py <rush>` (un blanc retiré contient-il de la
   parole ?), `ecouter.py <rush>` (que dit-on dans ces blancs ?) et `zone.py <rush> 12.3-15.0` (profil du son + transcription
   d'une zone seule). On corrige la sélection, on recoupe, on revérifie.
5. **Sortir** : `python3 scripts/exporter_cuts.py <rush>` → dans `montage/` :
   - `<rush>-plans.txt` : plans gardés en secondes ;
   - `<rush>-cuts.json` : contrat du moteur Steve 01 (images entières à 30 i/s, début inclus, fin exclue) ;
   - `<rush>-analysis-minimale.json` : mots + sous-titres simples, pour lancer `from-source` tout de suite ;
   - `<rush>-rapport.md` : durée avant/après, nombre de coupes, blanc moyen et maximum, points à écouter.
6. **Écouter chaque raccord** (et d'abord ceux du rapport) avant de dire que c'est bon. Sans écoute : livrer « pour revue ».

Enchaîner avec le moteur Steve 01 :
`node cli.cjs from-source --source <dossier>/sources/<rush>.mov --analysis <dossier>/montage/<rush>-analysis-minimale.json --cuts <dossier>/montage/<rush>-cuts.json --config examples/config.json --out build/<rush>-v1`

## 4. Moteur et coupe : qui gagne
Le moteur refuse une coupe qui traverse un mot. Nos bords coupent parfois 1 à 2 images dans la fin alignée d'un mot (la
voix est déjà retombée). Règle : **la coupe ne bouge jamais** ; `exporter_cuts.py` recale le mot dans son plan (pour le
sous-titre seulement) et le liste dans le rapport quand l'écart atteint 2 images. Le moteur n'a pas de durée minimale de plan.

## 5. Pièges déjà payés
- Whisper sur la vidéo entière **fusionne les reprises** et « étire » un mot par-dessus plusieurs secondes de parole ; par
  morceaux il perd des passages. Il faut les deux passes + compléments + recollage (preparer.sh). Vu le 13/10 : avec la passe
  entière seule, 3 reprises restaient dans 2 pubs sur 3.
- Les temps de mots de whisper ne suffisent PAS pour poser les bords : ils collent les mots entre eux et annoncent le début
  jusqu'à 0,6 s trop tôt. Sans alignement, on mesure 0,13 à 0,24 s de blanc par coupe (au lieu de 0,05) et un tiers de
  coupes en moins. Toujours aligner avant de couper.
- Fins de phrase trop longues : la traîne de voix entre -45 et -50 dB s'entend comme un blanc. Ne pas remonter le seuil
  au-dessus de -45 dB (la coupe tomberait sur de la voix), ne pas le baisser non plus.
- Une re-transcription du montage ENTIER peut ne pas voir une phrase dite deux fois : `verifier.py` retranscrit par morceaux,
  ne pas le remplacer par une passe globale. Une transcription qui retrouve le mot ne prouve pas que sa consonne est entière.
- Changer la cadence après la transcription décale tout : mise au format D'ABORD, puis tout le reste sur ce fichier.
- Les numéros de mots changent d'une transcription à l'autre : une sélection ne vaut que pour SA liste de mots.
- Whisper recopie parfois la consigne ou boucle (« Ah Ah Ah ») : les scripts l'écartent, mais relire la liste.

## 6. Licence de l'alignement — ESSAI INTERNE SEULEMENT
`aligner.py` utilise le modèle d'alignement **MMS_FA** (torchaudio), publié sous licence **CC-BY-NC 4.0 : usage non
commercial**. Il convient pour tester et comparer ; il ne peut pas tourner tel quel dans un service vendu à des clients.
Une version sans alignement a été mesurée le 13/10 : elle ne redonne que ~70 % des bords à une image près ; elle n'est donc
pas livrée ici. Avant toute mise en service, remplacer ce modèle par un aligneur à licence commerciale et refaire la mesure.
Le reste : mlx-whisper (MIT, modèle Whisper large-v3 sous licence MIT), numpy/scipy (BSD), ffmpeg (selon la compilation).
