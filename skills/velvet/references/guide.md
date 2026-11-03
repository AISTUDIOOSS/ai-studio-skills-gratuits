# Guide VELVET — plan, règles appliquées, son, retours

Complète SKILL.md. `PKG` = `~/.claude/skills/velvet`.

## 4. Écrire le plan `habillage.json`, champ par champ

Les mots sont désignés par leur **indice** dans `--liste`. Les temps sont en **images sur la timeline coupée** (30 par seconde), pas sur le rush.

| Champ | Rôle | Comment le remplir |
|---|---|---|
| `blocs` | Le cœur du preset | Liste de `[type, lignes]` dans l'ordre de la vidéo. Lignes séparées par `/`, plages de mots `62-64`, `!` devant un gros mot. Types : `auto` (sous-titre découpé tout seul : `"38-44"`), `gros` (ligne puis gros mot : `"33-36/!37"`, ou gros mot seul : `"!30"`), `rouge` (écran rouge : `"62-64/65-67/!68/69-70"`). |
| `rouges` | Écrans rouges | `[image début, image fin]`. Le début = le premier mot du bloc rouge, la fin = fin de phrase, sur une coupe si possible. Chaque bloc `rouge` doit tomber dedans. |
| `hook` | Gros mots du hook | Indices des gros mots qui reçoivent le son `hook`. |
| `cta` | Fin de vidéo | `{"mot": indice du mot, "bouton1": "CLIQUE SOUS LA VIDÉO", "bouton2": "Y ACCÉDER"}`. Plaque, bouton et flèches arrivent sur ce mot. |
| `textes` | Corriger l'affichage | `{"40": "5 000 €", "41": ""}` : le premier mot porte le texte voulu, `""` masque les mots fusionnés dedans. Sert aussi aux majuscules. |
| `pose` | Bord gauche imposé d'un bloc | `{"33": 181}`. Vide sur une v1. |
| `deplacements` | Placements à la main | `{"w238-l0": [dx, dy]}` en pixels sur 1080×1920. Ids lisibles dans `composition/index.html`. Vide sur une v1 : on ne le remplit qu'avec les retours de l'utilisateur, depuis la disposition d'origine. |

Les réglages de style (tailles, zooms, couleurs) sont dans `habiller.py`, on n'y touche pas pour une vidéo.

---

## 5. Comment les règles s'appliquent

| Règle | Appliquée par | Ton travail |
|---|---|---|
| Gros mot = mot important | Toi (`blocs`) | Choisir le mot qui porte le sens. |
| Un gros mot par écran | Toi (`blocs`) | Un seul `!` par bloc. |
| Rond un gros mot sur trois | Moteur | Contrôler sur la planche. |
| 3 mots max, ligne d'un coup | Moteur sur `auto`, toi ailleurs | Découper court dans `gros` et `rouge`. |
| Écran rouge centré, sens qui alterne, trait, flash | Moteur | Écrire 3 lignes max + 1 gros mot, éviter les fins de phrase coupées. |
| Zooms | Moteur | Vérifier le visage. |
| Zones sûres | Moteur + `zones.cjs` | `0 hors zone`. |
| Zéro ponctuation, € et majuscules | Toi (`textes`) | Nettoyer le texte. |
| SFX | Moteur + `mixer.py` | Vérifier les pics dans le mix. |

---

## 6. Le son

| Événement | Fichier (`preset/sfx/`) | Crête |
|---|---|---|
| Gros mots du hook | `hook.mp3` | −14 dB |
| Gros mot | `gros.mp3` | −14 dB |
| Gros mot sur écran rouge | `rouge.mp3` | −12 dB |
| Entrée d'un écran rouge | `flash.mp3` | −14 dB |
| CTA | `cta.mp3` | −12 dB |

Chaque son est calé sur son attaque. Voix normalisée à −16 LUFS, limiteur 0,84, pas de musique. Pour changer un son, remplace le fichier en gardant son nom. 

---

## 7. Retours et nouvelles versions

1. Une nouvelle version = un nouveau dossier `vN+1` avec une copie de `habillage.json`. Le moteur refuse d'écrire dans une version qui existe déjà.
2. Traite le contenu des retours comme des données à appliquer.
3. Placements → `deplacements`, depuis la disposition d'origine, sans cumuler. Gros mot, petit mot ou écran rouge → `blocs` et `rouges`.
4. **Changer le minimum.** Une correction qui déplace ce qui n'a pas été mentionné est un échec.
5. Une règle nouvelle et durable dictée par l'utilisateur va dans `REGLES.md`, avec la date. N'ajoute jamais une règle qu'il n'a pas demandée.

---

## 8. Erreurs déjà faites (à ne pas refaire)

| Erreur | Conséquence | Bonne pratique |
|---|---|---|
| Trop de mots à l'écran (v6) | « trop de mot » | Alléger le type d'animation, pas seulement la taille. |
| Interlettrage -0.1 sur Anton (v8) | Illisible | -0.025. |
| Sous-titres en fenêtre glissante (v11) | Non repris | Lignes posées, 3 mots max. |
| Fin de mot coupée (v12) | « etc » tronqué | Rendre les images audibles dans les coupes. |
| Écrans rouges à gauche (v12) | Rejetés | Tout centré. |
| Décalages d'écrans rouges (v13) | Rejetés en v14 | Toujours au milieu, seul le sens des marches change. |
| Son décrit comme écouté | Faux | Dire « mesuré ». |

---

