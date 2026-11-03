#!/usr/bin/env python3
"""Preset VELVET (référence C0209 v14). Règles : REGLES.md. Guide : GUIDE-CLAUDE.md.
  python3 PKG/preset/habiller.py --job job --rush RUSH --liste                    liste des mots, images et coupes
  python3 PKG/preset/habiller.py --job job --rush RUSH --out v1 --plan v1/habillage.json [--video RUSH-cuts.mp4] [--titre '…']
Gros mots Anton, tout le reste IBM Plex Sans Regular 400 Italic, aucune animation d'apparition : chaque mot se pose quand il est dit.
Hors rouge : une ligne puis le gros mot dessous, décalé à droite. Zooms secs sur les coupes et les débuts de phrase, jamais sur écran rouge.
Entrées jamais modifiées : RUSH-cuts.json et RUSH-analysis-minimale.json (dans --job/montage).
"""
import argparse, html, json, math, os, random, shutil, subprocess, sys
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(description='Preset VELVET')
ap.add_argument('--job', required=True); ap.add_argument('--rush', required=True)
ap.add_argument('--liste', action='store_true', help='affiche les mots, leurs images et les coupes, puis sort')
for o in ('--out', '--plan', '--source', '--video', '--titre'): ap.add_argument(o)
ARGS = ap.parse_args()
if not ARGS.liste and not (ARGS.out and ARGS.plan): ap.error('--out et --plan sont obligatoires')
FPS = 30
PRESET = 'velvet'
FS = dict(normal=68, big=140)
LSP = dict(normal=-0.03, big=-0.025)   # Anton : serré au maximum avant que les lettres se touchent (le -0.1 de la V6 valait pour Momo)
PAS_X, PAS_Y, PAS_GROS = 46, 62, 102   # écran rouge : escalier repris des placements validés
MARCHE, ECART = 137, 102   # hors rouge : ligne puis gros mot, valeurs de son placement sur FOUTRE
CENTRE_Y = 1195
# écrans rouges, dans l'ordre : sens des marches, décalages (toujours au milieu de l'image, seul le sens des marches varie)
RCOMPO = [(k, 0, 0) for k in ('droite', 'miroir', 'centre')]
# zones sûres Instagram : 65 px sur les côtés, 270 en haut, rien sous 1500, et 140 à droite sous 1150 (colonne des icônes)
BORD, DROITE_HAUT, DROITE_BAS, SEUIL_ICONES = 65, 1015, 940, 1150
TRAIT_VU = 6              # un trait ou un rond fini reste au moins ce nombre d'images à l'écran
TIENT_ROND = 2 + 8 + TRAIT_VU
FLASH = (1, .55, .2)      # flash blanc d'entrée d'écran rouge, image par image
SUB_FIN_Y = 1130          # sous-titres remontés pendant le CTA
SOUS_TRAIT = (5, 14)      # ligne sous le gros mot rouge : moyenne de ses réglages sur « en France » et « de tes résultats »
ZOOMS = [1, 1.25, 1, 1.35]
PLAN_MIN, PLAN_MAX = 36, 66   # entre deux zooms, en images
TOUR_Y = 28           # le rond ne doit pas toucher la ligne au-dessus
ENTOURE = 3           # hors rouge, un gros mot sur trois est entouré
MOTS_MAX = 3          # sous-titres : 3 mots par ligne au plus
D_UN_COUP = 24        # ligne dite en moins de 0,8 s : affichée d'un coup
FAIBLES = {'de', 'des', 'à', 'le', 'la', 'les', 'et', 'en', 'un', 'une', 'tes', 'ton', 'te', 'se', 'on', 'qui', 'que', 'pour', 'sur', 'au', 'dans', 'par', 'ou', 'vous', 'nos', 'je', 'avec', 'si', 'pas', 'du'}

job = os.path.join(ARGS.job, 'montage')
cuts = json.load(open(os.path.join(job, f'{ARGS.rush}-cuts.json')))['segments']
ana = json.load(open(os.path.join(job, f'{ARGS.rush}-analysis-minimale.json')))
P = json.load(open(ARGS.plan)) if ARGS.plan else {}
# Plan du rush (habillage.json) : données propres à la vidéo, le reste du fichier ne bouge pas
ROUGES = [tuple(r) for r in P.get('rouges', [])]   # écrans rouges en images sur la timeline coupée
HOOK = set(P.get('hook', []))                      # gros mots du hook : son « hook »
TEXTES = {int(k): v for k, v in P.get('textes', {}).items()}   # texte affiché d'un mot, '' pour le masquer
PLAN = [tuple(b) for b in P.get('blocs', [])]      # (type, lignes) ; lignes = mots séparés par « / », « ! » = gros mot ; 'auto' = sous-titre découpé tout seul
POSE = {int(k): v for k, v in P.get('pose', {}).items()}   # bord gauche imposé d'un bloc, par indice du 1er mot
DEPL = {k: tuple(v) for k, v in P.get('deplacements', {}).items()}   # placements demandés par l'utilisateur
CTA = P.get('cta', {})
N, offs, mots = 0, [], {}
for s in cuts:
    offs.append(N)
    for w in ana['words']:
        if s['startFrame'] <= w['startFrame'] < s['endFrame']:
            i = int(w['id'][1:])
            mots[i] = dict(i=i, f=N + w['startFrame'] - s['startFrame'], t=TEXTES.get(i, w['text']))
    N += s['endFrame'] - s['startFrame']
D = N / FPS

if ARGS.liste:
    debuts = {o: n for n, o in enumerate(offs)}
    for f in range(N):
        if f in debuts: print(f'--- coupe {debuts[f] + 1}/{len(cuts)} : image {f}')
        for w in (w for w in mots.values() if w['f'] == f): print(f"{w['i']:4d}  image {w['f']:5d}  {w['f'] / FPS:6.2f} s  {w['t']}")
    print(f'{len(mots)} mots, {N} images, {D:.2f} s'); sys.exit()
for k in ('rouges', 'blocs', 'cta'):
    if not P.get(k): sys.exit(f'Plan incomplet : champ « {k} » manquant ou vide.')
if CTA['mot'] not in mots: sys.exit(f"Le mot du CTA ({CTA['mot']}) n'existe pas dans le montage.")
FIN_B1 = CTA['mot']             # CTA, pastille et flèches arrivent ensemble sur ce mot
for typ, spec in PLAN:
    for p in spec.replace('!', '').split('/'):
        d, _, e = p.partition('-')
        vide = [i for i in range(int(d), int(e or d) + 1) if i not in mots]
        if vide: sys.exit(f'Bloc {typ} « {spec} » : mots {vide} absents du montage (coupés ?).')

vue = dict(normal=ImageFont.truetype(os.path.join(HERE, 'assets/IBMPlexSans-Italic-var.ttf'), FS['normal']),
           big=ImageFont.truetype(os.path.join(HERE, 'assets/Anton-Regular.ttf'), FS['big']))
def plage(p):
    a, _, b = p.partition('-')
    return [mots[i] for i in range(int(a), int(b or a) + 1) if i in mots and mots[i]['t']]
def texte(ws, big=False):
    t = ' '.join(w['t'] for w in ws)
    return t.upper() if big else t
def mesure(l):
    t = texte(l['ws'], l['big']); k = 'big' if l['big'] else 'normal'
    return min(950, vue[k].getlength(t) + LSP[k] * FS[k] * len(t))
def large(ws): return mesure(dict(ws=ws, big=False))

def decouper(ws):
    "Lignes de 3 mots au plus, jusqu'à 980 px : coupe aux pauses, évite de finir sur un petit mot et les mots seuls."
    n = len(ws); meilleur = [0] + [1e9] * n; depuis = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - MOTS_MAX), j):
            l = ws[i:j]
            if large(l) > DROITE_BAS - BORD or any(b['f'] - a['f'] > 19 for a, b in zip(l, l[1:])): continue
            cout = 1 + (5 if j < n and l[-1]['t'].lower() in FAIBLES else 0) + (3 if len(l) == 1 else 0)
            if meilleur[i] + cout < meilleur[j]: meilleur[j], depuis[j] = meilleur[i] + cout, i
    L, j = [], n
    while j: L.insert(0, ws[depuis[j]:j]); j = depuis[j]
    return L

blocs = []
for typ, spec in PLAN:
    if typ == 'auto':
        for ws in decouper(plage(spec)): blocs.append(dict(typ='sub', lignes=[dict(ws=ws, big=False)]))
    else:
        L = [dict(ws=plage(p.lstrip('!')), big=p[0] == '!') for p in spec.split('/')]
        blocs.append(dict(typ=typ, lignes=L))

for k, b in enumerate(b for b in blocs if b['typ'] == 'rouge'): b['compo'] = RCOMPO[k % len(RCOMPO)]
cf = [0] + offs[1:]
for b in blocs:
    f = b['lignes'][0]['ws'][0]['f']
    b['f0'] = max([c for c in cf if f - 6 <= c <= f] or [f])
blocs[0]['f0'] = 0
for a, b in zip(blocs, blocs[1:]): a['f1'] = b['f0']
blocs[-1]['f1'] = N

nb_gros = 0
for b in blocs:
    for l in b['lignes']:
        if l['big'] and b['typ'] != 'rouge':
            nb_gros += 1
            dispo = b['f1'] - (b['f0'] if l is b['lignes'][0] else max(l['ws'][0]['f'], b['f0']))
            if nb_gros % ENTOURE == 0 and dispo < TIENT_ROND: nb_gros -= 1   # pas le temps de finir le rond : il passe au gros mot suivant
            else: l['tour'] = nb_gros % ENTOURE == 0

def escalier(b):
    "Marches qui descendent vers la droite, comme le placement validé : renvoie (gauche, centre vertical) par ligne."
    L = b['lignes']; r = b['typ'] == 'rouge'
    n = [mesure(l) for l in L]
    sens, bx, by = b['compo'] if r else ('droite', 0, 0)
    marche = (-PAS_X if sens == 'miroir' else PAS_X) if r else MARCHE
    gauche = [marche * k for k in range(len(L))]
    if sens == 'centre': gauche = [-w / 2 for w in n]
    elif sens == 'miroir': gauche = [x - w for x, w in zip(gauche, n)]   # bords droits en marches vers la gauche
    g = next((k for k, l in enumerate(L) if l['big']), None)
    if r and g is not None and g + 1 < len(L): gauche[g + 1] += SOUS_TRAIT[0]
    decale = POSE.get(L[0]['ws'][0]['i'], 540 - (min(gauche) + max(x + w for x, w in zip(gauche, n))) / 2) + bx
    if r:   # chaque ligne est centrée ; gros mot pile au milieu, petites lignes à peine décalées selon le sens des marches
        signe = {'droite': 1, 'miroir': -1, 'centre': 0}[sens]
        gauche = [540 - w / 2 + (0 if l['big'] else signe * PAS_X * (k - (len(L) - 1) / 2)) for k, (l, w) in enumerate(zip(L, n))]
        decale = 0
    gauche = [max(BORD, min((DROITE_HAUT if r else DROITE_BAS) - w, x + decale)) for x, w in zip(gauche, n)]
    pas = []
    for a, c in zip(L, L[1:]):
        p = (PAS_GROS + 16 if c['big'] else PAS_GROS if a['big'] else PAS_Y) if r else ECART   # l'accent d'un gros mot ne touche pas la ligne du dessus
        pas.append(p + SOUS_TRAIT[1] if a['big'] and r else p + TOUR_Y if c.get('tour') else p)   # place pour le trait ou le rond
    tot = sum(pas)
    haut = lambda l: 96 if l['big'] else 60
    top = (960 + by + (haut(L[0]) - haut(L[-1])) / 2 if r else CENTRE_Y) - tot / 2
    ys = [top]
    for p in pas: ys.append(ys[-1] + p)
    return [(round(x), round(y)) for x, y in zip(gauche, ys)]

def rouge(f): return any(a <= f < b for a, b in ROUGES)
def zooms():
    "Sur chaque coupe et à chaque sortie d'écran rouge ; plan trop long : sur un début de phrase. Cadre différent à chaque fois."
    sures = sorted({f for f in cf + [b for a, b in ROUGES] if f == 0 or not rouge(f)})
    points = []
    for a, c in zip(sures, sures[1:] + [N]):
        points.append(a)
        if rouge(a): continue
        fin = min([c] + [d for d, _ in ROUGES if d > a]); der = a
        for f in sorted({b['f0'] for b in blocs if a < b['f0'] < fin}):
            if f - der >= PLAN_MIN and fin - f >= PLAN_MIN and (f - der >= PLAN_MAX or next_trop_loin(f, der, fin)):
                points.append(f); der = f
    return [[f, ZOOMS[k % len(ZOOMS)]] for k, f in enumerate(points)]
def next_trop_loin(f, der, fin):
    "Prendre ce début de phrase si le suivant arriverait trop tard."
    apres = [b['f0'] for b in blocs if f < b['f0'] < fin]
    return (apres[0] if apres else fin) - der > PLAN_MAX

def trait(graine):
    "Un trait d'enfant, jamais droit ; points (x de 0 à 1, y en px)."
    alea = random.Random(graine)
    n, pente = 6, alea.uniform(-5, 3)
    return [(round(-.02 + 1.04 * i / n, 3), round(8 + pente * i / n + alea.uniform(-5, 5), 1)) for i in range(n + 1)]

def cercle(graine):
    "Un tour d'enfant fait vite : part d'en haut à gauche, boucle et dépasse son départ ; points relatifs au mot (0 à 1 + marge en px)."
    alea = random.Random(graine)
    n, depart, pts = 14, -2.3, []
    for i in range(n + 1):
        a = depart + (2 * math.pi + .55) * i / n
        rx, ry = 1 + alea.uniform(-.03, .03), 1 + alea.uniform(-.06, .06) + .16 * i / n
        c, d = math.cos(a), math.sin(a)   # rond un peu carré : il doit contourner les coins du mot, pas les traverser
        pts.append((round(math.copysign(abs(c) ** .55, c) * rx, 3), round(math.copysign(abs(d) ** .55, d) * ry, 3)))
    return pts

def depl(i):
    return ' data-dx="%d" data-dy="%d"' % DEPL[i] if i in DEPL else ''

def fleche(graine, x0, y0, x1, y1):
    "Une flèche d'enfant d'un seul trait : descend en tremblant, puis les deux bords de la pointe."
    alea = random.Random(graine)
    n, pts = 5, []
    for i in range(n + 1):
        u = i / n; bosse = math.sin(u * math.pi) * alea.uniform(26, 40) * (1 if graine % 2 else -1)
        pts.append((x0 + (x1 - x0) * u + bosse + (alea.uniform(-7, 7) if 0 < i < n else 0), y0 + (y1 - y0) * u))
    d = f'M{pts[0][0]:.0f} {pts[0][1]:.0f}'
    for p, q in zip(pts[1:-1], pts[2:]): d += f' Q{p[0]:.0f} {p[1]:.0f} {(p[0] + q[0]) / 2:.0f} {(p[1] + q[1]) / 2:.0f}'
    d += f' L{x1} {y1} L{x1 - 40} {y1 - 44} M{x1} {y1} L{x1 + 38} {y1 - 48}'
    return d

STY = {'sub': ('s-sub', 'Sous-titres'), 'big': ('s-big', 'Gros mots'), 'sm': ('s-sm', 'Petites lignes hook et CTA'),
       'rsub': ('s-rsub', 'Sous-titres écran rouge'), 'rbig': ('s-rbig', 'Gros mots écran rouge')}
calques, plan, sons, reste_court = [], [], [], []
fin_cta = mots[FIN_B1]['f']
for b in blocs:
    pos_l = escalier(b) if len(b['lignes']) > 1 else None; r = b['typ'] == 'rouge'
    for k, l in enumerate(b['lignes']):
        ws = l['ws']
        kind = ('rbig' if r else 'big') if l['big'] else 'rsub' if r else 'sm' if b['typ'] in ('hook', 'cta') else 'sub'
        cl, lab = STY[kind]
        t0 = max(ws[0]['f'], b['f0'])
        if k == 0: t0 = b['f0']
        pos = f'data-l="{pos_l[k][0]}"' if pos_l else 'data-x="540"'
        y_c = pos_l[k][1] if pos_l else 960 if r else SUB_FIN_Y if b['f0'] >= fin_cta else 1244
        d_un_coup = l['big'] or ws[-1]['f'] - ws[0]['f'] <= D_UN_COUP
        quand = lambda w: t0 if d_un_coup or w is ws[0] and k == 0 else max(w['f'], b['f0'])   # ligne rapide : les mots arrivent ensemble
        sp = ' '.join(f'<span class="wd" data-w0="{quand(w) / FPS:.4f}">{html.escape(w["t"].upper() if l["big"] else w["t"])}</span>' for w in ws)
        ul = ''
        f_t, d_t = (t0 + 2, 8) if l.get('tour') else (t0 + 3, 7)
        if f_t + d_t + TRAIT_VU > b['f1']:   # le trait doit finir et se voir fini avant que le mot parte
            f_t = t0; d_t = max(3, b['f1'] - t0 - TRAIT_VU)
            if kind == 'rbig' or l.get('tour'): reste_court.append((texte(ws, True), b['f1'] - t0))
        if kind == 'rbig':
            ul = f'<svg class="ul" aria-hidden="true"><path pathLength="100" data-pts="{json.dumps(trait(ws[0]["i"]), separators=(",", ":"))}" data-f0="{f_t}" data-df="{d_t}"/></svg>'
        if l.get('tour'):
            ul = f'<svg class="tour" aria-hidden="true"><path pathLength="100" data-rond="{json.dumps(cercle(ws[0]["i"]), separators=(",", ":"))}" data-f0="{f_t}" data-df="{d_t}"/></svg>'
        if l['big']: sons.append(dict(f=t0, son='rouge' if r else 'hook' if ws[0]['i'] in HOOK else 'gros', mot=texte(ws, True)))
        dd = depl('w%03d-l%d' % (ws[0]['i'], k))
        calques.append(f'<div class="cap {cl}" id="w{ws[0]["i"]:03d}-l{k}" data-review-text data-style-label="{lab}" data-t0="{t0 / FPS:.4f}" data-dur="{(b["f1"] - t0) / FPS:.4f}" {pos} data-y="{y_c}"{dd}><div class="in"><span class="tx">{sp}</span>{ul}</div></div>')
    plan.append(dict(type=b['typ'], debut=b['f0'], fin=b['f1'], lignes=[texte(l['ws'], l['big']) for l in b['lignes']]))
def bouton(i, cls, t, x, y, f):
    return f'<div class="cap s-btn {cls}" id="{i}" data-review-text data-style-label="CTA de fin" data-t0="{f / FPS:.4f}" data-dur="{(N - f) / FPS:.4f}" data-x="{x}" data-y="{y}"><div class="in"><span class="tx"><span class="wd" data-w0="{f / FPS:.4f}">{t}</span></span></div></div>'
calques += [bouton('fin-b1', 'b1', CTA.get('bouton1', 'CLIQUE SOUS LA VIDÉO'), 470, 1265, fin_cta), bouton('fin-b2', 'b2', CTA.get('bouton2', 'Y ACCÉDER'), 745, 1342, fin_cta)]
fin_svg = f'<svg class="fl" viewBox="0 0 1080 1920" aria-hidden="true" data-t0="{fin_cta / FPS:.4f}" data-dur="{(N - fin_cta) / FPS:.4f}"><path pathLength="100" d="{fleche(3, 250, 1340, 285, 1495)}" data-f0="{fin_cta}" data-df="9"/><path pathLength="100" d="{fleche(4, 575, 1345, 540, 1495)}" data-f0="{fin_cta}" data-df="9"/></svg>'
sons += [dict(f=a, son='flash', mot='flash') for a, _ in ROUGES] + [dict(f=fin_cta, son='cta', mot='CTA')]
flashs = ''.join(f'<div class="flash" data-f="{a}"></div>' for a, _ in ROUGES)
fonds = ''.join(f'<div class="bg" data-t0="{a / FPS:.4f}" data-dur="{(b - a) / FPS:.4f}"></div>' for a, b in ROUGES)

CSS = '''@font-face{font-family:"IBM Plex Sans";src:url(assets/IBMPlexSans-Italic-var.ttf) format("truetype");font-weight:100 700;font-style:italic}
@font-face{font-family:"Anton";src:url(assets/Anton-Regular.ttf) format("truetype");font-weight:400;font-style:normal}
html,body{margin:0;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}
#cam,#cam video{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
#cam{transform-origin:52% 42%}
.bg{position:absolute;inset:0;z-index:3;opacity:0;background-color:#730419;background-image:linear-gradient(rgba(255,255,255,.1) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.1) 2px,transparent 2px),url(assets/fond-rouge-texture.jpg);background-size:108px 108px,108px 108px,1080px 1920px}
.cap{position:absolute;left:0;top:0;white-space:nowrap;visibility:hidden;z-index:5;pointer-events:none}
.cap .in{position:relative;display:block}
.cap .tx{display:block;width:max-content;line-height:1;font-family:"IBM Plex Sans",sans-serif;font-weight:400;font-style:italic;color:#fff;font-size:var(--fs);font-synthesis:none;-webkit-font-smoothing:antialiased}
.wd{visibility:hidden}
.s-sub{--fs:68px}.s-big{--fs:140px}.s-sm{--fs:68px}.s-rsub{--fs:68px}.s-rbig{--fs:140px}
.s-sub .tx,.s-sm .tx,.s-rsub .tx{letter-spacing:-0.03em}.s-big .tx,.s-rbig .tx{letter-spacing:-0.025em;font-family:"Anton",sans-serif;font-weight:400;font-style:normal}
.ul{position:absolute;left:0;top:100%;margin-top:-6px;width:100%;height:50px;overflow:visible}
.tour{position:absolute;left:0;top:0;width:100%;height:100%;overflow:visible}
.ul path,.tour path{fill:none;stroke:#fff;stroke-width:9;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:100 110;stroke-dashoffset:102}
.tour path{stroke-width:5}
.fl{position:absolute;inset:0;width:1080px;height:1920px;z-index:5;visibility:hidden;overflow:visible;pointer-events:none;filter:drop-shadow(0 3px 8px rgba(0,0,0,.4))}
.fl path{fill:none;stroke:#fff;stroke-width:9;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:100 110;stroke-dashoffset:102}
.s-btn .tx{font-family:"Anton",sans-serif;font-style:normal;font-weight:400;letter-spacing:.005em;text-shadow:none}
.b1 .tx{background:#fff;color:#111;font-size:76px;padding:20px 40px 22px;border-radius:12px;transform:rotate(-1.5deg);box-shadow:0 10px 30px rgba(0,0,0,.4)}
.b2{z-index:6}.b2 .tx{background:#730419;color:#fff;font-size:42px;padding:9px 22px 11px;border:4px solid #fff;border-radius:10px;transform:rotate(3deg)}
.flash{position:absolute;inset:0;z-index:7;background:#fff;opacity:0;pointer-events:none}
.s-sub .tx,.s-big .tx,.s-sm .tx{text-shadow:0 3px 16px rgba(0,0,0,.45)}
'''
JS = '''
const FPS=30,D=%s,Z=%s,FL=[1,.55,.2],droite=y=>y>=1150?940:1015;
function frames(c){const t=+c.dataset.t0;return [Math.round(t*FPS),Math.round((t+(+c.dataset.dur))*FPS)];}
function layout(){
  for(const c of document.querySelectorAll('.cap')){
    const d=c.dataset,tx=c.querySelector('.tx');tx.style.fontSize='';
    const y=+d.y+(+(d.dy||0)),pad=c.querySelector('.tour')?45:0,maxw=droite(y)-65-2*pad;
    if(tx.offsetWidth>maxw){const fs=parseFloat(getComputedStyle(tx).fontSize);tx.style.fontSize=(fs*maxw/tx.offsetWidth)+'px';}
    const w=tx.offsetWidth,h=tx.offsetHeight;
    for(const p of c.querySelectorAll('.ul path,.tour path')){
      const a=p.dataset.rond?JSON.parse(p.dataset.rond).map(([x,y])=>[w/2+x*(w/2+45),h/2+y*(h/2+22)]):JSON.parse(p.dataset.pts).map(([x,y])=>[x*w,y]);
      let t=`M${a[0][0]} ${a[0][1]}`;for(let i=1;i<a.length-1;i++){const m=[(a[i][0]+a[i+1][0])/2,(a[i][1]+a[i+1][1])/2];t+=` Q${a[i][0]} ${a[i][1]} ${m[0]} ${m[1]}`;}
      const z=a[a.length-1];p.setAttribute('d',t+` L${z[0]} ${z[1]}`);}
    c.style.left=Math.max(65+pad,Math.min(droite(y)-pad-w,(d.l!==undefined?+d.l:+d.x-w/2)+(+(d.dx||0))))+'px';c.style.top=(+d.y-h/2+(+(d.dy||0)))+'px';
  }
}
Promise.all([document.fonts.load('italic 400 100px "IBM Plex Sans"'),document.fonts.load('400 100px "Anton"')]).then(()=>document.fonts.ready).then(()=>{
  layout();
  const tl=gsap.timeline({paused:true});
  for(const c of document.querySelectorAll('.bg')){const [fs,fe]=frames(c);tl.set(c,{opacity:1},(fs-.5)/FPS);tl.set(c,{opacity:0},(fe-.5)/FPS);}
  for(const c of document.querySelectorAll('.cap,.fl')){const [fs,fe]=frames(c);
    if(fs)tl.set(c,{visibility:'visible'},(fs-.5)/FPS);else c.style.visibility='visible';
    if(fe<Math.round(D*FPS))tl.set(c,{visibility:'hidden'},(fe-.5)/FPS);}
  for(const w of document.querySelectorAll('.wd')){const f=Math.round(+w.dataset.w0*FPS);if(f)tl.set(w,{visibility:'inherit'},(f-.5)/FPS);else w.style.visibility='inherit';}
  for(const c of document.querySelectorAll('.flash')){const f=+c.dataset.f;FL.forEach((o,i)=>tl.set(c,{opacity:o},(f+i-.5)/FPS));tl.set(c,{opacity:0},(f+FL.length-.5)/FPS);}
  for(const p of document.querySelectorAll('.ul path,.tour path,.fl path'))tl.fromTo(p,{strokeDashoffset:102},{strokeDashoffset:0,duration:(+p.dataset.df)/FPS,ease:'none'},(+p.dataset.f0-.5)/FPS);
  for(const [f,z] of Z)if(f)tl.set('#cam',{scale:z},(f-.5)/FPS);
  tl.set({}, {}, D);
  window.__timelines=window.__timelines||{};window.__timelines['main']=tl;
});
''' % (round(D, 4), json.dumps(zooms(), separators=(',', ':')))
page = lambda video: f'''<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="preset" content="{PRESET}"><title>{TITRE}</title>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-fps="30" data-duration="{D:.4f}">
<div id="cam">{video}</div>{fonds}{flashs}
{chr(10).join(calques)}
{fin_svg}
</div><script>{JS}</script></body></html>'''

comp = os.path.join(ARGS.out, 'composition')
if os.path.exists(os.path.join(comp, 'index.html')): sys.exit(f'{comp} existe déjà : créer une nouvelle version (vN+1) plutôt que d’écraser.')
os.makedirs(os.path.join(comp, 'assets'), exist_ok=True)
TITRE = ARGS.titre or f'{ARGS.rush} · VELVET'
base = f'{ARGS.rush}-cuts.mp4'
if ARGS.video: shutil.copy2(ARGS.video, os.path.join(comp, 'assets', base))
else:   # vidéo coupée : image exacte, aucun fondu
    filt = ''.join(f"[0:v]trim=start_frame={s['startFrame']}:end_frame={s['endFrame']},setpts=PTS-STARTPTS[v{n}];"
                   f"[0:a]atrim=start={s['startFrame'] / FPS:.6f}:end={s['endFrame'] / FPS:.6f},asetpts=PTS-STARTPTS[a{n}];" for n, s in enumerate(cuts))
    filt += ''.join(f'[v{n}][a{n}]' for n in range(len(cuts))) + f'concat=n={len(cuts)}:v=1:a=1[v][a]'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', ARGS.source or os.path.join(ARGS.job, 'sources', ARGS.rush + '.mov'), '-filter_complex', filt, '-map', '[v]', '-map', '[a]', '-r', str(FPS),
                    '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', os.path.join(comp, 'assets', base)], check=True)
for f in os.listdir(os.path.join(HERE, 'assets')): shutil.copy2(os.path.join(HERE, 'assets', f), os.path.join(comp, 'assets', f))
video = f'src="assets/{base}" data-start="0" data-duration="{D:.4f}" data-track-index="0" data-has-audio="true" playsinline></video>'
open(os.path.join(comp, 'index.html'), 'w').write(page('<video id="facecam" class="clip" ' + video))
json.dump({'authoringSkill': 'general-video', 'media': {'autoProxy': True}}, open(os.path.join(comp, 'hyperframes.json'), 'w'), indent=2)
json.dump({'private': True, 'scripts': {'preview': 'npx --yes hyperframes@0.8.162 preview', 'render': 'npx --yes hyperframes@0.8.162 render'}}, open(os.path.join(comp, 'package.json'), 'w'), indent=2)
json.dump(plan, open(os.path.join(ARGS.out, 'captions-plan.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(sorted(sons, key=lambda x: x['f']), open(os.path.join(ARGS.out, 'sfx-plan.json'), 'w'), ensure_ascii=False, indent=1)
vus = {w['i'] for b in blocs for l in b['lignes'] for w in l['ws']}
trop = [texte(l['ws']) for b in blocs for l in b['lignes'] if not l['big'] and len(l['ws']) > MOTS_MAX]
hors = [p['lignes'] for p in plan if p['type'] == 'rouge' and not any(d <= p['debut'] < e for d, e in ROUGES)]
if hors: print('À REVOIR : blocs rouges hors de tout écran rouge', hors)
vides = [r for r in ROUGES if not any(p['type'] == 'rouge' and r[0] <= p['debut'] < r[1] for p in plan)]
if vides: print('À REVOIR : écrans rouges sans texte', vides)
print('traits raccourcis pour finir', reste_court)
print('lignes de plus de 3 mots', trop)
print('zooms', len(zooms()), zooms())
print('entourés', nb_gros, [l.split('"')[1] for l in calques if 'class="tour"' in l])
print('blocs', len(blocs), 'mots manquants', [i for i, w in mots.items() if w['t'] and i not in vus], 'durée', round(D, 3))
for p in plan: print(p['debut'], p['fin'], p['type'], ' | '.join(p['lignes']))
