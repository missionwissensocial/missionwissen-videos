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
CH = ["01 DIE FRAGE", "02 843", "03 FLICKENTEPPICH", "04 1871", "05 1949–1990", "06 HEUTE"]
B = [
 ("p1", 0, "Wie alt ist Deutschland?", "Wie *alt* ist *eigentlich* *Deutschland?*", None),
 ("p2", 0, "Viel jünger, als du denkst!", "Viel *jünger,* als du *denkst!*", None),
 ("p3", 1, "Das Frankenreich", "Lange gab es nur das *Frankenreich* von *Karl* dem *Großen.*", None),
 ("p4", 1, "843: geteilt in drei", "*Achthundertdreiundvierzig* teilten seine *Enkel* es in *drei* *Teile.*", None),
 ("p5", 1, "Der Osten: die Keimzelle", "Der *östliche* *Teil* gilt als *Keimzelle* von *Deutschland.*", None),
 ("p6", 2, "Das Heilige Römische Reich", "Daraus *wuchs* das *Heilige* *Römische* *Reich.*", None),
 ("p7", 2, "Ein Flickenteppich", "Aber das war *kein* *richtiger* *Staat,* sondern ein *Flickenteppich* aus rund *dreihundert* *Ländchen,* mit *eigenen* *Herrschern* und *eigenen* *Grenzen.*", None),
 ("p8", 2, "1806: das Ende", "*Achtzehnhundertsechs* *zerfiel* dieses *Reich.*", None),
 ("p9", 3, "1871: das Kaiserreich", "Erst *achtzehnhunderteinundsiebzig* entstand der *erste* *deutsche* *Nationalstaat:* das *Deutsche* *Kaiserreich.*", None),
 ("p10", 4, "1949: zwei deutsche Staaten", "Nach dem *Zweiten* *Weltkrieg* entstanden *neunzehnhundertneunundvierzig* *zwei* *deutsche* *Staaten:* die *Bundesrepublik* und die *DDR.*", None),
 ("p11", 4, "1990: wieder vereint", "Erst *neunzehnhundertneunzig* *wuchsen* sie *wieder* *zusammen.*", None),
 ("p12", 5, "Erst 36 Jahre alt!", "Das *Deutschland* von *heute* gibt es also erst seit *sechsunddreißig* *Jahren.*", None),
 ("p13", 5, "Hättest du's gedacht?", "Hättest du *gedacht,* dass *Deutschland* so *jung* ist?", None),
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
def CAM(lat, lon, z, fy=280): return [round(WX(lon), 1), round(WY(lat), 1), z, fy]
HOOK = CAM(51.2, 10.4, 18, 270); DEU = CAM(51.2, 10.6, 17.5, 270); FRANK = CAM(47.6, 6.8, 11.2, 285)
HRRV = CAM(50.2, 10.9, 15.0, 280); KRV = CAM(51.6, 14.2, 15.5, 285); END_ = CAM(51.2, 10.4, 16.5, 270)
cam = [("p1", 0, *HOOK), ("p2", 0, *HOOK), ("p3", 0.0, *FRANK), ("p5", 0, *FRANK), ("p6", 0.0, *HRRV), ("p8", 0.2, *HRRV), ("p9", -0.1, *KRV),
       ("p10", -0.1, *KRV), ("p10@entstanden", 0, *DEU), ("p12", 0, *DEU), ("p13", 0, *END_)]
GROW = dict(hrr=dict(c=[[WX(10.5), WY(50.5)]], a="p6@wuchs", o=-0.15, d=1.5, r=520),
            kr=dict(c=[[WX(13.4), WY(52.5)]], a="p9@achtzehnhunderteinundsiebzig", o=-0.1, d=1.8, r=520))
PANJS = dict(cam=cam, grow=GROW,
             years=[("p1", ""), ("p3", "UM 800"), ("p4", "843"), ("p7", "UM 1789"), ("p8", "1806"), ("p9", "1871"), ("p10", "1949"), ("p11", "1990"), ("p12", "2026")],
             tl=[["p4", 0.0], ["p8", 0.2], ["p9", 0.4], ["p10", 0.6], ["p11", 0.8], ["p12", 1.0]],
             cells=[[c["x"], c["y"]] for c in GEO["cells"]])
PUR2 = "rgba(123,63,228,.42)"; PURS = "#5B2BB5"
land = f'<path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
def P_(d, fill, stroke, sw=1.8, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" vector-effect="non-scaling-stroke" {extra}/>'
def grp(lid, inner, clip=None):
    c = f' clip-path="url(#{clip})"' if clip else ""
    return f'<g id="e_{lid}" style="opacity:0"><g{c}>{inner}</g></g>'
defs = (f'<defs><clipPath id="win"><rect x="-99999" y="-99999" width="199999" height="199999"/></clipPath>'
        f'<clipPath id="landc"><path d="{GEO["land"]}"/></clipPath><clipPath id="hrrc"><path d="{GEO["hrr"]}"/></clipPath>'
        f'<clipPath id="ws"><path d="{GEO["wside"]}"/></clipPath><clipPath id="es"><path d="{GEO["eside"]}"/></clipPath>'
        + "".join(f'<clipPath id="gc_{k}">' + "".join(f'<circle class="gcc" data-k="{k}" cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="0"/>' for c in v["c"]) + '</clipPath>' for k, v in GROW.items())
        + '</defs>')
PATCH = ["#B79BFF", "#8FE3D9", "#D9C9FF", "#C9CCD3", "#F2D28B", "#A9C6E8", "#E7B8C9", "#BFE6B0"]
import random as _r; _r.seed(3)
cells = "".join(f'<path class="cell" d="{c["d"]}" fill="{PATCH[_r.randrange(len(PATCH))]}" stroke="#FFFFFF" stroke-width="1.4" vector-effect="non-scaling-stroke" style="opacity:0"/>' for c in GEO["cells"])
mapsvg = (f'<svg width="920" height="560" style="position:absolute;left:0;top:0;overflow:hidden">{defs}<g id="mapg">{land}'
          f'<g clip-path="url(#landc)">'
          + f'<g id="e_west" style="opacity:0">{P_(GEO["west"], PUR2, PURS, 1.6, 'id="f_west"')}</g>'
          + f'<g id="e_mid" style="opacity:0">{P_(GEO["mid"], PUR2, PURS, 1.6, 'id="f_mid"')}</g>'
          + f'<g id="e_east" style="opacity:0">{P_(GEO["east"], PUR2, PURS, 1.6, 'id="f_east"')}</g>'
          + grp("hrr", P_(GEO["hrr"], "rgba(123,63,228,.30)", PURS, 2.2), "gc_hrr")
          + f'<g id="e_cells" style="opacity:0"><g clip-path="url(#hrrc)">{cells}</g></g>'
          + grp("kr", P_(GEO["kr"], "rgba(123,63,228,.45)", PURS, 2.2), "gc_kr")
          + grp("brd", P_(GEO["de"], "rgba(123,63,228,.45)", PURS, 2.2), "ws")
          + grp("ddr", P_(GEO["de"], "rgba(25,198,180,.45)", "#0E8C80", 2.2), "es")
          + grp("de", P_(GEO["de"], "rgba(123,63,228,.55)", PURS, 2.4))
          + '</g>'
          + f'<path id="b843" d="M{WX(3.3):.1f} {WY(51.4):.1f}L{WX(4.5):.1f} {WY(50.5):.1f}L{WX(4.8):.1f} {WY(49.5):.1f}L{WX(5):.1f} {WY(48):.1f}L{WX(4.8):.1f} {WY(46.5):.1f}L{WX(4.8):.1f} {WY(45):.1f}L{WX(4.6):.1f} {WY(43.5):.1f}'
            f'M{WX(7.2):.1f} {WY(54.0):.1f}L{WX(7.0):.1f} {WY(52):.1f}L{WX(7.6):.1f} {WY(50.5):.1f}L{WX(8.2):.1f} {WY(49.5):.1f}L{WX(8.0):.1f} {WY(48):.1f}L{WX(9.5):.1f} {WY(47.3):.1f}L{WX(10.5):.1f} {WY(46.8):.1f}L{WX(13.7):.1f} {WY(46.5):.1f}" '
            f'fill="none" stroke="#2B2D35" stroke-width="0.2" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
          + f'<path id="bdr" d="{GEO["border"]}" fill="none" stroke="#2B2D35" stroke-width="0.2" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
          + '</g></svg>')
def lab(lat, lon, text, i, o, col=PUR, d=0, pin=True, lid=""):
    p = f'<span class="pin" style="background:{col}"></span>' if pin else ""
    idd = f' id="{lid}"' if lid else ""
    return (f'<div class="geo" data-x="{WX(lon):.1f}" data-y="{WY(lat):.1f}" style="position:absolute;left:0;top:0">'
            f'<div class="el mk"{idd} {A(i, o, d)} style="left:{-11 if pin else -70}px;top:-14px;gap:8px">{p}'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
GR = "#3F434C"; TQD = "#0E8C80"; BLU = "#3A6EA5"
ov = (lab(48.3, 2.0, "FRANKENREICH", "p3@Frankenreich", "p4@drei", PURS, 0.1, False)
      + lab(47.3, -0.5, "WESTFRANKEN", "p4@drei", "p6", BLU, 0.1, False)
      + lab(44.6, 9.6, "MITTELREICH", "p4@drei", "p6", GR, 0.25, False)
      + lab(50.6, 11.2, "OSTFRANKEN", "p4@drei", "p6", PURS, 0.4, False, "lab_ost")
      + lab(53.9, 9.6, "HEILIGES RÖMISCHES REICH", "p6@Heilige", "p8@zerfiel", PURS, 0, False)
      + lab(52.5, 13.4, "BERLIN", "p9@entstand", "p10", PURS, 0.3)
      + lab(54.2, 16.0, "DEUTSCHES KAISERREICH", "p9@Kaiserreich", "p10", PURS, 0, False)
      + lab(50.2, 8.4, "BUNDESREPUBLIK", "p10@Bundesrepublik", "p11@zusammen", PURS, 0, False)
      + lab(52.0, 13.2, "DDR", "p10@DDR", "p11@zusammen", TQD, 0, False))
STN = [("843", 0), ("1806", .2), ("1871", .4), ("1949", .6), ("1990", .8), ("HEUTE", 1)]
ticks = "".join(f'<div class="mono" style="position:absolute;left:{36 + f * 848 - 45}px;top:44px;width:90px;text-align:center;font-size:20px;font-weight:700;color:#5D616B">{y}</div>'
                f'<div style="position:absolute;left:{36 + f * 848 - 1}px;top:24px;width:2px;height:16px;background:#8A8F99"></div>' for y, f in STN)
tline = (f'<div style="position:absolute;left:0;top:0;width:920px;height:84px">'
         f'<div style="position:absolute;left:36px;top:28px;width:848px;height:8px;border-radius:4px;background:#E6E7EB"></div>'
         f'<div id="tfill" style="position:absolute;left:36px;top:28px;width:848px;height:8px;border-radius:4px;background:{PUR};transform-origin:left;transform:scaleX(0)"></div>'
         f'{ticks}<div id="tdot" style="position:absolute;left:36px;top:32px;opacity:0"><div class="tipdot"></div></div></div>')
def stat(inner, anchor, out, x, w=840):
    return (f'<div class="el" {A(anchor, out, 0)} data-sfx="glass" style="left:{x}px;top:96px;width:{w}px">{inner}</div>')
I.update(crown='<path d="M8 36l-2-22 10 9 8-13 8 13 10-9-2 22z"/><path d="M8 41h32"/>', castle='<path d="M8 42V20h6v6h6v-6h8v6h6v-6h6v22z"/><path d="M20 42v-8h8v8"/>')
bottom = (f'<div style="position:absolute;left:0;top:560px;width:920px;height:200px;background:rgba(255,255,255,.93);border-top:1px solid rgba(26,31,51,.12);padding:16px 0">'
          f'<div style="position:relative;width:920px;height:170px">{tline}'
          + stat(f'<div class="row" style="gap:18px;justify-content:center">{ic(I["castle"], 54, PURS, 3.2)}<div class="mono" style="font-size:44px;font-weight:800;color:{PURS}">≈ {cnt(300, "p7@dreihundert", 0, 0.05)} LÄNDCHEN</div>'
                 f'<div class="mono" style="font-size:19px;color:#5D616B;margin-left:6px">UM 1789</div></div>', "p7@dreihundert", "p8@zerfiel", 40)
          + stat(f'<div class="row" style="gap:18px;justify-content:center"><div class="mono" style="font-size:44px;font-weight:800;color:{PURS}">SEIT 3. OKTOBER 1990</div></div>', "p12@sechsunddreißig", "end", 40)
          + '</div></div>')
chips = (el('<div class="chip mono" style="font-size:19px;padding:8px 12px;background:rgba(255,255,255,.95)">MENSCHHEITSGESCHICHTE · FOLGE 6</div>', 18, 18, A("p1", "p3", -0.6) + ' data-sfx="none"')
         + f'<div class="el" {A("p3", "p13", 0)} data-sfx="none" style="right:18px;top:18px"><div class="chip mono" style="font-size:24px;padding:8px 14px;background:rgba(255,255,255,.95)"><span id="yr">UM 800</span></div></div>'
         + el('<div class="chip mono" style="font-size:16px;padding:5px 9px;color:#8A8F99;border-color:#C9CCD3;background:rgba(255,255,255,.9)">KARTE SCHEMATISCH · GRENZEN VEREINFACHT</div>', 18, 522, A("p3", "end", 0.3) + ' data-sfx="none"'))
stage.append(mm(mapsvg + ov + bottom + chips, 80, 460, 920, 760, A("p1", "end", -0.6)))

# ---- Overlays (Bildschirm) ----
def chip_(txt, i, o, col=PURS, sfx="marker", icon="", y=948, fs=28):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 20px;border-color:{col};color:{col};background:rgba(255,255,255,.96)">{icon}{txt}</div>', 80, y, A(i, o, 0) + f' data-sfx="{sfx}"', 920, CENTER)
stage.append(el(f'<div class="qbig" style="position:relative;font-size:240px;line-height:1">?</div>', 742, 560, A("p1", "p3", -0.6) + ' data-sfx="none"'))
stage.append(chip_("ALTER: ??? JAHRE", "p1", "p2@jünger", PURS, "none", y=948, fs=32).replace('data-in="p1"', 'data-in="p1" data-d="-0.6"'))
stage.append(el(f'<div class="stamp mono" style="font-size:40px;white-space:nowrap;color:{PURS};border-color:{PURS}">JÜNGER, ALS DU DENKST!</div>', 80, 920, A("p2@jünger", "p3"), 920, CENTER))
stage.append(chip_("KARL DER GROSSE · UM 800", "p3@Karl", "p4", PURS, "marker", ic(I["crown"], 38, PURS, 3)))
stage.append(chip_("VERTRAG VON VERDUN · 843", "p4@Enkel", "p5", GR, "marker", ic(I["doc"], 38, GR, 3)))
stage.append(chip_("KEIMZELLE VON DEUTSCHLAND", "p5@Keimzelle", "p6", PURS, "glass"))
stage.append(chip_("KEIN RICHTIGER STAAT", "p7@kein", "p7@Herrschern", "#B8383C", "marker"))
stage.append(el(f'<div class="row" style="gap:18px;justify-content:center"><div class="chip mono" style="font-size:28px;border-color:{PURS};color:{PURS};background:rgba(255,255,255,.96)">EIGENE HERRSCHER</div></div>', 80, 948, A("p7@Herrschern", "p8", 0) + ' data-sfx="plop"', 450, "display:flex;justify-content:flex-end"))
stage.append(el(f'<div class="row" style="gap:18px"><div class="chip mono" style="font-size:28px;border-color:{PURS};color:{PURS};background:rgba(255,255,255,.96)">EIGENE GRENZEN</div></div>', 550, 948, A("p7@Grenzen", "p8", 0) + ' data-sfx="plop"', 450))
stage.append(el(f'<div class="stamp mono" style="font-size:40px;white-space:nowrap;color:#2B2D35;border-color:#2B2D35">1806 · DAS REICH ZERFÄLLT</div>', 80, 920, A("p8@zerfiel", "p9"), 920, CENTER))
stage.append(chip_("ERSTER DEUTSCHER NATIONALSTAAT", "p9@Nationalstaat", "p10", PURS, "glass", ic(I["crown"], 38, PURS, 3)))
stage.append(chip_("1949 · ZWEI DEUTSCHE STAATEN", "p10@zwei", "p11", GR, "marker"))
stage.append(chip_("3. OKTOBER 1990 · WIEDERVEREINIGUNG", "p11@zusammen", "p12", TQD, "success", "", 948, 27).replace('border-color:#0E8C80', 'border-color:#19C6B4'))
stage.append(el(f'<div class="col" style="align-items:center"><div class="qbig" style="position:relative;font-size:170px;line-height:1;letter-spacing:-8px">{cnt(36, "p12@sechsunddreißig", 0, 0.05)}</div><div class="mono" style="font-size:34px;font-weight:800;color:{PURS};margin-top:-6px">JAHRE</div></div>', 740, 600, A("p12@sechsunddreißig", "p13", -0.1) + ' data-sfx="none"', 260))
stage.append(card(f'<div class="col" style="gap:18px;height:100%;justify-content:center"><div class="mono small grey">HÄTTEST DU GEDACHT, DASS DEUTSCHLAND SO JUNG IST?</div>'
                  f'<div class="row" style="gap:20px"><div class="chip tq mono" style="font-size:34px">JA</div><div class="chip mono" style="font-size:34px;border-color:#8A8F99">NEIN</div></div></div>',
                  130, 620, 820, 220, "activeTQ", A("p13@gedacht", "end")))
stage.append(el('<div class="chip pu mono" style="font-size:22px;background:rgba(255,255,255,.95)">SCHREIB\'S IN DIE KOMMENTARE</div>', 260, 860, f'{A("p13@jung", "end", 0.1)} data-sfx="plop"', 560, CENTER))


SCENE_JS = r''' // ---- Bühne: Europakarte, Deutschland entsteht ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const M=document.getElementById('mapg');
  const keys=PAN.cam.map(k=>({t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4],fy:k[5]}));
  function base(tt){ if(tt<=keys[0].t) return keys[0]; for(let i=0;i<keys.length-1;i++){ const k0=keys[i],k1=keys[i+1]; if(tt>=k0.t&&tt<k1.t){ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e),fy:k0.fy+(k1.fy-k0.fy)*e}; } } return keys[keys.length-1]; }
  const bs=base(t), z=bs.z, cx=bs.x, cy=bs.y, FX=460, FY=bs.fy;
  M.setAttribute('transform',`translate(${FX},${FY}) scale(${z}) translate(${-cx},${-cy})`);
  const pj=(x,y)=>[FX+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('.geo')){ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }
  const op=(id,v)=>{document.getElementById(id).style.opacity=cl(v,0,1);};
  const mix=(a,b,u)=>a.map((v,i)=>Math.round(v+(b[i]-v)*u));
  // heutiges Deutschland: Hook + nach der Wiedervereinigung
  op('e_de', Math.max(1-pr(t,TS('p3',0.05),0.45), pr(t,TS('p11@zusammen',0.1),0.5)));
  // Frankenreich -> 843 dreigeteilt
  const fr=pr(t,TS('p3@Frankenreich',-0.3),0.6), sp=ease(pr(t,TS('p4@drei',-0.1),0.5)), gone=pr(t,TS('p6@wuchs',0.3),0.7);
  const P0=[123,63,228];
  document.getElementById('f_west').setAttribute('fill',`rgba(${mix(P0,[58,110,165],sp)},${.42-.12*sp})`);
  document.getElementById('f_mid').setAttribute('fill',`rgba(${mix(P0,[150,154,165],sp)},${.42-.14*sp})`);
  const kz=TS('p5@Keimzelle',-0.1); const pulse=t>kz&&t<kz+2.4?0.5+0.5*Math.sin((t-kz)*2*Math.PI/0.8-Math.PI/2):0;
  document.getElementById('f_east').setAttribute('fill',`rgba(123,63,228,${.42+.25*pulse})`);
  document.getElementById('f_east').setAttribute('stroke-width',1.6+2.4*pulse);
  op('e_west', fr*(1-pr(t,TS('p5@östliche',0),0.5)*0.55)*(1-gone)); op('e_mid', fr*(1-pr(t,TS('p5@östliche',0),0.5)*0.55)*(1-gone));
  op('e_east', fr*(1-pr(t,TS('p6@Römische',0),0.6)));
  const b8=document.getElementById('b843'); b8.style.strokeDashoffset=1-ease(pr(t,TS('p4@drei',-0.2),0.8)); b8.style.opacity=(t>TS('p4@drei',-0.2)?1:0)*(1-gone); b8.setAttribute('stroke-width',(3/z).toFixed(3));
  // Wachstum (clip-Kreise)
  for(const [k,v] of Object.entries(PAN.grow)){ const t0=TS(v.a,v.o), q=ease(pr(t,t0,v.d));
    document.querySelectorAll(`.gcc[data-k="${k}"]`).forEach(C=>C.setAttribute('r',(v.r*q).toFixed(1))); }
  const zf=TS('p8@zerfiel',-0.1);
  op('e_hrr', pr(t,TS(PAN.grow.hrr.a,PAN.grow.hrr.o),0.2)*(1-pr(t,zf,0.9)));
  // Flickenteppich: ~300 Zellen poppen nacheinander auf, 1806 zerfallen sie
  const c0=TS('p7@Flickenteppich',-0.25); const cells=document.querySelectorAll('.cell');
  op('e_cells', (t>=c0&&t<zf+1.6)?1:0);
  if(t>=c0-0.1&&t<zf+2){ const cxh=PAN.cells.reduce((a,c)=>a+c[0],0)/PAN.cells.length, cyh=PAN.cells.reduce((a,c)=>a+c[1],0)/PAN.cells.length;
   cells.forEach((c,i)=>{ const h=((i*7919)%300)/300; const ti=c0+h*1.7; const a=pr(t,ti,0.18);
     const fz=ease(pr(t,zf+h*0.6,0.7)); const [px,py]=PAN.cells[i];
     const dx=(px-cxh)*0.5*fz, dy=(py-cyh)*0.5*fz+14*fz*fz;
     c.style.opacity=a*(1-fz); c.setAttribute('transform',`translate(${dx.toFixed(2)},${dy.toFixed(2)})`); }); }
  // Kaiserreich
  op('e_kr', pr(t,TS(PAN.grow.kr.a,PAN.grow.kr.o),0.2)*(1-pr(t,TS('p10@entstanden',0),0.5)));
  // 1949: BRD + DDR, Grenze zeichnet sich; 1990 verschwindet sie
  const t49=TS('p10@entstanden',0.1);
  op('e_brd', pr(t,t49,0.5)*(1-pr(t,TS('p11@zusammen',0.1),0.5)));
  op('e_ddr', pr(t,TS('p10@zwei',-0.2),0.5)*(1-pr(t,TS('p11@zusammen',0.1),0.5)));
  const bd=document.getElementById('bdr'); bd.style.strokeDashoffset=1-ease(pr(t,TS('p10@zwei',-0.2),0.9));
  bd.style.opacity=(t>TS('p10@zwei',-0.2)?1:0)*(1-pr(t,TS('p11@wuchsen',0),0.6)); bd.setAttribute('stroke-width',(3.5/z).toFixed(3));
  // Abdunkeln für die Abschlussfrage
  M.style.opacity=1-0.5*pr(t,TS('p13@gedacht',-0.2),0.5);
  let yr=''; for(const [a,s] of PAN.years) if(t>=S[a]) yr=s; document.getElementById('yr').textContent=yr;
  // Zeitleiste (Stationen)
  let f=0, prv=0; for(const k of PAN.tl){ const a=S[k[0]]; if(t>=a) { f=prv+(k[1]-prv)*ease(pr(t,a,1.0)); } prv=k[1]; }
  document.getElementById('tfill').style.transform=`scaleX(${f})`;
  document.getElementById('tdot').style.left=(36+848*f)+'px'; document.getElementById('tdot').style.opacity=pr(t,S['p4'],0.3);
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
</style></head><body><div id="v">
<div id="chap" class="mono"></div><div id="prog">{"".join("<div></div>" for _ in CH)}</div><div id="wm">{mono}</div>
<div id="head"></div>
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
 const top=cl(1-pr(t,END,.3),0,1); ['chap','prog','head'].forEach(id=>document.getElementById(id).style.opacity=top);
 let hs=b.s; for(let i=BEATS.indexOf(b);i>0&&BEATS[i-1].head===b.head;i--) hs=BEATS[i-1].s;
 const H=document.getElementById('head'); H.textContent=b.head; H.style.fontSize=(b.head.length>38?'56px':'66px'); if(BEATS.indexOf(b)===0) hs=-1; const hp=ease(pr(t,hs,.3));
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
