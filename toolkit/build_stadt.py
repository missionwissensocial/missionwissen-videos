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
HOOK = 'Was ist <span style="color:#7B3FE4">älter</span>: Pyramiden oder die erste Stadt?'
B = [
 ("s1", 0, HOOK, "Was ist *älter:* die *großen* *Pyramiden* in *Ägypten* oder die *erste* *Stadt* der *Welt?*", "staunt"),
 ("s2", 0, HOOK, "Die *Antwort* verrate ich dir am *Ende.*", None),
 ("s3", 1, "", "Lange zogen *alle* *Menschen* als *Jäger* und *Sammler* umher.", None),
 ("s4", 1, "", "Dann *blieben* einige dort, wo es *Wasser* und *Nahrung* gab: an einer *Quelle* nahe dem *Toten* *Meer.*", None),
 ("s5", 1, "", "Dort entstand *Jericho.*", None),
 ("s6", 2, "", "Vor mehr als *zehntausend* *Jahren* bauten die Bewohner eine *Mauer* aus *Stein* und einen *runden* *Turm,* über *acht* *Meter* hoch.", None),
 ("s7", 2, "", "War *Jericho* damit schon eine *Stadt?*", None),
 ("s8", 2, "", "Die meisten Forscher sagen: *Nein.* Dort lebten wohl nur *einige* *hundert* bis *wenige* *tausend* Menschen. Eher ein *großes* *Dorf.*", None),
 ("s9", 3, "", "Denn zu einer *Stadt* gehören *sehr* *viele* *Menschen,* *Handwerker* und *Beamte,* die die *Vorräte* verwalten.", None),
 ("s10", 3, "", "Die *erste* *echte* *Stadt* entstand erst *viel* *später:* *Uruk,* im heutigen *Irak.*", None),
 ("s11", 3, "", "Vor gut *fünftausend* *Jahren* lebten in *Uruk* *Zehntausende* *Menschen.*", None),
 ("s12", 4, "", "Die *Antwort* also: *Jericho* ist über *zehntausend* *Jahre* alt, war aber nur ein *Dorf.*", None),
 ("s13", 4, "", "*Uruk* ist über *fünftausend* *Jahre* alt.", None),
 ("s14", 4, "", "Und die *großen* *Pyramiden* etwa *viertausendfünfhundert.*", None),
 ("s15", 4, "", "Die *erste* *Stadt* war also *vor* den *Pyramiden* da.", None),
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
GEO = json.load(open("geo.json")); K = GEO["K"]; CXF = GEO["CX"]
def WX(lon): return (lon + 180) * K * CXF
def WY(lat): return (90 - lat) * K
MAPTOP = 300; MAPH = 980
def CAMAT(lat, lon, z, sx, sy):
    return [round(WX(lon) + (540 - sx) / z, 3), round(WY(lat) + (MAPTOP + 360 - sy) / z * 0, 3), z, sy - MAPTOP]
JLAT, JLON = 31.871, 35.444      # Tell es-Sultan (Jericho)
ULAT, ULON = 31.322, 45.636      # Uruk (Warka)
GLAT, GLON = 29.979, 31.134      # Gizeh
JX, JY = WX(JLON), WY(JLAT); UX, UY = WX(ULON), WY(ULAT); GX, GY = WX(GLON), WY(GLAT)
VZ = 600.0                       # Referenz-Zoom des Dorfes (px-Koordinaten relativ zu Jericho)
OV0 = CAMAT(31.0, 38.6, 18.0, 540, 640); OV1 = CAMAT(31.1, 38.2, 19.5, 540, 640)
JZ = CAMAT(JLAT, JLON, 150, 540, 720); JV = CAMAT(JLAT, JLON, VZ, 540, 720); JV2 = CAMAT(JLAT, JLON, 470, 540, 700)
JT = CAMAT(JLAT, JLON, 1100, 540, 690); JV3 = CAMAT(JLAT, JLON, 820, 540, 700)
MID = CAMAT(31.6, 40.6, 36, 540, 700)
UZ = CAMAT(ULAT, ULON, 250, 540, 700); UZ2 = CAMAT(ULAT, ULON, 290, 540, 700)
FIN = CAMAT(30.9, 38.4, 19, 540, 560)
cam = [("s1", -0.6, *OV0), ("s3", 0, *OV1), ("s4@Quelle", -0.3, *OV1), ("s4@Meer", 0.1, *JZ), ("s5", 0, *JZ), ("s5@Jericho", 0.35, *JV),
       ("s6", 0.0, *JV), ("s6@Mauer", 0.1, *JT), ("s7", -0.1, *JT), ("s7@Stadt", 0.2, *JV3), ("s9", 0, *JV3), ("s10", 0, *JV2),
       ("s10@später", -0.2, *MID), ("s10@Irak", 0.0, *UZ), ("s11", 0, *UZ), ("s12", -0.2, *UZ2), ("s12@Jericho", 0.2, *FIN)]
# Wander-Spur der Jäger und Sammler (lon, lat) -> endet an der Quelle von Jericho
TRAIL = [(32.4, 30.6), (33.6, 30.2), (34.6, 31.0), (34.3, 32.6), (35.6, 34.0), (37.4, 35.4), (39.2, 36.0), (38.6, 34.4), (36.9, 33.2), (36.0, 32.4), (JLON, JLAT)]
TR = [[round(WX(lo), 3), round(WY(la), 3)] for lo, la in TRAIL]
trail_d = "M" + "L".join(f"{x} {y}" for x, y in TR)
# Dorf-Layout in px bei Referenz-Zoom VZ (relativ zu Jericho, y nach unten)
HUTS = [(-215, 40), (-150, 8), (150, 30), (220, 6), (-100, -42), (115, -46)]
SPRING = (175, 98)
TOWER = (-10, 22)
G1 = [(-175, 62), (-62, 58), (68, 56), (128, 62), (-130, -6), (60, -14), (190, -24), (-210, -10)]
import random as _r; _r.seed(3)
G2 = []
while len(G2) < 16:
    x, y = _r.uniform(-250, 250), _r.uniform(-70, 60)
    if abs(x) < 70 and y < 30: continue
    if all((x - a) ** 2 + (y - b) ** 2 > 38 ** 2 for a, b in G1 + G2): G2.append((round(x), round(y)))
URX, URY = 0.5 * K * CXF, 0.36 * K
G3 = []
while len(G3) < 150:
    x, y = _r.uniform(-1, 1), _r.uniform(-1, 1)
    if x * x + y * y < 0.88 and not (abs(x) < 0.2 and abs(y) < 0.24): G3.append((round(UX + x * URX, 3), round(UY + y * URY, 3)))
G3.sort(key=lambda p: (p[0] - UX) ** 2 + (p[1] - UY) ** 2)
ppl = ([dict(g=1, v=[round(JX + a / VZ, 4), round(JY + b / VZ, 4)], o=[round(_r.uniform(-.55, .55), 3), round(_r.uniform(-.45, .45), 3)]) for a, b in G1]
       + [dict(g=2, v=[round(JX + a / VZ, 4), round(JY + b / VZ, 4)]) for a, b in G2]
       + [dict(g=3, v=list(p)) for p in G3])
PANJS = dict(cam=cam, tr=TR, ppl=ppl, J=[JX, JY], U=[UX, UY], G=[GX, GY], VZ=VZ)

PURS = "#5B2BB5"; GR = "#3F434C"; TQD = "#0E8C80"; SAND = "#B88A1A"; WAT = "#4BA3D9"
land = f'<path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
cty = f'<path d="{GEO["cty"]}" fill="none" stroke="#C3C7CF" stroke-width="1" stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/>'
lakes = f'<path d="{GEO["lakes"]}" fill="#CFE7F6" stroke="{WAT}" stroke-width="1.2" vector-effect="non-scaling-stroke"/>'
rivers = "".join(f'<path d="{d}" fill="none" stroke="{WAT}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" opacity=".85"/>' for d in GEO["rivers"].values())
uell = f'M{UX-URX:.3f} {UY:.3f}A{URX:.3f} {URY:.3f} 0 1 0 {UX+URX:.3f} {UY:.3f}A{URX:.3f} {URY:.3f} 0 1 0 {UX-URX:.3f} {UY:.3f}Z'
mapsvg = (f'<svg width="1080" height="{MAPH}" style="position:absolute;left:0;top:0;overflow:hidden"><g id="mapg">{land}{cty}{lakes}{rivers}'
          f'<path id="trail" d="{trail_d}" fill="none" stroke="{PUR}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" opacity=".75"/>'
          f'<path id="hop" d="M{JX:.3f} {JY:.3f}Q{(JX+UX)/2:.3f} {min(JY,UY)-4:.3f} {UX:.3f} {UY:.3f}" fill="none" stroke="{PUR}" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
          f'<g id="e_ur" style="opacity:0"><path d="{uell}" fill="rgba(123,63,228,.14)"/>'
          f'<path id="uwall" d="{uell}" fill="none" stroke="{PURS}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" stroke-linecap="round"/></g>'
          + '</g></svg>')
def lab(lat, lon, text, i, o, col=PUR, d=0, pin=True, lid="", wx=None, wy=None, dx=0, dy=0, sfx=""):
    p = f'<span class="pin" style="background:{col}"></span>' if pin else ""
    idd = f' id="{lid}"' if lid else ""
    gx = wx if wx is not None else WX(lon); gy = wy if wy is not None else WY(lat)
    sf = f' data-sfx="{sfx}"' if sfx else ""
    return (f'<div class="geo" data-x="{gx:.3f}" data-y="{gy:.3f}">'
            f'<div class="el mk"{idd} {A(i, o, d)}{sf} style="left:{(-11 if pin else -70) + dx}px;top:{-14 + dy}px;gap:8px">{p}'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
def popg(wx, wy, inner, gid, zs, smax=2.0):
    """Pop-up, im Kartenraum verankert, skaliert mit Zoom/zs (Basis unten Mitte)."""
    return f'<div class="geo pz" data-x="{wx:.4f}" data-y="{wy:.4f}" data-zs="{zs}" data-smax="{smax}"><div id="{gid}" class="pop">{inner}</div></div>'
# eigene schlichte Skizzen
pyr_svg = ('<svg width="190" height="120" viewBox="0 0 190 120" style="position:absolute;left:-95px;top:-112px;overflow:visible">'
           '<path d="M8 112L62 40L116 112Z" fill="#F3E3B8" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M62 40L80 112" stroke="#2B2D35" stroke-width="1.6" opacity=".5"/>'
           '<path d="M92 112L136 52L180 112Z" fill="#F7EBC9" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M136 52L150 112" stroke="#2B2D35" stroke-width="1.6" opacity=".5"/><path d="M0 112H190" stroke="#2B2D35" stroke-width="2.4"/></svg>')
def hut_svg():
    return ('<svg width="66" height="48" viewBox="0 0 66 48" style="position:absolute;left:-33px;top:-46px;overflow:visible">'
            '<path d="M5 46C5 14 61 14 61 46Z" fill="#F1E6D2" stroke="#2B2D35" stroke-width="2.6" stroke-linejoin="round"/>'
            '<path d="M27 46V33a6 6 0 0 1 12 0V46" fill="#2B2D35" opacity=".75"/><path d="M14 30q19-10 38 0" stroke="#2B2D35" stroke-width="1.2" fill="none" opacity=".45"/></svg>')
stones = "".join(f'<path d="M{x} {y}h22" stroke="#2B2D35" stroke-width="1.2" opacity=".45"/>' for x in range(14, 470, 30) for y in (12, 24))
stones += "".join(f'<path d="M{x} 0v12M{x+15} 12v12M{x} 24v12" stroke="#2B2D35" stroke-width="1.2" opacity=".45"/>' for x in range(14, 470, 30))
wall_svg = (f'<svg width="500" height="36" viewBox="0 0 500 36" style="position:absolute;left:-250px;top:-36px;overflow:visible">'
            f'<path id="wallp" d="M0 0H500V36H0Z" fill="#E6DCCB" stroke="#2B2D35" stroke-width="2.6" stroke-linejoin="round"/>{stones}</svg>')
tring = "".join(f'<path d="M6 {y}Q55 {y+9} 104 {y}" stroke="#2B2D35" stroke-width="1.3" fill="none" opacity=".5"/>' for y in range(24, 150, 18))
tower_svg = ('<svg width="110" height="156" viewBox="0 0 110 156" style="position:absolute;left:-55px;top:-156px;overflow:visible">'
             '<path d="M6 154V14Q55 0 104 14V154Z" fill="#E9DFCC" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="55" cy="14" rx="49" ry="9" fill="#F4EDE0" stroke="#2B2D35" stroke-width="2.6"/>'
             f'{tring}<path d="M44 154V128a11 11 0 0 1 22 0V154" fill="#2B2D35" opacity=".8"/></svg>')
spring_svg = ('<svg width="110" height="44" viewBox="0 0 110 44" style="position:absolute;left:-55px;top:-22px;overflow:visible">'
              f'<ellipse cx="55" cy="22" rx="52" ry="19" fill="#CFE7F6" stroke="{WAT}" stroke-width="3"/>'
              f'<path d="M30 20q6-5 12 0t12 0M58 27q6-5 12 0t12 0" stroke="{WAT}" stroke-width="2.4" fill="none"/></svg>')
zig_svg = ('<svg width="170" height="96" viewBox="0 0 170 96" style="position:absolute;left:-85px;top:-92px;overflow:visible">'
           '<path d="M4 94H166V70H4Z" fill="#E9DFCC" stroke="#2B2D35" stroke-width="2.8"/><path d="M28 70H142V44H28Z" fill="#EFE6D6" stroke="#2B2D35" stroke-width="2.8"/>'
           '<path d="M54 44H116V18H54Z" fill="#F4EDE0" stroke="#2B2D35" stroke-width="2.8"/><path d="M85 94V18" stroke="#2B2D35" stroke-width="2" stroke-dasharray="5 5" opacity=".6"/></svg>')
qbadge = ('<div style="position:absolute;left:-46px;top:-46px;width:92px;height:92px;border-radius:50%;background:#7B3FE4;color:#fff;font-family:Unbounded;font-weight:600;'
          'font-size:58px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 6px rgba(123,63,228,.22),0 6px 16px rgba(26,31,51,.25)">?</div>')
geo_ov = (
    popg(GX, GY, pyr_svg, "pyr", 13, 1.6)
    + f'<div class="geo" data-x="{WX(41.0):.3f}" data-y="{WY(33.6):.3f}"><div id="qb" style="position:absolute;left:0;top:0">{qbadge}</div></div>'
    + lab(GLAT, GLON, "PYRAMIDEN", "s1", "s3", SAND, -0.6, False, "lpy", dx=-40, dy=14, sfx="none")
    + lab(0, 0, "ERSTE STADT?", "s1", "s3", PUR, -0.6, False, "lq", wx=WX(41.0), wy=WY(33.6), dx=-40, dy=56, sfx="none")
    + lab(31.25, 35.75, "TOTES MEER", "s4@Toten", "s6", WAT, 0, False, dx=28, dy=-10, sfx="marker")
    + "".join(popg(JX + hx / VZ, JY + hy / VZ, hut_svg(), f"hut{k}", VZ) for k, (hx, hy) in enumerate(HUTS))
    + popg(JX + TOWER[0] / VZ, JY + TOWER[1] / VZ, tower_svg, "tower", VZ)
    + popg(JX, JY + 70 / VZ, wall_svg, "wall", VZ)
    + popg(JX + SPRING[0] / VZ, JY + SPRING[1] / VZ, spring_svg, "spring", VZ)
    + lab(0, 0, "QUELLE", "s4@Quelle", "s6@Mauer", WAT, 0.5, False, wx=JX + SPRING[0] / VZ, wy=JY + (SPRING[1] + 34) / VZ, dx=10, dy=0, sfx="marker")
    + lab(JLAT, JLON, "JERICHO", "s5@Jericho", "s6@Mauer", PURS, 0.15, True, dx=0, dy=-10, sfx="marker")
    + lab(0, 0, "8 M", "s6@acht", "s7@Stadt", PURS, 0, False, wx=JX + (TOWER[0] + 62) / VZ, wy=JY + (TOWER[1] - 150) / VZ, dx=20, dy=0, sfx="marker")
    + popg(UX, UY + 0.06, zig_svg, "zig", 250, 1.3)
    + lab(ULAT, ULON, "URUK", "s10@Uruk", "s12", PURS, 0, True, dx=0, dy=-150, sfx="marker")
    + lab(31.72, 45.2, "HEUTE: IRAK", "s10@Irak", "s11@Zehntausende", GR, 0, False, sfx="marker")
    + lab(JLAT, JLON, "JERICHO", "s12@Jericho", "end", GR, 0, True, lid="fj", dx=0, dy=-12, sfx="none")
    + lab(ULAT, ULON, "URUK", "s13@Uruk", "end", PURS, 0, True, lid="fu", dx=0, dy=-12, sfx="none")
    + lab(GLAT, GLON, "PYRAMIDEN", "s14@Pyramiden", "end", SAND, 0, False, lid="fp", dx=-30, dy=26, sfx="none")
)
tick_ = f'<div style="position:absolute;left:-2px;top:-170px;width:4px;height:150px;background:{PURS};border-radius:2px"></div><div style="position:absolute;left:-12px;top:-170px;width:24px;height:4px;background:{PURS}"></div><div style="position:absolute;left:-12px;top:-24px;width:24px;height:4px;background:{PURS}"></div>'
geo_ov += f'<div class="geo pz" data-x="{JX + (TOWER[0] + 75) / VZ:.4f}" data-y="{JY + (TOWER[1] + 20) / VZ:.4f}" data-zs="{VZ}" data-smax="2"><div id="meas" class="pop">{tick_}</div></div>'
note = el('<div class="note mono">KARTE: NATURAL EARTH · ORTE UND GEBÄUDE SCHEMATISCH</div>', 18, MAPH - 46, A("s1", "end", -0.6) + ' data-sfx="none"')
people = "".join(f'<div class="ppl g{p["g"]}" style="opacity:0"></div>' for p in ppl)
stage.append(f'<div class="el mapwrap" data-in="s1" data-d="-0.6" data-out="end" data-sfx="none" style="left:0;top:{MAPTOP}px;width:1080px;height:{MAPH}px">{mapsvg}{geo_ov}<div id="pplw">{people}</div>{note}</div>')

# ---- Overlays (max. eins gleichzeitig) ----
OY = 1150
def chip_(txt, i, o, col=PURS, sfx="marker", icon="", y=OY, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 20px;border-color:{col};color:{col};background:rgba(255,255,255,.97);font-weight:700">{icon}{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
I.update(drop='<path d="M24 5C17 16 11 23 11 30a13 13 0 0 0 26 0c0-7-6-14-13-25z"/>',
         grain='<path d="M24 44V14"/><path d="M24 20c-6-1-9-5-9-10 6 0 9 4 9 10zM24 20c6-1 9-5 9-10-6 0-9 4-9 10zM24 30c-6-1-9-5-9-10 6 0 9 4 9 10zM24 30c6-1 9-5 9-10-6 0-9 4-9 10z"/>',
         walk='<circle cx="26" cy="8" r="4"/><path d="M24 15l-4 13 6 6 2 10M20 28l-6 14M24 18l8 6M22 18l-8 6"/>',
         crowd='<circle cx="14" cy="16" r="5"/><circle cx="34" cy="16" r="5"/><circle cx="24" cy="12" r="5"/><path d="M4 40c0-7 4-11 10-11M44 40c0-7-4-11-10-11M14 42c0-8 4-12 10-12s10 4 10 12"/>',
         hammer='<path d="M28 6l14 14-6 6-14-14z"/><path d="M25 17L8 34a3.5 3.5 0 0 0 5 5l17-17"/>',
         tablet='<rect x="9" y="5" width="30" height="38" rx="5"/><path d="M15 14l4 3 4-3M27 14h6M15 23h6M25 23l4 3 4-3M15 32l4 3 4-3M27 32h6"/>',
         jar='<path d="M17 6h14M18 6v6c-6 4-9 10-9 17 0 8 6 13 15 13s15-5 15-13c0-7-3-13-9-17V6"/>',
         check='<path d="M10 25l9 9 19-20"/>')
stage.append(chip_("ANTWORT KOMMT AM ENDE", "s2@Antwort", "s3", PURS, "glass", "", OY, 32, -0.1))
stage.append(chip_("JÄGER UND SAMMLER ZIEHEN UMHER", "s3@Jäger", "s4", PURS, "marker", ic(I["walk"], 40, PURS, 3), OY, 29, -0.2))
stage.append(chip_("WASSER + NAHRUNG", "s4@Wasser", "s5", WAT, "marker", ic(I["drop"], 40, WAT, 3), OY, 32))
stage.append(chip_("EINE DER ERSTEN FESTEN SIEDLUNGEN", "s5@Jericho", "s6", PURS, "none", "", OY, 29, 0.3))
stage.append(el(f'<div class="col" style="align-items:center"><div class="mono" style="font-size:30px;font-weight:800;color:{PURS}">VOR ÜBER</div>'
                f'<div class="huge2" style="color:{PURS}">{cnt(10000, "s6@zehntausend", 0, 0)}</div>'
                f'<div class="mono" style="font-size:30px;font-weight:800;color:{PURS};margin-top:2px">JAHREN</div></div>',
                0, 905, A("s6@zehntausend", "s7", -0.15) + ' data-sfx="none"', 1080, CENTER))
stage.append(chip_("SCHON EINE STADT?", "s7@Jericho", "s8@Nein", PURS, "glass", "", OY, 34))
stage.append(chip_("EINIGE HUNDERT BIS WENIGE TAUSEND MENSCHEN", "s8@einige", "s8@großes", GR, "marker", ic(I["crowd"], 40, GR, 3), OY, 26))
stage.append(el(f'<div class="stamp mono" style="font-size:46px;white-space:nowrap;color:#2B2D35;border-color:#2B2D35">EHER EIN DORF</div>', 40, OY - 20, A("s8@großes", "s9"), 1000, CENTER))
crit = "".join(f'<div class="chip mono row crit" data-ci="{k}" style="font-size:26px;gap:10px;padding:10px 16px;border-color:{PURS};color:{PURS};background:rgba(255,255,255,.97);font-weight:700;opacity:0">{ic(I[icn], 36, PURS, 3)}{t}</div>'
               for k, (icn, t) in enumerate([("crowd", "VIELE MENSCHEN"), ("hammer", "HANDWERKER"), ("tablet", "BEAMTE")]))
stage.append(el(f'<div class="col" style="gap:12px"><div class="mono" style="font-size:24px;font-weight:800;color:{GR};background:rgba(255,255,255,.95);padding:4px 12px;border-radius:8px">ZU EINER STADT GEHÖREN:</div><div class="row" style="gap:12px;justify-content:center">{crit}</div></div>',
                40, OY - 52, A("s9@Stadt", "s10@erste", -0.15) + ' data-sfx="none"', 1000, CENTER))
stage.append(chip_("DIE ERSTE ECHTE STADT", "s10@erste", "s11", PURS, "glass", "", OY, 34, 0.1))
stage.append(el(f'<div class="col" style="align-items:center"><div class="mono" style="font-size:30px;font-weight:800;color:{PURS};background:rgba(255,255,255,.9);padding:2px 10px;border-radius:8px">VOR GUT</div>'
                f'<div class="huge2" style="color:{PURS}">{cnt(5000, "s11@fünftausend", 0, 0)}</div>'
                f'<div class="mono" style="font-size:30px;font-weight:800;color:{PURS};margin-top:2px;background:rgba(255,255,255,.9);padding:2px 10px;border-radius:8px">JAHREN</div></div>',
                0, 905, A("s11@fünftausend", "s11@Zehntausende", -0.15) + ' data-sfx="none"', 1080, CENTER))
stage.append(chip_("ZEHNTAUSENDE MENSCHEN", "s11@Zehntausende", "s12", PURS, "none", ic(I["crowd"], 40, PURS, 3), OY, 32))
# Auflösung: Alters-Vergleich (Hauptbühne am Schluss)
SC = 56.0  # px pro 1.000 Jahre
rows = [("rj", "JERICHO", "DORF", 10000, "ÜBER 10.000", GR, "#8A8F99", "s12@Jericho"),
        ("ru", "URUK", "ERSTE STADT", 5000, "ÜBER 5.000", PURS, "#7B3FE4", "s13@Uruk"),
        ("rp", "PYRAMIDEN", "GIZEH", 4500, "ETWA 4.500", "#8A6A12", "#D9B44A", "s14@Pyramiden")]
rh = ""
for rid, n1, n2, v, txt, col, fill, anc in rows:
    rh += (f'<div class="crow" id="{rid}" data-a="{anc}"><div class="clab"><div style="font-family:Unbounded;font-weight:600;font-size:26px;color:{col}">{n1}</div>'
           f'<div class="mono" style="font-size:18px;font-weight:800;color:#8A8F99">{n2}</div></div>'
           f'<div class="ctrack"><div class="cfill" style="width:{v/1000*SC:.0f}px;background:{fill}"></div>'
           f'<div class="cnum mono" style="left:{v/1000*SC+14:.0f}px;color:{col}">{txt}</div></div></div>')
stage.append(el(f'<div class="cmp"><div class="mono" style="font-size:22px;font-weight:800;color:#5D616B;margin:0 0 10px 6px">ALTER IN JAHREN · SCHÄTZUNGEN</div>{rh}'
                f'<div id="pline" style="position:absolute;left:{18+236+4500/1000*SC:.0f}px;top:48px;width:0;height:290px;border-left:3px dashed #8A6A12;opacity:0"></div>'
                f'<div id="okb" class="mono" style="position:absolute;right:20px;top:14px;font-size:20px;font-weight:800;color:{TQD};background:rgba(25,198,180,.14);border:2px solid #19C6B4;border-radius:8px;padding:4px 10px;opacity:0">✓ VOR DEN PYRAMIDEN</div></div>',
                40, 830, A("s12@Jericho", "end", -0.15) + ' data-sfx="none"', 1000))

SCENE_JS = r''' // ---- Bühne: Karte Naher Osten ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const M=document.getElementById('mapg');
  const sm=u=>u*u*(3-2*u);
  function kf(arr,tt,n){ const ks=arr.map(k=>({t:TS(k[0],k[1]),v:k.slice(2)})); if(tt<=ks[0].t) return ks[0].v;
    for(let i=0;i<ks.length-1;i++){ const a=ks[i],b=ks[i+1]; if(tt>=a.t&&tt<b.t){ const e=sm((tt-a.t)/Math.max(1e-6,b.t-a.t)); return a.v.map((x,j)=> (n&&j===n)?Math.exp(Math.log(x)+(Math.log(b.v[j])-Math.log(x))*e):x+(b.v[j]-x)*e); } }
    return ks[ks.length-1].v; }
  const c=kf(PAN.cam,t,2); const cx=c[0], cy=c[1], z=c[2], FX=540, FY=c[3];
  M.setAttribute('transform',`translate(${FX},${FY}) scale(${z}) translate(${-cx},${-cy})`);
  const pj=(x,y)=>[FX+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('.geo')){ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px';
    if(g.dataset.zs){ g.style.transform=`scale(${Math.min(+g.dataset.smax, z/+g.dataset.zs)})`; } }
  const zi=[...document.querySelectorAll('.pz')]; zi.forEach(g=>{ g.style.zIndex=Math.round(+g.style.top.replace('px','')); });
  const op=(id,v)=>{document.getElementById(id).style.opacity=cl(v,0,1);};
  const popAt=(id,t0,t1,dur)=>{ const e=document.getElementById(id); const a=pr(t,t0,dur||0.35), o=t1?pr(t,t1,0.25):0;
    e.style.opacity=Math.min(1,a*2)*(1-o); e.style.transform=`scaleY(${0.2+0.8*(1+2.2*Math.pow(a-1,3)+1.2*Math.pow(a-1,2))})`; };
  // Hook: Pyramiden + Fragezeichen (ab Frame 0 sichtbar)
  popAt('pyr', -1, TS('s3',0)); document.getElementById('pyr').style.transform=`scaleY(1)`;
  op('pyr', (1-pr(t,TS('s3',0),0.3)) + pr(t,TS('s14@Pyramiden',-0.1),0.35));
  const q=document.getElementById('qb'); q.style.opacity=1-pr(t,TS('s3',0),0.3); q.style.transform=`scale(${1+0.08*Math.sin(t*5)}) rotate(${6*Math.sin(t*2.3)}deg)`;
  // Wander-Spur
  const tw0=TS('s3',0), tw1=TS('s4@Quelle',0.2); const tp=pr(t,tw0,tw1-tw0);
  const tr=document.getElementById('trail'); tr.style.strokeDashoffset=1-tp; tr.setAttribute('stroke-width',(5/z).toFixed(4));
  tr.style.opacity=(t>tw0?0.75:0)*(1-pr(t,TS('s4@Toten',0),0.5));
  const hp_=document.getElementById('hop'); hp_.style.strokeDashoffset=1-ease(pr(t,TS('s10@echte',0),TS('s10@Irak',0)-TS('s10@echte',0))); hp_.setAttribute('stroke-width',(6/z).toFixed(4)); hp_.style.opacity=(t>TS('s10@echte',0)?0.8:0)*(1-pr(t,TS('s11',0),0.5));
  const TRL=PAN.tr; const seg=[]; let tot=0; for(let i=1;i<TRL.length;i++){ const d=Math.hypot(TRL[i][0]-TRL[i-1][0],TRL[i][1]-TRL[i-1][1]); seg.push(d); tot+=d; }
  function along(u){ let L=u*tot; for(let i=0;i<seg.length;i++){ if(L<=seg[i]){ const k=L/seg[i]; return [TRL[i][0]+(TRL[i+1][0]-TRL[i][0])*k, TRL[i][1]+(TRL[i+1][1]-TRL[i][1])*k]; } L-=seg[i]; } return TRL[TRL.length-1]; }
  // Dorf
  for(let k=0;k<6;k++) popAt('hut'+k, TS('s5@Jericho',0.35+k*0.12), TS('s10@später',-0.3));
  popAt('spring', TS('s4@Quelle',0.35), TS('s10@später',-0.3));
  popAt('wall', TS('s6@Mauer',0), TS('s10@später',-0.3), 0.45);
  popAt('tower', TS('s6@Turm',-0.45), TS('s10@später',-0.3), 0.5);
  popAt('meas', TS('s6@acht',-0.1), TS('s7@Stadt',0));
  popAt('zig', TS('s10@Irak',0.1), TS('s12',0));
  // Uruk-Stadtfläche + Mauer
  op('e_ur', pr(t,TS('s10@Uruk',0),0.4)*(1-pr(t,TS('s12@Jericho',0),0.5)*0.6));
  const uw=document.getElementById('uwall'); uw.style.strokeDashoffset=1-ease(pr(t,TS('s11@fünftausend',-0.2),1.0)); uw.setAttribute('stroke-width',(7/z).toFixed(4));
  // Menschen (Hauptdarsteller)
  const P=document.querySelectorAll('#pplw .ppl'); const tq=TS('s4@Quelle',0.2);
  const g1in=TS('s3',-0.1), g1out=pr(t,TS('s10@später',-0.4),0.4);
  const g2in=TS('s8@einige',-0.1), g3in=TS('s11@Zehntausende',-0.25), g3out=pr(t,TS('s12@Jericho',0),0.5);
  P.forEach((d,i)=>{ const pp=PAN.ppl[i]; let w, a=0, sc=1;
    if(pp.g===1){ a=pr(t,g1in+i*0.05,0.3)*(1-g1out);
      const u=pr(t,tw0,tw1-tw0); const lead=along(Math.max(0,u-0.02*(i%4))); const wob=Math.sin(t*3+i*1.3)*0.15;
      const off=[pp.o[0]+wob*0.4, pp.o[1]+Math.cos(t*2.6+i)*0.12];
      const v=ease(pr(t,tq,1.0)); w=[lead[0]+off[0]*(1-v)+(pp.v[0]-PAN.J[0])*v, lead[1]+off[1]*(1-v)+(pp.v[1]-PAN.J[1])*v];
      if(u>=1) w=[PAN.J[0]+off[0]*(1-v)+(pp.v[0]-PAN.J[0])*v, PAN.J[1]+off[1]*(1-v)+(pp.v[1]-PAN.J[1])*v]; }
    else if(pp.g===2){ a=pr(t,g2in+(i%16)*0.06,0.25)*(1-g1out); w=pp.v; }
    else { const k=i-24; a=pr(t,g3in+k*0.009,0.2)*(1-g3out*0.85); w=pp.v; sc=0.62; }
    const jig=pp.g<3?Math.sin(t*4+i*2.1)*0.0035*(600/z):0;
    const p=pj(w[0]+jig,w[1]); d.style.left=p[0]+'px'; d.style.top=p[1]+'px'; d.style.opacity=a; d.style.transform=`scale(${sc*(0.6+0.4*ease(Math.min(1,a)))})`; });
  // Kriterien-Chips
  document.querySelectorAll('.crit').forEach((e,i)=>{ const a=pr(t,TS(['s9@viele','s9@Handwerker','s9@Beamte'][i],-0.1),0.25); e.style.opacity=a; e.style.transform=`scale(${0.7+0.3*ease(a)})`; });
  // Vergleich
  for(const r of document.querySelectorAll('.crow')){ const a=pr(t,TS(r.dataset.a,-0.1),0.3); r.style.opacity=a;
    r.querySelector('.cfill').style.transform=`scaleX(${ease(pr(t,TS(r.dataset.a,0),0.9))})`; r.querySelector('.cnum').style.opacity=pr(t,TS(r.dataset.a,0.5),0.3); }
  op('pline', pr(t,TS('s14@viertausendfünfhundert',0.2),0.4)); op('okb', pr(t,TS('s15@vor',-0.1),0.3));
  const ru=document.getElementById('ru'); const hl=pr(t,TS('s15@vor',-0.1),0.3); ru.style.background=`rgba(25,198,180,${0.10*hl})`; ru.style.borderColor=`rgba(25,198,180,${hl})`;
  // Karte abdunkeln zum Vergleich
  document.querySelector('.mapwrap svg').style.opacity=1-0.35*pr(t,TS('s12@Jericho',0.2),0.6);
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
.pop{{position:absolute;left:0;top:0;transform-origin:0 0}}
.pz{{transform-origin:0 0}}
.ppl{{position:absolute;width:20px;height:20px;margin:-10px 0 0 -10px;border-radius:50%;background:#7B3FE4;border:3px solid #fff;box-shadow:0 1px 4px rgba(26,31,51,.35);z-index:3000}}
.ppl.g3{{background:#7B3FE4}}
.cmp{{position:relative;width:1000px;background:rgba(255,255,255,.96);border:1px solid rgba(26,31,51,.12);border-radius:22px;padding:18px 18px 14px;box-shadow:0 10px 26px rgba(26,31,51,.14)}}
.crow{{display:flex;align-items:center;height:96px;border:2px solid transparent;border-radius:14px;margin-bottom:4px}}
.clab{{width:236px;flex:none;padding-left:8px}}
.ctrack{{position:relative;flex:1;height:44px}}
.cfill{{position:absolute;left:0;top:0;height:44px;border-radius:10px;transform-origin:left}}
.cnum{{position:absolute;top:6px;font-size:26px;font-weight:800;white-space:nowrap}}
#pplw{{position:absolute;left:0;top:0}}
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
 const top=cl(1-pr(t,END,.3),0,1); ['chap','prog','head'].forEach(id=>document.getElementById(id).style.opacity=top); document.getElementById('headbg').style.opacity=1-pr(t,S['s3']-0.2,0.5); document.getElementById('head').style.opacity=top*(1-pr(t,S['s3']-0.2,0.3));
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
