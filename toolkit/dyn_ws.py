"""Patch a build script into the 'dynamic' engine (v2): pop-ins, stamp slams, camera punch, word pop, zoom hooks, faster sketches.
(Variante mit Wort-Zeitstempeln: der Build liest vo13 direkt, kein align-Replace nötig.)"""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def R_(a, b):
    global s
    assert a in s, a[:90]
    s = s.replace(a, b)

R_('{"".join(stage)}', '<div id="cam" style="position:absolute;inset:0;transform-origin:540px 860px">{"".join(stage)}</div>')
old = s[s.index(" // elements\n"):s.index(" // counters")]
new = ''' // elements
 const bo=x=>1+2.70158*Math.pow(x-1,3)+1.70158*Math.pow(x-1,2);
 for(const e of els){{
  if(e._st===undefined) e._st=e.classList.contains('stamp')||!!e.querySelector('.stamp');
  const tin=(S[e.dataset.in]??0)+(+e.dataset.d||0); const tout=e.dataset.out?S[e.dataset.out]:1e9;
  const r=pr(t,tin,e._st?.2:.3); const po=pr(t,tout,e.dataset.zoom?.35:.15);
  let tr='';
  if(e._st){{ const k=ease(r); tr=`scale(${{2.3-1.3*k}})`; e.style.opacity=Math.min(1,r*3)*(1-po); }}
  else {{ const k=bo(r); tr=`translateY(${{30*(1-ease(r))}}px) scale(${{0.72+0.28*k}})`; e.style.opacity=Math.min(1,r*2.2)*(1-po); }}
  if(po>0&&!e.dataset.zoom) tr+=` translateX(${{-90*ease(po)}}px)`;
  if(e.dataset.zoom){{ const z=ease(pr(t,S[e.dataset.zoom]-0.05,.4)); tr+=` scale(${{1+3.2*z}})`; }}
  if(e.dataset.zin){{ const z=ease(pr(t,S[e.dataset.zin],.4)); tr+=` scale(${{0.35+0.65*z}})`; }}
  e.style.transform=tr; e.style.filter='none';
 }}
 {{ let hs2=b.s; for(let i=BEATS.indexOf(b);i>0&&BEATS[i-1].head===b.head;i--) hs2=BEATS[i-1].s;
   let sc=1+0.045*(1-ease(pr(t,hs2,.45))); let dx=0,dy=0;
   for(const e of els){{ if(!e._st) continue; const t0=(S[e.dataset.in]??0)+(+e.dataset.d||0)+0.18; const a=t>t0&&t<t0+0.35?Math.exp(-(t-t0)*14)*12:0; dx+=a*Math.sin(t*90); dy+=a*Math.cos(t*77); }}
   document.getElementById('cam').style.transform=`translate(${{dx}}px,${{dy}}px) scale(${{sc}})`; }}
'''
s = s.replace(old, new)
R_("const p=ease(pr(t,t0,+sk.dataset.sdur||1.5));", "const p=ease(pr(t,t0,(+sk.dataset.sdur||1.5)*0.65));")
R_("sk.querySelectorAll('.mesh').forEach(e=>e.style.opacity=pr(t,t0+(+sk.dataset.sdur||1.5)*0.6,0.6));", "sk.querySelectorAll('.mesh').forEach(e=>e.style.opacity=pr(t,t0+(+sk.dataset.sdur||1.5)*0.4,0.4));")
R_("const hp=ease(pr(t,hs,.3));", "const hp=ease(pr(t,hs,.22)); H.style.transform=`translateX(${{-60*(1-hp)}}px)`; H.style.opacity=top*hp;")
R_("H.style.color=`rgb(${{g}},${{g2}},${{g3}})`;", "H.style.color='#0B0B10';")
R_("R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');",
   "const rpop=(BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose!==b.pose)?1+0.12*(1-ease(pr(t,b.s,.25))):1; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px) scale(${{rpop}})`+(end?' translate(321px,90px) scale(0.62)':'');")
R_("`<span class=\"${{i<=wi?'on':''}} ${{w[2]?(b.ch%2?'kw2':'kw'):''}}\">${{w[0]}}</span>`",
   "`<span class=\"${{i<=wi?'on':''}} ${{w[2]?(b.ch%2?'kw2':'kw'):''}}\" style=\"display:inline-block;margin:0 .06em;transform:scale(${{i===wi?1+0.12*(1-ease(pr(t,w[1],.16))):1}})\">${{w[0]}}</span>`")
open(dst, "w").write(s)
print("ok")
