 // ---- Preis-Bühne ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const win=(tt,a,b,fi,fo)=>pr(tt,a,fi)*(1-pr(tt,b,fo));
  const ks=PAN.cam.map(k=>({t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4]}));
  function cam(tt){ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e)};}} return ks[ks.length-1]; }
  const c=cam(t); const zz=c.z*(1+0.012*Math.sin(t*0.9));
  document.getElementById('camg').setAttribute('transform',`translate(500 400) scale(${zz.toFixed(4)}) translate(${(-c.x).toFixed(2)} ${(-c.y).toFixed(2)})`);
  for(const e of document.querySelectorAll('.wg')){ let o=1; if(e.dataset.wi) o*=pr(t,S[e.dataset.wi]-0.05,0.3); if(e.dataset.wo) o*=1-pr(t,S[e.dataset.wo],0.3); e.setAttribute('opacity',o.toFixed(3)); }
  for(const e of document.querySelectorAll('.dr')){ const t0=S[e.dataset.a]+(+e.dataset.dl||0); e.style.strokeDashoffset=(1-ease(pr(t,t0,+e.dataset.dur||1))).toFixed(4); }
  // Spike-Linien + Fade
  const gap=document.getElementById('gap'); gap.setAttribute('opacity',win(t,S['s8@verlangen']-0.2,S['s9'],0.4,0.3).toFixed(3));
  // Preisschild
  const TG=document.getElementById('tag');
  const tx=PAN.x57-290, ty=80; const pulse=1+0.06*Math.sin(t*7)*win(t,S['s11@minus']-0.1,S['s11@Prozent']+0.5,0.1,0.2);
  const pop=0.6+0.4*ease(pr(t,-0.2,0.35)); const sw=3*Math.sin(t*2.2);
  const tagOut=pr(t,S['s13']-0.1,0.3);
  TG.setAttribute('transform',`translate(${tx} ${ty}) rotate(${sw.toFixed(2)}) scale(${(0.85*pop*pulse).toFixed(3)})`);
  TG.setAttribute('opacity',(1-tagOut).toFixed(3));
  document.getElementById('tagq').setAttribute('opacity',(1-pr(t,S['s2']-0.1,0.3)).toFixed(3));
  document.getElementById('tags1').setAttribute('opacity',win(t,S['s3@angeben']-0.3,S['s6'],0.3,0.2).toFixed(3));
  document.getElementById('tags2').setAttribute('opacity',pr(t,S['s6@UVP']-0.1,0.3).toFixed(3));
  {const X_=document.getElementById('tagx'); X_.style.strokeDashoffset=(1-ease(pr(t,S['s11@Prozent']-0.1,0.35))).toFixed(3); X_.setAttribute('opacity',(1-pr(t,S['s12@20']-0.1,0.15)).toFixed(3));}
  document.getElementById('tagbg').setAttribute('fill',t>=S['s12@20']-0.1?'#19C6B4':'#7B3FE4');
  const TT=document.getElementById('tagt'); TT.textContent=t>=S['s12@20']-0.1?'−20 €':'−50%';
  // Bilanz
  const bil=pr(t,S['s13']+0.1,0.4)*(1-pr(t,S['s15']-0.2,0.4));
  document.getElementById('bil').style.opacity=bil.toFixed(3);
  const v=8*ease(pr(t,S['s14@8']-0.1,0.8)); const BN=document.getElementById('bnum'); BN.textContent='−'+Math.round(v)+'%'; BN.style.opacity=pr(t,S['s14@8']-0.4,0.3).toFixed(3);
  const bh=ease(pr(t,S['s14@Oktober']-0.2,0.6)); document.getElementById('bo').style.height=(260*ease(pr(t,S['s14@idealo'],0.6)))+'px';
  document.getElementById('bb').style.height=(239*ease(pr(t,S['s14@Schnitt']-0.1,0.6)))+'px';
  // Lupe fährt die Preislinie entlang
  const lu=document.getElementById('lupe'); const lp=pr(t,S['s15@Preisvergleich'],2.2); const lo=pr(t,S['s15@Preisvergleich']-0.2,0.3)*(1-pr(t,S['end']-0.1,0.3));
  { const i=Math.min(PAN.pts.length-1,Math.floor(lp*(PAN.pts.length-1))); const p=PAN.pts[i]; lu.setAttribute('transform',`translate(${p[0]} ${p[1]})`); lu.setAttribute('opacity',lo.toFixed(3)); }
  // Headline nach dem Hook ausblenden
  { const H_=document.getElementById('head'); H_.style.opacity=(+H_.style.opacity||0)*(1-pr(t,S['s3']-0.3,0.35)); }
 }
