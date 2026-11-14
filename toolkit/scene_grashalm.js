// ===================== INIT (einmalig) =====================
const cv=document.getElementById('cv'), X=cv.getContext('2d');
function mk(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
const off=mk(1080,1920), O=off.getContext('2d');
function rnd(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const L=(a,b,k)=>a+(b-a)*k; const sm=u=>{u=cl(u,0,1);return u*u*(3-2*u);}; const eio=u=>{u=cl(u,0,1);return u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;};
function hx(c){const n=parseInt(c.slice(1),16);return [n>>16,n>>8&255,n&255];}
function mixc(c1,c2,k){const a=hx(c1),b=hx(c2);return `rgb(${Math.round(L(a[0],b[0],k))},${Math.round(L(a[1],b[1],k))},${Math.round(L(a[2],b[2],k))})`;}
function rg(g,x,y,r,c0,c1){const q=g.createRadialGradient(x,y,0,x,y,r);q.addColorStop(0,c0);q.addColorStop(1,c1);g.fillStyle=q;g.beginPath();g.arc(x,y,r,0,7);g.fill();}
const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+(o||0);

// ---- Weizen-Ähre (Hauptdarsteller). Basis (0,0), zeigt nach oben. st(i) -> {gone, dx,dy,rot} ----
function ear(c,x,y,ang,s,o){
 o=o||{}; const n=o.n||14, sp=22;
 c.save(); c.translate(x,y); c.rotate(ang); c.scale(s,s);
 if(o.glow){ c.shadowColor=o.glow; c.shadowBlur=o.glowR||22; }
 c.lineCap='round';
 c.strokeStyle=o.rach||'#A87A34'; c.lineWidth=4; c.beginPath(); c.moveTo(0,0);
 for(let i=0;i<=n;i++){ c.lineTo((i%2?3:-3),-(i*sp+10)); } c.stroke();
 if(!o.bald) for(let i=0;i<n;i++){
  const side=i%2?1:-1; let px=side*10, py=-(i*sp+20); let rot=side*0.42;
  const st=o.st?o.st(i):null; if(st&&st.gone) continue;
  if(st){px+=st.dx||0; py+=st.dy||0; rot+=st.rot||0;}
  c.save(); c.translate(px,py); c.rotate(rot);
  c.strokeStyle=o.awn||'rgba(250,222,160,.8)'; c.lineWidth=1.7; c.beginPath(); c.moveTo(0,-18); c.quadraticCurveTo(side*5,-80,side*12,-(o.awnL||150)); c.stroke();
  const g=c.createLinearGradient(-12,-26,12,14); g.addColorStop(0,o.c0||'#FFE9B0'); g.addColorStop(.5,o.c1||'#E4AC52'); g.addColorStop(1,o.c2||'#9A6624');
  c.fillStyle=g; c.beginPath(); c.ellipse(0,-4,12.5,23,0,0,Math.PI*2); c.fill();
  c.shadowBlur=0;
  c.strokeStyle='rgba(95,58,16,.55)'; c.lineWidth=1.4; c.stroke();
  c.strokeStyle='rgba(95,58,16,.32)'; c.beginPath(); c.moveTo(0,-25); c.lineTo(0,17); c.stroke();
  if(o.rim){ c.strokeStyle=o.rim; c.lineWidth=3.2; c.beginPath(); c.ellipse(0,-4,13.5,24,0,-1.25,0.95); c.stroke(); }
  if(o.glow){ c.shadowColor=o.glow; c.shadowBlur=o.glowR||22; }
  c.restore();
 }
 c.restore();
}
function grain(c,x,y,rot,s,o){ o=o||{}; c.save(); c.translate(x,y); c.rotate(rot); c.scale(s,s);
 if(o.glow){c.shadowColor=o.glow;c.shadowBlur=o.glowR||16;}
 const g=c.createLinearGradient(-12,-26,12,14); g.addColorStop(0,o.c0||'#FFE9B0'); g.addColorStop(.5,o.c1||'#E4AC52'); g.addColorStop(1,o.c2||'#9A6624');
 c.fillStyle=g; c.beginPath(); c.ellipse(0,0,12.5,23,0,0,Math.PI*2); c.fill(); c.shadowBlur=0;
 c.strokeStyle='rgba(95,58,16,.5)'; c.lineWidth=1.4; c.stroke(); c.restore(); }
function stalk(c,x0,y0,x1,y1,col,w,bend){ c.save(); c.strokeStyle=col; c.lineWidth=w; c.lineCap='round'; c.beginPath(); c.moveTo(x0,y0);
 c.quadraticCurveTo(L(x0,x1,.5)+(bend||0),L(y0,y1,.5),x1,y1); c.stroke(); c.restore(); }
function leaf(c,x,y,ang,len,w,col){ c.save(); c.translate(x,y); c.rotate(ang); c.fillStyle=col; c.beginPath(); c.moveTo(0,0);
 c.quadraticCurveTo(len*.45,-w,len,-w*.2); c.quadraticCurveTo(len*.45,w*.3,0,0); c.fill(); c.restore(); }

// ---- vorgerenderte Ebenen ----
function blurInto(src,px){ const c=mk(src.width,src.height), g=c.getContext('2d'); g.filter=`blur(${px}px)`; g.drawImage(src,0,0); return c; }
const MAC=(()=>{ // Makro-Hintergrund: Gegenlicht, unscharfes Feld, Bokeh
 const c=mk(1400,2100), g=c.getContext('2d');
 const gr=g.createLinearGradient(0,0,0,2100); gr.addColorStop(0,'#1A1130'); gr.addColorStop(.3,'#4E2540'); gr.addColorStop(.48,'#B4502E'); gr.addColorStop(.6,'#F2A146'); gr.addColorStop(.68,'#E79A45'); gr.addColorStop(.78,'#6B4020'); gr.addColorStop(1,'#140C06');
 g.fillStyle=gr; g.fillRect(0,0,1400,2100);
 rg(g,820,1240,820,'rgba(255,210,130,.75)','rgba(255,150,60,0)'); rg(g,820,1240,170,'rgba(255,250,225,1)','rgba(255,232,170,0)');
 const tmp=mk(1400,2100), h=tmp.getContext('2d'); const r=rnd(7);
 for(let i=0;i<140;i++){ const x=r()*1500-50, y=1230+r()*560, s=.3+r()*.55; stalk(h,x,y+700,x+(r()-.5)*50,y,'rgba(55,32,12,.9)',6*s);
  ear(h,x,y,(r()-.5)*.35,s,{c0:'#7A5226',c1:'#563415',c2:'#2E1A0A',awn:'rgba(70,40,16,.7)',rach:'#3A2410'}); }
 g.drawImage(blurInto(tmp,16),0,0);
 for(let i=0;i<46;i++){ const x=r()*1400,y=350+r()*1300,rad=16+r()*64; const a=.06+r()*.2; g.filter=`blur(${1.5+r()*4}px)`;
  g.fillStyle=`rgba(255,${200+r()*45|0},${120+r()*70|0},${a})`; g.beginPath(); g.arc(x,y,rad,0,7); g.fill(); g.strokeStyle=`rgba(255,238,200,${a*1.3})`; g.lineWidth=2.5; g.stroke(); }
 g.filter='none'; return c; })();
const FG=(()=>{ // unscharfes Vordergrund-Gras
 const c=mk(1600,700), g=c.getContext('2d'); const r=rnd(11);
 for(let i=0;i<260;i++){ const x=r()*1600, h=150+r()*420, w=5+r()*9; g.fillStyle=`rgba(${20+r()*25|0},${12+r()*14|0},${6},.95)`;
  g.beginPath(); g.moveTo(x-w,700); g.quadraticCurveTo(x+(r()-.5)*90,700-h*.6,x+(r()-.5)*140,700-h); g.quadraticCurveTo(x+(r()-.5)*40,700-h*.5,x+w,700); g.fill(); }
 return blurInto(c,5); })();
function ridge(g,W,y0,amp,seed,fill,H){ const r=rnd(seed); const ph=[r()*6,r()*6,r()*6]; g.fillStyle=fill; g.beginPath(); g.moveTo(0,H);
 for(let x=0;x<=W;x+=12){ const y=y0-amp*(.55*Math.sin(x/260+ph[0])+.3*Math.sin(x/97+ph[1])+.15*Math.sin(x/41+ph[2]))-r()*amp*.04; g.lineTo(x,y);} g.lineTo(W,H); g.closePath(); g.fill(); }
const LAND=(()=>{ const W=2600,H=1920; const far=mk(W,H), mid=mk(W,H), near=mk(W,H);
 let g=far.getContext('2d'); let q=g.createLinearGradient(0,800,0,1150); q.addColorStop(0,'rgba(120,82,120,.95)'); q.addColorStop(1,'rgba(170,105,90,.95)'); ridge(g,W,930,150,3,q,H);
 g=mid.getContext('2d'); q=g.createLinearGradient(0,950,0,1250); q.addColorStop(0,'#B9783E'); q.addColorStop(1,'#7C4E25'); ridge(g,W,1060,70,5,q,H);
 g=near.getContext('2d'); q=g.createLinearGradient(0,1120,0,1920); q.addColorStop(0,'#5A3E1E'); q.addColorStop(.4,'#3A2612'); q.addColorStop(1,'#140C05'); ridge(g,W,1170,40,9,q,H);
 const r=rnd(21); for(let i=0;i<900;i++){ const x=r()*W, y=1150+r()*700, h=10+r()*34; g.strokeStyle=`rgba(${120+r()*80|0},${80+r()*50|0},${30},${.25+r()*.35})`; g.lineWidth=1.5; g.beginPath(); g.moveTo(x,y); g.lineTo(x+(r()-.5)*10,y-h); g.stroke(); }
 return {far:blurInto(far,3.5),mid:blurInto(mid,1.2),near}; })();
const SOIL=(()=>{ const c=mk(512,512), g=c.getContext('2d'); g.fillStyle='#4A2F1A'; g.fillRect(0,0,512,512); const r=rnd(33);
 for(let i=0;i<1400;i++){ g.fillStyle=`rgba(${r()<.5?20:120},${r()<.5?12:80},${r()<.5?6:45},${.15+r()*.3})`; g.beginPath(); g.ellipse(r()*512,r()*512,1+r()*4,1+r()*3,r()*3,0,7); g.fill(); }
 for(let i=0;i<40;i++){ g.fillStyle=`rgba(${110+r()*50|0},${95+r()*40|0},${80},.6)`; g.beginPath(); g.ellipse(r()*512,r()*512,4+r()*9,3+r()*6,r()*3,0,7); g.fill(); }
 return X.createPattern(c,'repeat'); })();
const GRAINS=[0,1,2,3].map(k=>{ const c=mk(256,256), g=c.getContext('2d'); const im=g.createImageData(256,256); const r=rnd(100+k);
 for(let i=0;i<im.data.length;i+=4){ const v=r()*255; im.data[i]=im.data[i+1]=im.data[i+2]=v; im.data[i+3]=255; } g.putImageData(im,0,0); return X.createPattern(c,'repeat'); });
const VIG=(()=>{ const c=mk(1080,1920), g=c.getContext('2d'); const q=g.createRadialGradient(540,880,380,540,960,1250); q.addColorStop(0,'rgba(0,0,0,0)'); q.addColorStop(1,'rgba(0,0,0,.62)'); g.fillStyle=q; g.fillRect(0,0,1080,1920); return c; })();
const DUST=(()=>{ const r=rnd(5), a=[]; for(let i=0;i<70;i++) a.push([r()*1080,r()*1920,1+r()*3.2,.2+r()*.6,r()*6,10+r()*30]); return a; })();
function dust(c,t,col,k){ for(const d of DUST){ const y=(d[1]-t*d[5]+1920*4)%1920, x=d[0]+18*Math.sin(t*.7+d[4]); c.fillStyle=col.replace('A',(d[3]*(k??1)*(.6+.4*Math.sin(t*2+d[4]))).toFixed(3)); c.beginPath(); c.arc(x,y,d[2],0,7); c.fill(); } }

// ---- Karte ----
const MX=lon=>(lon+180)*GEO.K*GEO.CX, MY=lat=>(90-lat)*GEO.K;
const PL=new Path2D(GEO.land), PC=new Path2D(GEO.cty), PK=new Path2D(GEO.lakes), PR=GEO.rivers.map(d=>new Path2D(d));
const CRES=[[34.8,31.0],[35.4,32.6],[36.0,34.4],[36.6,36.0],[37.6,36.9],[39.0,37.3],[40.6,37.4],[42.4,37.2],[44.0,36.2],[45.2,34.8],[46.2,33.4],[47.2,32.0]];
const PCR=new Path2D(); CRES.forEach((p,i)=>{ const x=MX(p[0]),y=MY(p[1]); if(i) PCR.lineTo(x,y); else PCR.moveTo(x,y); });
const KARA=[39.8,37.7];
function kf(arr,tt,logIdx){ const ks=arr.map(k=>({t:TS(k[0],k[1]),v:k.slice(2)})); if(tt<=ks[0].t) return ks[0].v;
 for(let i=0;i<ks.length-1;i++){ const a=ks[i],b=ks[i+1]; if(tt>=a.t&&tt<b.t){ const e=eio((tt-a.t)/Math.max(1e-6,b.t-a.t)); return a.v.map((x,j)=>j===logIdx?Math.exp(Math.log(x)+(Math.log(b.v[j])-Math.log(x))*e):x+(b.v[j]-x)*e); } }
 return ks[ks.length-1].v; }
const MAPK=[["s3",-0.15,38.6,33.4,11],["s3@Nahen",0,39.2,34.6,17],["s4",-0.3,39.6,36.9,24],["s4",0.4,KARA[0],KARA[1],170]];

// ---- Personen-Silhouette ----
function person(c,x,y,h,bend,arm,basket,dir){ c.save(); c.translate(x,y); c.scale(dir||1,1); const u=h/300; c.scale(u,u);
 c.fillStyle='#1E130B'; c.strokeStyle='#1E130B'; c.lineCap='round';
 c.lineWidth=16; c.beginPath(); c.moveTo(-10,0); c.lineTo(-6,-120); c.moveTo(14,0); c.lineTo(6,-120); c.stroke();
 c.save(); c.translate(0,-125); c.rotate(bend);
 c.beginPath(); c.moveTo(-26,0); c.lineTo(26,0); c.lineTo(20,-110); c.lineTo(-20,-110); c.closePath(); c.fill();
 c.beginPath(); c.arc(4,-138,24,0,7); c.fill();
 c.lineWidth=12; c.beginPath(); c.moveTo(14,-96); c.quadraticCurveTo(46,-60+arm*20,58+arm*10,-10+arm*30); c.stroke();
 c.strokeStyle='rgba(255,170,90,.55)'; c.lineWidth=3; c.beginPath(); c.arc(4,-138,24,-1.2,0.6); c.stroke();
 c.restore();
 if(basket){ c.fillStyle='#3A2412'; c.beginPath(); c.ellipse(-34,-120,26,18,0,0,7); c.fill(); }
 c.restore(); }

// ---- Korb ----
function basket(c,x,y,s){ c.save(); c.translate(x,y); c.scale(s,s);
 const g=c.createLinearGradient(-150,0,150,0); g.addColorStop(0,'#5A3616'); g.addColorStop(.45,'#A06A33'); g.addColorStop(1,'#4A2C12');
 c.fillStyle=g; c.beginPath(); c.moveTo(-160,0); c.lineTo(160,0); c.lineTo(120,210); c.quadraticCurveTo(0,240,-120,210); c.closePath(); c.fill();
 c.strokeStyle='rgba(40,22,8,.55)'; c.lineWidth=3; for(let k=1;k<7;k++){ const yy=k*30; c.beginPath(); c.moveTo(-160+k*6,yy); c.quadraticCurveTo(0,yy+14,160-k*6,yy); c.stroke(); }
 for(let k=-5;k<=5;k++){ c.beginPath(); c.moveTo(k*30,4); c.lineTo(k*23,220); c.stroke(); }
 c.fillStyle='#7A4C22'; c.beginPath(); c.ellipse(0,0,165,26,0,0,7); c.fill(); c.strokeStyle='rgba(255,200,130,.5)'; c.lineWidth=3; c.beginPath(); c.ellipse(0,0,165,26,0,Math.PI*1.05,Math.PI*1.95); c.stroke();
 c.restore(); }
function basketBack(c,x,y,s){ c.save(); c.translate(x,y); c.scale(s,s); c.fillStyle='#2E1A0A'; c.beginPath(); c.ellipse(0,0,160,24,0,0,7); c.fill(); c.restore(); }

// ---- Haus / Stadt ----
function house(c,x,y,s,a){ if(a<=0) return; c.save(); c.translate(x,y); c.scale(s,s*(0.2+0.8*a)); c.globalAlpha*=Math.min(1,a*2);
 c.fillStyle='#8E6238'; c.beginPath(); c.moveTo(30,0); c.lineTo(52,-10); c.lineTo(52,-50); c.lineTo(30,-40); c.closePath(); c.fill();
 c.fillStyle='#C9925A'; c.fillRect(-30,-40,60,40); c.fillStyle='#6E4A28'; c.fillRect(-34,-46,64,7); c.beginPath(); c.moveTo(30,-46); c.lineTo(54,-56); c.lineTo(54,-50); c.lineTo(30,-40); c.fill();
 c.fillStyle='#2A1A0E'; c.fillRect(-8,-24,14,24); c.restore(); }
function city(c,x,y,s,a,lights){ if(a<=0) return; c.save(); c.translate(x,y); c.scale(s,s*(0.3+0.7*a)); c.globalAlpha*=Math.min(1,a*1.6);
 c.fillStyle='#4A3048'; c.fillRect(-220,-50,440,50); for(let k=-220;k<220;k+=22) c.fillRect(k,-62,12,12);
 c.fillRect(-240,-90,40,90); c.fillRect(200,-90,40,90);
 c.fillStyle='#55385A'; c.fillRect(-90,-110,180,60); c.fillRect(-60,-150,120,40); c.fillRect(-35,-180,70,30);
 c.fillStyle=`rgba(255,200,110,${lights})`; const r=rnd(9); for(let i=0;i<26;i++){ c.fillRect(-200+r()*400,-40+r()*28,5,5); } c.fillRect(-6,-170,12,10);
 c.restore(); }

// ---- Brötchen ----
function roll(c,x,y,s){ c.save(); c.translate(x,y); c.scale(s,s);
 c.save(); c.filter='blur(14px)'; c.fillStyle='rgba(0,0,0,.6)'; c.beginPath(); c.ellipse(10,120,250,40,0,0,7); c.fill(); c.restore();
 const g=c.createRadialGradient(-80,-80,10,0,0,280); g.addColorStop(0,'#F7D08A'); g.addColorStop(.45,'#D98F3E'); g.addColorStop(.8,'#9C5A20'); g.addColorStop(1,'#6A3A12');
 c.fillStyle=g; c.beginPath(); c.moveTo(-240,90); c.bezierCurveTo(-260,-60,-140,-170,0,-170); c.bezierCurveTo(140,-170,260,-60,240,90); c.quadraticCurveTo(0,140,-240,90); c.fill();
 const g2=c.createLinearGradient(0,-150,0,-40); g2.addColorStop(0,'#FBE6B8'); g2.addColorStop(1,'#E2B26A');
 c.fillStyle=g2; c.beginPath(); c.moveTo(-150,-70); c.quadraticCurveTo(0,-175,150,-70); c.quadraticCurveTo(0,-110,-150,-70); c.fill();
 const r=rnd(4); c.fillStyle='rgba(255,255,255,.55)'; for(let i=0;i<70;i++){ c.beginPath(); c.arc(-180+r()*360,-150+r()*170,1+r()*2.2,0,7); c.fill(); }
 c.strokeStyle='rgba(255,240,210,.35)'; c.lineWidth=6; c.beginPath(); c.moveTo(-210,0); c.bezierCurveTo(-200,-100,-120,-150,-30,-158); c.stroke();
 c.restore(); }

// ---- Komposition ----
function comp(fn,t,a,sc,ax,ay,blur,dx){
 if(a<=0.002) return; sc=sc??1; blur=blur||0; dx=dx||0;
 if(a>=0.999&&blur<0.05&&Math.abs(sc-1)<1e-4&&Math.abs(dx)<0.5){ X.save(); fn(X,t); X.restore(); return; }
 O.setTransform(1,0,0,1,0,0); O.globalAlpha=1; O.filter='none'; O.clearRect(0,0,1080,1920); O.save(); fn(O,t); O.restore();
 X.save(); X.globalAlpha=a; if(blur>0.05) X.filter=`blur(${blur.toFixed(2)}px)`;
 X.translate(ax+dx,ay); X.scale(sc,sc); X.translate(-ax,-ay); X.drawImage(off,0,0); X.restore(); }

// ===================== SHOTS =====================
// A: Makro-Hook – eine goldene Ähre im Gegenlicht
function shotA(c,t){
 const z=1+0.05*Math.min(t,6)/6;
 c.save(); c.translate(540,960); c.scale(z,z); c.translate(-540,-960);
 c.drawImage(MAC,-160-6*t,-120);
 // unscharfe Vordergrund-Ähren (Tiefe)
 c.save(); c.filter='blur(12px)'; ear(c,90,1500,0.18+0.02*Math.sin(t*1.1),2.2,{c0:'#6A4420',c1:'#4A2C10',c2:'#26150A',awn:'rgba(60,35,15,.7)'}); stalk(c,120,2000,90,1500,'#2A180A',14); c.restore();
 const sw=0.025*Math.sin(t*1.3);
 stalk(c,700,1950,612,1060,'#B9852F',10,40);
 leaf(c,660,1500,-2.3+sw,260,22,'#8C6A2A');
 ear(c,612,1060,-0.06+sw,1.75,{glow:'rgba(255,200,110,.85)',glowR:26,rim:'rgba(255,245,215,.85)'});
 c.restore();
 dust(c,t,'rgba(255,230,170,A)',1);
}
// B: Karte Naher Osten
function shotB(c,t){
 const g=c.createRadialGradient(540,760,100,540,900,1300); g.addColorStop(0,'#16314F'); g.addColorStop(1,'#060E1A'); c.fillStyle=g; c.fillRect(0,0,1080,1920);
 const k=kf(MAPK,t,2); const z=k[2], cx=MX(k[0]), cy=MY(k[1]);
 c.save(); c.setTransform(z,0,0,z,540-cx*z,760-cy*z);
 c.shadowColor='rgba(0,0,0,.65)'; c.shadowBlur=40; c.shadowOffsetY=10;
 const lg=c.createLinearGradient(MX(30),MY(42),MX(52),MY(24)); lg.addColorStop(0,'#D8B47C'); lg.addColorStop(.5,'#C39456'); lg.addColorStop(1,'#A8743C');
 c.fillStyle=lg; c.fill(PL); c.shadowColor='transparent'; c.shadowBlur=0; c.shadowOffsetY=0;
 c.save(); c.clip(PL);
 const cr=pr(t,TS('s3@Nahen',-0.35),0.7);
 if(cr>0){ c.globalAlpha=cr; c.filter=`blur(${Math.max(4,0.9*z)}px)`; c.strokeStyle='rgba(110,225,90,.95)'; c.lineWidth=3.4; c.lineJoin='round'; c.lineCap='round'; c.stroke(PCR);
  c.filter='none'; c.strokeStyle='rgba(170,245,140,.6)'; c.lineWidth=1.3; c.stroke(PCR); c.globalAlpha=1; }
 const hl=c.createRadialGradient(MX(38),MY(36),0,MX(38),MY(36),40); hl.addColorStop(0,'rgba(255,240,200,.28)'); hl.addColorStop(1,'rgba(255,240,200,0)'); c.fillStyle=hl; c.fillRect(MX(10),MY(60),MX(70)-MX(10),MY(0)-MY(60));
 c.restore();
 c.strokeStyle='rgba(255,255,255,.22)'; c.lineWidth=1.1/z; c.setLineDash([4/z,4/z]); c.stroke(PC); c.setLineDash([]);
 c.fillStyle='#2B6EA8'; c.fill(PK);
 c.shadowColor='rgba(110,200,255,.9)'; c.shadowBlur=10; c.strokeStyle='#7CCBFF'; c.lineWidth=2.2/z; c.lineJoin='round'; for(const p of PR) c.stroke(p); c.shadowBlur=0;
 c.restore();
 const P=(lon,lat)=>[540+(MX(lon)-cx)*z,760+(MY(lat)-cy)*z];
 c.font='700 22px JBM'; c.fillStyle='rgba(190,220,255,.55)'; c.textAlign='center'; const mm=P(31.5,33.6); if(z<20) c.fillText('MITTELMEER',mm[0],mm[1]);
 const eu=P(40.6,35.4); c.fillStyle='rgba(150,215,255,.75)'; if(z<40&&z>14) c.fillText('EUPHRAT',eu[0],eu[1]);
 // Hauptdarsteller als leuchtendes Korn am Karacadağ
 const pa=pr(t,TS('s3@Nahen',0.25),0.4); if(pa>0){ const p=P(KARA[0],KARA[1]); c.globalAlpha=pa;
  rg(c,p[0],p[1],70+10*Math.sin(t*4),'rgba(255,214,120,.55)','rgba(255,214,120,0)'); grain(c,p[0],p[1],0.4,1.1,{glow:'rgba(255,220,140,1)',glowR:24});
  c.strokeStyle=`rgba(255,230,170,${.8*(1-((t*1.2)%1))})`; c.lineWidth=3; c.beginPath(); c.arc(p[0],p[1],20+60*((t*1.2)%1),0,7); c.stroke(); c.globalAlpha=1; }
}
// C: Landschaft – Sammler und wilder Weizen
const TUFT=(()=>{ const r=rnd(44), a=[]; for(let i=0;i<120;i++) a.push([r()*1400-160, 1150+r()*200, .32+r()*.32, r()*6]); a.sort((p,q)=>p[1]-q[1]); return a; })();
function landSky(c,dusk){ const g=c.createLinearGradient(0,0,0,1200); g.addColorStop(0,mixc('#2A1A3E','#0E1430',dusk)); g.addColorStop(.45,mixc('#A8503A','#3A2E5A',dusk)); g.addColorStop(.8,mixc('#F4B060','#B86A4A',dusk)); g.addColorStop(1,mixc('#FFD58A','#E09A60',dusk));
 c.fillStyle=g; c.fillRect(0,0,1080,1920); }
function shotC(c,t){
 const t0=TS('s4',-0.3), u=t-t0; const pan=u*26;
 landSky(c,0); rg(c,760-pan*.1,960,520,'rgba(255,220,150,.75)','rgba(255,180,90,0)'); rg(c,760-pan*.1,960,90,'rgba(255,250,230,1)','rgba(255,240,200,0)');
 c.drawImage(LAND.far,-300-pan*.25,0); c.drawImage(LAND.mid,-300-pan*.5,0); c.drawImage(LAND.near,-300-pan,0);
 for(const p of TUFT){ const x=p[0]-pan*0.9, y=p[1], s=p[2]; const sw=0.05*Math.sin(t*1.6+p[3]);
  stalk(c,x,y,x+sw*200,y-210*s,'#C79A48',4*s+1); ear(c,x+sw*200,y-210*s,sw,s,{rim:'rgba(255,240,200,.7)'}); }
 const bendA=0.75+0.18*Math.sin(t*2.4), bendB=0.55+0.2*Math.sin(t*2.0+1);
 person(c,420-pan,1250,330,bendA,Math.sin(t*2.4),true,1); person(c,760-pan,1215,300,bendB,Math.sin(t*2+1),true,-1);
 dust(c,t,'rgba(255,225,160,A)',.8);
}
// D: Makro – Ähre zerfällt / Körner bleiben hängen / Korb
const N=14, SPD=(()=>{ const r=rnd(77), a=[]; for(let i=0;i<N;i++) a.push([(r()-.5)*260, (r()-.5)*12, 0.3+r()*0.5, r()]); return a; })();
const E1={x:400,y:1000,s:1.85}, E2={x:880,y:940,s:1.75}, GROUND=1130;
function shotD(c,t){
 const tz=TS('s5@zerfällt',-0.12), tk=TS('s6@kaum',0.1);
 const pan=-290*eio(pr(t,TS('s7',-0.15),1.0));
 const f12=eio(pr(t,TS('s7',-0.15),0.9)); // Fokus-Zug Ähre1 -> Ähre2
 c.drawImage(MAC,-200+pan*0.35,-150);
 const sw=0.03*Math.sin(t*1.4), wind=pr(t,TS('s7@hängen',-0.25),0.2)*(1-pr(t,TS('s7@hängen',0.6),0.4));
 const shake=wind*0.12*Math.sin(t*38);
 c.save(); c.translate(pan,0);
 // Ähre 2 (Mutante, lila leuchtend), anfangs unscharf im Hintergrund
 const tc=TS('s8@Ernten',0.15), tl=TS('s8@landen',0.25); const fly=eio(pr(t,tc,tl-tc));
 const BX=E2.x, BY=985; const basketIn=eio(pr(t,TS('s8@Ernten',-0.35),0.5)); const by=L(1700,BY,basketIn);
 c.restore(); { const gg=c.createLinearGradient(0,GROUND-40,0,GROUND+200); gg.addColorStop(0,'rgba(40,24,10,0)'); gg.addColorStop(.25,'rgba(52,32,14,.95)'); gg.addColorStop(1,'#120A04'); c.fillStyle=gg; c.fillRect(0,GROUND-40,1080,900); const r=rnd(61); for(let k=0;k<160;k++){ c.fillStyle=`rgba(${150+r()*60|0},${100+r()*40|0},${50},${.25+r()*.3})`; c.beginPath(); c.ellipse((r()*1600-200+pan*1.0+1600)%1600-260,GROUND-6+r()*150,1.5+r()*4,1+r()*2.5,0,0,7); c.fill(); } } c.save(); c.translate(pan,0);
 if(basketIn>0) basketBack(c,BX,by,1.05);
 const ex=L(E2.x,BX+20,fly), ey=L(E2.y,by+60,fly)-Math.sin(Math.PI*fly)*200, ea=L(sw*.8+shake,0.32,fly);
 c.save(); const b2=(1-f12)*9; if(b2>0.1) c.filter=`blur(${b2}px)`;
 if(fly<=0) stalk(c,E2.x+40,1950,E2.x,E2.y,'#B9852F',9,-30);
 else if(fly<0.45){ c.save(); c.globalAlpha=1-fly/0.45; c.translate(ex,ey); c.rotate(ea); stalk(c,0,0,30,420,'#B9852F',9,-20); c.restore(); }
 const glowA=0.35+0.65*pr(t,TS('s7@manchen',-0.2),0.5);
 ear(c,ex,ey,ea,L(E2.s,1.0,fly),{glow:`rgba(183,155,255,${glowA})`,glowR:30,rim:'rgba(205,185,255,.95)',st:i=>({rot:shake*(i%2?1:-1)*2})});
 c.restore();
 // weitere geerntete Ähren fallen in den Korb
 const extra=[[-110,0,'f'],[90,0.12,'f'],[-30,0.24,'f'],[150,0.36,'w'],[-160,0.48,'f'],[40,0.6,'w']];
 extra.forEach(([dx,dd,kind],k)=>{ const t1=TS('s8@besonders',-0.2+dd); const p=eio(pr(t,t1,0.55)); if(p<=0) return;
  const x=BX+dx, y=L(-200,by+40,p); const a=(k%2?-1:1)*(0.25+0.1*k);
  if(kind==='f') ear(c,x,y,a,1.0,{glow:'rgba(183,155,255,.9)',glowR:22,rim:'rgba(205,185,255,.95)'}); else ear(c,x,y,a,1.0,{bald:true,rach:'#8A6A3A'}); });
 // Kornhaufen im Korb
 const pile=pr(t,TS('s8@viele',-0.1),0.9); if(pile>0){ const r=rnd(55); for(let i=0;i<Math.floor(46*pile);i++){ const gx=BX+(r()-.5)*240, gy=by-6-r()*30; const lila=r()<0.62;
   grain(c,gx,gy,r()*3,0.55,lila?{glow:'rgba(183,155,255,.95)',glowR:12}:{}); } }
 if(basketIn>0) basket(c,BX,by,1.05);
 // Ähre 1 (wild): zerfällt
 c.save(); const b1=f12*10; if(b1>0.1) c.filter=`blur(${b1}px)`;
 stalk(c,E1.x+40,1950,E1.x,E1.y,'#B9852F',9,30);
 const rad=(i)=>{ const td=tz+(N-1-i)*0.055; return td; };
 ear(c,E1.x,E1.y,sw+shake*.5,E1.s,{rim:'rgba(255,240,205,.8)',glow:'rgba(255,200,110,.5)',glowR:16,st:i=>({gone:t>=rad(i)})});
 // fallende Körner (Weltkoordinaten)
 for(let i=0;i<N;i++){ const td=rad(i); if(t<td) continue; const q=SPD[i]; const side=i%2?1:-1;
  const x0=E1.x+side*10*E1.s+ (sw)*(-(i*22+20))*E1.s, y0=E1.y-(i*22+20)*E1.s; const dt=t-td;
  const yG=GROUND+q[1]; const tf=Math.sqrt(2*(yG-y0)/2600); let x,y,rot;
  if(dt<tf){ x=x0+q[0]*dt; y=y0+1300*dt*dt; rot=side*0.42+(q[2]*14)*dt*side; }
  else { const d2=dt-tf; x=x0+q[0]*tf+q[0]*0.25*(1-Math.exp(-d2*4)); y=yG-Math.abs(Math.sin(d2*14))*22*Math.exp(-d2*6); rot=side*0.42+(q[2]*14)*tf*side+1.2*side*(1-Math.exp(-d2*3)); }
  const fa=1-pr(t,tk+q[3]*0.5,0.45); if(fa<=0) continue;
  c.globalAlpha=fa; grain(c,x,y,rot,E1.s*0.95,{}); c.globalAlpha=1; }
 c.restore();
 // Hand greift ins Leere (s6)
 const hr=eio(pr(t,TS('s6@kaum',-0.35),0.45))*(1-pr(t,TS('s7',-0.2),0.3)); if(hr>0){ const hx=L(-120,300,hr), hy=L(900,1080,hr);
  c.save(); c.strokeStyle='#2A1A10'; c.lineCap='round'; c.lineWidth=46; c.beginPath(); c.moveTo(-200,820); c.quadraticCurveTo(hx-140,hy-140,hx,hy); c.stroke();
  c.lineWidth=13; for(let k=0;k<4;k++){ c.beginPath(); c.moveTo(hx+6,hy-10+k*9); c.lineTo(hx+52-k*4+10*Math.sin(t*8+k),hy+16+k*10); c.stroke(); }
  c.strokeStyle='rgba(255,170,90,.45)'; c.lineWidth=4; c.beginPath(); c.moveTo(-200,800); c.quadraticCurveTo(hx-150,hy-165,hx-4,hy-24); c.stroke(); c.restore(); }
 c.restore();
 // Vordergrund-Gras
 c.drawImage(FG,-200+pan*1.25,1290);
 dust(c,t,'rgba(255,225,165,A)',.7);
}
// E: Boden-Querschnitt – Aussaat, Zeitraffer, Feld wird zur Regel
const SEEDX=[250,390,530,670,810];
const FIELD=(()=>{ const r=rnd(91), a=[]; for(let x=-900;x<=1980;x+=46){ if(x>190&&x<870) continue; a.push([x+(r()-.5)*14, r(), r()*6, .85+r()*.3]); } return a; })();
function dayPhase(t){ const a=TS('s10@wächst',-0.1), b=TS('s11',-0.05), c2=TS('s12',0.2);
 if(t<a) return 0.22; if(t<b) return 0.22+1.0*eio(pr(t,a,b-a)); return 1.22+1.5*pr(t,b,c2-b); }
function shotE(c,t){
 const zt=eio(pr(t,TS('s11',-0.1),TS('s11@Regel',0.3)-TS('s11',-0.1))); const z=L(1.3,0.5,zt);
 const ph=dayPhase(t); const el=Math.sin(ph*2*Math.PI); const day=sm(el*2.2+0.45);
 const g=c.createLinearGradient(0,0,0,1000); g.addColorStop(0,mixc('#070B1E','#3E78B8',day)); g.addColorStop(.7,mixc('#1A1E3E','#F2B571',day)); g.addColorStop(1,mixc('#2A2440','#FFD9A0',day));
 c.fillStyle=g; c.fillRect(0,0,1080,1920);
 if(day<0.6){ const r=rnd(3); c.fillStyle=`rgba(255,255,255,${0.8*(1-day/0.6)})`; for(let i=0;i<120;i++){ c.fillRect(r()*1080,r()*900,2,2);} }
 const sa=ph*2*Math.PI; const sx=540-560*Math.cos(sa), sy=980-700*Math.sin(sa);
 if(el>-0.15){ rg(c,sx,sy,260,'rgba(255,225,160,.55)','rgba(255,200,120,0)'); rg(c,sx,sy,52,'rgba(255,250,230,1)','rgba(255,240,200,0)'); }
 c.save(); c.translate(540,1000); c.scale(z,z); c.translate(-540,-1000);
 // Boden
 c.fillStyle=SOIL; c.fillRect(-1800,1000,4800,2600);
 const sg=c.createLinearGradient(0,990,0,1060); sg.addColorStop(0,'#2A1A0C'); sg.addColorStop(1,'rgba(42,26,12,0)'); c.fillStyle=sg; c.fillRect(-1800,990,4800,70);
 c.fillStyle='#3B2614'; c.beginPath(); c.moveTo(-1800,1000); for(let x=-1800;x<=3000;x+=30) c.lineTo(x,996-6*Math.sin(x/37)); c.lineTo(3000,1012); c.lineTo(-1800,1012); c.fill();
 c.fillStyle=`rgba(0,0,0,${0.55*(1-day)})`; c.fillRect(-1800,1000,4800,2600);
 // Feld (Rauszoom)
 const frac=0.25+0.75*eio(pr(t,TS('s11',0.15),TS('s11@Regel',0.2)-TS('s11',0.15)));
 const barf=document.getElementById('barf'); if(barf){ barf.style.width=(frac*100).toFixed(1)+'%'; document.getElementById('barn').textContent=Math.round(frac*100)+' %'; }
 FIELD.forEach((p,k)=>{ const gg=eio(pr(t,TS('s11',-0.15)+Math.abs(p[0]-540)/1500*0.55,0.6)); if(gg<=0) return; const fest=sm((frac-p[1])/0.08+0.5);
  const H=330*p[3]*gg, sw=0.04*Math.sin(t*1.5+p[2]); stalk(c,p[0],1000,p[0]+sw*H,1000-H,'#B98A3A',7,10);
  if(gg>0.55){ const es=0.8*p[3]*sm((gg-0.55)/0.45);
   if(fest>0.02){ c.globalAlpha=fest; ear(c,p[0]+sw*H,1000-H,sw,es,{glow:'rgba(183,155,255,.8)',glowR:18,rim:'rgba(205,185,255,.9)'}); c.globalAlpha=1; }
   if(fest<0.98){ c.globalAlpha=1-fest; ear(c,p[0]+sw*H,1000-H,sw,es,{bald:true,rach:'#9A7A48'}); c.globalAlpha=1; } } });
 // Arm wirft Körner
 const ta=TS('s9@Man',-0.35), tr=TS('s9@sät',0.05);
 const arm=pr(t,ta,0.35)*(1-pr(t,TS('s9@aus',0.25),0.4)); if(arm>0){ const sw2=eio(pr(t,tr-0.3,0.4)); const ang=L(-0.35,0.12,sw2);
  c.save(); c.globalAlpha=arm; c.translate(1320,120); c.rotate(ang);
  c.fillStyle='#2A1A10'; c.beginPath(); c.moveTo(-30,-40); c.lineTo(40,30); c.lineTo(-440,420); c.lineTo(-500,360); c.closePath(); c.fill();
  c.beginPath(); c.ellipse(-490,410,56,42,0.75,0,7); c.fill();
  c.lineCap='round'; c.strokeStyle='#2A1A10'; c.lineWidth=17; const op=sw2;
  for(let k=0;k<4;k++){ const a0=0.9+k*0.28-op*0.5; c.beginPath(); c.moveTo(-500,420); c.lineTo(-500+Math.cos(a0+1.6)*80,420+Math.sin(a0+1.6)*80); c.stroke(); }
  c.strokeStyle='rgba(255,190,120,.5)'; c.lineWidth=5; c.beginPath(); c.moveTo(-28,-36); c.lineTo(-496,356); c.stroke(); c.restore(); }
 // Körner fliegen in den Boden, keimen
 SEEDX.forEach((sx2,i)=>{ const t1=tr+i*0.07, t2=t1+0.55; if(t<t1) return; const p=pr(t,t1,t2-t1);
  const hx0=1180-320*Math.cos(0.55)+0, hy0=360+182;
  let x=L(830,sx2,p), y=L(520,1000,p)-Math.sin(Math.PI*p)*260; const sink=eio(pr(t,t2,0.35)); y+=sink*42;
  const gg=eio(pr(t,TS('s10@wächst',-0.15)+i*0.06,1.4));
  if(gg>0){ // Wurzeln
   c.save(); c.strokeStyle='rgba(235,220,190,.75)'; c.lineWidth=2.4; c.lineCap='round'; for(let k=-2;k<=2;k++){ c.beginPath(); c.moveTo(sx2,1042); c.quadraticCurveTo(sx2+k*18,1042+60*gg,sx2+k*30*gg,1042+120*gg*(1-Math.abs(k)*.15)); c.stroke(); } c.restore();
   const H=330*gg, sw=0.04*Math.sin(t*1.5+i); stalk(c,sx2,1040,sx2+sw*H,1000-H,'#7FB84A',8*Math.min(1,gg*2)+1,8);
   if(gg>0.25) { leaf(c,sx2,1000-H*0.35,-0.9-0.2*Math.sin(i),110*gg,14,'#6FA640'); leaf(c,sx2,1000-H*0.55,-2.3,90*gg,12,'#7DB44C'); }
   if(gg>0.55){ const es=sm((gg-0.55)/0.45)*0.8; ear(c,sx2+sw*H,1000-H,sw,es,{glow:'rgba(183,155,255,.85)',glowR:20,rim:'rgba(205,185,255,.95)',c0:mixc('#C8E89A','#FFE9B0',gg),c1:mixc('#8DC25A','#E4AC52',sm((gg-.6)/.4))}); }
  }
  grain(c,x,y,p*9+i,0.85,{glow:'rgba(183,155,255,.95)',glowR:14});
  if(sink>0&&sink<1){ c.fillStyle=`rgba(120,80,45,${0.5*(1-sink)})`; for(let k=0;k<5;k++){ c.beginPath(); c.arc(sx2+(k-2)*10*(1+sink*2),998-sink*18*Math.sin(k+1),4,0,7); c.fill(); } }
 });
 c.restore();
}
// F: Landschaft mit Feldern, Dorf und später Stadt – Dämmerung
const HOUSES=[[600,1150,1.15,'s13@bleibt',0],[690,1162,1.0,'s13@bleibt',0.12],[525,1170,0.95,'s13@bleibt',0.24],
 [760,1140,0.9,'s14@größer',-0.2],[450,1150,0.85,'s14@größer',-0.08],[820,1170,1.05,'s14@größer',0.04],[640,1190,1.1,'s14@größer',0.16],[380,1180,0.9,'s14@größer',0.28],[880,1150,0.8,'s14@größer',0.4]];
const FIELDS=[[210,1110,220,60,'s12',-0.3],[330,1185,260,70,'s12',-0.3],[60,1170,200,64,'s13@Feld',0],[880,1215,240,70,'s14@Dörfer',0],[150,1235,220,60,'s14@Dörfer',0.15],[960,1120,180,50,'s14@größer',0]];
function shotF(c,t){
 const dusk=sm(pr(t,TS('s14@später',-0.3),1.3)); const t0=TS('s12',-0.1); const u=t-t0; const pan=u*14;
 const zz=1+0.06*pr(t,t0,5);
 landSky(c,dusk);
 const sx=820-pan*.1, sy=L(980,1080,dusk); rg(c,sx,sy,560,`rgba(255,215,140,${.75*(1-dusk*.6)})`,'rgba(255,180,90,0)'); rg(c,sx,sy,80,`rgba(255,250,230,${1-dusk*.7})`,'rgba(255,240,200,0)');
 if(dusk>0.2){ const r=rnd(8); c.fillStyle=`rgba(255,255,255,${.6*(dusk-.2)})`; for(let i=0;i<70;i++) c.fillRect(r()*1080,100+r()*600,2,2); }
 c.save(); c.translate(540,1010); c.scale(zz*1.45,zz*1.45); c.translate(-540,-1120);
 c.drawImage(LAND.far,-500-pan*.25,0);
 city(c,690-pan*.25,968,0.7,eio(pr(t,TS('s14@Städte',-0.35),0.6)),pr(t,TS('s14@Städte',0),0.8)*(0.4+0.6*dusk));
 c.drawImage(LAND.mid,-500-pan*.5,0);
 // Felder
 for(const f of FIELDS){ const a=eio(pr(t,TS(f[4],f[5]),0.5)); if(a<=0) continue; const x=f[0]-pan*.7, y=f[1], w=f[2]*a, h=f[3];
  c.save(); c.globalAlpha=Math.min(1,a*1.5); const g=c.createLinearGradient(0,y-h,0,y); g.addColorStop(0,'#F2C66A'); g.addColorStop(1,'#B98432');
  c.fillStyle=g; c.beginPath(); c.moveTo(x,y); c.lineTo(x+w,y); c.lineTo(x+w*0.88+30,y-h); c.lineTo(x+30,y-h); c.closePath(); c.fill();
  c.strokeStyle='rgba(120,80,30,.45)'; c.lineWidth=2; for(let k=1;k<6;k++){ const yy=y-h*k/6; c.beginPath(); c.moveTo(x+30*k/6,yy); c.lineTo(x+w-(w*0.12-30)*k/6,yy); c.stroke(); }
  c.fillStyle=`rgba(40,30,80,${.45*dusk})`; c.fill(); c.restore(); }
 // Häuser
 const hs=HOUSES.slice().sort((p,q)=>p[1]-q[1]);
 for(const h of hs){ const a=eio(pr(t,TS(h[3],h[4]),0.4)); house(c,h[0]-pan*.7,h[1],h[2],a);
  if(a>0&&dusk>0.3){ c.fillStyle=`rgba(255,190,100,${(dusk-.3)*1.2})`; c.fillRect(h[0]-pan*.7-1*h[2],h[1]-22*h[2],8*h[2],10*h[2]); } }
 c.drawImage(LAND.near,-500-pan,90);
 person(c,300-pan,1300,210,0.1,0.2*Math.sin(t*2),false,1);
 c.restore();
 c.fillStyle=`rgba(20,16,50,${.35*dusk})`; c.fillRect(0,0,1080,1920);
}
// G: 1/5 aller Kalorien
function shotG(c,t){
 const g=c.createRadialGradient(540,780,40,540,900,1200); g.addColorStop(0,'#4A2E14'); g.addColorStop(.6,'#1C1108'); g.addColorStop(1,'#070402'); c.fillStyle=g; c.fillRect(0,0,1080,1920);
 c.save(); c.globalAlpha=.55; c.drawImage(MAC,-160,-120); c.restore(); c.fillStyle='rgba(10,6,3,.55)'; c.fillRect(0,0,1080,1920);
 const cx=540, cy=760, R=372; const a0=pr(t,TS('s16',-0.15),0.4);
 c.globalAlpha=a0; c.strokeStyle='rgba(255,255,255,.13)'; c.lineWidth=46; c.beginPath(); c.arc(cx,cy,R,0,7); c.stroke();
 const sw=eio(pr(t,TS('s16@Fünftel',-0.15),0.9)); if(sw>0){ const gg=c.createLinearGradient(cx,cy-R,cx+R,cy); gg.addColorStop(0,'#FFE3A0'); gg.addColorStop(1,'#E0A040');
  c.shadowColor='rgba(255,200,110,.9)'; c.shadowBlur=30; c.strokeStyle=gg; c.lineCap='round'; c.beginPath(); c.arc(cx,cy,R,-Math.PI/2,-Math.PI/2+2*Math.PI*0.2*sw); c.stroke(); c.shadowBlur=0;
  const ea=-Math.PI/2+2*Math.PI*0.1*sw; ear(c,cx+(R+90)*Math.cos(ea),cy+(R+90)*Math.sin(ea)+40,ea+Math.PI/2,0.75,{glow:'rgba(255,200,110,.8)',glowR:18}); }
 c.globalAlpha=1; dust(c,t,'rgba(255,215,150,A)',1);
}
// H: Frühstücksbrötchen
function shotH(c,t){
 const u=t-TS('s17',-0.2); const z=1+0.05*pr(u,0,3.5);
 const g=c.createLinearGradient(0,0,0,1100); g.addColorStop(0,'#2A1A10'); g.addColorStop(1,'#6A4428'); c.fillStyle=g; c.fillRect(0,0,1080,1920);
 c.save(); c.filter='blur(30px)'; c.fillStyle='rgba(255,236,200,.13)'; for(let k=0;k<4;k++){ c.beginPath(); c.moveTo(-100+k*170,0); c.lineTo(80+k*170,0); c.lineTo(700+k*170,1100); c.lineTo(520+k*170,1100); c.fill(); } c.restore();
 rg(c,150,180,520,'rgba(255,240,210,.25)','rgba(255,240,210,0)');
 c.save(); c.translate(540,960); c.scale(z,z); c.translate(-540,-960);
 const tg=c.createLinearGradient(0,1020,0,1920); tg.addColorStop(0,'#7A4E2C'); tg.addColorStop(1,'#2E1A0C'); c.fillStyle=tg; c.fillRect(-100,1020,1300,1000);
 c.strokeStyle='rgba(30,16,6,.5)'; c.lineWidth=3; for(let k=0;k<5;k++){ const y=1080+k*110; c.beginPath(); c.moveTo(-100,y); c.lineTo(1300,y+8); c.stroke(); }
 const r=rnd(17); c.strokeStyle='rgba(255,210,160,.07)'; c.lineWidth=2; for(let k=0;k<40;k++){ const y=1030+r()*800; c.beginPath(); c.moveTo(-100,y); c.bezierCurveTo(300,y+r()*16,700,y-r()*16,1300,y); c.stroke(); }
 roll(c,620,1000,1.0);
 ear(c,250,1110,-0.55,0.95,{glow:'rgba(183,155,255,.85)',glowR:20,rim:'rgba(205,185,255,.95)'}); stalk(c,250,1110,330,1240,'#B9852F',7,0);
 const lp=eio(pr(t,TS('s17@stammt',-0.1),0.9)); if(lp>0){ c.save(); c.setLineDash([10,14]); c.lineDashOffset=-t*40; c.shadowColor='rgba(183,155,255,1)'; c.shadowBlur=16; c.strokeStyle='rgba(205,185,255,.95)'; c.lineWidth=5;
  const P0=[260,780], P1=[470,640], P2=[560,860]; c.beginPath(); c.moveTo(P0[0],P0[1]); const N2=40; for(let k=1;k<=Math.round(N2*lp);k++){ const s=k/N2; const x=(1-s)*(1-s)*P0[0]+2*(1-s)*s*P1[0]+s*s*P2[0], y=(1-s)*(1-s)*P0[1]+2*(1-s)*s*P1[1]+s*s*P2[1]; c.lineTo(x,y);} c.stroke(); c.restore(); }
 c.restore();
 dust(c,t,'rgba(255,235,200,A)',.6);
}
/*FRAME*/
 // ===================== FRAME =====================
 {
  X.setTransform(1,0,0,1,0,0); X.globalAlpha=1; X.filter='none'; X.globalCompositeOperation='source-over';
  X.fillStyle='#000'; X.fillRect(0,0,1080,1920);
  const hdx=2.2*Math.sin(t*.9)+1.2*Math.sin(t*2.3), hdy=1.8*Math.sin(t*1.1+1);
  X.setTransform(1.012,0,0,1.012,-6.5+hdx,-11.5+hdy);
  // A -> B
  const aB0=TS('s3',-0.15), aB1=TS('s3@elftausend',0.2); const kAB=eio(pr(t,aB0,aB1-aB0));
  if(t<aB1) comp(shotA,t,1-kAB,1+0.7*kAB,612,900,14*kAB,0);
  // B -> C
  const bC0=TS('s4',-0.3), bC1=TS('s4',0.4); const kBC=eio(pr(t,bC0,bC1-bC0));
  if(t>aB0&&t<bC1) comp(shotB,t,kAB*(1-kBC),L(1.35,1,kAB),540,760,(1-kAB)*10+kBC*8,0);
  // C -> D
  const cD0=TS('s5',-0.2), cD1=TS('s5',0.45); const kCD=eio(pr(t,cD0,cD1-cD0));
  if(t>bC0&&t<cD1) comp(shotC,t,kBC*(1-kCD),L(1.25,1,kBC)*(1+1.6*kCD),560,1060,kCD*12,0);
  // D -> E
  const dE0=TS('s9',-0.25), dE1=TS('s9',0.35); const kDE=eio(pr(t,dE0,dE1-dE0));
  if(t>cD0&&t<dE1) comp(shotD,t,kCD*(1-kDE),L(1.3,1,kCD)*L(1,0.75,kDE),540,1000,kDE*8+(1-kCD)*6,0);
  // E -> F
  const eF0=TS('s12',-0.05), eF1=TS('s13',0.05); const kEF=eio(pr(t,eF0,eF1-eF0));
  if(t>dE0&&t<eF1) comp(shotE,t,kDE*(1-kEF),L(1.35,1,kDE)*L(1,0.45,kEF),540,1020,0,0);
  // F -> G (Whip-Pan „heute“)
  const fG0=TS('s15',-0.05), fG1=TS('s15@heute',0.3); const kFG=eio(pr(t,fG0,fG1-fG0));
  if(t>eF0&&t<fG1) comp(shotF,t,kEF,L(2.0,1,kEF),540,1120,Math.sin(Math.PI*kFG)*26,-1150*kFG);
  // G -> H
  const gH0=TS('s17',-0.2), gH1=TS('s17',0.35); const kGH=eio(pr(t,gH0,gH1-gH0));
  if(t>fG0&&t<gH1) comp(shotG,t,1-kGH,1+0.12*kGH,540,760,Math.sin(Math.PI*kFG)*26,1150*(1-kFG));
  if(t>gH0) comp(shotH,t,kGH,L(1.12,1,kGH),540,960,0,0);
  // Post: Lichtleck, Vignette, Filmkorn
  X.setTransform(1,0,0,1,0,0); X.filter='none';
  X.globalCompositeOperation='screen'; X.globalAlpha=0.10+0.04*Math.sin(t*0.8); rg(X,1000,120,700,'rgba(255,170,90,1)','rgba(255,120,60,0)');
  X.globalCompositeOperation='source-over'; X.globalAlpha=1; X.drawImage(VIG,0,0);
  const fi=Math.round(t*30); X.globalCompositeOperation='overlay'; X.globalAlpha=0.09; X.fillStyle=GRAINS[fi%4];
  X.save(); X.translate((fi*37)%256,(fi*91)%256); X.fillRect(-256,-256,1080+512,1920+512); X.restore();
  X.globalCompositeOperation='source-over'; X.globalAlpha=1;
  cv.style.opacity=1-pr(t,END,0.4);
 }
