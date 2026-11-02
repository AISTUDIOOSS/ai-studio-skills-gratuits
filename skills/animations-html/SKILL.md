---
name: animations-html
description: Affiche dans la conversation, en HTML animé, les animations d'une vidéo analysée avec analyze-editing-inspiration (sous-titres, mots géants, écrans texte, vignettes, transitions, zooms…). Maquettes 9:16 qui tournent en boucle, avec bouton Rejouer et sélecteur de vitesse, rendues avec show_widget, directement dans le chat. Pas de fichier, pas de navigateur. À utiliser quand l'utilisateur dit « sors-moi les animations en HTML », « montre-les dans le chat », « fais les animations ici », ou lance /animations-html après /analyze-editing-inspiration.
---

# Animations en HTML dans le chat

Étape 2 après `analyze-editing-inspiration` (qui reste le seul skill d'analyse, on ne le modifie pas). Ce skill lit son analyse et **montre les animations animées dans la conversation** avec `mcp__visualize__show_widget`. Rien n'est écrit sur disque, rien ne s'ouvre dans le navigateur ni en Artifact.

## Trouver l'analyse
1. Si l'analyse a été faite plus tôt dans cette conversation : partir de là.
2. Sinon, demander à l'utilisateur le dossier de son analyse.
3. Lire `style-card.md` et `style-profile.json`. Les animations à montrer sont les règles de catégorie `text`, `motion`, `transitions` et `framing` (zooms) ; leurs `parameters` (durées, courbes, tailles, couleurs) et les `evidence` liées donnent timecodes et observations. `basis` (`observed` / `inferred` / `proposed`) passe tel quel sur l'étiquette.
4. Ouvrir 2–3 images de preuve (`asset` des evidence, ou planches du dossier) pour caler couleurs, positions et proportions.
5. Il manque un détail (durée, courbe) ? Reconstruire et étiqueter « proposé ». Aucune analyse ? Proposer de lancer `/analyze-editing-inspiration` d'abord. Si l'utilisateur décrit lui-même les animations, partir de sa description, tout en « proposé ».

## Rendu
1. Appeler **en silence** `mcp__visualize__read_me` avec `{"modules":["interactive"],"platform":"desktop"}` (une fois par conversation ; ne pas en parler).
2. **Un widget par famille** (ou par groupe de 4–8 animations) : ex. « sous-titres », « écrans texte », « vignettes et transitions ». Au-delà de 8 maquettes, découper en plusieurs widgets. `title` en snake_case précis (`<slug>_sous_titres`).
3. Structure de chaque widget — reprendre le modèle de `exemples/vignette_flottante_animations.html` et `exemples/sous_titres_visage_et_ecrans_texte.html` (les lire avant d'écrire) :
   - `<h2 class="sr-only">` qui décrit le widget ;
   - une barre : bouton **Rejouer tout** + sélecteur **Vitesse** (1× / 0,5× / 0,25×) qui règle une variable CSS `--k` multipliant toutes les durées ;
   - une grille `repeat(auto-fit,minmax(140px,1fr))` de **maquettes 9:16** (140 × 249 px, coins 12 px) ;
   - dans chaque maquette, un décor simple qui évoque le plan de la vidéo (fond, silhouette en formes CSS, couleurs prises sur les frames) — jamais de photo ni de visage réel ;
   - l'animation en `@keyframes` CSS, **boucle infinie**, durées et courbes reprises de l'analyse (entrée, maintien, sortie, puis pause), mises à l'échelle de la maquette (tailles en % de la hauteur → px sur 249) ;
   - sous la maquette : `id · nom` (ex. « a03 · Pop du mot géant ») + une ligne : timecode(s), durée d'entrée, et `observé` / `inféré` / `proposé` ;
   - un petit `<script>` de replay (`animation='none'` → reflow → `''`).
4. Textes : ceux de la vidéo (relevés dans les evidence) par défaut. Couleurs et polices : celles de la référence, pas la D.A de l'utilisateur — sauf si l'utilisateur demande « dans ma D.A » : alors texte blanc, fond orange `#FF5900`, aucune ponctuation à l'écran, pas de bleu ni de téléphone.
5. Polices : utiliser une police système proche (`-apple-system, Inter, Helvetica`) ou Google Fonts si la ressemblance compte ; dire que c'est une police **ressemblante**.
6. Thème : couleurs de l'interface via les variables CSS du `read_me` (`--text-primary`, `--text-secondary`…) ; les maquettes gardent leurs couleurs propres.
7. `loading_messages` : 1–3 phrases courtes et ludiques en français.

## Après le rendu
Dans le message (en français, court) :
- ce que montre chaque widget, et lesquelles sont fidèles (`observé`) ou reconstruites (`proposé`) ;
- les limites (courbes estimées, police ressemblante) ;
- proposer la suite : « Je peux en reproduire une dans Frame / HyperFrames » ou « la refaire dans ta D.A ».

## Règles
- Uniquement `show_widget` dans le chat. Pas de fichier HTML, pas de navigateur, pas d'Artifact — sauf si l'utilisateur le demande.
- Une animation par maquette, lisible seule. Pas de texte qui déborde du 9:16.
- Ne jamais inventer une animation absente de l'analyse (sauf variante demandée) ; une variante proposée est étiquetée « proposé ».
