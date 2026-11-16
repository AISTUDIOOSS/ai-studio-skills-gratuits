# Installation — instructions pour Claude Code

Tu es Claude Code. La personne t'a collé le lien de ce dépôt. Installe tout, sans lui poser de question technique. Elle n'est peut-être pas technique : parle-lui simplement, en français.

1. Récupère le pack dans `~/.ai-studio-montage` :
   - s'il n'existe pas : `git clone https://github.com/AISTUDIOOSS/ai-studio-skills-gratuits.git ~/.ai-studio-montage`
   - s'il existe : `git -C ~/.ai-studio-montage pull --ff-only`
   - sans git : télécharge `https://github.com/AISTUDIOOSS/ai-studio-skills-gratuits/archive/refs/heads/main.zip` et décompresse-le dans `~/.ai-studio-montage`.
2. Lance `bash ~/.ai-studio-montage/install.sh` au premier plan (pas en arrière-plan), avec le délai maximum de ta commande (10 minutes) : la première fois, il télécharge les outils. S'il est coupé avant `INSTALLATION OK`, relance exactement la même commande, autant de fois qu'il faut : il reprend sans risque.
3. Lis la sortie :
   - Code 3 « Google Chrome manque » : demande à la personne de l'installer depuis google.com/chrome, puis relance l'étape 2.
   - Code 4 « Clé ElevenLabs manquante » : la transcription de la voix passe par ElevenLabs. Explique-lui simplement : créer un compte sur elevenlabs.io, puis Developers → API Keys → Create Key, et te coller la clé ici. Enregistre-la sans jamais la réafficher : `mkdir -p ~/.config/elevenlabs && printf '%s' 'LA_CLÉ' > ~/.config/elevenlabs/key && chmod 600 ~/.config/elevenlabs/key`, puis relance l'étape 2.
   - Code 5 « La clé ElevenLabs ne marche pas » : la clé est fausse ou le compte n'a plus de crédits. Demande-lui de vérifier sur elevenlabs.io et de te recoller une clé, enregistre-la comme ci-dessus, puis relance l'étape 2.
   - Autre erreur : corrige-la si c'est un outil manquant, puis relance. Si c'est impossible, explique en une phrase ce qui bloque.
   - Mac Intel ou Windows : dis que ce pack ne fonctionne que sur un Mac Apple Silicon.
4. L'installation est terminée quand la sortie finit par `INSTALLATION OK`. Dis alors à la personne :
   - qu'elle doit fermer Claude Code puis le rouvrir, pour que les skills apparaissent ;
   - qu'elle peut ensuite taper `/velvet` suivi du chemin de son rush (une vidéo face cam verticale) : Claude coupe, habille et livre le MP4 ;
   - que les autres skills installés sont qualitycut, preset-steve, preset-melvyn, zooms-secs, zooms-progressifs, analyze-editing-inspiration et animations-html ;
   - que le guide est dans [GUIDE-MONTAGE.md](GUIDE-MONTAGE.md).

L'installation demande une seule chose : une clé ElevenLabs (pour retranscrire la voix). Elle reste sur la machine, dans `~/.config/elevenlabs/key`. Les anciennes versions des skills déjà installés sont mises de côté dans `~/.ai-studio-montage-sauvegarde/`. Le pack ne contient pas Frame.
