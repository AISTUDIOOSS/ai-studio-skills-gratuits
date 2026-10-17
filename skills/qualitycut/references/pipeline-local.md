# Pipeline local et contrat Steve 01

Les scripts proviennent de coupes-uptrainer v1.0.0 fourni par Nico. [Le document d'origine](uptrainer-original.md) détaille les algorithmes ; en cas de contradiction éditoriale, SKILL.md fusionné fait référence. [QualityCut original](qualitycut-original.md) est conservé pour comparaison.

## Préparer

Mac Apple Silicon, Python 3.9–3.12, FFmpeg et ffprobe. Installer requirements.txt dans un environnement isolé si nécessaire. Choisir un nouveau dossier de travail par rush/révision hors synchronisation ; éviter de relancer preparer.sh sur une analyse finalisée, car les indices de mots peuvent changer.

```sh
PYTHON=/chemin/venv/bin/python bash /chemin/qualitycut/scripts/preparer.sh /chemin/job /chemin/rush.mp4
export MONTAGE_DOSSIER=/chemin/job
```

Normalisation AVANT l'analyse : source verticale 1080×1920, 30 i/s constantes, audio 48 kHz et 16 kHz. Vérifier rotation/cadrage. Conserver le rush original. La normalisation n'est pas à imposer à une timeline native existante.

preparer.sh effectue : transcription entière, transcription par régions de parole, alignement, recherche des zones parlées manquantes, fusion avec la première passe, nouvel alignement, liste numérotée. Lire transcription/LISTE-MOTS.txt entièrement ainsi que RUSH-zones-a-revoir.json. Ce second fichier signale les sons courts sans les ajouter automatiquement au texte. Examiner les zones qui touchent les passages retenus, les bords ou une fusion envisagée ; consigner leur classement dans la revue. Une absence de signalement ne prouve pas une absence de reprise.

Écrire montage/RUSH.txt, une sélection par ligne : `premier_index-dernier_index # motif`. Les indices commencent à zéro et appartiennent uniquement à cette transcription. Garder la transcription source ; corrections textuelles facultatives dans montage/RUSH-texte.json.

## Couper et vérifier

Avec le python de cet environnement, et MONTAGE_DOSSIER défini :

```sh
python /chemin/qualitycut/scripts/couper.py RUSH
python /chemin/qualitycut/scripts/appliquer_revue.py RUSH
python /chemin/qualitycut/scripts/verifier.py RUSH
python /chemin/qualitycut/scripts/blancs.py RUSH
python /chemin/qualitycut/scripts/ecouter.py RUSH
python /chemin/qualitycut/scripts/zone.py RUSH 43.0-47.0
python /chemin/qualitycut/scripts/exporter_cuts.py RUSH
```

zone.py s'utilise sur les zones problématiques, pas systématiquement à 43–47 s. ecouter.py et zone.py retranscrivent : ce ne sont pas une écoute humaine ou multimodale. Un mot retrouvé par ASR ne garantit pas une consonne entière.

Pour préserver une zone que le calcul a coupée à tort, écrire montage/RUSH-revue.json :

```json
{"joins":[{"leftLastWord":145,"rightFirstWord":146,"reason":"La coupe retirait la fin utile du mot.","classification":"continuite_voix","audioReview":{"method":"ecoute_multimodale","observation":"Fin du mot identifiée dans la zone ajoutée ; aucune reprise."}}]}
```

Ces indices sont illustratifs : ne pas copier cette attestation sans avoir réellement examiné le son. Utiliser ecoute_humaine ou ecoute_multimodale selon la méthode réellement disponible. Une ASR ne remplit pas cette condition. Les anciens fichiers de revue sans ces champs doivent être réexaminés. appliquer_revue.py réunit les plans autour de ces mots après couper.py. Il exige une classification et une attestation de revue sonore ; il refuse les indices de mots non consécutifs, un couple introuvable, une mauvaise cadence ou un motif vide. Il ne peut pas détecter les mots absents de la transcription ni prouver la sincérité de l’attestation. Il est idempotent ; relancer après chaque nouveau calcul. Archiver ce fichier avec la liste de mots correspondante. Pour d'autres modifications de bornes, documenter et vérifier la correction localement ; ne pas déplacer les mots pour dissimuler une coupe incertaine.

## Export interne et contrôle avant livraison

Après les contrôles automatiques, produire l’export interne et appliquer [revue-avant-livraison.md](revue-avant-livraison.md) sur ce fichier. Ne pas le présenter avant la revue complète. La transcription de verifier.py porte sur un audio reconstruit depuis les coupes : elle ne vérifie ni les images ni l’encodage du MP4 livré.

## Sorties

- RUSH-cuts.json : intervalles source en images, début inclus/fin exclue.
- RUSH-analysis-minimale.json : mots et groupes simples, pas une composition éditoriale finale.
- RUSH-plans.txt et RUSH-rapport.md : plans, mesures et risques. Ajouter les décisions de revue et le statut d'écoute après le dernier export, qui réécrit le rapport.
- sources/RUSH.mov : source exacte à donner au moteur ; ne pas appliquer les indices au rush original à une autre cadence.

exporter_cuts.py peut recaler les timestamps des mots dans un plan pour satisfaire le moteur. Ces ajustements doivent rester visibles dans le rapport, avec l'alignement original conservé. L'acceptation du JSON ne constitue pas une validation audio.

```sh
node cli.cjs from-source --source /chemin/job/sources/RUSH.mov --analysis /chemin/job/montage/RUSH-analysis-minimale.json --cuts /chemin/job/montage/RUSH-cuts.json --config examples/config.json --out build/RUSH-nouvelle-version
```

Cette commande crée le projet avec les groupes minimaux. Pour un montage habillé, le planificateur Steve doit préparer ses vrais groupes et zooms avant le rendu. Ne pas changer les coupes validées pendant cette passe d'habillage.

## Portée de l'aligneur

Le modèle MMS_FA livré par le pipeline original est indiqué CC-BY-NC 4.0 (usage non commercial) dans la documentation UpTrainer. Le bundle reste un prototype d'essai ; l'intégration dans un service commercial nécessite un aligneur compatible et une nouvelle comparaison des bords. Ne pas présenter cette fusion comme prête pour un déploiement commercial.
