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
CH = ["01 AB SONNTAG", "02 WARUM?", "03 REH IM LICHT", "04 NICHT AUSWEICHEN", "05 WENN'S KRACHT", "06 UND DU?"]
B = [
 ("p1", 0, "Ab Sonntag: Feierabend im Dunkeln", "Ab *Sonntag* fährst du nach *Feierabend* direkt in die *Dämmerung* –", "staunt"),
 ("p2", 0, "Genau dann laufen Rehe.", "genau dann, wenn *Rehe* über die *Straße* laufen.", None),
 ("p3", 1, "Schuld: die Zeitumstellung", "Durch die *Zeitumstellung* fällt der *Berufsverkehr* plötzlich in die *Stunde,*", None),
 ("p4", 1, "Dämmerung = Futterzeit", "in der *Wildtiere* *Futter* suchen.", None),
 ("p5", 2, "Reh im Licht? Fernlicht aus!", "Steht ein *Reh* im *Scheinwerferlicht,* schalte das *Fernlicht* *aus.*", None),
 ("p6", 2, "Grelles Licht lähmt.", "Das *grelle* *Licht* *blendet* das Tier, es bleibt wie *erstarrt* stehen.", None),
 ("p7", 2, "Hupen hilft.", "*Hupe* *kräftig,* dann kann es sich am *Geräusch* orientieren und *flüchten.*", None),
 ("p8", 2, "Bremsen – es kommen mehr.", "*Bremse* *kontrolliert* und rechne damit, dass noch *weitere* *Tiere* folgen.", None),
 ("p9", 3, "Nicht ausweichen!", "Und ganz wichtig: *nicht* *ausweichen!*", None),
 ("p10", 3, "Lenkrad fest, Spur halten.", "*Lenkrad* *festhalten,* in der *Spur* bleiben.", None),
 ("p11", 3, "Reh ist das kleinere Übel.", "Der *Aufprall* mit dem Reh ist meist *weniger* *schlimm* als der *Gegenverkehr* oder ein *Baum.*", None),
 ("p12", 4, "Kracht es doch:", "Kracht es doch: *Warnblinker* an, *Unfallstelle* sichern,", None),
 ("p13", 4, "Kracht es doch:", "*Polizei* rufen und das Tier *nicht* *anfassen.*", None),
 ("p14", 5, "Hättest du ausgewichen?", "Ehrlich: Hättest du *ausgewichen?*", "denkt"),
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
 sun='<circle cx="24" cy="24" r="8"/><path d="M24 4v6M24 38v6M4 24h6M38 24h6M10 10l4 4M34 34l4 4M38 10l-4 4M14 34l-4 4"/>',
 moon='<path d="M32 8a17 17 0 1 0 8 26A14 14 0 0 1 32 8z"/>',
 horn='<path d="M6 19h8l14-9v28l-14-9H6z"/><path d="M34 16q5 8 0 16M39 11q9 13 0 26"/>',
 brake='<rect x="12" y="8" width="24" height="32" rx="6"/><path d="M18 16h12M18 24h12M18 32h12"/>',
 wheel='<circle cx="24" cy="24" r="18"/><circle cx="24" cy="24" r="5"/><path d="M6 24h13M29 24h13M24 29v13"/>',
 warn='<path d="M24 6L44 40H4z"/><path d="M24 18v10M24 34v1"/>',
 phone='<path d="M14 6h20v36H14z"/><path d="M21 37h6"/>',
 hand='<path d="M16 40V18a3 3 0 0 1 6 0v10V12a3 3 0 0 1 6 0v16V14a3 3 0 0 1 6 0v18c0 6-4 10-10 10h-2c-4 0-6-2-8-6l-4-8a3 3 0 0 1 5-3l1 3"/>',
)
DEER_ICON = '<path d="M14 22c0-4 18-5 24-1 3 2 2 7-1 8-8 2-17 2-21 0-2-1-3-4-2-7z"/><path d="M16 22l-5-10M11 12c-3 0-6 1-6 3s4 2 7 1M10 11l1-5M18 29v12M22 30v11M34 30v11M37 28v13"/>'
def deer(x, y, s=1.0, c=INK, w=2.4, eyes=False):
    b = (P("M30 70 C30 50 110 48 130 62 C140 70 138 88 128 92 C100 98 50 98 34 90 C28 86 28 78 30 70 Z", w, c)
         + P("M40 66 L24 26 M56 62 L40 22", w, c)
         + P("M18 22 C20 12 40 10 44 20 C46 28 36 32 24 32 L8 36 C2 36 2 28 10 26 Z", w, c)
         + P("M34 14 L42 0 L44 16 M26 16 L24 2 L34 12", w, c)
         + P("M40 92 L36 150 M54 94 L52 150 M112 94 L116 150 M124 90 L128 150", w, c)
         + P("M134 66 l10 -8", w, c))
    if eyes:
        b += f'<circle class="mesh" style="opacity:0" cx="20" cy="22" r="6" fill="{TQ}"/>' + f'<circle class="mesh" style="opacity:0" cx="20" cy="22" r="14" fill="{TQ}" fill-opacity=".25"/>'
    return f'<g transform="translate({x},{y}) scale({s})">{b}</g>'
def car_side(x, y, s=1.0, c=INK, w=2.4):
    b = (P("M10 80 L10 55 C10 48 20 44 40 42 L70 20 C76 14 90 12 110 12 L160 12 C176 12 186 18 196 30 L212 42 C230 44 238 50 238 60 L238 80 Z", w, c)
         + P("M78 40 L98 22 H132 V40 Z M142 40 V22 H170 C178 22 184 28 190 40 Z", w * 0.7, c)
         + C(55, 82, 18, w, c) + C(195, 82, 18, w, c) + R(226, 48, 12, 10, 3, w, PUR))
    return f'<g transform="translate({x},{y}) scale({s})">{b}</g>'
def scene_road():
    cone = "M254 250 L600 150 L600 330 Z"
    o = D("M0 300 H760", 2.4, INK) + D("M40 330 H120 M200 330 H280 M360 330 H440 M520 330 H600 M680 330 H740", 2, INK2)
    o += f'<path class="mesh" style="opacity:0" d="{cone}" fill="{PUR}" fill-opacity=".10"/>' + P("M254 250 L600 150 M254 254 L600 330", 1.6, PUR)
    o += car_side(20, 200) + deer(560, 150)
    o += P("M690 40 a26 26 0 1 0 22 38 a20 20 0 0 1 -22 -38 Z", 2, INK2) + TX(20, 40, "DÄMMERUNG", 22, INK2)
    return o
def scene_graze():
    o = D("M0 300 H760", 2.4, INK)
    o += P("M470 300 A90 90 0 0 1 650 300", 2.6, PUR) + P("M560 190 V170 M490 220 l-14 -14 M630 220 l14 -14 M455 260 h-20 M665 260 h20", 2, PUR)
    o += deer(150, 150, 1.0) + deer(330, 166, 0.9)
    o += P("M60 300 l6 -18 l6 18 M100 300 l5 -14 l5 14 M300 300 l6 -18 l6 18 M700 300 l5 -16 l5 16", 1.8, INK2)
    o += TX(560, 350, "SONNENUNTERGANG", 18, PUR, "JBM", 700, "middle")
    return o
def scene_glare():
    o = D("M0 330 H760", 2.4, INK)
    o += f'<path class="mesh" style="opacity:0" d="M0 60 L420 120 L420 330 L0 330 Z" fill="{PUR}" fill-opacity=".10"/>'
    for yy in (90, 150, 210, 270):
        o += P(f"M30 {yy} L300 {yy + (190 - yy) * 0.25}", 2, PUR)
    o += deer(420, 30, 2.0, eyes=True)
    return o
def scene_top():
    o = D("M0 110 H760 M0 310 H760", 2.6, INK) + D("M20 210 H90 M150 210 H220 M280 210 H350 M410 210 H480 M540 210 H610 M670 210 H740", 2, INK2)
    o += R(70, 236, 150, 60, 14) + R(150, 242, 36, 48, 6, 1.6, INK2) + R(214, 244, 8, 12, 2, 2, PUR) + R(214, 276, 8, 12, 2, 2, PUR)
    o += R(600, 126, 150, 60, 14) + R(626, 132, 36, 48, 6, 1.6, INK2)
    o += C(380, 56, 36) + C(380, 56, 14, 1.6, INK2)
    o += P("M510 266 C510 252 570 252 580 266 C570 280 510 280 510 266 Z") + P("M510 266 L492 260 L488 266 L492 272 Z") + P("M496 262 l-4 -8 M496 270 l-4 8", 1.8)
    o += P("M222 262 C300 262 330 170 370 100", 4, RED) + P("M356 104 L372 96 L374 114", 4, RED)
    o += P("M300 210 C340 180 420 150 520 150", 4, RED) + P("M506 140 L524 150 L508 162", 4, RED)
    return o
def straight_arrow():
    return P("M222 266 H470", 6, TQ) + P("M452 250 L474 266 L452 282", 6, TQ)
def scene_top_ok():
    return scene_top().replace(RED, "#C9CCD3") + straight_arrow()

# p1 hook
stage.append(card(f'<div class="col" style="gap:8px;height:100%;justify-content:center"><div class="mono small grey">DEIN FEIERABEND AB 25.10.</div><div class="huge" style="font-size:170px">17 Uhr</div><div class="mono small" style="color:#7B3FE4">= SCHON DÄMMERUNG</div></div>', 80, 470, 920, 290, "active", A("p1","p2")))
for i, (lab, key) in enumerate([("SONNTAG", "p1@Sonntag"), ("FEIERABEND", "p1@Feierabend"), ("DÄMMERUNG", "p1@Dämmerung")]):
    stage.append(el(f'<div class="chip mono" style="font-size:30px">{lab}</div>', 440, 850 + i * 110, f'{A(key, "p2")} data-sfx="plop"', 560, "display:flex;justify-content:center"))
# p2 deer on road
stage.append(mm(sketch(scene_road(), 760, 380, 80, 40, "p2", 0, 1.6, 1.0) + mk("REH", 600, 420, "p2@Rehe", 0, PUR) + mk("STRASSE", 60, 420, "p2@Straße", 0, INK), 80, 470, 920, 470, A("p2","p3")))
stage.append(el('<div class="mono small grey" style="text-align:center">SKIZZE · NICHT MASSSTÄBLICH</div>', 80, 970, A("p2","p3",0.4), 920))
# p3 time change
stage.append(card(f'<div class="col" style="gap:10px;height:100%;justify-content:center">{ic(I["sun"],90,"#8A8F99")}<div class="mono small grey">17 UHR · BIS SAMSTAG</div><div class="bignum" style="font-size:64px;color:#8A8F99">hell</div></div>', 80, 470, 450, 380, "", A("p3@Zeitumstellung","p4")))
stage.append(card(f'<div class="col" style="gap:10px;height:100%;justify-content:center">{ic(I["moon"],90,PUR)}<div class="mono small" style="color:#7B3FE4">17 UHR · AB SONNTAG</div><div class="bignum" style="font-size:64px">dämmrig</div></div>', 550, 470, 450, 380, "active", A("p3@Zeitumstellung","p4",0.35)))
stage.append(el(f'<div class="chip pu mono" style="font-size:30px;display:flex;align-items:center;gap:14px">{ic(I["clock"],40,PUR)}UHR 1 STUNDE ZURÜCK</div>', 80, 900, f'{A("p3@Berufsverkehr","p4")} data-sfx="plop"', 920, "display:flex;justify-content:center"))
stage.append(el('<div class="chip mono" style="font-size:30px">BERUFSVERKEHR = DÄMMERUNG</div>', 80, 1020, f'{A("p3@Stunde","p4")} data-sfx="plop"', 920, "display:flex;justify-content:center"))
# p4 feeding time
stage.append(mm(sketch(scene_graze(), 760, 380, 80, 40, "p4", 0, 1.6, 1.0) + mk("FUTTERSUCHE", 60, 420, "p4@Futter", 0, PUR), 80, 470, 920, 470, A("p4","p5")))
stage.append(el('<div class="chip tq mono" style="font-size:30px">WILDTIERE: AKTIV IN DER DÄMMERUNG</div>', 80, 990, A("p4@Wildtiere","p5",0.3), 920, "display:flex;justify-content:center"))
# p5 high beam off
stage.append(mm(sketch(scene_road(), 760, 380, 80, 40, "p5", 0, 1.2, 1.0) + mk("FERNLICHT", 300, 420, "p5@Fernlicht", 0, PUR), 80, 470, 920, 470, A("p5","p6")))
stage.append(el('<div class="stamp mono" style="font-size:56px">FERNLICHT AUS</div>', 80, 990, A("p5@aus","p6"), 920, "display:flex;justify-content:center"))
# p6 glare -> frozen
stage.append(mm(sketch(scene_glare(), 760, 380, 80, 40, "p6", 0, 1.4, 1.0) + mk("GEBLENDET", 60, 420, "p6@blendet", 0, PUR), 80, 470, 920, 470, A("p6","p7")))
stage.append(el('<div class="stamp mono" style="font-size:56px;color:#7B3FE4;border-color:#7B3FE4">ERSTARRT</div>', 80, 990, A("p6@erstarrt","p7"), 920, "display:flex;justify-content:center"))
# p7 horn
stage.append(card(f'<div class="row" style="gap:30px;height:100%">{ic(I["horn"],120,PUR,2.8)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">KRÄFTIG</div><div class="bignum" style="font-size:96px">Hupen</div></div></div>', 80, 470, 920, 300, "active", f'{A("p7","p8")} data-wob="1"'))
stage.append(card(f'<div class="row" style="gap:26px;height:100%"><svg width="110" height="110" viewBox="0 0 48 48" fill="none" stroke="#0B0B10" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">{DEER_ICON}</svg><div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">GERÄUSCH = ORIENTIERUNG</div><div class="rowtitle" style="font-size:44px;margin:0">Reh flüchtet</div></div></div>', 80, 820, 920, 230, "activeTQ", A("p7@Geräusch","p8")))
stage.append(el('<div class="okc">✓</div>', 880, 790, A("p7@flüchten","p8"), None))
# p8 brake + more animals
stage.append(card(f'<div class="row" style="gap:30px;height:100%">{ic(I["brake"],110,"#0B0B10",2.8)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">KONTROLLIERT</div><div class="bignum" style="font-size:90px">Bremsen</div></div></div>', 80, 470, 920, 280, "active", A("p8","p9")))
for i, key in enumerate(["p8@weitere", "p8@weitere", "p8@Tiere"]):
    stage.append(el(f'<svg width="200" height="200" viewBox="0 0 48 48" fill="none" stroke="#0B0B10" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{DEER_ICON}</svg>', 120 + i * 290, 800, f'{A(key,"p9",0.15*i)} data-sfx="plop"'))
stage.append(el('<div class="chip pu mono" style="font-size:30px">MEIST KOMMEN NOCH MEHR</div>', 80, 1030, A("p8@folgen","p9"), 920, "display:flex;justify-content:center"))
# p9 no swerve
stage.append(mm(sketch(scene_top(), 760, 380, 80, 40, "p9", 0, 1.4, 1.0) + mk("BAUM", 300, 24, "p9@ausweichen", 0.2, RED) + mk("GEGENVERKEHR", 600, 24, "p9@ausweichen", 0.4, RED), 80, 470, 920, 470, A("p9","p10")))
stage.append(el('<div class="stamp mono" style="font-size:60px">NICHT AUSWEICHEN</div>', 80, 990, A("p9@ausweichen","p10"), 920, "display:flex;justify-content:center"))
# p10 hold lane
stage.append(mm(sketch(scene_top_ok(), 760, 380, 80, 40, "p10", 0, 0.8, 1.0) + mk("IN DER SPUR", 60, 420, "p10@Spur", 0, TQ), 80, 470, 920, 470, A("p10","p11")))
stage.append(el(f'<div class="chip tq mono" style="font-size:30px;display:flex;align-items:center;gap:14px">{ic(I["wheel"],44,"#0E8C80")}LENKRAD FESTHALTEN</div>', 80, 990, f'{A("p10@festhalten","p11")} data-sfx="plop"', 920, "display:flex;justify-content:center"))
# p11 comparison
stage.append(card(f'<div class="col" style="gap:12px;height:100%;justify-content:center"><svg width="130" height="130" viewBox="0 0 48 48" fill="none" stroke="#0E8C80" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{DEER_ICON}</svg><div class="mono small grey">AUFPRALL REH</div><div class="rowtitle" style="font-size:40px;margin:0;color:#0E8C80;text-align:center">meist weniger schlimm</div></div>', 80, 470, 450, 440, "activeTQ", A("p11@Aufprall","p12")))
stage.append(card(f'<div class="col" style="gap:12px;height:100%;justify-content:center">{ic(I["warn"],130,RED,2.4)}<div class="mono small grey">GEGENVERKEHR · BAUM</div><div class="rowtitle" style="font-size:40px;margin:0;color:#E5484D;text-align:center">oft viel gefährlicher</div></div>', 550, 470, 450, 440, "", A("p11@Gegenverkehr","p12")))
stage.append(el('<div class="chip pu mono" style="font-size:30px">LIEBER BREMSEN ALS AUSWEICHEN</div>', 80, 970, A("p11@Baum","p12",0.2), 920, "display:flex;justify-content:center"))
# p12+p13 after crash
stage.append(card('<div class="mono small grey">NACH EINEM WILDUNFALL</div>', 80, 470, 920, 600, "active", A("p12","p14")))
rows = [("WARNBLINKER AN", "✓", "p12@Warnblinker", TQ), ("UNFALLSTELLE SICHERN", "✓", "p12@Unfallstelle", TQ), ("POLIZEI RUFEN · 110", "✓", "p13@Polizei", TQ), ("TIER ANFASSEN", "✕", "p13@anfassen", RED)]
for i, (lab, sym, key, col) in enumerate(rows):
    bg = "rgba(25,198,180,.10)" if col == TQ else "rgba(229,72,77,.08)"
    tc = "#0E8C80" if col == TQ else RED
    stage.append(el(f'<div class="rline" style="font-size:34px;background:{bg};outline:2px solid {col}"><span class="mono">{lab}</span><span class="mono" style="color:{tc};font-size:40px">{sym}</span></div>', 120, 560 + i * 120, A(key, "p14"), 840))
stage.append(el('<div class="mono small grey" style="text-align:center">POLIZEI STELLT WILDUNFALLBESCHEINIGUNG AUS</div>', 80, 1100, A("p13@anfassen","p14",0.4), 920))
# p14 question
stage.append(card('<div class="col" style="gap:14px;height:100%;justify-content:center"><div class="mono small grey">EHRLICH</div><div class="bignum" style="font-size:66px;letter-spacing:-2px;text-align:center">Hättest du<br>ausgewichen?</div></div>', 80, 470, 920, 340, "active", A("p14","end")))
stage.append(el('<div class="chip mono" style="font-size:34px">JA</div>', 440, 870, f'{A("p14@ausgewichen","end")} data-sfx="plop"', 260, "display:flex;justify-content:center"))
stage.append(el('<div class="chip pu mono" style="font-size:34px">NEIN</div>', 740, 870, f'{A("p14@ausgewichen","end",0.2)} data-sfx="plop"', 260, "display:flex;justify-content:center"))
stage.append(el('<div class="mono small grey" style="text-align:center">SCHREIB\'S IN DIE KOMMENTARE</div>', 440, 990, A("p14@ausgewichen","end",0.4), 560))

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
