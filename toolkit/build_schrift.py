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
HOOK = 'Wie und wo wurde die <span style="color:#7B3FE4">Schrift</span> erfunden?'
B = [
 ("s1", 0, HOOK, "Wie und *wo* wurde die *Schrift* *erfunden?*", "staunt"),
 ("s2", 0, HOOK, "Eine der *ersten* *Schriften* entstand vor rund *5.300* *Jahren* in *Uruk* – im heutigen *Irak.*", None),
 ("s3", 1, "", "Dort verwalteten *Tempel* riesige *Vorräte:* *Gerste,* *Bier* und *Vieh.*", None),
 ("s4", 1, "", "Aber *wer* hat *wie* *viel* *geliefert?*", None),
 ("s5", 2, "", "Zuerst halfen kleine *Zählmarken* aus *Ton.*", None),
 ("s6", 2, "", "Die *Marken* reisten mit der *Ware* mit – *versiegelt* in einer *Tonkugel,* damit keiner *schummelt.*", None),
 ("s7", 2, "", "Damit man trotzdem sah, was *drin* ist, drückte man jede *Marke* vorher *außen* in den weichen *Ton.*", None),
 ("s8", 3, "", "Die *Abdrücke* *allein* *reichen* ja!", None),
 ("s9", 3, "", "Also kamen die *Zeichen* direkt auf eine *Tontafel.*", None),
 ("s10", 3, "", "Die *Abdrücke* zeigten, *wie* *viel.*", None),
 ("s11", 4, "", "Kleine *Bilder* zeigten, *was* – ein *Rinderkopf* für *Rind.*", None),
 ("s12", 4, "", "Mit dem *Schilfgriffel* wurden daraus *keilförmige* *Striche:* die *Keilschrift.*", None),
 ("s13", 5, "", "Die Schrift begann also nicht mit *Geschichten* – sondern mit *Lieferlisten.*", None),
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
    return [round(WX(lon) + (540 - sx) / z, 3), round(WY(lat), 3), z, sy - MAPTOP]
ULAT, ULON = 31.322, 45.636      # Uruk (Warka)
UX, UY = WX(ULON), WY(ULAT)
OV0 = CAMAT(31.4, 40.4, 16.5, 540, 700); OV1 = CAMAT(31.4, 40.9, 18.0, 540, 700)
UZ = CAMAT(ULAT, ULON, 250, 540, 700); UZ2 = CAMAT(ULAT, ULON, 215, 540, 690)
UDEEP = CAMAT(ULAT, ULON, 4000, 540, 700)
cam = [("s1", -0.6, *OV0), ("s2", 0, *OV1), ("s2@Uruk", -0.5, *OV1), ("s2@Uruk", 0.6, *UZ), ("s3", 0, *UZ),
       ("s4", -0.3, *UZ2), ("s5", 0.0, *UZ2), ("s5@Zählmarken", 0.4, *UDEEP)]
# Dörfer rund um Uruk (Weltkoordinaten-Offsets) – Lieferpunkte laufen zum Tempel
import math, random as _r; _r.seed(7)
VIL = [(UX + 2.1 * math.cos(a), UY + 1.6 * math.sin(a)) for a in [0.3, 1.2, 2.0, 2.9, 3.7, 4.6, 5.4]]
PANJS = dict(cam=cam, U=[UX, UY], vil=[[round(x, 3), round(y, 3)] for x, y in VIL])

PURS = "#5B2BB5"; GR = "#3F434C"; TQD = "#0E8C80"; SAND = "#B88A1A"; WAT = "#4BA3D9"
CLAY = "#DCC09A"; CLAYD = "#A97F55"; CLAYL = "#EBD7B8"
land = f'<path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
cty = f'<path d="{GEO["cty"]}" fill="none" stroke="#C3C7CF" stroke-width="1" stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/>'
lakes = f'<path d="{GEO["lakes"]}" fill="#CFE7F6" stroke="{WAT}" stroke-width="1.2" vector-effect="non-scaling-stroke"/>'
rivers = "".join(f'<path d="{d}" fill="none" stroke="{WAT}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" opacity=".85"/>' for d in GEO["rivers"].values())
URX, URY = 0.32 * K * CXF, 0.24 * K
uell = f'M{UX-URX:.3f} {UY:.3f}A{URX:.3f} {URY:.3f} 0 1 0 {UX+URX:.3f} {UY:.3f}A{URX:.3f} {URY:.3f} 0 1 0 {UX-URX:.3f} {UY:.3f}Z'
mapsvg = (f'<svg width="1080" height="{MAPH}" style="position:absolute;left:0;top:0;overflow:hidden"><g id="mapg">{land}{cty}{lakes}{rivers}'
          f'<g id="e_ur" style="opacity:0"><path d="{uell}" fill="rgba(123,63,228,.13)" stroke="{PURS}" stroke-width="3" vector-effect="non-scaling-stroke"/></g>'
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
    return f'<div class="geo pz" data-x="{wx:.4f}" data-y="{wy:.4f}" data-zs="{zs}" data-smax="{smax}"><div id="{gid}" class="pop">{inner}</div></div>'

# ---- eigene schlichte Skizzen ----
zig_svg = ('<svg width="170" height="96" viewBox="0 0 170 96" style="position:absolute;left:-85px;top:-92px;overflow:visible">'
           '<path d="M4 94H166V70H4Z" fill="#E9DFCC" stroke="#2B2D35" stroke-width="2.8"/><path d="M28 70H142V44H28Z" fill="#EFE6D6" stroke="#2B2D35" stroke-width="2.8"/>'
           '<path d="M54 44H116V18H54Z" fill="#F4EDE0" stroke="#2B2D35" stroke-width="2.8"/><path d="M85 94V18" stroke="#2B2D35" stroke-width="2" stroke-dasharray="5 5" opacity=".6"/></svg>')
sack_svg = ('<svg width="90" height="90" viewBox="0 0 90 90" style="position:absolute;left:-45px;top:-88px;overflow:visible">'
            '<path d="M30 14q15 8 30 0l-4 12q22 12 22 38q0 22-33 22T12 64q0-26 22-38z" fill="#F1E3BF" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
            '<path d="M34 26h22" stroke="#2B2D35" stroke-width="3"/>'
            '<g stroke="#B88A1A" stroke-width="3" fill="none" stroke-linecap="round"><path d="M45 74V44"/><path d="M45 52q-8-2-9-9q8 1 9 9zM45 52q8-2 9-9q-8 1-9 9zM45 62q-8-2-9-9q8 1 9 9zM45 62q8-2 9-9q-8 1-9 9z"/></g></svg>')
jar_svg = ('<svg width="80" height="96" viewBox="0 0 80 96" style="position:absolute;left:-40px;top:-94px;overflow:visible">'
           '<path d="M26 8h28M28 8v12C12 30 8 44 8 58c0 18 14 32 32 32s32-14 32-32c0-14-4-28-20-38V8" fill="#E2C49A" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M14 52h52" stroke="#2B2D35" stroke-width="2" opacity=".5"/><path d="M40 20v8" stroke="#2B2D35" stroke-width="2"/>'
           '<path d="M22 66q18 8 36 0" stroke="#B88A1A" stroke-width="3" fill="none"/></svg>')
cow_svg = ('<svg width="130" height="86" viewBox="0 0 130 86" style="position:absolute;left:-65px;top:-84px;overflow:visible">'
           '<path d="M24 30q6-10 22-10h46q14 0 18 10l4 12-8 6v30h-10V56H46v22H36V52q-10-2-12-14z" fill="#FFFFFF" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M24 30l-12 4q-8 4-6 12l6 8q6 4 12-2l6-10" fill="#FFFFFF" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M16 30q-6-10 2-16M28 26q4-10 14-10" stroke="#2B2D35" stroke-width="3" fill="none" stroke-linecap="round"/>'
           '<path d="M60 30q10 6 20 0" stroke="#2B2D35" stroke-width="2" fill="none" opacity=".5"/><circle cx="14" cy="38" r="2" fill="#2B2D35"/></svg>')
tab_svg = ('<svg width="120" height="96" viewBox="0 0 120 96" style="position:absolute;left:-60px;top:-96px;overflow:visible">'
           f'<rect x="6" y="6" width="108" height="84" rx="14" fill="{CLAY}" stroke="#2B2D35" stroke-width="3"/>'
           '<g fill="#2B2D35" opacity=".75"><path d="M22 26l10 4-10 4z"/><path d="M40 26l10 4-10 4z"/><path d="M66 22l8 10-8 3z"/><path d="M84 26l10 4-10 4z"/>'
           '<path d="M22 52l10 4-10 4z"/><path d="M46 50l8 10-8 3z"/><path d="M70 52l10 4-10 4z"/><path d="M88 52l10 4-10 4z"/></g>'
           '<path d="M16 42h88M16 70h88" stroke="#2B2D35" stroke-width="1.6" opacity=".45"/></svg>')
qbadge = ('<div style="position:absolute;left:-40px;top:-40px;width:80px;height:80px;border-radius:50%;background:#7B3FE4;color:#fff;font-family:Unbounded;font-weight:600;'
          'font-size:50px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 6px rgba(123,63,228,.22),0 6px 16px rgba(26,31,51,.25)">?</div>')
geo_ov = (
    popg(UX, UY - 0.10, tab_svg, "htab", 16, 1.7)
    + f'<div class="geo" data-x="{UX + 0.55*K*CXF*0.6:.3f}" data-y="{UY - 0.2*K:.3f}"><div id="qb" style="position:absolute;left:0;top:0">{qbadge}</div></div>'
    + lab(ULAT, ULON, "URUK", "s2@Uruk", "s3@Tempel", PURS, -0.2, True, dx=0, dy=-12, sfx="marker")
    + lab(32.3, 44.0, "HEUTE: IRAK", "s2@Irak", "s3@Gerste", GR, 0, False, sfx="marker")
    + lab(33.6, 41.3, "EUPHRAT", "s2@Uruk", "s3", WAT, 0.3, False, sfx="none")
    + lab(34.4, 44.2, "TIGRIS", "s2@Uruk", "s3", WAT, 0.4, False, sfx="none")
    + popg(UX, UY + 0.05, zig_svg, "zig", 150, 1.7)
    + popg(UX - 1.05, UY + 0.40, sack_svg, "sack", 150, 1.7)
    + popg(UX + 1.05, UY + 0.40, jar_svg, "jar", 150, 1.7)
    + popg(UX, UY + 0.95, cow_svg, "cow", 150, 1.7)
    + lab(0, 0, "TEMPEL", "s3@Tempel", "s4", PURS, 0.1, False, wx=UX, wy=UY - 0.78, dx=-10, dy=0, sfx="marker")
    + f'<div class="geo" data-x="{UX:.3f}" data-y="{UY - 1.0:.3f}"><div id="qb2" style="position:absolute;left:0;top:0;opacity:0">{qbadge}</div></div>'
)
note = el('<div class="note mono">KARTE: NATURAL EARTH · DARSTELLUNG SCHEMATISCH</div>', 18, MAPH - 46, A("s1", "s5", -0.6) + ' data-sfx="none"')
dots = "".join(f'<div class="ppl dlv" style="opacity:0"></div>' for _ in range(len(VIL) * 2))
series = el('<div class="chip mono" style="font-size:24px;padding:8px 14px;background:rgba(255,255,255,.95);border-color:#7B3FE4;color:#5B2BB5;font-weight:800">MENSCHHEITSGESCHICHTE · FOLGE 7</div>', 40, 150, A("s1", "s3", -0.6) + ' data-sfx="none"', style="top:160px")
stage.append(f'<div class="el mapwrap" data-in="s1" data-d="-0.6" data-out="s5@Zählmarken" data-sfx="none" style="left:0;top:{MAPTOP}px;width:1080px;height:{MAPH}px">{mapsvg}{geo_ov}<div id="pplw">{dots}</div>{note}{series}</div>')

# ---- Werkbank (Maßstabswechsel: Zoom in den Tempel) ----
BC = (540, 450); BR = 235
TOK = [(280, 560), (410, 560), (540, 560), (670, 560), (800, 560)]
INS = [(455, 500), (540, 540), (625, 500), (495, 420), (585, 420)]
MRK = [(400, 335), (470, 290), (550, 275), (630, 292), (690, 345)]
TABM = [(305, 355), (380, 355), (455, 355), (305, 445), (380, 445)]
BENCH = dict(BC=BC, BR=BR, tok=TOK, ins=INS, mrk=MRK, tabm=TABM)
PANJS["bench"] = BENCH
def cone(i, hero=False):
    f = "#C9B2FF" if hero else CLAY; s = PURS if hero else "#2B2D35"
    return (f'<g id="tk{i}" class="tok"><g transform="translate(-26,-40)"><path d="M26 4C18 20 6 46 6 58c0 10 9 16 20 16s20-6 20-16C46 46 34 20 26 4z" fill="{f}" stroke="{s}" stroke-width="3.2" stroke-linejoin="round"/>'
            f'<path d="M16 52q10 6 20 0" stroke="{s}" stroke-width="1.6" fill="none" opacity=".5"/></g></g>')
def mark(i, hero=False):
    c = PURS if hero else "#6E4F2E"
    return f'<g id="mk{i}" class="mrk" style="opacity:0"><path d="M0 -15C-6 -6 -11 6 -11 11c0 6 5 8 11 8s11-2 11-8C11 6 6 -6 0 -15z" fill="{c}" opacity=".78"/></g>'
ox_ink = (P("M600 380q60-34 120 0", 4, "#3A2A1C", 'id="ox1"') + P("M612 382q-22-34 -6-58M708 382q22-34 6-58", 4, "#3A2A1C", 'id="ox2"')
          + P("M626 384l8 70q26 26 52 0l8-70", 4, "#3A2A1C", 'id="ox3"') + P("M646 412h4M672 412h4M650 444q10 6 20 0", 4, "#3A2A1C", 'id="ox4"'))
def wedge(x, y, rot, i):
    return (f'<g class="wdg" id="wd{i}" transform="translate({x},{y}) rotate({rot})" style="opacity:0">'
            f'<path d="M-12 -9L12 0L-12 9Z" fill="#3A2A1C"/><path d="M10 0H44" stroke="#3A2A1C" stroke-width="4.5" stroke-linecap="round"/></g>')
WD = [(612, 372, 0), (668, 352, 0), (604, 412, 60), (690, 402, 120), (640, 452, 90)]
wedges = "".join(wedge(x, y, r, i) for i, (x, y, r) in enumerate(WD))
# Listenzeilen (Auflösung)
rows = ""
for k, yy in enumerate([700, 780]):
    ms = "".join(f'<path d="M{300+j*48} {yy-14}C{294+j*48} {yy-6} {289+j*48} {yy+6} {289+j*48} {yy+10}c0 6 5 8 11 8s11-2 11-8C{311+j*48} {yy+6} {306+j*48} {yy-6} {300+j*48} {yy-14}z" fill="#6E4F2E" opacity=".75"/>' for j in range(3 - k))
    ws_ = "".join(f'<g transform="translate({600+j*40},{yy}) rotate({[0,60,120,90][(j+k)%4]})"><path d="M-10 -8L10 0L-10 8Z" fill="#3A2A1C"/><path d="M8 0H34" stroke="#3A2A1C" stroke-width="4" stroke-linecap="round"/></g>' for j in range(3))
    rows += f'<g class="lrow" id="lr{k}" style="opacity:0"><path d="M262 {yy-46}H818" stroke="#6E4F2E" stroke-width="2.4" opacity=".55"/>{ms}{ws_}</g>'
stylus = (f'<g id="sty" style="opacity:0"><g transform="rotate(-38)"><rect x="-9" y="-330" width="18" height="320" rx="8" fill="#CDB074" stroke="#2B2D35" stroke-width="3"/>'
          f'<path d="M-9 -12L0 8L9 -12Z" fill="#B0904E" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/>'
          f'<path d="M-9 -230h18M-9 -120h18" stroke="#2B2D35" stroke-width="2.4" opacity=".6"/></g></g>')
seal = (f'<g id="seal" style="opacity:0"><rect x="-26" y="-60" width="52" height="120" rx="12" fill="#E8E2D6" stroke="#2B2D35" stroke-width="3"/>'
        f'<path d="M-26 -30h52M-26 0h52M-26 30h52" stroke="#2B2D35" stroke-width="1.8" opacity=".55"/></g>')
bench_svg = (f'<svg id="bsvg" width="1080" height="980" viewBox="0 0 1080 980" style="position:absolute;left:0;top:0;overflow:visible">'
             f'<rect id="ball" x="{BC[0]-BR}" y="{BC[1]-BR}" width="{2*BR}" height="{2*BR}" rx="{BR}" fill="{CLAY}" fill-opacity=".45" stroke="#2B2D35" stroke-width="4" style="opacity:0"/>'
             f'<path id="band" d="M{BC[0]-BR+8} {BC[1]+40}Q{BC[0]} {BC[1]+90} {BC[0]+BR-8} {BC[1]+40}" stroke="#8A6A45" stroke-width="22" fill="none" opacity="0" stroke-linecap="round"/>'
             f'<path id="bandp" d="M{BC[0]-BR+8} {BC[1]+40}Q{BC[0]} {BC[1]+90} {BC[0]+BR-8} {BC[1]+40}" stroke="#F3E6CF" stroke-width="3" stroke-dasharray="6 10" fill="none" opacity="0"/>'
             f'<path id="lid" d="M{BC[0]-120} {BC[1]-148}Q{BC[0]} {BC[1]-230} {BC[0]+120} {BC[1]-148}Z" fill="{CLAYL}" stroke="#2B2D35" stroke-width="4" stroke-linejoin="round" style="opacity:0"/>'
             f'<g transform="translate(660,400) scale(1.6) translate(-660,-400)"><g id="ox" style="opacity:0">{ox_ink}</g>{wedges}</g>{rows}'
             + "".join(mark(i, i == 2) for i in range(5))
             + "".join(cone(i, i == 2) for i in range(6))
             + f'{seal}{stylus}</svg>')
stage.append(f'<div class="el mm" id="bench" data-in="s5@Zählmarken" data-d="-0.1" data-out="end" data-sfx="none" style="left:0;top:{MAPTOP}px;width:1080px;height:{MAPH}px;border-radius:0;transform-origin:540px 400px">{bench_svg}'
             + '<div id="bnote" class="note mono" style="position:absolute;left:18px;top:934px">DARSTELLUNG SCHEMATISCH · ZÄHLMARKEN UND ZEICHEN VEREINFACHT</div></div>')

# ---- große Zahl / Wortmarke (Hauptfigur) ----
stage.append(el(f'<div class="col" style="align-items:center"><div class="huge2" style="color:{PURS};font-size:170px">{cnt(5300, "s2@5300", 0, 0)}</div>'
                f'<div class="mono" style="font-size:32px;font-weight:800;color:{PURS};margin-top:2px;background:rgba(255,255,255,.9);padding:2px 12px;border-radius:8px">JAHRE ALT</div></div>',
                0, 905, A("s2@5300", "s3", -0.15) + ' data-sfx="none"', 1080, CENTER))
stage.append(el(f'<div id="bigq" class="row" style="gap:26px;align-items:baseline"><span class="huge2" style="color:{PURS};font-size:170px">{cnt(5, "s10@wie", 0, 0)}</span>'
                f'<span id="bx" class="huge2" style="font-size:120px;color:#3A2A1C;opacity:0">× RIND</span></div>',
                0, 330, A("s10@Abdrücke", "s12@Schilfgriffel", -0.1) + ' data-sfx="none"', 1080, CENTER))
stage.append(el(f'<div class="huge2" style="font-size:96px;color:{PURS};letter-spacing:-3px">KEILSCHRIFT</div>',
                0, 380, A("s12@Keilschrift", "s13@Geschichten", -0.1) + ' data-sfx="glass"', 1080, CENTER))

# ---- Overlays (max. eins gleichzeitig) ----
OY = 1150
def chip_(txt, i, o, col=PURS, sfx="marker", icon="", y=OY, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 20px;border-color:{col};color:{col};background:rgba(255,255,255,.97);font-weight:700">{icon}{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
stage.append(chip_("ZÄHLMARKEN AUS TON", "s5@Zählmarken", "s6@versiegelt", PURS, "marker", "", OY, 32, 0.4))
stage.append(el(f'<div class="stamp mono" style="font-size:46px;white-space:nowrap;color:#2B2D35;border-color:#2B2D35">VERSIEGELT</div>', 40, OY - 20, A("s6@schummelt", "s7@drin", -0.1), 1000, CENTER))
stage.append(chip_("ABDRÜCKE AUSSEN = INHALT", "s7@Marke", "s8@reichen", "#6E4F2E", "marker", "", OY, 30, 0.1))
stage.append(chip_("DIE KUGEL BRAUCHT KEINER MEHR", "s8@reichen", "s9@Tontafel", PURS, "glass", "", OY, 30, 0.1))
stage.append(chip_("TONTAFEL", "s9@Tontafel", "s10@Abdrücke", "#6E4F2E", "marker", "", OY, 32, 0.1))
stage.append(chip_("✕ KEINE GESCHICHTEN", "s13@Geschichten", "s13@Lieferlisten", RED, "fail", "", 1190, 32, -0.1))
stage.append(el(f'<div class="stamp mono" style="font-size:52px;white-space:nowrap;color:{PURS};border-color:{PURS}">LIEFERLISTE</div>', 40, 1180, A("s13@Lieferlisten", "end", 0), 1000, CENTER))
# Ton-Akzente (unsichtbare Marker für sfx.py)
def sx(anchor, d, kind): return el("", 540, 600, A(anchor, "end", d) + f' data-sfx="{kind}"')
for k in range(5): stage.append(sx("s5@Zählmarken", 0.12 + k * 0.1, "plop"))

SCENE_JS = r''' // ---- Bühne: Karte -> Tempel -> Werkbank ----
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
  document.querySelectorAll('.pz').forEach(g=>{ g.style.zIndex=Math.round(+g.style.top.replace('px','')); });
  const op=(id,v)=>{document.getElementById(id).style.opacity=cl(v,0,1);};
  const popAt=(id,t0,t1,dur)=>{ const e=document.getElementById(id); const a=pr(t,t0,dur||0.35), o=t1?pr(t,t1,0.25):0;
    e.style.opacity=Math.min(1,a*2)*(1-o); e.style.transform=`scaleY(${0.2+0.8*(1+2.2*Math.pow(a-1,3)+1.2*Math.pow(a-1,2))})`; };
  // Hook: Tontafel + Fragezeichen bei Uruk (ab Frame 0)
  { const e=document.getElementById('htab'); const o=pr(t,TS('s2@Uruk',-0.3),0.3); e.style.opacity=1-o; e.style.transform=`rotate(${4*Math.sin(t*2.2)}deg) scale(${1+0.04*Math.sin(t*3.1)})`; }
  const q=document.getElementById('qb'); q.style.opacity=1-pr(t,TS('s2@Uruk',-0.3),0.3); q.style.transform=`scale(${1+0.1*Math.sin(t*5)}) rotate(${8*Math.sin(t*2.3)}deg)`;
  op('e_ur', pr(t,TS('s2@Uruk',0.2),0.4)*(1-pr(t,TS('s5@Zählmarken',0),0.3)));
  popAt('zig', TS('s3@Tempel',-0.1), TS('s5@Zählmarken',0.2), 0.45);
  popAt('sack', TS('s3@Gerste',-0.05), TS('s5',0)); popAt('jar', TS('s3@Bier',-0.05), TS('s5',0)); popAt('cow', TS('s3@Vieh',-0.05), TS('s5',0));
  // Lieferungen: Punkte laufen von Dörfern zum Tempel
  const D=document.querySelectorAll('.dlv'); const d0=TS('s3@Vieh',0.3), d1=TS('s5@Zählmarken',0);
  D.forEach((d,i)=>{ const v=PAN.vil[i%PAN.vil.length]; const ph=((t-d0)*0.55+(i>=PAN.vil.length?0.5:0)+i*0.13)%1; const u=sm(Math.max(0,ph));
    const w=[v[0]+(PAN.U[0]-v[0])*u, v[1]+(PAN.U[1]-v[1])*u]; const p=pj(w[0],w[1]);
    d.style.left=p[0]+'px'; d.style.top=p[1]+'px'; d.style.opacity=(t>d0&&t<d1)?Math.min(1,(t-d0)*3)*(1-pr(t,d1-0.4,0.4))*(ph<0.9?1:(1-ph)*10):0; });
  { const e=document.getElementById('qb2'); const a=pr(t,TS('s4@wer',-0.1),0.3); e.style.opacity=a*(1-pr(t,TS('s5',0),0.3)); e.style.transform=`scale(${0.6+0.4*ease(a)+0.06*Math.sin(t*6)})`; }
  // Maßstabswechsel in die Werkbank
  { const bn=document.getElementById('bench'); const a=ease(pr(t,TS('s5@Zählmarken',-0.15),0.55)); bn.style.transform=`scale(${0.08+0.92*a})`; bn.style.opacity=t<TS('s5@Zählmarken',-0.15)?0:Math.min(1,a*1.6)*(1-pr(t,S['end'],0.2)); }
  const BC=PAN.bench.BC, BR=PAN.bench.BR;
  const SET=(id,x,y,s,r,o)=>{ const e=document.getElementById(id); e.setAttribute('transform',`translate(${x},${y}) rotate(${r||0}) scale(${s})`); e.style.opacity=o; };
  const lerp=(a,b,u)=>a+(b-a)*u;
  // Kugel
  const tBall=TS('s6@Marken',-0.1), tIn=TS('s6@versiegelt',-0.35), tLid=TS('s6@Tonkugel',0), tSeal=TS('s6@damit',0);
  const tPress=TS('s7@drückte',0), tPressE=TS('s7@Ton',0.1), tGone=TS('s8@allein',0), tMorph=TS('s9@Zeichen',0), tMorphE=TS('s9@Tontafel',0.2);
  const ball=document.getElementById('ball'); const ba=pr(t,tBall,0.35);
  const mu=ease(pr(t,tMorph,tMorphE-tMorph));
  const g13=ease(pr(t,TS('s13',0),0.6)); const bw=lerp(2*BR,620,mu), h0=lerp(2*BR,380,mu), bh=h0+200*g13, brx=lerp(BR,34,mu), bx=lerp(BC[0],540,mu), by0=lerp(BC[1],470,mu);
  ball.setAttribute('x',bx-bw/2); ball.setAttribute('y',by0-h0/2); ball.setAttribute('width',bw); ball.setAttribute('height',bh); ball.setAttribute('rx',brx);
  ball.style.opacity=ba; ball.setAttribute('fill-opacity',(0.42+0.58*Math.max(pr(t,tLid,0.4)*0, pr(t,tGone,0.5), mu)).toFixed(3));
  ball.style.transform=`scale(${1+0.04*Math.sin(t*4)*(1-mu)})`; ball.style.transformOrigin='540px 450px';
  // Deckel schließt sich, Siegel rollt
  { const e=document.getElementById('lid'); const a=pr(t,tLid-0.1,0.35); e.style.opacity=a*(1-pr(t,tMorph,0.3)); e.setAttribute('transform',`translate(0,${-60*(1-ease(a))})`); }
  { const a=pr(t,tSeal,0.9); op('band', (t>tSeal?0.55:0)*(1-pr(t,tMorph,0.3))); document.getElementById('band').style.strokeDasharray='1'; document.getElementById('band').setAttribute('pathLength','1'); document.getElementById('band').style.strokeDashoffset=1-a;
    op('bandp', (t>tSeal+0.2?0.9:0)*(1-pr(t,tMorph,0.3)));
    const s=document.getElementById('seal'); const sxx=lerp(BC[0]-BR+10,BC[0]+BR-10,ease(a)); const syy=BC[1]+40+50*(1-Math.pow(2*ease(a)-1,2));
    s.setAttribute('transform',`translate(${sxx},${syy-70}) rotate(${-90+360*a*0.3})`); s.style.opacity=(t>tSeal-0.15&&t<tSeal+1.1)?Math.min(1,(t-tSeal+0.15)*5)*(1-pr(t,tSeal+0.9,0.2)):0; }
  // Zählmarken (Hauptdarsteller = lila Marke)
  for(let i=0;i<5;i++){ const tk=PAN.bench.tok[i], ins=PAN.bench.ins[i]; const a=pr(t,TS('s5@Zählmarken',0.1+i*0.1),0.3);
    const wig=Math.sin(t*5+i)*3*(t<tIn?1:0); const fly=ease(pr(t,tIn+i*0.08,0.6));
    let x=lerp(tk[0],ins[0],fly), y=lerp(tk[1],ins[1],fly)-Math.sin(fly*Math.PI)*140+wig, s=(0.7+0.3*(1+2.2*Math.pow(a-1,3)+1.2*Math.pow(a-1,2)))*lerp(2.1,1.1,fly);
    const o=Math.min(1,a*2)*(1-0.55*pr(t,tLid,0.4))*(1-pr(t,tGone,0.5));
    SET('tk'+i,x,y,s,wig*2,o); }
  // Abdrücke außen (eine Marke drückt nach der anderen)
  const np=(tPressE-tPress)/5;
  for(let i=0;i<5;i++){ const m=PAN.bench.mrk[i], tm=PAN.bench.tabm[i]; const tp=tPress+i*np; const a=pr(t,tp+np*0.55,0.12);
    const u=ease(pr(t,tMorph,tMorphE-tMorph)); const x=lerp(m[0],tm[0],u), y=lerp(m[1],tm[1],u);
    const glow=pr(t,tGone,0.3)*(1-pr(t,tMorph,0.3)) + (t>TS('s10@wie',0)+i*0.16 && t<TS('s11@Bilder',0)?1:0);
    SET('mk'+i,x,y,lerp(1.25,1.7,u)+0.25*glow*(0.5+0.5*Math.sin(t*8)),0,a); }
  // Presse-Marke: eine Zählmarke nach der anderen wird außen in den Ton gedrückt
  { let x=840,y=640,o=0,r=0; const k=Math.floor((t-tPress)/np);
    if(t>=tPress-0.3&&t<tPressE+0.4){ o=Math.min(1,(t-tPress+0.3)*4)*(1-pr(t,tPressE+0.1,0.3));
      if(k>=0&&k<5){ const m=PAN.bench.mrk[k]; const ph=((t-tPress)%np)/np; const prev=k>0?PAN.bench.mrk[k-1]:[840,640];
        const mv=ease(Math.min(1,ph/0.45)); x=lerp(prev[0],m[0],mv); y=lerp(prev[1],m[1],mv)-40-40*Math.sin(Math.min(1,ph/0.45)*Math.PI)+(ph>0.5&&ph<0.75?20:0); r=180; }
      else if(k>=5){ x=PAN.bench.mrk[4][0]; y=PAN.bench.mrk[4][1]-40; r=180; } }
    SET('tk5',x,y,1.25,r,o); }
  // Rinderkopf als Bild, dann Keile mit Schilfgriffel
  { const tox=TS('s11@Rinderkopf',-0.15); const ox=document.getElementById('ox'); ox.style.opacity=(t>tox?1:0)*(1-pr(t,TS('s12@keilförmige',0.3),0.5));
    ['ox1','ox2','ox3','ox4'].forEach((id,k)=>{ document.getElementById(id).style.strokeDashoffset=1-ease(pr(t,tox+k*0.18,0.4)); }); }
  { const ts0=TS('s12@Schilfgriffel',-0.2), tw=TS('s12@keilförmige',-0.1), twe=TS('s12@Keilschrift',0.1); const e=document.getElementById('sty');
    const WD=[[612,372],[668,352],[604,412],[690,402],[640,452]].map(p=>[660+(p[0]-660)*1.6,400+(p[1]-400)*1.6]); const nw=WD.length; const per=(twe-tw)/nw;
    let x=900, y=260; const ain=ease(pr(t,ts0,0.4)); let k=Math.floor((t-tw)/per);
    if(t<tw){ x=lerp(1150,760,ain); y=lerp(120,330,ain); }
    else if(k<nw){ const p=WD[k], ph=((t-tw)%per)/per; const prev=k>0?WD[k-1]:[760,330]; const mv=ease(Math.min(1,ph/0.45)); x=lerp(prev[0],p[0],mv)-20; y=lerp(prev[1],p[1],mv)-16-22*Math.sin(Math.min(1,ph/0.45)*Math.PI)+(ph>0.55&&ph<0.8?6:0); }
    else { const u=ease(pr(t,twe,0.5)); x=lerp(WD[nw-1][0]-20,1150,u); y=lerp(WD[nw-1][1]-16,140,u); }
    e.setAttribute('transform',`translate(${x},${y})`); e.style.opacity=(t>ts0&&t<twe+0.6)?1:0;
    for(let i=0;i<nw;i++){ const a=pr(t,tw+i*per+per*0.6,0.12); const w=document.getElementById('wd'+i); w.style.opacity=a; } }
  // Liste
  ['lr0','lr1'].forEach((id,k)=>op(id, pr(t,TS('s13',0.5+k*0.35),0.3)));
  // Zahl -> "× RIND"
  op('bx', pr(t,TS('s11@Rind',-0.1),0.3));
 }
'''
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
.ppl.g3{{background:#7B3FE4}} .ppl.dlv{{width:24px;height:24px;margin:-12px 0 0 -12px;background:#B88A1A}}
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
 let rop=0; if(pose&&!end){{const prevHad=BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose; rop=(prevHad||BEATS.indexOf(b)===0)?1:ease(pr(t,b.s,.3)); const nb=BEATS[BEATS.indexOf(b)+1]; if(nb&&!nb.pose) rop*=1-pr(t,nb.s-0.2,.2); if(!nb) rop*=1-pr(t,END-0.2,.2);}}
 if(end){{rop=ease(pr(t,END+0.3,.35));}}
 R.style.opacity=rop; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');
 let prevPose=null; const bi=BEATS.indexOf(b); if(bi>0) prevPose=BEATS[bi-1].pose; const pf=BEATS.indexOf(b)===0?1:pr(t,b.s,.15);
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
html = html.replace('/*SCENEJS*/', SCENE_JS)
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))

