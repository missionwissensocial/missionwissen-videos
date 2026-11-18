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
HOOK = 'Warum ist dein Handy-Akku in der <span style="color:#7B3FE4">Kälte</span> so schnell leer?'
B = [
 ("s1", 0, HOOK, "Warum geht dein *Handy-Akku* in der *Kälte* so schnell *leer?*", "staunt"),
 ("s2", 0, HOOK, "Im *Akku* wandern winzige *Teilchen* hin und her: *Lithium-Ionen.*", None),
 ("s3", 0, "", "Nur wenn sie *wandern,* bekommt dein Handy *Strom.*", None),
 ("s4", 0, "", "Dabei schwimmen sie durch eine *Flüssigkeit.*", None),
 ("s5", 0, "", "Bei *Kälte* wird diese Flüssigkeit *zäh,* fast wie *Honig.*", None),
 ("s6", 0, "", "Die Teilchen kommen nur noch *langsam* voran.", None),
 ("s7", 0, "", "Die *Folge?*", None),
 ("s8", 0, "", "Die *Spannung* *sinkt* – also der *Druck,* der den Strom ins Handy schiebt.", None),
 ("s9", 0, "", "An dieser *Spannung* schätzt das Handy die *Prozente.*", None),
 ("s10", 0, "", "Es zeigt *weniger* an – oder *schaltet* *ab,* weil der Druck nicht reicht.", None),
 ("s11", 0, "", "Dabei ist noch *Energie* drin.", None),
 ("s12", 0, "", "Wird der Akku wieder *warm,* kommen die *Prozente* *zurück.*", None),
 ("s13", 0, "", "Im *Winter* also: Handy in die *Innentasche.*", None),
 ("s14", 0, "", "Und lade es erst, wenn es wieder *warm* ist.", None),
 ("s15", 0, "", "Sonst *stauen* sich die langsamen Teilchen und bleiben *kleben* – der Akku speichert *dauerhaft* *weniger.*", None),
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



# ================= Bühne "Handy → Akku → Zelle" (durchgehende SVG-Kamera, Hauptdarsteller: ein Lithium-Ion) =================
import math
CENTER = "display:flex;justify-content:center"
AMB = "#E8A33D"
# Welt-Koordinaten = Panel-Koordinaten bei Zoom 1 (Panel 1000x800). Kamera per SVG-Transform (scharf).
G = []
def g(inner, wi=None, wo=None, extra=""):
    a = (f' data-wi="{wi}"' if wi else "") + (f' data-wo="{wo}"' if wo else "")
    return f'<g class="wg"{a} {extra}>{inner}</g>'
def dr(d, w=2.2, c=INK, a="s1", dur=1.0, dl=0.0, extra=""):
    return f'<path class="dr" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="{d}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round" data-a="{a}" data-dl="{dl}" data-dur="{dur}" {extra}/>'

# --- Mantel (s13), um das Handy herum gezeichnet ---
coat = (dr("M330 -60 Q500 40 670 -60", 4, INK, "s13", 0.6, -0.1)
        + dr("M330 -60 L120 0 Q60 30 50 120 L10 1000", 4, INK, "s13", 0.9, -0.05)
        + dr("M670 -60 L880 0 Q940 30 950 120 L990 1000", 4, INK, "s13", 0.9, -0.05)
        + dr("M330 -60 L250 300 L300 1000 M670 -60 L750 300 L700 1000", 3.2, INK2, "s13", 0.9, 0.1)
        + dr("M150 260 L130 1000 M850 260 L870 1000", 2.4, INK2, "s13", 0.8, 0.25))
G.append(g(coat, None, "s14"))
# Wärme-Schein in der Tasche
G.append(f'<defs><radialGradient id="warm"><stop offset="0" stop-color="{PUR}" stop-opacity=".28"/><stop offset="1" stop-color="{PUR}" stop-opacity="0"/></radialGradient>'
         f'<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#5D616B" stroke-width="2"/></pattern>'
         f'<pattern id="hatch2" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="6" stroke="{PUR}" stroke-width="2"/></pattern></defs>')
G.append(f'<ellipse id="warmglow" cx="500" cy="560" rx="330" ry="300" fill="url(#warm)" opacity="0"/>')

# --- Ladekabel (s14) ---
G.append(g(dr("M500 712 V760 Q500 800 540 820 Q600 850 600 1000", 6, INK, "s14@lade", 0.7, -0.1)
           + f'<rect x="484" y="706" width="32" height="26" rx="4" fill="{INK}" class="wfade" data-fa="s14@lade" data-fd="0.1"/>', None, "s15"))

# --- Handy ---
ph = []
ph.append(f'<rect x="350" y="90" width="300" height="620" rx="44" fill="#fff" stroke="{INK}" stroke-width="5"/>')
ph.append(f'<rect x="460" y="108" width="80" height="16" rx="8" fill="{INK}"/>')
ph.append(f'<rect id="screen" x="368" y="146" width="264" height="546" rx="22" fill="#15161C"/>')
# Akku/Zelle (Röntgenblick) – liegt auf dem Bildschirm
cell = []
cell.append(f'<rect x="404" y="356" width="192" height="176" rx="10" fill="#fff" stroke="{INK2}" stroke-width="2.4"/>')
cell.append(f'<rect id="liquid" x="442" y="372" width="116" height="144" fill="rgba(25,198,180,.18)"/>')
cell.append(f'<rect x="414" y="372" width="28" height="144" fill="url(#hatch)" stroke="{INK}" stroke-width="1.6"/>')
cell.append(f'<rect x="558" y="372" width="28" height="144" fill="url(#hatch2)" stroke="{INK}" stroke-width="1.6"/>')
cell.append(f'<text x="428" y="530" text-anchor="middle" font-family="JBM" font-weight="800" font-size="9" fill="{INK}">−</text>')
cell.append(f'<text x="572" y="530" text-anchor="middle" font-family="JBM" font-weight="800" font-size="9" fill="{PUR}">+</text>')
# Kleber-Belag an der Minus-Seite (s15)
crust = "".join(f'<circle class="cr" cx="{444 + (k % 2) * 3.5:.1f}" cy="{378 + k * 8.4:.1f}" r="{3.2 + (k * 7 % 3) * 0.7:.1f}" fill="#8A8F99" data-k="{k}"/>' for k in range(17))
cell.append(f'<g id="crust">{crust}</g>')
# Draht + "Handy-Lampe"
cell.append(f'<path id="wire" d="M428 372 V350 H572 V372" stroke="{INK}" stroke-width="2.2" fill="none" stroke-linejoin="round"/>')
cell.append(f'<rect x="492" y="340" width="16" height="22" rx="3" fill="#fff" stroke="{INK}" stroke-width="1.8"/><rect id="lamp" x="495" y="344" width="10" height="14" rx="1.5" fill="{TQ}" opacity=".2"/>')
cell.append("".join(f'<circle class="eld" r="1.8" fill="{PUR}"/>' for _ in range(10)))
# Ionen
NI = 13
for k in range(NI):
    if k == 0:
        cell.append(f'<g class="ion" id="ion0"><circle r="10" fill="{PUR}" opacity=".18"/><circle r="6.2" fill="{PUR}" stroke="#fff" stroke-width="1.3"/>'
                    f'<text y="2.3" text-anchor="middle" font-family="JBM" font-weight="800" font-size="5.6" fill="#fff">Li+</text></g>')
    else:
        cell.append(f'<g class="ion"><circle r="4" fill="#B79BFF" stroke="#fff" stroke-width="1"/><text y="1.6" text-anchor="middle" font-family="JBM" font-weight="800" font-size="4.2" fill="#fff">+</text></g>')
ph.append(f'<g id="xray" opacity="0">{"".join(cell)}</g>')
# Bildschirm-Inhalt
ph.append(f'<g id="scr"><text x="500" y="250" text-anchor="middle" font-family="JBM" font-weight="700" font-size="22" fill="#8A8F99">AKKU</text>'
          f'<text id="pct" x="500" y="400" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="80" fill="#fff">80%</text>'
          f'<rect x="430" y="450" width="128" height="58" rx="10" fill="none" stroke="#fff" stroke-width="5"/><rect x="560" y="466" width="10" height="26" rx="3" fill="#fff"/>'
          f'<rect id="bfill" x="438" y="458" width="112" height="42" rx="5" fill="{TQ}"/></g>')
ph.append('<rect id="offscr" x="368" y="146" width="264" height="546" rx="22" fill="#050507" opacity="0"/>')
G.append(f'<g id="phone">{"".join(ph)}</g>')
# Taschen-Vorderseite (verdeckt das Handy unten, s13)
G.append(g(f'<path d="M300 540 H700 V900 H300 Z" fill="#fff" stroke="{INK}" stroke-width="4"/>'
           + dr("M330 580 H670", 2, INK2, "s13@Innentasche", 0.5, 0.1), "s13@Innentasche", "s14", 'id="pocket"'))

world = f'<svg id="wsvg" width="1000" height="800" viewBox="0 0 1000 800" style="position:absolute;left:0;top:0"><g id="camg">{"".join(G)}</g></svg>'

# --- Schneeflocken (Bildschirm-Ebene im Panel) ---
flakes = "".join(f'<div class="flake" data-k="{k}" style="left:{(k * 137) % 960 + 10}px">✻</div>' for k in range(16))

# --- große Temperatur-Zahl ---
temp = (f'<div id="tempbox" class="row" style="position:absolute;left:34px;top:26px;gap:14px;opacity:0">'
        f'<svg width="46" height="150" viewBox="0 0 46 150"><rect x="14" y="6" width="18" height="110" rx="9" fill="#fff" stroke="{INK}" stroke-width="4"/>'
        f'<rect id="merc" x="19" y="40" width="8" height="80" rx="4" fill="{TQ}"/><circle cx="23" cy="128" r="16" fill="{TQ}" stroke="{INK}" stroke-width="4" id="bulb"/></svg>'
        f'<div id="tempnum" class="num" style="font-size:150px">20°</div></div>')

# --- Spannungs-Anzeige (Manometer) ---
ticks = "".join(f'<line x1="0" y1="-112" x2="0" y2="-98" stroke="{INK}" stroke-width="3" transform="rotate({a})"/>' for a in range(-80, 81, 20))
gauge = (f'<div class="gcard"><svg width="260" height="170" viewBox="-130 -130 260 170">'
         f'<path d="M-112 0 A112 112 0 0 1 -86 -72" stroke="{RED}" stroke-width="14" fill="none"/>'
         f'<path d="M-86 -72 A112 112 0 0 1 112 0" stroke="{TQ}" stroke-width="14" fill="none"/>{ticks}'
         f'<line id="needle" x1="0" y1="0" x2="0" y2="-96" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><circle r="11" fill="{INK}"/></svg>'
         f'<div class="mono" style="font-size:26px;font-weight:800;text-align:center;margin-top:-4px">SPANNUNG</div></div>')

panel = world + flakes + temp
stage.append(mm(panel, 40, 440, 1000, 800, A("s1", "end", -0.6) + ' data-sfx="none"'))

# ---- Overlays (Bildschirm, höchstens eins gleichzeitig) ----
def omk(text, x, y, i, o, d=0.0, col=PUR):
    stage.append(f'<div class="el mk" {A(i, o, d)} style="left:{x}px;top:{y}px;gap:10px"><span class="pin" style="background:{col}"></span><span class="mono lab" style="color:{col};border-color:{col};font-size:30px">{text}</span></div>')
omk("LITHIUM-IONEN", 420, 1172, "s2@Lithium-Ionen", "s3", -0.2)
omk("STROM FÜRS HANDY", 400, 1172, "s3@Strom", "s4", -0.25, INK)
omk("FLÜSSIGKEIT", 460, 1172, "s4@Flüssigkeit", "s5", -0.3, TQ)
omk("❄ ZÄH WIE HONIG", 400, 1172, "s5@zäh", "s6", -0.1, "#B87A1F")
omk("NUR NOCH LANGSAM", 380, 1172, "s6@langsam", "s7", -0.2, "#B87A1F")
stage.append(el(gauge, 720, 470, A("s8@Spannung", "s10", -0.15) + ' data-sfx="glass"'))
omk("→ ANZEIGE %", 740, 735, "s9@schätzt", "s10", -0.1, INK)
stage.append(el('<div class="stamp mono" style="font-size:64px">AUS</div>', 40, 1080, A("s10@ab", "s11", -0.05), 1000, CENTER))
omk("NOCH ENERGIE DRIN", 400, 1172, "s11@Energie", "s12", -0.15, TQ)
omk("✓ PROZENTE ZURÜCK", 400, 1172, "s12@Prozente", "s13", 0.0, TQ)
omk("INNENTASCHE = WARM", 380, 1172, "s13@Innentasche", "s14", 0.1, PUR)
stage.append(el(f'<div class="chip mono" style="font-size:30px;padding:12px 20px;font-weight:800;background:#fff;border-color:{TQ}">🔌 ERST WARM, DANN LADEN ✓</div>', 40, 1160, A("s14@warm", "s15", -0.1) + ' data-sfx="success"', 1000, CENTER))
omk("TEILCHEN BLEIBEN KLEBEN", 300, 1172, "s15@kleben", "s15@dauerhaft", -0.3, RED)
stage.append(el('<div class="stamp mono" style="font-size:52px">DAUERHAFT WENIGER</div>', 40, 1040, A("s15@dauerhaft", "end", -0.05), 1000, CENTER))
stage.append(el('<div class="note mono">SCHEMATISCH</div>', 60, 1206, A("s2", "end", 0.3) + ' data-sfx="none"'))

cam = [("s1", 0, 345, 400, 1.0), ("s2", -0.1, 380, 405, 1.04), ("s2@Akku", 0.25, 500, 442, 4.0),
       ("s7", -0.1, 500, 442, 4.0), ("s7", 0.7, 520, 430, 2.3), ("s9", -0.1, 520, 430, 2.3), ("s9", 0.7, 500, 400, 1.0),
       ("s11", -0.1, 500, 400, 1.0), ("s11", 0.5, 500, 440, 2.4), ("s12", -0.15, 500, 440, 2.4), ("s12", 0.55, 345, 400, 1.0), ("s13", -0.1, 345, 400, 1.0), ("s13", 0.7, 500, 470, 0.62), ("s14", -0.15, 500, 470, 0.62), ("s14", 0.6, 500, 420, 0.9),
       ("s15", -0.1, 500, 420, 0.9), ("s15", 0.9, 500, 442, 4.0), ("end", 0, 500, 442, 4.0)]
PANJS = dict(cam=cam, ni=NI)

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
 const top=cl(1-pr(t,END,.3),0,1); const hf=1-pr(t,S['s3']-0.3,0.35); document.getElementById('headbg').style.opacity=hf; document.getElementById('head').style.opacity=top*hf;
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
 // ---- Akku-Bühne ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const win=(tt,a,b,fi,fo)=>pr(tt,a,fi)*(1-pr(tt,b,fo));
  const ks=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4]}}));
  function cam(tt){{ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){{const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){{const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e)}};}}}} return ks[ks.length-1]; }}
  const c=cam(t); const zz=c.z*(1+0.012*Math.sin(t*0.9));
  document.getElementById('camg').setAttribute('transform',`translate(500 400) scale(${{zz.toFixed(4)}}) translate(${{(-c.x).toFixed(2)}} ${{(-c.y).toFixed(2)}})`);
  // Welt-Gruppen
  for(const e of document.querySelectorAll('.wg')){{ let o=1; if(e.dataset.wi) o*=pr(t,S[e.dataset.wi]-0.05,0.3); if(e.dataset.wo) o*=1-pr(t,S[e.dataset.wo],0.3); e.setAttribute('opacity',o.toFixed(3)); }}
  for(const e of document.querySelectorAll('.dr')){{ const t0=S[e.dataset.a]+(+e.dataset.dl||0); e.style.strokeDashoffset=(1-ease(pr(t,t0,+e.dataset.dur||1))).toFixed(4); }}
  for(const e of document.querySelectorAll('.wfade')){{ e.setAttribute('opacity',pr(t,S[e.dataset.fa]+(+e.dataset.fd||0),0.2).toFixed(3)); }}
  // Zustände
  const coldF=tt=>Math.min(1, win(tt,S['s5@Kälte']-0.1,S['s12@warm'],0.8,1.0)+pr(tt,S['s15']-0.1,0.6));
  const k=coldF(t);
  const xr=Math.max(win(t,S['s2@Akku']-0.3,S['s9']+0.2,0.5,0.5), win(t,S['s11']-0.1,S['s12@warm']-0.2,0.4,0.4), pr(t,S['s15']-0.1,0.5));
  const off=pr(t,S['s10@ab']-0.1,0.25)*(1-pr(t,S['s12@warm'],0.3));
  document.getElementById('xray').setAttribute('opacity',xr.toFixed(3));
  const mix=(a,b,u)=>Math.round(a+(b-a)*u);
  document.getElementById('screen').setAttribute('fill',`rgb(${{mix(21,246,xr)}},${{mix(22,246,xr)}},${{mix(28,248,xr)}})`);
  document.getElementById('scr').setAttribute('opacity',((1-xr)*(1-off)).toFixed(3));
  document.getElementById('offscr').setAttribute('opacity',(off*(1-xr)).toFixed(3));
  // Prozent-Anzeige
  let p=80-49*ease(pr(t,0.3,2.2)); p-=22*ease(pr(t,S['s10@weniger']-0.1,0.9)); p+=37*ease(pr(t,S['s12@Prozente']-0.2,1.0));
  const PT=document.getElementById('pct'); PT.textContent=Math.round(p)+'%'; PT.setAttribute('fill',p<15?'#E5484D':'#fff');
  const BF=document.getElementById('bfill'); BF.setAttribute('width',(112*p/100).toFixed(1)); BF.setAttribute('fill',p<20?'#E5484D':'#19C6B4');
  // Temperatur
  const tb=document.getElementById('tempbox');
  tb.style.opacity=Math.max(win(t,-1,S['s2']+0.1,0.01,0.3), win(t,S['s12']-0.1,S['s13']-0.1,0.3,0.3)).toFixed(3);
  let tv=t<S['s5']?20-30*ease(pr(t,0.2,2.0)):-10+30*ease(pr(t,S['s12@warm']-0.2,1.2));
  const tr=Math.round(tv); document.getElementById('tempnum').textContent=(tr<0?'−':'')+Math.abs(tr)+'°';
  document.getElementById('tempnum').style.color=tr<5?'#19C6B4':'#7B3FE4';
  {{ const h=20+60*(tv+10)/30; const M=document.getElementById('merc'); M.setAttribute('height',h.toFixed(1)); M.setAttribute('y',(120-h).toFixed(1)); const col=tr<5?'#19C6B4':'#7B3FE4'; M.setAttribute('fill',col); document.getElementById('bulb').setAttribute('fill',col); }}
  // Schnee
  const snow=Math.max(win(t,-1,S['s2@Akku'],0.01,0.4), win(t,S['s5@Kälte']-0.2,S['s12@warm'],0.4,0.6), pr(t,S['s15']-0.1,0.5));
  for(const f of document.querySelectorAll('.flake')){{ const i=+f.dataset.k; const y=((t*70+i*97)%860)-50; f.style.transform=`translate(${{(16*Math.sin(t*1.3+i)).toFixed(1)}}px,${{y.toFixed(1)}}px) rotate(${{(t*40+i*30)%360}}deg)`; f.style.opacity=(snow*0.6).toFixed(3); f.style.fontSize=(24+(i%3)*12)+'px'; }}
  // Flüssigkeit
  document.getElementById('liquid').setAttribute('fill',`rgba(${{mix(25,232,k)}},${{mix(198,163,k)}},${{mix(180,61,k)}},${{(0.18+0.42*k).toFixed(3)}})`);
  // Ionen: Phase integrieren (Tempo sinkt bei Kälte)
  let ph=0; for(let s=0;s<t;s+=1/30) ph+=(1-0.85*coldF(s))/30;
  const st0=S['s15@stauen']-0.1;
  [...document.querySelectorAll('.ion')].forEach((e,i)=>{{
    const lane=i===0?444:380+((i*37)%128); const phi=i*0.83;
    let x=447+106*(0.5-0.5*Math.cos(ph*2.4+phi)), y=lane+3*Math.sin(ph*3+i);
    const sk=ease(pr(t,st0+i*0.09,0.8)); const xs=450+(i%3)*6;
    x=x+(xs-x)*sk; e.setAttribute('transform',`translate(${{x.toFixed(2)}} ${{y.toFixed(2)}})`); e.style.filter=sk>0?`grayscale(${{sk.toFixed(2)}})`:'none';
  }});
  for(const cr of document.querySelectorAll('.cr')){{ if(!cr.dataset.r0) cr.dataset.r0=cr.getAttribute('r'); const q=ease(pr(t,S['s15@kleben']-0.3+(+cr.dataset.k)*0.04,0.4)); cr.setAttribute('r',(cr.dataset.r0*q).toFixed(2)); }}
  // Elektronen im Draht + Lampe
  const v=1-0.85*k;
  [...document.querySelectorAll('.eld')].forEach((e,j)=>{{ let u=((j/10+ph*0.45)%1)*188; let x,y; if(u<22){{x=428;y=372-u;}} else if(u<166){{x=428+(u-22);y=350;}} else {{x=572;y=350+(u-166);}} e.setAttribute('cx',x.toFixed(2)); e.setAttribute('cy',y.toFixed(2)); }});
  document.getElementById('lamp').setAttribute('opacity',(0.15+0.8*v*pr(t,S['s3']-0.2,0.4)).toFixed(3));
  // Manometer
  {{ const a=55-117*ease(pr(t,S['s8@sinkt']-0.1,1.0))+2*Math.sin(t*9); document.getElementById('needle').setAttribute('transform',`rotate(${{a.toFixed(1)}})`); }}
  // Handy in die Innentasche
  {{ const dy=170*ease(pr(t,S['s13@Innentasche']-0.3,0.7))*(1-ease(pr(t,S['s14']-0.2,0.6))); document.getElementById('phone').setAttribute('transform',`translate(0 ${{dy.toFixed(1)}})`);
    document.getElementById('warmglow').setAttribute('opacity',win(t,S['s13@Innentasche'],S['s14'],0.5,0.4).toFixed(3)); }}
  // Headline nach dem Hook ausblenden (dyn_ws überschreibt die Opacity)
  {{ const H_=document.getElementById('head'); H_.style.opacity=(+H_.style.opacity||0)*(1-pr(t,S['s3']-0.3,0.35)); }}
 }}
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
