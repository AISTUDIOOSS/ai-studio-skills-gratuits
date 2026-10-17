// Personnalisation Frame — Steve classique (formation). Aperçu instantané dans l’iframe éditable ; le MP4 ne change qu’au prochain export.
// Rôles : titleFont = textes blancs (CaptionHeavy 49 px), bodyFont = grands obliques (CaptionOblique 110 px),
// captionFont = capsules rouges (CaptionLightOblique 110 px). Valeurs d'origine = composition rendue.
(()=>{
const frameEl=$('editPreview'),key='frame-theme-'+location.port;
const palettes={
  original:{ink:'#ffffff',accent:'#ffffff',captionBg:'#ff0000',captionText:'#ffffff'},
  noir:{ink:'#ffffff',accent:'#ffffff',captionBg:'#111111',captionText:'#ffffff'},
  jaune:{ink:'#ffffff',accent:'#ffe14d',captionBg:'#ffe14d',captionText:'#111111'}};
const original={palette:'original',colors:{...palettes.original},titleFont:'CaptionHeavy',bodyFont:'CaptionOblique',captionFont:'CaptionLightOblique',titleTracking:0,bodyTracking:0,captionTracking:0};
let settings=structuredClone(original);
try{const saved=JSON.parse(localStorage.getItem(key));if(saved)settings={...settings,...saved,colors:{...settings.colors,...saved.colors}};}catch{}
const labels={ink:'Sous-titres simples',accent:'Gros mots blancs',captionBg:'Fond du surlignage',captionText:'Texte du surlignage'};
for(const [id,label] of Object.entries(labels)){const l=document.createElement('label');l.append(document.createTextNode(label));const input=document.createElement('input');input.type='color';input.id='theme-'+id;input.setAttribute('aria-label',label);input.oninput=()=>{settings.colors[id]=input.value;settings.palette='custom';activate();};l.append(input);$('themeColors').append(l);}
const fonts=[['CaptionHeavy','Caption Heavy — textes blancs d’origine'],['CaptionOblique','Caption Oblique — obliques d’origine'],['CaptionLightOblique','Caption Light Oblique — capsules d’origine'],['Arial','Arial'],['Helvetica Neue','Helvetica Neue'],['Georgia','Georgia']];
for(const id of ['titleFont','bodyFont','captionFont']){for(const [value,label] of fonts){const o=document.createElement('option');o.value=value;o.textContent=label;$(id).append(o);}$(id).onchange=()=>{settings[id]=$(id).value;activate();};}
for(const role of ['title','body','caption']){const id=role+'Tracking';for(const control of [$(id),$(id+'Range')])control.oninput=()=>{if(control.value==='')return;const n=Number(control.value);if(!Number.isFinite(n))return;settings[id]=Math.max(-50,Math.min(20,n));activate();};$(id+'Reset').onclick=()=>{settings[id]=0;activate();};}
function ui(){for(const role of ['title','body','caption']){const id=role+'Tracking';$(id).value=settings[id]??0;$(id+'Range').value=settings[id]??0;}const strip=$('paletteStrip');if(strip){strip.replaceChildren();for(const value of Object.values(settings.colors)){const swatch=document.createElement('i');swatch.style.background=value;strip.append(swatch);}}for(const id of Object.keys(labels))$('theme-'+id).value=settings.colors[id];for(const id of ['titleFont','bodyFont','captionFont']){$(id).value=settings[id];$(id).style.fontFamily=settings[id];}$('themePreset').value=settings.palette==='custom'?'':settings.palette;}
function apply(){const d=frameEl.contentDocument;if(!d?.documentElement)return;const root=d.documentElement,on=$('themePreview').checked,s=on?settings:original;
  for(const role of ['title','body','caption'])root.style.setProperty('--'+role+'-tracking',(s[role+'Tracking']??0)+'px');
  root.style.setProperty('--theme-ink',s.colors.ink);root.style.setProperty('--theme-accent',s.colors.accent);root.style.setProperty('--caption-bg',s.colors.captionBg);root.style.setProperty('--caption-text',s.colors.captionText);
  root.style.setProperty('--title-font',s.titleFont);root.style.setProperty('--body-font',s.bodyFont);root.style.setProperty('--caption-font',s.captionFont);
  const w=frameEl.contentWindow;if(w?.reviewRelayout)d.fonts.ready.then(()=>{w.reviewRelayout();w.seekReview?.(video.currentTime,!video.paused,video.playbackRate);});}
function activate(){localStorage.setItem(key,JSON.stringify(settings));$('themePreview').checked=true;localStorage.setItem(key+'-enabled','true');ui();apply();$('themeStatus').textContent='Aperçu mis à jour · MP4 inchangé';}
$('themePreset').onchange=()=>{const name=$('themePreset').value;if(!palettes[name])return;settings.palette=name;settings.colors={...palettes[name]};activate();};
$('resetTheme').onclick=()=>{settings=structuredClone(original);activate();};
$('themePreview').checked=localStorage.getItem(key+'-enabled')==='true';$('themePreview').onchange=()=>{localStorage.setItem(key+'-enabled',String($('themePreview').checked));apply();};
$('saveTheme').onclick=()=>{const c={id:crypto.randomUUID(),time:video.currentTime,end:null,global:true,scene:'Style global',text:`Style global : palette ${settings.palette}, textes blancs ${settings.titleFont}, grands obliques ${settings.bodyFont}, capsules ${settings.captionFont}. Couleurs : blancs ${settings.colors.ink}, obliques ${settings.colors.accent}, capsule ${settings.colors.captionBg} / ${settings.colors.captionText}. Espacement ajouté : blancs ${settings.titleTracking??0}px, obliques ${settings.bodyTracking??0}px, capsules ${settings.captionTracking??0}px. Réglages exacts joints au retour.`,shapes:[],attachments:[],done:false,theme:{source:'c0210-claude-steve-classique',version:'v1',preset:'b309b30d-b39e-405a-aab7-49e57a9498b7@1',scope:'global',roles:{titleFont:'textes blancs .s-w',bodyFont:'grands obliques .s-o',captionFont:'capsules rouges .s-r'},...structuredClone(settings)}};state.comments=state.comments.filter(x=>!x.theme);state.comments.push(c);save();renderList();renderMarkers();toast('Style ajouté aux retours · pense à les envoyer');};
frameEl.addEventListener('load',apply);ui();apply();
})();
