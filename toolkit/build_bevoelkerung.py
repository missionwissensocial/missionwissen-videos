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
CH = ["01 DIE FRAGE", "02 EISZEIT", "03 LANDWIRTSCHAFT", "04 1800", "05 HEUTE", "06 UND DU?"]
B = [
 ("p1", 0, "Wie viele Menschen gab es früher?", "Wie *viele* *Menschen* lebten *früher* auf der *Erde?*", None),
 ("p2", 1, "Ende der Eiszeit", "Am *Ende* der letzten *Eiszeit,* vor rund *zwölftausend* *Jahren,* waren es nach *Schätzungen* nur ein paar *Millionen.*", None),
 ("p3", 1, "Weniger als eine Großstadt", "*Weniger,* als heute in manch einer *Großstadt* wohnen.", None),
 ("p4", 2, "Dann kam die Landwirtschaft", "Dann kam die *Landwirtschaft:* Wer *Felder* hat, kann *mehr* *Menschen* *ernähren.*", None),
 ("p5", 2, "Trotzdem: ganz langsam", "Trotzdem wuchs die *Menschheit* *langsam,* denn *Hunger,* *Seuchen* und *Kriege* *bremsten* immer wieder.", None),
 ("p6", 3, "1800: die erste Milliarde", "Erst um *achtzehnhundert* gab es die *erste* *Milliarde.*", None),
 ("p7", 3, "Plötzlich steil nach oben", "Dann ging es *plötzlich* *steil* nach *oben:* bessere *Medizin,* sauberes *Wasser,* mehr *Essen.*", None),
 ("p8", 4, "Heute: über 8 Milliarden", "*Heute* leben über *acht* *Milliarden* *Menschen* auf der *Erde.*", None),
 ("p9", 4, "Die letzte Milliarde", "Für die *letzte* *Milliarde* haben wir nur *zwölf* *Jahre* gebraucht.", None),
 ("p10", 4, "Der Sprung kam spät", "Fast die *ganze* *Geschichte* über waren wir also *wenige,* der *große* *Sprung* kam erst ganz *zuletzt.*", None),
 ("p11", 5, "Hättest du's gedacht?", "*Hättest* du *gedacht,* dass es so *spät* losging, *ja* oder *nein?*", "winkt"),
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

I.update(
 bone='<path d="M13 19a5 5 0 1 1 6-7l17 17a5 5 0 1 1 7 6 5 5 0 1 1-7 6L19 24a5 5 0 1 1-6-5z"/>',
 dna='<path d="M15 4c0 13 18 13 18 20S15 31 15 44M33 4c0 13-18 13-18 20s18 7 18 20M19 11h10M18 37h12M21 17h6M21 31h6"/>',
 boat='<path d="M5 30h38l-6 9H11z"/><path d="M24 7v23M24 9l13 17H24"/>',
 walk='<circle cx="26" cy="8" r="4"/><path d="M24 15l-5 13 7 6 3 10M19 28l-6 14M22 18l9 6 6-2M21 19l-8 6"/>',
)
CENTER = "display:flex;justify-content:center"
I.update(
 wheat='<path d="M24 44V14"/><path d="M24 20c-6-1-9-5-9-10 6 1 9 5 9 10zM24 20c6-1 9-5 9-10-6 1-9 5-9 10zM24 30c-6-1-9-5-9-10 6 1 9 5 9 10zM24 30c6-1 9-5 9-10-6 1-9 5-9 10z"/>',
 city='<path d="M5 43h38M9 43V20h10v23M19 43V8h12v35M31 43V16h9v27"/><path d="M13 25h2M13 31h2M23 14h4M23 21h4M23 28h4M35 22h2M35 29h2"/>',
 med='<rect x="8" y="8" width="32" height="32" rx="8"/><path d="M24 15v18M15 24h18"/>',
 drop='<path d="M24 5c8 11 13 18 13 25a13 13 0 0 1-26 0c0-7 5-14 13-25z"/>',
 bread='<path d="M8 22c0-7 7-11 16-11s16 4 16 11c0 3-2 4-4 4v14H12V26c-2 0-4-1-4-4z"/>',
 people='<circle cx="16" cy="15" r="5"/><circle cx="32" cy="15" r="5"/><path d="M5 38c0-7 5-11 11-11s11 4 11 11M21 38c0-7 5-11 11-11s11 4 11 11"/>',
)
# ---- Bevölkerungskurve (Schätzungen HYDE 3.3 / Gapminder / UN WPP; Zeitachse gestaucht) ----
DATA = [(-10000,4.4),(-8000,5),(-6000,8),(-4000,16),(-3000,28),(-2000,45),(-1000,72),(1,230),(500,210),(1000,295),(1300,400),(1400,370),
        (1500,460),(1600,560),(1700,610),(1800,990),(1850,1260),(1900,1650),(1950,2500),(1960,3020),(1974,4000),(1987,5000),
        (1999,6000),(2011,7000),(2022,8000),(2026,8300)]
PX0, PY0, PW, PH = 90, 520, 760, 440   # Plot im Panel (920x600)
SEGX = [(-10000, 0), (0, 330), (1800, 600), (2026, 760)]
def YX(y):
    for (a, xa), (b, xb) in zip(SEGX, SEGX[1:]):
        if y <= b: return PX0 + xa + (xb - xa) * (y - a) / (b - a)
    return PX0 + PW
def PY(m): return PY0 - PH * m / 9000
import math
def popat(y):
    for (a, ma), (b, mb) in zip(DATA, DATA[1:]):
        if y <= b: u = (y - a) / (b - a); return math.exp(math.log(ma) + (math.log(mb) - math.log(ma)) * u)
    return DATA[-1][1]
pts = []
yr = -10000.0
while yr < 2026:
    pts.append([round(yr, 1), round(YX(yr), 1), round(PY(popat(yr)), 1)])
    yr += 120 if yr < 0 else (12 if yr < 1800 else 1.5)
pts.append([2026, round(YX(2026), 1), round(PY(8300), 1)])
hl = " ".join(f"{p[1]},{p[2]}" for p in pts if 2010 <= p[0] <= 2023)
CURVE = dict(pts=pts, keys=[("p1", 0, -10000), ("p2@Millionen", 0, -10000), ("p4@Landwirtschaft", 0, -10000), ("p4@ernähren", 0.6, -3000),
             ("p5@Trotzdem", 0, -3000), ("p5@wieder", 0.4, 1700), ("p6@achtzehnhundert", -0.2, 1700), ("p6@Milliarde", 0.2, 1800),
             ("p7@steil", 0, 1800), ("p7@oben", 0.4, 1950), ("p7@Essen", 0.2, 2000), ("p8@acht", 0.2, 2026)])
ax = (f'<line x1="{PX0}" y1="{PY0}" x2="{PX0+PW+10}" y2="{PY0}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>'
      f'<line x1="{PX0}" y1="{PY0}" x2="{PX0}" y2="{PY0-PH-10}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>')
for y, lab_ in [(-10000, "−10.000"), (0, "JAHR 0"), (1800, "1800"), (2026, "HEUTE")]:
    x = YX(y); anc = "start" if y == -10000 else ("end" if y == 2026 else "middle")
    ax += f'<line x1="{x:.1f}" y1="{PY0}" x2="{x:.1f}" y2="{PY0+12}" stroke="{INK}" stroke-width="2.4"/>'
    ax += f'<text x="{x:.1f}" y="{PY0+44}" text-anchor="{anc}" font-family="JBM" font-weight="700" font-size="22" fill="{INK2}">{lab_}</text>'
for m, lab_ in [(2000, "2"), (4000, "4"), (6000, "6"), (8000, "8")]:
    ax += f'<line x1="{PX0-10}" y1="{PY(m):.1f}" x2="{PX0}" y2="{PY(m):.1f}" stroke="{INK}" stroke-width="2.4"/><text x="{PX0-18}" y="{PY(m)+8:.1f}" text-anchor="end" font-family="JBM" font-weight="700" font-size="22" fill="{INK2}">{lab_}</text>'
ax += f'<text x="{PX0-18}" y="{PY0-PH-24}" text-anchor="start" font-family="JBM" font-weight="700" font-size="20" fill="{INK2}">MRD. MENSCHEN</text>'
y1, y8 = PY(1000), PY(8000)
chartsvg = (f'<svg width="920" height="600" style="position:absolute;left:0;top:0;overflow:visible">{ax}'
            f'<line id="l1" x1="{PX0}" y1="{y1:.1f}" x2="{YX(1800):.1f}" y2="{y1:.1f}" stroke="{PUR}" stroke-width="2.4" stroke-dasharray="8 8" style="opacity:0"/>'
            f'<line id="l8" x1="{PX0}" y1="{y8:.1f}" x2="{YX(2022):.1f}" y2="{y8:.1f}" stroke="{PUR}" stroke-width="2.4" stroke-dasharray="8 8" style="opacity:0"/>'
            f'<rect id="bflat" x="{PX0+4}" y="{PY0-120}" width="{YX(1800)-PX0-8:.1f}" height="112" rx="10" fill="rgba(138,143,153,.12)" stroke="#8A8F99" stroke-width="2" stroke-dasharray="6 6" style="opacity:0"/>'
            f'<rect id="bjump" x="{YX(1800)+4:.1f}" y="{PY0-PH-6}" width="{YX(2026)-YX(1800)-4:.1f}" height="{PH+2}" rx="10" fill="rgba(123,63,228,.10)" stroke="{PUR}" stroke-width="2" stroke-dasharray="6 6" style="opacity:0"/>'
            f'<polyline id="curvew" points="" fill="none" stroke="#FFFFFF" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<polyline id="curve" points="" fill="none" stroke="{PUR}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<polyline id="hl" points="{hl}" fill="none" stroke="{TQ}" stroke-width="12" stroke-linecap="round" style="opacity:0"/></svg>')
ov = '<div id="tip" style="position:absolute;left:0;top:0;opacity:0"><div class="tipring"></div><div class="tipdot"></div></div>'
def lab(x, y, text, i, o, col=PUR, d=0, sfx=""):
    return (f'<div class="el mk" {A(i, o, d)}{sfx} style="left:{x:.0f}px;top:{y:.0f}px"><span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div>')
ov += el('<div class="chip mono" style="font-size:19px;padding:8px 12px">MENSCHHEITSGESCHICHTE · FOLGE 2</div>', 22, 22, A("p1", "p3", 0.2) + ' data-sfx="none"')
ov += el('<div class="chip mono" style="font-size:17px;padding:6px 10px;color:#8A8F99;border-color:#C9CCD3;white-space:nowrap">SCHÄTZUNGEN · ZEITACHSE GESTAUCHT</div>', 500, 18, A("p2@Schätzungen", "p11", 0.2) + ' data-sfx="none"')
ov += el('<div class="qbig" style="position:static;font-size:200px;line-height:1">?</div>', 380, 120, A("p1", "p2", 0.1))
ov += lab(PX0 + 10, PY0 - 70, "≈ 1–10 MIO. · SCHÄTZUNG", "p2@Millionen", "p4", "#0E8C80", -0.3)
ov += lab(PX0 + 10, y1 - 54, "1 MRD. · UM 1800", "p6@Milliarde", "p10", PUR, -0.2)
ov += lab(PX0 + 10, y8 - 54, "ÜBER 8 MRD. · HEUTE", "p8@Milliarden", "p11", PUR, 0)
ov += lab(YX(1800) - 330, PY0 - 300, "7 → 8 MRD.: 12 JAHRE", "p9@zwölf", "p10", "#0E8C80", 0)
ov += lab(PX0 + 20, PY0 - 172, "FAST DIE GANZE ZEIT: WENIGE", "p10@wenige", "p11", "#8A8F99", -0.2)
ov += lab(YX(1800) - 140, 180, "ZULETZT", "p10@zuletzt", "p11", PUR, -0.2)
stage.append(mm(chartsvg + f'<div id="ov" style="position:absolute;inset:0">{ov}</div>', 80, 640, 920, 600, A("p1", "p11", -0.4)))
# ---- Karten oberhalb des Diagramms (y 460–620) ----
def top(icon, col, small, big, i, o, cls="active", d=0, fs=50):
    return card(f'<div class="row" style="gap:28px;height:100%">{ic(I[icon],80,col)}<div class="col" style="gap:4px;align-items:flex-start"><div class="mono small grey">{small}</div><div class="bignum" style="font-size:{fs}px;letter-spacing:-1.5px">{big}</div></div></div>', 80, 455, 920, 160, cls, A(i, o, d))
stage.append(top("people", PUR, "WELTBEVÖLKERUNG", "Früher vs. heute", "p1", "p2", d=0.05))
stage.append(top("clock", TQ, "VOR RUND 12.000 JAHREN", "nur ein paar Millionen", "p2@zwölftausend", "p3", "activeTQ", -0.2, 48))
stage.append(top("city", "#8A8F99", "WENIGER ALS HEUTE IN", "manch einer Großstadt", "p3@Weniger", "p4", "", -0.1, 48))
stage.append(top("wheat", PUR, "LANDWIRTSCHAFT", "Felder ernähren mehr", "p4@Landwirtschaft", "p5", d=-0.2, fs=48))
stage.append(el('<div class="row" style="gap:18px;justify-content:center"><div class="chip mono" style="font-size:30px">HUNGER</div><div class="chip mono" style="font-size:30px">SEUCHEN</div><div class="chip mono" style="font-size:30px">KRIEGE</div></div>', 80, 490, A("p5@Hunger", "p6", -0.1) + ' data-sfx="plop"', 920))
stage.append(el('<div class="stamp mono" style="font-size:48px;color:#E5484D;border-color:#E5484D">BREMSEN</div>', 80, 760, A("p5@bremsten", "p6"), 920, CENTER))
stage.append(top("people", PUR, "UM 1800", f"die erste Milliarde", "p6@Erst", "p7", d=0, fs=50))
stage.append(el(f'<div class="row" style="gap:18px;justify-content:center"><div class="chip pu mono" style="font-size:28px">MEDIZIN</div><div class="chip tq mono" style="font-size:28px">SAUBERES WASSER</div><div class="chip pu mono" style="font-size:28px">MEHR ESSEN</div></div>', 80, 490, A("p7@Medizin", "p8", -0.1) + ' data-sfx="plop"', 920))
stage.append(top("globe", PUR, "HEUTE", f"über {cnt(8, 'p8@acht')} Milliarden", "p8", "p9", d=0, fs=56))
stage.append(top("clock", TQ, "DIE LETZTE MILLIARDE", f"in nur {cnt(12, 'p9@zwölf')} Jahren", "p9@letzte", "p10", "activeTQ", -0.1, 56))
stage.append(el('<div class="stamp mono" style="font-size:52px;color:#7B3FE4;border-color:#7B3FE4">GROSSER SPRUNG</div>', 80, 480, A("p10@Sprung", "p11"), 920, CENTER))
# p11 Frage (Roboter winkt)
stage.append(card(f'<div class="row" style="gap:30px;height:100%;justify-content:center">{ic(I["people"],130,PUR)}<div class="qbig" style="position:static;font-size:150px;line-height:1">?</div></div>', 440, 470, 560, 300, "active", A("p11@Hättest", "end")))
stage.append(el('<div class="row" style="gap:24px;justify-content:center"><div class="chip tq mono" style="font-size:40px;padding:14px 34px">JA</div><div class="chip mono" style="font-size:40px;padding:14px 34px">NEIN</div></div>', 440, 820, f'{A("p11@ja", "end")} data-sfx="plop"', 560))
stage.append(el('<div class="chip pu mono" style="font-size:22px">SCHREIB\'S IN DIE KOMMENTARE</div>', 440, 960, f'{A("p11@nein", "end", 0.2)} data-sfx="plop"', 560, CENTER))

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
</style></head><body><div id="v">
<div id="chap" class="mono"></div><div id="prog">{"".join("<div></div>" for _ in CH)}</div><div id="wm">{mono}</div>
<div id="head"></div>
{"".join(stage)}
{endcard}
<div id="robot">{robots}</div>
<div id="cap"><div id="pill"></div></div>
</div>
<script>
const CURVE={json.dumps(CURVE, ensure_ascii=False)};
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
 const H=document.getElementById('head'); H.textContent=b.head; H.style.fontSize=(b.head.length>38?'56px':'66px'); const hp=ease(pr(t,hs,.3));
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
 // ---- Bevölkerungskurve ----
 {{
  const K=CURVE.keys.map(k=>({{t:(S[k[0]]??0)+k[1],y:k[2]}}));
  let yr=K[0].y; for(let i=0;i<K.length-1;i++){{ const a=K[i],c=K[i+1]; if(t>=a.t&&t<c.t){{ const u=(t-a.t)/Math.max(1e-6,c.t-a.t), e=u*u*(3-2*u); yr=a.y+(c.y-a.y)*e; break; }} if(t>=c.t) yr=c.y; }}
  const P=CURVE.pts; const arr=[]; let tip=P[0];
  for(let i=0;i<P.length;i++){{ if(P[i][0]<=yr){{ arr.push(P[i]); tip=P[i]; }} else {{ if(i>0){{ const a=P[i-1],c=P[i],u=(yr-a[0])/(c[0]-a[0]); tip=[yr,a[1]+(c[1]-a[1])*u,a[2]+(c[2]-a[2])*u]; arr.push(tip); }} break; }} }}
  const on=t>=S['p2@Millionen']-0.3;
  const str=on?arr.map(p=>p[1].toFixed(1)+','+p[2].toFixed(1)).join(' '):'';
  document.getElementById('curve').setAttribute('points',str); document.getElementById('curvew').setAttribute('points',str);
  const TP=document.getElementById('tip'); TP.style.left=tip[1]+'px'; TP.style.top=tip[2]+'px'; TP.style.opacity=on?pr(t,S['p2@Millionen']-0.3,0.3):0;
  const rg=TP.querySelector('.tipring'); const ph=(t%1.1)/1.1; rg.style.transform=`scale(${{0.5+1.1*ph}})`; rg.style.opacity=1-ph;
  const fo=(id,a,b)=>{{document.getElementById(id).style.opacity=pr(t,a,0.4)*(1-pr(t,b,0.3));}};
  fo('l1',S['p6@Milliarde']-0.2,S['p10']); fo('l8',S['p8@Milliarden'],S['p11']); fo('hl',S['p9@letzte'],S['p10']);
  fo('bflat',S['p10@wenige']-0.2,S['p11']); fo('bjump',S['p10@zuletzt']-0.2,S['p11']);
 }}
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
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))
