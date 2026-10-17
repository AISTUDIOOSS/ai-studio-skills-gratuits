#!/usr/bin/env python3
"""Habillage Steve classique (formation) sur des coupes QualityCut validées.

  python3 presets/steve-classique-formation/habiller.py --job /chemin/job --rush RUSH --out projets/<nom>/v1 \
      [--source /chemin/job/sources/RUSH.mov] [--video RUSH-cuts.mp4 existant] [--groupes choix.json] [--titre '…']
      [--preset .frame-data/presets/<id>/vN] [--ecart PX]

Entrées (jamais modifiées) : RUSH-cuts.json (intervalles source en images, fin exclue) et RUSH-analysis-minimale.json
(mots alignés sur la source normalisée), cherchés dans --job et --job/montage. La source doit être la source normalisée
exacte (sources/RUSH.mov, 30 i/s) : les indices d'images ne s'appliquent pas au rush original à une autre cadence.

--groupes (choix éditoriaux de Claude, facultatif) :
  {"affichage": {"66": "Uptrainer"},
   "groupes": [["stair", [[0, 1, "w"], [2, 4, "r"]]], ["single", [[11, 11, "o"]]]]}
  indices de mots inclusifs ; styles w = petit blanc heavy 49 px, r = capsule rouge 110 px, o = grand blanc oblique 110 px.
  Les autres mots sont groupés automatiquement (1–3 mots, ≤ 16 signes, sans couper après un mot faible).

--preset : version de preset Frame enregistrée depuis Personnaliser (« Mettre à jour le preset »). Ses règles par type
(source/preset-customizations.json → styleTypes : police, taille, couleurs, espacement, animation d'entrée) s'appliquent
à tous les sous-titres du type ; la mise en page est recalculée avec ces valeurs. Sans --preset : Steve classique v1.

--video : réutilise une vidéo coupée déjà produite sur ces mêmes coupes (révision d'habillage seule, octets identiques).

Mise en page et animations = règles exactes du preset Steve classique v1 (caption-renderer.js + captions.json,
vérifiées à 1e-13 px sur ses 206 sous-titres) : texte centré (540, 1080) sur la ligne « middle » du canvas ;
escaliers : boîtes d'encre décalées de min(70, 0,35 × largeur d'encre précédente), écart 8 px (12 après une ligne
de 110 px), bloc centré en (540, 1120) ; capsule rouge = encre + 0,09 × taille (vertical × 0,55), révélée de gauche
à droite en 10 images (1 − (1 − u)³, u = (f − début + 1)/10) ; montée 28 px en 10 images (smootherstep quintique,
opacité smoothstep en 5 images) pour les accents de 110 px visibles ≥ 16 images, coupe sèche sinon.

Sorties : <out>/composition (index.html HyperFrames, captions-plan.json, assets/RUSH-cuts.mp4) et <out>/editable
(aperçu à calques Frame : seekReview, reviewRelayout, theme.js + theme-panel.html). Les révisions demandées dans Frame
s'appliquent ensuite par calque : data-dx / data-dy (décalage relatif à la mise en page originale) et
data-anim = cut | rise | fade | slide-up | slide-left | pop | none, avec data-anim-dur (secondes).
"""
import argparse, json, os, shutil, subprocess, sys

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FAIBLES = set("de le la les des un une à au en ton tes ces ce que qui et ou d'en nos sur pour dans se te on il je nous ne n'y avec par sous si leur l'".split())

ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
ap.add_argument('--job', required=True); ap.add_argument('--rush', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--source'); ap.add_argument('--video'); ap.add_argument('--groupes'); ap.add_argument('--titre'); ap.add_argument('--preset')
ap.add_argument('--ecart', type=float, help="écart d'encre entre lignes d'escalier en px (défaut : 8, 12 après 110 px, comme le preset v1) ; +6 px au contact d'une capsule rouge")
a = ap.parse_args()

# Preset d'origine (lu par Frame pour « Mettre à jour le preset ») et règles par type enregistrées depuis Personnaliser.
PRESET_ID, TYPES = 'b309b30d-b39e-405a-aab7-49e57a9498b7', {}
LABELS = {'w': 'Sous-titres simples', 'o': 'Gros mots blancs', 'r': 'Surlignage'}
if a.preset:
    meta = json.load(open(os.path.join(a.preset, 'preset.json')))
    PRESET_ID = meta['id']
    custom = os.path.join(a.preset, 'source', 'preset-customizations.json')
    for t in (json.load(open(custom)).get('styleTypes', []) if os.path.isfile(custom) else []):
        st = next((c[2:] for c in t.get('classes', []) if c in ('s-w', 's-o', 's-r')), None)
        if st and t.get('changes'): TYPES[st] = t['changes']
    print('Preset', meta.get('name'), 'v%s' % meta.get('version'), '· types réglés :', ', '.join(LABELS[k] for k in TYPES) or 'aucun')
def type_css():
    css = ''
    for st, c in TYPES.items():
        r = [f'{k}:{v}!important' for k, v in (('font-size', f"{c['fontSize']}px" if 'fontSize' in c else None), ('color', c.get('color')),
             ('font-family', c.get('fontFamily')), ('letter-spacing', f"{c['letterSpacing']}em" if 'letterSpacing' in c else None)) if v is not None]
        if r: css += f'.s-{st} .tx{{{";".join(r)}}}'
        if c.get('backgroundColor'): css += f".s-{st} .box{{background-color:{c['backgroundColor']}!important}}"
    return css

def trouver(nom):
    for d in (a.job, os.path.join(a.job, 'montage')):
        p = os.path.join(d, nom)
        if os.path.isfile(p): return p
    sys.exit(f'Introuvable : {nom} dans {a.job} ou {a.job}/montage')
cuts = json.load(open(trouver(f'{a.rush}-cuts.json')))['segments']
analyse = json.load(open(trouver(f'{a.rush}-analysis-minimale.json')))
if analyse.get('fps', FPS) != FPS: sys.exit(f"Cadence {analyse.get('fps')} ≠ {FPS} : utiliser la source normalisée.")
source = a.source or os.path.join(a.job, 'sources', a.rush + '.mov')
if not os.path.isfile(source): sys.exit(f'Source normalisée introuvable : {source} (option --source)')
choix = json.load(open(a.groupes)) if a.groupes else {}
AFFICHAGE = {int(k): v for k, v in choix.get('affichage', {}).items()}
IMPOSES = choix.get('groupes', [])

# Mots recalés sur la timeline coupée : un mot est gardé si son début tombe dans un plan gardé.
mots, plans, off = [], [], 0
for p, s in enumerate(cuts):
    a0, b0 = s['startFrame'], s['endFrame']
    plans.append({'plan': p + 1, 'start': off, 'end': off + b0 - a0})
    for i, w in enumerate(analyse['words']):
        if a0 <= w['startFrame'] < b0 or (w['startFrame'] < a0 < w['endFrame'] and w['startFrame'] >= a0 - 2):
            mots.append({'i': i, 'text': w['text'], 'plan': p + 1, 'start': off + max(0, w['startFrame'] - a0), 'end': off + min(b0, w['endFrame']) - a0})
    off += b0 - a0
N = off
if not mots: sys.exit('Aucun mot dans les plans gardés.')
by_i = {w['i']: w for w in mots}; order = [w['i'] for w in mots]
def txt(i): return AFFICHAGE.get(i, by_i[i]['text']).replace('’', "'").replace(' ', ' ').replace(' ', ' ')
def rng(x, y): return [i for i in order if x <= i <= y]

impose_at, couverts = {}, set()
for kind, lines in IMPOSES:
    ids = [i for x, y, _ in lines for i in rng(x, y)]
    if not ids: sys.exit(f'Groupe imposé hors montage : {lines}')
    impose_at[ids[0]] = (kind, [(rng(x, y), st) for x, y, st in lines]); couverts.update(ids)

groupes, k = [], 0
while k < len(order):
    i = order[k]
    if i in impose_at:
        kind, lines = impose_at[i]; groupes.append({'kind': kind, 'lines': lines}); k += sum(len(l) for l, _ in lines); continue
    g = [i]; k += 1
    while k < len(order):
        j = order[k]
        if j in couverts or by_i[j]['plan'] != by_i[g[-1]]['plan'] or by_i[j]['start'] - by_i[g[-1]]['end'] > 8: break
        if len(g) >= 3 or len(' '.join(txt(x) for x in g + [j])) > 16: break
        g.append(j); k += 1
    while len(g) > 1 and txt(g[-1]).lower() in FAIBLES and k < len(order) and order[k] not in couverts and by_i[order[k]]['plan'] == by_i[g[-1]]['plan']:
        g.pop(); k -= 1
    groupes.append({'kind': 'single', 'lines': [(g, 'w')]})

# Groupes automatiques trop brefs (< 6 images) : fusion avec un voisin du même plan si la ligne reste ≤ 20 signes.
def ln(ids): return len(' '.join(txt(x) for x in ids))
def dur(n):
    x = by_i[groupes[n]['lines'][0][0][0]]['start']
    return (by_i[groupes[n + 1]['lines'][0][0][0]]['start'] if n + 1 < len(groupes) else N) - x
n = 0
while n < len(groupes):
    g = groupes[n]
    if g['kind'] == 'single' and g['lines'][0][1] == 'w' and dur(n) < 6:
        ids = g['lines'][0][0]
        for m in (n + 1, n - 1):
            if 0 <= m < len(groupes) and groupes[m]['kind'] == 'single' and groupes[m]['lines'][0][1] == 'w':
                o = groupes[m]['lines'][0][0]
                if by_i[o[0]]['plan'] == by_i[ids[0]]['plan'] and ln(o + ids) <= 20:
                    groupes[m]['lines'][0] = ((ids + o) if m > n else (o + ids), 'w'); del groupes[n]; n -= 1; break
    n += 1

# Pas de flash vide : fin exclusive d'un groupe = début du suivant, sur la grille d'images.
caps = []
for gi, g in enumerate(groupes): g['start'] = 0 if gi == 0 else by_i[g['lines'][0][0][0]]['start']
for gi, g in enumerate(groupes):
    g['end'] = groupes[gi + 1]['start'] if gi + 1 < len(groupes) else N
    for li, (ids, st) in enumerate(g['lines']):
        t0 = g['start'] if li == 0 else max(g['start'], by_i[ids[0]]['start'])
        caps.append({'id': f'g{gi:03d}l{li}', 'group': f'g{gi:03d}', 'layout': 'staircase' if g['kind'] == 'stair' else 'single',
                     'line': li, 'style': st, 'text': ' '.join(txt(x) for x in ids), 'words': ids, 'startFrame': t0, 'endFrame': g['end'],
                     'animation': TYPES.get(st, {}).get('animation') if TYPES.get(st, {}).get('animation', 'original') != 'original'
                                  else 'rise' if (st != 'w' and g['end'] - t0 >= 16) else 'cut',
                     **({'animDur': TYPES[st].get('animationDuration', .4)} if TYPES.get(st, {}).get('animation', 'original') != 'original' else {})})
probs = [('court', c['id'], c['text']) for c in caps if c['endFrame'] - c['startFrame'] < 3]
probs += [('capsule rouge longue (> 15 signes, une seule ligne)', c['text']) for c in caps if c['style'] == 'r' and len(c['text']) > 15]
# Règles du preset v2 (Nicolas) : ≤ 4 mots par ligne, 1 à 2 surlignages rouges dans le hook (3 premières s), gros blancs ≈ 1 / 5–7 s.
probs += [('plus de 4 mots sur une ligne', c['id'], c['text']) for c in caps if len(c['words']) > 4]
hook = sum(1 for c in caps if c['style'] == 'r' and c['startFrame'] < 3 * FPS)
if not 1 <= hook <= 2: probs.append(('hook : %d surlignage(s) rouge(s) dans les 3 premières secondes, attendu 1 à 2' % hook,))
gros = [c for c in caps if c['style'] == 'o']
if len(gros) < N / FPS / 7: probs.append(('gros mots blancs : %d pour %.0f s, attendu environ un toutes les 5 à 7 s' % (len(gros), N / FPS),))
probs += [('gros mot blanc bref (< 15 images)', c['id'], c['text']) for c in gros if c['endFrame'] - c['startFrame'] < 15]

zooms = [{'plan': p['plan'], 'start': p['start'], 'end': p['end'], 'scale': [1.30, 1.12][n % 2]} for n, p in enumerate(plans)]
D = N / FPS
comp, edit = os.path.join(a.out, 'composition'), os.path.join(a.out, 'editable')
for d in (comp, edit):
    if os.path.exists(os.path.join(d, 'index.html')): sys.exit(f'{d} existe déjà : créer une nouvelle version (vN+1) plutôt que d’écraser.')
    os.makedirs(os.path.join(d, 'assets'), exist_ok=True)

# Vidéo coupée : intervalles exacts de cuts.json sur la source normalisée (ré-encodage image près, audio compris).
video = f'{a.rush}-cuts.mp4'
filt = ''.join(f"[0:v]trim=start_frame={s['startFrame']}:end_frame={s['endFrame']},setpts=PTS-STARTPTS[v{n}];"
               f"[0:a]atrim=start={s['startFrame']/FPS:.6f}:end={s['endFrame']/FPS:.6f},asetpts=PTS-STARTPTS[a{n}];" for n, s in enumerate(cuts))
filt += ''.join(f'[v{n}][a{n}]' for n in range(len(cuts))) + f'concat=n={len(cuts)}:v=1:a=1[v][a]'
if a.video: shutil.copy2(a.video, os.path.join(comp, 'assets', video))
else: subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', source, '-filter_complex', filt, '-map', '[v]', '-map', '[a]', '-r', str(FPS),
                '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', os.path.join(comp, 'assets', video)], check=True)
for f in os.listdir(os.path.join(HERE, 'assets')): shutil.copy2(os.path.join(HERE, 'assets', f), os.path.join(comp, 'assets', f))

json.dump({'rush': a.rush, 'preset': 'Steve classique (formation)', 'fps': FPS, 'totalFrames': N, 'cuts': f'{a.rush}-cuts.json (bords inchangés)',
           'zooms': zooms, 'groups': len(groupes), 'captions': caps, 'problems': probs}, open(os.path.join(comp, 'captions-plan.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({'authoringSkill': 'general-video', 'media': {'autoProxy': True}}, open(os.path.join(comp, 'hyperframes.json'), 'w'), indent=2)
json.dump({'private': True, 'scripts': {'preview': 'npx --yes hyperframes@0.8.152 preview', 'render': 'npx --yes hyperframes@0.8.152 render'}},
          open(os.path.join(comp, 'package.json'), 'w'), indent=2)

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
cap_html = ''.join(
    f'<div class="cap s-{c["style"]}" id="{c["id"]}" data-review-text data-group="{c["group"]}" data-layout="{c["layout"]}" '
    f'data-line="{c["line"]}" data-anim="{c["animation"]}" ' + (f'data-anim-dur="{c["animDur"]}" ' if 'animDur' in c else '') + f'data-style-label="{LABELS[c["style"]]}" data-t0="{c["startFrame"]/FPS:.6f}" data-dur="{(c["endFrame"]-c["startFrame"])/FPS:.6f}"><div class="in">'
    + ('<span class="box"></span>' if c['style'] == 'r' else '') + f'<span class="tx">{esc(c["text"])}</span></div></div>\n' for c in caps)
titre = esc(a.titre or f'{a.rush} · Steve classique')
html = f'''<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="frame-preset" content="{PRESET_ID}"><title>{titre}</title>
<script src="assets/gsap.min.js"></script><style>
@font-face{{font-family:CaptionHeavy;src:url('assets/heavy.otf')}}@font-face{{font-family:CaptionOblique;src:url('assets/oblique.otf')}}@font-face{{font-family:CaptionLightOblique;src:url('assets/light-oblique.ttf')}}
*{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#25292f}}
#root{{position:relative;width:100%;height:100%;overflow:hidden;background:#25292f}}
#cam{{position:absolute;inset:0;overflow:hidden;transform-origin:50% 36%}}
#facecam{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.cap{{position:absolute;left:0;top:0;white-space:nowrap;visibility:hidden;z-index:5;pointer-events:none}}
.cap .in{{position:relative;display:block}}
.cap .tx{{position:relative;display:block;color:#fff;letter-spacing:-0.025em;line-height:.94}}
.s-w .tx{{font:49px/.94 CaptionHeavy}}
.s-r .tx{{font:110px/.94 CaptionLightOblique}}
.s-o .tx{{font:110px/.94 CaptionOblique}}
.s-r .box{{position:absolute;left:0;top:0;background:#ff0000;transform-origin:0 50%}}
{type_css()}</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-fps="30" data-duration="{D:.6f}">
<div id="cam"><video id="facecam" class="clip" src="assets/{video}" data-start="0" data-duration="{D:.6f}" data-track-index="0" data-has-audio="true" playsinline></video></div>
{cap_html}</div>
<script>
const FPS=30, ZOOMS={json.dumps(zooms)}, ECART={json.dumps(a.ecart)};
// Géométrie du preset (caption-renderer.js) : mesures canvas de la police réellement calculée, ligne « middle ».
const MCV=document.createElement('canvas').getContext('2d'), BASES={{}};
function baseDom(font){{ // distance haut de bloc → ligne de base alphabétique d'un bloc DOM line-height .94
  if(BASES[font]!=null) return BASES[font];
  const d=document.createElement('div'); d.style.cssText='position:absolute;left:0;top:0;width:1000px;visibility:hidden;white-space:nowrap';
  d.style.font=font; d.style.lineHeight='.94'; d.innerHTML='H<i style="display:inline-block;width:0;height:0;vertical-align:baseline"></i>';
  document.body.appendChild(d); const r=d.getBoundingClientRect(), k=r.width/1000;
  BASES[font]=(d.querySelector('i').getBoundingClientRect().top-r.top)/k; d.remove(); return BASES[font];
}}
function mesure(c){{
  const tx=c.querySelector('.tx'), cs=getComputedStyle(tx), fs=parseFloat(cs.fontSize), font=fs+'px '+cs.fontFamily, t=tx.textContent||' ';
  MCV.font=font; MCV.letterSpacing=cs.letterSpacing==='normal'?'0px':cs.letterSpacing; MCV.textAlign='center';
  MCV.textBaseline='alphabetic'; const al=MCV.measureText('H').actualBoundingBoxAscent;
  MCV.textBaseline='middle'; const b=MCV.measureText(t), mid=MCV.measureText('H').actualBoundingBoxAscent;
  const pad=c.classList.contains('s-r')?fs*.09:0, py=pad*.55;
  return {{fs,font,w:b.width,off:al-mid,pad,py,il:b.actualBoundingBoxLeft,ir:b.actualBoundingBoxRight,ia:b.actualBoundingBoxAscent,id:b.actualBoundingBoxDescent,
    l:b.actualBoundingBoxLeft+pad,r:b.actualBoundingBoxRight+pad,a:b.actualBoundingBoxAscent+py,d:b.actualBoundingBoxDescent+py,iw:b.actualBoundingBoxLeft+b.actualBoundingBoxRight}};
}}
function poser(c,x,y,m){{ // (x, y) = centre canvas du preset ; ligne de base DOM alignée sur celle du canvas
  const top=y+m.off-baseDom(m.font); c.style.left=(x-m.w/2)+'px'; c.style.top=top+'px'; c.dataset.cx=x; c.dataset.cy=y;
  const box=c.querySelector('.box');
  if(box){{box.style.left=(m.w/2-m.il-m.pad)+'px';box.style.top=(y-m.ia-m.py-top)+'px';box.style.width=(m.il+m.ir+2*m.pad)+'px';box.style.height=(m.ia+m.id+2*m.py)+'px';}}
}}
function layout(){{
  const caps=[...document.querySelectorAll('.cap')], groups={{}};
  for(const c of caps)(groups[c.dataset.group]=groups[c.dataset.group]||[]).push(c);
  for(const g of Object.values(groups)){{
    const ms=g.map(mesure);
    if(g[0].dataset.layout==='single'){{poser(g[0],540,1080,ms[0]);continue;}}
    // escalier compact du preset : décalage min(70, .35 × encre précédente), écart 8 px (12 après 110 px), bloc centré (540, 1120) ; --ecart : écart choisi, +6 px au contact d'une capsule
    let L=0,top=0,maxR=0; const P=[];
    g.forEach((c,i)=>{{if(i){{const p=ms[i-1];L+=Math.min(70,.35*p.iw);top+=p.a+p.d+(ECART==null?(p.fs>=100?12:8):ECART+(p.pad||ms[i].pad?6:0));}}P.push([L,top]);maxR=Math.max(maxR,L+ms[i].l+ms[i].r);}});
    const H=top+ms[g.length-1].a+ms[g.length-1].d, ox=540-maxR/2, oy=1120-H/2;
    g.forEach((c,i)=>poser(c,ox+P[i][0]+ms[i].l,oy+P[i][1]+ms[i].a,ms[i]));
  }}
  // Révisions Frame : décalages relatifs à la mise en page originale (movement anchor original-layout-offset)
  for(const c of caps){{if(c.dataset.dx)c.style.left=(parseFloat(c.style.left)+(+c.dataset.dx))+'px';if(c.dataset.dy)c.style.top=(parseFloat(c.style.top)+(+c.dataset.dy))+'px';}}
}}
// Entrées choisies dans Frame (elementEdit.after.animation) : remplacent la montée et la révélation de capsule d'origine.
function frames(c){{const t=+c.dataset.t0;return [Math.round(t*FPS),Math.round((t+(+c.dataset.dur))*FPS)];}}
const ENTREES={{fade:{{}},'slide-up':{{y:55}},'slide-left':{{x:-70}},pop:{{scale:.65}}}};
function build(){{
  layout();
  const tl=gsap.timeline({{paused:true}}), cam=document.getElementById('cam');
  for(const z of ZOOMS){{const t=z.start/FPS,d=(z.end-z.start)/FPS;
    tl.fromTo(cam,{{scale:z.scale}},{{scale:z.scale*1.025,duration:d,ease:'none',immediateRender:z.start===0}},t);}}
  for(const c of document.querySelectorAll('.cap')){{
    const [fs,fe]=frames(c), s=fs/FPS, inn=c.querySelector('.in'), box=c.querySelector('.box'), anim=c.dataset.anim;
    // bascules à mi-image : visible sur les images [début, fin[ quel que soit l'arrondi des secondes
    tl.set(c,{{visibility:'visible'}},Math.max(0,(fs-.5)/FPS)); tl.set(c,{{visibility:'hidden'}},(fe-.5)/FPS);
    if(anim==='rise'){{
      tl.fromTo(inn,{{y:28}},{{y:0,duration:10/FPS,ease:u=>u*u*u*(u*(u*6-15)+10),immediateRender:false}},s);
      // opacité posée séparément sur capsule et texte, comme le globalAlpha du canvas du preset
      tl.fromTo([...inn.children],{{opacity:0}},{{opacity:1,duration:5/FPS,ease:u=>u*u*(3-2*u),immediateRender:false}},s);
    }}
    if(ENTREES[anim]){{const from={{opacity:0,...ENTREES[anim]}},to={{opacity:1,x:0,y:0,scale:1}};
      tl.fromTo(inn,from,{{...to,duration:+c.dataset.animDur||.4,ease:'expo.out',immediateRender:false}},s);}}
    // révélation du preset : 1-(1-u)³ avec u=(f-début+1)/10, soit 27,1 % dès la première image
    if(box&&(anim==='cut'||anim==='rise')) tl.fromTo(box,{{scaleX:0}},{{scaleX:1,duration:9/FPS,ease:u=>1-Math.pow(.9-.9*u,3),immediateRender:false}},s);
  }}
  tl.set({{}},{{}},{D:.6f});
  tl.seek(0,false);
  window.__timelines['main']=tl;
}}
document.fonts.ready.then(()=>Promise.all(['CaptionHeavy','CaptionOblique','CaptionLightOblique'].map(f=>document.fonts.load('110px '+f)))).then(build);
</script></body></html>
'''
open(os.path.join(comp, 'index.html'), 'w').write(html)

# Aperçu à calques Frame (--editable-dir) : même composition + adaptateur seekReview et variables de personnalisation.
SEEK = '''// Aperçu à calques Frame : seekReview(secondes, lecture, vitesse) ; la vidéo de l'iframe reste muette, le MP4 maître est seul audible.
window.seekReview=function(t,playing=false,rate=1){
  const tl=window.__timelines&&window.__timelines.main; if(tl) tl.seek(t,false);
  for(const c of document.querySelectorAll('.cap')){const [fs,fe]=frames(c),f=t*FPS;c.style.visibility=f>=fs-.5&&f<fe-.5?'visible':'hidden';}
  const v=document.getElementById('facecam'); v.muted=true; v.playbackRate=rate;
  if(playing){if(Math.abs(v.currentTime-t)>.18)v.currentTime=t;if(v.paused)v.play().catch(()=>{});}
  else{v.pause();if(Math.abs(v.currentTime-t)>.015)v.currentTime=t;}
};
window.reviewRelayout=layout;
'''
THEME_CSS = (".s-w .tx{font-family:var(--title-font,CaptionHeavy);color:var(--theme-ink,#fff);letter-spacing:calc(-0.025em + var(--title-tracking,0px))}"
  ".s-o .tx{font-family:var(--body-font,CaptionOblique);color:var(--theme-accent,#fff);letter-spacing:calc(-0.025em + var(--body-tracking,0px))}"
  ".s-r .tx{font-family:var(--caption-font,CaptionLightOblique);color:var(--caption-text,#fff);letter-spacing:calc(-0.025em + var(--caption-tracking,0px))}"
  ".s-r .box{background:var(--caption-bg,#ff0000)}\n")
open(os.path.join(edit, 'index.html'), 'w').write(html.replace('<head>', '<head><script>window.__timelines=window.__timelines||{};</script>', 1)
    .replace('<video id="facecam" class="clip" ', '<video id="facecam" ', 1).replace('</style></head>', THEME_CSS + '</style></head>', 1)
    .replace('</script></body></html>', SEEK + '</script></body></html>'))
for f in os.listdir(os.path.join(comp, 'assets')):
    dst = os.path.join(edit, 'assets', f)
    if not os.path.exists(dst): os.link(os.path.join(comp, 'assets', f), dst)
for f in ('theme.js', 'theme-panel.html'): shutil.copy2(os.path.join(HERE, 'editable', f), os.path.join(edit, f))

print(f'{len(groupes)} groupes, {len(caps)} calques, {N} images ({D:.3f} s) → {a.out}')
for p in probs: print('À REVOIR', p)
