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
CH = [""]
HOOK = '<div class="mono" style="display:inline-block;font-family:JBM;font-size:28px;font-weight:800;letter-spacing:.02em;color:#7B3FE4;background:#F1EBFD;border:2px solid #7B3FE4;border-radius:10px;padding:6px 14px;margin-bottom:14px">MEGA-PROJEKTE · FOLGE 2</div><br>Die größte <span style="color:#7B3FE4">Maschine</span> der Welt – vom Mond gedehnt?'
B = [
 ("b1", 0, HOOK, "Die *größte* *Maschine* der Welt wird vom *Mond* *gedehnt.*", "staunt"),
 ("b2", 0, HOOK, "Wie kann das *sein?*", "denkt"),
 ("b3", 0, "", "Die Maschine ist ein *Ring,* *27* *Kilometer* lang, rund *100* *Meter* unter der Erde.", None),
 ("b4", 0, "", "Er liegt an der Grenze zwischen der *Schweiz* und *Frankreich,* am Forschungszentrum *CERN.*", None),
 ("b5", 0, "", "Es ist ein *Teilchenbeschleuniger.*", None),
 ("b6", 0, "", "Er bringt *Protonen,* winzige Bausteine von Atomen, fast auf *Lichtgeschwindigkeit.*", None),
 ("b7", 0, "", "Über *11.000* *Mal* pro *Sekunde* fliegen sie einmal ganz um den Ring.", None),
 ("b8", 0, "", "Damit sie in der *Kurve* bleiben, lenken über *1.200* riesige *Magnete* sie.", None),
 ("b9", 0, "", "Diese Magnete werden auf *minus* *271* *Grad* gekühlt, *kälter* als im *Weltall.*", None),
 ("b10", 0, "", "Nur so fließt der *Strom* in ihnen *ohne* *Verlust,* und sie werden *stark* genug.", None),
 ("b11", 0, "", "*Zwei* *Teilchenstrahlen* rasen in *entgegengesetzte* Richtungen.", None),
 ("b12", 0, "", "An *vier* *Stellen* lässt man sie *frontal* *zusammenprallen.*", None),
 ("b13", 0, "", "Aus der *Wucht* des Aufpralls entstehen für einen winzigen Moment ganz *neue* *Teilchen.*", None),
 ("b14", 0, "", "So wollen Forscher herausfinden, woraus unsere *Welt* *besteht.*", None),
 ("b15", 0, "", "*2012* haben sie so das berühmte *Higgs-Teilchen* entdeckt.", None),
 ("b16", 0, "", "Und der *Mond?*", None),
 ("b17", 0, "", "Er zieht nicht nur am *Meer,* sondern auch am festen *Boden.*", None),
 ("b18", 0, "", "Der Boden *wölbt* sich dabei um bis zu *25* *Zentimeter.*", None),
 ("b19", 0, "", "Der Ring wölbt sich mit und wird dabei *gedehnt* und wieder *gestaucht,* um etwa *einen* *Millimeter.*", None),
 ("b20", 0, "", "Klingt nach *nichts.*", None),
 ("b21", 0, "", "Aber die *Magnete* rücken dadurch ein winziges Stück *auseinander.*", None),
 ("b22", 0, "", "Die Teilchen fliegen nicht mehr genau *mittig* hindurch, und ihre *Energie* ändert sich ein kleines bisschen.", None),
 ("b23", 0, "", "Die Forscher müssen aber *genau* wissen, mit welcher *Wucht* die Teilchen zusammenprallen.", None),
 ("b24", 0, "", "Deshalb wird die Maschine laufend *nachgeregelt,* damit die Teilchen in der *Mitte* bleiben.", None),
 ("b25", 0, "", "Übrigens: Als der Ring *2008* startete, hatten viele *Angst,* er könnte ein *schwarzes* *Loch* erzeugen.", None),
 ("b26", 0, "", "Doch aus dem *Weltall* prasseln seit *Milliarden* *Jahren* Teilchen mit noch *mehr* *Wucht* auf die Erde.", None),
 ("b27", 0, "", "Und die *Erde* gibt es *immer* *noch.*", None),
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



# ================= Bühne: 4 Ebenen (Karte, Querschnitt, Magnet-Nahansicht, Erde+Mond) mit Kameraflügen =================
import math, random
CENTER = "display:flex;justify-content:center"
PW, PH = 1080, 880; PTOP = 400
LIL = "#7B3FE4"; LIL2 = "#B79BFF"; WAT = "#19C6B4"; GRD = "#F3F0EA"
RCX, RCY, RR = 600, 450, 250   # Ring in der Karte

def layer(lid, inner, defs=""):
    return (f'<div id="L{lid}" class="lay" style="position:absolute;inset:0;opacity:0;transform-origin:540px 440px">'
            f'<svg width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" style="position:absolute;left:0;top:0;overflow:hidden">'
            f'<defs>{defs}</defs><g id="{lid}cam">{inner}</g></svg></div>')

GDEF = (f'<radialGradient id="glw"><stop offset="0" stop-color="{LIL}" stop-opacity=".55"/><stop offset="1" stop-color="{LIL}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="glt"><stop offset="0" stop-color="{WAT}" stop-opacity=".55"/><stop offset="1" stop-color="{WAT}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="glb"><stop offset="0" stop-color="#FFD84A" stop-opacity=".95"/><stop offset=".4" stop-color="#FF9F3D" stop-opacity=".6"/><stop offset="1" stop-color="#FF9F3D" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="moonG" cx=".35" cy=".3"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#C9CDD5"/></radialGradient>'
        f'<radialGradient id="bh"><stop offset="0" stop-color="#0B0B10"/><stop offset=".55" stop-color="#0B0B10"/><stop offset="1" stop-color="#0B0B10" stop-opacity="0"/></radialGradient>'
        f'<pattern id="hat" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="9" stroke="#B9B2A3" stroke-width="1.3"/></pattern>'
        f'<pattern id="hat2" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(-30)"><line x1="0" y1="0" x2="0" y2="12" stroke="#C9C2B3" stroke-width="1.2"/></pattern>')

def moon(cx, cy, r, mid):
    return (f'<g id="{mid}"><circle cx="{cx}" cy="{cy}" r="{r*1.6:.0f}" fill="url(#glw)" opacity=".25"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#moonG)" stroke="#2B2D35" stroke-width="3"/>'
            f'<circle cx="{cx-r*.3:.1f}" cy="{cy-r*.2:.1f}" r="{r*.18:.1f}" fill="#B9BEC8"/><circle cx="{cx+r*.28:.1f}" cy="{cy+r*.25:.1f}" r="{r*.12:.1f}" fill="#B9BEC8"/>'
            f'<circle cx="{cx+r*.1:.1f}" cy="{cy-r*.45:.1f}" r="{r*.08:.1f}" fill="#B9BEC8"/></g>')

def pt(a, r=RR):
    return RCX + r * math.cos(math.radians(a)), RCY + r * math.sin(math.radians(a))

# ---------------- Ebene M: Karte (Draufsicht, schematisch) ----------------
M = []
# Jura (Gebirge oben links), See (unten rechts), Rhône
M.append(f'<path d="M-200 -200 L560 -200 L470 40 L330 120 L150 230 L-60 330 L-200 380 Z" fill="url(#hat)" opacity=".5"/>'
         f'<path d="M-200 380 L-60 330 L150 230 L330 120 L470 40 L560 -200" fill="none" stroke="#A9AEB8" stroke-width="2.5" stroke-dasharray="3 7"/>'
         f'<text x="120" y="120" font-family="JBM" font-weight="800" font-size="22" fill="#A9AEB8" transform="rotate(-28 120 120)">JURA</text>')
M.append(f'<path id="lake" d="M905 760 C960 700 1040 650 1150 600 L1350 560 L1350 1100 L1050 1100 C1000 960 960 860 905 760 Z" fill="{WAT}" fill-opacity=".28" stroke="{WAT}" stroke-width="3"/>'
         f'<path d="M905 760 C860 740 820 760 760 800 C700 840 640 880 560 960" fill="none" stroke="{WAT}" stroke-width="5" stroke-linecap="round" opacity=".7"/>'
         f'<text x="1010" y="820" font-family="JBM" font-weight="800" font-size="22" fill="#0E9C8E">GENFER SEE</text>')
# Grenze CH/FR (schematisch: Kanton Genf als Ausbuchtung)
BORDER = "M-150 640 C120 620 300 610 430 560 C540 520 610 470 690 520 C760 565 790 650 860 640 C930 630 990 560 1010 470 C1030 380 1120 330 1300 300"
M.append(f'<path id="border" d="{BORDER}" fill="none" stroke="#E5484D" stroke-width="4" stroke-dasharray="14 10" pathLength="1" opacity="0"/>')
M.append(f'<g id="cty" opacity="0"><text x="190" y="250" font-family="JBM" font-weight="800" font-size="34" fill="#2B2D35" text-anchor="middle">🇫🇷 FRANKREICH</text>'
         f'<text x="1000" y="905" font-family="JBM" font-weight="800" font-size="34" fill="#2B2D35" text-anchor="middle">🇨🇭 SCHWEIZ</text>'
         f'<circle cx="905" cy="760" r="9" fill="#2B2D35"/><text x="890" y="800" font-family="JBM" font-weight="800" font-size="22" fill="#2B2D35" text-anchor="end">GENF</text></g>')
# Ring
M.append(f'<circle cx="{RCX}" cy="{RCY}" r="{RR+40}" fill="url(#glw)" opacity="0" id="ringglow"/>')
M.append(f'<g id="ringg"><circle id="ring0" cx="{RCX}" cy="{RCY}" r="{RR}" fill="none" stroke="#2B2D35" stroke-width="20"/>'
         f'<circle id="ring1" cx="{RCX}" cy="{RCY}" r="{RR}" fill="none" stroke="{LIL}" stroke-width="13"/>'
         f'<circle id="ringrun" cx="{RCX}" cy="{RCY}" r="{RR}" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="18 26" opacity=".85"/>'
         f'<ellipse id="ringghost" cx="{RCX}" cy="{RCY}" rx="{RR}" ry="{RR}" fill="none" stroke="#8A8F99" stroke-width="3" stroke-dasharray="8 8" opacity="0"/>'
         + "".join(f'<circle class="pa" r="9" fill="{LIL}" stroke="#fff" stroke-width="3" data-k="{k}"/>' for k in range(6))
         + "".join(f'<circle class="pb" r="9" fill="{WAT}" stroke="#fff" stroke-width="3" data-k="{k}"/>' for k in range(6))
         + f'<g id="hero"><circle r="34" fill="url(#glw)"/><circle r="15" fill="{LIL}" stroke="#fff" stroke-width="4"/><text y="7" text-anchor="middle" font-family="JBM" font-weight="800" font-size="17" fill="#fff">p⁺</text></g>'
         + '</g>')
EXP = [("ATLAS", 110), ("ALICE", 200), ("CMS", 290), ("LHCb", 20)]
ex = []
for k, (n, a) in enumerate(EXP):
    x, y = pt(a); lx, ly = pt(a, RR + 58)
    ex.append(f'<g class="exp" data-k="{k}"><circle class="exr" cx="{x:.1f}" cy="{y:.1f}" r="22" fill="none" stroke="#FFB020" stroke-width="5"/>'
              f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#FFB020" stroke="#2B2D35" stroke-width="3"/>'
              f'<text x="{lx:.1f}" y="{ly+8:.1f}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="24" fill="#2B2D35">{n}</text></g>')
M.append(f'<g id="exps" opacity="0">{"".join(ex)}</g>')
cx_, cy_ = pt(110)
M.append(f'<g id="cern" opacity="0"><rect x="{cx_+24:.0f}" y="{cy_-6:.0f}" width="96" height="40" rx="8" fill="#fff" stroke="#2B2D35" stroke-width="3"/>'
         f'<text x="{cx_+72:.0f}" y="{cy_+22:.0f}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="22" fill="{LIL}">CERN</text></g>')
# Kollisions-Explosion bei ATLAS
rnd = random.Random(7)
trk = []
for k in range(26):
    a = rnd.uniform(0, 360); L = rnd.uniform(40, 120); cv = rnd.uniform(-40, 40)
    x2 = cx_ + L * math.cos(math.radians(a)); y2 = cy_ + L * math.sin(math.radians(a))
    mx = (cx_ + x2) / 2 + cv * math.cos(math.radians(a + 90)); my = (cy_ + y2) / 2 + cv * math.sin(math.radians(a + 90))
    col = [LIL, WAT, "#FFB020", "#E5484D", "#2B2D35"][k % 5]
    trk.append(f'<path class="trk" d="M{cx_:.1f} {cy_:.1f} Q{mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}" stroke="{col}" stroke-width="2.6" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" stroke-linecap="round"/>')
M.append(f'<g id="burst" opacity="0"><circle id="flash" cx="{cx_:.1f}" cy="{cy_:.1f}" r="60" fill="url(#glb)"/>{"".join(trk)}'
         f'<g id="higgs" opacity="0"><circle cx="{cx_+70:.1f}" cy="{cy_-70:.1f}" r="16" fill="#FFB020" stroke="#2B2D35" stroke-width="3"/><text x="{cx_+70:.1f}" y="{cy_-63:.1f}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="18">H</text></g></g>')
# Mond (Hook) + Zugpfeile
M.append(moon(960, 120, 62, "mmoon"))
M.append(f'<g id="pull" opacity="0">' + "".join(f'<path class="pl" d="M{900-k*40} {150+k*28} l-46 30" stroke="{LIL}" stroke-width="5" stroke-linecap="round" fill="none" marker-end="url(#ah)"/>' for k in range(3)) + '</g>')
# Schwarzes Loch
M.append(f'<g id="bhole" opacity="0" transform="translate({RCX} {RCY})"><circle r="95" fill="url(#bh)"/>'
         + "".join(f'<path class="sw" d="M{r} 0 A{r} {r*.55:.0f} 0 1 1 {-r} 0" fill="none" stroke="{LIL2}" stroke-width="4" stroke-linecap="round" stroke-dasharray="30 22"/>' for r in (70, 110, 150))
         + f'<text id="bhq" y="22" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="70" fill="#fff">?</text></g>')
M.append(f'<text id="mnote" x="30" y="860" font-family="JBM" font-weight="700" font-size="17" fill="#8A8F99" opacity="0">STARK ÜBERTRIEBEN</text>')
AH = f'<marker id="ah" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="{LIL}"/></marker>'
LM = layer("m", "".join(M), GDEF + AH)

# ---------------- Ebene C: Querschnitt (Seitenansicht) ----------------
C = []
C.append(f'<g id="csky"><circle cx="980" cy="70" r="0"/></g>')
C.append(moon(960, 90, 50, "cmoon"))
C.append(f'<g id="cground"><path d="M-300 330 L120 330 L190 250 L260 300 L330 210 L420 290 L520 330 L1400 330 L1400 1200 L-300 1200 Z" fill="{GRD}" stroke="#2B2D35" stroke-width="3.2" stroke-linejoin="round"/>'
         f'<path d="M-300 330 L120 330 L190 250 L260 300 L330 210 L420 290 L520 330 L1400 330 L1400 1200 L-300 1200 Z" fill="url(#hat2)" opacity=".7"/>'
         f'<path d="M-300 470 C100 455 500 490 1400 465 M-300 600 C200 590 600 615 1400 595 M-300 760 C200 750 700 775 1400 755" stroke="#C9C2B3" stroke-width="2" fill="none"/>'
         + "".join(f'<g transform="translate({x} 330)"><rect x="-16" y="-30" width="32" height="30" fill="#fff" stroke="#2B2D35" stroke-width="2.4"/><path d="M-22 -30 L0 -48 L22 -30 Z" fill="#E8E1D3" stroke="#2B2D35" stroke-width="2.4" stroke-linejoin="round"/></g>' for x in (620, 680, 760, 900, 960))
         + "".join(f'<g transform="translate({x} 330)"><line x1="0" y1="0" x2="0" y2="-26" stroke="#2B2D35" stroke-width="3"/><circle cy="-36" r="16" fill="#CDEBD8" stroke="#2B2D35" stroke-width="2.4"/></g>' for x in (560, 820, 1040, 60, -20))
         + f'<g id="tun"><circle cx="540" cy="680" r="62" fill="#fff" stroke="#2B2D35" stroke-width="4"/>'
         f'<circle cx="522" cy="680" r="14" fill="#E9E4F9" stroke="{LIL}" stroke-width="4"/><circle cx="558" cy="680" r="14" fill="#DDF5F2" stroke="{WAT}" stroke-width="4"/>'
         f'<circle cx="522" cy="680" r="5" fill="{LIL}"/><circle cx="558" cy="680" r="5" fill="{WAT}"/>'
         f'<rect x="490" y="732" width="100" height="8" rx="4" fill="#8A8F99"/></g>'
         f'<g id="depth" opacity="0"><line x1="660" y1="336" x2="660" y2="614" stroke="{LIL}" stroke-width="5"/><path d="M660 334 l-11 20 h22 z M660 616 l-11 -20 h22 z" fill="{LIL}"/>'
         f'<rect x="684" y="440" width="190" height="62" rx="12" fill="#fff" stroke="{LIL}" stroke-width="3"/><text x="779" y="483" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="34" fill="{LIL}">≈ 100 M</text></g>'
         f'<text x="540" y="790" text-anchor="middle" font-family="JBM" font-weight="800" font-size="22" fill="#2B2D35">TUNNEL MIT 2 STRAHLROHREN</text></g>')
C.append(f'<path id="cbase" d="M-300 330 L120 330 L190 250 L260 300 L330 210 L420 290 L520 330 L1400 330" fill="none" stroke="#8A8F99" stroke-width="3" stroke-dasharray="10 8" opacity="0"/>')
C.append(f'<g id="cpull" opacity="0">' + "".join(f'<path d="M{760+k*120} 300 l60 -70" stroke="{LIL}" stroke-width="6" stroke-linecap="round" fill="none" marker-end="url(#ah2)"/>' for k in range(3)) + '</g>')
C.append(f'<text id="cnote" x="30" y="860" font-family="JBM" font-weight="700" font-size="17" fill="#8A8F99">SCHEMATISCH · NICHT MASSSTÄBLICH</text>')
AH2 = f'<marker id="ah2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="{LIL}"/></marker>'
LC = layer("c", "".join(C), GDEF + AH2)

# ---------------- Ebene G: Magnet-Nahansicht (Draufsicht auf Tunnelstück) ----------------
G = []
ACX, ACY, AR = 540, 1900, 1500   # großer Kreisbogen
G.append(f'<path id="tband" d="M{ACX-AR} {ACY} A{AR} {AR} 0 0 1 {ACX+AR} {ACY}" fill="none" stroke="#ECEEF2" stroke-width="210"/>'
         f'<path d="M{ACX-AR-105} {ACY} A{AR+105} {AR+105} 0 0 1 {ACX+AR+105} {ACY}" fill="none" stroke="#2B2D35" stroke-width="3"/>'
         f'<path d="M{ACX-AR+105} {ACY} A{AR-105} {AR-105} 0 0 1 {ACX+AR-105} {ACY}" fill="none" stroke="#2B2D35" stroke-width="3"/>')
G.append('<g id="mags"></g>')
G.append(f'<path id="ideal" d="M{ACX-AR} {ACY} A{AR} {AR} 0 0 1 {ACX+AR} {ACY}" fill="none" stroke="#8A8F99" stroke-width="3" stroke-dasharray="10 10"/>')
G.append(f'<path id="ppath" fill="none" stroke="{LIL}" stroke-width="5" stroke-linecap="round" opacity=".9"/>')
G.append(f'<g id="ghero"><circle r="40" fill="url(#glw)"/><circle r="17" fill="{LIL}" stroke="#fff" stroke-width="4"/><text y="7" text-anchor="middle" font-family="JBM" font-weight="800" font-size="18" fill="#fff">p⁺</text></g>')
G.append('<g id="frost" opacity="0">' + "".join(f'<path class="fr" d="M0 -9 V9 M-8 -4.5 L8 4.5 M-8 4.5 L8 -4.5" stroke="#7FD6F0" stroke-width="2.4" stroke-linecap="round"/>' for _ in range(22)) + '</g>')
G.append(f'<text id="gnote" x="30" y="860" font-family="JBM" font-weight="700" font-size="17" fill="#8A8F99">SCHEMATISCH</text>')
G.append(f'<g id="knob" opacity="0" transform="translate(940 230)"><circle r="56" fill="#fff" stroke="#2B2D35" stroke-width="4"/><g id="knobi"><line x1="0" y1="0" x2="0" y2="-42" stroke="{LIL}" stroke-width="8" stroke-linecap="round"/></g>'
         f'<circle r="8" fill="#2B2D35"/><text y="88" text-anchor="middle" font-family="JBM" font-weight="800" font-size="20" fill="#2B2D35">NACHREGELN</text></g>')
LG = layer("g", "".join(G), GDEF)

# ---------------- Ebene E: Erde + Mond ----------------
E = []
E.append(f'<g id="rays" opacity="0">' + "".join(f'<line class="ray" data-k="{k}" stroke="{["#FFB020", LIL2, WAT][k % 3]}" stroke-width="4" stroke-linecap="round"/>' for k in range(30)) + '</g>')
E.append(f'<ellipse id="ebulge" cx="440" cy="470" rx="250" ry="250" fill="{WAT}" fill-opacity=".25" stroke="{WAT}" stroke-width="3"/>')
E.append(f'<circle cx="440" cy="470" r="230" fill="#EAF7F5" stroke="#2B2D35" stroke-width="4"/>')
E.append(f'<g id="conts" fill="#F3F0EA" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round">'
         f'<path d="M330 300 C380 270 450 280 470 320 C490 360 450 380 420 400 C400 430 360 420 340 390 C320 360 300 330 330 300 Z"/>'
         f'<path d="M430 420 C480 410 520 440 520 500 C520 560 490 620 450 640 C420 620 410 560 400 520 C390 480 400 430 430 420 Z"/>'
         f'<path d="M520 300 C580 280 640 320 640 380 C620 420 580 410 550 400 C520 380 500 330 520 300 Z"/>'
         f'<path d="M260 470 C290 450 320 480 310 520 C300 560 270 570 250 540 C240 510 240 480 260 470 Z"/></g>')
E.append(f'<ellipse id="gbulge" cx="440" cy="470" rx="230" ry="230" fill="none" stroke="{LIL}" stroke-width="5" stroke-dasharray="14 9"/>')
E.append(f'<g id="eloc"><circle cx="425" cy="318" r="12" fill="none" stroke="{LIL}" stroke-width="5"/><circle cx="425" cy="318" r="4" fill="{LIL}"/></g>')
E.append(moon(920, 470, 70, "emoon"))
E.append(f'<g id="elab" opacity="0"><text x="440" y="760" text-anchor="middle" font-family="JBM" font-weight="800" font-size="24" fill="#0E9C8E">MEER: EBBE &amp; FLUT</text>'
         f'<text x="440" y="796" text-anchor="middle" font-family="JBM" font-weight="800" font-size="24" fill="{LIL}">BODEN: AUCH!</text></g>')
E.append(f'<g id="eok" opacity="0"><circle cx="440" cy="470" r="260" fill="none" stroke="{WAT}" stroke-width="8"/></g>')
E.append(f'<text id="enote" x="30" y="860" font-family="JBM" font-weight="700" font-size="17" fill="#8A8F99">SCHEMATISCH · STARK ÜBERTRIEBEN</text>')
LE = layer("e", "".join(E), GDEF)

panel = LM + LC + LG + LE
stage.append(f'<div class="mm el" {A("b1", "end", -1)} data-sfx="none" style="left:0;top:{PTOP}px;width:{PW}px;height:{PH}px;border-radius:0;border-left:0;border-right:0;overflow:hidden">{panel}</div>')

# ---- Overlays (Bildschirm-Ebene, höchstens eins gleichzeitig) ----
def chip(text, y, i, o, d=0.0, col=LIL, sfx="pop"):
    stage.append(el(f'<div class="chip mono" style="font-size:32px;padding:12px 22px;font-weight:800;background:#fff;border-color:{col};color:{col}">{text}</div>', 0, y, A(i, o, d) + f' data-sfx="{sfx}"', 1080, CENTER))
def big(inner, y, i, o, d=0.0, sfx="pop", size=150, sub=None):
    s = f'<div class="mono" style="font-size:28px;font-weight:800;text-align:center;color:#5D616B;letter-spacing:.02em">{sub}</div>' if sub else ""
    stage.append(el(f'<div style="background:rgba(255,255,255,.82);border-radius:24px;padding:4px 26px 10px"><div class="num" style="font-size:{size}px;text-align:center;white-space:nowrap">{inner}</div>{s}</div>', 0, y, A(i, o, d) + f' data-sfx="{sfx}"', 1080, CENTER))
def stampg(text, y, i, o, d=0.0, size=52):
    stage.append(el(f'<div class="stamp mono" style="font-size:{size}px;color:{WAT};border-color:{WAT}">{text}</div>', 0, y, A(i, o, d), 1080, CENTER))

big(f'{cnt(27, "b3@27", 0, -0.25)}<span style="font-size:80px"> KM</span>', 410, "b3@27", "b3@100", -0.3, "none", 160, "UMFANG DES RINGS")
chip("⚛️ TEILCHENBESCHLEUNIGER", 1180, "b5", "b6", -0.1)
chip("p⁺ PROTON · BAUSTEIN VON ATOMEN", 1180, "b6@Protonen", "b6@fast", -0.1, LIL)
chip("⚡ FAST LICHTGESCHWINDIGKEIT", 1180, "b6@fast", "b7", 0.0, INK)
big(f'<span style="font-size:60px">ÜBER </span>{cnt(11000, "b7@11000", 0, -0.2)}', 410, "b7@11000", "b8", -0.3, "none", 140, "RUNDEN PRO SEKUNDE")
big(f'<span style="font-size:60px">ÜBER </span>{cnt(1200, "b8@1200", 0, -0.2)}', 410, "b8@1200", "b9", -0.3, "none", 140, "RIESIGE MAGNETE")
big('<span id="temp">0</span><span style="font-size:80px"> °C</span>', 410, "b9@minus", "b10", -0.3, "none", 150, '<span id="tsub" style="opacity:0">KÄLTER ALS IM WELTALL (≈ −270 °C)</span>')
chip("⚡ STROM FLIESST OHNE VERLUST", 1180, "b10@Strom", "b11", -0.1, WAT)
chip("⇄ ZWEI STRAHLEN · GEGENRICHTUNG", 1180, "b11", "b12", 0.0, INK)
chip("💥 4 STELLEN · FRONTALER AUFPRALL", 1180, "b12@vier", "b13", -0.1, "#C77700")
chip("✨ FÜR EINEN MOMENT: NEUE TEILCHEN", 1180, "b13@neue", "b14", -0.3, LIL)
chip("❓ WORAUS BESTEHT UNSERE WELT?", 1180, "b14", "b15", 0.1, INK)
stampg("✓ HIGGS-TEILCHEN · 2012", 1130, "b15", "b16", 0.0, 50)
big(f'<span style="font-size:60px">BIS ZU </span>{cnt(25, "b18@25", 0, -0.2)}<span style="font-size:70px"> CM</span>', 410, "b18@25", "b19", -0.3, "none", 150, "SO STARK WÖLBT SICH DER BODEN")
big('<span style="font-size:110px">≈ 1 MM</span>', 410, "b19@einen", "b21", -0.4, "pop", 150, "LÄNGER ODER KÜRZER · BEI 27 KM")
chip("↔ MAGNETE RÜCKEN AUSEINANDER", 1180, "b21", "b22", 0.1, LIL)
gauge = (f'<div class="gcard" style="padding:12px 26px"><svg width="300" height="170" viewBox="-150 -140 300 170">'
         f'<path d="M-120 0 A120 120 0 0 1 120 0" fill="none" stroke="#DDE0E6" stroke-width="22"/>'
         f'<path d="M-24 -117 A120 120 0 0 1 24 -117" fill="none" stroke="{WAT}" stroke-width="22"/>'
         f'<g id="needle"><line x1="0" y1="0" x2="0" y2="-104" stroke="#0B0B10" stroke-width="6" stroke-linecap="round"/></g><circle r="11" fill="#0B0B10"/></svg>'
         f'<div class="mono" style="font-size:26px;font-weight:800;text-align:center">ENERGIE DER TEILCHEN</div></div>')
stage.append(el(gauge, 0, 420, A("b22@Energie", "b23@Wucht", -0.3) + ' data-sfx="glass"', 1080, CENTER))
chip("🎯 DIE WUCHT MUSS GENAU STIMMEN", 1180, "b23@Wucht", "b24", -0.3, INK)
stampg("✓ LAUFEND NACHGEREGELT", 1130, "b24@nachgeregelt", "b25", -0.1, 48)
chip("😱 2008: ANGST VOR EINEM SCHWARZEN LOCH", 1180, "b25@Angst", "b26", -0.2, "#E5484D")
chip("☄️ TEILCHEN AUS DEM ALL: NOCH MEHR WUCHT", 1180, "b26@Weltall", "b27", -0.1, "#C77700")
stampg("✓ DIE ERDE GIBT ES NOCH", 1130, "b27@Erde", "end", -0.1, 50)
stage.append(el('<div class="note mono">SCHEMATISCH · QUELLEN: CERN, LSAG-SICHERHEITSBERICHT 2008</div>', 20, 1250, A("b3", "end", 0.3) + ' data-sfx="none"'))

# Ebenen-Plan: (anker, offset, ebene)
TR = [("b1", -1, "m"), ("b3@100", -0.25, "c"), ("b4", -0.15, "m"), ("b8", -0.25, "g"), ("b11", -0.2, "m"),
      ("b16", -0.1, "e"), ("b18", -0.25, "c"), ("b19", -0.15, "m"), ("b21", -0.25, "g"), ("b25", -0.2, "m"), ("b26", -0.15, "e")]
# Kamera Karte: (anker, offset, x, y, z)
MC = [("b1", -1, 620, 420, 1.0), ("b2", 0.0, 610, 430, 1.04), ("b3", 0.0, 600, 450, 1.0), ("b4", -0.2, 600, 450, 1.0), ("b4", 0.6, 640, 520, 0.82),
      ("b5", -0.2, 640, 520, 0.82), ("b5", 0.5, 600, 450, 1.0), ("b7", 0.0, 600, 450, 1.0), ("b11", -0.4, 600, 450, 1.0), ("b12", 0.0, 600, 450, 1.0),
      ("b13", -0.3, cx_, cy_, 1.0), ("b13", 0.4, cx_, cy_, 3.0), ("b14", 0.6, cx_, cy_, 3.2), ("b15", 0.0, cx_ - 40, cy_ - 40, 2.6), ("b16", 0.0, cx_ - 40, cy_ - 40, 2.6),
      ("b19", -0.3, 600, 450, 1.05), ("b20", 0.4, 600, 450, 1.0), ("b25", -0.3, 600, 450, 1.0), ("b25@schwarzes", 0.0, 600, 450, 1.25), ("b26", 0.0, 600, 450, 1.35)]
PANJS = dict(tr=TR, mc=MC, rc=[RCX, RCY, RR], exp=[pt(a) for _, a in EXP], arc=[ACX, ACY, AR])
STAGEJS = open("stage.js").read()

# ---- End card (identisch zum Template) ----
logo = open("../brand/out/missionwissen-logo-transparent-dunkel.svg").read()
logo = re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="820" height="253"', logo, count=1)
endcard = f'<div class="el" {A("end",None,0.1)} style="left:130px;top:470px">{logo}</div>' + f'<div class="el" {A("end",None,0.5)} style="left:0;width:1080px;top:790px;display:flex;justify-content:center"><div class="row" style="gap:28px"><div class="follow">+&nbsp;Folgen</div><div class="follow">🔖&nbsp;Speichern</div></div></div>' + f'<div class="el" {A("end",None,0.7)} style="left:0;width:1080px;top:935px;text-align:center"><div class="mono small grey">JEDEN TAG EIN BISSCHEN SCHLAUER</div></div>'
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
.follow{{font-family:Unbounded;font-weight:600;font-size:42px;color:#fff;background:#7B3FE4;border-radius:999px;padding:24px 56px;box-shadow:0 0 30px rgba(123,63,228,.4),0 8px 18px rgba(26,31,51,.15)}}
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
.konf{{position:absolute;opacity:0}}
.num{{font-family:Unbounded;font-weight:600;font-size:170px;letter-spacing:-6px;line-height:1}}
.cal{{width:190px;height:170px;border-radius:16px;border:3px solid #0B0B10;background:#fff;overflow:hidden;box-shadow:0 6px 14px rgba(26,31,51,.12)}}
.calh{{background:#7B3FE4;color:#fff;font-size:22px;font-weight:700;text-align:center;padding:8px 0}}
.calb{{font-family:Unbounded;font-weight:600;font-size:92px;text-align:center;line-height:1.2}}
#chap,#prog{{display:none}}
#headbg{{position:absolute;left:0;top:0;width:1080px;height:440px;z-index:2;background:linear-gradient(rgba(255,255,255,.97) 78%,rgba(255,255,255,0))}}
#head{{top:200px;z-index:3}} #wm{{z-index:4}}
.mbox{{width:88px;height:88px;border-radius:14px;border:3px solid #0B0B10;background:#fff;font-family:Unbounded;font-weight:600;font-size:36px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 10px rgba(26,31,51,.10)}}
.seat{{width:44px;height:44px;border-radius:50%;background:#fff;border:4px solid #0B0B10}}
.plate{{width:32px;height:14px;border-radius:50%;border:2.5px solid #7A7F8C;background:#fff}}
.bar{{width:170px;border-radius:14px 14px 4px 4px;border:3px solid #0B0B10}}
.barv{{width:180px;text-align:center;font-size:40px;font-weight:800}}
.barl{{width:180px;text-align:center;font-size:22px;font-weight:700;line-height:1.2;color:#5D616B}}
.note{{font-size:16px;color:#8A8F99;background:rgba(255,255,255,.9);border:1.5px solid #C9CCD3;border-radius:8px;padding:5px 9px;white-space:nowrap}}
#bigcal{{transform-origin:50% 0}}
.flake{{position:absolute;top:0;color:#8FD9D0;font-weight:700;opacity:0}}
.gcard{{background:#fff;border:2px solid #0B0B10;border-radius:18px;padding:14px 10px 12px;box-shadow:0 8px 18px rgba(26,31,51,.12)}}
.cal{{border-radius:22px}}
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
 const top=cl(1-pr(t,END,.3),0,1); const hf=1-pr(t,S['b3']-0.3,0.35); document.getElementById('headbg').style.opacity=hf; document.getElementById('head').style.opacity=top*hf;
 let hs=b.s; for(let i=BEATS.indexOf(b);i>0&&BEATS[i-1].head===b.head;i--) hs=BEATS[i-1].s;
 const H=document.getElementById('head'); H.innerHTML=b.head||BEATS[0].head; H.style.fontSize='64px'; if(BEATS.indexOf(b)<3) hs=-1; const hp=ease(pr(t,hs,.3));
 const g=Math.round(181+(11-181)*hp), g2=Math.round(184+(11-184)*hp), g3=Math.round(192+(16-192)*hp); H.style.color=`rgb(${{g}},${{g2}},${{g3}})`;
 // elements
 for(const e of els){{
  const tin=(S[e.dataset.in]??(console.log('missing '+e.dataset.in),0))+(+e.dataset.d||0); const tout=e.dataset.out?S[e.dataset.out]:1e9;
  const pi=ease(pr(t,tin,.35)), po=pr(t,tout,.2);
  e.style.opacity=pi*(1-po); e.style.transform=`translateY(${{16*(1-pi)}}px)`;
 }}
 // counters
 for(const c of document.querySelectorAll('.count')){{const t0=(S[c.dataset.cin]??0)+(+c.dataset.cd||0); const dd=+c.dataset.dec||0; const v=+c.dataset.count*ease(pr(t,t0,0.8)); c.textContent=dd?v.toFixed(dd).replace('.',','):Math.round(v).toLocaleString('de-DE');}}
 // sketches
 for(const sk of document.querySelectorAll('.sketch')){{const t0=(S[sk.dataset.sin]??0)+(+sk.dataset.sd||0); const p=ease(pr(t,t0,+sk.dataset.sdur||1.5)); sk.querySelectorAll('.ink').forEach(e=>e.style.strokeDashoffset=1-p); sk.querySelectorAll('.mesh').forEach(e=>e.style.opacity=pr(t,t0+(+sk.dataset.sdur||1.5)*0.6,0.6));}}
{STAGEJS}
 // robot
 let pose=b.pose; if(end) pose='winkt';
 const R=document.getElementById('robot');
 let rop=0; if(pose&&!end){{const prevHad=BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose; rop=prevHad?1:ease(pr(t,b.s-(BEATS.indexOf(b)===0?0.3:0),.3)); const nb=BEATS[BEATS.indexOf(b)+1]; if(nb&&!nb.pose) rop*=1-pr(t,nb.s-0.2,.2); if(!nb) rop*=1-pr(t,END-0.2,.2);}}
 if(end){{rop=ease(pr(t,END+0.3,.35));}}
 R.style.opacity=rop; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');
 let prevPose=null; const bi=BEATS.indexOf(b); if(bi>0) prevPose=BEATS[bi-1].pose; const pf=bi===0?1:pr(t,b.s,.15);
 for(const p of R.querySelectorAll('.pose')){{const n=p.dataset.pose; p.style.opacity=end?(n==='winkt'?1:0):(n===pose?pf:(n===prevPose&&prevPose!==pose?1-pf:0)); if(pose===prevPose&&n===pose) p.style.opacity=1;}}
 const bl=((t+1.5)%3.7); const sy=bl<0.12?0.2:1; R.querySelectorAll('.eyes').forEach(e=>e.style.transform=`scaleY(${{sy}})`);
 R.querySelectorAll('.pulse').forEach(e=>e.setAttribute('opacity',0.3+0.1*Math.sin(t*2*Math.PI/1.8)));
 // captions
 const P=document.getElementById('pill'); const W=b.words; let wi=0; W.forEach((w,i)=>{{if(t>=w[1]) wi=i;}});
 const cid=W[wi][3]; P.innerHTML=W.map((w,i)=>[w,i]).filter(x=>x[0][3]===cid).map(([w,i])=>`<span class="${{i<=wi?'on':''}} ${{w[2]?(b.ch%2?'kw2':'kw'):''}}">${{w[0]}}</span>`).join(' ');
 document.getElementById('cap').style.opacity=t<AUD+0.3?1:1-pr(t,AUD+0.3,.3);
}};
render(0);
</script></body></html>'''
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))
