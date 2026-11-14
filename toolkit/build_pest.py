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

# ---------- beats ----------
CH = ["", "", "", "", "", ""]
HOOK = 'War Corona die <span style="color:#7B3FE4">tödlichste</span> Seuche aller Zeiten?'
B = [
 ("p1", 0, HOOK, "War *Corona* die *tödlichste* *Seuche* aller *Zeiten?* *Nein.*", "staunt"),
 ("p2", 0, HOOK, "*Früher* gab es *Seuchen,* an denen ein *viel* *größerer* *Teil* der *Menschen* *starb.*", None),
 ("p3", 0, HOOK, "Wie *groß* der *Unterschied* ist, zeige ich dir am *Ende.*", None),
 ("p4", 1, "", "Zum Beispiel die *Pest:* *1347* legen *Handelsschiffe* auf *Sizilien* an.", None),
 ("p5", 1, "", "An *Bord* sind wohl *Ratten* und *Flöhe.*", None),
 ("p6", 2, "", "In den *Flöhen* steckt ein *Bakterium,* der *Erreger* der *Pest.*", None),
 ("p7", 2, "", "*Sticht* ein *Floh* einen *Menschen,* *steckt* er ihn *an.*", None),
 ("p8", 3, "", "Über *Häfen* und *Handelswege* breitet sich die *Seuche* aus.", None),
 ("p9", 3, "", "In nur *vier* *Jahren* erreicht sie fast *ganz* *Europa.*", None),
 ("p10", 4, "", "*Medikamente* gibt es damals *nicht.*", None),
 ("p11", 4, "", "*Viele* *Kranke* *sterben* in *wenigen* *Tagen.*", None),
 ("p12", 5, "", "Der *Vergleich:*", None),
 ("p13", 5, "", "Durch *Corona* starben nach *Schätzung* der *WHO* etwa *zwei* von *tausend* *Menschen* *weltweit.*", None),
 ("p14", 5, "", "Durch die *Pest* starben in *Europa* wohl rund *dreihundert* von *tausend.*", None),
 ("p15", 5, "", "Der *Anteil* war *über* *hundertmal* so *hoch.*", None),
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



# ================= Bühne: Weltkarte -> Mittelmeer (Schiff) -> Lupe (Ratte/Floh/Bakterium/Mensch) -> Europa färbt sich -> 1000er-Raster =================
import math
CENTER = "display:flex;justify-content:center"
GEO = json.load(open("geo.json")); K = GEO["K"]; CXF = GEO["CX"]
def WX(lon): return (lon + 180) * K * CXF
def WY(lat): return (90 - lat) * K
def CAM(lat, lon, z): return [round(WX(lon), 2), round(WY(lat), 2), z]
PW, PH = 1000, 800
MES = (38.19, 15.55)
# Kamera-Keyframes (Anker, Offset, x, y, z)
cam = [("p1", 0, *CAM(28, 15, 1.12)), ("p2@Früher", 0, *CAM(30, 18, 1.22)), ("p3", 0.2, *CAM(40.5, 25, 14)),
       ("p4@Handelsschiffe", 0, *CAM(40.5, 25, 14)), ("p4@Sizilien", 0.2, *CAM(39.5, 19, 17)),
       ("p5", -0.2, *CAM(39.5, 19, 17)), ("p5", 0.5, *CAM(*MES, 34)), ("p8", -0.1, *CAM(*MES, 34)),
       ("p8", 0.9, *CAM(41.5, 10.5, 11)), ("p9", -0.1, *CAM(41.5, 10.5, 11)), ("p9", 1.2, *CAM(50, 16, 6.2)),
       ("p12", 0, *CAM(50, 16, 6.2)), ("end", 0, *CAM(50, 16, 5.6))]
# Corona-Punkte (Städte weltweit), erst Wuhan
CITIES = [(30.6, 114.3), (39.9, 116.4), (31.2, 121.5), (37.6, 127.0), (35.7, 139.7), (13.8, 100.5), (1.35, 103.8), (28.6, 77.2), (19.1, 72.9),
          (35.7, 51.4), (41.0, 29.0), (45.5, 9.2), (41.9, 12.5), (40.4, -3.7), (48.9, 2.3), (51.5, -0.1), (52.5, 13.4), (59.3, 18.1), (55.8, 37.6),
          (30.0, 31.2), (6.5, 3.4), (-1.3, 36.8), (-26.2, 28.0), (40.7, -74.0), (41.9, -87.6), (34.1, -118.2), (47.6, -122.3), (43.7, -79.4),
          (19.4, -99.1), (4.7, -74.1), (-12.0, -77.0), (-23.5, -46.6), (-34.6, -58.4), (-33.4, -70.6), (-33.9, 151.2), (-37.8, 145.0),
          (25.2, 55.3), (24.7, 46.7), (14.6, 121.0), (-6.2, 106.8), (23.8, 90.4), (33.7, 73.1), (50.1, 14.4), (52.2, 21.0), (38.7, -9.1),
          (53.3, -6.3), (60.2, 24.9), (37.9, 23.7), (44.4, 26.1), (-4.3, 15.3), (9.0, 38.7), (33.6, -7.6), (-8.8, 13.2), (21.0, 105.8)]
cdots = "".join(f'<circle class="cdot" data-k="{i}" cx="{WX(lo):.1f}" cy="{WY(la):.1f}" r="0" fill="{PUR}" fill-opacity=".75" stroke="#fff"/>' for i, (la, lo) in enumerate(CITIES))
# Schiffsroute Kaffa -> Bosporus -> Ägäis -> Peloponnes -> Messina
ROUTE = [(45.0, 35.4), (43.6, 32.5), (42.0, 29.6), (41.1, 29.0), (40.5, 26.5), (39.2, 25.4), (37.4, 24.6), (36.2, 23.0), (36.6, 21.2), (37.4, 18.0), (38.0, 16.0), MES]
rpts = [[round(WX(lo), 2), round(WY(la), 2)] for la, lo in ROUTE]
route_d = "M" + "L".join(f"{x} {y}" for x, y in rpts)
# Handelswege ab Messina (SCHEMATISCH)
PORTS = dict(GENUA=(44.41, 8.93), MARSEILLE=(43.30, 5.37), VENEDIG=(45.44, 12.33), TUNIS=(36.8, 10.18))
TR = dict(GENUA=[MES, (38.9, 15.2), (40.3, 14.2), (41.6, 12.0), (42.8, 10.3), PORTS["GENUA"]],
          MARSEILLE=[MES, (38.6, 14.0), (40.0, 10.5), (42.0, 7.5), PORTS["MARSEILLE"]],
          VENEDIG=[MES, (37.9, 16.4), (39.5, 18.6), (41.0, 18.2), (43.0, 15.5), PORTS["VENEDIG"]],
          TUNIS=[MES, (37.9, 13.5), (37.3, 11.6), PORTS["TUNIS"]])
trd = "".join(f'<path class="trade" data-k="{i}" d="M' + "L".join(f"{WX(lo):.2f} {WY(la):.2f}" for la, lo in v) + f'" fill="none" stroke="{RED}" stroke-linecap="round" pathLength="1" stroke-dasharray="0.03 0.02" stroke-dashoffset="0" style="opacity:0"/>' for i, v in enumerate(TR.values()))
pdots = "".join(f'<circle class="pdot" data-k="{i}" cx="{WX(lo):.2f}" cy="{WY(la):.2f}" r="0" fill="{RED}" stroke="#fff"/>' for i, (la, lo) in enumerate(PORTS.values()))
mx, my = WX(MES[1]), WY(MES[0])
mapsvg = (f'<svg id="msvg" width="{PW}" height="{PH}" style="position:absolute;left:0;top:0;overflow:hidden">'
          f'<defs><clipPath id="spread"><circle id="spc" cx="{mx:.2f}" cy="{my:.2f}" r="0"/></clipPath></defs>'
          f'<g id="mapg"><path id="landp" d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
          f'<g clip-path="url(#spread)"><path d="{GEO["eur"]}" fill="rgba(229,72,77,.42)" stroke="#B8383C" stroke-width="1.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></g>'
          f'<path id="route" d="{route_d}" fill="none" stroke="#5D616B" stroke-linecap="round" stroke-dasharray="0.6 0.5"/>'
          f'{trd}{pdots}{cdots}</g></svg>')
def lab(lat, lon, text, i, o, col=PUR, d=0, pin=True, side="r", dy=-14):
    p = f'<span class="pin" style="background:{col}"></span>' if pin else ""
    lb = f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span>'
    pos = (f"left:{-11 if pin else -60}px" if side == "r" else "right:-11px")
    inner = p + lb if side == "r" else lb + p
    return (f'<div class="geo" data-x="{WX(lon):.2f}" data-y="{WY(lat):.2f}" style="position:absolute;left:0;top:0">'
            f'<div class="el mk" {A(i, o, d)} style="{pos};top:{dy}px;gap:8px">{inner}</div></div>')
GR = "#3F434C"; RD = "#B8383C"
ov = (lab(44.3, 33.8, "SCHWARZES MEER", "p4@Handelsschiffe", "p4@Sizilien", GR, -0.1, False)
      + lab(37.55, 14.2, "SIZILIEN · 1347", "p4@Sizilien", "p5", RD, 0, False, "l")
      + lab(*PORTS["GENUA"], "GENUA", "p8@Handelswege", "p9", RD, 0.1, True, "l", -40)
      + lab(*PORTS["MARSEILLE"], "MARSEILLE", "p8@Handelswege", "p9", RD, 0.25, True, "l", 6)
      + lab(*PORTS["VENEDIG"], "VENEDIG", "p8@Handelswege", "p9", RD, 0.4))
# Schiff (Hauptdarsteller, bildschirmfest, folgt der Route)
ship = (f'<svg width="120" height="110" viewBox="0 0 120 110" style="overflow:visible">'
        f'<path d="M58 8 V74" stroke="{INK}" stroke-width="4"/><path d="M60 12 Q96 30 92 64 L60 64 Z" fill="#fff" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
        f'<path d="M56 16 Q30 34 32 62 L56 62 Z" fill="#F1EEF9" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
        f'<path d="M8 74 H112 L98 98 H22 Z" fill="#8B6A4E" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
        f'<path d="M58 4 l14 4 -14 4" fill="{RED}"/></svg>')
shipel = f'<div id="ship" style="position:absolute;left:0;top:0;opacity:0;width:0;height:0"><div style="position:absolute;left:-60px;top:-100px">{ship}</div></div>'
# Großer Jahreszähler
yearel = f'<div id="yrbox" style="position:absolute;left:28px;top:18px;opacity:0"><div class="num" id="yr" style="font-size:120px;color:{INK}">2020</div></div>'

# ---------- Lupe (Maßstabswechsel) ----------
LR = 300  # Radius
def rat(x, y, s=1.0, flip=False):
    tr = f'translate({x} {y}) scale({-s if flip else s} {s})'
    return (f'<g transform="{tr}"><path d="M-70 10 Q-110 0 -120 -30" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'<ellipse cx="-20" cy="0" rx="58" ry="32" fill="#8A8F99" stroke="{INK}" stroke-width="4"/>'
            f'<ellipse cx="38" cy="-6" rx="30" ry="22" fill="#8A8F99" stroke="{INK}" stroke-width="4"/><circle cx="26" cy="-28" r="12" fill="#C9CCD3" stroke="{INK}" stroke-width="3.5"/>'
            f'<circle cx="48" cy="-10" r="4.5" fill="{INK}"/><circle cx="68" cy="-2" r="5" fill="#E58F9A"/>'
            f'<path d="M-50 28 v12 M-6 30 v12 M24 14 v18" stroke="{INK}" stroke-width="4" stroke-linecap="round"/></g>')
def flea(x, y, s=1.0, cls="", extra=""):
    return (f'<g class="{cls}" transform="translate({x} {y}) scale({s})" {extra}>'
            f'<path d="M-6 18 L-30 46 L-48 40 M8 20 L-4 50 L-20 52 M22 16 L40 46 L62 40" fill="none" stroke="#4A2E1F" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<ellipse cx="0" cy="0" rx="40" ry="26" fill="#7A4A2E" stroke="#3A2215" stroke-width="4"/>'
            f'<circle cx="40" cy="-4" r="15" fill="#7A4A2E" stroke="#3A2215" stroke-width="4"/><path d="M52 2 L66 14" stroke="#3A2215" stroke-width="4" stroke-linecap="round"/></g>')
# A: Schiffsdeck mit Ratten + Flöhen
deckA = (f'<g id="lzA">'
         f'<path d="M-280 120 H280" stroke="{INK}" stroke-width="5"/><path d="M-280 150 H280 M-280 185 H280" stroke="#C9CCD3" stroke-width="3"/>'
         f'<rect x="-210" y="0" width="120" height="120" rx="6" fill="#E8DCC9" stroke="{INK}" stroke-width="4"/><path d="M-210 60 H-90 M-150 0 V120" stroke="{INK}" stroke-width="2.5"/>'
         f'<rect x="120" y="30" width="110" height="90" rx="6" fill="#E8DCC9" stroke="{INK}" stroke-width="4"/><path d="M120 75 H230" stroke="{INK}" stroke-width="2.5"/>'
         f'<rect x="-60" y="-150" width="90" height="270" fill="none" stroke="#C9CCD3" stroke-width="3" stroke-dasharray="8 8"/>'
         f'<g class="ratA" style="opacity:0">{rat(-20, 80, 1.35)}</g><g class="ratB" style="opacity:0">{rat(185, 2, 0.95, True)}</g>'
         + "".join(f'<g class="fleaA" data-k="{i}" style="opacity:0">{flea(0, 0, 0.45)}</g>' for i in range(6))
         + '</g>')
# B: großer Floh mit Bakterien
bac = "".join(f'<rect class="bac" data-k="{i}" x="-14" y="-6" width="28" height="12" rx="6" fill="{PUR}" stroke="#fff" stroke-width="2" style="opacity:0" transform="translate({x} {y}) rotate({r})"/>'
              for i, (x, y, r) in enumerate([(-50, -10, 20), (-20, 18, -30), (10, -20, 60), (30, 12, 10), (-70, 22, -50), (55, -6, 80), (-30, -34, 40), (5, 30, -10)]))
fleaB = (f'<g id="lzB" style="opacity:0"><g id="bigflea">'
         f'<path d="M-40 70 L-110 170 L-170 150 M20 80 L-10 190 L-70 200 M80 60 L150 170 L230 150" fill="none" stroke="#4A2E1F" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<ellipse cx="0" cy="0" rx="150" ry="98" fill="#9A6440" stroke="#3A2215" stroke-width="7"/>'
         f'<ellipse cx="-10" cy="4" rx="110" ry="64" fill="rgba(255,255,255,.55)" stroke="#3A2215" stroke-width="2" stroke-dasharray="7 7"/>'
         f'<circle cx="150" cy="-20" r="54" fill="#9A6440" stroke="#3A2215" stroke-width="7"/><circle cx="168" cy="-34" r="8" fill="{INK}"/>'
         f'<path d="M196 0 L240 46" stroke="#3A2215" stroke-width="8" stroke-linecap="round"/>{bac}</g></g>')
# C: Floh springt auf Menschen
person = (f'<g id="pers" transform="translate(110 -10)"><circle cx="0" cy="-120" r="62" fill="#fff" stroke="{INK}" stroke-width="6"/>'
          f'<path id="pbody" d="M-110 200 Q-110 -30 0 -40 Q110 -30 110 200 Z" fill="#fff" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
          f'<path d="M-80 40 Q-150 90 -170 160" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
          f'<circle id="bite" cx="-140" cy="110" r="0" fill="none" stroke="{RED}" stroke-width="6"/></g>')
sceneC = f'<g id="lzC" style="opacity:0">{person}<g id="hopflea">{flea(0, 0, 0.6)}</g></g>'
lupe = (f'<div id="lupe" style="position:absolute;left:{PW // 2}px;top:390px;width:0;height:0;opacity:0">'
        f'<svg width="{2 * LR + 160}" height="{2 * LR + 160}" viewBox="{-LR - 80} {-LR - 80} {2 * LR + 160} {2 * LR + 160}" style="position:absolute;left:{-LR - 80}px;top:{-LR - 80}px;overflow:visible">'
        f'<defs><clipPath id="lclip"><circle r="{LR}"/></clipPath><pattern id="lmm" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M0 0.5H25M0.5 0V25" stroke="rgba(11,11,16,.08)" stroke-width="1"/></pattern></defs>'
        f'<path d="M{LR * 0.72:.0f} {LR * 0.72:.0f} L{LR * 1.12:.0f} {LR * 1.12:.0f}" stroke="{INK}" stroke-width="34" stroke-linecap="round"/>'
        f'<circle r="{LR}" fill="#FCFCFD"/><circle r="{LR}" fill="url(#lmm)"/>'
        f'<g clip-path="url(#lclip)">{deckA}{fleaB}{sceneC}</g>'
        f'<circle r="{LR}" fill="none" stroke="{INK}" stroke-width="14"/><circle r="{LR - 9}" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="4"/>'
        f'</svg></div>')
def lmk(text, x, y, i, o, col=PUR, d=0):
    return f'<div class="el mk" {A(i, o, d)} style="left:{x}px;top:{y}px;gap:8px"><span class="mono lab" style="color:{col};border-color:{col};font-size:26px">{text}</span></div>'
lupelabs = (lmk("RATTEN", 420, 712, "p5@Ratten", "p5@Flöhe", INK, 0) + lmk("FLÖHE", 430, 712, "p5@Flöhe", "p6", "#7A4A2E", 0)
            + lmk("BAKTERIUM · YERSINIA PESTIS", 300, 712, "p6@Bakterium", "p7", PUR, 0) + lmk("ANSTECKUNG", 400, 712, "p7@steckt", "p8", RED, 0))

# ---------- Karten-Overlays (je Szene max. 1) ----------
ovl = []
ovl.append(el(f'<div class="chip mono row" style="font-size:30px;gap:14px;padding:12px 22px;background:rgba(255,255,255,.95);border-color:{PUR};color:{PUR}">CORONA · 2020–2022</div>', 470, 690, A("p1", "p1@Nein", -0.6) + ' data-sfx="none"'))
ovl.append(el('<div class="stamp mono" style="font-size:64px">NEIN.</div>', 540, 650, A("p1@Nein", "p2@Früher", -0.05)))
ovl.append(el(f'<div class="chip mono row" style="font-size:28px;gap:14px;padding:12px 22px;background:rgba(255,255,255,.95)">⚖️ AM ENDE: CORONA vs. PEST</div>', 0, 690, A("p3@Unterschied", "p4", -0.1) + ' data-sfx="marker"', PW, CENTER))
ovl.append(el(f'<div class="chip mono" style="font-size:22px;padding:6px 12px;color:#8A8F99;border-color:#C9CCD3;background:rgba(255,255,255,.9)">AUSBREITUNG SCHEMATISCH</div>', 18, 752, A("p8", "p12", 0) + ' data-sfx="none"'))
# Medikamente: keine
bottle = (f'<svg width="150" height="190" viewBox="0 0 150 190"><rect x="45" y="6" width="60" height="28" rx="6" fill="#fff" stroke="{INK}" stroke-width="5"/>'
          f'<rect x="20" y="34" width="110" height="148" rx="18" fill="#fff" stroke="{INK}" stroke-width="5"/><rect x="20" y="80" width="110" height="56" fill="#F1EEF9" stroke="{INK}" stroke-width="4"/>'
          f'<path d="M75 92 v32 M59 108 h32" stroke="{PUR}" stroke-width="7" stroke-linecap="round"/></svg>')
ovl.append(el(f'<div class="card active" style="position:relative;width:560px;height:300px;padding:26px"><div class="row" style="gap:40px;height:100%;justify-content:center">'
              f'<div style="position:relative">{bottle}<div class="xx" style="left:-6px;top:-30px;font-size:230px;line-height:1">✕</div></div>'
              f'<div class="col" style="align-items:flex-start;gap:10px"><div class="mono" style="font-size:34px;font-weight:800">KEINE</div><div class="mono" style="font-size:34px;font-weight:800">MEDIKAMENTE</div>'
              f'<div class="mono" style="font-size:20px;color:#8A8F99">ANTIBIOTIKA ERST AB 1940ER</div></div></div></div>', 220, 430, A("p10@Medikamente", "p11", -0.1) + ' data-sfx="glass"'))
days = "".join(f'<div class="dbox mono" data-k="{k}">TAG<br><b>{k + 1}</b></div>' for k in range(5))
ppl = "".join(f'<div class="ppl" data-k="{k}">{ic(I["person"], 56, INK, 3.6)}</div>' for k in range(10))
ovl.append(el(f'<div class="card active" style="position:relative;width:640px;height:330px;padding:26px"><div class="col" style="gap:22px">'
              f'<div class="row" style="gap:14px">{days}</div><div class="row" style="gap:6px">{ppl}</div>'
              f'<div class="mono" style="font-size:20px;color:#8A8F99">OHNE BEHANDLUNG · SCHEMATISCH</div></div></div>', 180, 410, A("p11@Viele", "p12", -0.1) + ' data-sfx="glass"'))
# ---------- Auflösung: 2 × 1000er-Raster ----------
GC, GRW, CS = 40, 25, 11
def grid(gid, x):
    dots = "".join(f'<circle cx="{(k % GC) * CS + 5.5}" cy="{(k // GC) * CS + 5.5}" r="4.2" fill="#D9DBE1"/>' for k in range(GC * GRW))
    return f'<svg id="{gid}" width="{GC * CS}" height="{GRW * CS}" style="position:absolute;left:{x}px;top:0;overflow:visible">{dots}</svg>'
def side(gid, x, title, col, val, anchor, note, tin):
    return (el(f'<div class="col" style="width:440px"><div class="chip mono" style="font-size:30px;padding:8px 20px;font-weight:800;border-color:{col};color:{col};background:#fff">{title}</div></div>', x, 30, A(tin, "end", 0) + ' data-sfx="glass"')
            + el(f'<div class="col" style="width:440px;gap:6px"><div class="num" style="font-size:170px;color:{col}">{cnt(val, anchor, 0, 0)}</div>'
               f'<div class="mono" style="font-size:26px;font-weight:700;color:#5D616B">VON 1.000</div></div>', x, 110, A(anchor, "end", -0.1) + ' data-sfx="none"')
            + el(f'<div style="position:relative;width:440px;height:275px">{grid(gid, 0)}</div>', x, 370, A(tin, "end", 0.1) + ' data-sfx="none"')
            + el(f'<div class="note mono" style="font-size:18px;white-space:normal;text-align:center;width:440px">{note}</div>', x, 652, A(tin, "end", 0.2) + ' data-sfx="none"'))
cmp_ = (side("gC", 40, "CORONA", PUR, 2, "p13@zwei", "WELTWEIT · 2020–21 · WHO-SCHÄTZUNG (ÜBERSTERBLICHKEIT)", "p12")
        + side("gP", 520, "PEST", RED, 300, "p14@dreihundert", "EUROPA · 1347–1351 · SCHÄTZUNG (30–50 %+)", "p12@Vergleich"))
ring = f'<div id="cring" class="el" {A("p13@zwei", "p14", 0)} data-sfx="none" style="left:0;top:0"><div style="position:absolute;left:{40 + 19 * CS + 11 - 34}px;top:{370 + 12 * CS + 5 - 34}px;width:68px;height:68px;border-radius:50%;border:4px solid {PUR}"></div></div>'
big = el(f'<div class="stamp mono" style="font-size:44px;color:{RED};border-color:{RED}">ÜBER 100 × SO HOCH</div>', 0, 470, A("p15@hundertmal", "end", -0.15), PW, CENTER)
chips = (el('<div class="chip mono" style="font-size:19px;padding:8px 12px;white-space:nowrap">KARTE: NATURAL EARTH</div>', 720, 18, A("p1", "p12", -0.6) + ' data-sfx="none"'))
stage.append(mm(mapsvg + ov + shipel + yearel + "".join(ovl) + lupe + lupelabs + cmp_ + ring + big + chips, 40, 440, PW, PH, A("p1", "end", -0.6) + ' data-sfx="none"'))
PANJS = dict(cam=cam, route=rpts, trade=[[[round(WX(lo),2),round(WY(la),2)] for la,lo in v] for v in TR.values()], ncity=len(CITIES), mes=[mx, my])

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
.geo{{width:0;height:0}}
.dbox{{width:96px;height:96px;border-radius:14px;border:3px solid #0B0B10;text-align:center;font-size:18px;font-weight:700;line-height:1.25;padding-top:12px}} .dbox b{{font-family:Unbounded;font-size:34px}}
.ppl{{width:56px}}
#lupe{{z-index:1}}
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
 const top=cl(1-pr(t,END,.3),0,1); const hf=1-pr(t,S['p3']-0.2,0.35); document.getElementById('headbg').style.opacity=hf; document.getElementById('head').style.opacity=top*hf;
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
 // ---- Bühne: Karte, Schiff, Lupe, Ausbreitung, Raster ----
 {{
  {{ const H_=document.getElementById('head'); H_.style.opacity=(+H_.style.opacity||0)*(1-pr(t,S['p3']-0.2,0.35)); }}
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const M=document.getElementById('mapg');
  const keys=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4]}}));
  function base(tt){{ if(tt<=keys[0].t) return keys[0]; for(let i=0;i<keys.length-1;i++){{ const k0=keys[i],k1=keys[i+1]; if(tt>=k0.t&&tt<k1.t){{ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e)}}; }} }} return keys[keys.length-1]; }}
  const bs=base(t), z=bs.z, cx=bs.x, cy=bs.y, FX=500, FY=400;
  M.setAttribute('transform',`translate(${{FX}},${{FY}}) scale(${{z}}) translate(${{-cx}},${{-cy}})`);
  const pj=(x,y)=>[FX+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('.geo')){{ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }}
  // Corona-Punkte (ab Frame 0 sichtbar, verschwinden beim Zurückspulen)
  const cout=1-pr(t,S['p2@Früher'],1.4);
  document.querySelectorAll('.cdot').forEach(c=>{{ const k=+c.dataset.k; const t0=-1.4+k*0.05; const q=pr(t,t0,0.25); const pl=1+0.18*Math.sin(t*5+k);
    c.setAttribute('r',(q*7.5*pl/z).toFixed(3)); c.setAttribute('stroke-width',(1.5/z).toFixed(3)); c.style.opacity=cout; }});
  // Jahreszahl
  {{ const Y=document.getElementById('yr'), YB=document.getElementById('yrbox'); let v=2020; const tr=S['p2@Früher'];
    if(t>=tr) v=Math.round(2020-(2020-1347)*ease(pr(t,tr,2.4)));
    if(t>=S['p9@vier']-0.2) v=1347+Math.floor(4*pr(t,S['p9@vier']-0.2,2.3)+0.0001);
    Y.textContent=v; Y.style.color=v<1400?'#B8383C':'#0B0B10';
    YB.style.opacity=pr(t,tr-0.3,0.3)*(1-pr(t,S['p12']-0.2,0.3)); }}
  // Schiff entlang der Route
  const R_=PAN.route; const segs=[]; let LT=0; for(let i=1;i<R_.length;i++){{ const l=Math.hypot(R_[i][0]-R_[i-1][0],R_[i][1]-R_[i-1][1]); segs.push(l); LT+=l; }}
  function along(u){{ let d=u*LT; for(let i=0;i<segs.length;i++){{ if(d<=segs[i]||i===segs.length-1){{ const f=Math.min(1,d/segs[i]); return [R_[i][0]+(R_[i+1][0]-R_[i][0])*f, R_[i][1]+(R_[i+1][1]-R_[i][1])*f, i, f]; }} d-=segs[i]; }} }}
  const s0=S['p4@Pest']-0.2, s1=S['p4@Sizilien']+0.15; const us=ease(pr(t,s0,s1-s0)*0.999)*0.999+0.0005;
  const sp=along(us); const SH=document.getElementById('ship'); const sq=pj(sp[0],sp[1]);
  SH.style.left=sq[0]+'px'; SH.style.top=sq[1]+'px';
  SH.style.opacity=pr(t,S['p4']-0.4,0.3)*(1-pr(t,S['p5']+0.15,0.3));
  SH.style.transform=`rotate(${{(4*Math.sin(t*3.2)).toFixed(2)}}deg) scale(${{(0.9+0.1*Math.sin(t*1.7)).toFixed(3)}})`;
  {{ let d='M'+R_[0][0]+' '+R_[0][1]; for(let i=1;i<=sp[2];i++) d+='L'+R_[i][0]+' '+R_[i][1]; d+='L'+sp[0].toFixed(2)+' '+sp[1].toFixed(2);
    const rt=document.getElementById('route'); rt.setAttribute('d',d); rt.setAttribute('stroke-width',(3.5/z).toFixed(3)); rt.setAttribute('stroke-dasharray',`${{(10/z).toFixed(3)}} ${{(8/z).toFixed(3)}}`);
    rt.style.opacity=pr(t,s0,0.2)*(1-pr(t,S['p8'],0.4)); }}
  // Handelswege + Häfen
  document.querySelectorAll('.trade').forEach(p=>{{ const k=+p.dataset.k; const pts=PAN.trade[k]; const q=ease(pr(t,S['p8@Häfen']-0.1+k*0.18,1.1));
    let L=0; const ls=[]; for(let i=1;i<pts.length;i++){{ const l=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]); ls.push(l); L+=l; }}
    let rem=q*L; let d='M'+pts[0][0]+' '+pts[0][1]; for(let i=1;i<pts.length;i++){{ if(rem>=ls[i-1]){{ d+='L'+pts[i][0]+' '+pts[i][1]; rem-=ls[i-1]; }} else {{ const f=rem/ls[i-1]; d+='L'+(pts[i-1][0]+(pts[i][0]-pts[i-1][0])*f).toFixed(2)+' '+(pts[i-1][1]+(pts[i][1]-pts[i-1][1])*f).toFixed(2); break; }} }}
    p.setAttribute('d',d); p.setAttribute('stroke-width',(4/z).toFixed(3)); p.setAttribute('stroke-dasharray',`${{(12/z).toFixed(3)}} ${{(8/z).toFixed(3)}}`);
    p.style.opacity=(q>0?1:0)*(1-pr(t,S['p9@ganz'],0.6)); }});
  document.querySelectorAll('.pdot').forEach(c=>{{ const k=+c.dataset.k; const q=pr(t,S['p8@Häfen']+0.9+k*0.18,0.25); const pl=1+0.25*Math.sin(t*6+k);
    c.setAttribute('r',(q*9*pl/z).toFixed(3)); c.setAttribute('stroke-width',(2/z).toFixed(3)); c.style.opacity=1-pr(t,S['p12'],0.4); }});
  // Ausbreitung über Europa (Kreis um Messina, SCHEMATISCH)
  document.getElementById('spc').setAttribute('r',(4*pr(t,S['p8'],0.6)+118*ease(pr(t,S['p9@vier']-0.2,2.4))).toFixed(2));
  // Lupe
  {{ const L=document.getElementById('lupe'); const mp=pj(PAN.mes[0],PAN.mes[1]);
    const oi=ease(pr(t,S['p5']-0.05,0.45)), oo=ease(pr(t,S['p8']-0.15,0.4)); const op=oi*(1-oo);
    const sc=0.12+0.88*op; const lx=mp[0]+(500-mp[0])*op, ly=mp[1]+(390-mp[1])*op;
    L.style.left=lx+'px'; L.style.top=ly+'px'; L.style.transform=`scale(${{sc.toFixed(3)}})`; L.style.opacity=Math.min(1,op*3);
    const fA=1-pr(t,S['p6']-0.15,0.25), fB=pr(t,S['p6']-0.15,0.25)*(1-pr(t,S['p7']-0.15,0.25)), fC=pr(t,S['p7']-0.15,0.25);
    document.getElementById('lzA').style.opacity=fA; document.getElementById('lzB').style.opacity=fB; document.getElementById('lzC').style.opacity=fC;
    const ra=pr(t,S['p5@Ratten']-0.15,0.25); document.querySelectorAll('.ratA,.ratB').forEach((r,i)=>{{ r.style.opacity=ra; r.setAttribute('transform',`translate(${{(i?-1:1)*(30*(1-ease(ra))+4*Math.sin(t*6+i))}} 0)`); }});
    const FP=[[-70,40],[-10,50],[40,30],[150,-20],[200,-36],[230,-10]];
    document.querySelectorAll('.fleaA').forEach(f=>{{ const k=+f.dataset.k; const q=pr(t,S['p5@Flöhe']-0.1+k*0.06,0.15); const ph=((t*1.6+k*0.37)%1); const hop=Math.sin(Math.PI*Math.min(1,ph*2.2))*(ph<0.45?38:0);
      f.style.opacity=q; f.setAttribute('transform',`translate(${{FP[k][0]+(ph<0.45?ph*40-9:9)}} ${{FP[k][1]-hop}})`); }});
    const bf=document.getElementById('bigflea'); bf.setAttribute('transform',`translate(-40 10) scale(${{(1+0.02*Math.sin(t*4)).toFixed(3)}})`);
    document.querySelectorAll('.bac').forEach(b_=>{{ const k=+b_.dataset.k; const q=pr(t,S['p6@Bakterium']-0.1+k*0.07,0.2); b_.style.opacity=q;
      const tr0=b_.getAttribute('transform').replace(/ scale\([^)]*\)/,''); b_.setAttribute('transform',tr0+` scale(${{(0.4+0.6*ease(q)+0.08*Math.sin(t*7+k)).toFixed(3)}})`); }});
    // Floh springt auf den Arm
    {{ const j0=S['p7@Sticht']-0.1, jq=ease(pr(t,j0,0.6)); const x0=-230,y0=150,x1=-55,y1=95; const hx=x0+(x1-x0)*jq, hy=y0+(y1-y0)*jq-Math.sin(Math.PI*jq)*170;
      document.getElementById('hopflea').setAttribute('transform',`translate(${{hx.toFixed(1)}} ${{hy.toFixed(1)}}) rotate(${{(-25*Math.sin(Math.PI*jq)).toFixed(1)}})`);
      const bq=pr(t,S['p7@steckt']-0.1,0.5); const bt=document.getElementById('bite'); bt.setAttribute('r',(10+40*ease(bq)+(bq>=1?4*Math.sin(t*8):0)).toFixed(1)); bt.style.opacity=bq>0?1:0;
      document.getElementById('pbody').setAttribute('fill',`rgba(229,72,77,${{(0.3*pr(t,S['p7@steckt'],0.6)).toFixed(3)}})`); }}
  }}
  // Tage + Menschen
  document.querySelectorAll('.dbox').forEach(d=>{{ const k=+d.dataset.k; const on=t>=S['p11@Kranke']+k*0.22; d.style.background=on?'#7B3FE4':'#fff'; d.style.color=on?'#fff':'#0B0B10'; }});
  const GREY=[1,2,4,5,7,8]; document.querySelectorAll('.ppl').forEach(p=>{{ const k=+p.dataset.k; const j=GREY.indexOf(k); p.style.opacity=j<0?1:1-0.75*pr(t,S['p11@sterben']+j*0.12,0.3); }});
  // Karte abblenden für den Vergleich
  document.getElementById('msvg').style.opacity=1-0.9*pr(t,S['p12']-0.1,0.5);
  // Raster
  {{ const cC=document.getElementById('gC').children; const on=t>=S['p13@zwei']; for(const k of [12*40+19,12*40+20]) cC[k].setAttribute('fill',on?'#7B3FE4':'#D9DBE1');
    const cP=document.getElementById('gP').children; const n=Math.round(300*ease(pr(t,S['p14@dreihundert'],0.8))); for(let k=0;k<1000;k++) cP[k].setAttribute('fill',k<n?'#E5484D':'#D9DBE1');
    const rg=document.getElementById('cring').firstElementChild; rg.style.transform=`scale(${{(1+0.15*Math.sin(t*6)).toFixed(3)}})`; }}
 }}
 // robot
 let pose=b.pose; if(end) pose='winkt';
 const R=document.getElementById('robot');
 let rop=0; if(pose&&!end){{const prevHad=BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose; rop=prevHad?1:ease(pr(t,b.s-(BEATS.indexOf(b)===0?0.3:0),.3)); const nb=BEATS[BEATS.indexOf(b)+1]; if(nb&&!nb.pose) rop*=1-pr(t,nb.s-0.2,.2); if(!nb) rop*=1-pr(t,END-0.2,.2);}}
 if(end){{rop=ease(pr(t,END+0.3,.35));}}
 R.style.opacity=rop; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');
 let prevPose=null; const bi=BEATS.indexOf(b); if(bi>0) prevPose=BEATS[bi-1].pose; const pf=pr(t,b.s-(bi===0?0.2:0),.15);
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
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))
