# Génère les clips de sous-titres : 1 ligne, ≤ 4 mots, jamais deux à la fois.
# Débuts = temps des mots alignés (job/transcription/LISTE-MOTS.txt).
import html, re, pathlib

END = 31.267
# (début, texte, mots-clés en accent)
CAPS = [
    (0.04, "NE POSTE PLUS", []),
    (0.56, "UN SEUL RÉEL", ["RÉEL"]),
    (1.30, "AVANT D'INSTALLER", ["D'INSTALLER"]),
    (1.96, "CES 5 SKILLS", ["5", "SKILLS"]),
    (2.70, "CLAUDE", ["CLAUDE"]),
    (3.06, "JE LES AI MIS", []),
    (3.44, "GRATUITEMENT", ["GRATUITEMENT"]),
    (3.90, "SUR GITHUB", ["GITHUB"]),
    (4.42, "ET ILS FONT", []),
    (4.90, "DE CLAUDE", ["CLAUDE"]),
    (5.44, "TOUTE TON ÉQUIPE", ["ÉQUIPE"]),
    (6.20, "VIDÉO", ["VIDÉO"]),
    (6.58, "LE PREMIER", ["PREMIER"]),
    (7.00, "TROUVE DES RÉELS", []),
    (7.72, "QUI EXPLOSENT", ["EXPLOSENT"]),
    (8.40, "DANS TA NICHE", ["NICHE"]),
    (8.86, "IL TE NOTE", []),
    (9.36, "LEURS 3 PREMIÈRES", ["3"]),
    (10.18, "SECONDES", ["SECONDES"]),
    (10.54, "LE DEUXIÈME", ["DEUXIÈME"]),
    (11.08, "ÉCRIT TES SCRIPTS", ["SCRIPTS"]),
    (11.82, "DE LA SEMAINE", ["SEMAINE"]),
    (12.34, "AVEC 3 ACCROCHES", ["3", "ACCROCHES"]),
    (13.24, "POUR CHACUN", []),
    (13.70, "LE TROISIÈME", ["TROISIÈME"]),
    (14.26, "ENLÈVE TOUT", []),
    (14.66, "CE QUI SONNE", []),
    (15.14, "COMME CHATGPT", ["CHATGPT"]),
    (15.84, "LE QUATRIÈME", ["QUATRIÈME"]),
    (16.46, "MONTE TA VIDÉO", ["VIDÉO"]),
    (17.16, "SOUS-TITRES", ["SOUS-TITRES"]),
    (17.56, "BLANCS COUPÉS", ["COUPÉS"]),
    (18.02, "ZOOM", ["ZOOM"]),
    (18.24, "ET TU AS UN", []),
    (18.82, "MP4", ["MP4"]),
    (19.34, "PRÊT À POSTER", ["POSTER"]),
    (20.06, "MAIS LE DERNIER", ["DERNIER"]),
    (20.60, "C'EST CELUI", []),
    (21.16, "QUE JE PRÉFÈRE", ["PRÉFÈRE"]),
    (21.80, "TU LUI DONNES", []),
    (22.24, "UNE VIDÉO LONGUE", ["LONGUE"]),
    (23.00, "ET IL T'EN SORT", []),
    (23.60, "PLUSIEURS SHORTS", ["SHORTS"]),
    (24.36, "CE SONT JUSTE", []),
    (24.98, "DES FICHIERS TEXTE", ["FICHIERS", "TEXTE"]),
    (25.70, "TU N'AS NI", []),
    (26.30, "ABONNEMENT", ["ABONNEMENT"]),
    (26.79, "NI COMPTE À CRÉER", []),
    (27.48, "COMMENTE SKILLS", ["SKILLS"]),
    (28.14, "ABONNE-TOI", ["ABONNE-TOI"]),
    (28.61, "ET JE T'ENVOIE", []),
    (29.07, "L'INSTALLATION", ["L'INSTALLATION"]),
    (29.70, "ÉTAPE PAR ÉTAPE", ["ÉTAPE"]),
    (30.55, "EN DM", ["DM"]),
    (30.95, "MAINTENANT", ["MAINTENANT"]),
]

out = []
for i, (t, txt, kws) in enumerate(CAPS):
    words = txt.split(" ")
    assert len(words) <= 4, txt
    nxt = CAPS[i + 1][0] if i + 1 < len(CAPS) else END
    assert nxt > t, txt
    dur = round(nxt - t - 0.01, 3)  # léger écart : jamais deux pastilles à la même image
    spans = " ".join(
        f'<span class="{"k" if w in kws else "w"}">{html.escape(w)}</span>' for w in words
    )
    out.append(
        f'      <div id="cap{i}" class="cap clip" data-start="{t}" data-duration="{dur}" data-track-index="9"><div class="chip">{spans}</div></div>'
    )

p = pathlib.Path(__file__).with_name("index.html")
src = p.read_text()
block = "\n".join(out)
src = re.sub(r"(<!--CAPS-->).*?(<!--/CAPS-->)", lambda m: m.group(1) + "\n" + block + "\n      " + m.group(2), src, flags=re.S)
p.write_text(src)
print(len(CAPS), "pastilles")
