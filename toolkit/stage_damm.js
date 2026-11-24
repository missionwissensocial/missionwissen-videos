 // ---- Damm-Bühne ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const win=(tt,a,b,fi,fo)=>pr(tt,a,fi)*(1-pr(tt,b,fo));
  const G=PAN.geo, D=Math.PI/180, R0=400;
  const $=id=>document.getElementById(id);
  // ---------- Ebenen-Übergänge ----------
  let vv=0;
  for(const tr of PAN.tr){ const t0=TS(tr[0],tr[1]); if(t>=t0-0.35){ const u=ease(pr(t,t0-0.35,0.6)); vv=tr[2]==='mv'?u:1-u; } }
  const ml=$('mlay'), vl=$('vlay');
  ml.style.opacity=(1-vv).toFixed(3); vl.style.opacity=vv.toFixed(3);
  ml.style.display=vv>0.999?'none':'block'; vl.style.display=vv<0.001?'none':'block';
  // ---------- Karte ----------
  if(vv<0.999){
   const ks=PAN.cam.map(k=>({t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4]}));
   function cam(tt){ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e)};}} return ks[ks.length-1]; }
   const c=cam(t); const z=c.z*(1+0.015*Math.sin(t*0.8))*(1+14*vv*vv);
   $('mcam').setAttribute('transform',`translate(540 440) scale(${z.toFixed(4)}) translate(${(-c.x).toFixed(3)} ${(-c.y).toFixed(3)})`);
   // Drehung
   let L0=108+100*(1-ease(pr(t,-0.2,3.4)));
   L0+=360*(1-Math.pow(1-pr(t,TS('b28',-0.15),2.6),2.2));
   if(t<TS('b28',-0.15)) L0=108+100*(1-ease(pr(t,-0.2,3.4)));
   const P0=30*D, sP=Math.sin(P0), cP=Math.cos(P0);
   function pj(lo,la){ const l=(lo-L0)*D, p=la*D, cp=Math.cos(p); const cs=sP*Math.sin(p)+cP*cp*Math.cos(l); let x=R0*cp*Math.sin(l), y=-R0*(cP*Math.sin(p)-sP*cp*Math.cos(l)); if(cs<0){const n=Math.hypot(x,y)||1; x=x/n*R0; y=y/n*R0;} return [x,y,cs]; }
   function rp(rings,close){ let s=''; for(const r of rings){ const q=r.map(p=>pj(p[0],p[1])); if(q.every(p=>p[2]<0)) continue; s+='M'+q.map(p=>p[0].toFixed(2)+' '+p[1].toFixed(2)).join('L')+(close?'Z':''); } return s; }
   const key=L0.toFixed(3);
   if(window._k!==key){ window._k=key;
     $('land1').setAttribute('d',rp(G.land,true)); $('land5').setAttribute('d',rp(G.land50,true)); $('cn').setAttribute('d',rp(G.cn,true));
     const gr=[]; for(let lo=-180;lo<180;lo+=30){const r=[]; for(let la=-80;la<=80;la+=5) r.push([lo,la]); gr.push(r);} for(let la=-60;la<=60;la+=30){const r=[]; for(let lo=-180;lo<=180;lo+=5) r.push([lo,la]); gr.push(r);}
     $('grat').setAttribute('d',rp(gr,false));
     $('yz').setAttribute('d',rp([G.yz],false));
     const rs=G.yz.slice(G.icq,G.idam+1).slice().reverse(); $('res').setAttribute('d',rp([rs],false)); $('resg').setAttribute('d',rp([rs],false));
     const ro=G.yz.slice(G.icq).slice().reverse(); $('route').setAttribute('d',rp([ro],false));
     window._ro=ro.map(p=>pj(p[0],p[1]));
     const dm=pj(G.dam[0],G.dam[1]); window._dm=dm;
   }
   const zt=z, dm=window._dm;
   const hi=pr(z,2.0,1.5); $('land5').setAttribute('opacity',hi.toFixed(3)); $('land1').setAttribute('opacity',(1-0.999*hi).toFixed(3));
   $('cn').setAttribute('opacity',(0.9*win(t,TS('b2@China',-0.3),TS('b24',0),0.5,0.6)).toFixed(3));
   const yzE=$('yz'); yzE.style.strokeDashoffset=(1-ease(pr(t,TS('b4@Jangtse',-0.6),1.8))).toFixed(4); yzE.setAttribute('stroke-width',(4.2/zt).toFixed(4));
   const rE=$('res'); rE.style.strokeDashoffset=(1-ease(pr(t,TS('b12@See',-0.2),1.4))).toFixed(4); rE.setAttribute('stroke-width',(10/zt).toFixed(4));
   $('resg').setAttribute('stroke-width',(26/zt).toFixed(4)); $('resg').setAttribute('opacity',(pr(t,TS('b12@See',0.8),0.5)*(1-pr(t,TS('b22',0),0.3))+win(t,TS('b24',-0.2),TS('b25',0),0.4,0.4)).toFixed(3));
   if(t<TS('b12@See',-0.3)) rE.setAttribute('opacity',0); else rE.setAttribute('opacity',1);
   // Schiff + Route
   const su=ease(pr(t,TS('b22@Frachtschiffe',-0.1),TS('b22@Land',0)-TS('b22@Frachtschiffe',-0.1)));
   const ro=window._ro; const roE=$('route'); roE.style.strokeDashoffset=(1-su).toFixed(4); roE.setAttribute('stroke-width',(4.5/zt).toFixed(4)); roE.setAttribute('opacity',win(t,TS('b22',-0.3),TS('b23',0.3),0.2,0.4).toFixed(3));
   { // Position entlang der Route (Bogenlänge)
     if(!window._rl){ let L=[0]; for(let i=1;i<ro.length;i++) L.push(L[i-1]+Math.hypot(ro[i][0]-ro[i-1][0],ro[i][1]-ro[i-1][1])); window._rl=L; }
     const L=window._rl, tot=L[L.length-1], d=su*tot; let i=1; while(i<L.length-1&&L[i]<d) i++;
     const f=(d-L[i-1])/Math.max(1e-6,L[i]-L[i-1]); const x=ro[i-1][0]+(ro[i][0]-ro[i-1][0])*f, y=ro[i-1][1]+(ro[i][1]-ro[i-1][1])*f;
     const sh=$('ship'); sh.setAttribute('transform',`translate(${x.toFixed(3)} ${y.toFixed(3)}) scale(${(1.25/zt).toFixed(5)}) scale(-1 1) translate(0 ${(-6+1.5*Math.sin(t*6)).toFixed(2)})`);
     sh.setAttribute('opacity',win(t,TS('b22',-0.1),TS('b23',0.2),0.3,0.3).toFixed(3));
   }
   // Damm-Punkt
   const dv=pr(t,TS('b2@Drei-Schluchten-Damm',-0.2),0.3);
   const dd=$('dam'); dd.setAttribute('cx',dm[0]); dd.setAttribute('cy',dm[1]); dd.setAttribute('r',(9/zt).toFixed(4)); dd.setAttribute('stroke-width',(3/zt).toFixed(4)); dd.setAttribute('opacity',dv.toFixed(3));
   const ph=(t*0.9)%1; const dp=$('dampulse'); dp.setAttribute('cx',dm[0]); dp.setAttribute('cy',dm[1]); dp.setAttribute('r',((10+34*ph)/zt).toFixed(4)); dp.setAttribute('stroke-width',(3/zt).toFixed(4)); dp.setAttribute('opacity',(dv*(1-ph)*0.9).toFixed(3));
   const gw=$('damglow'); gw.setAttribute('cx',dm[0]); gw.setAttribute('cy',dm[1]); gw.setAttribute('r',((90+20*Math.sin(t*4))/zt).toFixed(3)); gw.setAttribute('opacity',win(t,TS('b24',-0.2),TS('b25',0),0.4,0.4).toFixed(3));
   // Deutschland zum Vergleich (gleicher Maßstab, ortho um Deutschlandmitte)
   if(!window._de){ const lo0=G.decen[0]*D, la0=G.decen[1]*D; const pd=(lo,la)=>{const l=lo*D-lo0,p=la*D; return [R0*Math.cos(p)*Math.sin(l), -R0*(Math.cos(la0)*Math.sin(p)-Math.sin(la0)*Math.cos(p)*Math.cos(l))];};
     $('dep').setAttribute('d',G.de.map(r=>'M'+r.map(p=>pd(p[0],p[1]).map(v=>v.toFixed(2)).join(' ')).join('L')+'Z').join(''));
     const a=pd(G.hh[0],G.hh[1]), b=pd(G.mu[0],G.mu[1]); const ln=$('dline'); ln.setAttribute('x1',a[0]); ln.setAttribute('y1',a[1]); ln.setAttribute('x2',b[0]); ln.setAttribute('y2',b[1]); window._de=1; }
   $('deg').setAttribute('transform','translate(-8 30)'); $('deg').setAttribute('opacity',win(t,TS('b13',-0.2),TS('b14',0.3),0.4,0.3).toFixed(3));
   const dl=$('dline'); dl.setAttribute('stroke-width',(8/zt).toFixed(4)); dl.style.strokeDashoffset=(1-ease(pr(t,TS('b13@Hamburg',-0.1),1.0))).toFixed(4);
   // Achse
   let ang=0; const tw=win(t,TS('b33@kippt',-0.2),TS('b34',0.05),0.3,0.25); ang=tw*(26*Math.sin((t-TS('b33@kippt',-0.2))*5.5));
   $('axis').setAttribute('opacity',win(t,TS('b31@Erdachse',-0.4),TS('b35',-0.3),0.4,0.3).toFixed(3)); $('axis').setAttribute('transform',`rotate(${ang.toFixed(2)})`);
   $('axis').querySelector('line').setAttribute('stroke',tw>0.05?'#E5484D':'#7B3FE4');
   $('spin').setAttribute('opacity',win(t,TS('b28',-0.1),TS('b29',0.2),0.3,0.4).toFixed(3));
   // Labels
   const LG=$('labels'); if(!LG.childNodes.length){ for(const l of PAN.lb){ const e=document.createElementNS('http://www.w3.org/2000/svg','text'); e.textContent=l[0]; e.setAttribute('font-family','JBM'); e.setAttribute('font-weight','800'); e.setAttribute('fill',l[6]); e.setAttribute('text-anchor',l[9]); e.setAttribute('paint-order','stroke'); e.setAttribute('stroke','#fff'); e.setAttribute('stroke-linejoin','round'); LG.appendChild(e);} }
   PAN.lb.forEach((l,i)=>{ const e=LG.childNodes[i]; const p=pj(l[1],l[2]); e.setAttribute('x',(p[0]+l[7]/zt).toFixed(3)); e.setAttribute('y',(p[1]+l[8]/zt).toFixed(3)); e.setAttribute('font-size',(l[5]/zt).toFixed(4)); e.setAttribute('stroke-width',(6/zt).toFixed(4)); e.setAttribute('opacity',win(t,TS(l[3],-0.1),TS(l[4],0),0.3,0.3).toFixed(3)); });
  }
  // ---------- Tal ----------
  if(vv>0.001){
   const vs=0.4+0.6*vv; let vx=540,vy=440,vz=1;
   const fz=(a,o,d,x,y,zz,b,bo)=>{ const w=win(t,TS(a,o),TS(b,bo),d,0.7); vx+= (x-540)*w; vy+=(y-440)*w; vz*=1+(zz-1)*w; };
   fz('b9',-0.3,0.7,600,470,1.06,'b10',0); fz('b19',-0.2,0.7,540,640,1.55,'b20@Fünftel',-0.4); fz('b21',-0.3,0.7,540,560,1.05,'b22',0); fz('b35',-0.6,0.6,540,620,1.12,'end',0.5);
   vz*=1+0.012*Math.sin(t*0.7);
   $('vcam').setAttribute('transform',`translate(540 440) scale(${(vs*vz).toFixed(4)}) translate(${-vx} ${-vy})`);
   // Wasserpegel
   let lv=680;
   if(t>=TS('b6@Seite',-0.3)) lv=680+20*ease(pr(t,TS('b6@Seite',-0.3),0.8));
   if(t>=TS('b11',-0.2)) lv=700-370*ease(pr(t,TS('b11@stieg',-0.3),2.2));
   if(t>=TS('b14',0.1)) lv=680;
   if(t>=TS('b17',-0.2)) lv=680-340*ease(pr(t,TS('b17',0.0),3.0));
   if(t>=TS('b18',-0.2)) lv=340+4*Math.sin(t*2);
   const lw=(y)=>{ for(const id of ['lake','lake2']){ const e=$(id); e.setAttribute('y',y.toFixed(1)); e.setAttribute('height',(900-y).toFixed(1)); } $('lakesurf').setAttribute('d',`M0 ${y.toFixed(1)} H1080`); };
   lw(lv);
   // Tunnel (Umleitung)
   $('tunnel').setAttribute('opacity',win(t,TS('b6',-0.1),TS('b8',0),0.4,0.4).toFixed(3)); $('divflow').style.strokeDashoffset=(-t*60).toFixed(1);
   // Damm: Bau + Sichtbarkeit
   let H=0; if(t>=TS('b7',-0.2)){ const p=pr(t,TS('b7',-0.2),TS('b10@2006',0)-TS('b7',-0.2)); const q=Math.floor(p*16)/16, f=p*16-Math.floor(p*16); H=400*Math.min(1,q+ease(Math.min(1,f*1.6))/16); }
   const dclip=$('dclip'); dclip.setAttribute('y',(700-H).toFixed(1)); dclip.setAttribute('height',H.toFixed(1));
   const dvis=t<TS('b11',-0.2)?1:(t<TS('b18',-0.4)?1-ease(pr(t,TS('b11',-0.2),0.7)):ease(pr(t,TS('b18',-0.4),0.8)));
   $('dam').setAttribute('opacity',Math.min(1,dvis*1.4).toFixed(3)); $('dam').setAttribute('transform',`translate(0 ${(520*(1-dvis)).toFixed(1)})`);
   const topY=700-H; const bw=win(t,TS('b7',-0.3),TS('b10@Mauer',0.2),0.3,0.4);
   const xl=(y)=>{const L=[[0,250],[110,280],[200,400],[270,560],[300,700]]; for(let i=0;i<L.length-1;i++){ if(y>=L[i][1]&&y<=L[i+1][1]) return L[i][0]+(L[i+1][0]-L[i][0])*(y-L[i][1])/(L[i+1][1]-L[i][1]); } return 300;};
   const xr=(y)=>1080-xl(y)+(y>600?-0:0);
   document.querySelectorAll('.crane').forEach((c,k)=>{ const x=+c.dataset.x; c.setAttribute('transform',`translate(${x} ${topY.toFixed(1)})`); c.setAttribute('opacity',bw.toFixed(3)); c.querySelector('.jib').setAttribute('transform',`scale(${Math.cos(t*0.9+k*1.7).toFixed(3)} 1)`); });
   document.querySelectorAll('.wk').forEach((w,k)=>{ const a=xl(topY)+20, b=1080-xl(topY)-20; const u=((k*0.37+t*0.08*(k%2?1:-1))%1+1)%1; w.setAttribute('cx',(a+(b-a)*u).toFixed(1)); w.setAttribute('cy',(topY-5-2*Math.abs(Math.sin(t*6+k))).toFixed(1)); w.setAttribute('opacity',bw.toFixed(3)); });
   // Turbinen
   document.querySelectorAll('.turb').forEach((e,k)=>{ const on=pr(t,TS('b19',0.0)+k*0.045,0.08); e.setAttribute('fill',on>0.5?'#19C6B4':'#5D616B'); });
   $('jets').setAttribute('opacity',win(t,TS('b19@Turbinen',-0.3),TS('b21',0),0.4,0.4).toFixed(3));
   document.querySelectorAll('.jet').forEach((e,k)=>e.setAttribute('transform',`translate(0 ${(6*Math.sin(t*14+k)).toFixed(1)})`));
   // Maße + Dom
   $('dims').setAttribute('opacity',win(t,TS('b8@zwei',-0.2),TS('b10',0),0.4,0.3).toFixed(3));
   $('hdim').setAttribute('opacity',pr(t,TS('b8@180',-0.2),0.4).toFixed(3));
   $('dom').setAttribute('opacity',win(t,TS('b9@Kölner',-0.2),TS('b10',0.1),0.4,0.3).toFixed(3));
   // Altes Dorf + Menschen + neue Städte
   $('oldtown').setAttribute('opacity',win(t,TS('b11',-0.3),TS('b18',0),0.4,0.5).toFixed(3));
   const pv=win(t,TS('b14',0.1),TS('b18',-0.2),0.5,0.4); $('people').setAttribute('opacity',pv.toFixed(3));
   document.querySelectorAll('.pp').forEach(e=>{ const k=+e.dataset.k; const u=ease(pr(t,TS('b15@Million',0.1)+k*0.035,1.5)); const sx=+e.dataset.sx, sy=+e.dataset.sy, tx=+e.dataset.tx, ty=+e.dataset.ty;
     const x=sx+(tx-sx)*u, y=sy+(ty-sy)*u-10*Math.abs(Math.sin(u*Math.PI*5)); e.setAttribute('cx',x.toFixed(1)); e.setAttribute('cy',y.toFixed(1)); });
   $('city').setAttribute('opacity',win(t,TS('b16@Städte',-0.4),TS('b18',0),0.2,0.5).toFixed(3));
   document.querySelectorAll('.tw').forEach(e=>{ const k=+e.dataset.k; const u=pr(t,TS('b16@Städte',-0.2)+k*0.09,0.4); const s=1+2.7*Math.pow(u-1,3)+1.7*Math.pow(u-1,2); const yb=+e.dataset.yb; e.setAttribute('transform',`translate(0 ${yb}) scale(1 ${Math.max(0,s).toFixed(3)}) translate(0 ${-yb})`); });
   // Unterlauf-Stadt, Regen, Flut
   $('town').setAttribute('opacity',pr(t,TS('b21',-0.3),0.5).toFixed(3));
   const rv=win(t,TS('b21',-0.2),TS('b21@schützt',0.8),0.4,0.5); $('rain').setAttribute('opacity',rv.toFixed(3));
   document.querySelectorAll('.rd').forEach(e=>{ const k=+e.dataset.k; const x=(k*97)%1100-10, y=((t*900+k*173)%960)-80; e.setAttribute('transform',`translate(${(x-0.25*y*0.3).toFixed(1)} ${y.toFixed(1)})`); });
   const fl=ease(pr(t,TS('b35@Flutwelle',-0.5),1.1)); $('flood').setAttribute('opacity',(fl>0?1:0)); $('floodr').setAttribute('height',(200*fl).toFixed(1));
   document.querySelectorAll('.foam').forEach((e,k)=>e.setAttribute('transform',`translate(${(Math.sin(t*5+k)*8).toFixed(1)} ${(700+180*fl-6).toFixed(1)})`));
   $('crack').setAttribute('opacity',pr(t,TS('b35',-0.7),0.2).toFixed(3));
   document.querySelectorAll('#town .th').forEach((e,k)=>{ const s=pr(t,TS('b35@Flutwelle',-0.2)+k*0.05,0.4); e.setAttribute('opacity',(1-s).toFixed(3)); });
  }
  // ---------- HTML-Overlays mit Zuständen ----------
  { const y=$('year'); const p=pr(t,TS('b7',0),TS('b10@2006',0)-TS('b7',0)); y.textContent=String(Math.round(1994+12*ease(p))); y.style.color=p>=1?'#7B3FE4':'#0B0B10'; }
  { const f=$('defill'); const h=50*ease(pr(t,TS('b20@Fünftel',0.1),0.7)); f.setAttribute('y',(250-h).toFixed(1)); f.setAttribute('height',h.toFixed(1)); }
  { const u=ease(pr(t,TS('b26@höher',-0.2),0.9)); $('sdrop').setAttribute('transform',`translate(0 ${(-40*u).toFixed(1)})`); $('sw').setAttribute('transform',`translate(0 ${(-30*u).toFixed(1)})`); $('sarrow').setAttribute('opacity',pr(t,TS('b26@Erdmittelpunkt',-0.6),0.4).toFixed(3));
    const down=pr(t,TS('b25@unten',-0.3),0.4); $('sdrop').setAttribute('opacity',(0.35+0.65*Math.max(down,u)).toFixed(3)); }
  { // Eiskunstläuferin: Drehung integrieren
    const ta=TS('b27@ausstreckt',-0.2); const w0=9, w1=2.6; const ex=ease(pr(t,ta,0.6));
    let ph=0; const t0=TS('b27',-0.4); for(let s=t0;s<t;s+=1/30){ ph+=(w0+(w1-w0)*ease(pr(s,ta,0.6)))/30; }
    const L=40+50*ex, ay=-40+(-48)*ex; const cx=Math.cos(ph);
    const al=$('arml'), ar=$('armr'); al.setAttribute('x2',(-L*cx).toFixed(1)); al.setAttribute('y2',(ay).toFixed(1)); ar.setAttribute('x2',(L*cx).toFixed(1)); ar.setAttribute('y2',(ay).toFixed(1));
    $('sk').setAttribute('transform',`scale(${(0.85+0.15*Math.abs(Math.cos(ph))).toFixed(3)} 1)`);
    $('swirl').style.strokeDashoffset=(-ph*40).toFixed(1);
    const lab=$('sklab'); lab.textContent=t>TS('b27@langsamer',-0.3)?'ARME RAUS → LANGSAMER':'ARME AN → SCHNELL'; lab.style.color=t>TS('b27@langsamer',-0.3)?'#7B3FE4':'#0B0B10'; }
  { const go=ease(pr(t,TS('b32@Zentimeter',-0.3),0.9)); const back=ease(pr(t,TS('b34@zurück',-0.4),0.8)); const wob=win(t,TS('b33@kippt',-0.2),TS('b34',0),0.3,0.2)*24*Math.sin(t*16);
    $('pmark').setAttribute('transform',`translate(${(320*go*(1-back)+wob).toFixed(1)} 0)`); }
  // Headline nach dem Hook ausblenden (dyn_ws überschreibt die Opacity)
  { const H_=$('head'); H_.style.opacity=(+H_.style.opacity||0)*(1-pr(t,S['b3']-0.3,0.35)); }
 }
