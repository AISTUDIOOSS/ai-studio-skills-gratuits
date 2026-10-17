/* Shared deterministic caption renderer: source-pixel geometry, no wall-clock animation. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.CaptionRenderer=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 function pose(c,frame,positions={}){
  const p=positions[c.id]||c,u=Math.max(0,Math.min(1,(frame-c.startFrame)/(c.durationFrames||20)));
  const ease=u*u*u*(u*(u*6-15)+10);
  return{x:p.x,y:p.y+(c.animation==='rise'?(c.risePx||0)*(1-ease):0),alpha:c.animation==='rise'?Math.min(1,2*u)**2*(3-2*Math.min(1,2*u)):1};
 }
 function effective(c,sizes={}){return {...c,fontSize:sizes[c.id]??c.fontSize};}
 function metrics(ctx,c,doc){
  c=effective(c,doc.sizes||{});
  const spacing=c.fontSize*(doc.style?.letterSpacingEm??-.025),lineHeight=c.fontSize*(doc.style?.lineHeight??.94);
  ctx.font=`${c.fontSize}px ${c.font==='lightOblique'?'CaptionLightOblique':c.font==='oblique'?'CaptionOblique':'CaptionHeavy'}`;
  if('letterSpacing' in ctx)ctx.letterSpacing=spacing+'px';
  const measure=text=>('letterSpacing' in ctx?ctx.measureText(text).width:[...text].reduce((w,ch)=>w+ctx.measureText(ch).width,0)+Math.max(0,[...text].length-1)*spacing);
  return{spacing,lineHeight,measure};
 }
 function draw(ctx,doc,frame,positions={},options={}){
  const width=options.width||doc.width,height=options.height||doc.height;
  if(options.clear!==false)ctx.clearRect(0,0,width,height);
  ctx.save();ctx.scale(width/doc.width,height/doc.height);ctx.textAlign='center';ctx.textBaseline='middle';
  for(const original of doc.captions){const c=effective(original,options.sizes||doc.sizes||{});if(frame<c.startFrame||frame>=c.endFrame)continue;
   const p=pose(c,frame,positions),lines=c.text.split('\n'),m=metrics(ctx,c,doc);ctx.fillStyle=c.color||'#fff';ctx.globalAlpha=p.alpha;
   lines.forEach((line,i)=>{const y=p.y+(i-(lines.length-1)/2)*m.lineHeight;
    if(c.highlight){
     const h=c.highlight, box=ctx.measureText(line), pad=h.paddingPx??c.fontSize*.09;
     const py=h.paddingY??pad*.55;
     const left=p.x-box.actualBoundingBoxLeft-pad, top=y-box.actualBoundingBoxAscent-py;
     const bw=box.actualBoundingBoxLeft+box.actualBoundingBoxRight+2*pad, bh=box.actualBoundingBoxAscent+box.actualBoundingBoxDescent+2*py;
     const u=Math.max(0,Math.min(1,(frame-c.startFrame+1)/(h.durationFrames||8))), reveal=1-(1-u)**3;
     ctx.fillStyle=h.color||'#ff0000';ctx.fillRect(left,top,bw*reveal,bh);ctx.fillStyle=c.color||'#fff';
    }
    if('letterSpacing' in ctx)ctx.fillText(line,p.x,y);
    else{let x=p.x-m.measure(line)/2;ctx.textAlign='left';for(const ch of [...line]){ctx.fillText(ch,x,y);x+=ctx.measureText(ch).width+m.spacing;}ctx.textAlign='center';}
   });
  }ctx.restore();
 }
 return{pose,draw,metrics,effective};
});
