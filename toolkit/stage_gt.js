 // ---- Gotthard-Bühne ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const win=(tt,a,b,fi,fo)=>pr(tt,a,fi)*(1-pr(tt,b,fo));
  const ks=PAN.cam.map(k=>({t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4]}));
  function cam(tt){ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e)};}} return ks[ks.length-1]; }
  const c=cam(t); const zz=c.z*(1+0.012*Math.sin(t*0.9));
  document.getElementById('camg').setAttribute('transform',`translate(500 400) scale(${zz.toFixed(4)}) translate(${(-c.x).toFixed(2)} ${(-c.y).toFixed(2)})`);
  for(const e of document.querySelectorAll('.wg')){ let o=1; if(e.dataset.wi) o*=pr(t,S[e.dataset.wi]-0.05,0.3); if(e.dataset.wo) o*=1-pr(t,S[e.dataset.wo],0.3); e.setAttribute('opacity',o.toFixed(3)); }
  for(const e of document.querySelectorAll('.dr')){ const t0=S[e.dataset.a]+(+e.dataset.dl||0); e.style.strokeDashoffset=(1-ease(pr(t,t0,+e.dataset.dur||1))).toFixed(4); }
  for(const e of document.querySelectorAll('.wfade')){ e.setAttribute('opacity',pr(t,S[e.dataset.fa]+(+e.dataset.fd||0),0.2).toFixed(3)); }
  const sw=Math.max(1,(1/zz)*1.0);
  for(const e of document.querySelectorAll('.shaft')) e.setAttribute('stroke-width',(16).toFixed(1));
  // Tunnelspitzen
  const TY=PAN.ty, MX=PAN.mx;
  const meet=ease(pr(t,S['s15@trafen']-0.4,0.8));
  let L=700+360*ease(pr(t,-0.3,S['s2@genau']+0.3)); L=L+(MX-L)*meet;
  let R=1500-360*ease(pr(t,-0.3,S['s2@genau']+0.3)); R=R+(MX-R)*meet;
  document.getElementById('tunL').setAttribute('d',`M60 ${TY} L${L.toFixed(1)} ${TY}`);
  document.getElementById('tunR').setAttribute('d',`M${R.toFixed(1)} ${TY} L1940 ${TY}`);
  const jit=1.5*Math.sin(t*40);
  document.getElementById('tipL').setAttribute('cx',(L+jit).toFixed(1)); document.getElementById('tipL').setAttribute('cy',TY);
  document.getElementById('tipR').setAttribute('cx',(R-jit).toFixed(1)); document.getElementById('tipR').setAttribute('cy',TY);
  document.getElementById('qm').setAttribute('opacity',(win(t,S['s2']-0.2,S['s3'],0.3,0.3)).toFixed(3));
  document.getElementById('tipglow').setAttribute('opacity',(0.5+0.5*Math.sin(t*5))*win(t,S['s15@trafen']+0.2,S['s16'],0.3,0.4));
  { const b=document.getElementById('burst'); const p=pr(t,S['s15@trafen']+0.3,0.5); b.setAttribute('opacity',(p>0&&p<1?1-p:0).toFixed(3)); b.setAttribute('transform',`translate(${MX} ${TY}) scale(${(0.6+p*0.8).toFixed(3)}) translate(${-MX} ${-TY})`); }
  for(const e of document.querySelectorAll('.ws')){ const k=+e.dataset.k; e.setAttribute('r',(22*ease(pr(t,S['s4@Stellen']-0.1+k*0.12,0.3))*(1+0.15*Math.sin(t*6+k))).toFixed(1)); }
  // Bohrmaschine
  { const z=c.z; const tb=win(t,S['s5']+0.25,S['s7']-0.2,0.3,0.3); document.getElementById('tbm').style.opacity=tb.toFixed(3);
    document.getElementById('cutter').setAttribute('transform',`translate(850 390) rotate(${(t*120)%360})`);
    document.getElementById('tbmg').setAttribute('transform',`translate(${(-40+30*pr(t,S['s5'],3)).toFixed(1)} 0)`);
    document.getElementById('tbmq').setAttribute('opacity',win(t,S['s6@wohin']-0.2,S['s7'],0.25,0.2).toFixed(3)); }
  // große Zahlen
  { const p=ease(pr(t,S['s3@57']-0.1,0.8)); const B=document.getElementById('big57'); B.textContent=Math.round(57*p)+' KM'; B.style.opacity=win(t,S['s3@57']-0.2,S['s4']-0.1,0.25,0.3).toFixed(3); }
  { const p=ease(pr(t,S['s15@2010']-0.1,0.8)); const B=document.getElementById('big2010'); B.textContent=Math.round(1999+11*p); B.style.opacity=win(t,S['s15@2010']-0.2,S['s16']-0.1,0.25,0.3).toFixed(3); }
  // Messpunkt-Kette
  const ch=PAN.chain; const n=ch.length;
  [...document.querySelectorAll('.mp')].forEach((e,k)=>{ const t0=S['s9@Messpunkt']-0.2+k*((S['s9@Maschine']-S['s9@Messpunkt'])/n); e.setAttribute('opacity',(pr(t,t0,0.15)*(1-pr(t,S['s15'],0.3))).toFixed(3)); });
  { const Ls=document.getElementById('laser'); const p=pr(t,S['s10@Lasergerät']-0.1,S['s11']-S['s10@Lasergerät']); const f=p*(n-1); const i=Math.min(n-2,Math.floor(f)); const u=f-i;
    const x0=ch[i], x1=ch[i]+(ch[i+1]-ch[i])*Math.min(1,u*1.6);
    Ls.setAttribute('x1',x0); Ls.setAttribute('x2',x1.toFixed(1)); Ls.setAttribute('y1',TY-6); Ls.setAttribute('y2',TY-6); Ls.setAttribute('opacity',win(t,S['s10@Lasergerät']-0.1,S['s11'],0.2,0.2).toFixed(3)); }
  document.getElementById('fans').setAttribute('opacity',win(t,S['s11@winzigen']-0.2,S['s13'],0.3,0.3).toFixed(3));
  { const D=document.getElementById('drift'); const corr=ease(pr(t,S['s13@Kreiselkompass'],1.0)); const grow=ease(pr(t,S['s12']-0.1,1.2));
    const a=0.16*(1-corr); let d=`M1940 ${TY}`; for(let k=1;k<=20;k++){ const x=1940-42*k*grow; const y=TY+a*(42*k*grow)*(k/20); d+=` L${x.toFixed(1)} ${y.toFixed(1)}`; }
    D.setAttribute('d',d); D.setAttribute('opacity',win(t,S['s12']-0.1,S['s15'],0.3,0.3).toFixed(3)); D.setAttribute('stroke',corr>0.6?'#19C6B4':'#E5484D');
    document.getElementById('miss').setAttribute('opacity',win(t,S['s12@abdriften'],S['s13@Kreiselkompass'],0.3,0.3).toFixed(3)); }
  // Kreisel + Erde
  document.getElementById('gyro').style.opacity=win(t,S['s13@Kreiselkompass']-0.3,S['s14'],0.3,0.25).toFixed(3);
  document.getElementById('gyrod').setAttribute('transform',`scale(${Math.cos(t*14).toFixed(3)} 1)`);
  document.getElementById('earth').style.opacity=win(t,S['s14']-0.05,S['s15']-0.1,0.3,0.25).toFixed(3);
  [...document.querySelectorAll('.mer')].forEach((e,k)=>{ const ph=(t*1.2+k*Math.PI/4)%Math.PI; e.setAttribute('rx',(110*Math.abs(Math.cos(ph))).toFixed(1)); });
  // Abweichung
  { const dv=pr(t,S['s16']-0.1,0.35); document.getElementById('dev').style.opacity=dv.toFixed(3);
    document.getElementById('devq').style.opacity=(1-pr(t,S['s17']-0.1,0.2)).toFixed(3);
    document.getElementById('n8').style.opacity=pr(t,S['s17@8']-0.15,0.25).toFixed(3); document.getElementById('n1').style.opacity=pr(t,S['s17@1']-0.15,0.25).toFixed(3);
    document.getElementById('bar8').style.transform=`scaleX(${ease(pr(t,S['s17@8']-0.1,0.6)).toFixed(3)})`;
    document.getElementById('bar1').style.transform=`scaleX(${ease(pr(t,S['s17@1']-0.1,0.6)).toFixed(3)})`;
    document.getElementById('bar25').style.transform=`scaleX(${ease(pr(t,S['s18@25']-0.1,0.7)).toFixed(3)})`;
    document.getElementById('n25').style.opacity=pr(t,S['s18@25']+0.3,0.3).toFixed(3); }
  { const H_=document.getElementById('head'); H_.style.opacity=(+H_.style.opacity||0)*(1-pr(t,S['s3']-0.3,0.35)); }
 }
