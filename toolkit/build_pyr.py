import json, os, re, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
GF = os.path.abspath("../fonts/gf/ofl")

# ---------- robot ----------
src = open("../robot3/soft.py").read().split("poses=")[0].replace("import os\n", "").replace("os.chdir(os.path.dirname(os.path.abspath(__file__)))\n", "")
ns = {}; exec(src, ns)
def robot_svg(p, **k):
    s = ns["robot"](p, **k)
    e = ns["eyes"](k.get("eye","neutral"), p)
    s = s.replace(e, '<g class="eyes">' + e + '</g>', 1)
    s = s.replace('opacity="0.3" filter="url(#' + p + 'soft)"/>', 'opacity="0.3" class="pulse" filter="url(#' + p + 'soft)"/>', 1)
    return s
POSES = {"neutral": {}, "zeigt": dict(ra="point", tilt=-3), "winkt": dict(eye="happy", la="wave", tilt=3),
         "denkt": dict(eye="think", ra="think"), "staunt": dict(eye="wow")}

# ---------- beats ----------
CH = ["", "", "", "", "", ""]
HOOK = 'Wie haben die Ägypter die <span style="color:#7B3FE4">Pyramiden</span> gebaut?'
B = [
 ("p1", 0, HOOK, "Wie haben die *Ägypter* die *Pyramiden* gebaut, ganz ohne *moderne* *Kräne* und *Maschinen?*", "staunt"),
 ("p2", 0, HOOK, "Sicher weiß es *niemand.* Aber vieles ist sehr *wahrscheinlich.*", None),
 ("p3", 1, "", "Die *größte* Pyramide, die *Cheops-Pyramide* bei *Kairo,* besteht aus über *zwei* *Millionen* *Steinblöcken.*", None),
 ("p4", 1, "", "Jeder wiegt im Schnitt etwa so viel wie *zwei* *Autos.*", None),
 ("p5", 1, "", "Die meisten Blöcke kamen aus einem *Steinbruch* *direkt* *neben* der *Baustelle.*", None),
 ("p6", 2, "", "Nur die *weißen* *Steine* für die *glatte* *Außenhülle* kamen per *Schiff* über den *Nil,* vom *anderen* *Ufer.*", None),
 ("p7", 2, "", "Das steht auf *viertausendfünfhundert* Jahre alten *Papyrus-Rollen:* im *Arbeitstagebuch* eines *Aufsehers,* der die Transporte *selbst* geleitet hat.", None),
 ("p8", 3, "", "An Land zogen *Arbeiter* alle Blöcke auf *Holzschlitten.*", None),
 ("p9", 3, "", "Im *trockenen* *Sand* graben sich Schlitten *ein.* *Feuchter* *Sand* dagegen wird *fest.*", None),
 ("p10", 3, "", "Physiker haben getestet: Darauf braucht man nur etwa *halb* *so* *viel* *Kraft.*", None),
 ("p11", 3, "", "Forscher vermuten: Darum gossen die Arbeiter *Wasser* vor den *Schlitten.*", None),
 ("p12", 4, "", "Nach oben ging es wohl über *Rampen.*", None),
 ("p13", 4, "", "Ob sie *gerade* hochführten oder sich um die Pyramide *herumwanden,* darüber *streiten* Forscher bis heute.", None),
 ("p14", 5, "", "Und die Arbeiter waren *keine* *Sklaven.*", None),
 ("p15", 5, "", "Sie bekamen *Lohn,* vor allem *Brot* und *Bier.*", None),
 ("p16", 5, "", "Und sie bekamen *eigene* *Gräber* neben den *Pyramiden.*", None),
]

# word start times from ElevenLabs Scribe transcript (original speed), dashes excluded
WS = json.load(open("ws.json"))
SPEED = 1.3
out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","vo13.mp3"],capture_output=True,text=True).stdout
AUD = float(out.strip())

flat=[]; owner=[]
for bi,(bid,ch,head,text,pose) in enumerate(B):
    for tk in text.split():
        if tk in ("–","-"): continue
        flat.append(tk); owner.append(bi)
assert len(flat)==len(WS), (len(flat), len(WS))
starts=[x/SPEED for x in WS]
beats=[]
for bi,(bid,ch,head,text,pose) in enumerate(B):
    idx=[k for k,o in enumerate(owner) if o==bi]
    words=[[flat[k], round(starts[k],3)] for k in idx]
    beats.append(dict(id=bid,ch=ch,head=head,s=round(max(0,starts[idx[0]]-0.12),3),pose=pose,words=words))
for i,b in enumerate(beats): b["e"]=beats[i+1]["s"] if i+1<len(beats) else round(AUD,3)
beats[0]["s"]=0.0
END=round(AUD+0.15,3); TOTAL=AUD+3.4
for b in beats:
    inkw=False
    for w in b["words"]:
        raw=w[0]; start=raw.startswith("*"); stop=("*" in raw[1:]) if start else ("*" in raw)
        kw=inkw or start
        if start and stop: inkw=False
        elif start: inkw=True
        elif stop and inkw: inkw=False
        w[0]=raw.replace("*",""); w.append(1 if kw else 0)
for b in beats:
    cid=0; cur=0; cnt=0
    for w in b["words"]:
        L=len(w[0])
        if cnt and (cur+1+L>24 or cnt>=4): cid+=1; cur=0; cnt=0
        cur+=(1 if cnt else 0)+L; cnt+=1; w.append(cid)
S={b["id"]:b["s"] for b in beats}; S["end"]=END
for b in beats:
    for w,t_,k,*_ in b["words"]:
        key=b["id"]+"@"+re.sub(r"[^\wäöüß,-]","",w).strip(",")
        S.setdefault(key,t_)

def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
srt = []; n = 1
for b in beats:
    ws = b["words"]
    for i in range(0, len(ws), 4):
        ch = ws[i:i + 4]; st = ch[0][1]; en = ws[i + 4][1] if i + 4 < len(ws) else b["e"]
        srt.append(f"{n}\n{ts(st)} --> {ts(en)}\n{' '.join(w[0] for w in ch)}\n"); n += 1
os.makedirs("out", exist_ok=True)
open("out/untertitel.srt", "w").write("\n".join(srt))
open("out/skript.txt", "w").write("\n".join(re.sub(r"\*", "", x[3]) for x in B) + "\n")
rows = ["| Zeit | Kapitel | Headline | Sprechtext | Roboter |", "|---|---|---|---|---|"]
for b in beats:
    rows.append(f"| {b['s']:.1f}–{b['e']:.1f} s | {CH[b['ch']]} | {b['head']} | {' '.join(w[0] for w in b['words'])} | {b['pose'] or '–'} |")
open("out/beats.md", "w").write("\n".join(rows) + f"\n\nGesamtlänge: {TOTAL:.1f} s\n")

# ---------- helpers ----------
def ic(d, size=56, col="#0B0B10", sw=3.2):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 48 48" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
I = dict(
 person='<circle cx="24" cy="15" r="7"/><path d="M10 42c0-8 6-13 14-13s14 5 14 13"/>',
 doc='<path d="M12 5h17l9 9v29H12z"/><path d="M29 5v9h9M18 24h14M18 31h14M18 38h9"/>',
 globe='<circle cx="24" cy="24" r="18"/><path d="M6 24h36M24 6c-7 8-7 28 0 36M24 6c7 8 7 28 0 36"/>',
 clock='<circle cx="24" cy="24" r="18"/><path d="M24 13v11l7 5"/>',
 idc='<rect x="5" y="11" width="38" height="26" rx="4"/><circle cx="16" cy="22" r="4"/><path d="M10 32c1-4 11-4 12 0M27 19h11M27 25h11M27 31h7"/>',
 ccard='<rect x="5" y="11" width="38" height="26" rx="4"/><path d="M5 19h38M11 30h8"/>',
 euro='<path d="M34 12a13 13 0 1 0 0 24"/><path d="M8 21h20M8 28h18"/>',
 mail='<rect x="5" y="11" width="38" height="26" rx="3"/><path d="M5 13l19 13 19-13"/>',
)
TQ = "#19C6B4"; PUR = "#7B3FE4"; RED = "#E5484D"
def card(inner, x, y, w, h, cls="", attrs="", extra_style=""):
    return f'<div class="card {cls}" {attrs} style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra_style}">{inner}</div>'
def el(inner, x, y, attrs, w=None, style=""):
    ws = f"width:{w}px;" if w else ""
    return f'<div class="el" {attrs} style="left:{x}px;top:{y}px;{ws}{style}">{inner}</div>'
stage = []
A = lambda i, o=None, d=0: f'data-in="{i}"' + (f' data-out="{o}"' if o else '') + (f' data-d="{d}"' if d else '')
def cnt(v, anchor, dec=0, d=0):
    return f'<span class="count" data-count="{v}" data-dec="{dec}" data-cin="{anchor}" data-cd="{d}">0</span>'
INK = "#2B2D35"; INK2 = "#7A7F8C"
def P(d, w=2.2, c=INK, extra=""): return f'<path class="ink" pathLength="1" stroke-dasharray="1" d="{d}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def C(cx, cy, r, w=2.2, c=INK): return f'<circle class="ink" pathLength="1" stroke-dasharray="1" cx="{cx}" cy="{cy}" r="{r}" stroke="{c}" stroke-width="{w}" fill="none"/>'
def R(x, y, w_, h, rx=0, w=2.2, c=INK): return f'<rect class="ink" pathLength="1" stroke-dasharray="1" x="{x}" y="{y}" width="{w_}" height="{h}" rx="{rx}" stroke="{c}" stroke-width="{w}" fill="none"/>'
def D(d, w=1.3, c=INK2): return f'<path class="ink" pathLength="1" stroke-dasharray="1" d="{d}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round"/>'
def TX(x, y, s, size=22, col=INK, fam="JBM", wt=700, anchor="start"):
    return f'<text class="mesh" style="opacity:0" x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" font-weight="{wt}" font-size="{size}" fill="{col}">{s}</text>'
_sid = [0]
def mesh(clip_d, w, h):
    _sid[0] += 1; i = f"m{_sid[0]}"
    return (f'<defs><clipPath id="c{i}"><path d="{clip_d}"/></clipPath><pattern id="p{i}" width="16" height="16" patternUnits="userSpaceOnUse">'
            f'<path d="M0 0.5H16M0.5 0V16" stroke="#9AA0AA" stroke-width="1" stroke-dasharray="1.5 3.5"/></pattern></defs>'
            f'<g class="mesh" style="opacity:0" clip-path="url(#c{i})"><rect width="{w}" height="{h}" fill="url(#p{i})"/></g>')
def sketch(body, w, h, x, y, anchor, d=0, dur=1.6, scale=1.0):
    return (f'<svg class="sketch" data-sin="{anchor}" data-sd="{d}" data-sdur="{dur}" width="{w*scale:.0f}" height="{h*scale:.0f}" viewBox="0 0 {w} {h}" '
            f'style="position:absolute;left:{x}px;top:{y}px;overflow:visible">{body}</svg>')
def mk(text, x, y, anchor, d=0.6, col="#7B3FE4"):
    return (f'<div class="el mk" {A(anchor,None,d)} style="left:{x}px;top:{y}px"><span class="mkbox" style="border-color:{col}"></span>'
            f'<span class="mono" style="color:{col}">{text}</span></div>')
def mm(inner, x, y, w, h, attrs):
    return f'<div class="mm el" {attrs} style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{inner}</div>'



CENTER = "display:flex;justify-content:center"
STOP = 300; STH = 980; SYL = 470   # Bühne: Bildschirm-y 300..1280, Kamera-Fokus lokal y=560
PURS = "#5B2BB5"; GR = "#3F434C"; TQD = "#0E8C80"; SAND = "#B88A1A"; WAT = "#4BA3D9"
SANDF = "#F3E6C6"; STONE = "#E6D3A6"; WHITE_ST = "#FBF8F1"
# ---- Welt (Seitenansicht, Boden y=0) ----
PX0, PX1, PAX, PAY = 200, 1600, 900, -890      # Pyramide
RAMP = [(-300, 0), (500, -381)]                 # Rampe am linken Hang
def lerp2(a, b, u): return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
# Kamera [cx, cy, z]
HOOK0 = [900, -470, 0.66]; HOOK1 = [880, -450, 0.72]
FACE = [700, -330, 1.25]
QUAR = [-1030, -70, 1.15]
NILE = [-1960, -80, 0.95]
SLED0 = [-800, -100, 1.25]; SLED1 = [-560, -90, 1.25]
CLOSE = [-500, -60, 2.1]; CLOSE2 = [-430, -60, 2.1]
RAMPV = [250, -330, 0.78]
PYRV = [850, -450, 0.64]
VILL = [2250, -110, 1.0]; VILL2 = [2330, -200, 0.55]
FINV = [880, -330, 0.27]
cam = [("p1", -0.6, *HOOK0), ("p3", -0.2, *HOOK1), ("p3@Cheops-Pyramide", 0.2, *FACE), ("p5", -0.2, *FACE), ("p5@Steinbruch", 0.2, *QUAR),
       ("p6", 0, *QUAR), ("p6@Schiff", -0.2, *NILE), ("p8", -0.3, *NILE), ("p8@Arbeiter", 0.2, *SLED0), ("p9", -0.2, *SLED1),
       ("p9@trockenen", 0.2, *CLOSE), ("p11", 0, *CLOSE), ("p11@Wasser", 0.4, *CLOSE2), ("p12", -0.2, *CLOSE2), ("p12@Rampen", 0.1, *RAMPV),
       ("p13", 0.3, *RAMPV), ("p13@herumwanden", 0, *PYRV), ("p14", -0.4, *PYRV), ("p14@keine", 0.2, *VILL), ("p15", 0, *VILL),
       ("p16", 0, *VILL2), ("p16@Gräber", 0.2, *VILL2)]
# Schlitten-Weg (Welt-x, -y) über Zeit
sled = [("p8", -0.2, -820, 0), ("p9", 0, -560, 0), ("p11@Schlitten", 0.3, -420, 0), ("p12", 0, -330, 0), ("p12@Rampen", 0.2, -300, 0),
        ("p13@gerade", 0.4, RAMP[1][0] - 20, RAMP[1][1] + 15)]
boat = [("p6", 0, -2560), ("p6@Ufer", 0.6, -1660)]
PANJS = dict(cam=cam, sled=sled, boat=boat, ramp=RAMP, SYL=SYL)

# ---- Welt-SVG ----
W0, W1 = -3200, 3600
def poly(pts, fill, stroke=INK, sw=3, extra=""):
    return f'<path d="M{" L".join(f"{x} {y}" for x, y in pts)}Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'
g = []
g.append(f'<circle cx="1500" cy="-760" r="70" fill="#FFE7A3" stroke="#E6B84D" stroke-width="3"/>')
# Boden
g.append(f'<rect x="{W0}" y="0" width="{W1-W0}" height="600" fill="{SANDF}"/>')
# Nil (Seitenansicht: Senke mit Wasser)
g.append(poly([(-2380, 0), (-2330, 50), (-1620, 50), (-1570, 0)], "#CFE7F6", WAT, 3))
g.append(f'<g id="waves">' + "".join(f'<path d="M{x} 20q18 -10 36 0t36 0" fill="none" stroke="{WAT}" stroke-width="3" stroke-linecap="round"/>' for x in range(-2300, -1650, 140)) + '</g>')
# Tura-Kliff (Ostufer) mit weißem Kalkstein
g.append(poly([(-3200, 0), (-3200, -190), (-2560, -190), (-2470, -120), (-2440, 0)], WHITE_ST, INK, 3))
g.append("".join(f'<path d="M{x} -{h} h70" stroke="#C9C2B2" stroke-width="2"/>' for x, h in [(-3100, 150), (-2950, 110), (-2800, 160), (-2700, 80), (-3050, 60)]))
# Steinbruch (Grube) mit Stufen
g.append(poly([(-1300, 0), (-1270, 60), (-1180, 60), (-1150, 125), (-860, 125), (-830, 60), (-790, 60), (-770, 0)], "#FAF5E8", INK, 3))
for k, (x, y) in enumerate([(-1140, 70), (-1080, 70), (-1260, 15), (-900, 70), (-1020, 70), (-960, 25)]):
    g.append(f'<rect x="{x}" y="{y}" width="56" height="44" fill="{STONE}" stroke="{INK}" stroke-width="2.4" rx="2"/>')
g.append(f'<rect id="qblock" x="-880" y="15" width="56" height="44" fill="{STONE}" stroke="{PURS}" stroke-width="3.5" rx="2"/>')
# Hafen-Steg am Westufer
g.append(f'<path d="M-1590 0 h-90 M-1660 0 v40 M-1610 0 v40" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
# Weg (befestigt) bis zur Rampe
g.append(f'<rect id="wet" x="-560" y="-2" width="260" height="14" fill="#C9A86A" opacity="0"/>')
g.append(f'<path id="pile" d="M0 0" fill="#E9D3A0" stroke="{INK}" stroke-width="2"/>')
# Pyramide (wächst per clip)
pyr = [(PX0, 0), (PAX, PAY), (PX1, 0)]
g.append(f'<defs><clipPath id="pclip"><rect id="pcr" x="{PX0-10}" y="{PAY}" width="{PX1-PX0+20}" height="{-PAY+2}"/></clipPath>'
         f'<clipPath id="ptri"><path d="M{PX0} 0L{PAX} {PAY}L{PX1} 0Z"/></clipPath>'
         f'<pattern id="blk" width="60" height="34" patternUnits="userSpaceOnUse"><path d="M0 0.5H60M0.5 0V17M30 17V34M0 17.5H60" stroke="#9A8150" stroke-width="1.6" fill="none"/></pattern></defs>')
g.append(f'<g clip-path="url(#pclip)">{poly(pyr, STONE, INK, 3)}<g clip-path="url(#ptri)"><rect id="pgrid" x="{PX0}" y="{PAY}" width="{PX1-PX0}" height="{-PAY}" fill="url(#blk)" opacity=".55"/></g>'
         f'<path id="casing" d="M{PX0} 0L{PAX} {PAY}L{PX1} 0Z" fill="{WHITE_ST}" stroke="{INK}" stroke-width="3" opacity="1"/>'
         f'<path id="cshade" d="M{PAX} {PAY}L{PX1} 0L{PAX+120} 0Z" fill="#E9E1CF" opacity="1"/></g>')
g.append(f'<path id="pbuild" d="M0 0" fill="none" stroke="{INK}" stroke-width="3"/>')
# Rampe (Lehm/Schutt)
(rx0, ry0), (rx1, ry1) = RAMP
g.append(f'<path id="ramp" d="M{rx0-40} 0L{rx1} {ry1}L{rx1+40} {ry1}L{rx1+120} 0Z" fill="#D9B98A" stroke="{INK}" stroke-width="3" stroke-linejoin="round" opacity="0"/>')
# Dorf + Gräber
for k, x in enumerate([1880, 2030, 2180, 2360, 2520]):
    h = [70, 85, 70, 90, 75][k]
    g.append(f'<g class="house" style="opacity:0"><rect x="{x}" y="{-h}" width="120" height="{h}" fill="#E8D2AE" stroke="{INK}" stroke-width="2.6"/><rect x="{x+48}" y="{-40}" width="24" height="40" fill="{INK}" opacity=".75"/><path d="M{x-6} {-h}h132" stroke="{INK}" stroke-width="4"/></g>')
g.append(f'<g class="house" style="opacity:0"><path d="M2680 0a50 50 0 0 1 100 0Z" fill="#D9B98A" stroke="{INK}" stroke-width="2.6"/><path d="M2715 0v-18a15 15 0 0 1 30 0V0" fill="{INK}" opacity=".7"/></g>')
for k, x in enumerate([2880, 3010, 3140]):
    g.append(f'<g class="grave" style="opacity:0">{poly([(x, 0), (x+12, -50), (x+88, -50), (x+100, 0)], "#E2D5BC", INK, 2.6)}<path d="M{x+42} -30h16" stroke="{INK}" stroke-width="3"/></g>')
g.append(f'<path d="M{W0} 0H{W1}" stroke="{INK}" stroke-width="3"/>')
world_svg = f'<svg width="1" height="1" style="position:absolute;left:0;top:0;overflow:visible">{"".join(g)}</svg>'
# Schlitten + Block (Hauptdarsteller), Arbeiter
def worker(k, flip=False):
    s = -1 if flip else 1
    return (f'<g class="wk" data-k="{k}"><circle cx="0" cy="-58" r="9" fill="#fff" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M0 -48 L{4*s} -22" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>'
            f'<path class="arm" d="M{2*s} -42 L{-16*s} -40" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
            f'<path class="lg1" d="M{4*s} -22 L{-4*s} 0" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>'
            f'<path class="lg2" d="M{4*s} -22 L{12*s} 0" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/></g>')
sled_svg = (f'<svg width="1" height="1" style="position:absolute;left:0;top:0;overflow:visible"><g id="sledg">'
            f'<g id="sledbody"><path d="M-42 -6 H44 q10 0 12 -10" fill="none" stroke="#7A5530" stroke-width="5" stroke-linecap="round"/>'
            f'<rect x="-36" y="-14" width="74" height="8" fill="#B07F4C" stroke="{INK}" stroke-width="2"/>'
            f'<rect x="-30" y="-58" width="62" height="44" fill="{STONE}" stroke="{PURS}" stroke-width="3.5" rx="2"/></g>'
            f'<path id="rope" d="M50 -16 L110 -36" stroke="#8A6A3A" stroke-width="2.6"/>'
            + "".join(f'<g transform="translate({120 + k*34},0)">{worker(k)}</g>' for k in range(5))
            + f'<g id="pourer" transform="translate(84,0)" style="opacity:0"><circle cx="0" cy="-58" r="9" fill="#fff" stroke="{INK}" stroke-width="3"/>'
              f'<path d="M0 -48 L-2 -22 M-2 -22 L-8 0 M-2 -22 L6 0 M0 -42 L-14 -50" stroke="{INK}" stroke-width="3.2" stroke-linecap="round" fill="none"/>'
              f'<path d="M-30 -62 q4 -14 16 -10 l4 14 q-10 8 -20 -4z" fill="#C98A55" stroke="{INK}" stroke-width="2"/></g>'
            + "".join(f'<circle class="drop" r="3" fill="{WAT}" style="opacity:0"/>' for _ in range(8))
            + '</g></svg>')
boat_svg = (f'<svg width="1" height="1" style="position:absolute;left:0;top:0;overflow:visible"><g id="boatg">'
            f'<path d="M-90 -6 Q0 30 90 -6 L76 -14 H-76Z" fill="#B07F4C" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<rect x="-30" y="-58" width="60" height="44" fill="{WHITE_ST}" stroke="{PURS}" stroke-width="3.5" rx="2"/>'
            f'<path d="M50 -14 V-120 M50 -116 Q90 -80 52 -40" stroke="{INK}" stroke-width="3" fill="#FFFFFF" stroke-linejoin="round"/></g></svg>')
def wlab(x, y, text, i, o, col=PURS, d=0, dx=0, dy=0, sfx="marker", lid=""):
    idd = f' id="{lid}"' if lid else ""
    return (f'<div class="geo" data-x="{x}" data-y="{y}"><div class="el mk"{idd} {A(i, o, d)} data-sfx="{sfx}" style="left:{-70+dx}px;top:{-14+dy}px">'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
labs = (wlab(PAX, PAY, "CHEOPS-PYRAMIDE · BEI KAIRO", "p3@Cheops-Pyramide", "p4", PURS, 0.2, dx=-110, dy=-70)
        + wlab(-1030, 125, "STEINBRUCH", "p5@Steinbruch", "p6", PURS, 0.3, dx=0, dy=24)
        + wlab(-2470, -150, "OSTUFER: WEISSER KALKSTEIN", "p6@weißen", "p7", GR, 0, dx=40, dy=-60)
        + wlab(-1980, 50, "NIL", "p6@Nil", "p8", WAT, 0, dx=40, dy=26)
        + wlab(-1640, 0, "WESTUFER: BAUSTELLE", "p6@Ufer", "p8", PURS, 0.3, dx=0, dy=-110)
        + wlab(-430, -60, "TROCKEN", "p9@trockenen", "p9@Feuchter", "#8A6A12", 0, dx=40, dy=-120, lid="ltr")
        + wlab(-430, -60, "FEUCHT", "p9@Feuchter", "p10", WAT, 0, dx=40, dy=-120)
        + wlab(RAMP[0][0] + 200, -150, "RAMPE", "p12@Rampen", "p13@herumwanden", "#8A6A12", 0.2, dx=-80, dy=0)
        + wlab(2200, -95, "ARBEITERSIEDLUNG", "p14@Sklaven", "p15@Lohn", PURS, 0.2, dx=-40, dy=-60)
        + wlab(3010, -50, "ARBEITERGRÄBER", "p16@Gräber", "end", PURS, 0.1, dx=-200, dy=-60))
note = el('<div class="note mono">DARSTELLUNG SCHEMATISCH · NICHT MASSSTÄBLICH</div>', 18, STH - 46, A("p1", "end", -0.6) + ' data-sfx="none"')
stage.append(f'<div class="el stagewrap" data-in="p1" data-d="-0.6" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px">'
             f'<div id="world">{world_svg}<div id="boatw" class="wpos">{boat_svg}</div><div id="sledw" class="wpos">{sled_svg}</div></div>{labs}{note}</div>')

# ---- Overlays (max. eins gleichzeitig) ----
OY = 1150
def chip_(txt, i, o, col=PURS, sfx="marker", icon="", y=OY, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 20px;border-color:{col};color:{col};background:rgba(255,255,255,.97);font-weight:700">{icon}{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
I.update(scroll='<path d="M10 10h26a5 5 0 0 1 0 10H14v18a5 5 0 0 1-10 0V14a4 4 0 0 1 6-4z"/><path d="M18 26h14M18 32h10"/>',
         bread='<path d="M8 30c0-10 7-16 16-16s16 6 16 16v6H8z"/><path d="M18 20l-3 6M26 18l-2 7M33 21l-3 6"/>',
         jug='<path d="M17 6h14M18 6v6c-6 4-9 10-9 17 0 8 6 13 15 13s15-5 15-13c0-7-3-13-9-17V6"/>',
         drop='<path d="M24 5C17 16 11 23 11 30a13 13 0 0 0 26 0c0-7-6-14-13-25z"/>')
stage.append(chip_("SICHER WEISS ES NIEMAND – ABER VIELES IST WAHRSCHEINLICH", "p2", "p3", PURS, "glass", "", OY, 25, -0.1))
stage.append(el(f'<div class="col" style="align-items:center"><div class="mono" style="font-size:30px;font-weight:800;color:{PURS};background:rgba(255,255,255,.9);padding:2px 10px;border-radius:8px">ÜBER</div>'
                f'<div class="huge2" style="color:{PURS};font-size:150px;letter-spacing:-4px">{cnt(2000000, "p3@zwei", 0, 0)}</div>'
                f'<div class="mono" style="font-size:30px;font-weight:800;color:{PURS};margin-top:2px;background:rgba(255,255,255,.9);padding:2px 10px;border-radius:8px">STEINBLÖCKE</div></div>',
                0, 960, A("p3@zwei", "p4", -0.15) + ' data-sfx="none"', 1080, CENTER))
car = '<path d="M6 30h36v-8l-6-8H16l-6 8H6z" /><circle cx="15" cy="32" r="4"/><circle cx="34" cy="32" r="4"/>'
blk = f'<svg width="150" height="110" viewBox="0 0 150 110"><rect x="8" y="10" width="134" height="92" rx="4" fill="{STONE}" stroke="{PURS}" stroke-width="5"/></svg>'
stage.append(card(f'<div class="row" style="gap:28px;justify-content:center">{blk}<div style="font-family:Unbounded;font-weight:600;font-size:70px;color:{PURS}">≈</div>'
                  f'<div class="row" style="gap:6px">{ic(car, 110, INK, 3)}{ic(car, 110, INK, 3)}</div></div>'
                  f'<div class="mono" style="text-align:center;font-size:26px;font-weight:800;color:{PURS};margin-top:6px">1 BLOCK ≈ 2 AUTOS · IM SCHNITT ETWA 2,3 TONNEN</div>',
                  60, 960, 960, 290, "active", A("p4@Schnitt", "p5", -0.1)))
stage.append(chip_("STEINBRUCH DIREKT NEBEN DER BAUSTELLE", "p5@direkt", "p6", PURS, "none", "", OY, 30))
stage.append(chip_("WEISSE STEINE FÜR DIE GLATTE AUSSENHÜLLE", "p6@Außenhülle", "p7", GR, "marker", "", OY, 28, -0.2))
scr = (f'<svg width="300" height="150" viewBox="0 0 300 150"><rect x="30" y="20" width="240" height="110" fill="#F1E2B8" stroke="{INK}" stroke-width="3"/>'
       f'<rect x="14" y="14" width="24" height="122" rx="12" fill="#E3CD93" stroke="{INK}" stroke-width="3"/><rect x="262" y="14" width="24" height="122" rx="12" fill="#E3CD93" stroke="{INK}" stroke-width="3"/>'
       + "".join(f'<path d="M{x} {y}h{w}" stroke="#7A5530" stroke-width="4" stroke-linecap="round"/>' for x, y, w in [(56, 44, 70), (140, 44, 96), (56, 66, 110), (180, 66, 56), (56, 88, 60), (130, 88, 104), (56, 110, 130)])
       + '</svg>')
stage.append(card(f'<div class="row" style="gap:24px">{scr}<div class="col" style="align-items:flex-start;gap:8px">'
                  f'<div style="font-family:Unbounded;font-weight:600;font-size:40px;color:{PURS}">≈ 4.500 JAHRE</div>'
                  f'<div class="mono" style="font-size:24px;font-weight:800;color:{GR}">PAPYRUS-ROLLEN</div>'
                  f'<div class="mono" style="font-size:24px;font-weight:800;color:{GR}">ARBEITSTAGEBUCH EINES AUFSEHERS</div></div></div>',
                  50, 1000, 980, 230, "active", A("p7@viertausendfünfhundert", "p8", -0.2)))
stage.append(chip_("HOLZSCHLITTEN", "p8@Holzschlitten", "p9", "#7A5530", "marker", "", OY, 32))
bars = (f'<div class="col" style="gap:14px;align-items:stretch;width:100%">'
        f'<div class="row" style="gap:16px"><div class="mono" style="width:270px;font-size:26px;font-weight:800;color:#8A6A12">TROCKENER SAND</div><div class="fbar"><div class="ffill" id="fb1" style="width:470px;background:#D9B44A"></div></div><div class="mono" style="font-size:26px;font-weight:800;color:#8A6A12">100 %</div></div>'
        f'<div class="row" style="gap:16px"><div class="mono" style="width:270px;font-size:26px;font-weight:800;color:{WAT}">FEUCHTER SAND</div><div class="fbar"><div class="ffill" id="fb2" style="width:235px;background:{WAT}"></div></div><div class="mono" style="font-size:26px;font-weight:800;color:{WAT}">≈ 50 %</div></div>'
        f'<div class="mono" style="font-size:20px;font-weight:800;color:#8A8F99;text-align:center">BENÖTIGTE ZUGKRAFT · LABORVERSUCH (FALL ET AL. 2014)</div></div>')
stage.append(card(bars, 40, 1010, 1000, 230, "active", A("p10@halb", "p11", -0.6)))
stage.append(chip_("FORSCHER VERMUTEN: WASSER VOR DEN SCHLITTEN", "p11@Wasser", "p12", WAT, "none", ic(I["drop"], 40, WAT, 3), OY, 26, -0.4))
mini = lambda straight: (f'<svg width="230" height="150" viewBox="0 0 230 150"><path d="M20 140L115 20L210 140Z" fill="{STONE}" stroke="{INK}" stroke-width="3"/>'
                         + (f'<path d="M-10 140L80 64L96 64L40 140Z" fill="#D9B98A" stroke="{INK}" stroke-width="2.6"/>' if straight else
                            f'<path d="M30 132L190 124L162 98L60 92L86 66L140 62L124 44" fill="none" stroke="#B07F4C" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>')
                         + '</svg>')
stage.append(card(f'<div class="row" style="gap:40px;justify-content:center"><div class="col">{mini(True)}<div class="mono" style="font-size:26px;font-weight:800;color:#8A6A12">GERADE?</div></div>'
                  f'<div class="col">{mini(False)}<div class="mono" style="font-size:26px;font-weight:800;color:#8A6A12">SPIRALE?</div></div></div>'
                  f'<div class="mono" style="text-align:center;font-size:22px;font-weight:800;color:#8A8F99;margin-top:4px">FORSCHER STREITEN BIS HEUTE</div>',
                  90, 960, 900, 300, "active", A("p13@gerade", "p14", -0.2)))
stage.append(el(f'<div class="stamp mono" style="font-size:48px;white-space:nowrap;color:#2B2D35;border-color:#2B2D35">KEINE SKLAVEN</div>', 40, OY - 20, A("p14@Sklaven", "p15", -0.1), 1000, CENTER))
stage.append(chip_("LOHN: VOR ALLEM BROT UND BIER", "p15@Lohn", "p16", SAND, "plop", ic(I["bread"], 40, SAND, 3) + ic(I["jug"], 40, SAND, 3), OY, 30))
stage.append(chip_("EIGENE GRÄBER NEBEN DEN PYRAMIDEN", "p16@Gräber", "end", PURS, "glass", "", OY, 30, -0.1))
# Brot/Bier-Pop-ups über dem Dorf (Welt-verankert)
for k, (x, icn) in enumerate([(1940, "bread"), (2090, "jug"), (2240, "bread"), (2420, "jug"), (2580, "bread")]):
    stage[-1] += ""
foodpops = "".join(f'<div class="geo" data-x="{x}" data-y="-130"><div class="food el" {A("p15@Brot" if icn=="bread" else "p15@Bier", "p16@Gräber", 0.08*k)} data-sfx="plop" style="left:-30px;top:-30px">'
                   f'<div style="width:60px;height:60px;border-radius:50%;background:#fff;border:2.5px solid {SAND};display:flex;align-items:center;justify-content:center">{ic(I[icn], 40, SAND, 3)}</div></div></div>'
                   for k, (x, icn) in enumerate([(1940, "bread"), (2090, "jug"), (2240, "bread"), (2420, "jug"), (2580, "bread")]))
stage[[i for i, s_ in enumerate(stage) if 'stagewrap' in s_][0]] = stage[[i for i, s_ in enumerate(stage) if 'stagewrap' in s_][0]].replace(f'{labs}{note}', f'{labs}{foodpops}{note}')

SCENE_JS = r''' // ---- Bühne: Seitenansicht Pyramidenbau ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const sm=u=>u*u*(3-2*u);
  function kf(arr,tt,logi){ const ks=arr.map(k=>({t:TS(k[0],k[1]),v:k.slice(2)})); if(tt<=ks[0].t) return ks[0].v;
    for(let i=0;i<ks.length-1;i++){ const a=ks[i],b=ks[i+1]; if(tt>=a.t&&tt<b.t){ const e=sm((tt-a.t)/Math.max(1e-6,b.t-a.t)); return a.v.map((x,j)=> (j===logi)?Math.exp(Math.log(x)+(Math.log(b.v[j])-Math.log(x))*e):x+(b.v[j]-x)*e); } }
    return ks[ks.length-1].v; }
  const c=kf(PAN.cam,t,2); const cx=c[0], cy=c[1], z=c[2];
  const Wd=document.getElementById('world'); Wd.style.transform=`translate(${540-cx*z}px,${PAN.SYL-cy*z}px) scale(${z})`;
  const pj=(x,y)=>[540+(x-cx)*z, PAN.SYL+(y-cy)*z];
  for(const g of document.querySelectorAll('.geo')){ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }
  const op=(id,v)=>{document.getElementById(id).style.opacity=cl(v,0,1);};
  // Pyramide: fertig (Hook) -> Baustelle -> wieder fertig
  const bIn=pr(t,TS('p5',-0.2),0.4), bOut=ease(pr(t,TS('p13@gerade',0.3),TS('p13@herumwanden',0)-TS('p13@gerade',0.3)));
  const lvl= bIn<1 ? 1-0.57*ease(bIn) : 0.43+0.57*bOut;     // sichtbarer Höhenanteil
  const H=890*lvl; const pcr=document.getElementById('pcr'); pcr.setAttribute('y',(-H).toFixed(1)); pcr.setAttribute('height',(H+2).toFixed(1));
  const cas=Math.max(1-pr(t,TS('p3@zwei',-0.3),0.4), pr(t,TS('p13@herumwanden',0.2),0.6));
  op('casing',cas); op('cshade',cas*0.9); document.getElementById('pgrid').style.opacity=(0.55*(1-cas)).toFixed(3);
  // Baukante oben (flach) während Bau
  const pb=document.getElementById('pbuild'); if(lvl<0.999){ const yy=-H; const hw=700*(1-lvl); pb.setAttribute('d',`M${900-hw} ${yy}H${900+hw}`); pb.style.opacity=1; } else pb.style.opacity=0;
  op('ramp', pr(t,TS('p12',-0.3),0.5)*(1-pr(t,TS('p13@herumwanden',0.3),0.6)));
  // Steinbruch-Block hebt sich
  const qb=document.getElementById('qblock'); const ql=ease(pr(t,TS('p5@Steinbruch',0.2),0.8)); qb.setAttribute('y',(15-60*ql).toFixed(1)); qb.style.opacity=1-pr(t,TS('p8',-0.3),0.3);
  // Boot
  const bw=document.getElementById('boatw'); const bx=kf(PAN.boat,t)[0];   bw.style.left=0; bw.style.top=0; bw.style.transform=`translate(${bx}px,${6+3*Math.sin(t*3)}px)`;
  bw.style.opacity=pr(t,TS('p6',-0.3),0.3)*(1-pr(t,TS('p8',0),0.4));
  document.getElementById('waves').setAttribute('transform',`translate(${(t*30)%140-70},0)`);
  // Schlitten
  const sw_=document.getElementById('sledw'); const sp=kf(PAN.sled,t); const R=PAN.ramp; const onR=sp[0]>R[0][0];
  let sy=sp[1]; let ang=0; if(onR){ const u=(sp[0]-R[0][0])/(R[1][0]-R[0][0]); sy=R[0][1]+(R[1][1]-R[0][1])*Math.min(1,u)+0; ang=Math.atan2(R[1][1]-R[0][1],R[1][0]-R[0][0])*180/Math.PI; }
  const dry=pr(t,TS('p9@trockenen',0.1),0.5)*(1-pr(t,TS('p9@Feuchter',-0.1),0.5)); const sink=10*dry;
  sw_.style.transform=`translate(${sp[0]}px,${sy}px) rotate(${ang}deg)`; sw_.style.opacity=pr(t,TS('p8',-0.3),0.3)*(1-pr(t,TS('p13@gerade',0.6),0.4));
  document.getElementById('sledbody').setAttribute('transform',`translate(0,${sink})`);
  const moving = (t>TS('p8',-0.2)&&t<TS('p13@gerade',0.4));
  document.querySelectorAll('#sledg .wk').forEach((w,k)=>{ const ph=t*7+k*1.3; const a=moving?Math.sin(ph):0;
    w.querySelector('.lg1').setAttribute('transform',`rotate(${18*a} 4 -22)`); w.querySelector('.lg2').setAttribute('transform',`rotate(${-18*a} 4 -22)`);
    w.setAttribute('transform',`translate(0,${moving?-Math.abs(Math.sin(ph))*2:0}) rotate(${moving?-10:0} 0 0)`); });
  // Sandwall vor dem Schlitten (trocken)
  const pile=document.getElementById('pile'); const ph_=12*dry; const px=sp[0]+44;
  pile.setAttribute('d',`M${px} 0 q16 ${-ph_*2} 34 0Z`); pile.style.opacity=dry>0.01&&!onR?1:0;
  // nasser Boden + Wasser gießen
  const wetA=pr(t,TS('p9@Feuchter',-0.1),0.5)*(1-pr(t,TS('p12',0),0.4)); const wet=document.getElementById('wet'); wet.setAttribute('x',(sp[0]-120).toFixed(1)); wet.style.opacity=(0.75*wetA).toFixed(3);
  const po=pr(t,TS('p11@Wasser',-0.4),0.3)*(1-pr(t,TS('p12',0),0.3)); op('pourer',po);
  document.querySelectorAll('#sledg .drop').forEach((d,i)=>{ const ph=((t*1.8+i/8)%1); d.setAttribute('cx',(70+ph*6+i%3).toFixed(1)); d.setAttribute('cy',(-46+ph*46).toFixed(1)); d.style.opacity=po*(ph<0.95?1:0); });
  // Dorf / Gräber
  document.querySelectorAll('.house').forEach((h,i)=>{ const a=pr(t,TS('p14',-0.2+i*0.1),0.35); h.style.opacity=a; h.setAttribute('transform',`translate(0,${(1-ease(a))*20})`); });
  document.querySelectorAll('.grave').forEach((h,i)=>{ const a=pr(t,TS('p16@Gräber',-0.1+i*0.15),0.35); h.style.opacity=a; });
  // Kraft-Balken
  const f1=ease(pr(t,TS('p10@halb',-0.5),0.6)), f2=ease(pr(t,TS('p10@halb',-0.1),0.6));
  document.getElementById('fb1').style.transform=`scaleX(${f1})`; document.getElementById('fb2').style.transform=`scaleX(${f2})`;
 }
'''

# ---- End card (identisch zum Template) ----
logo = open("../brand/out/missionwissen-logo-transparent-dunkel.svg").read()
logo = re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="820" height="253"', logo, count=1)
endcard = f'<div class="el" {A("end",None,0.1)} style="left:130px;top:470px">{logo}</div>' + f'<div class="el" {A("end",None,0.5)} style="left:0;width:1080px;top:790px;display:flex;justify-content:center"><div class="follow">+&nbsp;Folgen</div></div>' + f'<div class="el" {A("end",None,0.7)} style="left:0;width:1080px;top:935px;text-align:center"><div class="mono small grey">JEDEN TAG EIN BISSCHEN SCHLAUER</div></div>'
robots = "".join(f'<div class="pose" data-pose="{n}">{robot_svg("r"+n[:2]+"-", **k)}</div>' for n, k in POSES.items())
mono = '<svg width="72" height="72" viewBox="0 0 80 80" fill="none"><g stroke="#0B0B10" stroke-width="6" stroke-linecap="round"><path d="M20 32 V24 a10 10 0 0 1 20 0 V32 M40 24 a10 10 0 0 1 20 0 V32"/><path d="M20 48 V56 a10 10 0 0 0 20 0 V48 M40 56 a10 10 0 0 0 20 0 V48"/></g><circle cx="40" cy="40" r="3.2" fill="#7B3FE4"/></svg>'

html = f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><style>
@font-face{{font-family:Unbounded;src:url("file://{GF}/unbounded/Unbounded[wght].ttf");font-weight:200 900}}
@font-face{{font-family:Inter;src:url("file://{GF}/inter/Inter[opsz,wght].ttf");font-weight:100 900}}
@font-face{{font-family:JBM;src:url("file://{GF}/jetbrainsmono/JetBrainsMono[wght].ttf");font-weight:100 800}}
*{{box-sizing:border-box}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif;color:#0B0B10}}
#v{{position:relative;width:1080px;height:1920px;overflow:hidden;
background:linear-gradient(rgba(11,11,16,.04) 1px,transparent 1px) 0 0/48px 48px,linear-gradient(90deg,rgba(11,11,16,.04) 1px,transparent 1px) 0 0/48px 48px,linear-gradient(#FFFFFF 40%,#F4F4F6)}}
.mono{{font-family:JBM,monospace;font-weight:500;letter-spacing:.02em}}
.small{{font-size:24px}} .grey{{color:#8A8F99}}
#chap{{position:absolute;left:80px;top:136px;font-size:26px;color:#8A8F99}}
#prog{{position:absolute;left:420px;top:146px;display:flex;gap:10px}}
#prog div{{width:56px;height:6px;border-radius:3px;background:#DDE0E6}}
#prog div.on{{background:#0B0B10}}
#wm{{position:absolute;left:924px;top:112px;opacity:.35}}
#head{{position:absolute;left:80px;top:230px;width:920px;font-family:Unbounded;font-weight:600;font-size:66px;line-height:1.12;letter-spacing:-1.5px}}
.card{{position:absolute;background:rgba(255,255,255,.72);backdrop-filter:blur(16px);border:1px solid rgba(26,31,51,.10);border-radius:22px;
box-shadow:0 8px 18px rgba(26,31,51,.10),0 1.5px 2.5px rgba(26,31,51,.12),inset 0 1.5px 0 rgba(255,255,255,.95);padding:32px}}
.card.active{{border:2px solid #7B3FE4;box-shadow:0 0 24px rgba(123,63,228,.25),0 8px 18px rgba(26,31,51,.10)}}
.card.activeTQ{{border:2px solid #19C6B4;box-shadow:0 0 24px rgba(25,198,180,.3),0 8px 18px rgba(26,31,51,.10)}}
.el{{position:absolute}}
.row{{display:flex;align-items:center}} .col{{display:flex;flex-direction:column;align-items:center}}
.rowtitle{{font-family:Unbounded;font-weight:600;font-size:40px;margin-bottom:8px}}
.rline{{display:flex;justify-content:space-between;padding:18px 24px;border-radius:12px}}
.chip{{font-size:24px;border:2px solid #0B0B10;border-radius:10px;padding:12px 18px;background:rgba(255,255,255,.75)}}
.chip.tq{{border-color:#19C6B4;background:rgba(25,198,180,.12)}} .chip.pu{{border-color:#7B3FE4;background:rgba(123,63,228,.10)}}
.bignum{{font-family:Unbounded;font-weight:600;font-size:110px;letter-spacing:-3px;line-height:1.05}}
.huge{{font-family:Unbounded;font-weight:600;font-size:200px;letter-spacing:-6px;line-height:1}}
.stamp{{font-size:30px;font-weight:700;color:#E5484D;border:3px solid #E5484D;border-radius:12px;padding:12px 22px;transform:rotate(-6deg);background:rgba(255,255,255,.85)}}
.qbig{{position:absolute;font-family:Unbounded;font-weight:600;font-size:220px;color:#7B3FE4}}
.okc{{width:84px;height:84px;flex:none;border-radius:50%;background:#19C6B4;color:#fff;font-size:48px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 0 24px rgba(25,198,180,.45)}}
.cbox{{width:64px;height:64px;flex:none;border-radius:12px;border:3px solid #8A8F99;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:700;color:#fff}}
.cbox.on{{background:#8A8F99}} .cbox.tq{{background:#19C6B4;border-color:#19C6B4;box-shadow:0 0 20px rgba(25,198,180,.45)}}
.mm{{border-radius:22px;border:1px solid rgba(26,31,51,.10);box-shadow:0 8px 18px rgba(26,31,51,.08),inset 0 1.5px 0 rgba(255,255,255,.95);overflow:hidden;
background:linear-gradient(rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(90deg,rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,
linear-gradient(rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,linear-gradient(90deg,rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,#FCFCFD}}
.mk{{display:flex;align-items:center;gap:12px;font-size:22px;white-space:nowrap}} .mkbox{{width:20px;height:20px;border:2.4px solid;display:inline-block}}
.follow{{font-family:Unbounded;font-weight:600;font-size:48px;color:#fff;background:#7B3FE4;border-radius:999px;padding:24px 56px;box-shadow:0 0 30px rgba(123,63,228,.4),0 8px 18px rgba(26,31,51,.15)}}
#robot{{position:absolute;z-index:5;left:40px;top:790px;width:357px;height:500px}}
#robot .pose{{position:absolute;inset:0}} #robot svg{{width:357px;height:500px}}
.eyes{{transform-box:fill-box;transform-origin:center}}
.dot{{width:20px;height:20px;border-radius:50%;background:#7B3FE4;border:3px solid #fff;box-shadow:0 0 12px rgba(123,63,228,.55),0 2px 4px rgba(26,31,51,.25)}}
.pin{{width:22px;height:22px;flex:none;border-radius:50%;border:4px solid #fff;box-shadow:0 0 0 2px rgba(26,31,51,.15),0 2px 6px rgba(26,31,51,.3)}}
.ipin{{width:52px;height:52px;flex:none;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(26,31,51,.25)}}
.lab{{font-size:22px;font-weight:700;background:rgba(255,255,255,.92);border:2px solid;border-radius:8px;padding:4px 10px}}
#tip{{width:0;height:0}} .tipdot{{position:absolute;left:-12px;top:-12px;width:24px;height:24px;border-radius:50%;background:#7B3FE4;border:4px solid #fff;box-shadow:0 0 18px rgba(123,63,228,.8)}}
.tipring{{position:absolute;left:-26px;top:-26px;width:52px;height:52px;border-radius:50%;border:3px solid #7B3FE4}}
#cap{{position:absolute;left:0;width:1080px;top:1300px;display:flex;justify-content:center}}
#pill{{background:rgba(11,11,16,.88);border-radius:16px;padding:14px 24px;font-weight:700;font-size:50px;color:#fff;max-width:920px;text-align:center;line-height:1.2}}
#pill span{{opacity:.45}} #pill span.on{{opacity:1}} #pill span.kw{{color:#B79BFF}} #pill span.kw2{{color:#19C6B4}}
.xx{{position:absolute;left:62px;top:-18px;font-size:66px;color:#E5484D;font-weight:800}}
.spr{{position:absolute;width:5px;height:104px;background:#2B2D35;border-radius:3px;transform:rotate(22deg);transform-origin:bottom}}
.spr2{{position:absolute;left:-60px;top:-3px;width:120px;height:5px;background:#2B2D35;border-radius:3px}}
.spr2::after{{content:"";position:absolute;right:-14px;top:-5px;border-left:16px solid #2B2D35;border-top:7px solid transparent;border-bottom:7px solid transparent}}
.hbar{{position:relative;width:790px;height:30px;border-radius:15px;background:#F0F1F4;overflow:hidden}}
.gbar2{{height:100%;border-radius:15px;transform-origin:left}}
.hlab{{position:absolute;right:14px;top:3px;font-size:18px;font-weight:700;color:#5D616B}}
.star{{position:absolute;border-radius:50%;background:#fff;opacity:0}}
.fdot{{position:absolute;left:-9px;top:-9px;width:18px;height:18px;border-radius:50%;background:#B79BFF;border:3px solid #fff;box-shadow:0 1px 4px rgba(26,31,51,.3)}}
.f1,.f2{{transform-box:fill-box;transform-origin:50% 100%}}
#tod::before{{content:"";display:inline-block;width:12px;height:12px;border-radius:50%;background:#7B3FE4;margin-right:10px;vertical-align:1px}}
.card{{background:rgba(255,255,255,.95)}}
.geo{{width:0;height:0}}
#chap,#prog{{display:none}}
#headbg{{position:absolute;left:0;top:0;width:1080px;height:440px;z-index:2;background:linear-gradient(rgba(255,255,255,.97) 78%,rgba(255,255,255,0))}}
#head{{top:200px;z-index:3}} #wm{{z-index:4}}
.geo{{position:absolute;width:0;height:0}}
.mapwrap{{background:linear-gradient(rgba(11,11,16,.07) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(90deg,rgba(11,11,16,.07) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(rgba(11,11,16,.03) 1px,transparent 1px) 0 0/10px 10px,linear-gradient(90deg,rgba(11,11,16,.03) 1px,transparent 1px) 0 0/10px 10px,#FCFCFD;overflow:hidden}}
.lab{{font-size:26px;font-weight:800;background:rgba(255,255,255,.94);border:2.5px solid;border-radius:8px;padding:5px 12px;white-space:nowrap}}
.note{{font-size:16px;color:#8A8F99;background:rgba(255,255,255,.9);border:1.5px solid #C9CCD3;border-radius:8px;padding:5px 9px;white-space:nowrap}}
#kal{{position:absolute;left:0;top:0;width:300px;transform-origin:150px 160px;z-index:2}}
.kal{{width:300px;background:#fff;border:3px solid #7B3FE4;border-radius:22px;overflow:hidden;text-align:center;padding-bottom:16px;box-shadow:0 10px 26px rgba(26,31,51,.18),0 2px 4px rgba(26,31,51,.12);display:flex;flex-direction:column;align-items:center}}
.kalh{{width:100%;background:#7B3FE4;color:#fff;font-size:30px;font-weight:800;padding:10px 0;letter-spacing:.14em}}
.kald{{font-family:Unbounded;font-weight:600;font-size:130px;line-height:1.08;color:#0B0B10}}
.kaly{{font-family:Unbounded;font-weight:600;font-size:76px;line-height:1;color:#7B3FE4;letter-spacing:-2px;transform-origin:50% 50%}}
.krow{{font-family:JBM,monospace;font-size:22px;font-weight:800;border:2px solid;border-radius:8px;padding:5px 10px;white-space:nowrap}}
.huge2{{font-family:Unbounded;font-weight:600;font-size:190px;letter-spacing:-6px;line-height:1;color:#2B2D35;text-shadow:0 0 20px #fff,0 0 10px #fff}}
.ppl{{position:absolute;width:20px;height:20px;margin:-10px 0 0 -10px;border-radius:50%;border:3px solid #fff;box-shadow:0 1px 4px rgba(26,31,51,.35)}}
#world{{position:absolute;left:0;top:0;transform-origin:0 0}}
.wpos{{position:absolute;left:0;top:0}}
.stagewrap{{background:linear-gradient(rgba(11,11,16,.06) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(90deg,rgba(11,11,16,.06) 1px,transparent 1px) 0 0/50px 50px,#FCFCFD;overflow:hidden}}
.fbar{{width:470px;height:34px;background:#F0F1F4;border-radius:10px;overflow:hidden;flex:none}}
.ffill{{height:100%;transform-origin:left;border-radius:10px}}
.geo{{z-index:4000}}
</style></head><body><div id="v">
<div id="chap" class="mono"></div><div id="prog">{"".join("<div></div>" for _ in CH)}</div><div id="wm">{mono}</div>
<div id="headbg"></div><div id="head"></div>
{"".join(stage)}
{endcard}
<div id="robot">{robots}</div>
<div id="cap"><div id="pill"></div></div>
</div>
<script>
const PAN={json.dumps(PANJS, ensure_ascii=False)};
const BEATS={json.dumps(beats, ensure_ascii=False)};
const S={json.dumps(S, ensure_ascii=False)}; const CH={json.dumps(CH, ensure_ascii=False)}; const END={END:.3f}; const AUD={AUD:.3f};
const cl=(x,a,b)=>Math.max(a,Math.min(b,x)); const ease=p=>1-Math.pow(1-p,3); const pr=(t,t0,d)=>cl((t-t0)/d,0,1);
const els=[...document.querySelectorAll('[data-in]')];
function beatAt(t){{let b=BEATS[0];for(const x of BEATS) if(t>=x.s) b=x; return b;}}
window.render=function(t){{
 const end=t>=END; const b=beatAt(t);
 document.getElementById('chap').textContent=CH[b.ch];
 [...document.querySelectorAll('#prog div')].forEach((d,i)=>d.className=i<=b.ch?'on':'');
 const top=cl(1-pr(t,END,.3),0,1); ['chap','prog','head'].forEach(id=>document.getElementById(id).style.opacity=top); document.getElementById('headbg').style.opacity=1-pr(t,S['p3']-0.2,0.5); document.getElementById('head').style.opacity=top*(1-pr(t,S['n4']-0.2,0.3));
 let hs=b.s; for(let i=BEATS.indexOf(b);i>0&&BEATS[i-1].head===b.head;i--) hs=BEATS[i-1].s;
 const H=document.getElementById('head'); H.innerHTML=b.head; H.style.fontSize='62px'; if(BEATS.indexOf(b)===0) hs=-1; const hp=ease(pr(t,hs,.3));
 const g=Math.round(181+(11-181)*hp), g2=Math.round(184+(11-184)*hp), g3=Math.round(192+(16-192)*hp); H.style.color=`rgb(${{g}},${{g2}},${{g3}})`;
 // elements
 for(const e of els){{
  const tin=(S[e.dataset.in]??(console.log('missing '+e.dataset.in),0))+(+e.dataset.d||0); const tout=e.dataset.out?S[e.dataset.out]:1e9;
  const pi=ease(pr(t,tin,.35)), po=pr(t,tout,.2);
  e.style.opacity=pi*(1-po); e.style.transform=`translateY(${{16*(1-pi)}}px)`;
 }}
 // counters
 for(const c of document.querySelectorAll('.count')){{const t0=(S[c.dataset.cin]??0)+(+c.dataset.cd||0); const dd=+c.dataset.dec||0; const v=+c.dataset.count*ease(pr(t,t0,0.8)); c.textContent=(dd===0&&+c.dataset.count>=1000)?Math.round(v).toLocaleString('de-DE'):v.toFixed(dd).replace('.',',');}}
 // sketches
 for(const sk of document.querySelectorAll('.sketch')){{const t0=(S[sk.dataset.sin]??0)+(+sk.dataset.sd||0); const p=ease(pr(t,t0,+sk.dataset.sdur||1.5)); sk.querySelectorAll('.ink').forEach(e=>e.style.strokeDashoffset=1-p); sk.querySelectorAll('.mesh').forEach(e=>e.style.opacity=pr(t,t0+(+sk.dataset.sdur||1.5)*0.6,0.6));}}
/*SCENEJS*/
 // robot
 let pose=b.pose; if(end) pose='winkt';
 const R=document.getElementById('robot');
 let rop=0; if(pose&&!end){{const prevHad=BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose; rop=prevHad?1:ease(pr(t,b.s,.3)); const nb=BEATS[BEATS.indexOf(b)+1]; if(nb&&!nb.pose) rop*=1-pr(t,nb.s-0.2,.2); if(!nb) rop*=1-pr(t,END-0.2,.2);}}
 if(end){{rop=ease(pr(t,END+0.3,.35));}}
 R.style.opacity=rop; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');
 let prevPose=null; const bi=BEATS.indexOf(b); if(bi>0) prevPose=BEATS[bi-1].pose; const pf=pr(t,b.s,.15);
 for(const p of R.querySelectorAll('.pose')){{const n=p.dataset.pose; p.style.opacity=end?(n==='winkt'?1:0):(n===pose?pf:(n===prevPose&&prevPose!==pose?1-pf:0)); if(pose===prevPose&&n===pose) p.style.opacity=1;}}
 const bl=(t%3.7); const sy=bl<0.12?0.2:1; R.querySelectorAll('.eyes').forEach(e=>e.style.transform=`scaleY(${{sy}})`);
 R.querySelectorAll('.pulse').forEach(e=>e.setAttribute('opacity',0.3+0.1*Math.sin(t*2*Math.PI/1.8)));
 // captions
 const P=document.getElementById('pill'); const W=b.words; let wi=0; W.forEach((w,i)=>{{if(t>=w[1]) wi=i;}});
 const cid=W[wi][3]; P.innerHTML=W.map((w,i)=>[w,i]).filter(x=>x[0][3]===cid).map(([w,i])=>`<span class="${{i<=wi?'on':''}} ${{w[2]?(b.ch%2?'kw2':'kw'):''}}">${{w[0]}}</span>`).join(' ');
 document.getElementById('cap').style.opacity=t<AUD+0.3?1:1-pr(t,AUD+0.3,.3);
}};
render(0);
</script></body></html>'''
html = html.replace('/*SCENEJS*/', SCENE_JS)
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))
