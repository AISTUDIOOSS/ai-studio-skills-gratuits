---
name: qualitycut
description: "Monter et resserrer chirurgicalement des vidéos parlées dans Palmier Pro ou Adobe Premiere Pro selon le style de cut de Nico : sélection des meilleures reprises, suppression des silences, souffles, préparations et déchets, attaques verbales immédiates, sorties très courtes, ripple propre et vérification mot à mot. Utiliser quand l’utilisateur demande QualityCut, un montage parlé dense, un Reel très rythmé, le nettoyage précis d’une interview ou d’un talking head, ou de reproduire la façon de couper de Nico."
---

# QualityCut

Produire un montage parlé dense sans silence parasite ni mot mangé. Traiter chaque bord individuellement ; ne jamais appliquer un padding ou un seuil sonore universel.

Lire [references/nico-cut-profile.md](nico-cut-profile.md) avant toute modification. Dans Adobe Premiere Pro, lire aussi [references/premiere-recorded-workflow.md](premiere-recorded-workflow.md).

## Choisir l’environnement

- Dans Palmier Pro, suivre le flux MCP ci-dessous.
- Dans Adobe Premiere Pro, utiliser Computer Use et le flux démontré dans la référence Premiere.
- Ne jamais transposer des coordonnées enregistrées : retrouver la séquence, la tête de lecture, les clips liés et les commandes par leur état visible et leurs libellés accessibles.

## Préparer l’analyse

1. Dans Palmier, connecter le MCP et ouvrir explicitement le projet demandé avec `manage_project`. Dans Premiere, confirmer que l’application et la bonne séquence sont visibles.
2. Dans Palmier, appeler `get_timeline` et `get_media`. Dans Premiere, relever la durée, les pistes ciblées, l’état de « Sélection liée » et l’absence de verrouillage bloquant.
3. Lire la transcription complète avec `get_transcript` dans Palmier. Dans Premiere, ouvrir `Texte > Transcription` et lancer `Transcrire` si nécessaire.
4. Lire d’abord les segments, puis les mots autour des reprises et raccords sensibles.
5. Si l’utilisateur a fourni une zone montée en exemple, l’analyser avant d’éditer : trims source, attaques, sorties, silences internes, audio lié et logique de sélection.

## Sélectionner les prises

1. Isoler les faux départs, répétitions, reformulations et blocs exploitables.
2. Garder la formulation la plus complète et naturelle, pas automatiquement la dernière.
3. Reconstruire une phrase à partir de plusieurs prises seulement si chaque jonction conserve les mots entiers et reste intelligible.
4. Utiliser `remove_words` pour les déchets alignés sur des mots. Après chaque appel, relire la transcription car les indices changent.
5. Utiliser `ripple_delete_ranges` pour les souffles, attentes, préparations ou zones non verbales qui ne suivent pas les mots.
6. Grouper les suppressions connues dans un appel quand les coordonnées appartiennent au même état de timeline.

## Régler les bords

- Entrer au premier élément phonétique utile. Ne conserver aucune inspiration par défaut.
- Sortir dès que la dernière syllabe utile est acquise et que la voix retombe.
- Supprimer les souffles, expirations, bruits de bouche, gestes d’attente et queues de prise sans information.
- Ne jamais utiliser une marge fixe de 6, 8 ou 12 images.
- Ne jamais décider à partir du seul niveau sonore : une fin de mot faible peut ressembler à un souffle.
- Vérifier les consonnes faibles, fins de mots et mots courts avec la transcription en granularité `words`.
- Conserver audio et vidéo liés et couper sur la même image.
- Fermer chaque suppression par ripple ; ne laisser aucun gap involontaire.

## Encadrer l’automatisation

- Ne pas exécuter `remove_silence` sur toute la timeline comme résultat final sans contrôle.
- Si `remove_silence` aide au dérushage, le limiter à des clips ciblés, puis vérifier immédiatement la transcription complète.
- Si un mot utile disparaît ou raccourcit, appeler `undo` immédiatement et reprendre manuellement.
- Ne pas utiliser un seuil RMS global pour tous les locuteurs ou tous les clips.
- Ne pas interpréter le nom d’un fichier comme preuve de son contenu.

## Construire le rythme

- Viser des blocs généralement compris entre 1 et 2 secondes, sans rendre cette durée obligatoire.
- Conserver un bloc plus long si son débit reste tendu et informatif.
- Accepter les jump cuts francs : le rythme et l’intelligibilité priment sur la continuité corporelle parfaite.
- Pendant la phase de sélection, ne pas ajouter automatiquement de fondu ou crossfade.
- Réserver les microfondus à une passe audio séparée et seulement aux raccords réellement audibles.

## Vérifier obligatoirement

1. Relire toute la transcription en `words` après les suppressions.
2. Comparer le texte final avec la sélection voulue ; aucune syllabe ou mot faible ne doit manquer par accident.
3. Appeler `get_timeline` et confirmer : aucun gap, aucun overlap, audio lié, vitesse inchangée, ordre correct.
4. Inspecter les raccords où un clip faible rejoint une attaque forte ; signaler les risques de clic avant d’ajouter un fondu.
5. En cas de surcoupe détectée juste après une action, utiliser `undo`, relire l’état, puis refaire le raccord.
6. Ne déclarer la passe terminée qu’après ces contrôles.

## Communiquer

Indiquer la durée avant/après, le nombre de blocs, les reprises supprimées et les vérifications effectuées. Distinguer clairement : sélection, nettoyage des bords, puis finition audio.
