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
HOOK = 'Freitag, der <span style="color:#7B3FE4">13.</span> – wirklich ein Pechtag?'
B = [
 ("s1", 0, HOOK, "Heute ist *Freitag,* der *Dreizehnte.*", "staunt"),
 ("s2", 0, HOOK, "Passieren heute wirklich *mehr* *Schäden* als sonst?", None),
 ("s3", 0, HOOK, "Die *Statistik* dazu verrate ich dir am *Ende.*", None),
 ("s4", 1, "", "Woher kommt die *Angst* vor der *Dreizehn?*", None),
 ("s5", 1, "", "Die *Zwölf* davor gilt als *vollständig:*", None),
 ("s6", 1, "", "*zwölf* *Monate,* *zwölf* *Stunden* auf der *Uhr.*", None),
 ("s7", 1, "", "Die *Dreizehn* ist *eins* *zu* *viel.*", None),
 ("s9", 2, "", "Beim letzten *Abendmahl* saßen *dreizehn* *Männer* am *Tisch:*", None),
 ("s10", 2, "", "*Jesus* und seine *zwölf* *Jünger.*", None),
 ("s11", 2, "", "Einer davon, *Judas,* *verriet* ihn.", None),
 ("s12", 2, "", "Und an einem *Freitag* wurde Jesus *gekreuzigt.*", None),
 ("s13", 3, "", "*Beides* *zusammen,* *Freitag* und *Dreizehn,* gilt aber erst seit dem *neunzehnten* *Jahrhundert* als *Pechtag.*", None),
 ("s16", 4, "", "Eine große deutsche *Versicherung* hat *zwanzig* *Jahre* lang *Schäden* an *Autos* und *Häusern* ausgewertet.", None),
 ("s17", 4, "", "An einem *Freitag,* dem *Dreizehnten,* meldeten ihre Kunden sogar rund *sechs* *Prozent* *weniger* *Schäden* als an anderen *Freitagen.*", None),
 ("s18", 5, "", "Also: *kein* *Pechtag.*", None),
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


# ================= Bühne "Pech-Zeitstrahl" (durchgehendes Panorama, Kamerafahrt, schwarze Katze als Hauptdarsteller) =================
import math
CENTER = "display:flex;justify-content:center"
WW = 5900; FY = 400
W_ = []
def wel(inner, x, y, attrs, style=""): W_.append(el(inner, x, y, attrs, None, style))
def wsk(*a, **k): W_.append(sketch(*a, **k))
def wmk(text, x, y, i, o, d=0.1, col=PUR):
    W_.append(f'<div class="el mk" {A(i, o, d)} style="left:{x}px;top:{y}px;gap:10px"><span class="pin" style="background:{col}"></span><span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div>')
def calsheet(head, body, w=190, h=170, hs=22, bs=92, col="#0B0B10", hcol=PUR):
    return (f'<div class="cal" style="width:{w}px;height:{h}px"><div class="calh mono" style="font-size:{hs}px;background:{hcol}">{head}</div>'
            f'<div class="calb" style="font-size:{bs}px;color:{col};line-height:{(h-hs-16)}px">{body}</div></div>')

# Boden-Linie (Weg der Katze)
W_.append(f'<svg width="{WW}" height="800" style="position:absolute;left:0;top:0;overflow:visible">'
          f'<line x1="0" y1="742" x2="{WW}" y2="742" stroke="{INK2}" stroke-width="2" stroke-dasharray="6 8"/></svg>')

# ---- Station 1: Hook (x 100–1100) ----
wel(f'<div id="bigcal">{calsheet("FREITAG", "13", 400, 430, 44, 250, PUR, INK)}</div>', 420, 60, A("s1", "s4", -0.6) + ' data-sfx="none"')
wel('<div class="chip mono" style="font-size:30px;padding:10px 20px;font-weight:700;background:#fff">13. NOVEMBER 2026</div>', 470, 520, A("s1@Dreizehnte", "s4", -0.1))
wel('<div class="qbig" style="position:static;font-size:200px;line-height:1">?</div>', 860, 70, A("s2@mehr", "s4", -0.1))
wel(f'<div class="chip mono" style="font-size:30px;padding:10px 18px;font-weight:700;border-color:{RED};color:{RED};background:#fff">MEHR SCHÄDEN?</div>', 780, 330, A("s2@Schäden", "s4", -0.1))
wmk("STATISTIK → AM ENDE", 470, 625, "s3@Statistik", "s4", 0.0)

# ---- Station 2: Zwölf vs. Dreizehn (x 1250–2250) ----
wel(f'<div class="num" style="font-size:300px;color:{PUR}">13</div>', 1530, 90, A("s4@Dreizehn", "s5", -0.2))
wel('<div class="qbig" style="position:static;font-size:200px;line-height:1">?</div>', 1990, 150, A("s4@Angst", "s5", 0))
ticks = "".join(f'<line x1="0" y1="-150" x2="0" y2="-128" stroke="{INK}" stroke-width="{7 if k % 3 == 0 else 4}" stroke-linecap="round" transform="rotate({k * 30})"/>' for k in range(12))
nums = "".join(f'<text x="{112 * math.sin(math.radians(k * 30)):.1f}" y="{-112 * math.cos(math.radians(k * 30)) + 11:.1f}" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="30" fill="{INK}">{k if k else 12}</text>' for k in range(12))
clock = (f'<svg width="330" height="330" viewBox="-165 -165 330 330"><circle r="160" fill="#fff" stroke="{INK}" stroke-width="5"/>{ticks}{nums}'
         f'<line id="hh" x1="0" y1="12" x2="0" y2="-70" stroke="{INK}" stroke-width="11" stroke-linecap="round"/>'
         f'<line id="mh" x1="0" y1="16" x2="0" y2="-110" stroke="{PUR}" stroke-width="7" stroke-linecap="round"/><circle r="10" fill="{INK}"/></svg>')
wel(f'<div class="num" style="font-size:240px;color:{TQ}">12</div>', 1300, 120, A("s5@Zwölf", "s6@Monate", -0.1))
wel(f'<div class="chip tq mono" style="font-size:34px;padding:10px 22px;font-weight:700">VOLLSTÄNDIG</div>', 1330, 440, A("s5@vollständig", "s9", -0.1))
MON = "J F M A M J J A S O N D".split()
for k in range(12):
    r, c = divmod(k, 4)
    W_.append(f'<div class="el mbox" {A("s6@Monate", "s9", round(-0.25 + k * 0.05, 2))} data-sfx="{"plop" if k % 3 == 0 else "none"}" style="left:{1700 + c * 104}px;top:{80 + r * 104}px">{MON[k]}</div>')
wmk("12 MONATE", 1715, 415, "s6@Monate", "s9", 0.4, INK)
wel(clock, 1290, 70, A("s6@Stunden", "s9", -0.2))
wmk("12 STUNDEN", 1330, 520, "s6@Uhr", "s9", -0.1, INK)
W_.append(f'<div class="el mbox" id="m13" {A("s7@Dreizehn", "s9", -0.05)} style="left:2124px;top:392px;background:{RED};border-color:{RED};color:#fff;font-size:44px">13</div>')

# ---- Station 3: Abendmahl (x 2500–3450) ----
wmk("LAUT BIBEL", 2600, 270, "s9@Abendmahl", "s10", 0.0)
tab = R(2560, 420, 780, 90, 10, 3.0) + P("M2600 510 v90 M3300 510 v90", 3.0) + D("M2580 445 H3320", 1.3)
wsk(tab, WW, 800, 0, 0, "s9@Abendmahl", -0.2, 1.0)
for k in range(13):
    x = 2590 + k * 57; dl = round(0.05 + k * 0.07, 2)
    W_.append(f'<div class="el seat" {A("s9@dreizehn", "s13", dl)} data-sfx="{"bubble"}" style="left:{x}px;top:350px"></div>')
    W_.append(f'<div class="el plate" {A("s9@Tisch", "s13", round(k * 0.03, 2))} data-sfx="none" style="left:{x + 6}px;top:440px"></div>')
wel(f'<div class="row" style="gap:16px"><span class="num" style="font-size:150px;color:{PUR}">{cnt(13, "s9@dreizehn", 0, 0.05)}</span><span class="mono" style="font-size:30px;font-weight:700;line-height:1.2">AM<br>TISCH</span></div>', 2700, 110, A("s9@dreizehn", "s10", -0.1))
W_.append(f'<div class="el seat" {A("s10@Jesus", "s13", -0.1)} style="left:{2590 + 6 * 57}px;top:350px;background:{PUR};border-color:{PUR};transform:scale(1.25)"></div>')
wmk("JESUS", 2880, 270, "s10@Jesus", "s11", -0.05, PUR)
for k in range(13):
    if k == 6: continue
    W_.append(f'<div class="el seat" {A("s10@Jünger", "s13", round(-0.15 + abs(k - 6) * 0.04, 2))} data-sfx="none" style="left:{2590 + k * 57}px;top:350px;background:{TQ};border-color:{TQ}"></div>')
wmk("12 JÜNGER", 2620, 600, "s10@Jünger", "s11", 0.1, TQ)
W_.append(f'<div class="el seat" {A("s11@Judas", "s13", -0.05)} data-sfx="none" style="left:{2590 + 12 * 57}px;top:350px;background:{RED};border-color:{RED};transform:scale(1.25)"></div>')
wmk("JUDAS: VERRAT", 3100, 270, "s11@Judas", "s12", 0.0, RED)
wel(calsheet("FREITAG", "✝", 200, 180, 24, 90, INK, INK), 3110, 110, A("s12@Freitag", "s13", -0.1))
wmk("KARFREITAG", 3100, 600, "s12@gekreuzigt", "s13", 0.0, INK)

# ---- Station 4: Zeitstrahl (x 3650–4650) ----
AX = 640
W_.append(f'<svg width="{WW}" height="800" style="position:absolute;left:0;top:0;overflow:visible">'
          f'<line x1="3700" y1="{AX}" x2="4620" y2="{AX}" stroke="{INK}" stroke-width="3"/>'
          + "".join(f'<line x1="{x}" y1="{AX - 12}" x2="{x}" y2="{AX + 12}" stroke="{INK}" stroke-width="3"/><text x="{x}" y="{AX + 50}" text-anchor="middle" font-family="JBM" font-weight="700" font-size="26" fill="{INK2}">{y}</text>' for x, y in ((3760, "1700"), (4040, "1800"), (4320, "1900"), (4560, "2026")))
          + '</svg>')
W_.append(f'<div class="el" {A("s13@neunzehnten", "end", -0.15)} data-sfx="none" style="left:4040px;top:{AX - 22}px;width:280px;height:44px">'
          f'<div class="grow" data-ga="s13@neunzehnten" style="position:absolute;inset:0;border-radius:8px;background:rgba(123,63,228,.25);border:2.5px solid {PUR};transform-origin:left"></div></div>')
wmk("19. JAHRHUNDERT", 4060, 545, "s13@Jahrhundert", "s16", 0.0)
W_.append(f'<div class="el" id="mA" {A("s13@Beides", "s16", -0.15)} style="left:3700px;top:130px">{calsheet("FREITAG", "FR", 220, 200, 26, 100, INK, PUR)}</div>')
W_.append(f'<div class="el" id="mB" {A("s13@Beides", "s16", -0.05)} style="left:4380px;top:130px">{calsheet("ZAHL", "13", 220, 200, 26, 100, PUR, INK)}</div>')
wel(f'<div class="chip mono" style="font-size:32px;padding:10px 20px;font-weight:700;border-color:{RED};color:{RED};background:#fff">= PECHTAG?</div>', 4060, 400, A("s13@Pechtag", "s16", -0.1))

# ---- Station 5: Statistik (x 4850–5850) ----
shield = P("M60 8 L110 26 V70 Q110 120 60 140 Q10 120 10 70 V26 Z", 3) + P("M38 74 l16 16 l30 -34", 3.4, TQ)
W_.append(f'<div class="el" {A("s16@Versicherung", "s17", -0.3)} data-sfx="none" style="left:0;top:0">'+sketch(shield, 120, 150, 4920, 90, "s16@Versicherung", -0.3, 0.9, 1.3)+'</div>')
wmk("VERSICHERUNG (R+V)", 4900, 320, "s16@Versicherung", "s17", 0.1)
wel(f'<div class="row" style="gap:14px"><span class="num" style="font-size:150px;color:{PUR}">{cnt(20, "s16@zwanzig", 0, 0)}</span><span class="mono" style="font-size:30px;font-weight:700;line-height:1.2">JAHRE<br>DATEN</span></div>', 5150, 100, A("s16@zwanzig", "s17", -0.1))
car = P("M10 70 V48 l20 -24 h60 l22 24 h18 V70 Z", 3) + C(38, 72, 12, 3) + C(102, 72, 12, 3) + D("M36 30 h22 v18 h-34 M64 30 h20 l14 18 h-34", 1.6)
house = P("M10 60 L70 10 L130 60 M24 50 V120 H116 V50", 3) + R(56, 80, 28, 40, 2, 2.4) + R(30, 66, 18, 18, 2, 2) + R(92, 66, 18, 18, 2, 2)
W_.append(f'<div class="el" {A("s16@Autos", "s17", -0.25)} data-sfx="none" style="left:0;top:0">'+sketch(car, 140, 90, 5160, 420, "s16@Autos", -0.25, 0.8, 1.3)+'</div>')
W_.append(f'<div class="el" {A("s16@Häusern", "s17", -0.25)} data-sfx="none" style="left:0;top:0">'+sketch(house, 140, 130, 5430, 380, "s16@Häusern", -0.25, 0.8, 1.2)+'</div>')
BB = 640
wel(f'<div class="bar" style="height:440px;background:#C9CCD3"></div>', 4920, BB - 440, A("s17@Dreizehnten", "end", -0.35) + ' data-sfx="panel"', "transform-origin:bottom")
wel(f'<div class="bar" style="height:415px;background:{TQ}"></div>', 5140, BB - 415, A("s17@Dreizehnten", "end", -0.1) + ' data-sfx="panel"', "transform-origin:bottom")
wel(f'<div class="mono barv" style="color:#5D616B">≈ {cnt(3403, "s17@Dreizehnten", 0, -0.35)}</div>', 4915, BB - 500, A("s17@Dreizehnten", "end", -0.35) + ' data-sfx="none"')
wel(f'<div class="mono barv" style="color:{TQ}">≈ {cnt(3209, "s17@Dreizehnten", 0, -0.1)}</div>', 5135, BB - 475, A("s17@Dreizehnten", "end", -0.1) + ' data-sfx="none"')
wel(f'<div class="mono barl">ANDERE<br>FREITAGE</div>', 4915, BB + 12, A("s17@Dreizehnten", "end", -0.35) + ' data-sfx="none"')
wel(f'<div class="mono barl" style="color:{TQ}">FREITAG,<br>DER 13.</div>', 5135, BB + 12, A("s17@Dreizehnten", "end", -0.1) + ' data-sfx="none"')
wel(f'<div class="num" style="font-size:180px;color:{PUR}">−{cnt(6, "s17@sechs", 0, -0.1)}<span style="font-size:120px"> %</span></div>', 5350, 140, A("s17@sechs", "end", -0.15))
wmk("WENIGER SCHÄDEN", 5390, 380, "s17@weniger", "end", 0.0, INK)
wel('<div class="note mono">R+V · Ø PRO TAG · 20 JAHRE · KFZ + SACH</div>', 4910, 762 - 36, A("s17@anderen", "end", 0.2) + ' data-sfx="none"')

# ---- Hauptdarsteller: schwarze Katze (läuft unten mit der Kamera mit) ----
catsvg = (f'<svg width="150" height="120" viewBox="0 0 150 120" style="overflow:visible">'
          f'<path class="tail" d="M22 62 Q-4 40 10 10" stroke="{INK}" stroke-width="9" fill="none" stroke-linecap="round"/>'
          + "".join(f'<line class="leg l{i}" x1="{x}" y1="74" x2="{x}" y2="110" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>' for i, x in enumerate((34, 48, 92, 106)))
          + f'<ellipse cx="68" cy="66" rx="50" ry="24" fill="{INK}"/>'
          f'<g class="chead"><circle cx="116" cy="42" r="22" fill="{INK}"/><path d="M100 30 L102 8 L114 22 Z M120 22 L132 8 L134 30 Z" fill="{INK}"/>'
          f'<ellipse cx="110" cy="40" rx="4" ry="6" fill="#FFC23D"/><ellipse cx="125" cy="40" rx="4" ry="6" fill="#FFC23D"/></g></svg>')
W_.append(f'<div id="cat" style="position:absolute;left:0;top:0;opacity:0">{catsvg}</div>')

chips = el('<div class="chip mono" style="font-size:19px;padding:8px 12px">FREITAG, DER 13.</div>', 18, 18, A("s1", "s4", -0.6) + ' data-sfx="none"')
world = f'<div id="world" style="position:absolute;left:0;top:0;width:{WW}px;height:800px;transform-origin:0 0">{"".join(W_)}</div>'
stage.append(mm(world + chips, 40, 440, 1000, 800, A("s1", "end", -0.6) + ' data-sfx="none"'))

# ---- Overlays (Bildschirm) ----
stage.append(el('<div class="stamp mono" style="font-size:54px">EINS ZU VIEL</div>', 40, 1100, A("s7@viel", "s9", -0.1), 1000, CENTER))
stage.append(el(f'<div class="stamp mono" style="font-size:60px;color:{TQ};border-color:{TQ}">KEIN PECHTAG</div>', 40, 1120, A("s18@Pechtag", "end", -0.15), 1000, CENTER))

cam = [("s1", 0, 560, 1.06), ("s2", 0, 600, 1.0), ("s4", -0.35, 600, 1.0), ("s4", 0.45, 1750, 1.0), ("s9", -0.35, 1750, 1.0), ("s9", 0.45, 2950, 1.0),
       ("s9@Tisch", -0.2, 2950, 1.0), ("s9@Tisch", 0.4, 2950, 1.08), ("s12", -0.2, 2950, 1.08), ("s12", 0.3, 2980, 1.0), ("s13", -0.35, 2980, 1.0),
       ("s13", 0.45, 4150, 1.0), ("s16", -0.35, 4150, 1.0), ("s16", 0.45, 5350, 1.0), ("s18", 0, 5350, 1.0), ("end", 0, 5350, 0.97)]
PANJS = dict(cam=cam)

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
 const top=cl(1-pr(t,END,.3),0,1); const hf=1-pr(t,S['s4']-0.35,0.35); document.getElementById('headbg').style.opacity=hf; document.getElementById('head').style.opacity=top*hf;
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
 // ---- Panorama ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const ks=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],z:k[3]}}));
  function base(tt){{ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){{ const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){{ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e)}}; }} }} return ks[ks.length-1]; }}
  const bs=base(t);
  document.getElementById('world').style.transform=`translate(500px,400px) scale(${{bs.z}}) translate(${{-bs.x}}px,-400px)`;
  // Katze
  const CT=document.getElementById('cat'); const bx=base(t+0.04).x, mv=Math.abs(bx-bs.x)>0.8;
  let cx=bs.x+330, cy=742-112, hop=0; const tp=t-S['s18@Pechtag']; if(tp>0&&tp<1.2) hop=Math.abs(Math.sin(tp*Math.PI*2.5))*40*(1-tp/1.2);
  CT.style.opacity=ease(pr(t,S['s1@Dreizehnte']-0.2,0.4));
  CT.style.transform=`translate(${{cx-75}}px,${{cy-hop-(mv?Math.abs(Math.sin(t*16))*5:0)}}px)`;
  const sw=mv?Math.sin(t*16)*24:0; CT.querySelectorAll('.leg').forEach((l,i)=>{{const x=+l.getAttribute('x1'); l.setAttribute('transform',`rotate(${{(i%2?-sw:sw).toFixed(1)}} ${{x}} 74)`);}});
  CT.querySelector('.tail').setAttribute('transform',`rotate(${{(8*Math.sin(t*3)).toFixed(1)}} 22 62)`);
  // großer Kalender wackelt im Hook
  {{ const g=document.getElementById('bigcal'); const w=Math.sin(t*5)*2.2*(1-pr(t,S['s3'],0.5)); g.style.transform=`rotate(${{w.toFixed(2)}}deg) scale(${{(1+0.03*Math.sin(t*3)).toFixed(3)}})`; }}
  // Uhr läuft
  {{ const m=(t-S['s6@Stunden'])*240; document.getElementById('hh').setAttribute('transform',`rotate(${{(m/12).toFixed(1)}})`); document.getElementById('mh').setAttribute('transform',`rotate(${{m.toFixed(1)}})`); }}
  // 13. Monatsbox wackelt
  {{ const e=document.getElementById('m13'); const a=pr(t,S['s7@Dreizehn'],0.2); e.style.rotate=(a*10*Math.sin((t-S['s7@Dreizehn'])*8)).toFixed(1)+'deg'; }}
  // Freitag + 13 fahren zusammen
  {{ const q=ease(pr(t,S['s13@zusammen']-0.1,0.9)); document.getElementById('mA').style.translate=`${{(q*200).toFixed(1)}}px 0`; document.getElementById('mB').style.translate=`${{(-q*240).toFixed(1)}}px 0`; }}
  for(const g of document.querySelectorAll('.grow')) g.style.transform=`scaleX(${{ease(pr(t,S[g.dataset.ga],0.8))}})`;
  // Balken wachsen
  for(const e of document.querySelectorAll('.bar')){{ const el=e.parentElement; const t0=S[el.dataset.in]+(+el.dataset.d||0); e.style.transformOrigin='bottom'; e.style.transform=`scaleY(${{ease(pr(t,t0,0.8)).toFixed(3)}})`; }}
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
