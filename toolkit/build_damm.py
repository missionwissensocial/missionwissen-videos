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
HOOK = '<div class="mono" style="display:inline-block;font-family:JBM;font-size:28px;font-weight:800;letter-spacing:.02em;color:#7B3FE4;background:#F1EBFD;border:2px solid #7B3FE4;border-radius:10px;padding:6px 14px;margin-bottom:14px">MEGA-PROJEKTE · FOLGE 1</div><br>Kann ein <span style="color:#7B3FE4">Staudamm</span> die Erde bremsen?'
B = [
 ("b1", 0, HOOK, "Kann ein *einziger* *Staudamm* die *Erde* *langsamer* drehen lassen?", "staunt"),
 ("b2", 0, HOOK, "Einer schon: der *Drei-Schluchten-Damm* in *China.*", None),
 ("b3", 0, "", "Das *stärkste* *Wasserkraftwerk* der Welt.", None),
 ("b4", 0, "", "Er staut den *Jangtse,* den längsten Fluss Asiens.", None),
 ("b5", 0, "", "*1994* begann der Bau.", None),
 ("b6", 0, "", "Zuerst leitete man den Fluss zur *Seite* um.", None),
 ("b7", 0, "", "Dann gossen *Zehntausende* *Arbeiter* eine Mauer aus *Beton.*", None),
 ("b8", 0, "", "Über *zwei* *Kilometer* lang und rund *180* *Meter* hoch.", None),
 ("b9", 0, "", "Höher als der *Kölner* *Dom.*", None),
 ("b10", 0, "", "*2006* stand die Mauer.", None),
 ("b11", 0, "", "Dahinter *stieg* das *Wasser.*", None),
 ("b12", 0, "", "Es entstand ein *See,* über *600* *Kilometer* lang.", None),
 ("b13", 0, "", "So weit wie von *Hamburg* nach *München.*", None),
 ("b14", 0, "", "Doch im Tal, das jetzt unter Wasser liegt, lebten *Menschen.*", None),
 ("b15", 0, "", "Über eine *Million* mussten *umziehen.*", None),
 ("b16", 0, "", "Ganze *Städte* wurden weiter *oben* am Hang neu gebaut.", None),
 ("b17", 0, "", "*Tempel,* *Gräber* und über *tausend* historische Stätten liegen heute *unter* *Wasser.*", None),
 ("b18", 0, "", "Und was *bringt* der Damm?", None),
 ("b19", 0, "", "*32* riesige *Turbinen* machen *Strom.*", None),
 ("b20", 0, "", "Im Rekordjahr *2020* so viel wie ein *Fünftel* des deutschen Stromverbrauchs in einem Jahr.", None),
 ("b21", 0, "", "Bei *Starkregen* fängt der See Wasser auf und *schützt* so Millionen Menschen vor *Hochwasser.*", None),
 ("b22", 0, "", "Und große *Frachtschiffe* kommen jetzt vom Meer aus über *2000* *Kilometer* weit ins Land.", None),
 ("b23", 0, "", "Und die *Erde?*", None),
 ("b24", 0, "", "Im See stecken rund *40* *Milliarden* *Tonnen* Wasser.", None),
 ("b25", 0, "", "Früher floss es *unten* im Tal.", None),
 ("b26", 0, "", "Jetzt liegt es viel *höher,* also weiter weg vom *Erdmittelpunkt.*", None),
 ("b27", 0, "", "Wie bei einer *Eiskunstläuferin,* die die *Arme* *ausstreckt:* Sie dreht sich *langsamer.*", None),
 ("b28", 0, "", "*Genauso* die *Erde.*", None),
 ("b29", 0, "", "Forscher der *NASA* haben berechnet: Jeder Tag ist dadurch *60* *Milliardstel* *Sekunden* länger.", None),
 ("b30", 0, "", "*Unvorstellbar* *wenig.*", None),
 ("b31", 0, "", "Und weil so viel *Gewicht* an einer Stelle sitzt, hat sich auch die *Erdachse* *verschoben.*", None),
 ("b32", 0, "", "Um etwa *zwei* *Zentimeter.*", None),
 ("b33", 0, "", "Und wenn der Damm *bricht,* kippt dann die *Erdachse?*", None),
 ("b34", 0, "", "*Nein.* Sie rutscht nur diese *zwei* *Zentimeter* zurück.", None),
 ("b35", 0, "", "Die echte *Gefahr* wäre die *Flutwelle.*", None),
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



# ================= Bühne: Globus/Karte (#msvg) + Tal-Ansicht (#vsvg), Zoom-Übergänge =================
import math
GEO = json.load(open("geo.json"))
CENTER = "display:flex;justify-content:center"
WAT = "#19C6B4"; WAT2 = "#0E9C8E"; CON1 = "#E9EBEF"; CON2 = "#C9CDD5"; GRD = "#F3F0EA"
PW, PH = 1080, 880; PTOP = 400

# ---------- Tal (Frontansicht) ----------
LS = [(0, 250), (110, 280), (200, 400), (270, 560), (300, 700)]
RS = [(1080, 240), (980, 280), (890, 400), (810, 560), (780, 700)]
def pts(p): return " ".join(f"{x},{y}" for x, y in p)
def y_on(poly, x):
    for (a, b), (c, d) in zip(poly, poly[1:]):
        lo, hi = min(a, c), max(a, c)
        if lo <= x <= hi and c != a: return b + (d - b) * (x - a) / (c - a)
    return poly[-1][1]
def x_on(poly, y):
    for (a, b), (c, d) in zip(poly, poly[1:]):
        if b <= y <= d: return a + (c - a) * (y - b) / (d - b)
    return poly[-1][0]
V = []
V.append(f'<defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CON1}"/><stop offset="1" stop-color="{CON2}"/></linearGradient>'
         f'<linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WAT}" stop-opacity=".55"/><stop offset="1" stop-color="{WAT2}" stop-opacity=".75"/></linearGradient>'
         f'<linearGradient id="fg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3E8F98"/><stop offset="1" stop-color="#245F6B"/></linearGradient>'
         f'<pattern id="hat" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="9" stroke="#B9B2A3" stroke-width="1.3"/></pattern>'
         f'<clipPath id="vi"><polygon points="{pts(LS + RS[::-1] + [(1080, 0), (0, 0)])}"/></clipPath>'
         f'<clipPath id="dpc"><polygon points="{pts(LS[1:] + RS[1:][::-1])}"/></clipPath>'
         f'<clipPath id="dbuild"><rect id="dclip" x="0" y="700" width="1080" height="0"/></clipPath>'
         f'<clipPath id="floodc"><rect id="floodr" x="0" y="700" width="1080" height="0"/></clipPath></defs>')
# Fernberge
V.append(f'<polygon points="0,330 140,250 300,290 430,215 570,265 700,205 860,262 1080,230 1080,460 0,460" fill="#F1F2F5" stroke="#A9AEB8" stroke-width="2"/>')
# See / Fluss (Wasser im Tal, Pegel per JS)
V.append(f'<g clip-path="url(#vi)"><rect id="lake" x="0" y="680" width="1080" height="240" fill="url(#wg)"/>'
         f'<path id="lakesurf" d="M0 680 H1080" stroke="#fff" stroke-width="3" opacity=".8"/></g>')
# alte Häuser, Tempel, Gräber im Tal (vor dem Wasser gezeichnet -> liegen "unter" dem halbtransparenten Wasser? -> Wasser kommt danach nochmal)
old = []
for k, (x, w, h) in enumerate([(318, 34, 26), (356, 40, 30), (402, 30, 24), (440, 44, 32), (492, 36, 26), (534, 42, 30), (712, 38, 28), (752, 26, 22)]):
    yb = 700
    old.append(f'<rect x="{x}" y="{yb-h}" width="{w}" height="{h}" fill="#fff" stroke="#2B2D35" stroke-width="2.4"/>'
               f'<path d="M{x-5} {yb-h} L{x+w/2} {yb-h-16} L{x+w+5} {yb-h} Z" fill="#E8E1D3" stroke="#2B2D35" stroke-width="2.4" stroke-linejoin="round"/>'
               f'<rect x="{x+w/2-5}" y="{yb-12}" width="10" height="12" fill="#2B2D35" opacity=".7"/>')
# Tempel (eigene, schlichte Form)
tx = 640
old.append(f'<g id="temple"><rect x="{tx-30}" y="664" width="60" height="36" fill="#fff" stroke="#2B2D35" stroke-width="2.4"/>'
           f'<path d="M{tx-46} 666 Q{tx} 650 {tx+46} 666 Q{tx} 660 {tx-46} 666 Z" fill="{PUR}" stroke="#2B2D35" stroke-width="2"/>'
           f'<rect x="{tx-20}" y="636" width="40" height="22" fill="#fff" stroke="#2B2D35" stroke-width="2.2"/>'
           f'<path d="M{tx-34} 638 Q{tx} 622 {tx+34} 638 Q{tx} 632 {tx-34} 638 Z" fill="{PUR}" stroke="#2B2D35" stroke-width="2"/>'
           f'<line x1="{tx}" y1="622" x2="{tx}" y2="608" stroke="#2B2D35" stroke-width="2.4"/><rect x="{tx-8}" y="680" width="16" height="20" fill="#2B2D35" opacity=".7"/></g>')
for gx in (582, 596, 610):
    old.append(f'<path d="M{gx-5} 700 V690 Q{gx} 683 {gx+5} 690 V700 Z" fill="#D9DBE0" stroke="#2B2D35" stroke-width="1.6"/>')
V.append(f'<g id="oldtown">{"".join(old)}</g>')
# Wasser-Overlay über den Häusern (gleicher Pegel)
V.append(f'<g clip-path="url(#vi)"><rect id="lake2" x="0" y="680" width="1080" height="240" fill="{WAT}" opacity=".42"/></g>')
# Hänge
V.append(f'<polygon points="{pts(LS + [(300, 880), (0, 880)])}" fill="{GRD}" stroke="#2B2D35" stroke-width="3.2" stroke-linejoin="round"/>'
         f'<polygon points="{pts(LS + [(300, 880), (0, 880)])}" fill="url(#hat)" opacity=".55"/>'
         f'<polygon points="{pts(RS + [(780, 880), (1080, 880)])}" fill="{GRD}" stroke="#2B2D35" stroke-width="3.2" stroke-linejoin="round"/>'
         f'<polygon points="{pts(RS + [(780, 880), (1080, 880)])}" fill="url(#hat)" opacity=".55"/>')
# Umleitungstunnel links
V.append(f'<g id="tunnel" opacity="0"><path d="M246 700 V672 Q262 650 280 672 V700 Z" fill="#1C1E25" stroke="#2B2D35" stroke-width="2.5"/>'
         f'<path id="divflow" d="M330 692 Q300 692 270 690" stroke="#fff" stroke-width="3" fill="none" stroke-dasharray="10 12"/></g>')
# Menschen (wandern auf die Hänge)
PP = []
import random
rr = random.Random(4)
for k in range(34):
    sx = 320 + (k * 13.7) % 440; sy = 696 - rr.uniform(0, 8)
    left = sx < 540
    ty = rr.uniform(262, 330)
    tx_ = (x_on(LS, ty) - rr.uniform(8, 60)) if left else (x_on(RS, ty) + rr.uniform(8, 60))
    ty = y_on(LS if left else RS, tx_) - 6
    PP.append(f'<circle class="pp" r="5.2" fill="{PUR}" stroke="#fff" stroke-width="1.6" data-sx="{sx:.1f}" data-sy="{sy:.1f}" data-tx="{tx_:.1f}" data-ty="{ty:.1f}" data-k="{k}"/>')
V.append(f'<g id="people">{"".join(PP)}</g>')
# Neue Städte am Hang (oben)
cty_ = []
for k, (x, h) in enumerate([(14, 70), (44, 104), (76, 84), (124, 62), (946, 66), (990, 100), (1024, 78), (1056, 92)]):
    yb = y_on(LS if x < 540 else RS, x + 12) + 4
    cty_.append(f'<g class="tw" data-k="{k}" data-yb="{yb:.1f}"><rect x="{x}" y="{yb-h:.1f}" width="26" height="{h}" fill="#fff" stroke="#2B2D35" stroke-width="2.2"/>'
                + "".join(f'<rect x="{x+5+(j%2)*10}" y="{yb-h+8+(j//2)*14:.1f}" width="6" height="7" fill="{PUR}" opacity=".55"/>' for j in range(int(h // 14) * 2 - 2)) + '</g>')
V.append(f'<g id="city">{"".join(cty_)}</g>')
# Damm
dam = []
dam.append(f'<polygon points="{pts(LS[1:] + RS[1:][::-1])}" fill="url(#cg)" stroke="#2B2D35" stroke-width="3.2" stroke-linejoin="round"/>')
joints = "".join(f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#AEB3BD" stroke-width="1.4"/>' for y in range(325, 700, 25))
joints += "".join(f'<line x1="{x}" y1="{300 + (x // 48 % 2) * 25}" x2="{x}" y2="700" stroke="#C3C7CF" stroke-width="1.1" stroke-dasharray="25 25"/>' for x in range(130, 970, 48))
dam.append(f'<g clip-path="url(#dpc)">{joints}</g>')
gates = "".join(f'<rect x="{478 + 20 * k}" y="318" width="12" height="230" rx="3" fill="#8D939E" stroke="#2B2D35" stroke-width="1.6"/>' for k in range(7))
dam.append(gates)
dam.append(f'<rect x="306" y="628" width="468" height="70" fill="#DADDE3" stroke="#2B2D35" stroke-width="2.2"/>')
dam.append("".join(f'<rect class="turb" x="{312 + k * 14.4:.1f}" y="644" width="9" height="34" rx="2" fill="#5D616B"/>' for k in range(32)))
dam.append(f'<line x1="125" y1="300" x2="965" y2="300" stroke="#2B2D35" stroke-width="7" stroke-linecap="round"/>')
dam.append(f'<g id="crack" opacity="0"><path class="dr" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M540 300 L528 360 L556 410 L522 470 L560 540 L530 610 L548 700" stroke="{RED}" stroke-width="6" fill="none" stroke-linejoin="round" data-a="b35" data-dl="0.0" data-dur="0.5"/></g>')
V.append(f'<g id="vdam"><g clip-path="url(#dbuild)">{"".join(dam)}</g>'
         + "".join(f'<g class="crane" data-x="{x}" data-k="{k}"><line x1="0" y1="0" x2="0" y2="-120" stroke="#2B2D35" stroke-width="5"/>'
                   f'<g class="jib"><line x1="-50" y1="-118" x2="110" y2="-118" stroke="#2B2D35" stroke-width="4"/><line x1="0" y1="-140" x2="-50" y2="-118" stroke="#2B2D35" stroke-width="2"/><line x1="0" y1="-140" x2="110" y2="-118" stroke="#2B2D35" stroke-width="2"/>'
                   f'<line class="hook" x1="80" y1="-118" x2="80" y2="-70" stroke="#2B2D35" stroke-width="1.6"/><rect class="load" x="70" y="-70" width="20" height="12" fill="{PUR}"/></g>'
                   f'<line x1="-12" y1="0" x2="12" y2="0" stroke="#2B2D35" stroke-width="6"/></g>' for k, x in enumerate((360, 560, 760)))
         + "".join(f'<circle class="wk" r="4" fill="{PUR}" data-k="{k}"/>' for k in range(26)) + '</g>')
# Turbinen-Wasser (b19)
V.append(f'<g id="jets" opacity="0">' + "".join(f'<path class="jet" d="M{330 + k * 60} 700 q8 40 -4 90" stroke="{WAT}" stroke-width="7" fill="none" stroke-linecap="round" opacity=".8"/>' for k in range(8)) + '</g>')
# Maße
V.append(f'<g id="dims" opacity="0"><line x1="125" y1="262" x2="965" y2="262" stroke="{PUR}" stroke-width="4"/>'
         f'<path d="M125 262 l18 -10 v20 z M965 262 l-18 -10 v20 z" fill="{PUR}"/>'
         f'<rect x="452" y="232" width="176" height="56" rx="10" fill="#fff" stroke="{PUR}" stroke-width="3"/><text x="540" y="273" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="34" fill="{PUR}">2,3 KM</text>'
         f'<g id="hdim"><line x1="1030" y1="300" x2="1030" y2="700" stroke="{INK}" stroke-width="4"/><path d="M1030 300 l-10 18 h20 z M1030 700 l-10 -18 h20 z" fill="{INK}"/>'
         f'<rect x="968" y="472" width="104" height="54" rx="10" fill="#fff" stroke="{INK}" stroke-width="3"/><text x="1020" y="510" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="27" fill="{INK}">181 M</text></g></g>')
# Kölner Dom (eigene, schlichte Silhouette, maßstäblich 157 m vs. 181 m)
DH = 400 * 157 / 181; dx0 = 600; top = 700 - DH
dom = (f'<g id="dom" opacity="0"><path d="M{dx0} 700 V{top+90:.0f} L{dx0+22} {top:.0f} L{dx0+44} {top+90:.0f} V700 Z M{dx0+110} 700 V{top+90:.0f} L{dx0+132} {top:.0f} L{dx0+154} {top+90:.0f} V700 Z" fill="#fff" stroke="{PUR}" stroke-width="4" stroke-linejoin="round"/>'
       f'<path d="M{dx0+44} 700 V{top+200:.0f} L{dx0+77} {top+160:.0f} L{dx0+110} {top+200:.0f} V700 Z" fill="#fff" stroke="{PUR}" stroke-width="4" stroke-linejoin="round"/>'
       + "".join(f'<rect x="{dx0+12+o}" y="{top+120+j*70:.0f}" width="20" height="40" rx="10" fill="none" stroke="{PUR}" stroke-width="2.4"/>' for o in (0, 110) for j in range(3))
       + f'<line x1="{dx0-30}" y1="{top:.0f}" x2="{dx0+190}" y2="{top:.0f}" stroke="{PUR}" stroke-width="2.4" stroke-dasharray="8 8"/>'
       f'<rect x="{dx0-296}" y="{top-24:.0f}" width="274" height="48" rx="10" fill="#fff" stroke="{PUR}" stroke-width="3"/><text x="{dx0-159}" y="{top+10:.0f}" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="20" fill="{PUR}">KÖLNER DOM 157 M</text></g>')
V.append(dom)
# Unterlauf: Fluss + Stadt im Vordergrund (b21, b35)
town = [f'<path d="M490 700 L590 700 L700 880 L380 880 Z" fill="url(#wg)"/>']
for k, (x, y, w, h) in enumerate([(318, 800, 44, 32), (372, 830, 36, 28), (308, 852, 40, 26), (716, 806, 46, 34), (770, 836, 40, 28), (726, 856, 36, 22), (420, 858, 30, 20)]):
    town.append(f'<g class="th"><rect x="{x}" y="{y-h}" width="{w}" height="{h}" fill="#fff" stroke="#2B2D35" stroke-width="2.4"/>'
                f'<path d="M{x-5} {y-h} L{x+w/2} {y-h-15} L{x+w+5} {y-h} Z" fill="#E8E1D3" stroke="#2B2D35" stroke-width="2.4" stroke-linejoin="round"/></g>')
V.insert(V.index(next(v for v in V if 'id="tunnel"' in v)), f'<rect x="290" y="700" width="500" height="180" fill="{GRD}"/><rect x="290" y="700" width="500" height="180" fill="url(#hat)" opacity=".55"/><line x1="300" y1="700" x2="780" y2="700" stroke="#2B2D35" stroke-width="3"/>')
V.append(f'<g id="town" opacity="0">{"".join(town)}</g>')
V.append(f'<g id="flood" opacity="0" clip-path="url(#floodc)"><path d="M300 700 H780 L1080 880 H0 Z" fill="url(#fg)" opacity=".92"/>'
         + "".join(f'<path class="foam" d="M{-40 + k * 110} 0 q30 -18 60 0 t60 0" stroke="#fff" stroke-width="4" fill="none" opacity=".8"/>' for k in range(11)) + '</g>')
# Regen
V.append('<g id="rain" opacity="0">' + "".join(f'<line class="rd" data-k="{k}" x1="0" y1="0" x2="-8" y2="34" stroke="{WAT2}" stroke-width="3" stroke-linecap="round" opacity=".7"/>' for k in range(46)) + '</g>')
vsvg = f'<svg id="vsvg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" style="position:absolute;left:0;top:0"><g id="vcam">{"".join(V)}</g></svg>'

# ---------- Globus / Karte ----------
M = []
M.append(f'<defs><radialGradient id="oc" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#F2FBFA"/><stop offset="1" stop-color="#CDEDEA"/></radialGradient>'
         f'<radialGradient id="glow"><stop offset="0" stop-color="{PUR}" stop-opacity=".55"/><stop offset="1" stop-color="{PUR}" stop-opacity="0"/></radialGradient></defs>')
M.append(f'<circle id="ocean" cx="0" cy="0" r="400" fill="url(#oc)" stroke="#2B2D35" stroke-width="2.5" vector-effect="non-scaling-stroke"/>')
M.append(f'<path id="grat" fill="none" stroke="#9FD9D3" stroke-width="1" vector-effect="non-scaling-stroke" opacity=".7"/>')
M.append(f'<path id="land1" fill="#FFFFFF" stroke="#2B2D35" stroke-width="1.6" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>')
M.append(f'<path id="land5" fill="#FFFFFF" stroke="#2B2D35" stroke-width="1.6" vector-effect="non-scaling-stroke" stroke-linejoin="round" opacity="0"/>')
M.append(f'<path id="cn" fill="#EFE7FD" stroke="{PUR}" stroke-width="2.2" vector-effect="non-scaling-stroke" opacity="0"/>')
M.append(f'<path id="yz" fill="none" stroke="#2F9FD0" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
M.append(f'<path id="resg" fill="none" stroke="{WAT}" stroke-opacity=".35" stroke-linecap="round" stroke-linejoin="round" opacity="0"/>')
M.append(f'<path id="res" fill="none" stroke="{WAT2}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
M.append(f'<path id="route" fill="none" stroke="{PUR}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
M.append(f'<g id="deg" opacity="0"><path id="dep" fill="#F4F0FF" stroke="{PUR}" stroke-width="2" vector-effect="non-scaling-stroke"/>'
         f'<line id="dline" stroke="{PUR}" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></g>')
M.append(f'<circle id="damglow" r="40" fill="url(#glow)" opacity="0"/>')
M.append(f'<circle id="dampulse" r="10" fill="none" stroke="{PUR}" opacity="0"/>')
M.append(f'<circle id="dam" r="7" fill="{PUR}" stroke="#fff" opacity="0"/>')
M.append(f'<g id="ship" opacity="0"><path d="M-22 -2 L18 -2 L24 -8 L24 2 L16 9 L-18 9 Z" fill="#fff" stroke="#2B2D35" stroke-width="2.2" stroke-linejoin="round"/>'
         f'<rect x="-14" y="-10" width="9" height="8" fill="{PUR}"/><rect x="-4" y="-10" width="9" height="8" fill="{WAT}"/><rect x="6" y="-10" width="8" height="8" fill="#E8A33D"/><rect x="-22" y="-18" width="8" height="16" fill="#fff" stroke="#2B2D35" stroke-width="2"/></g>')
M.append(f'<g id="axis" opacity="0"><line x1="0" y1="-560" x2="0" y2="560" stroke="{PUR}" stroke-width="5" stroke-dasharray="18 12" vector-effect="non-scaling-stroke"/>'
         f'<circle cx="0" cy="-346.4" r="9" fill="{PUR}" stroke="#fff" stroke-width="3"/></g>')
M.append(f'<g id="spin" opacity="0"><path d="M-300 -330 A440 440 0 0 1 300 -330" fill="none" stroke="{PUR}" stroke-width="7" stroke-linecap="round"/><path d="M300 -330 l-36 -4 l22 -26 z" fill="{PUR}"/></g>')
M.append('<g id="labels"></g>')
msvg = f'<svg id="msvg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" style="position:absolute;left:0;top:0"><g id="mcam">{"".join(M)}</g></svg>'

# Karten-Labels: (text, lon, lat, in, out, px, farbe, dx, dy, anchor)
LB = [("CHINA", 103, 36, "b2@China", "b5", 30, PUR, 0, 0, "middle"),
      ("DREI-SCHLUCHTEN-DAMM", GEO["dam"][0], GEO["dam"][1], "b2@Drei-Schluchten-Damm", "b5", 24, INK, 16, -18, "start"),
      ("JANGTSE", 116, 30.2, "b4@Jangtse", "b5", 24, "#2F9FD0", 0, 34, "middle"),
      ("CHONGQING", GEO["cq"][0], GEO["cq"][1], "b12@See", "b14", 22, INK, -14, -14, "end"),
      ("DAMM", GEO["dam"][0], GEO["dam"][1], "b12", "b14", 22, PUR, 14, -14, "start"),
      ("SHANGHAI", GEO["sh"][0], GEO["sh"][1], "b22", "b23", 22, INK, 0, 34, "middle"),
      ("CHONGQING", GEO["cq"][0], GEO["cq"][1], "b22@Kilometer", "b23", 22, INK, 0, -16, "middle")]
PANJS = dict(geo=GEO, lb=LB)

panel = f'<div id="mlay" style="position:absolute;inset:0">{msvg}</div><div id="vlay" style="position:absolute;inset:0;opacity:0">{vsvg}</div>'
stage.append(f'<div class="mm el" {A("b1", "end", -1)} data-sfx="none" style="left:0;top:{PTOP}px;width:{PW}px;height:{PH}px;border-radius:0;border-left:0;border-right:0">{panel}</div>')

# ---- Overlays (Bildschirm-Ebene, höchstens eins gleichzeitig) ----
def chip(text, y, i, o, d=0.0, col=PUR, sfx="pop"):
    stage.append(el(f'<div class="chip mono" style="font-size:32px;padding:12px 22px;font-weight:800;background:#fff;border-color:{col};color:{col}">{text}</div>', 0, y, A(i, o, d) + f' data-sfx="{sfx}"', 1080, CENTER))
def big(inner, y, i, o, d=0.0, sfx="pop", size=150):
    stage.append(el(f'<div class="num" style="font-size:{size}px;text-align:center;white-space:nowrap">{inner}</div>', 0, y, A(i, o, d) + f' data-sfx="{sfx}"', 1080, CENTER))
chip("⚡ STÄRKSTES WASSERKRAFTWERK DER WELT", 1180, "b3", "b4", -0.1)
stage.append(f'<div class="el" {A("b5", "b11", -0.25)} data-sfx="none" style="left:0;top:410px;width:1080px;text-align:center"><div id="year" class="num" style="font-size:150px">1994</div></div>')
chip("↩ FLUSS ZUR SEITE UMGELEITET", 1180, "b6@Seite", "b7", -0.2, WAT2)
chip("👷 ZEHNTAUSENDE ARBEITER", 1180, "b7@Zehntausende", "b8", -0.1, INK)
stage.append(el('<div class="stamp mono" style="font-size:54px">✓ MAUER STEHT</div>', 0, 1150, A("b10@Mauer", "b11", -0.3), 1080, CENTER))
big(f'<span style="font-size:60px">ÜBER </span>{cnt(600, "b12@600", 0, -0.3)}<span style="font-size:80px"> KM</span>', 410, "b12@600", "b13", -0.35, "none")
chip("HAMBURG → MÜNCHEN ≈ 600 KM", 1180, "b13@Hamburg", "b14", 0.0, PUR)
chip("⏪ VORHER: DÖRFER IM TAL", 440, "b14", "b15", 0.2, INK)
big(f'<span style="font-size:60px">ÜBER </span>{cnt(1000000, "b15@Million", 0, -0.3)}', 410, "b15@Million", "b16", -0.3, "none", 130)
chip("🏙 NEUE STÄDTE WEITER OBEN", 440, "b16@Städte", "b17", -0.1, PUR)
chip("🏛 ÜBER 1.000 HISTORISCHE STÄTTEN", 440, "b17@tausend", "b18", -0.4, WAT2)
big(f'{cnt(32, "b19", 0, 0)}<span style="font-size:70px"> TURBINEN</span>', 410, "b19", "b20", -0.1, "none", 140)
# Deutschland-Karte mit 1/5
import math as _m
def de_path(sc, cx, cy):
    lo0, la0 = 10.4, 51.1
    out = ""
    for r in GEO["de"]:
        s = "M" + "L".join(f"{cx + sc*(lo-lo0)*_m.cos(_m.radians(la0)):.1f} {cy - sc*(la-la0):.1f}" for lo, la in r) + "Z"
        out += s
    return out
dpath = de_path(24, 110, 125)
decard = (f'<div class="row" style="gap:34px;background:#fff;border:3px solid #0B0B10;border-radius:22px;padding:18px 34px;box-shadow:0 8px 18px rgba(26,31,51,.12)">'
          f'<svg width="220" height="250" viewBox="0 0 220 250"><defs><clipPath id="dec"><path d="{dpath}"/></clipPath></defs>'
          f'<path d="{dpath}" fill="#F4F0FF" stroke="#0B0B10" stroke-width="3"/><rect id="defill" clip-path="url(#dec)" x="0" y="250" width="220" height="0" fill="{PUR}"/>'
          f'<path d="{dpath}" fill="none" stroke="#0B0B10" stroke-width="3"/></svg>'
          f'<div><div class="num" style="font-size:120px;color:{PUR}">⅕</div><div class="mono" style="font-size:24px;font-weight:800;line-height:1.35">DES DEUTSCHEN<br>STROMVERBRAUCHS<br><span style="color:#8A8F99">REKORDJAHR 2020</span></div></div></div>')
stage.append(el(decard, 0, 420, A("b20@Fünftel", "b21", -0.3) + ' data-sfx="glass"', 1080, CENTER))
chip("🌧 SEE FÄNGT WASSER AUF", 440, "b21@Starkregen", "b21@schützt", 0.0, WAT2)
chip("🛡 MILLIONEN MENSCHEN GESCHÜTZT ✓", 440, "b21@schützt", "b22", 0.0, PUR, "success")
big(f'<span style="font-size:60px">ÜBER </span>{cnt(2000, "b22@2000", 0, -0.2)}<span style="font-size:80px"> KM</span>', 410, "b22@2000", "b23", -0.3, "none")
big(f'{cnt(40, "b24@40", 0, -0.2)}<span style="font-size:64px"> MRD. TONNEN</span>', 410, "b24@40", "b25", -0.3, "none", 150)
# Schema-Karte Erde im Schnitt (b25-b26)
scheme = (f'<div class="gcard" style="padding:18px 26px"><svg width="560" height="400" viewBox="-280 -200 560 400">'
          f'<circle cx="0" cy="120" r="300" fill="#F2FBFA" stroke="#0B0B10" stroke-width="3"/>'
          f'<path d="M-90 -175 L-40 -190 L-10 -150 L10 -150 L40 -192 L90 -176" fill="none" stroke="#0B0B10" stroke-width="3" stroke-linejoin="round"/>'
          f'<path id="sw" d="M-28 -160 L28 -160 L12 -150 L-12 -150 Z" fill="{WAT}"/>'
          f'<circle cx="0" cy="120" r="8" fill="#0B0B10"/><text x="16" y="128" font-family="JBM" font-weight="800" font-size="20" fill="#0B0B10">ERDMITTELPUNKT</text>'
          f'<line x1="0" y1="112" x2="0" y2="-150" stroke="#8A8F99" stroke-width="2.5" stroke-dasharray="8 8"/>'
          f'<g id="sdrop"><circle cx="0" cy="-154" r="12" fill="{WAT2}" stroke="#fff" stroke-width="3"/></g>'
          f'<g id="sarrow" opacity="0"><path d="M60 -150 V-196" stroke="{PUR}" stroke-width="5"/><path d="M60 -200 l-10 16 h20 z" fill="{PUR}"/><text x="76" y="-170" font-family="JBM" font-weight="800" font-size="22" fill="{PUR}">HÖHER = WEITER WEG</text></g>'
          f'</svg><div class="mono" style="font-size:16px;color:#8A8F99;text-align:center">SCHEMATISCH · STARK ÜBERTRIEBEN</div></div>')
stage.append(el(scheme, 0, 430, A("b25", "b27", -0.2) + ' data-sfx="glass"', 1080, CENTER))
# Eiskunstläuferin
skater = (f'<div class="gcard" style="padding:14px 26px"><svg width="420" height="360" viewBox="-210 -190 420 360">'
          f'<ellipse cx="0" cy="150" rx="120" ry="16" fill="#E7F7F5"/>'
          f'<g id="sk"><circle cx="0" cy="-130" r="24" fill="#fff" stroke="#0B0B10" stroke-width="4"/>'
          f'<path d="M-16 -100 L16 -100 L22 -10 L-22 -10 Z" fill="{PUR}" stroke="#0B0B10" stroke-width="3.5" stroke-linejoin="round"/>'
          f'<path d="M-22 -10 L22 -10 L50 30 L-50 30 Z" fill="#B79BFF" stroke="#0B0B10" stroke-width="3.5" stroke-linejoin="round"/>'
          f'<line x1="-10" y1="30" x2="-10" y2="140" stroke="#0B0B10" stroke-width="7" stroke-linecap="round"/><line x1="10" y1="30" x2="10" y2="140" stroke="#0B0B10" stroke-width="7" stroke-linecap="round"/>'
          f'<line id="arml" x1="0" y1="-88" x2="-40" y2="-40" stroke="#0B0B10" stroke-width="8" stroke-linecap="round"/><line id="armr" x1="0" y1="-88" x2="40" y2="-40" stroke="#0B0B10" stroke-width="8" stroke-linecap="round"/></g>'
          f'<path id="swirl" d="M-120 100 A120 22 0 1 0 120 100" fill="none" stroke="{PUR}" stroke-width="5" stroke-linecap="round" stroke-dasharray="40 26"/>'
          f'</svg><div id="sklab" class="mono" style="font-size:30px;font-weight:800;text-align:center">SCHNELL</div></div>')
stage.append(el(skater, 0, 420, A("b27", "b28", -0.1) + ' data-sfx="glass"', 1080, CENTER))
big('<span style="font-size:96px">+0,000 000 06 s</span>', 425, "b29@60", "b31", -0.25, "pop")
stage.append(el(f'<div class="chip mono" style="font-size:28px;font-weight:800;color:#5D616B;background:#fff">PRO TAG · BERECHNUNG NASA (2005)</div>', 0, 560, A("b29@60", "b30", 0.1) + ' data-sfx="none"', 1080, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:52px">UNVORSTELLBAR WENIG</div>', 0, 600, A("b30", "b31", 0.0), 1080, CENTER))
# Lupe: Lineal 2 cm
ruler = (f'<div class="gcard" style="padding:16px 24px"><svg width="440" height="170" viewBox="0 0 440 170">'
         f'<rect x="10" y="80" width="420" height="70" rx="8" fill="#FFF7E6" stroke="#0B0B10" stroke-width="3"/>'
         + "".join(f'<line x1="{30 + k * 16}" y1="80" x2="{30 + k * 16}" y2="{80 + (34 if k % 10 == 0 else 22 if k % 5 == 0 else 14)}" stroke="#0B0B10" stroke-width="2"/>' for k in range(0, 25))
         + "".join(f'<text x="{30 + k * 160}" y="140" text-anchor="middle" font-family="JBM" font-weight="800" font-size="20">{k} cm</text>' for k in range(3))
         + f'<g id="pmark"><line x1="30" y1="20" x2="30" y2="80" stroke="{PUR}" stroke-width="4"/><circle cx="30" cy="22" r="13" fill="{PUR}" stroke="#fff" stroke-width="3"/></g>'
         f'<text x="300" y="40" font-family="JBM" font-weight="800" font-size="24" fill="{PUR}">NORDPOL</text></svg></div>')
stage.append(el(ruler, 0, 1020, A("b32", "b35", -0.3) + ' data-sfx="glass"', 1080, CENTER))
chip("❓ MYTHOS: ERDE KIPPT", 440, "b33@kippt", "b34", -0.1, RED)
stage.append(el('<div class="stamp mono" style="font-size:64px">NEIN</div>', 0, 470, A("b34", "b35", -0.05), 1080, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:46px">ECHTE GEFAHR: FLUTWELLE</div>', 0, 440, A("b35@Gefahr", "end", -0.1), 1080, CENTER))
stage.append(el('<div class="note mono">SCHEMATISCH · QUELLEN: BRITANNICA, NASA/JPL, CTG, UBA</div>', 20, 1250, A("b3", "end", 0.3) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">SZENARIO</div>', 900, 1250, A("b35", "end", 0.0) + ' data-sfx="none"'))

# Kamera-Keyframes Karte: (anker, offset, x, y, z) – Welt: Globus R=400 um (0,0)
DAMX, DAMY = 17.8, -6.1
mcam = [("b1", 0, 0, 0, 1.0), ("b2", -0.2, 0, 0, 1.0), ("b2@China", 0.1, 0, -10, 2.5), ("b4", 0.0, 0, -10, 2.5), ("b4", 0.9, 4, -8, 2.9),
        ("b5", -0.45, DAMX, DAMY, 9), ("b5", 0.3, DAMX, DAMY, 9),
        ("b12", -0.3, DAMX, DAMY, 40), ("b12", 0.5, 2, -2, 15), ("b13", -0.1, 2, -2, 15), ("b13", 0.5, 6, 16, 10.5), ("b14", -0.5, 6, 16, 10.5), ("b14", 0.2, DAMX, DAMY, 14),
        ("b22", -0.3, 36, -4, 8.8), ("b23", -0.1, 36, -4, 8.8), ("b23", 0.9, 0, 0, 1.0), ("b24", 0.3, 0, 0, 1.15), ("b25", -0.2, 0, 0, 1.0),
        ("b28", -0.1, 0, 0, 1.0), ("b30", 0, 0, -40, 0.92), ("b31", 0.5, 0, -60, 0.82), ("b35", -0.8, 0, -60, 0.82), ("b35", -0.1, DAMX, DAMY, 9)]
TR = [("b5", 0.0, "mv"), ("b12", -0.15, "vm"), ("b14", 0.25, "mv"), ("b22", 0.05, "vm"), ("b35", 0.0, "mv")]
PANJS.update(cam=mcam, tr=TR)

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
 // ---- Damm-Bühne ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const win=(tt,a,b,fi,fo)=>pr(tt,a,fi)*(1-pr(tt,b,fo));
  const G=PAN.geo, D=Math.PI/180, R0=400;
  const $=id=>document.getElementById(id);
  // ---------- Ebenen-Übergänge ----------
  let vv=0;
  for(const tr of PAN.tr){{ const t0=TS(tr[0],tr[1]); if(t>=t0-0.35){{ const u=ease(pr(t,t0-0.35,0.6)); vv=tr[2]==='mv'?u:1-u; }} }}
  const ml=$('mlay'), vl=$('vlay');
  ml.style.opacity=(1-vv).toFixed(3); vl.style.opacity=vv.toFixed(3);
  ml.style.display=vv>0.999?'none':'block'; vl.style.display=vv<0.001?'none':'block';
  // ---------- Karte ----------
  if(vv<0.999){{
   const ks=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4]}}));
   function cam(tt){{ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){{const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){{const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e)}};}}}} return ks[ks.length-1]; }}
   const c=cam(t); const z=c.z*(1+0.015*Math.sin(t*0.8))*(1+14*vv*vv);
   $('mcam').setAttribute('transform',`translate(540 440) scale(${{z.toFixed(4)}}) translate(${{(-c.x).toFixed(3)}} ${{(-c.y).toFixed(3)}})`);
   // Drehung
   let L0=108+70*(1-ease(pr(t,-0.2,3.4)));
   if(t>=TS('b28',-0.15)) L0=108+360*Math.pow(1-pr(t,TS('b28',-0.15),2.6),2.2);
   const P0=30*D, sP=Math.sin(P0), cP=Math.cos(P0);
   function pj(lo,la){{ const l=(lo-L0)*D, p=la*D, cp=Math.cos(p); const cs=sP*Math.sin(p)+cP*cp*Math.cos(l); let x=R0*cp*Math.sin(l), y=-R0*(cP*Math.sin(p)-sP*cp*Math.cos(l)); if(cs<0){{const n=Math.hypot(x,y)||1; x=x/n*R0; y=y/n*R0;}} return [x,y,cs]; }}
   function rp(rings,close){{ let s=''; for(const r of rings){{ const q=r.map(p=>pj(p[0],p[1])); if(q.every(p=>p[2]<0)) continue; s+='M'+q.map(p=>p[0].toFixed(2)+' '+p[1].toFixed(2)).join('L')+(close?'Z':''); }} return s; }}
   const key=L0.toFixed(3);
   if(window._k!==key){{ window._k=key;
     $('land1').setAttribute('d',rp(G.land,true)); $('land5').setAttribute('d',rp(G.land50,true)); $('cn').setAttribute('d',rp(G.cn,true));
     const gr=[]; for(let lo=-180;lo<180;lo+=30){{const r=[]; for(let la=-80;la<=80;la+=5) r.push([lo,la]); gr.push(r);}} for(let la=-60;la<=60;la+=30){{const r=[]; for(let lo=-180;lo<=180;lo+=5) r.push([lo,la]); gr.push(r);}}
     $('grat').setAttribute('d',rp(gr,false));
     $('yz').setAttribute('d',rp([G.yz],false));
     const rs=G.yz.slice(G.icq,G.idam+1).slice().reverse(); $('res').setAttribute('d',rp([rs],false)); $('resg').setAttribute('d',rp([rs],false));
     const ro=G.yz.slice(G.icq).slice().reverse(); $('route').setAttribute('d',rp([ro],false));
     window._ro=ro.map(p=>pj(p[0],p[1]));
     const dm=pj(G.dam[0],G.dam[1]); window._dm=dm;
   }}
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
   {{ // Position entlang der Route (Bogenlänge)
     if(!window._rl){{ let L=[0]; for(let i=1;i<ro.length;i++) L.push(L[i-1]+Math.hypot(ro[i][0]-ro[i-1][0],ro[i][1]-ro[i-1][1])); window._rl=L; }}
     const L=window._rl, tot=L[L.length-1], d=su*tot; let i=1; while(i<L.length-1&&L[i]<d) i++;
     const f=(d-L[i-1])/Math.max(1e-6,L[i]-L[i-1]); const x=ro[i-1][0]+(ro[i][0]-ro[i-1][0])*f, y=ro[i-1][1]+(ro[i][1]-ro[i-1][1])*f;
     const sh=$('ship'); sh.setAttribute('transform',`translate(${{x.toFixed(3)}} ${{y.toFixed(3)}}) scale(${{(1.25/zt).toFixed(5)}}) scale(-1 1) translate(0 ${{(-6+1.5*Math.sin(t*6)).toFixed(2)}})`);
     sh.setAttribute('opacity',win(t,TS('b22',-0.1),TS('b23',0.2),0.3,0.3).toFixed(3));
   }}
   // Damm-Punkt
   const dv=pr(t,TS('b2@Drei-Schluchten-Damm',-0.2),0.3);
   const dd=$('dam'); dd.setAttribute('cx',dm[0]); dd.setAttribute('cy',dm[1]); dd.setAttribute('r',(9/zt).toFixed(4)); dd.setAttribute('stroke-width',(3/zt).toFixed(4)); dd.setAttribute('opacity',dv.toFixed(3));
   const ph=(t*0.9)%1; const dp=$('dampulse'); dp.setAttribute('cx',dm[0]); dp.setAttribute('cy',dm[1]); dp.setAttribute('r',((10+34*ph)/zt).toFixed(4)); dp.setAttribute('stroke-width',(3/zt).toFixed(4)); dp.setAttribute('opacity',(dv*(1-ph)*0.9).toFixed(3));
   const gw=$('damglow'); gw.setAttribute('cx',dm[0]); gw.setAttribute('cy',dm[1]); gw.setAttribute('r',((90+20*Math.sin(t*4))/zt).toFixed(3)); gw.setAttribute('opacity',win(t,TS('b24',-0.2),TS('b25',0),0.4,0.4).toFixed(3));
   // Deutschland zum Vergleich (gleicher Maßstab, ortho um Deutschlandmitte)
   if(!window._de){{ const lo0=G.decen[0]*D, la0=G.decen[1]*D; const pd=(lo,la)=>{{const l=lo*D-lo0,p=la*D; return [R0*Math.cos(p)*Math.sin(l), -R0*(Math.cos(la0)*Math.sin(p)-Math.sin(la0)*Math.cos(p)*Math.cos(l))];}};
     $('dep').setAttribute('d',G.de.map(r=>'M'+r.map(p=>pd(p[0],p[1]).map(v=>v.toFixed(2)).join(' ')).join('L')+'Z').join(''));
     const a=pd(G.hh[0],G.hh[1]), b=pd(G.mu[0],G.mu[1]); const ln=$('dline'); ln.setAttribute('x1',a[0]); ln.setAttribute('y1',a[1]); ln.setAttribute('x2',b[0]); ln.setAttribute('y2',b[1]); window._de=1; }}
   $('deg').setAttribute('transform','translate(-8 30)'); $('deg').setAttribute('opacity',win(t,TS('b13',-0.2),TS('b14',0.3),0.4,0.3).toFixed(3));
   const dl=$('dline'); dl.setAttribute('stroke-width',(8/zt).toFixed(4)); dl.style.strokeDashoffset=(1-ease(pr(t,TS('b13@Hamburg',-0.1),1.0))).toFixed(4);
   // Achse
   let ang=0; const tw=win(t,TS('b33@kippt',-0.2),TS('b34',0.05),0.3,0.25); ang=tw*(26*Math.sin((t-TS('b33@kippt',-0.2))*5.5));
   $('axis').setAttribute('opacity',win(t,TS('b31@Erdachse',-0.4),TS('b35',-0.3),0.4,0.3).toFixed(3)); $('axis').setAttribute('transform',`rotate(${{ang.toFixed(2)}})`);
   $('axis').querySelector('line').setAttribute('stroke',tw>0.05?'#E5484D':'#7B3FE4');
   $('spin').setAttribute('opacity',win(t,TS('b28',-0.1),TS('b29',0.2),0.3,0.4).toFixed(3));
   // Labels
   const LG=$('labels'); if(!LG.childNodes.length){{ for(const l of PAN.lb){{ const e=document.createElementNS('http://www.w3.org/2000/svg','text'); e.textContent=l[0]; e.setAttribute('font-family','JBM'); e.setAttribute('font-weight','800'); e.setAttribute('fill',l[6]); e.setAttribute('text-anchor',l[9]); e.setAttribute('paint-order','stroke'); e.setAttribute('stroke','#fff'); e.setAttribute('stroke-linejoin','round'); LG.appendChild(e);}} }}
   PAN.lb.forEach((l,i)=>{{ const e=LG.childNodes[i]; const p=pj(l[1],l[2]); e.setAttribute('x',(p[0]+l[7]/zt).toFixed(3)); e.setAttribute('y',(p[1]+l[8]/zt).toFixed(3)); e.setAttribute('font-size',(l[5]/zt).toFixed(4)); e.setAttribute('stroke-width',(6/zt).toFixed(4)); e.setAttribute('opacity',win(t,TS(l[3],-0.1),TS(l[4],0),0.3,0.3).toFixed(3)); }});
  }}
  // ---------- Tal ----------
  if(vv>0.001){{
   const vs=0.4+0.6*vv; let vx=540,vy=440,vz=1;
   const fz=(a,o,d,x,y,zz,b,bo)=>{{ const w=win(t,TS(a,o),TS(b,bo),d,0.7); vx+= (x-540)*w; vy+=(y-440)*w; vz*=1+(zz-1)*w; }};
   fz('b9',-0.3,0.7,600,470,1.06,'b10',0); fz('b14',0.2,0.8,540,580,1.3,'b16',-0.2); fz('b19',-0.2,0.7,540,640,1.55,'b20@Fünftel',-0.4); fz('b21',-0.3,0.7,540,560,1.05,'b22',0); fz('b35',-0.6,0.6,540,620,1.12,'end',0.5);
   vz*=1+0.012*Math.sin(t*0.7);
   $('vcam').setAttribute('transform',`translate(540 440) scale(${{(vs*vz).toFixed(4)}}) translate(${{-vx}} ${{-vy}})`);
   // Wasserpegel
   let lv=680;
   if(t>=TS('b6@Seite',-0.3)) lv=680+20*ease(pr(t,TS('b6@Seite',-0.3),0.8));
   if(t>=TS('b11',-0.2)) lv=700-370*ease(pr(t,TS('b11@stieg',-0.3),2.2));
   if(t>=TS('b14',0.1)) lv=680;
   if(t>=TS('b17',-0.2)) lv=680-340*ease(pr(t,TS('b17',0.0),3.0));
   if(t>=TS('b18',-0.2)) lv=340+4*Math.sin(t*2);
   const lw=(y)=>{{ for(const id of ['lake','lake2']){{ const e=$(id); e.setAttribute('y',y.toFixed(1)); e.setAttribute('height',(900-y).toFixed(1)); }} $('lakesurf').setAttribute('d',`M0 ${{y.toFixed(1)}} H1080`); }};
   lw(lv);
   // Tunnel (Umleitung)
   $('tunnel').setAttribute('opacity',win(t,TS('b6',-0.1),TS('b8',0),0.4,0.4).toFixed(3)); $('divflow').style.strokeDashoffset=(-t*60).toFixed(1);
   // Damm: Bau + Sichtbarkeit
   let H=0; if(t>=TS('b7',-0.2)){{ const p=pr(t,TS('b7',-0.2),TS('b10@2006',0)-TS('b7',-0.2)); const q=Math.floor(p*16)/16, f=p*16-Math.floor(p*16); H=400*Math.min(1,q+ease(Math.min(1,f*1.6))/16); }}
   const dclip=$('dclip'); dclip.setAttribute('y',(700-H).toFixed(1)); dclip.setAttribute('height',H.toFixed(1));
   const dvis=t<TS('b11',-0.2)?1:(t<TS('b18',-0.4)?1-ease(pr(t,TS('b11',-0.2),0.7)):ease(pr(t,TS('b18',-0.4),0.8)));
   $('vdam').setAttribute('opacity',Math.min(1,dvis*1.4).toFixed(3)); $('vdam').setAttribute('transform',`translate(0 ${{(520*(1-dvis)).toFixed(1)}})`);
   const topY=700-H; const bw=win(t,TS('b7',-0.3),TS('b10@Mauer',0.2),0.3,0.4);
   const xl=(y)=>{{const L=[[0,250],[110,280],[200,400],[270,560],[300,700]]; for(let i=0;i<L.length-1;i++){{ if(y>=L[i][1]&&y<=L[i+1][1]) return L[i][0]+(L[i+1][0]-L[i][0])*(y-L[i][1])/(L[i+1][1]-L[i][1]); }} return 300;}};
   const xr=(y)=>1080-xl(y)+(y>600?-0:0);
   document.querySelectorAll('.crane').forEach((c,k)=>{{ const x=+c.dataset.x; c.setAttribute('transform',`translate(${{x}} ${{topY.toFixed(1)}})`); c.setAttribute('opacity',bw.toFixed(3)); c.querySelector('.jib').setAttribute('transform',`scale(${{Math.cos(t*0.9+k*1.7).toFixed(3)}} 1)`); }});
   document.querySelectorAll('.wk').forEach((w,k)=>{{ const a=xl(topY)+20, b=1080-xl(topY)-20; const u=((k*0.37+t*0.08*(k%2?1:-1))%1+1)%1; w.setAttribute('cx',(a+(b-a)*u).toFixed(1)); w.setAttribute('cy',(topY-5-2*Math.abs(Math.sin(t*6+k))).toFixed(1)); w.setAttribute('opacity',bw.toFixed(3)); }});
   // Turbinen
   document.querySelectorAll('.turb').forEach((e,k)=>{{ const on=pr(t,TS('b19',0.0)+k*0.045,0.08); e.setAttribute('fill',on>0.5?'#19C6B4':'#5D616B'); }});
   $('jets').setAttribute('opacity',win(t,TS('b19@Turbinen',-0.3),TS('b21',0),0.4,0.4).toFixed(3));
   document.querySelectorAll('.jet').forEach((e,k)=>e.setAttribute('transform',`translate(0 ${{(6*Math.sin(t*14+k)).toFixed(1)}})`));
   // Maße + Dom
   $('dims').setAttribute('opacity',win(t,TS('b8@zwei',-0.2),TS('b10',0),0.4,0.3).toFixed(3));
   $('hdim').setAttribute('opacity',pr(t,TS('b8@180',-0.2),0.4).toFixed(3));
   $('dom').setAttribute('opacity',win(t,TS('b9@Kölner',-0.2),TS('b10',0.1),0.4,0.3).toFixed(3));
   // Altes Dorf + Menschen + neue Städte
   $('oldtown').setAttribute('opacity',win(t,TS('b11',-0.3),TS('b18',0),0.4,0.5).toFixed(3));
   const pv=win(t,TS('b14',0.1),TS('b18',-0.2),0.5,0.4); $('people').setAttribute('opacity',pv.toFixed(3));
   document.querySelectorAll('.pp').forEach(e=>{{ const k=+e.dataset.k; const u=ease(pr(t,TS('b15@Million',0.1)+k*0.035,1.5)); const sx=+e.dataset.sx, sy=+e.dataset.sy, tx=+e.dataset.tx, ty=+e.dataset.ty;
     const x=sx+(tx-sx)*u, y=sy+(ty-sy)*u-10*Math.abs(Math.sin(u*Math.PI*5)); e.setAttribute('cx',x.toFixed(1)); e.setAttribute('cy',y.toFixed(1)); }});
   $('city').setAttribute('opacity',win(t,TS('b16@Städte',-0.4),TS('b18',0),0.2,0.5).toFixed(3));
   document.querySelectorAll('.tw').forEach(e=>{{ const k=+e.dataset.k; const u=pr(t,TS('b16@Städte',-0.2)+k*0.09,0.4); const s=1+2.7*Math.pow(u-1,3)+1.7*Math.pow(u-1,2); const yb=+e.dataset.yb; e.setAttribute('transform',`translate(0 ${{yb}}) scale(1 ${{Math.max(0,s).toFixed(3)}}) translate(0 ${{-yb}})`); }});
   // Unterlauf-Stadt, Regen, Flut
   $('town').setAttribute('opacity',pr(t,TS('b21',-0.3),0.5).toFixed(3));
   const rv=win(t,TS('b21',-0.2),TS('b21@schützt',0.8),0.4,0.5); $('rain').setAttribute('opacity',rv.toFixed(3));
   document.querySelectorAll('.rd').forEach(e=>{{ const k=+e.dataset.k; const x=(k*97)%1100-10, y=((t*900+k*173)%960)-80; e.setAttribute('transform',`translate(${{(x-0.25*y*0.3).toFixed(1)}} ${{y.toFixed(1)}})`); }});
   const fl=ease(pr(t,TS('b35@echte',-0.1),1.3)); $('flood').setAttribute('opacity',(fl>0?1:0)); $('floodr').setAttribute('height',(200*fl).toFixed(1));
   document.querySelectorAll('.foam').forEach((e,k)=>e.setAttribute('transform',`translate(${{(Math.sin(t*5+k)*8).toFixed(1)}} ${{(700+180*fl-6).toFixed(1)}})`));
   $('crack').setAttribute('opacity',pr(t,TS('b35',-0.05),0.15).toFixed(3));
   document.querySelectorAll('#town .th').forEach((e,k)=>{{ const s=pr(t,TS('b35@Gefahr',0.2)+k*0.06,0.4); e.setAttribute('opacity',(1-s).toFixed(3)); }});
  }}
  for(const e of document.querySelectorAll('.dr')){{ const t0=S[e.dataset.a]+(+e.dataset.dl||0); e.style.strokeDashoffset=(1-ease(pr(t,t0,+e.dataset.dur||1))).toFixed(4); }}
  // ---------- HTML-Overlays mit Zuständen ----------
  {{ const y=$('year'); const p=pr(t,TS('b7',0),TS('b10@2006',0)-TS('b7',0)); y.textContent=String(Math.round(1994+12*ease(p))); y.style.color=p>=1?'#7B3FE4':'#0B0B10'; }}
  {{ const f=$('defill'); const h=50*ease(pr(t,TS('b20@Fünftel',0.1),0.7)); f.setAttribute('y',(250-h).toFixed(1)); f.setAttribute('height',h.toFixed(1)); }}
  {{ const u=ease(pr(t,TS('b26@höher',-0.2),0.9)); $('sdrop').setAttribute('transform',`translate(0 ${{(-40*u).toFixed(1)}})`); $('sw').setAttribute('transform',`translate(0 ${{(-30*u).toFixed(1)}})`); $('sarrow').setAttribute('opacity',pr(t,TS('b26@Erdmittelpunkt',-0.6),0.4).toFixed(3));
    const down=pr(t,TS('b25@unten',-0.3),0.4); $('sdrop').setAttribute('opacity',(0.35+0.65*Math.max(down,u)).toFixed(3)); }}
  {{ // Eiskunstläuferin: Drehung integrieren
    const ta=TS('b27@ausstreckt',-0.2); const w0=9, w1=2.6; const ex=ease(pr(t,ta,0.6));
    let ph=0; const t0=TS('b27',-0.4); for(let s=t0;s<t;s+=1/30){{ ph+=(w0+(w1-w0)*ease(pr(s,ta,0.6)))/30; }}
    const L=40+50*ex, ay=-40+(-48)*ex; const cx=Math.cos(ph);
    const al=$('arml'), ar=$('armr'); al.setAttribute('x2',(-L*cx).toFixed(1)); al.setAttribute('y2',(ay).toFixed(1)); ar.setAttribute('x2',(L*cx).toFixed(1)); ar.setAttribute('y2',(ay).toFixed(1));
    $('sk').setAttribute('transform',`scale(${{(0.85+0.15*Math.abs(Math.cos(ph))).toFixed(3)}} 1)`);
    $('swirl').style.strokeDashoffset=(-ph*40).toFixed(1);
    const lab=$('sklab'); lab.textContent=t>TS('b27@langsamer',-0.3)?'ARME RAUS → LANGSAMER':'ARME AN → SCHNELL'; lab.style.color=t>TS('b27@langsamer',-0.3)?'#7B3FE4':'#0B0B10'; }}
  {{ const go=ease(pr(t,TS('b32@Zentimeter',-0.3),0.9)); const back=ease(pr(t,TS('b34@zurück',-0.4),0.8)); const wob=win(t,TS('b33@kippt',-0.2),TS('b34',0),0.3,0.2)*24*Math.sin(t*16);
    $('pmark').setAttribute('transform',`translate(${{(320*go*(1-back)+wob).toFixed(1)}} 0)`); }}
  // Headline nach dem Hook ausblenden (dyn_ws überschreibt die Opacity)
  {{ const H_=$('head'); H_.style.opacity=(+H_.style.opacity||0)*(1-pr(t,S['b3']-0.3,0.35)); }}
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
