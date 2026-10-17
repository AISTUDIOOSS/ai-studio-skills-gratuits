# Contrat du profil descriptif — version 1

Le JSON est une fiche structurée destinée à la bibliothèque d’inspirations, pas un format d’import Premiere, Remotion ou HyperFrames.

Champs racine :
- `schema_version`: `1`.
- `id`: identifiant stable choisi à la création ; conserver l’ID si révision explicite.
- `kind`: `global-editing`. Les références motion isolées seront gérées par leur fonction dédiée.
- `title`: titre court décrivant le style.
- `source`: objet `url`, `local_file`, `creator`, `duration_seconds`, `width`, `height`, `fps`, `analysis_date`. Valeurs inconnues à `null` ; les chemins sont relatifs au dossier livré lorsque possible.
- `coverage`: `mode` parmi `full`, `sampled`, `source-report-only`, `unavailable` ; `reviewed_ranges` tableau de paires `[début, fin]` en secondes ; `audio` parmi `inspected`, `transcript-only`, `not-inspected`, `unavailable` ; `timing_precision_seconds` nombre ou `null` ; `limitations` liste de textes. Pour une reprise de rapport, conserver sa provenance et ne pas affirmer une nouvelle inspection du média.
- `evidence`: liste d’objets avec `id`, `start_seconds`, `end_seconds`, `modality` (`visual`, `audio`, `audiovisual`, `source-report`), `observation`, `asset` (chemin ou `null`).
- `rules`: liste d’objets avec `id`, `category` (`rhythm`, `cuts`, `framing`, `text`, `motion`, `transitions`, `sound`, `color`), `statement`, `basis` (`observed`, `inferred`, `proposed`), `evidence_ids`, `trigger`, `parameters`, `avoid_when`, `implementation`.
- `implementation`: dans chaque règle, objet `status` (`verified`, `candidate`, `unsupported`, `unknown`), `target`, `test_evidence` (texte/localisation ou `null`), `notes`. Sans test, jamais `verified`.
- `unknowns`: liste des informations non déterminées.
- `adaptation_brief`: texte autonome décrivant comment reprendre les mécanismes avec le contenu de l’utilisateur. Ne pas inclure d’engagement de reproduction exacte.

`parameters` est un objet libre : chaque valeur quantitative non directement mesurée doit être qualifiée dans son nom ou sa description (exemple `suggested_duration_seconds`). Conserver séparément les données observées et les paramètres proposés.

Contraintes : nombres temporels finis et positifs ou nuls ; fin strictement supérieure au début ; toutes les preuves contenues dans les plages effectivement examinées. `source-report-only` signale une conversion documentaire et ne certifie pas un essai audiovisuel. Une source inaccessible produit un rapport de limitation, pas une fausse bibliothèque de règles.
