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
CH = ["", "", "", "", ""]
HOOK = 'Warum hat <span style="color:#19C6B4">Frankreich</span> Glasfaser – und wir nicht?'
B = [
 ("p1", 0, HOOK, "In *Frankreich* kann fast *jede* *Wohnung* *Glasfaser* bekommen – also *superschnelles* *Internet* bis ins *Haus.*", "staunt"),
 ("p2", 0, HOOK, "Bei *uns* läuft das Internet *meist* noch über die *alte* *Telefonleitung* aus *Kupfer.*", "staunt"),
 ("p3", 0, HOOK, "Wie *groß* Frankreichs *Vorsprung* ist, zeige ich dir am *Ende.*", None),
 ("p4", 1, "", "Wie *schafft* Frankreich das? *Erstens:* Dort wird *kaum* *gegraben.*", None),
 ("p5", 1, "", "Denn *Graben* ist beim *Ausbau* das *Teuerste.*", None),
 ("p6", 1, "", "Das neue *Kabel* wird durch *alte* *Telefonrohre* unter der *Straße* *gezogen*", None),
 ("p7", 1, "", "– oder an *Masten* *aufgehängt.*", None),
 ("p8", 2, "", "Bei *uns* hängen Kabel nur *selten* an *Masten,* und in *alten* *Rohren* ist oft *kein* *Platz* mehr.", None),
 ("p9", 2, "", "Also wird *meist* *neu* *gegraben.*", None),
 ("p10", 3, "", "*Zweitens:* Frankreich *schaltet* die alte *Kupferleitung* bis *zweitausenddreißig* *ab.*", None),
 ("p11", 3, "", "Wer dann zu *Hause* Internet will, braucht *Glasfaser.*", None),
 ("p12", 2, "", "Bei *uns* wurde die *Kupferleitung* stattdessen *schneller* gemacht – mit *neuer* *Technik* in den *grauen* *Kästen* am *Straßenrand.*", None),
 ("p13", 3, "", "*Glasfaser* schafft zwar ein *Vielfaches.*", None),
 ("p14", 2, "", "Aber *vielen* *reicht* das *Kupfer* – sie bestellen *keinen* *Glasfaseranschluss,* selbst wenn er *möglich* ist.", None),
 ("p15", 2, "", "Und *ohne* *Kunden* lohnt sich der *Ausbau* für die *Anbieter* *weniger.*", None),
 ("p16", 4, "", "Das *Ergebnis:*", None),
 ("p17", 4, "", "In *Frankreich* liegt Glasfaser für *fünfundneunzig* *Prozent* aller *Wohnungen* und *Büros* bereit.", None),
 ("p18", 4, "", "Bei *uns* erst für *zweiundsechzig* *Prozent.*", None),
 ("p19", 4, "", "*Immerhin:* Vor *einem* *Jahr* waren es bei uns erst *dreiundfünfzig* *Prozent.*", None),
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

# ================= Bühne: Karte FR/DE auf Millimeterpapier, kippt in Straßenszenen =================
GEO = json.load(open("geo.json")); L0, B0, KX, KY = GEO["L0"], GEO["B0"], GEO["KX"], GEO["KY"]
def WX(lon): return (lon - L0) * KX
def WY(lat): return (B0 - lat) * KY
TQ = "#19C6B4"; PUR = "#7B3FE4"; RED = "#E5484D"; CU = "#B8692E"; TQD = "#0E8C80"; PURS = "#5B2BB5"; GR = "#3F434C"
PW, PH = 4600, 8400          # Plane-Größe
FX0, FY0 = 540, 860          # Bildschirmpunkt des Kamera-Fokus
# Straßenszenen (Weltkoordinaten)
FRX, FRY = round(WX(0.7), 1), round(WY(47.4), 1)
DEX, DEY = round(WX(9.3), 1), round(WY(50.6), 1)
MAPC = (540, 556)
cam = [
 ("p1", -0.2, MAPC[0], MAPC[1], 1.0, 0), ("p4@Erstens", -0.5, MAPC[0] - 4, MAPC[1] + 6, 1.08, 0),
 ("p4@kaum", 0.0, FRX - 2.6, FRY - 0.9, 180, 60), ("p8", 0.1, FRX + 2.6, FRY - 0.9, 180, 60),
 ("p8@Kabel", 0.0, (FRX + DEX) / 2, (FRY + DEY) / 2, 2.3, 26), ("p8@selten", 0.3, DEX - 3.0, DEY - 0.9, 180, 60),
 ("p9", 0.0, DEX - 2.6, DEY - 0.9, 180, 60), ("p10", -0.3, DEX + 1.6, DEY - 0.9, 180, 60), ("p10@Frankreich", 0.1, MAPC[0], MAPC[1], 1.0, 0),
 ("p12", -0.1, MAPC[0], MAPC[1], 1.0, 0), ("p12@Kupferleitung", 0.0, WX(10.4), WY(51.2) + 40, 1.55, 0),
 ("p16", -0.2, WX(10.4), WY(51.2) + 40, 1.55, 0), ("p16@Ergebnis", 0.2, MAPC[0], MAPC[1] - 10, 1.0, 0), ("end", 0, MAPC[0], MAPC[1] - 10, 1.0, 0),
]
# --- Karte ---
def path(d, fill, stroke, cls="ol", extra=""): return f'<path class="{cls}" d="{d}" fill="{fill}" stroke="{stroke}" stroke-linejoin="round" {extra}/>'
other = "".join(path(d, "#FFFFFF", "#9AA0AA") for d in GEO["other"])
cfr = "".join(f'<circle class="cfr" data-f="{c["f"]}" data-r="{c["r"]}" cx="{c["x"]}" cy="{c["y"]}" r="0"/>' for c in GEO["circ_fr"])
cde = "".join(f'<circle class="cde" data-f="{c["f"]}" data-r="{c["r"]}" cx="{c["x"]}" cy="{c["y"]}" r="0"/>' for c in GEO["circ_de"])
cu_de = "".join(f'<path class="cu cude" d="{d}" pathLength="1" stroke-dasharray="1" fill="none" stroke="{CU}" stroke-linecap="round"/>' for d in GEO["cu_de"])
cu_fr = "".join(f'<path class="cu cufr" d="{d}" pathLength="1" stroke-dasharray="1" fill="none" stroke="{CU}" stroke-linecap="round"/>' for d in GEO["cu_fr"])
route_d = "M" + "L".join(f"{x} {y}" for x, y in GEO["route"])
# --- Straßenszene (Welt-Einheiten: 1 = ca. Hausbreite) ---
def street(cx, cy, kind):
    road = f'<rect x="{cx-11}" y="{cy-0.55}" width="22" height="1.1" fill="#E4E6EB" stroke="#2B2D35" stroke-width="0.03"/>'
    mid = f'<path d="M{cx-11} {cy} H{cx+11}" stroke="#FFFFFF" stroke-width="0.07" stroke-dasharray="0.5 0.4"/>'
    walk = f'<path d="M{cx-11} {cy-0.72} H{cx+11} M{cx-11} {cy+0.72} H{cx+11}" stroke="#9AA0AA" stroke-width="0.03"/>'
    s = road + mid + walk
    if kind == "fr":
        s += f'<path id="duct" d="M{cx-11} {cy+0.28} H{cx+11}" stroke="#7A7F8C" stroke-width="0.09" stroke-dasharray="0.22 0.12" fill="none"/>'
        s += "".join(f'<rect x="{cx+x-0.16}" y="{cy+0.12}" width="0.32" height="0.32" rx="0.04" fill="#C9CCD3" stroke="#2B2D35" stroke-width="0.025"/>' for x in (-6, -2, 2, 6))
        s += f'<path id="dcab" d="M{cx-11} {cy+0.28} H{cx+11}" stroke="{TQ}" stroke-width="0.12" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
    else:
        s += "".join(f'<path d="M{cx-11} {cy+0.24+o}" H{cx+11}" stroke="#7A7F8C" stroke-width="0.05" fill="none"/>'.replace('" H',' H') for o in (-0.06, 0, 0.06))
        s += f'<path id="ductde" d="M{cx-11} {cy+0.24} H{cx+11}" stroke="#E5484D" stroke-width="0.24" stroke-opacity="0" fill="none"/>'
        s += f'<path id="trench" d="M{cx-11} {cy+0.32} H{cx+11}" stroke="#8B5A2B" stroke-width="0.26" stroke-linecap="round" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
        s += f'<path id="trench2" d="M{cx-11} {cy+0.32} H{cx+11}" stroke="#5E3A18" stroke-width="0.1" stroke-linecap="round" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
    return f'<g id="st_{kind}" style="opacity:0">{s}</g>'
mapsvg = (f'<svg id="map" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" style="position:absolute;left:0;top:0;overflow:visible">'
          f'<defs><clipPath id="clfr">{cfr}</clipPath><clipPath id="clde">{cde}</clipPath>'
          f'<clipPath id="landfr"><path d="{GEO["fr"]}"/></clipPath><clipPath id="landde"><path d="{GEO["de"]}"/></clipPath></defs>'
          f'<g id="camg"><g id="mapl">{other}'
          + path(GEO["fr"], "#FFFFFF", "#2B2D35") + path(GEO["de"], "rgba(184,105,46,.10)", "#2B2D35", "ol", 'id="defill"')
          + f'<g id="cufr_g" clip-path="url(#landfr)">{cu_fr}</g><g clip-path="url(#landde)" id="cude_g">{cu_de}</g>'
          + f'<g id="frf" clip-path="url(#clfr)"><path d="{GEO["fr"]}" fill="rgba(25,198,180,.42)"/></g>'
          + f'<g id="def" clip-path="url(#clde)"><path d="{GEO["de"]}" fill="rgba(25,198,180,.42)"/></g>'
          + path(GEO["fr"], "none", "#2B2D35", "ol2") + path(GEO["de"], "none", "#2B2D35", "ol2")
          + f'<path id="rglow" d="{route_d}" fill="none" stroke="{TQ}" stroke-opacity=".35" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
          + f'<path id="route" d="{route_d}" fill="none" stroke="{TQD}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
          + '</g>' + street(FRX, FRY, "fr") + street(DEX, DEY, "de") + '</g></svg>')
# --- Pop-ups (stehen beim Kippen auf) ---
INK = "#2B2D35"
def house(i, lit_col):
    return (f'<svg viewBox="0 0 60 56" width="100%" height="100%"><path d="M6 26 L30 6 L54 26 V52 H6 Z" fill="#FCFCFD" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M6 26 L30 6 L54 26" fill="none" stroke="{PUR}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<rect class="win" x="13" y="31" width="10" height="9" fill="#E6E7EB" stroke="{INK}" stroke-width="2"/><rect class="win" x="37" y="31" width="10" height="9" fill="#E6E7EB" stroke="{INK}" stroke-width="2"/>'
            f'<rect x="25" y="38" width="10" height="14" fill="none" stroke="{INK}" stroke-width="2.5"/></svg>')
import random as _r; _r.seed(11)
pops = []
for kind, cx, cy in (("fr", FRX, FRY), ("de", DEX, DEY)):
    for i, x in enumerate([-9.6, -8.2, -6.8, -5.4, -4.0, -2.6, -1.2, 0.2, 1.6, 3.0, 4.4, 5.8, 7.2, 8.6, 10.0]):
        pops.append(f'<div class="pop house" data-s="{kind}" data-x="{cx+x+_r.uniform(-.15,.15):.2f}" data-y="{cy-1.55:.2f}" data-w="{_r.uniform(.95,1.15):.2f}" data-r="0.93" data-d="{_r.uniform(0,.35):.2f}">{house(i, TQ)}</div>')
# Masten mit altem Telefondraht + neuer Glasfaser (FR)
for j in range(10):
    x0 = FRX - 11 + 1.0 + j * 2.4
    last = j == 9
    seg = (f'<svg viewBox="0 0 240 160" width="100%" height="100%" style="overflow:visible"><path d="M0 160 V14 M0 22 H16 M224 22 H240" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
           + (f'<path d="M240 160 V14 M224 22 H256" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>' if last else '')
           + f'<path d="M0 34 Q120 60 240 34" fill="none" stroke="#9AA0AA" stroke-width="3"/>'
           f'<path class="acab" d="M0 22 Q120 52 240 22" fill="none" stroke="{TQ}" stroke-width="6" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
    pops.append(f'<div class="pop pole" data-s="fr" data-x0="{x0:.2f}" data-x="{x0+1.2:.2f}" data-y="{FRY-0.82:.2f}" data-w="2.4" data-r="{160/240:.4f}" data-d="0">{seg}</div>')
# Bagger (DE) – eigene schlichte Zeichnung
dig = (f'<svg viewBox="0 0 200 120" width="100%" height="100%" style="overflow:visible"><rect x="22" y="92" width="110" height="22" rx="11" fill="#3F434C"/>'
       + "".join(f'<circle cx="{34+k*22}" cy="103" r="6" fill="#9AA0AA"/>' for k in range(5))
       + f'<rect x="28" y="56" width="98" height="36" rx="6" fill="{PUR}" stroke="#4A1FA0" stroke-width="3"/><rect x="34" y="26" width="44" height="34" rx="5" fill="#FCFCFD" stroke="{INK}" stroke-width="3"/>'
       f'<rect x="40" y="32" width="30" height="18" rx="3" fill="#BFE9E4"/>'
       f'<g id="arm" transform="rotate(0 118 62)"><path d="M118 62 L170 26 L196 70" fill="none" stroke="#F2B233" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
       f'<path d="M188 64 L206 76 L196 96 L180 86 Z" fill="#3F434C"/></g></svg>')
pops.append(f'<div class="pop" id="digger" data-s="de" data-x="{DEX:.2f}" data-y="{DEY+1.25:.2f}" data-w="1.9" data-r="0.6" data-d="0">{dig}</div>')
for k in range(8):
    pops.append(f'<div class="pop dirt" data-s="de" data-k="{k}" data-x="{DEX-9+k*1.6:.2f}" data-y="{DEY+0.95:.2f}" data-w="0.75" data-r="0.45" data-d="0">'
                f'<svg viewBox="0 0 60 28" width="100%" height="100%"><path d="M2 27 Q14 4 30 6 Q46 4 58 27 Z" fill="#B07A45" stroke="#5E3A18" stroke-width="2.5"/></svg></div>')
pops.append(f'<div class="pop" id="orbD" data-s="fr" data-x="0" data-y="0" data-w="0.5" data-r="1" data-d="0"><div class="orb"></div></div>')
pops.append(f'<div class="pop" id="orbA" data-s="fr" data-x="0" data-y="0" data-w="0.42" data-r="1" data-d="0"><div class="orb" style="position:absolute;left:0;top:0;width:100%;height:auto;aspect-ratio:1"></div></div>')
plane = (f'<div id="persp"><div id="plane" style="left:{FX0-PW/2}px;top:{FY0-PH/2}px;width:{PW}px;height:{PH}px">{mapsvg}{"".join(pops)}</div></div>')
stage.append(plane); stage.append('<div id="headbg"></div>')
# --- Bildschirm-Labels, die an der Karte hängen (nur Draufsicht) ---
def glab(lon, lat, inner, i, o, d=0, idd=""):
    ii = f' id="{idd}"' if idd else ""
    return (f'<div class="geo" data-x="{WX(lon):.1f}" data-y="{WY(lat):.1f}"><div class="el"{ii} {A(i, o, d)} data-sfx="none" style="left:0;top:0;transform-origin:0 0">'
            f'<div style="transform:translate(-50%,-50%)">{inner}</div></div></div>')
def maplab(t, col): return f'<span class="mono lab" style="color:{col};border-color:{col}">{t}</span>'
FLAG_FR = '<span class="flag"><i style="background:#2B4AA0"></i><i style="background:#fff"></i><i style="background:#D33A3A"></i></span>'
FLAG_DE = '<span class="flag v"><i style="background:#111"></i><i style="background:#D33A3A"></i><i style="background:#F2C230"></i></span>'
geo = (glab(2.2, 47.9, maplab("FRANKREICH", TQD), "p1", "p4@Erstens", -0.6)
       + glab(10.2, 52.6, maplab("DEUTSCHLAND", CU), "p1", "p4@Erstens", -0.6)
       + glab(10.4, 51.5, '<div class="mono" style="font-size:30px;font-weight:800;color:#fff;background:' + CU + ';border-radius:10px;padding:6px 14px;white-space:nowrap">KUPFER = ALTE TELEFONLEITUNG</div>', "p2@Kupfer", "p3@Ende", 0)
       + glab(2.6, 46.6, f'<div class="col"><div class="mono" style="font-size:26px;font-weight:800;color:{TQD};letter-spacing:.08em">KUPFER-AUS</div><div class="huge" id="y30" style="font-size:190px;color:{TQD}">2023</div><div class="mono" style="font-size:28px;font-weight:800;color:{TQD};margin-top:-6px;white-space:nowrap">SCHLUSS MIT DSL</div></div>', "p10@zweitausenddreißig", "p11@Glasfaser", -0.1, "bigyr")
       + glab(2.6, 46.5, f'<div class="col">{FLAG_FR}<div class="huge num" style="color:{TQD}">{cnt(95, "p17@fünfundneunzig", 0, -0.3)}<span class="pc">%</span></div></div>', "p17@fünfundneunzig", "end", -0.15)
       + glab(10.4, 51.0, f'<div class="col">{FLAG_DE}<div class="huge num" style="color:{GR}">{cnt(62, "p18@zweiundsechzig", 0, -0.3)}<span class="pc">%</span></div></div>', "p18@zweiundsechzig", "end", -0.15))
stage.append(f'<div id="geol">{geo}</div>')
# --- Overlays (höchstens eines gleichzeitig) ---
def chip_(txt, i, o, col=PURS, sfx="marker", y=1150, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 22px;border-color:{col};color:{col};background:rgba(255,255,255,.97);white-space:nowrap">{txt}</div>', 80, y, A(i, o, d) + f' data-sfx="{sfx}"', 920, CENTER)
stage.append(chip_(f'{FLAG_FR}&nbsp;?? %&nbsp;&nbsp;<span style="color:#8A8F99">vs.</span>&nbsp;&nbsp;{FLAG_DE}&nbsp;?? %&nbsp;&nbsp;<span style="font-size:22px;color:#8A8F99">AM ENDE</span>', "p3@Vorsprung", "p4@Erstens", GR, "glass", 1130, 36))
stage.append(chip_("1 · KAUM GRABEN", "p4@Erstens", "p5@Teuerste", TQD, "marker", 420, 34))
stage.append(el(f'<div class="stamp mono" style="font-size:38px;white-space:nowrap">GRABEN: BIS ZU 80 % DER KOSTEN</div>', 80, 400, A("p5@Teuerste", "p6@Telefonrohre", -0.15), 920, CENTER))
stage.append(chip_("KABEL DURCH ALTE TELEFONROHRE", "p6@Telefonrohre", "p7@Masten", TQD, "marker", 420))
stage.append(chip_("… ODER AN MASTEN", "p7@Masten", "p8", TQD, "marker", 420, 34))
stage.append(chip_(f'{FLAG_DE}&nbsp;KAUM KABEL AN MASTEN', "p8@selten", "p8@Rohren", CU, "marker", 420))
stage.append(chip_(f'{FLAG_DE}&nbsp;ALTE ROHRE: OFT KEIN PLATZ', "p8@Rohren", "p9", CU, "marker", 420))
stage.append(chip_(f'{FLAG_DE}&nbsp;ALSO: NEU GRABEN', "p9@neu", "p10", CU, "marker", 420, 34))
stage.append(chip_("2 · KUPFER ABSCHALTEN", "p10@Zweitens", "p10@schaltet", TQD, "marker", 1150, 34))
stage.append(el(f'<div class="stamp mono" style="font-size:44px;white-space:nowrap;color:{CU};border-color:{CU}">KUPFERNETZ AUS</div>', 80, 1120, A("p10@schaltet", "p10@zweitausenddreißig", 0.05), 920, CENTER))
stage.append(chip_("DANN NUR NOCH GLASFASER", "p11@Glasfaser", "p12", TQD, "success", 1150))
# Verteilerkasten (eigene Zeichnung): Glasfaser bis zum Kasten, Kupfer bis ins Haus, neues Modul fährt ein
KAST = (f'<svg viewBox="0 0 820 300" width="820" height="300">'
        f'<path d="M20 150 H300" stroke="{TQ}" stroke-width="10" stroke-linecap="round"/><text x="40" y="128" font-family="JBM" font-weight="800" font-size="24" fill="{TQD}">GLASFASER</text>'
        f'<rect x="300" y="40" width="190" height="230" rx="12" fill="#C9CCD3" stroke="#2B2D35" stroke-width="4"/><rect x="312" y="52" width="166" height="206" rx="6" fill="#E4E6EB" stroke="#7A7F8C" stroke-width="2"/>'
        f'<g id="kmod"><rect x="335" y="95" width="120" height="70" rx="8" fill="{PUR}" stroke="#4A1FA0" stroke-width="3"/><text x="395" y="138" text-anchor="middle" font-family="JBM" font-weight="800" font-size="22" fill="#fff">NEU</text></g>'
        f'<text x="395" y="235" text-anchor="middle" font-family="JBM" font-weight="800" font-size="20" fill="#3F434C">GRAUER KASTEN</text>'
        f'<path d="M490 150 H690" stroke="{CU}" stroke-width="8" stroke-linecap="round" stroke-dasharray="2 14"/><text x="520" y="128" font-family="JBM" font-weight="800" font-size="24" fill="{CU}">KUPFER</text>'
        f'<path d="M700 175 L745 135 L790 175 V250 H700 Z" fill="#FCFCFD" stroke="#2B2D35" stroke-width="4" stroke-linejoin="round"/><path d="M700 175 L745 135 L790 175" fill="none" stroke="{PUR}" stroke-width="5"/>'
        f'<path id="kspeed" d="M520 190 h40 m-12 -10 l12 10 l-12 10 M590 190 h40 m-12 -10 l12 10 l-12 10" stroke="{CU}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')
stage.append(card(f'<div class="col" style="gap:6px"><div class="mono small grey">KUPFER WURDE SCHNELLER GEMACHT</div>{KAST}</div>', 90, 560, 900, 400, "", A("p12", "p13", 0.1)))
BARS = (f'<div class="col" style="gap:22px;align-items:stretch;width:100%">'
        f'<div class="mono small grey" style="text-align:center">GESCHWINDIGKEIT (SCHEMATISCH)</div>'
        f'<div><div class="mono" style="font-size:26px;font-weight:800;color:{CU}">KUPFER (NEUE TECHNIK) · BIS 250 MBIT/S</div><div class="hbar"><div class="gbar2" id="bcu" style="width:20%;background:{CU}"></div></div></div>'
        f'<div><div class="mono" style="font-size:26px;font-weight:800;color:{TQD}">GLASFASER · 1.000 MBIT/S UND MEHR</div><div class="hbar"><div class="gbar2" id="bgf" style="width:100%;background:{TQ}"></div></div></div></div>')
stage.append(card(BARS, 90, 600, 900, 330, "activeTQ", A("p13", "p14", 0.05)))
def hs(lit): return (f'<svg viewBox="0 0 60 56" width="110" height="102"><path d="M6 26 L30 6 L54 26 V52 H6 Z" fill="#FCFCFD" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
                     f'<path d="M6 26 L30 6 L54 26" fill="none" stroke="{TQ if lit else "#9AA0AA"}" stroke-width="4"/><rect x="24" y="34" width="12" height="18" fill="{TQ if lit else "#E6E7EB"}" stroke="#2B2D35" stroke-width="2.5"/></svg>')
HOUSES = (f'<div class="col" style="gap:14px"><div class="mono small grey">WO GLASFASER MÖGLICH IST, BESTELLT …</div>'
          f'<div class="row" style="gap:26px">{hs(True)}{hs(False)}{hs(False)}{hs(False)}</div>'
          f'<div class="mono" style="font-size:30px;font-weight:800;color:{TQD}">NUR ETWA 1 VON 4</div></div>')
stage.append(card(HOUSES, 140, 620, 800, 330, "", A("p14", "p16", 0.1)))
stage.append(chip_("WENIGER KUNDEN → WENIGER AUSBAU", "p15@ohne", "p16", CU, "marker", 1000))
stage.append(chip_(f'{FLAG_DE}&nbsp;VOR 1 JAHR: 53 % → HEUTE: 62 %', "p19@Jahr", "end", TQD, "success", 1178))
# dezente Hinweise
stage.append(el('<div class="note mono">KARTE & GLASFASER-FLÄCHEN SCHEMATISCH</div>', 40, 1252, A("p1", "p4@Erstens", -0.6) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">SZENE SCHEMATISCH</div>', 40, 1252, A("p4@kaum", "p10@Frankreich", 0.3) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">FLÄCHEN SCHEMATISCH · BMBIT/S-ANGABEN: HÖCHSTWERTE</div>'.replace("BMBIT","MBIT"), 40, 1252, A("p10@Frankreich", "p17", 0.3) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">ANTEIL WOHNUNGEN/BÜROS MIT GLASFASER-ANSCHLUSSMÖGLICHKEIT · QUELLEN: ARCEP, BREKO · STAND 30.06.2026</div>', 40, 1252, A("p17", "end", 0.2) + ' data-sfx="none"'))
CAMJS = json.dumps(cam)

SCENE_JS = r''' // ---- Bühne ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const K=PAN.cam.map(k=>[TS(k[0],k[1]),k[2],k[3],k[4],k[5]]);
  const sm=u=>u*u*(3-2*u);
  let C=K[0]; if(t>=K[K.length-1][0]) C=K[K.length-1]; else for(let i=0;i<K.length-1;i++){ const a=K[i],q=K[i+1]; if(t>=a[0]&&t<q[0]){ const u=sm((t-a[0])/Math.max(1e-6,q[0]-a[0]));
     // Zoom logarithmisch; Mittelpunkt so, dass Fokuspunkt auf dem Bildschirm sauber wandert
     const z=Math.exp(Math.log(a[3])+(Math.log(q[3])-Math.log(a[3]))*u);
     const w=(1/z-1/a[3])/((1/q[3]-1/a[3])||1e-9); const v=(Math.abs(q[3]-a[3])<1e-6)?u:cl(w,0,1);
     C=[t,a[1]+(q[1]-a[1])*v,a[2]+(q[2]-a[2])*v,z,a[4]+(q[4]-a[4])*u]; break; } }
  const fx=C[1], fy=C[2], z=C[3], tilt=C[4], k=tilt/60;
  const CX=PAN.PW/2, CY=PAN.PH/2;
  document.getElementById('camg').setAttribute('transform',`translate(${CX},${CY}) scale(${z}) translate(${-fx},${-fy})`);
  document.getElementById('plane').style.transform=`rotateX(${tilt}deg)`;
  const pj=(x,y)=>[CX+(x-fx)*z, CY+(y-fy)*z];
  document.querySelectorAll('.ol').forEach(e=>e.setAttribute('stroke-width',(1.7/z).toFixed(4)));
  document.querySelectorAll('.ol2').forEach(e=>e.setAttribute('stroke-width',(2.2/z).toFixed(4)));
  const mapA=1-pr(z,22,10);              // Kartenebene ausblenden, wenn ganz nah
  const ML=document.getElementById('mapl'); ML.style.opacity=mapA; ML.style.display=mapA<0.01?'none':'';
  // Glasfaser-Route (Hauptdarsteller) zeichnet sich durch Frankreich
  const bo2=x=>1+2.70158*Math.pow(x-1,3)+1.70158*Math.pow(x-1,2); const FX0=PAN.FX0, FY0=PAN.FY0;
  const ur=0.18+0.82*ease(pr(t,0,TS('p3@Ende',0)));
  for(const id of ['route','rglow']){ const r=document.getElementById(id); r.style.strokeDashoffset=1-ur; r.setAttribute('stroke-width',((id==='route'?4.2:13)/z).toFixed(4)); }
  // FR-Flächen wachsen, wenn die Route ankommt
  document.querySelectorAll('.cfr').forEach(c=>{ const f=+c.dataset.f; const q=ease(pr(ur,f-0.05,0.14));
    c.setAttribute('r',(+c.dataset.r*q).toFixed(1)); });
  const pulse=t>TS('p11@Glasfaser',-0.2)&&t<TS('p12',0)?0.5+0.5*Math.sin((t-TS('p11@Glasfaser',-0.2))*2*Math.PI/0.6-Math.PI/2):0;
  document.getElementById('frf').style.opacity=0.85+0.15*pulse;
  document.getElementById('frf').firstElementChild.setAttribute('fill',`rgba(25,198,180,${.42+.25*pulse})`);
  // DE-Flächen: erst bei der Auflösung
  const t62=TS('p18@uns',-0.1);
  document.querySelectorAll('.cde').forEach(c=>{ const q=ease(pr(t,t62+(+c.dataset.f)*0.9,0.5)); c.setAttribute('r',(+c.dataset.r*q).toFixed(1)); });
  // Kupfer
  const cuw=1.6/z; const boost=pr(t,TS('p12@Technik',-0.2),0.5)*(1-pr(t,TS('p13',0),0.4));
  document.querySelectorAll('.cude').forEach((e,i)=>{ e.setAttribute('stroke-width',(cuw*(1.6+1.6*boost)).toFixed(4)); e.style.strokeDashoffset=0;
     e.setAttribute('stroke', boost>0.05?`rgb(${Math.round(184+60*boost)},${Math.round(105+40*boost)},46)`:'#B8692E'); });
  document.getElementById('cude_g').style.filter=boost>0.05?`drop-shadow(0 0 ${(6*boost).toFixed(1)}px rgba(242,140,40,.9))`:'none';
  const off=TS('p10@schaltet',0.0);
  document.querySelectorAll('.cufr').forEach((e,i)=>{ const q=ease(pr(t,off+(i%7)*0.07,0.5)); e.style.strokeDashoffset=q; e.setAttribute('stroke-width',(cuw*1.2).toFixed(4)); });
  document.getElementById('cufr_g').style.opacity=0.35;
  // Abdunkeln für die Abschlussfrage
  document.getElementById('camg').style.opacity=(1-0.45*pr(t,TS('p12',0.0),0.4)*(1-pr(t,TS('p16',-0.2),0.4)))*(1-pr(t,END,0.35));
  // Straßenszenen
  const gA=pr(z,8,6);
  const inFR=t<TS('p8@Kabel',0.0), inDE=!inFR&&t<TS('p10@Frankreich',0.5);
  document.getElementById('st_fr').style.opacity=inFR?gA:0; document.getElementById('st_de').style.opacity=inDE?gA:0;
  const sw=(n)=>n; // Weltbreiten sind fest
  // FR: Leerrohr-Puls, Kabel ziehen, Masten
  const du=document.getElementById('duct'); const dp=t>TS('p6@Telefonrohre',-0.1)&&t<TS('p6@gezogen',0)?0.5+0.5*Math.sin((t-TS('p6@Telefonrohre',-0.1))*2*Math.PI/0.5):0;
  du.setAttribute('stroke-width',(0.09+0.07*dp).toFixed(3)); du.setAttribute('stroke',dp>0.01?'#5B2BB5':'#7A7F8C');
  const u1=ease(pr(t,TS('p6@gezogen',-0.3),1.4)), u2=ease(pr(t,TS('p7@Masten',0.25),1.0));
  document.getElementById('dcab').style.strokeDashoffset=1-u1;
  const hx1=PAN.FRX-11+22*u1, hx2=PAN.FRX-11+22*u2;
  // DE: Bagger gräbt
  const dgx=fx+1.3; const tf=cl((dgx-0.7-(PAN.DEX-11))/22,0,1);
  const tvis=t>=TS('p9',-0.2); const tf2=tvis?tf:0;
  document.getElementById('trench').style.strokeDashoffset=1-tf2;
  document.getElementById('trench2').style.strokeDashoffset=1-tf2;
  document.getElementById('arm').setAttribute('transform',`rotate(${(14*Math.sin(t*2*Math.PI/0.7)).toFixed(1)} 118 62)`);
  // Pop-ups positionieren
  for(const p of document.querySelectorAll('#plane .pop')){
    const s=p.dataset.s; const on=(s==='fr'&&inFR)||(s==='de'&&inDE);
    let x=+p.dataset.x, y=+p.dataset.y, w=(+p.dataset.w)*z, hgt=w*(+p.dataset.r);
    let a=bo2(pr(k,0.35+(+p.dataset.d)*0.6,0.35));
    if(p.classList.contains('pole')){ const x0=+p.dataset.x0; a=bo2(pr(t,TS('p7@Masten',-0.25)+(x0-PAN.FRX+10)*0.02,0.4))*(k>0.5?1:0); p.querySelector('.acab').style.strokeDashoffset=1-cl((hx2-x0)/2.4,0,1); }
    if(p.id==='digger'){ x=dgx; a=bo2(pr(t,TS('p9',-0.2),0.35)); }
    if(p.classList.contains('dirt')){ a=tvis?bo2(cl((dgx-x-1.0)/0.6,0,1)):0; }
    let flatp=false;
    if(p.id==='orbD'){ x=hx1; y=PAN.FRY+0.28; a=(t>TS('p6@gezogen',-0.3)&&u1<0.999)?1:0; hgt=w; flatp=true; }
    if(p.id==='orbA'){ x=hx2; const sp=((((hx2-(PAN.FRX-10))/2.4)%1)+1)%1; const yy=22+60*sp*(1-sp);
       y=PAN.FRY-0.82; hgt=((160-yy)/100+(+p.dataset.w)*0.5)*z; a=(t>TS('p7@Masten',0.25)&&u2<0.999)?1:0; }
    const [px,py]=pj(x,y);
    p.style.width=w+'px'; p.style.height=hgt+'px';
    const isOrb=p.id==='orbD'||p.id==='orbA';
    const up=flatp?`translate(${px-w/2}px,${py-w/2}px)`:`translate(${px-w/2}px,${py-hgt}px) rotateX(${-tilt}deg) scaleY(${isOrb?1:Math.max(0.001,a)})`;
    p.style.transform=up; p.style.opacity=on&&gA>0.5&&(isOrb?a>0:k>0.3)?1:0; p.style.zIndex=Math.round(py)+(isOrb?50:0);
    if(p.classList.contains('house')){ const lit=s==='fr'&&(x<hx1||x<hx2)&&t<TS('p8',0);
       p.querySelectorAll('.win').forEach(wn=>{ wn.setAttribute('fill',lit?'#19C6B4':'#E6E7EB'); }); p.style.filter=lit?'drop-shadow(0 0 10px rgba(25,198,180,.8))':'none'; }
  }
  // Bildschirm-Labels an der Karte (nur Draufsicht)
  const flat=1-pr(tilt,0.5,4);
  document.getElementById('geol').style.opacity=flat*(1-pr(t,END,0.3));
  for(const g of document.querySelectorAll('.geo')){ const sx=FX0+(+g.dataset.x-fx)*z, sy=FY0+(+g.dataset.y-fy)*z; g.style.left=sx+'px'; g.style.top=sy+'px'; }
  // 2030-Zähler
  { const dd=document.getElementById('ductde'); const q=t>TS('p8@Rohren',-0.1)&&t<TS('p9',0)?0.5+0.5*Math.sin((t-TS('p8@Rohren',-0.1))*2*Math.PI/0.5-Math.PI/2):0; dd.setAttribute('stroke-opacity',(0.55*q).toFixed(2)); }
  document.getElementById('kmod').setAttribute('transform',`translate(0,${(-170*(1-ease(pr(t,TS('p12@Technik',-0.15),0.45)))).toFixed(1)})`);
  document.getElementById('kmod').style.opacity=pr(t,TS('p12@Technik',-0.15),0.15);
  document.getElementById('kspeed').style.opacity=pr(t,TS('p12@schneller',-0.1),0.3)*(0.6+0.4*Math.sin(t*12));
  document.getElementById('bcu').style.width=(20*ease(pr(t,TS('p13',0.1),0.6)))+'%';
  document.getElementById('bgf').style.width=(100*ease(pr(t,TS('p13@Vielfaches',-0.3),0.9)))+'%';
  document.getElementById('y30').textContent=2023+Math.round(7*ease(pr(t,TS('p10@zweitausenddreißig',-0.1),0.9)));
  // Roboter-Position (Hook rechts unten, CTA wie Template)
  document.getElementById('robot').style.left=(t>=END?40:700)+'px';
  document.getElementById('headbg').style.opacity=1-pr(t,TS('p4',-0.15),0.3);
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
#persp{{position:absolute;left:0;top:0;width:1080px;height:1920px;perspective:1150px;perspective-origin:540px 640px;overflow:hidden;background:linear-gradient(#ECEEF8,#FFFFFF 55%)}}
#plane{{position:absolute;transform-style:preserve-3d;transform-origin:50% 50%;
background:linear-gradient(rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(90deg,rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,
linear-gradient(rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,linear-gradient(90deg,rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,#FCFCFD}}
.pop{{position:absolute;left:0;top:0;transform-origin:50% 100%;transform-style:preserve-3d}}
.orb{{width:100%;height:100%;border-radius:50%;background:radial-gradient(circle,#FFFFFF 0 22%,#19C6B4 45%,rgba(25,198,180,0) 72%)}}
#headbg{{position:absolute;left:0;top:0;width:1080px;height:560px;background:linear-gradient(rgba(255,255,255,.97) 60%,rgba(255,255,255,0))}}
#head{{top:200px;z-index:3}}
.geo{{position:absolute;width:0;height:0}}
.lab{{font-size:26px;font-weight:800;background:rgba(255,255,255,.94);border:2.5px solid;border-radius:8px;padding:5px 12px;white-space:nowrap}}
.flag{{display:inline-flex;width:54px;height:36px;border-radius:5px;overflow:hidden;box-shadow:0 0 0 2px rgba(26,31,51,.25);vertical-align:middle}} .flag i{{flex:1}}
.flag.v{{flex-direction:column}}
.col .flag{{width:96px;height:64px;margin-bottom:6px}}
.num{{font-size:150px;letter-spacing:-6px;white-space:nowrap;text-shadow:0 0 18px #fff,0 0 8px #fff}} .pc{{font-size:76px;letter-spacing:0;margin-left:6px}}
#y30{{text-shadow:0 0 18px #fff,0 0 8px #fff}}
.note{{font-size:16px;color:#8A8F99;background:rgba(255,255,255,.9);border:1.5px solid #C9CCD3;border-radius:8px;padding:5px 9px;white-space:nowrap}}
</style></head><body><div id="v">
<div id="chap" class="mono"></div><div id="prog">{"".join("<div></div>" for _ in CH)}</div><div id="wm">{mono}</div>
<div id="head"></div>
{"".join(stage)}
{endcard}
<div id="robot">{robots}</div>
<div id="cap"><div id="pill"></div></div>
</div>
<script>
const PAN={json.dumps(dict(cam=cam,PW=PW,PH=PH,FX0=FX0,FY0=FY0,FRX=FRX,FRY=FRY,DEX=DEX,DEY=DEY), ensure_ascii=False)};
const BEATS={json.dumps(beats, ensure_ascii=False)};
const S={json.dumps(S, ensure_ascii=False)}; const CH={json.dumps(CH, ensure_ascii=False)}; const END={END:.3f}; const AUD={AUD:.3f};
const cl=(x,a,b)=>Math.max(a,Math.min(b,x)); const ease=p=>1-Math.pow(1-p,3); const pr=(t,t0,d)=>cl((t-t0)/d,0,1);
const els=[...document.querySelectorAll('[data-in]')];
function beatAt(t){{let b=BEATS[0];for(const x of BEATS) if(t>=x.s) b=x; return b;}}
window.render=function(t){{
 const end=t>=END; const b=beatAt(t);
 document.getElementById('chap').textContent=CH[b.ch];
 [...document.querySelectorAll('#prog div')].forEach((d,i)=>d.className=i<=b.ch?'on':'');
 const top=cl(1-pr(t,END,.3),0,1); ['chap','prog','head'].forEach(id=>document.getElementById(id).style.opacity=top);
 let hs=b.s; for(let i=BEATS.indexOf(b);i>0&&BEATS[i-1].head===b.head;i--) hs=BEATS[i-1].s;
 const H=document.getElementById('head'); H.innerHTML=b.head; H.style.fontSize='64px'; if(BEATS.indexOf(b)===0) hs=-1; const hp=ease(pr(t,hs,.3));
 const g=Math.round(181+(11-181)*hp), g2=Math.round(184+(11-184)*hp), g3=Math.round(192+(16-192)*hp); H.style.color=`rgb(${{g}},${{g2}},${{g3}})`;
 // elements
 for(const e of els){{
  const tin=(S[e.dataset.in]??(console.log('missing '+e.dataset.in),0))+(+e.dataset.d||0); const tout=e.dataset.out?S[e.dataset.out]:1e9;
  const pi=ease(pr(t,tin,.35)), po=pr(t,tout,.2);
  e.style.opacity=pi*(1-po); e.style.transform=`translateY(${{16*(1-pi)}}px)`;
 }}
 // counters
 for(const c of document.querySelectorAll('.count')){{const t0=(S[c.dataset.cin]??0)+(+c.dataset.cd||0); const dd=+c.dataset.dec||0; const v=+c.dataset.count*ease(pr(t,t0,0.8)); c.textContent=v.toFixed(dd).replace('.',',');}}
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
