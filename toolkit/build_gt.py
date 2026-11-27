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
HOOK = 'Wie treffen sich zwei Tunnel im Berg auf den <span style="color:#7B3FE4">Zentimeter?</span>'
B = [
 ("s1", 0, HOOK, "Zwei *Bautrupps* graben sich tief im *Berg* *aufeinander* *zu.*", "staunt"),
 ("s2", 0, HOOK, "Wie *treffen* sie sich nach *Kilometern* im Fels – auf wenige *Zentimeter* *genau?*", None),
 ("s3", 0, "", "Das ist der *Gotthard-Basistunnel* in der *Schweiz:* *57* *Kilometer* lang, bei seiner Eröffnung der *längste* *Eisenbahntunnel* der *Welt.*", None),
 ("s4", 0, "", "Gegraben wurde an *mehreren* *Stellen* gleichzeitig – manche Trupps kamen über tiefe *Schächte* in den Berg.", None),
 ("s5", 0, "", "Riesige *Bohrmaschinen* fraßen sich durch den Fels, jede über *400* *Meter* lang.", None),
 ("s6", 0, "", "Aber woher wissen die Trupps, *wohin* sie graben?", None),
 ("s7", 0, "", "Draußen bestimmen Vermesser ihre *Startpunkte* per *GPS.*", None),
 ("s8", 0, "", "Im Berg kommt das *Satellitensignal* aber *nicht* *an.*", None),
 ("s9", 0, "", "Deshalb setzen sie alle paar hundert Meter einen neuen *Messpunkt* – wie eine *Kette* von draußen bis zur *Maschine.*", None),
 ("s10", 0, "", "Von Punkt zu Punkt misst ein *Lasergerät* *Abstand,* *Richtung* und *Höhe.*", None),
 ("s11", 0, "", "Doch jede Messung hat einen *winzigen* *Fehler.*", None),
 ("s12", 0, "", "Über viele Kilometer würde der Tunnel so *abdriften.*", None),
 ("s13", 0, "", "Deshalb prüfen sie die Richtung mit einem *Kreiselkompass.*", None),
 ("s14", 0, "", "Der zeigt nach *Norden,* weil er sich nach der *Drehung* der *Erde* ausrichtet – ganz *ohne* *Magnet.*", None),
 ("s15", 0, "", "*2010* *trafen* sich die Trupps.", None),
 ("s16", 0, "", "Die *Abweichung?*", None),
 ("s17", 0, "", "Seitlich *8* *Zentimeter,* in der Höhe nur *1* *Zentimeter.*", None),
 ("s18", 0, "", "Erlaubt waren *25* *Zentimeter.*", None),
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



# ================= Bühne "Alpen-Querschnitt → Tunnel" (durchgehende SVG-Kamera, Hauptdarsteller: Bohrmaschine/Tunnelspitze) =================
import math
CENTER = "display:flex;justify-content:center"
G = []
def g(inner, wi=None, wo=None, extra=""):
    a = (f' data-wi="{wi}"' if wi else "") + (f' data-wo="{wo}"' if wo else "")
    return f'<g class="wg"{a} {extra}>{inner}</g>'
def dr(d, w=2.2, c=INK, a="s1", dur=1.0, dl=0.0, extra=""):
    return f'<path class="dr" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="{d}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round" data-a="{a}" data-dl="{dl}" data-dur="{dur}" {extra}/>'
PROF = [(-400, 720), (-200, 700), (60, 640), (200, 420), (330, 300), (470, 360), (600, 200), (760, 260), (900, 150), (1050, 240), (1200, 170), (1350, 300), (1500, 230), (1650, 380), (1800, 560), (1940, 640), (2200, 700), (2400, 720)]
def surf(x):
    for (x0, y0), (x1, y1) in zip(PROF, PROF[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return 720
TY = 640; MX = 1100
prof_d = "M" + " L".join(f"{x} {y}" for x, y in PROF)
G.append(f'<defs><pattern id="rock" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><line x1="0" y1="0" x2="0" y2="22" stroke="#C9CCD3" stroke-width="2"/></pattern>'
         f'<radialGradient id="glow"><stop offset="0" stop-color="{PUR}" stop-opacity=".55"/><stop offset="1" stop-color="{PUR}" stop-opacity="0"/></radialGradient></defs>')
G.append(f'<path d="{prof_d} L2400 1400 L-400 1400 Z" fill="#F1F2F5"/><path d="{prof_d} L2400 1400 L-400 1400 Z" fill="url(#rock)" opacity=".7"/>')
G.append(f'<path d="{prof_d}" fill="none" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
# Schnee-Gipfel
for (x, y) in [(600, 200), (900, 150), (1200, 170), (1500, 230)]:
    G.append(f'<path d="M{x-40} {y+28} L{x} {y} L{x+40} {y+28} Q{x} {y+16} {x-40} {y+28} Z" fill="#fff" stroke="{INK}" stroke-width="3"/>')
# Satelliten + Signale (s7/s8)
SATS = [(450, -430), (1000, -540), (1550, -440)]
sat_svg = ""
for (x, y) in SATS:
    sat_svg += (f'<g transform="translate({x} {y})"><rect x="-26" y="-18" width="52" height="36" rx="6" fill="#fff" stroke="{INK}" stroke-width="5"/>'
                f'<rect x="-96" y="-12" width="60" height="24" fill="{TQ}" stroke="{INK}" stroke-width="4"/><rect x="36" y="-12" width="60" height="24" fill="{TQ}" stroke="{INK}" stroke-width="4"/></g>')
G.append(g(sat_svg, "s7", "s9"))
sig = ""
for (x, y), (px, py) in zip(SATS, [(60, TY), (1940, TY), (1940, TY)]):
    sig += dr(f"M{x} {y+20} L{px} {py-10}", 6, TQ, "s7@GPS", 0.6, -0.3, 'stroke-dasharray="1"')
G.append(g(sig, "s7", "s9", 'class="wg sig"'))
G.append(g("".join(f'<g transform="translate({px} {TY-10})"><path d="M-22 -40 L22 -40 L0 0 Z" fill="{TQ}" stroke="{INK}" stroke-width="4"/></g>' for px in (60, 1940)), "s7@Startpunkte", "s9"))
# Signal endet an der Oberfläche über der Tunnelspitze
ix = 1150; sy = surf(ix)
G.append(g(dr(f"M1000 -520 L{ix} {sy-6}", 6, TQ, "s8@Satellitensignal", 0.5, -0.1)
           + dr(f"M{ix} {sy+10} L{ix} {TY-20}", 5, RED, "s8@nicht", 0.5, -0.1, 'stroke-dasharray="1"')
           + f'<g class="wfade" data-fa="s8@nicht" data-fd="0.1"><path d="M{ix-34} {sy+30} l68 68 M{ix+34} {sy+30} l-68 68" stroke="{RED}" stroke-width="14" stroke-linecap="round"/></g>', "s8", "s9"))
# Schächte / Zugangsstollen (s4)
shafts = [(f"M900 {surf(900)} L900 {TY}", "SCHACHT SEDRUN"), (f"M230 {surf(230):.0f} L420 {TY}", "AMSTEG"), (f"M1610 {surf(1610):.0f} L1450 {TY}", "FAIDO")]
for k, (d, lab) in enumerate(shafts):
    G.append(dr(d, 16, INK, "s4@Schächte", 0.7, -0.2 + k * 0.15, 'class="dr shaft"'))
G.append(g(f'<text x="930" y="{surf(900)+120:.0f}" font-family="JBM" font-weight="800" font-size="40" fill="{INK}">≈ 800 M TIEF</text>', "s4@Schächte", "s5"))
# Tunnel (zwei Spitzen) – Pfade werden im JS gesetzt
G.append(f'<path id="tunL" d="" stroke="{INK}" stroke-width="18" fill="none" stroke-linecap="round"/>')
G.append(f'<path id="tunR" d="" stroke="{INK}" stroke-width="18" fill="none" stroke-linecap="round"/>')
G.append(f'<circle id="tipL" r="26" fill="{PUR}" stroke="#fff" stroke-width="6"/><circle id="tipR" r="26" fill="{PUR}" stroke="#fff" stroke-width="6"/>')
G.append(f'<circle id="tipglow" cx="{MX}" cy="{TY}" r="90" fill="url(#glow)" opacity="0"/>')
G.append(f'<text id="qm" x="{MX}" y="{TY-60}" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="120" fill="{PUR}">?</text>')
# 57-km-Klammer (s3)
G.append(g(dr(f"M60 {TY+70} V{TY+100} H1940 V{TY+70}", 7, PUR, "s3@57", 0.8, -0.2), "s3@57", "s4"))
# Arbeitsstellen (s4)
G.append(g("".join(f'<circle cx="{x}" cy="{TY}" r="22" fill="{TQ}" stroke="#fff" stroke-width="5" class="ws" data-k="{k}"/>' for k, x in enumerate([60, 420, 900, 1450, 1940])), "s4@Stellen", "s5"))
# Messpunkt-Kette (s9–s14): von Bodio (rechts) bis zur rechten Tunnelspitze
CH_X = [1940 - 40 * k for k in range(21)]
G.append(f'<g id="chain">' + "".join(f'<g class="mp" data-k="{k}" opacity="0"><path d="M{x-12} {TY+30} L{x} {TY+8} L{x+12} {TY+30}" fill="none" stroke="{INK}" stroke-width="4"/><circle cx="{x}" cy="{TY}" r="9" fill="#fff" stroke="{PUR}" stroke-width="5"/></g>' for k, x in enumerate(CH_X)) + '</g>')
G.append(f'<line id="laser" x1="0" y1="0" x2="0" y2="0" stroke="{RED}" stroke-width="7" stroke-linecap="round" opacity="0"/>')
G.append(f'<g id="fans" opacity="0">' + "".join(f'<path d="M{x} {TY} L{x-70} {TY-9} M{x} {TY} L{x-70} {TY+9}" stroke="{RED}" stroke-width="3" fill="none"/>' for x in CH_X[2:19:4]) + '</g>')
G.append(f'<path id="drift" d="" stroke="{RED}" stroke-width="8" fill="none" stroke-dasharray="18 14" opacity="0"/>')
G.append(f'<g id="miss" opacity="0"><text x="{MX+10}" y="{TY+210}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="46" fill="{RED}">✕ VERFEHLT</text></g>')
# Durchschlag-Burst (s15)
G.append(f'<g id="burst" opacity="0">' + "".join(f'<line x1="{MX+math.cos(a)*40:.1f}" y1="{TY+math.sin(a)*40:.1f}" x2="{MX+math.cos(a)*100:.1f}" y2="{TY+math.sin(a)*100:.1f}" stroke="{PUR}" stroke-width="8" stroke-linecap="round"/>' for a in [i * math.pi / 5 for i in range(10)]) + '</g>')
world = f'<svg id="wsvg" width="1000" height="800" viewBox="0 0 1000 800" style="position:absolute;left:0;top:0"><g id="camg">{"".join(G)}</g></svg>'

# --- Detail: Bohrmaschine (s5–s6), Bildschirm-Ebene im Panel ---
cut = "".join(f'<line x1="0" y1="0" x2="{math.cos(a)*62:.1f}" y2="{math.sin(a)*62:.1f}" stroke="{INK}" stroke-width="5"/>' for a in [i * math.pi / 4 for i in range(8)])
wag = "".join(f'<rect x="{x}" y="372" width="120" height="70" rx="8" fill="#fff" stroke="{INK}" stroke-width="4"/><circle cx="{x+26}" cy="452" r="10" fill="{INK}"/><circle cx="{x+94}" cy="452" r="10" fill="{INK}"/>' for x in range(-760, 560, 140))
tbm = (f'<div id="tbm" style="position:absolute;left:0;top:0;width:1000px;height:800px;opacity:0;background:#FCFCFD;overflow:hidden">'
       f'<svg width="1000" height="800" viewBox="0 0 1000 800"><rect x="0" y="0" width="1000" height="800" fill="url(#rock2)"/>'
       f'<defs><pattern id="rock2" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><line x1="0" y1="0" x2="0" y2="26" stroke="#D5D8DE" stroke-width="3"/></pattern></defs>'
       f'<rect x="-10" y="300" width="1020" height="180" fill="#FCFCFD" stroke="{INK}" stroke-width="5"/>'
       f'<g id="tbmg">{wag}<rect x="560" y="330" width="250" height="120" rx="14" fill="{PUR}" stroke="{INK}" stroke-width="5"/>'
       f'<text x="685" y="402" text-anchor="middle" font-family="JBM" font-weight="800" font-size="28" fill="#fff">BOHRKOPF</text>'
       f'<rect x="810" y="306" width="26" height="168" rx="8" fill="{INK}"/><g id="cutter" transform="translate(850 390)"><circle r="78" fill="#fff" stroke="{INK}" stroke-width="6"/>{cut}<circle r="14" fill="{PUR}"/></g>'
       f'<g transform="translate(520 400)"><circle cx="0" cy="-34" r="7" fill="{INK}"/><path d="M0 -26 V0 M0 -18 L-9 -8 M0 -18 L9 -8 M0 0 L-7 16 M0 0 L7 16" stroke="{INK}" stroke-width="4" stroke-linecap="round"/></g></g>'
       f'<path id="tbmbr" d="M40 540 H900 M40 520 V560 M900 520 V560" stroke="{PUR}" stroke-width="6" fill="none"/>'
       f'<text x="470" y="610" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="64" fill="{PUR}">◀ ÜBER 400 M</text>'
       f'<text id="tbmq" x="690" y="270" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="150" fill="{PUR}" opacity="0">?</text>'
       f'<text x="120" y="290" font-family="JBM" font-weight="800" font-size="22" fill="{INK2}">MENSCH ZUM VERGLEICH →</text></svg></div>')
# --- Großzahl-Ebene ---
big = (f'<div id="big57" class="num" style="position:absolute;left:0;width:1000px;top:40px;text-align:center;font-size:180px;color:{PUR};opacity:0">57 KM</div>'
       f'<div id="big2010" class="num" style="position:absolute;left:0;width:1000px;top:40px;text-align:center;font-size:190px;color:{PUR};opacity:0">2010</div>')
# --- Kreiselkompass (s13) + Erde (s14) ---
gyro = (f'<div id="gyro" class="gcard" style="position:absolute;left:330px;top:60px;width:340px;opacity:0;text-align:center">'
        f'<svg width="300" height="230" viewBox="-150 -115 300 230"><ellipse rx="120" ry="34" fill="none" stroke="{INK}" stroke-width="6"/>'
        f'<g id="gyrod"><ellipse rx="86" ry="86" fill="none" stroke="{PUR}" stroke-width="10"/><line x1="-86" y1="0" x2="86" y2="0" stroke="{PUR}" stroke-width="6"/></g>'
        f'<line x1="0" y1="-105" x2="0" y2="105" stroke="{INK}" stroke-width="6"/><circle r="12" fill="{INK}"/></svg>'
        f'<div class="mono" style="font-size:26px;font-weight:800">KREISELKOMPASS</div></div>')
mer = "".join(f'<ellipse class="mer" data-k="{k}" cx="0" cy="0" rx="60" ry="110" fill="none" stroke="{TQ}" stroke-width="4"/>' for k in range(4))
earth = (f'<div id="earth" class="gcard" style="position:absolute;left:300px;top:40px;width:400px;opacity:0;text-align:center">'
         f'<svg width="360" height="290" viewBox="-180 -145 360 290"><circle r="110" fill="#E9FBF8" stroke="{INK}" stroke-width="6"/>{mer}'
         f'<line x1="-130" y1="0" x2="130" y2="0" stroke="{TQ}" stroke-width="4"/>'
         f'<path d="M0 -112 V-140 M-12 -126 L0 -142 L12 -126" stroke="{PUR}" stroke-width="7" fill="none" stroke-linecap="round"/><text x="22" y="-118" font-family="JBM" font-weight="800" font-size="30" fill="{PUR}">N</text>'
         f'<path id="spin" d="M-150 30 A150 40 0 0 0 150 30" stroke="{INK}" stroke-width="5" fill="none"/><path d="M150 30 l-24 -6 l10 20 z" fill="{INK}"/>'
         f'<g transform="translate(130 90)"><path d="M-22 -26 V6 A22 22 0 0 0 22 6 V-26" stroke="{RED}" stroke-width="12" fill="none"/><line x1="-34" y1="-34" x2="34" y2="34" stroke="{RED}" stroke-width="6"/></g></svg>'
         f'<div class="mono" style="font-size:24px;font-weight:800">ERDDREHUNG → NORDEN · OHNE MAGNET</div></div>')
# --- Abweichung (s16–s18) ---
def hb(idn, lab, col, w, dashed=False):
    st = f"border:4px dashed {INK2};background:transparent" if dashed else f"background:{col}"
    return (f'<div style="display:flex;align-items:center;gap:18px;margin:18px 0"><div class="mono" style="width:230px;font-size:28px;font-weight:800;text-align:right">{lab}</div>'
            f'<div style="position:relative;width:600px;height:64px"><div id="{idn}" style="position:absolute;left:0;top:0;height:64px;width:{w}px;border-radius:12px;{st};transform-origin:left"></div></div></div>')
dev = (f'<div id="dev" style="position:absolute;left:0;top:0;width:1000px;height:800px;opacity:0;background:#FCFCFD">'
       f'<div id="devq" class="num" style="position:absolute;left:0;width:1000px;top:60px;text-align:center;font-size:150px;color:{PUR}">?</div>'
       f'<div id="devbars" style="position:absolute;left:40px;top:300px">'
       + hb("bar8", "SEITLICH", PUR, 192) + hb("bar1", "HÖHE", TQ, 24) + hb("bar25", "ERLAUBT", "", 600, True) +
       f'</div><div id="devnum" class="row" style="position:absolute;left:0;width:1000px;top:70px;justify-content:center;gap:60px">'
       f'<div class="num" id="n8" style="font-size:150px;color:{PUR}">8 CM</div><div class="num" id="n1" style="font-size:150px;color:{TQ}">1 CM</div></div>'
       f'<div class="mono" id="n25" style="position:absolute;left:0;width:1000px;top:640px;text-align:center;font-size:40px;font-weight:800;color:#5D616B">BIS 25 CM ERLAUBT ✓</div></div>')
panel = world + tbm + big + gyro + earth + dev
stage.append(mm(panel, 40, 440, 1000, 800, A("s1", "end", -0.6) + ' data-sfx="none"'))

# ---- Overlays ----
def omk(text, x, y, i, o, d=0.0, col=PUR):
    stage.append(f'<div class="el mk" {A(i, o, d)} style="left:{x}px;top:{y}px;gap:10px"><span class="pin" style="background:{col}"></span><span class="mono lab" style="color:{col};border-color:{col};font-size:30px">{text}</span></div>')
stage.append(el(f'<div class="chip mono" style="font-size:26px;font-weight:800;background:#fff;border-color:{PUR};color:{PUR}">MEGA-PROJEKTE · FOLGE 3</div>', 40, 1160, A("s1", "s3", -1.0) + ' data-sfx="none"', 1000, CENTER))
omk("🇨🇭 GOTTHARD-BASISTUNNEL", 300, 1172, "s3@Gotthard-Basistunnel", "s3@57", -0.1, INK)
omk("2016: LÄNGSTER BAHNTUNNEL DER WELT", 190, 1172, "s3@längste", "s4", -0.2, PUR)
omk("MEHRERE BAUSTELLEN GLEICHZEITIG", 210, 1172, "s4@mehreren", "s5", -0.1, TQ)
omk("GPS ✓", 450, 1172, "s7@GPS", "s8", -0.1, TQ)
omk("IM BERG: KEIN SIGNAL", 330, 1172, "s8@nicht", "s9", 0.0, RED)
omk("MESSPUNKT-KETTE", 380, 1172, "s9@Kette", "s10", -0.1, PUR)
omk("ABSTAND · RICHTUNG · HÖHE", 260, 1172, "s10@Abstand", "s11", -0.1, RED)
omk("WINZIGER FEHLER PRO MESSUNG", 230, 1172, "s11@winzigen", "s12", -0.1, RED)
stage.append(el('<div class="stamp mono" style="font-size:56px">ABGEDRIFTET</div>', 40, 1070, A("s12@abdriften", "s13", 0.1), 1000, CENTER))
stage.append(el(f'<div class="chip mono" style="font-size:34px;padding:12px 22px;font-weight:800;background:#fff;border-color:{TQ}">≈ EINE HANDBREIT ✓</div>', 40, 1160, A("s18@25", "end", 0.2), 1000, CENTER))
stage.append(el('<div class="note mono">SCHEMATISCH · NICHT MASSSTÄBLICH</div>', 60, 456, A("s2", "s15", 0.3) + ' data-sfx="none"'))
stage.append(el(f'<div style="font-size:0">{cnt(57, "s3@57", 0, 0.0)}{cnt(2010, "s15@2010", 0, 0.0)}{cnt(8, "s17@8", 0, 0.0)}</div>', 0, 0, A("s3", "end") + ' data-sfx="none"'))

cam = [("s1", 0, 1080, 520, 0.80), ("s2", 0.5, 1100, 560, 0.95), ("s3", -0.1, 1000, 440, 0.52), ("s4", -0.1, 1000, 440, 0.52),
       ("s5", -0.2, 1000, 440, 0.52), ("s5", 0.6, 1140, 640, 5.5), ("s7", -0.25, 1140, 640, 5.5), ("s7", 0.45, 1000, 150, 0.40),
       ("s8", -0.1, 1000, 150, 0.40), ("s8", 0.4, 1150, 300, 0.62), ("s9", -0.1, 1150, 300, 0.62), ("s9", 0.6, 1540, 600, 0.95),
       ("s11", -0.1, 1540, 600, 0.95), ("s11", 0.5, 1500, 620, 1.25), ("s12", -0.1, 1500, 620, 1.25), ("s12", 0.6, 1300, 660, 0.85),
       ("s15", -0.2, 1300, 660, 0.85), ("s15", 0.5, MX, TY, 2.2), ("end", 0, MX, TY, 2.2)]
PANJS = dict(cam=cam, ty=TY, mx=MX, chain=CH_X)

# ---- End card (identisch zum Template) ----
logo = open("../brand/out/missionwissen-logo-transparent-dunkel.svg").read()
logo = re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="820" height="253"', logo, count=1)
endcard = f'<div class="el" {A("end",None,0.1)} style="left:130px;top:470px">{logo}</div>' + f'<div class="el" {A("end",None,0.5)} style="left:0;width:1080px;top:790px;display:flex;justify-content:center"><div class="row" style="gap:28px"><div class="follow">+&nbsp;Folgen</div><div class="follow">🔖&nbsp;Speichern</div></div></div>' + f'<div class="el" {A("end",None,0.7)} style="left:0;width:1080px;top:935px;text-align:center"><div class="mono small grey">JEDEN TAG EIN BISSCHEN SCHLAUER</div></div>'
robots = "".join(f'<div class="pose" data-pose="{n}">{robot_svg("r"+n[:2]+"-", **k)}</div>' for n, k in POSES.items())
mono = '<svg width="72" height="72" viewBox="0 0 80 80" fill="none"><g stroke="#0B0B10" stroke-width="6" stroke-linecap="round"><path d="M20 32 V24 a10 10 0 0 1 20 0 V32 M40 24 a10 10 0 0 1 20 0 V32"/><path d="M20 48 V56 a10 10 0 0 0 20 0 V48 M40 56 a10 10 0 0 0 20 0 V48"/></g><circle cx="40" cy="40" r="3.2" fill="#7B3FE4"/></svg>'

STAGEJS = open("part_js.js").read()
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
