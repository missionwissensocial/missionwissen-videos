"""Baustein „Maßstabswechsel“ (Stil-Update 03.11.2026, Vorbild schraffur/Bahn-Video) – Demo.

Idee: Eine Millimeterpapier-Karte kippt per CSS-3D (rotateX) in eine schräge Landschaft, kleine Skizzen-Häuser/Bahnhof
klappen wie in einem Pop-up-Buch hoch, ein „Hauptdarsteller“ (hier: Zug) fährt eine Route und zieht einen Zähler mit.
Danach kippt alles zurück in die Draufsicht. Ein durchgehender Kameraflug, kein Schnitt.

Technik (wichtig für Schärfe):
- Zoom NICHT per CSS-scale (3D-Layer würden unscharf gerastert), sondern im SVG (<g transform>) wie bei den Karten-Builds.
- CSS-3D nur für die Neigung: #plane {transform: rotateX(tilt)} in #persp {perspective}. Das Millimeterpapier liegt auf #plane
  und verzerrt sich dadurch automatisch perspektivisch.
- Pop-ups sind HTML-Elemente in #plane (transform-style: preserve-3d), per Projektion pj(x,y) positioniert,
  transform-origin unten Mitte, rotateX(-tilt·k) → stehen auf; Größe skaliert mit dem Zoom.
- Strichstärken pro Frame als px/z setzen (non-scaling-stroke verträgt sich nicht mit pathLength-Dash).

Benutzung: python3 build_massstab_demo.py  (im Ordner mit ../geo/ne, ../fonts wie bei setup.sh) → massstab.html;
python3 build_massstab_demo.py shots → Testframes ms_*.png. In echte Builds: CSS/HTML/JS-Block übernehmen, Zeiten an S-Anker hängen.
Alle Zahlen in der Demo sind BEISPIELWERTE.
"""
import json, os, sys, math
NE = os.path.expanduser("~/mw/geo/ne/geojson")
GF = os.path.abspath(os.path.expanduser("~/mw/fonts/gf/ofl"))
# Welt-Koordinaten: Plattkarte mit Breitenkorrektur, 60 px pro Breitengrad
L0, B0, KX, KY = 2.0, 56.5, 60 * 0.64, 60
X = lambda lon: (lon - L0) * KX
Y = lambda lat: (B0 - lat) * KY
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in r) + "Z" for r in rs)
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
shape = {n: d_of([r for f in cty["features"] if f["properties"]["NAME"] == n for r in rings(f["geometry"])]) for n in ("Germany", "Switzerland", "France", "Austria")}
ROUTE = [(10.0, 53.55), (9.73, 52.37), (9.5, 51.3), (8.68, 50.11), (8.47, 49.49), (8.4, 49.0), (7.85, 48.0), (7.59, 47.56)]
RP = [(X(a), Y(b)) for a, b in ROUTE]
route_d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in RP)
BAS = RP[-1]
# Gleise rund um Basel (Weltkoordinaten, in km-Maßstab egal – nur Bildwirkung): zwei Gleise, Richtung Nord-Süd
def track(x0, y0, x1, y1, off):
    dx, dy = x1 - x0, y1 - y0; n = math.hypot(dx, dy); ox, oy = -dy / n * off, dx / n * off
    return f"M{x0+ox:.2f} {y0+oy:.2f}L{x1+ox:.2f} {y1+oy:.2f}"
_dx, _dy = RP[-1][0] - RP[-2][0], RP[-1][1] - RP[-2][1]; _n = math.hypot(_dx, _dy)
TR0 = (BAS[0] - _dx / _n * 7, BAS[1] - _dy / _n * 7); TR1 = (BAS[0] + _dx / _n * 2.0, BAS[1] + _dy / _n * 2.0)  # Gleise in Verlängerung der Route
tracks = "".join(f'<path class="trk" d="{track(*TR0, *TR1, o)}"/>' for o in (-0.22, -0.08, 0.08, 0.22))
# Pop-up-Objekte (Häuser + Bahnhof) – Weltposition, Typ, Verzögerung
import random; random.seed(4)
POP = [("station", BAS[0] - 1.3, BAS[1] - 0.6, 0.0)]
for i in range(16):
    a = random.uniform(0, 2 * math.pi); r = random.uniform(1.4, 3.6)
    hx, hy = BAS[0] + math.cos(a) * r * 1.2, BAS[1] - 1.2 + math.sin(a) * r
    if abs(hx - BAS[0]) < 1.0: hx += 1.8 * (1 if hx > BAS[0] else -1)  # Gleise frei halten
    POP.append(("house", hx, hy, 0.08 + i * 0.05))
INK = "#2B2D35"; PUR = "#7B3FE4"; TQ = "#19C6B4"
HOUSE = (f'<svg viewBox="0 0 60 56" width="100%" height="100%"><path d="M6 26 L30 6 L54 26 V52 H6 Z" fill="#FCFCFD" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
         f'<path d="M6 26 L30 6 L54 26" fill="none" stroke="{PUR}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<rect x="24" y="34" width="12" height="18" fill="none" stroke="{INK}" stroke-width="2.5"/></svg>')
STATION = (f'<svg viewBox="0 0 140 70" width="100%" height="100%"><path d="M6 24 H134 V66 H6 Z" fill="#FCFCFD" stroke="{INK}" stroke-width="3"/>'
           f'<path d="M2 24 L70 4 L138 24" fill="none" stroke="{PUR}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
           + "".join(f'<path d="M{18+i*22} 66 V40 a8 8 0 0 1 16 0 V66" fill="none" stroke="{INK}" stroke-width="2.5"/>' for i in range(5)) + '</svg>')
pops = "".join(f'<div class="pop" data-k="{k}" data-x="{x:.2f}" data-y="{y:.2f}" data-d="{d}" data-w="{2.6 if k=="station" else 0.8}">{STATION if k=="station" else HOUSE}</div>' for k, x, y, d in POP)
TRAIN = (f'<svg viewBox="0 0 120 40" width="100%" height="100%"><rect x="2" y="4" width="116" height="32" rx="14" fill="{PUR}" stroke="#4A1FA0" stroke-width="3"/>'
         + "".join(f'<rect x="{16+i*20}" y="11" width="13" height="10" rx="3" fill="#FFFFFF"/>' for i in range(5)) + '</svg>')
W, H = 3200, 4400  # Plane-Größe (größer als Bühne, damit beim Kippen keine Kante sichtbar wird)
# Kamera-Keyframes: t, Fokus (Welt), Zoom, Neigung (Grad)
FULL = (X(10.3), Y(51.2), 1.45); GROUND = (BAS[0] + 0.2, BAS[1] - 1.0, 95.0)
CAM = [(0.0, *FULL, 0), (3.6, *FULL, 0), (5.6, *GROUND, 58), (9.2, *GROUND, 58), (11.2, *FULL, 0), (14.0, *FULL, 0)]
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Unbounded;src:url("file://{GF}/unbounded/Unbounded[wght].ttf");font-weight:200 900}}
@font-face{{font-family:JBM;src:url("file://{GF}/jetbrainsmono/JetBrainsMono[wght].ttf");font-weight:100 800}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#fff}}
#v{{position:relative;width:1080px;height:1920px;overflow:hidden;background:linear-gradient(#FFFFFF 40%,#F4F4F6)}}
#persp{{position:absolute;left:0;top:250px;width:1080px;height:1150px;perspective:1300px;perspective-origin:540px 300px;overflow:hidden;background:linear-gradient(#EEF0FA,#FFFFFF)}}
#plane{{position:absolute;left:{540-W/2}px;top:{620-H/2}px;width:{W}px;height:{H}px;transform-style:preserve-3d;transform-origin:50% 50%;
background:linear-gradient(rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(90deg,rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,
linear-gradient(rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,linear-gradient(90deg,rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,#FCFCFD}}
#map{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;overflow:visible}}
.trk{{fill:none;stroke:#5D616B;stroke-linecap:round}} .slp{{fill:none}}
.pop{{position:absolute;left:0;top:0;transform-origin:50% 100%;transform-style:preserve-3d}}
.lab{{position:absolute;font-family:JBM;font-weight:800;font-size:34px;color:#fff;background:#E5484D;border-radius:10px;padding:4px 12px;white-space:nowrap;transform:translate(-50%,-150%)}}
#title{{position:absolute;left:80px;top:150px;width:920px;font-family:Unbounded;font-weight:600;font-size:62px;line-height:1.1;letter-spacing:-1.5px;color:#0B0B10}}
#note{{position:absolute;left:80px;top:1360px;font-family:JBM;font-size:20px;color:#8A8F99}}
</style></head><body><div id="v">
<div id="persp"><div id="plane">
<svg id="map" viewBox="0 0 {W} {H}"><g id="cam">
<path d="{shape["France"]}" fill="#FFFFFF" stroke="{INK}" class="ol"/><path d="{shape["Austria"]}" fill="#FFFFFF" stroke="{INK}" class="ol"/>
<path d="{shape["Germany"]}" fill="rgba(123,63,228,.16)" stroke="{INK}" class="ol"/><path d="{shape["Switzerland"]}" fill="rgba(25,198,180,.28)" stroke="#0E8C80" class="ol"/>
<g id="trks" style="opacity:0">{tracks}</g>
<path id="route" d="{route_d}" fill="none" stroke="#E5484D" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
</g></svg>
{pops}
<div id="train" class="pop" data-w="70">{TRAIN}</div>
<div id="cnt" class="lab">+0 MIN</div>
</div></div>
<div id="title">Baustein: Maßstabswechsel</div>
<div id="note">DEMO · BEISPIELWERTE · KARTE SCHEMATISCH</div>
</div>
<script>
const CAM={json.dumps(CAM)}, RP={json.dumps([[round(a,2),round(b,2)] for a,b in RP])}, W={W}, H={H}, TR0={json.dumps(TR0)}, TR1={json.dumps(TR1)};
const cl=(x,a,b)=>Math.max(a,Math.min(b,x)), pr=(t,t0,d)=>cl((t-t0)/d,0,1), ease=p=>1-Math.pow(1-p,3), sm=u=>u*u*(3-2*u);
const bo=x=>1+2.70158*Math.pow(x-1,3)+1.70158*Math.pow(x-1,2);
function cam(t){{ if(t<=CAM[0][0]) return CAM[0]; for(let i=0;i<CAM.length-1;i++){{const a=CAM[i],b=CAM[i+1]; if(t>=a[0]&&t<b[0]){{const u=sm((t-a[0])/(b[0]-a[0]));
  return [t,a[1]+(b[1]-a[1])*u,a[2]+(b[2]-a[2])*u,Math.exp(Math.log(a[3])+(Math.log(b[3])-Math.log(a[3]))*u),a[4]+(b[4]-a[4])*u];}}}} return CAM[CAM.length-1]; }}
// Punkt auf Polyline bei Anteil u
const seg=[]; let LEN=0; for(let i=1;i<RP.length;i++){{const l=Math.hypot(RP[i][0]-RP[i-1][0],RP[i][1]-RP[i-1][1]); seg.push(l); LEN+=l;}}
function along(u){{ let d=u*LEN; for(let i=0;i<seg.length;i++){{ if(d<=seg[i]||i===seg.length-1){{const f=cl(d/seg[i],0,1); return [RP[i][0]+(RP[i+1][0]-RP[i][0])*f, RP[i][1]+(RP[i+1][1]-RP[i][1])*f, Math.atan2(RP[i+1][1]-RP[i][1],RP[i+1][0]-RP[i][0])];}} d-=seg[i]; }} }}
window.render=function(t){{
 const [_,fx,fy,z,tilt]=cam(t); const CX=W/2, CY=H/2;
 document.getElementById('cam').setAttribute('transform',`translate(${{CX}},${{CY}}) scale(${{z}}) translate(${{-fx}},${{-fy}})`);
 const pj=(x,y)=>[CX+(x-fx)*z, CY+(y-fy)*z];
 document.getElementById('plane').style.transform=`rotateX(${{tilt}}deg)`;
 document.querySelectorAll('.ol').forEach(e=>e.setAttribute('stroke-width',(2/z).toFixed(4)));
 const R=document.getElementById('route'); R.setAttribute('stroke-width',(7/z).toFixed(4));
 const up=ease(pr(t,0.3,3.4)); R.style.strokeDashoffset=1-up;   // Route zeichnet sich mit dem Zug
 const T=document.getElementById('trks'); T.style.opacity=pr(t,4.6,0.6)*(1-pr(t,9.6,0.6)); T.querySelectorAll('.trk').forEach(e=>e.setAttribute('stroke-width',(5/z).toFixed(4)));
 const k=tilt/58; // 0 = Draufsicht, 1 = voll gekippt
 // Pop-ups: stehen auf, sobald gekippt (gestaffelt), klappen beim Zurückkippen wieder ein
 for(const p of document.querySelectorAll('.pop[data-k]')){{ const [x,y]=pj(+p.dataset.x,+p.dataset.y); const w=(+p.dataset.w)*z;
   const a=bo(pr(k,0.35+(+p.dataset.d)*0.6,0.35)); p.style.width=w+'px'; p.style.height=(w*0.9)+'px';
   p.style.transform=`translate(${{x-w/2}}px,${{y-w*0.9}}px) rotateX(${{-tilt}}deg) scaleY(${{Math.max(0.001,a)}})`; p.style.opacity=k>0.3?1:0; p.style.zIndex=Math.round(y); }}
 // Hauptdarsteller: Zug fährt die Route (0.3–3.7 s), dann auf den Gleisen in Basel ein (6.0–8.4 s)
 let tx,ty,ang; const u=ease(pr(t,0.3,3.4));
 if(t<5.8){{ [tx,ty,ang]=along(u); }} else {{ const v=ease(pr(t,6.0,2.4)); tx=TR0[0]+(TR1[0]-TR0[0])*(0.15+0.7*v); ty=TR0[1]+(TR1[1]-TR0[1])*(0.15+0.7*v); ang=Math.atan2(TR1[1]-TR0[1],TR1[0]-TR0[0]); }}
 const tr=document.getElementById('train'); const [px,py]=pj(tx,ty); const tw=Math.max(60, 1.5*z);
 tr.style.width=tw+'px'; tr.style.height=(tw/3)+'px';
 tr.style.transform=`translate(${{px-tw/2}}px,${{py-tw/6}}px) rotateZ(${{ang}}rad) rotateX(${{-tilt*0.35}}deg)`;
 tr.style.opacity=(t<4.9||t>5.9)?1:0; tr.style.zIndex=Math.round(py)+1;
 // Zähler hängt am Zug
 const c=document.getElementById('cnt'); c.textContent='+'+Math.round(24*u)+' MIN'; c.style.left=px+'px'; c.style.top=py+'px';
 c.style.transform=`translate(-50%,-150%) rotateX(${{-tilt}}deg)`; c.style.opacity=t>0.3&&t<5.0?1:0;
}};
render(0);
</script></body></html>'''
open("massstab.html", "w").write(html)
print("ok massstab.html")
if len(sys.argv) > 1 and sys.argv[1] == "shots":
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--allow-file-access-from-files"]); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto("file://" + os.path.abspath("massstab.html")); pg.wait_for_timeout(600)
        for t in (0.5, 2.5, 4.4, 5.0, 6.5, 8.0, 10.2, 12.0):
            pg.evaluate(f"render({t})"); pg.screenshot(path=f"ms_{t}.png")
        b.close()
