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
CH = ["01 DIE FRAGE", "02 VORBEREITEN", "03 EINLENKEN", "04 GERADE", "05 GEGENLENKEN"]
B = [
 ("p1", 0, "Parallel einparken?", "*Parallel* *einparken* und du *schwitzt* jedes *Mal?*", "staunt"),
 ("p2", 0, "5 Schritte zum Merken", "Merk dir diese *fünf* *Schritte.*", None),
 ("p3", 1, "Schritt 1: Lücke prüfen", "*Erstens:* Passt dein *Auto* in *ganzer* *Länge* neben die *Lücke,* dann passt es auch *hinein.*", None),
 ("p4", 1, "Schritt 2: Daneben halten", "*Zweitens:* Halte *parallel* neben dem *Vordermann,* etwa *fünfzig* *Zentimeter* *Abstand,*", None),
 ("p5", 1, "Schritt 2: Spiegel runter", "und kipp den *rechten* *Spiegel* nach *unten* zum *Bordstein.*", None),
 ("p6", 2, "Schritt 3: Rad auf Höhe Heck", "*Drittens:* Rolle *langsam* *zurück,* bis dein *Hinterrad* auf *Höhe* seines *Hecks* ist.", None),
 ("p7", 2, "Schritt 3: Voll nach rechts", "Jetzt das *Lenkrad* *voll* nach *rechts.*", None),
 ("p8", 3, "Schritt 4: Bei 45 Grad gerade", "*Viertens:* Steht dein Auto etwa *fünfundvierzig* *Grad* *schräg,* *Lenkrad* *gerade* und weiter *zurück* –", None),
 ("p9", 3, "Schritt 4: Spiegel trifft Heck", "bis dein *rechter* *Spiegel* auf einer *Linie* mit seinem *Heck* ist.", None),
 ("p10", 4, "Schritt 5: Voll nach links", "*Fünftens:* *voll* nach *links* *gegenlenken,* bis du *parallel* stehst.", None),
 ("p11", 4, "Immer: umschauen!", "Und *immer* gilt: *umschauen* und nur *lenken,* während das *Auto* *rollt.*", "winkt"),
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

# ---------- sketches ----------
CURB = 372
def parked(x, lab=""):
    o = mesh(f"M{x} 307 h150 v60 h-150 Z", 760, 420) + R(x, 307, 150, 60, 14, 2.4) + P(f"M{x+100} 312 L{x+112} 337 L{x+100} 362", 1.8, INK2) + P(f"M{x+30} 314 V360", 1.6, INK2)
    if lab: o += TX(x+75, 300, lab, 16, INK2, "JBM", 700, "middle")
    return o
def street():
    o = P(f"M0 {CURB} H760", 3)
    for x in range(10, 760, 34): o += D(f"M{x} {CURB+6} L{x-14} {CURB+30}", 1.4, INK2)
    for x in range(20, 760, 70): o += D(f"M{x} 150 H{x+34}", 2, INK2)
    o += parked(20, "HINTERMANN") + parked(395, "VORDERMANN") + parked(570)
    o += TX(740, CURB+50, "BORDSTEIN", 16, INK2, "JBM", 700, "end")
    return o
def ghost():
    return (f'<rect class="mesh" style="opacity:0" x="200" y="220" width="150" height="60" rx="14" fill="rgba(123,63,228,.08)" stroke="{PUR}" stroke-width="3" stroke-dasharray="10 7"/>'
            + P("M170 400 V390 M170 395 H395 M395 390 V400", 2, PUR) + TX(282, 412, "LÜCKE", 16, PUR, "JBM", 700, "middle"))
def gap50():
    return P("M560 283 V307", 3, TQ) + P("M552 283 H568 M552 307 H568", 2, TQ) + TX(574, 300, "≈ 50 CM", 18, "#0E8C80", "JBM", 700, "start")
def hecklinie():
    return f'<line class="mesh" style="opacity:0" x1="395" y1="110" x2="395" y2="{CURB}" stroke="{PUR}" stroke-width="2.4" stroke-dasharray="8 7"/>'
def angle45():
    return P("M590 230 H680", 2.4) + P("M590 230 L654 166", 2.4, PUR) + P("M640 230 A50 50 0 0 0 625 195", 2.2, PUR) + TX(690, 210, "45°", 26, PUR, "JBM", 700, "start")
def car_svg():
    body = ('<rect x="-75" y="-30" width="150" height="60" rx="16" fill="#F5F0FF" stroke="#7B3FE4" stroke-width="3.2"/>'
            '<path d="M18 -24 L36 -20 L36 20 L18 24 Z" fill="#DCCBFF" stroke="#7B3FE4" stroke-width="2"/>'
            '<path d="M-52 -20 L-42 -22 L-42 22 L-52 20 Z" fill="#DCCBFF" stroke="#7B3FE4" stroke-width="2"/>'
            '<rect x="20" y="-38" width="10" height="9" rx="3" fill="#7B3FE4"/><rect x="20" y="29" width="10" height="9" rx="3" fill="#19C6B4"/>'
            '<rect x="-60" y="-34" width="22" height="7" rx="3" fill="#0B0B10"/><rect x="-60" y="27" width="22" height="7" rx="3" fill="#0B0B10"/>'
            '<rect x="40" y="-34" width="22" height="7" rx="3" fill="#0B0B10"/><rect x="40" y="27" width="22" height="7" rx="3" fill="#0B0B10"/>')
    return body
import json as _j
def KF(*k): return _j.dumps(k).replace('"', '&quot;')
CAR_KF = KF(["p4",0,140,253,0], ["p4@Vordermann",0.3,470,253,0,"io"],
            ["p6@langsam",0,470,253,0], ["p6@Hecks",0,445,253,0,"io"],
            ["p7@rechts",0.15,445,253,0], ["p8@Viertens",0,417,256,-22,"i"], ["p8@fünfundvierzig",0,380,258,-45,"o"],
            ["p8@weiter",0,380,258,-45], ["p9@Heck",0,347,287,-45,"io"],
            ["p10@gegenlenken",0,347,287,-45], ["p10@parallel",0,312,322,-18,"i"], ["p10@stehst",0.2,285,337,0,"o"])
WHEEL_KF = KF(["p7@voll",0,70,70,0], ["p7@rechts",0.5,70,70,540,"io"], ["p8@Lenkrad",0,70,70,540], ["p8@gerade",0.3,70,70,0,"io"],
              ["p10@voll",0,70,70,0], ["p10@gegenlenken",0.3,70,70,-540,"io"], ["p10@stehst",0,70,70,-540], ["p11",0.3,70,70,0,"io"])
WHEEL = (f'<svg width="140" height="140" viewBox="0 0 140 140"><g data-kf="{WHEEL_KF}">'
         '<circle r="56" fill="none" stroke="#0B0B10" stroke-width="10"/><circle r="14" fill="#0B0B10"/>'
         '<path d="M-14 0 H-52 M14 0 H52 M0 14 V52" stroke="#0B0B10" stroke-width="9" stroke-linecap="round"/>'
         '<rect x="-7" y="-62" width="14" height="14" rx="3" fill="#7B3FE4"/></g></svg>')
def step(n, main, sub, x=80, w=920, col=PUR):
    return (f'<div class="row" style="gap:28px;height:100%;width:100%"><div style="width:96px;height:96px;flex:none;border-radius:50%;background:{col};color:#fff;'
            f'font-family:Unbounded;font-weight:600;font-size:52px;display:flex;align-items:center;justify-content:center">{n}</div>'
            f'<div class="col" style="align-items:flex-start;gap:8px"><span class="mono small grey">SCHRITT {n}</span><span class="mono" style="font-size:31px;font-weight:700">{main}</span>'
            f'<span class="mono small grey">{sub}</span></div></div>')
hook_scene = street() + f'<g transform="translate(330 262) rotate(-32)">{car_svg()}</g>' + TX(560, 215, "?", 90, RED, "Unbounded", 600, "middle")

def mk2(text, x, y, anchor, out, d=0, col="#7B3FE4"):
    return (f'<div class="el mk" {A(anchor,out,d)} style="left:{x}px;top:{y}px"><span class="mkbox" style="border-color:{col}"></span>'
            f'<span class="mono" style="color:{col}">{text}</span></div>')
def sketch2(body, x, y, anchor, d=0, dur=1.6, scale=1.15):
    return (f'<svg class="sketch" data-sin="{anchor}" data-sd="{d}" data-sdur="{dur}" width="{760*scale:.0f}" height="{320*scale:.0f}" viewBox="0 100 760 320" '
            f'style="position:absolute;left:{x}px;top:{y}px;overflow:visible">{body}</svg>')
def wrap(inner, i, o): return f'<div class="el" {A(i,o)} data-sfx="none" style="left:0;top:0;width:920px;height:450px">{inner}</div>'
SX, SY = 23, 50
# ---------- scenes ----------
# p1 hook
stage.append(mm(sketch2(hook_scene, 118, 20, "p1", 0, 1.0, 0.9) + mk("SCHEMATISCH", 640, 22, "p1", 0.4, INK2), 80, 470, 920, 330, A("p1","p2")))
stage.append(el('<div class="chip mono" style="font-size:30px;border-color:#E5484D;color:#E5484D">ZU WEIT? ZU SCHRÄG?</div>', 440, 860, f'{A("p1@schwitzt","p2")} data-sfx="plop"', 560, "display:flex;justify-content:center"))
stage.append(el('<div class="chip mono" style="font-size:30px">BORDSTEIN GERAMMT?</div>', 440, 970, f'{A("p1@Mal","p2")} data-sfx="plop"', 560, "display:flex;justify-content:center"))
# p2
stage.append(card('<div class="col" style="gap:10px;height:100%;justify-content:center"><div class="huge" style="font-size:200px;color:#7B3FE4">5</div><div class="mono" style="font-size:34px">SCHRITTE ZUM MERKEN</div></div>', 80, 470, 920, 400, "active", A("p2","p3")))
for i in range(5):
    stage.append(el(f'<div style="width:110px;height:110px;border-radius:50%;border:3px solid #7B3FE4;background:rgba(123,63,228,.08);font-family:Unbounded;font-weight:600;font-size:52px;color:#7B3FE4;display:flex;align-items:center;justify-content:center">{i+1}</div>',
                    105+i*180, 920, f'{A("p2@Schritte","p3",i*0.09)} data-sfx="plop"'))
# p3-p10 scene panel
stage.append(mm(sketch2(street(), SX, SY, "p3", 0, 1.4)
  + wrap(sketch2(ghost(), SX, SY, "p3@Länge", 0, 0.8), "p3@Länge", "p4")
  + wrap(sketch2(gap50(), SX, SY, "p4@fünfzig", 0, 0.6), "p4@fünfzig", "p6")
  + sketch2(hecklinie(), SX, SY, "p6@Hinterrad", 0, 0.4)
  + wrap(sketch2(angle45(), SX, SY, "p8@fünfundvierzig", 0, 0.8), "p8@fünfundvierzig", "p10")
  + f'<div class="el" {A("p4","p11")} data-sfx="none" style="left:{SX}px;top:{SY}px"><svg width="874" height="368" viewBox="0 100 760 320" style="overflow:visible"><g data-kf="{CAR_KF}">{car_svg()}</g></svg></div>'
  + mk2("PASST DANEBEN = PASST REIN", 40, 26, "p3@hinein", "p4", 0, PUR)
  + mk("SCHEMATISCH", 720, 26, "p3", 0.6, INK2)
  + mk2("HINTERRAD = SEIN HECK", 40, 26, "p6@Hecks", "p7", 0, PUR)
  + mk2("SPIEGEL = HECK", 40, 26, "p9@Heck", "p10", 0, PUR)
  + mk("PARALLEL ✓", 40, 26, "p10@parallel", 0, TQ), 80, 470, 920, 450, A("p3","p11")))
# step cards
stage.append(card(step(1, "PASST ES IN GANZER LÄNGE DANEBEN?", "DANN PASST ES AUCH HINEIN"), 80, 960, 920, 220, "active", A("p3@Erstens","p4")))
stage.append(card(step(2, "PARALLEL NEBEN DEN VORDERMANN", "≈ 50 CM SEITLICHER ABSTAND"), 80, 960, 920, 220, "active", A("p4@Zweitens","p5")))
stage.append(card(step(2, "RECHTEN SPIEGEL RUNTERKIPPEN", "SO SIEHST DU DEN BORDSTEIN"), 80, 960, 920, 220, "active", A("p5@rechten","p6")))
stage.append(card(step(3, "HINTERRAD AUF HÖHE HECK", "LANGSAM ZURÜCKROLLEN"), 80, 960, 740, 220, "active", A("p6@Drittens","p7")))
stage.append(card(step(3, "LENKRAD VOLL RECHTS", "UND WEITER ZURÜCK"), 80, 960, 740, 220, "active", A("p7@Lenkrad","p8")))
stage.append(card(step(4, "BEI ≈ 45 GRAD: GERADE", "LENKRAD ZURÜCK IN MITTE"), 80, 960, 740, 220, "active", A("p8@Viertens","p9")))
stage.append(card(step(4, "BIS SPIEGEL = SEIN HECK", "GERADE ZURÜCKROLLEN"), 80, 960, 740, 220, "active", A("p9@Spiegel","p10")))
stage.append(card(step(5, "VOLL LINKS GEGENLENKEN", "BIS DU PARALLEL STEHST", col=TQ), 80, 960, 740, 220, "activeTQ", A("p10@Fünftens","p11")))
for lab,i,o in [("VOLL RECHTS","p7@voll","p8@gerade"),("GERADE","p8@gerade","p10@voll"),("VOLL LINKS","p10@voll","p11")]:
    stage.append(el(f'<div class="mono" style="font-size:20px;font-weight:700;color:#7B3FE4;text-align:center;white-space:nowrap">{lab}</div>', 830, 1150, f'{A(i,o)} data-sfx="none"', 180))
stage.append(el(WHEEL, 850, 990, f'{A("p6@Drittens","p11")} data-sfx="pop"'))
# p11
stage.append(card('<div class="col" style="gap:12px;height:100%;justify-content:center"><div class="mono small grey">IMMER GILT</div><div class="rowtitle" style="font-size:60px;margin:0">Umschauen!</div><div class="mono" style="font-size:30px">SCHULTERBLICK · SPIEGEL · HECKSCHEIBE</div></div>', 80, 470, 920, 330, "active", A("p11","end")))
stage.append(el('<div class="chip pu mono" style="font-size:30px">NUR IM ROLLEN LENKEN</div>', 440, 860, f'{A("p11@lenken","end")} data-sfx="plop"', 560, "display:flex;justify-content:center"))
stage.append(el('<div class="chip mono" style="font-size:30px">NICHT IM STAND KURBELN</div>', 440, 970, f'{A("p11@rollt","end")} data-sfx="plop"', 560, "display:flex;justify-content:center"))

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
