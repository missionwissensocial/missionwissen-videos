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
CH = ["01 DIE FRAGE", "02 DAS LAGER", "03 DAS ESSEN", "04 DIE JAGD", "05 DIE ARBEIT", "06 DER ABEND", "07 UND DU?"]
B = [
 ("p1", 0, "Wie lebten unsere Vorfahren?", "Wie haben unsere *Vorfahren* in der *Steinzeit* eigentlich *gelebt?*", None),
 ("p2", 0, "Ein Tag in der Eiszeit", "Stell dir *einen* *Tag* in der *Eiszeit* vor.", None),
 ("p3", 1, "Aufwachen im Fellzelt", "Du wachst in einem *Zelt* aus *Fellen* auf, in einer *kleinen* *Gruppe,* kaum größer als eine *Schulklasse.*", None),
 ("p4", 1, "Immer unterwegs", "Ein *festes* *Zuhause* gibt es *nicht:* Ihr zieht den *Tieren* und den *Jahreszeiten* hinterher.", None),
 ("p5", 2, "Was gibt's zu essen?", "Gegessen wird, was die *Natur* hergibt: *Beeren,* *Wurzeln,* *Kräuter,* *Vogeleier* und, wenn die *Jagd* klappt, *Fleisch.*", None),
 ("p6", 3, "Jagd im Team", "Gejagt wird *gemeinsam,* mit *Speeren* aus *Holz.*", None),
 ("p7", 3, "Speere aus Niedersachsen", "Einige der *ältesten* *Speere* der *Welt* hat man in *Niedersachsen* gefunden.", None),
 ("p8", 4, "Wie viel Arbeit war das?", "Und wie viel *Arbeit* war das?", None),
 ("p9", 4, "Nur rund 20 Stunden", "Eine *Studie* bei *heutigen* *Jägern* und *Sammlern* zeigt: Fürs *Jagen* und *Sammeln* gehen nur rund *zwanzig* *Stunden* pro *Woche* drauf.", None),
 ("p10", 5, "Abends am Feuer", "*Abends* sitzt man *zusammen* am *Feuer* und macht *Musik.*", None),
 ("p11", 5, "Flöten aus Knochen", "Auf der *Schwäbischen* *Alb* fand man *Flöten* aus *Vogelknochen,* sie gehören zu den *ältesten* *Instrumenten* der Welt.", None),
 ("p12", 5, "Wie alt wurden sie?", "Und wer die *Kindheit* überstand, konnte durchaus *sechzig* oder *siebzig* werden.", None),
 ("p13", 5, "Trotzdem: hartes Leben", "*Leicht* war dieses *Leben* trotzdem *nicht.*", None),
 ("p14", 6, "Würdest du tauschen?", "Würdest du *einen* *Tag* *tauschen,* *ja* oder *nein?*", None),
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


# ================= Panorama "Ein Tag in der Steinzeit" =================
import math
I.update(
 spear='<path d="M8 42L40 8"/><path d="M40 8l-9 3 6 6z"/>',
 flute='<rect x="4" y="20" width="40" height="8" rx="4"/><circle cx="16" cy="24" r="1.6"/><circle cx="23" cy="24" r="1.6"/><circle cx="30" cy="24" r="1.6"/>',
 heart='<path d="M24 41S7 31 7 18a9 9 0 0 1 17-4 9 9 0 0 1 17 4c0 13-17 23-17 23z"/>',
 sun='<circle cx="24" cy="24" r="8"/><path d="M24 6v5M24 37v5M6 24h5M37 24h5M11 11l3.5 3.5M33.5 33.5L37 37M11 37l3.5-3.5M33.5 14.5L37 11"/>',
 moon='<path d="M33 30A14 14 0 0 1 19 9a15 15 0 1 0 14 21z"/>',
 house='<path d="M8 22L24 9l16 13M12 19v20h24V19"/><path d="M21 39V29h6v10"/>',
 snow='<path d="M24 6v36M8.4 15l31.2 18M8.4 33l31.2-18"/><path d="M19 9l5 4 5-4M19 39l5-4 5 4"/>',
 leaf='<path d="M10 38C10 18 22 9 40 8c0 19-9 31-29 31z"/><path d="M10 38l16-16"/>',
 flower='<circle cx="24" cy="20" r="4"/><path d="M24 24v18M24 34c-6 0-9-4-9-7 4 0 9 3 9 7z"/><circle cx="24" cy="11" r="4"/><circle cx="32" cy="20" r="4"/><circle cx="16" cy="20" r="4"/><circle cx="24" cy="28" r="0.1"/>',
 drop='<path d="M24 6c8 11 13 18 13 24a13 13 0 0 1-26 0c0-6 5-13 13-24z"/>',
 study='<path d="M8 40V10h22l10 10v20z"/><path d="M30 10v10h10M14 30l6-6 5 4 8-9"/>',
)
WW = 5000
CENTER = "display:flex;justify-content:center"
GY = lambda x: 640 + 10 * math.sin(x / 210)            # Trampelpfad (Spur)
def ground_d(x0, x1, y0=600):
    pts = []; x = x0
    while x <= x1:
        pts.append(f"{x - x0:.0f} {y0 + 7 * math.sin(x / 95) + 4 * math.sin(x / 37):.1f}"); x += 40
    return "M" + " L".join(pts)
def mount_d(x0, x1, seed):
    import random; r = random.Random(seed); pts = [f"0 360"]; x = x0
    while x < x1:
        x += r.randint(70, 140); pts.append(f"{x - x0} {r.randint(255, 330)}"); x += r.randint(60, 120); pts.append(f"{x - x0} {r.randint(335, 365)}")
    return "M" + " L".join(pts)
def backdrop(x0, x1, anchor, d=0, seed=1):
    w = x1 - x0
    body = P(mount_d(x0, x1, seed), 1.4, INK2) + P(ground_d(x0, x1), 2.4)
    for k in range(int(w / 110)):                         # Grasbüschel
        gx = 30 + k * 110 + (k * 37) % 50; gy = 606 + 7 * math.sin((x0 + gx) / 95)
        body += D(f"M{gx} {gy:.0f} l-5 -14 M{gx + 6} {gy:.0f} l1 -17 M{gx + 12} {gy:.0f} l6 -12", 1.3)
    return sketch(body, w, 760, x0, 0, anchor, d, 2.2)

W_ = []   # world-Elemente
def wel(inner, x, y, attrs, style=""): W_.append(el(inner, x, y, attrs, None, style))
def wsk(*a, **k): W_.append(sketch(*a, **k))
def wmk(text, x, y, i, o, d=0.1, col=PUR, icon=None):
    pin = f'<span class="pin" style="background:{col}"></span>' if not icon else f'<span class="ipin">{ic(I[icon], 38, col, 3.4)}</span>'
    W_.append(f'<div class="el mk" {A(i, o, d)} style="left:{x}px;top:{y}px;gap:10px">{pin}<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div>')
def fig(col=INK, sc=1.0, arm=""):
    return (f'<svg width="{30*sc:.0f}" height="{54*sc:.0f}" viewBox="0 0 30 54" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round">'
            f'<circle cx="15" cy="8" r="6.5" fill="#fff"/><path d="M15 15v19M15 34l-7 17M15 34l7 17{arm or " M5 24h20"}"/></svg>')

# ---- Station 1: Lager (x 0–1000) ----
for i, (x0, x1, s) in enumerate([(0, 1000, 3), (1000, 2000, 5), (2000, 2950, 7), (2950, 3900, 9), (3900, 5000, 11)]):
    backdrop(x0, x1, ["p1", "p4@zieht", "p5@Gegessen", "p6", "p8@Arbeit"][i], [-1.2, 0, 0, 0, 0][i], s)
def tent(cx, w=200, h=190, base=605):
    l, r, top = cx - w / 2, cx + w / 2, base - h
    s = P(f"M{l} {base} L{cx} {top} L{r} {base}", 2.6) + P(f"M{cx - 16} {top - 22} L{cx + 18} {top + 30} M{cx + 16} {top - 22} L{cx - 18} {top + 30}", 2.2)
    s += P(f"M{cx - 26} {base} L{cx} {base - 70} L{cx + 26} {base}", 2.2)
    for k in range(1, 6):                                   # Fell-Schraffur
        yy = top + k * h / 6; dx = (yy - top) / h * w / 2
        s += D(f"M{cx - dx + 12} {yy:.0f} q{dx - 12:.0f} 10 {2 * dx - 24:.0f} 0", 1.3)
    return s
wsk(tent(250) + tent(520, 230, 210) + tent(790, 180, 170), 1000, 760, 0, 0, "p1", -1.0, 1.8)
wel(f'<div class="chip mono" style="font-size:19px;padding:8px 12px">ILLUSTRATION · SCHEMATISCH</div>', 560, 712, A("p3", "p4", 0.2) + ' data-sfx="none"')
wmk("ZELT AUS FELLEN", 600, 320, "p3@Fellen", "p4@zieht", 0.0)
k = 0
for row, (y, n, x0) in enumerate([(612, 9, 150), (652, 8, 172), (692, 8, 150)]):
    for j in range(n):
        x = x0 + j * 86 + (row % 2) * 10
        W_.append(f'<div class="el aa" {A("p3@Gruppe", "p4@zieht", round(-0.05 + k * 0.035, 3))} style="left:{x}px;top:{y - 38}px">{fig(PUR if (k % 7 == 3) else INK, 0.75)}</div>'); k += 1
wmk("≈ EINE SCHULKLASSE", 70, 300, "p3@Schulklasse", "p4@zieht", 0.0, TQ)
# ---- Station 2: Wandern (x 1000–2000) ----
W_.append(f'<div class="el" {A("p4@Zuhause", "p4@zieht", 0)} data-sfx="fail" style="left:680px;top:300px"><div class="ipin" style="width:96px;height:96px">{ic(I["house"], 66, INK, 3)}</div><div class="xx">✕</div></div>')
herd = ""
for j, (hx, hy) in enumerate([(0, 40), (120, 0), (230, 50), (340, 15)]):
    herd += (f'<g transform="translate({hx} {hy})">' + P("M10 60 q40 -22 90 -6 q10 4 14 -10 l8 -20 l10 4 l-6 26 q-6 20 -22 22", 2.2) +
             P("M30 58 l-4 44 M48 60 l2 44 M84 62 l-4 40 M98 60 l4 42", 2.0) + P("M120 26 l-8 -22 M120 26 l6 -26 M114 10 l-10 -4 M126 6 l10 -6", 1.6) + "</g>")
W_.append(f'<div class="el" {A("p4@Tieren", "p5@hergibt", -0.2)} data-sfx="none" style="left:1440px;top:470px"><div class="mv" data-ma="p4@Tieren" data-vx="70">{sketch(herd, 480, 170, 0, 0, "p4@Tieren", -0.2, 1.4)}</div></div>')
wmk("RENTIERE · PFERDE", 1500, 410, "p4@Tieren", "p5@hergibt", 0.3, INK2)
wheel = (f'<div class="spin" data-sa="p4@Jahreszeiten" style="position:relative;width:200px;height:200px;border-radius:50%;border:3px dashed {PUR};background:rgba(255,255,255,.85)">'
         + "".join(f'<div style="position:absolute;left:{70 + 68 * math.cos(a):.0f}px;top:{70 + 68 * math.sin(a):.0f}px;width:60px;height:60px">{ic(I[n], 60, c, 3)}</div>'
                   for a, n, c in [(-math.pi / 2, "snow", INK), (0, "flower", TQ), (math.pi / 2, "sun", PUR), (math.pi, "leaf", INK2)]) + '</div>')
wel(wheel, 1160, 250, A("p4@Jahreszeiten", "p5@hergibt", -0.2))
wmk("JAHRESZEITEN", 1135, 470, "p4@Jahreszeiten", "p5@hergibt", 0.2)
# ---- Station 3: Essen (x 2000–2950) ----
bush = P("M10 230 q-20 -60 30 -90 q10 -70 80 -60 q40 -50 90 0 q60 0 50 70 q30 40 0 80 z", 2.4) + P("M100 230 v40", 2.4)
for bx, by in [(60, 150), (90, 120), (130, 170), (150, 110), (180, 150), (110, 200), (200, 190), (70, 200)]:
    bush += f'<circle cx="{bx}" cy="{by}" r="11" fill="{PUR}" fill-opacity=".85" class="mesh" style="opacity:0"/>' + C(bx, by, 11, 1.8)
wsk(bush, 240, 280, 1880, 345, "p5@Beeren", -0.3, 1.0)
roots = P("M60 0 v50 M60 50 q-20 30 -40 40 M60 50 q10 40 30 60 M60 70 q-4 30 -2 70", 2.2) + P("M40 -40 q20 -30 20 -60 q10 30 30 40", 2.0)
wsk(roots, 140, 200, 2150, 600, "p5@Wurzeln", -0.3, 0.9)
herbs = "".join(P(f"M{x} 120 q{-14 + 7 * j} -50 {6 * j - 10} -100 M{x} 80 q-24 -6 -30 -26 M{x} 60 q22 -4 30 -24", 2.0) for j, x in enumerate([30, 70, 110]))
wsk(herbs, 150, 130, 2310, 480, "p5@Kräuter", -0.3, 0.9)
nest = P("M10 70 q70 50 140 0", 2.6) + D("M14 74 q66 38 132 -2 M22 82 q58 26 116 -4", 1.4) + "".join(
    f'<ellipse cx="{x}" cy="58" rx="17" ry="22" fill="#fff" stroke="{INK}" stroke-width="2.2" class="mesh" style="opacity:0"/>' for x in (50, 80, 110))
wsk(nest, 160, 110, 2440, 500, "p5@Vogeleier", -0.3, 0.8)
meat = P("M30 70 q-30 -40 10 -60 q50 -20 70 30 q10 30 -20 40 z", 2.4) + P("M40 70 l-16 22 m0 0 a8 8 0 1 1 -10 -8 m10 8 a8 8 0 1 1 -2 12", 2.2)
W_.append(f'<div class="el" {A("p5@Fleisch", "p6@gemeinsam", -0.15)} data-sfx="plop" style="left:2620px;top:460px">{sketch(meat, 130, 110, 0, 0, "p5@Fleisch", -0.2, 0.7)}</div>')
for x, y, w_, key in [(1900, 300, "BEEREN", "Beeren"), (2215, 660, "WURZELN", "Wurzeln"), (2290, 405, "KRÄUTER", "Kräuter"), (2440, 430, "VOGELEIER", "Vogeleier"), (2610, 380, "FLEISCH", "Fleisch")]:
    W_.append(f'<div class="el" {A("p5@" + key, "p6@gemeinsam", 0)} data-sfx="plop" style="left:{x}px;top:{y}px"><div class="chip {"tq" if key != "Fleisch" else "pu"} mono" style="font-size:24px;padding:8px 14px">{w_}</div></div>')
# ---- Station 4: Jagd (x 2950–3900) ----
for j, x in enumerate([3000, 3075, 3150, 3225]):
    W_.append(f'<div class="el" {A("p6@gemeinsam", "p8@Arbeit", round(j * 0.08, 2))} data-sfx="none" style="left:{x}px;top:{548 - (j % 2) * 8}px">{fig(INK, 1.0, " M15 22l12 -6")}<div class="spr" style="left:20px;top:-46px"></div></div>')
lake = P("M10 80 q120 -70 300 -40 q160 20 140 70 q-40 50 -230 40 q-230 -10 -210 -70z", 2.4) + "".join(D(f"M{60 + 70 * k} {70 + 12 * (k % 2)} q14 -8 28 0 q14 8 28 0", 1.4) for k in range(5))
wsk(lake, 460, 140, 3290, 580, "p6@Gejagt", -0.2, 1.2)
horses = ""
for j, (hx, hy) in enumerate([(0, 20), (170, 0)]):
    horses += (f'<g transform="translate({hx} {hy})">' + P("M20 70 q50 -26 100 -10 q8 2 12 -14 l14 -30 q12 -6 22 6 l-4 8 l-16 10 q-4 30 -26 34", 2.2) +
               P("M40 66 l-6 50 M58 70 l2 46 M104 70 l-4 46 M118 66 l4 48 M20 70 q-14 8 -14 30", 2.0) + D("M136 22 q-8 10 -10 24", 1.4) + "</g>")
W_.append(f'<div class="el" {A("p6@Gejagt", "p8@Arbeit", -0.1)} data-sfx="none" style="left:3380px;top:410px">{sketch(horses, 360, 140, 0, 0, "p6@Gejagt", -0.1, 1.2)}</div>')
W_.append(f'<div class="el" {A("p6@Speeren", "p8@Arbeit", -0.1)} data-sfx="none" style="left:3250px;top:500px;width:10px;height:10px"><div class="fly" data-fa="p6@Speeren" data-dx="140" data-dy="70" style="position:absolute;left:0;top:0"><div class="spr2"></div></div></div>')
wmk("GEMEINSAM", 3020, 420, "p6@gemeinsam", "p7@ältesten", 0.0)
wmk("SPEERE AUS HOLZ", 3180, 300, "p6@Holz", "p8@Arbeit", 0.0, INK)
wmk("SCHÖNINGEN · NIEDERSACHSEN", 3270, 640, "p7@Niedersachsen", "p8@Arbeit", -0.1, TQ)
# ---- Station 5: Arbeit (x 3900–4300) ----
week = "".join(R(20 + 78 * j, 0, 58, 230, 6, 2.0) for j in range(7))
wsk(week, 580, 280, 3730, 330, "p8@Arbeit", 0.1, 1.0)
for j, dname in enumerate(["MO", "DI", "MI", "DO", "FR", "SA", "SO"]):
    W_.append(f'<div class="el" {A("p8@Arbeit", "p10@Feuer", 0.3)} data-sfx="none" style="left:{3750 + 78 * j}px;top:570px;width:58px;text-align:center"><span class="mono" style="font-size:20px;color:{INK2}">{dname}</span></div>')
    hh = [3.5, 3, 2.5, 3.5, 3, 2.5, 2][j]                  # schematische Verteilung, Summe 20
    W_.append(f'<div class="el" {A("p9@zwanzig", "p10@Feuer", 0)} data-sfx="none" style="left:{3752 + 78 * j}px;top:332px;width:54px;height:226px"><div class="gro" data-ga="p9@zwanzig" data-gd="{0.08 * j:.2f}" style="position:absolute;bottom:0;left:0;width:54px;height:{hh / 8 * 226:.0f}px;border-radius:6px;background:{PUR};opacity:.85;transform-origin:bottom"></div></div>')
W_.append(f'<div class="el" {A("p8@Arbeit", "p9@zwanzig", 0.15)} style="left:3960px;top:360px"><div class="qbig" style="position:static;font-size:170px;line-height:1">?</div></div>')
wmk("SCHEMATISCH · SUMME ≈ 20 STD", 3760, 620, "p9@Woche", "p10@Feuer", 0.2, INK2)
# ---- Station 6: Feuer (x 4300–5000) ----
fire = P("M-70 80 L70 40 M-70 40 L70 80", 4) + C(0, 60, 95, 1.2, INK2)
for a in range(0, 360, 30):
    fire += D(f"M{110 * math.cos(math.radians(a)):.0f} {60 + 40 * math.sin(math.radians(a)):.0f} l{14 * math.cos(math.radians(a)):.0f} {6 * math.sin(math.radians(a)):.0f}", 1.6)
wsk(fire, 0, 0, 4720, 560, "p10@Feuer", -0.3, 0.8)
W_.append(f'<div class="el" {A("p10@Feuer", "end", -0.2)} data-sfx="none" style="left:4650px;top:470px"><div class="flame">'
          f'<svg width="140" height="150" viewBox="0 0 140 150"><path class="f1" d="M70 140 C20 130 20 80 50 50 C55 80 70 70 66 20 C100 50 125 95 100 130 C95 138 85 140 70 140z" fill="{PUR}" fill-opacity=".85" stroke="{INK}" stroke-width="2.4"/>'
          f'<path class="f2" d="M70 138 C48 130 48 104 62 86 C66 102 76 98 74 76 C92 96 98 120 86 132z" fill="#fff" stroke="{INK}" stroke-width="2"/></svg></div></div>')
for j, (x, y) in enumerate([(4510, 560), (4570, 610), (4850, 610), (4910, 560), (4640, 650), (4790, 650)]):
    W_.append(f'<div class="el aa" {A("p10@zusammen", "end", round(j * 0.06, 2))} style="left:{x}px;top:{y - 50}px">{fig(INK, 1.0, " M5 24l10 4 10 -4")}</div>')
for j in range(4):
    W_.append(f'<div class="el" {A("p10@Musik", "p12", 0)} data-sfx="none" style="left:{4760 + 30 * j}px;top:420px"><div class="note" data-na="p10@Musik" data-ni="{j}" style="font-size:44px;color:{PUR};font-weight:700">{"♪♫"[j % 2]}</div></div>')
wmk("MUSIK AM FEUER", 4560, 300, "p10@Musik", "p11@Flöten", 0.1, PUR)

# ---- Spur + Gruppe (Tip) ----
W_.append(f'<svg width="{WW}" height="760" style="position:absolute;left:0;top:0;overflow:visible"><polyline id="trail" points="" fill="none" stroke="{PUR}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 14" vector-effect="non-scaling-stroke"/></svg>')
W_.append('<div id="tip" style="position:absolute;left:0;top:0;opacity:0"><div class="tipring"></div><div class="tipdot"></div></div>')
for j in range(5): W_.append(f'<div class="fol" data-j="{j}" style="position:absolute;left:0;top:0;opacity:0"><div class="fdot"></div></div>')

# ---- Himmel (bildschirmfest) ----
stars = "".join(f'<div class="star" style="left:{(j * 137) % 900 + 10}px;top:{(j * 59) % 230 + 14}px;width:{3 + j % 3}px;height:{3 + j % 3}px"></div>' for j in range(26))
sky = (f'<div id="sky" style="position:absolute;left:0;top:0;width:920px;height:360px">{stars}'
       f'<div id="sun" style="position:absolute;left:0;top:0">{ic(I["sun"], 92, INK, 2.6)}</div>'
       f'<div id="moon" style="position:absolute;left:0;top:0;opacity:0">{ic(I["moon"], 74, "#FFFFFF", 3)}</div></div>')
chips = (el('<div class="chip mono" style="font-size:19px;padding:8px 12px">MENSCHHEITSGESCHICHTE · FOLGE 3</div>', 22, 22, A("p1", "p3", -0.6) + ' data-sfx="none"')
         + f'<div class="el" {A("p2@Tag", "p14@tauschen", 0)} data-sfx="none" style="right:22px;top:22px"><div class="chip mono row" style="font-size:20px;padding:8px 14px;gap:8px"><span id="tod">MORGENS</span></div></div>')
world = f'<div id="world" style="position:absolute;left:0;top:0;width:{WW}px;height:760px;transform-origin:0 0">{"".join(W_)}</div>'
stage.append(mm(sky + world + chips, 80, 460, 920, 760, A("p1", "end", -0.6)))

# ---- Overlays ----
stage.append(el('<div class="stamp mono" style="font-size:54px;color:#7B3FE4;border-color:#7B3FE4">STEINZEIT</div>', 80, 1075, A("p1@Steinzeit", "p2@Tag"), 920, CENTER))
stage.append(el(f'<div class="chip mono" style="font-size:26px;padding:10px 18px;border-color:{TQ};background:rgba(255,255,255,.92)">❄ IN DER EISZEIT</div>', 80, 1100, A("p2@Eiszeit", "p3@Zelt", 0) + ' data-sfx="marker"', 920, CENTER))
stage.append(card(f'<div class="row" style="gap:26px;height:100%">{ic(I["spear"], 84, PUR)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">SCHÖNINGER SPEERE · NIEDERSACHSEN</div><div class="bignum" style="font-size:46px;letter-spacing:-1px">rund 200.000 Jahre alt</div></div></div>', 110, 530, 860, 160, "active", A("p7@ältesten", "p8", 0.1)))
stage.append(card(f'<div class="col" style="gap:14px;align-items:flex-start;height:100%;justify-content:center"><div class="row" style="gap:18px"><div class="bignum" style="font-size:72px;letter-spacing:-2px">≈ {cnt(20, "p9@zwanzig")} Std.</div><div class="mono small grey" style="line-height:1.3">PRO WOCHE<br>JAGEN &amp; SAMMELN</div></div>'
                  f'<div class="hbar"><div class="gbar2" data-ga="p9@zwanzig" style="width:50%;background:{PUR}"></div><span class="mono hlab" style="left:14px;right:auto;color:#fff">JÄGER &amp; SAMMLER</span></div><div class="hbar"><div class="gbar2" data-ga="p9@Woche" style="width:100%;background:#C9CCD3"></div><span class="mono hlab">VOLLZEITJOB HEUTE ≈ 40</span></div><div class="mono row" style="font-size:19px;gap:8px;color:#5D616B">{ic(I["study"], 26, "#5D616B", 3.4)}STUDIE (2019) BEI DEN AGTA, PHILIPPINEN</div></div>', 110, 530, 860, 290, "active", A("p9@zwanzig", "p10", -0.1)))
stage.append(el(f'<div class="chip mono row" style="font-size:22px;gap:10px;background:rgba(255,255,255,.95)">{ic(I["study"], 34, INK, 3.2)}STUDIE: HEUTIGE JÄGER &amp; SAMMLER</div>', 80, 540, A("p9@Studie", "p9@zwanzig", -0.1) + ' data-sfx="marker"', 920, CENTER))
fl = (P("M10 40 L480 26", 14, "#D8D2C6") + P("M10 34 q-6 6 0 14 L480 32 q6 -6 0 -12 z", 2.4) + "".join(C(150 + 70 * k, 33.5 - 2 * k, 6, 2.2) for k in range(4)) + D("M40 34 l12 -2 M300 26 l16 0", 1.2))
stage.append(card(f'<div class="col" style="gap:10px;align-items:flex-start;height:100%;justify-content:center"><div class="mono small grey">FLÖTE AUS GEIERKNOCHEN · HOHLE FELS, SCHWÄBISCHE ALB</div>'
                  f'<div style="position:relative;height:70px;width:500px">{sketch(fl, 500, 70, 0, 0, "p11@Flöten", -0.1, 1.0)}</div><div class="bignum" style="font-size:46px;letter-spacing:-1px">rund 35.000 Jahre alt</div></div>', 110, 530, 860, 260, "active", A("p11@Flöten", "p12", -0.1)))
stage.append(card(f'<div class="row" style="gap:26px;height:100%">{ic(I["heart"], 84, TQ)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">WER DIE KINDHEIT ÜBERSTAND</div><div class="bignum" style="font-size:66px;letter-spacing:-2px">{cnt(60, "p12@Kindheit", 0, 0.1)}–{cnt(70, "p12@Kindheit", 0, 0.3)} Jahre</div></div></div>', 110, 530, 860, 170, "activeTQ", A("p12@Kindheit", "p13", 0)))
stage.append(el(f'<div class="chip mono" style="font-size:20px;padding:8px 14px;color:#8A8F99;border-color:#C9CCD3;background:rgba(255,255,255,.95)">DATEN: HEUTIGE JÄGER &amp; SAMMLER</div>', 80, 1120, A("p12@sechzig", "p13", 0.3) + ' data-sfx="none"', 920, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:56px">LEICHT? NEIN.</div>', 80, 560, A("p13@Leicht", "p14"), 920, CENTER))
# p14 Frage (Roboter winkt), Panorama zoomt auf den ganzen Tag raus
stage.append(card(f'<div class="row" style="gap:30px;height:100%;justify-content:center">{ic(I["sun"],120,PUR)}<div class="qbig" style="position:static;font-size:150px;line-height:1">?</div></div>', 260, 520, 560, 240, "active", A("p14@Würdest", "end")))
stage.append(el('<div class="row" style="gap:24px;justify-content:center"><div class="chip tq mono" style="font-size:40px;padding:14px 34px">JA</div><div class="chip mono" style="font-size:40px;padding:14px 34px">NEIN</div></div>', 260, 790, f'{A("p14@ja", "end")} data-sfx="plop"', 560))
stage.append(el('<div class="chip pu mono" style="font-size:22px">SCHREIB\'S IN DIE KOMMENTARE</div>', 260, 900, f'{A("p14@nein", "end", 0.2)} data-sfx="plop"', 560, CENTER))
stage.append(el(f'<div class="chip mono" style="font-size:20px;padding:8px 14px;color:#8A8F99;border-color:#C9CCD3">DEIN TAG IN DER STEINZEIT</div>', 80, 1160, A("p14@tauschen", "end", 0.4) + ' data-sfx="none"', 920, CENTER))

cam = [("p1", 0, 470, 1.12, 380), ("p2", 0, 470, 1.0, 380), ("p4@zieht", 0, 470, 1, 380), ("p4@hinterher", 0.5, 1390, 1, 380),
       ("p5@Gegessen", -0.1, 1390, 1, 380), ("p5@hergibt", 0.1, 2330, 1, 380), ("p6", -0.15, 2330, 1, 380), ("p6@gemeinsam", 0.25, 3240, 1, 380),
       ("p7@ältesten", 0, 3240, 1, 380), ("p7@gefunden", 0.2, 3440, 1.08, 380), ("p8", 0, 3440, 1.08, 380), ("p8@Arbeit", 0.35, 4010, 1, 380),
       ("p10", -0.2, 4010, 1, 380), ("p10@Feuer", 0.1, 4720, 1, 380), ("p11", 0, 4720, 1, 380), ("p12", 0, 4720, 1.06, 400),
       ("p14", -0.1, 4720, 1.0, 380), ("p14@tauschen", 0.2, 2500, 0.184, 610)]
tipk = [("p4@zieht", 0, 470), ("p4@hinterher", 0.3, 1320), ("p5@Gegessen", 0, 1320), ("p5@hergibt", 0.1, 2200), ("p6", -0.1, 2200),
        ("p6@gemeinsam", 0, 2900), ("p8@Arbeit", -0.1, 2920), ("p8@Arbeit", 0.5, 3660), ("p10", -0.1, 3660), ("p10@Feuer", 0.2, 4460)]
PANJS = dict(cam=cam, tip=tipk, gy=[640, 10, 210])


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
.card{{background:rgba(255,255,255,.93)}}
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
 // ---- Panorama: Ein Tag in der Steinzeit ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const ks=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],z:k[3],fy:k[4]}}));
  function base(tt){{ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){{ const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){{ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e),fy:k0.fy+(k1.fy-k0.fy)*e}}; }} }} return ks[ks.length-1]; }}
  const bs=base(t);
  document.getElementById('world').style.transform=`translate(460px,${{bs.fy}}px) scale(${{bs.z}}) translate(${{-bs.x}}px,-380px)`;
  const tk=PAN.tip.map(k=>({{t:TS(k[0],k[1]),x:k[2]}}));
  function tipx(tt){{ if(tt<=tk[0].t) return tk[0].x; for(let i=0;i<tk.length-1;i++){{ const a=tk[i],c=tk[i+1]; if(tt>=a.t&&tt<c.t){{ const u=(tt-a.t)/Math.max(1e-6,c.t-a.t); return a.x+(c.x-a.x)*u*u*(3-2*u); }} }} return tk[tk.length-1].x; }}
  const gy=x=>PAN.gy[0]+PAN.gy[1]*Math.sin(x/PAN.gy[2]);
  const t0=tk[0].t, on=ease(pr(t,t0,0.4)); const tx=tipx(t), mv=Math.abs(tipx(t+0.05)-tx)>0.4;
  const TP=document.getElementById('tip'); TP.style.left=tx+'px'; TP.style.top=(gy(tx)-(mv?Math.abs(Math.sin(t*14))*7:0))+'px'; TP.style.opacity=on;
  const rg=TP.querySelector('.tipring'); const ph=(t%1.1)/1.1; rg.style.transform=`scale(${{0.5+1.1*ph}})`; rg.style.opacity=1-ph;
  document.querySelectorAll('.fol').forEach(f=>{{ const j=+f.dataset.j; const fx=tipx(t-0.12*(j+1))-26*(j+1); f.style.left=fx+'px'; f.style.top=(gy(fx)+(j%2?11:-11)-(mv?Math.abs(Math.sin(t*14+j*1.3))*5:0))+'px'; f.style.opacity=on; }});
  let pts=[]; if(t>=t0){{ for(let x=tk[0].x;x<tx;x+=24) pts.push(x.toFixed(0)+','+gy(x).toFixed(1)); pts.push(tx.toFixed(0)+','+gy(tx).toFixed(1)); }}
  document.getElementById('trail').setAttribute('points',pts.join(' '));
  // Himmel: Sonne wandert von Morgen bis Abend, dann Nacht
  const ta=S['p2'], tb=S['p10@Feuer'], dp=cl((t-ta)/(tb-ta),0,1), nf=ease(pr(t,S['p10'],1.6));
  let sx=60+760*dp, sy=270-200*Math.sin(Math.PI*dp); if(t<ta) sy=330-60*ease(pr(t,0,ta));
  const SU=document.getElementById('sun'); SU.style.left=(sx-46)+'px'; SU.style.top=(sy-46)+'px'; SU.style.opacity=1-nf; SU.style.transform=`rotate(${{t*12}}deg)`;
  const MO=document.getElementById('moon'); MO.style.left='790px'; MO.style.top=(110+40*(1-nf))+'px'; MO.style.opacity=nf;
  const a1=t<ta?0.16:Math.max(0.16*(1-dp/0.15),0.2*cl((dp-0.7)/0.3,0,1),0); const al=a1*(1-nf)+0.8*nf;
  const r=Math.round(123+(20-123)*nf), g=Math.round(63+(22-63)*nf), bb=Math.round(228+(52-228)*nf);
  document.getElementById('sky').style.background=`linear-gradient(rgba(${{r}},${{g}},${{bb}},${{al}}) 0%,rgba(${{r}},${{g}},${{bb}},${{al*0.75}}) 60%,rgba(${{r}},${{g}},${{bb}},0) 100%)`;
  document.querySelectorAll('.star').forEach((s,i)=>s.style.opacity=nf*(0.55+0.45*Math.sin(t*3+i*1.7)));
  document.getElementById('tod').textContent = t>=S['p10'] ? (nf>0.55?'NACHTS':'ABENDS') : dp<0.2?'MORGENS':dp<0.45?'VORMITTAGS':dp<0.6?'MITTAGS':'NACHMITTAGS';
  // Bewegungen in der Welt
  for(const e of document.querySelectorAll('.spin')) e.style.transform=`rotate(${{Math.max(0,t-S[e.dataset.sa])*75}}deg)`;
  for(const e of document.querySelectorAll('.mv')) e.style.transform=`translateX(${{Math.max(0,t-S[e.dataset.ma])*(+e.dataset.vx)}}px)`;
  for(const e of document.querySelectorAll('.fly')){{ const u=pr(t,S[e.dataset.fa]+0.15,0.75), dx=+e.dataset.dx, dy=+e.dataset.dy;
    const x=dx*u, y=dy*u-120*Math.sin(Math.PI*u), ang=Math.atan2(dy-120*Math.PI*Math.cos(Math.PI*u), dx)*180/Math.PI; e.style.transform=`translate(${{x}}px,${{y}}px) rotate(${{ang}}deg)`; }}
  for(const e of document.querySelectorAll('.gro')) e.style.transform=`scaleY(${{ease(pr(t,S[e.dataset.ga]+(+e.dataset.gd),0.6))}})`;
  for(const e of document.querySelectorAll('.gbar2')) e.style.transform=`scaleX(${{ease(pr(t,S[e.dataset.ga],0.9))}})`;
  for(const e of document.querySelectorAll('.note')){{ const i=+e.dataset.ni, q=t-S[e.dataset.na]; if(q<0){{e.style.opacity=0;continue;}} const p2=(q+i*0.55)%2.2; e.style.opacity=Math.sin(Math.PI*p2/2.2); e.style.transform=`translate(${{Math.sin(p2*3+i)*16}}px,${{-p2*75}}px)`; }}
  document.querySelectorAll('.f1').forEach(e=>e.style.transform=`scale(${{1+0.06*Math.sin(t*11)+0.04*Math.sin(t*17.3)}},${{1+0.09*Math.sin(t*13+1)}})`);
  document.querySelectorAll('.f2').forEach(e=>e.style.transform=`scale(${{1+0.08*Math.sin(t*15+2)}},${{1+0.12*Math.sin(t*19)}})`);
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
