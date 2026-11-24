 // ---- CERN-Bühne ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const win=(tt,a,b,fi,fo)=>pr(tt,a,fi)*(1-pr(tt,b,fo));
  const $=id=>document.getElementById(id);
  const sm=u=>u*u*(3-2*u);
  // ---------- Ebenen ----------
  const tr=PAN.tr.map(x=>({t:TS(x[0],x[1]),l:x[2]}));
  let cur=tr[0].l, prev=null, tp=1;
  for(const x of tr){ if(t>=x.t && x.l!==cur){ prev=cur; cur=x.l; tp=pr(t,x.t,0.6); } }
  for(const l of ['m','c','g','e']){
    const L=$('L'+l); let o=0, s=1;
    if(l===cur){ o=prev?sm(tp):1; s=prev?0.72+0.28*ease(tp):1; }
    else if(l===prev && tp<1){ o=1-sm(tp); s=1+0.6*ease(tp); }
    L.style.opacity=o.toFixed(3); L.style.transform=`scale(${s.toFixed(4)})`; L.style.display=o<0.002?'none':'block';
  }
  const vis=l=>(l===cur)||(l===prev&&tp<1);
  // ---------- Karte ----------
  if(vis('m')){
   const ks=PAN.mc.map(k=>({t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4]}));
   let c=ks[0]; if(t>ks[0].t){ c=ks[ks.length-1]; for(let i=0;i<ks.length-1;i++){const k0=ks[i],k1=ks[i+1]; if(t>=k0.t&&t<k1.t){const u=sm((t-k0.t)/Math.max(1e-6,k1.t-k0.t)); c={x:k0.x+(k1.x-k0.x)*u,y:k0.y+(k1.y-k0.y)*u,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*u)}; break;}} }
   const z=c.z*(1+0.012*Math.sin(t*0.9));
   $('mcam').setAttribute('transform',`translate(540 440) scale(${z.toFixed(4)}) translate(${(-c.x).toFixed(2)} ${(-c.y).toFixed(2)})`);
   const [RX,RY,RR]=PAN.rc;
   // Ring atmet (Hook + Mond-Teil)
   const br=win(t,-1,TS('b3',0),0.1,0.4)+win(t,TS('b19',-0.2),TS('b21',-0.3),0.4,0.4);
   const ph=Math.sin(t*3.2); const sx=1+0.045*br*ph, sy=1-0.03*br*ph;
   $('ringg').setAttribute('transform',`translate(${RX} ${RY}) scale(${sx.toFixed(4)} ${sy.toFixed(4)}) translate(${-RX} ${-RY})`);
   $('ringghost').setAttribute('opacity',(0.9*br).toFixed(3));
   $('ringghost').setAttribute('transform',`translate(${RX} ${RY}) scale(${(1/sx).toFixed(4)} ${(1/sy).toFixed(4)}) translate(${-RX} ${-RY})`);
   $('mnote').setAttribute('opacity',br.toFixed(3));
   $('mmoon').setAttribute('opacity',(win(t,-1,TS('b3',0.2),0.1,0.4)+win(t,TS('b19',-0.2),TS('b21',-0.3),0.4,0.4)).toFixed(3));
   $('mmoon').setAttribute('transform',`translate(0 ${(6*Math.sin(t*1.7)).toFixed(1)})`);
   $('pull').setAttribute('opacity',(0.9*br*(0.6+0.4*Math.sin(t*6))).toFixed(3));
   $('ringrun').style.strokeDashoffset=(-t*90).toFixed(1);
   $('ringglow').setAttribute('opacity',(0.8*win(t,TS('b3@27',-0.3),TS('b3@100',0),0.3,0.4)).toFixed(3));
   // Grenze, Länder, CERN
   $('border').setAttribute('opacity',pr(t,TS('b4@Grenze',-0.3),0.2).toFixed(3));
   $('border').style.strokeDasharray=`${(ease(pr(t,TS('b4@Grenze',-0.3),1.2))).toFixed(4)} 1`;
   $('cty').setAttribute('opacity',(pr(t,TS('b4@Schweiz',-0.2),0.4)*(1-pr(t,TS('b25@schwarzes',-0.4),0.4))).toFixed(3));
   $('cern').setAttribute('opacity',(pr(t,TS('b4@CERN',-0.2),0.3)*(1-win(t,TS('b13',-0.4),TS('b16',0),0.3,0.3))).toFixed(3));
   // Held-Proton
   let ang=-90, w=0.9; const t6=TS('b6@fast',-0.2);
   for(let s=0;s<t;s+=1/30){ const acc=pr(s,t6,1.6); w=0.9+(11-0.9)*acc*acc; ang+=w*57.3/30; }
   const hv=win(t,-1,TS('b11',0),0.1,0.3);
   const hx=RX+RR*Math.cos(ang*Math.PI/180), hy=RY+RR*Math.sin(ang*Math.PI/180);
   $('hero').setAttribute('transform',`translate(${hx.toFixed(1)} ${hy.toFixed(1)})`); $('hero').setAttribute('opacity',hv.toFixed(3));
   // zwei Strahlen
   const bv=win(t,TS('b11',-0.2),TS('b16',0),0.4,0.3)+win(t,TS('b19',-0.2),TS('b25@schwarzes',0),0.4,0.4);
   document.querySelectorAll('.pa').forEach(e=>{const k=+e.dataset.k; const a=(t*130+k*60)*Math.PI/180; e.setAttribute('cx',(RX+RR*Math.cos(a)).toFixed(1)); e.setAttribute('cy',(RY+RR*Math.sin(a)).toFixed(1)); e.setAttribute('opacity',bv.toFixed(3));});
   document.querySelectorAll('.pb').forEach(e=>{const k=+e.dataset.k; const a=(-t*130+k*60+30)*Math.PI/180; e.setAttribute('cx',(RX+RR*Math.cos(a)).toFixed(1)); e.setAttribute('cy',(RY+RR*Math.sin(a)).toFixed(1)); e.setAttribute('opacity',bv.toFixed(3));});
   $('exps').setAttribute('opacity',win(t,TS('b12@vier',-0.3),TS('b16',0),0.3,0.3).toFixed(3));
   document.querySelectorAll('.exr').forEach((e,k)=>{ const p=((t*2.2+k*0.25)%1); e.setAttribute('r',(14+26*p).toFixed(1)); e.setAttribute('opacity',(1-p).toFixed(3)); });
   // Kollision
   const t13=TS('b13@Aufpralls',-0.4);
   $('burst').setAttribute('opacity',win(t,t13,TS('b16',0),0.1,0.3).toFixed(3));
   document.querySelectorAll('.trk').forEach((e,k)=>{ const t0=t13+(k%6)*0.12+Math.floor(k/6)*0.9; e.style.strokeDashoffset=(1-ease(pr(t,t0,0.5))).toFixed(4); e.setAttribute('stroke-opacity',(1-0.6*pr(t,t0+1.6,0.6)).toFixed(3)); });
   const fl=pr(t,t13,0.08)*(1-pr(t,t13+0.2,0.5))+0.35*win(t,t13+0.9,t13+1.2,0.05,0.2)+0.35*win(t,TS('b15',-0.1),TS('b15',0.2),0.05,0.3);
   $('flash').setAttribute('opacity',fl.toFixed(3)); $('flash').setAttribute('r',(40+50*fl).toFixed(1));
   $('higgs').setAttribute('opacity',pr(t,TS('b15@Higgs-Teilchen',-0.4),0.3).toFixed(3));
   // Schwarzes Loch
   const bh=win(t,TS('b25@schwarzes',-0.3),TS('b26',0.1),0.5,0.3);
   $('bhole').setAttribute('opacity',bh.toFixed(3));
   document.querySelectorAll('.sw').forEach((e,k)=>e.setAttribute('transform',`rotate(${(t*(60+k*25)).toFixed(1)})`));
   $('bhq').setAttribute('opacity',pr(t,TS('b25@erzeugen',-0.2),0.3).toFixed(3));
  }
  // ---------- Querschnitt ----------
  if(vis('c')){
   const inB18=t>=TS('b18',-0.4);
   const z=1+0.02*Math.sin(t*0.8)+(inB18?0:0.08*(1-ease(pr(t,TS('b3@100',-0.25),1.2))));
   $('ccam').setAttribute('transform',`translate(540 440) scale(${z.toFixed(4)}) translate(-540 -440)`);
   $('depth').setAttribute('opacity',(inB18?0:pr(t,TS('b3@100',0.0),0.4)).toFixed(3));
   const rise=inB18?ease(pr(t,TS('b18@wölbt',-0.2),1.0))*(0.85+0.15*Math.sin((t-TS('b18@wölbt',0))*2.5)):0;
   $('cground').setAttribute('transform',`translate(0 ${(-60*rise).toFixed(1)})`);
   $('cbase').setAttribute('opacity',(inB18?pr(t,TS('b18@wölbt',-0.2),0.3):0).toFixed(3));
   $('cmoon').setAttribute('opacity',(inB18?1:0));
   $('cpull').setAttribute('opacity',(inB18?(0.6+0.4*Math.sin(t*6))*pr(t,TS('b18',-0.1),0.3):0).toFixed(3));
  }
  // ---------- Magnete ----------
  if(vis('g')){
   const [AX,AY,AR]=PAN.arc; const D=Math.PI/180;
   const g=$('mags');
   if(!g.childNodes.length){ let h=''; for(let k=0;k<11;k++){ h+=`<g class="mg" data-k="${k}"><rect x="-70" y="-78" width="140" height="156" rx="16" fill="#E9E4F9" stroke="#2B2D35" stroke-width="3.5"/>`+
      `<rect x="-52" y="-60" width="104" height="120" rx="10" fill="none" stroke="#7B3FE4" stroke-width="4"/>`+
      `<path class="coil" d="M-52 -30 H52 M-52 0 H52 M-52 30 H52" stroke="#E8A33D" stroke-width="5" stroke-dasharray="10 12" fill="none"/>`+
      `<rect x="-70" y="-14" width="140" height="28" fill="#fff" stroke="#2B2D35" stroke-width="2.5"/></g>`; } g.innerHTML=h; }
   const spread=1+0.22*ease(pr(t,TS('b21@auseinander',-0.6),0.9))*(1-ease(pr(t,TS('b24@nachgeregelt',0),0.8)));
   const z=(t<TS('b21',-0.3)?0.82+0.18*ease(pr(t,TS('b8',-0.25),1.2)):1.0)*(1+0.012*Math.sin(t*0.9));
   $('gcam').setAttribute('transform',`translate(540 440) scale(${z.toFixed(4)}) translate(-540 -400)`);
   const coilOn=pr(t,TS('b10@Strom',-0.3),0.3)*(t<TS('b11',0)?1:0)+ (t>=TS('b21',-0.5)?0.5:0);
   document.querySelectorAll('.mg').forEach(e=>{ const k=+e.dataset.k; const a=(-90+(k-5)*6.2*spread)*D; const r=AR;
     const x=AX+r*Math.cos(a), y=AY+r*Math.sin(a); e.setAttribute('transform',`translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(a/D+90).toFixed(2)})`);
     e.querySelector('.coil').style.strokeDashoffset=(-t*80*coilOn).toFixed(1); e.querySelector('.coil').setAttribute('opacity',(0.25+0.75*coilOn).toFixed(2)); });
   const off=34*ease(pr(t,TS('b22@mittig',-0.5),0.7))*(1-ease(pr(t,TS('b24@Mitte',-0.6),0.8)));
   const r=AR+off; const a0=-122, a1=-58;
   $('ppath').setAttribute('d',`M${(AX+r*Math.cos(a0*D)).toFixed(1)} ${(AY+r*Math.sin(a0*D)).toFixed(1)} A${r} ${r} 0 0 1 ${(AX+r*Math.cos(a1*D)).toFixed(1)} ${(AY+r*Math.sin(a1*D)).toFixed(1)}`);
   $('ppath').setAttribute('stroke',off>6?'#E5484D':'#7B3FE4');
   const u=((t-TS('b8',0))/1.5)%1; const aa=(a0+(a1-a0)*((u+1)%1))*D;
   $('ghero').setAttribute('transform',`translate(${(AX+r*Math.cos(aa)).toFixed(1)} ${(AY+r*Math.sin(aa)).toFixed(1)})`);
   const fv=win(t,TS('b9@gekühlt',-0.4),TS('b11',0),0.6,0.3);
   $('frost').setAttribute('opacity',fv.toFixed(3));
   if(!window._fr){ window._fr=[...document.querySelectorAll('.fr')].map((e,k)=>{ const a=(-90+(k%11-5)*6.2+ (k>10?2.4:-2.4))*D; const rr=AR+(k>10?60:-60); return [AX+rr*Math.cos(a),AY+rr*Math.sin(a)]; }); }
   document.querySelectorAll('.fr').forEach((e,k)=>{ const p=window._fr[k]; const s=pr(t,TS('b9@gekühlt',-0.4)+k*0.05,0.3); e.setAttribute('transform',`translate(${p[0].toFixed(1)} ${p[1].toFixed(1)}) scale(${(s*(1+0.1*Math.sin(t*3+k))).toFixed(3)}) rotate(${(k*17).toFixed(0)})`); });
   $('knob').setAttribute('opacity',win(t,TS('b24',-0.2),TS('b25',0),0.3,0.3).toFixed(3));
   $('knobi').setAttribute('transform',`rotate(${(-70*ease(pr(t,TS('b24@nachgeregelt',-0.4),1.0))+25).toFixed(1)})`);
  }
  // ---------- Erde ----------
  if(vis('e')){
   const z=1+0.015*Math.sin(t*0.8);
   $('ecam').setAttribute('transform',`translate(540 440) scale(${z.toFixed(4)}) translate(-540 -440)`);
   const tide=ease(pr(t,TS('b17@Meer',-0.3),0.8))*(t<TS('b26',-0.4)?1:0);
   const gtide=ease(pr(t,TS('b17@Boden',-0.3),0.8))*(t<TS('b26',-0.4)?1:0);
   const wob=0.85+0.15*Math.sin(t*2.4);
   $('ebulge').setAttribute('rx',(232+48*tide*wob).toFixed(1)); $('ebulge').setAttribute('ry',(232-8*tide*wob).toFixed(1)); $('ebulge').setAttribute('opacity',(tide).toFixed(3));
   $('gbulge').setAttribute('rx',(230+20*gtide*wob).toFixed(1)); $('gbulge').setAttribute('ry',(230-4*gtide*wob).toFixed(1)); $('gbulge').setAttribute('opacity',gtide.toFixed(3));
   $('elab').setAttribute('opacity',(pr(t,TS('b17@Boden',-0.2),0.4)*(t<TS('b26',-0.4)?1:0)).toFixed(3));
   $('emoon').setAttribute('transform',`translate(0 ${(10*Math.sin(t*1.3)).toFixed(1)})`);
   $('emoon').setAttribute('opacity',(t<TS('b26',-0.4)?1:0.25).toFixed(2));
   const rv=win(t,TS('b26@Weltall',-0.4),'end' in S?TS('end',0.3):1e9,0.5,0.4);
   $('rays').setAttribute('opacity',rv.toFixed(3));
   document.querySelectorAll('.ray').forEach(e=>{ const k=+e.dataset.k; const a=(k*137.5)%360*Math.PI/180; const per=1.1+(k%5)*0.13; const p=((t*1.0+k*0.173)%per)/per;
     const R0=700-470*p, R1=R0+70; e.setAttribute('x1',(440+R1*Math.cos(a)).toFixed(1)); e.setAttribute('y1',(470+R1*Math.sin(a)).toFixed(1)); e.setAttribute('x2',(440+R0*Math.cos(a)).toFixed(1)); e.setAttribute('y2',(470+R0*Math.sin(a)).toFixed(1)); e.setAttribute('opacity',(p<0.92?1:0)); });
   $('eok').setAttribute('opacity',(pr(t,TS('b27@Erde',-0.2),0.4)*(0.7+0.3*Math.sin(t*4))).toFixed(3));
   const lp=0.5+0.5*Math.sin(t*5); $('eloc').setAttribute('opacity',(0.6+0.4*lp).toFixed(3));
  }
  // ---------- HTML-Overlays mit Zuständen ----------
  { const e=$('temp'); const p=ease(pr(t,TS('b9@minus',-0.1),1.1)); e.textContent=(p<0.02?'20':'−'+Math.round(271*p)).replace('−0','0'); e.style.color=p>=1?'#2F9FD0':'#0B0B10';
    $('tsub').style.opacity=pr(t,TS('b9@kälter',-0.2),0.3).toFixed(3); }
  { const n=$('needle'); const wv=pr(t,TS('b22@Energie',0),0.3); n.setAttribute('transform',`rotate(${(wv*(22*Math.sin(t*5.5)+10*Math.sin(t*13))).toFixed(1)})`); }
  // Headline nach dem Hook ausblenden (dyn_ws überschreibt die Opacity)
  { const H_=$('head'); H_.style.opacity=(+H_.style.opacity||0)*(1-pr(t,S['b3']-0.3,0.35)); }
 }
