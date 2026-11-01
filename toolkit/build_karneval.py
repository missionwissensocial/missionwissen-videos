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
CH = ["01 DIE FRAGE", "02 DIE ELF", "03 DER ELFERRAT", "04 MARTINSTAG", "05 DIE SESSION", "06 UND DU?"]
B = [
 ("p1", 0, "Warum am 11.11. um 11:11?", "Warum startet der *Karneval* ausgerechnet am *elften* *Elften* um *elf* *Uhr* *elf?*", None),
 ("p2", 0, "Niemand weiß es sicher", "Ganz *sicher* weiß das *niemand* – aber die *beste* *Spur* führt zur *Zahl* *Elf.*", None),
 ("p3", 1, "Die Elf: die Narrenzahl", "Sie gilt als *Narrenzahl:*", None),
 ("p4", 1, "Zwischen 10 und 12", "*eins* *mehr* als die *zehn* *Gebote,* *eins* *weniger* als die *zwölf* *Apostel.*", None),
 ("p5", 1, "Immer ein bisschen daneben", "Also immer ein *bisschen* *daneben* – *perfekt* für *Narren.*", None),
 ("p6", 2, "Der Elferrat", "Passend dazu sitzt bei *Karnevalssitzungen* ein *Elferrat* auf der *Bühne.*", None),
 ("p7", 3, "11.11. ist auch Martinstag", "Dazu kommt der *Martinstag,* auch am *elften* *November.*", None),
 ("p8", 3, "Danach: Fasten bis Weihnachten", "Früher begann danach eine *Fastenzeit* bis *Weihnachten.*", None),
 ("p9", 3, "Vorher: noch mal feiern", "Also wurde vorher noch mal *kräftig* *gegessen* und *gefeiert.*", None),
 ("p10", 4, "Dann wird's ruhiger", "Nach dem *Auftakt* wird es erst mal *ruhiger.*", None),
 ("p11", 4, "Höhepunkt im Februar", "Der *Höhepunkt* kommt erst im *Februar* – bis am *Aschermittwoch* alles *vorbei* ist.", None),
 ("p12", 5, "Und du?", "Und *du:* *Jeck* oder *Karnevalsmuffel?*", None),
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


# ================= Bühne "Narren-Zeitstrahl" (durchgehendes Panorama mit Kamerafahrt) =================
import math
CENTER = "display:flex;justify-content:center"
YEL = "#FFC23D"
WW = 4200; AX = 620
W_ = []
def wel(inner, x, y, attrs, style=""): W_.append(el(inner, x, y, attrs, None, style))
def wsk(*a, **k): W_.append(sketch(*a, **k))
def wmk(text, x, y, i, o, d=0.1, col=PUR):
    W_.append(f'<div class="el mk" {A(i, o, d)} style="left:{x}px;top:{y}px;gap:10px"><span class="pin" style="background:{col}"></span><span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div>')
def hat(w=200, c1=PUR, c2=TQ):
    h = w * 0.8
    return (f'<svg width="{w}" height="{h:.0f}" viewBox="-12 -10 144 100" style="overflow:visible">'
            f'<path d="M14 64 C14 40 4 26 -5 18 C22 18 38 36 44 62 Z" fill="{c1}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M106 64 C106 40 116 26 125 18 C98 18 82 36 76 62 Z" fill="{c1}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M38 64 C42 34 52 12 60 0 C68 12 78 34 82 64 Z" fill="{c2}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<rect x="10" y="60" width="100" height="20" rx="7" fill="#fff" stroke="{INK}" stroke-width="3"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="8" fill="{YEL}" stroke="{INK}" stroke-width="2.6"/>' for x, y in [(-5, 18), (60, 0), (125, 18)])
            + '</svg>')
def fig(col=INK, sc=1.0):
    return (f'<svg width="{30*sc:.0f}" height="{54*sc:.0f}" viewBox="0 0 30 54" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round">'
            f'<circle cx="15" cy="8" r="6.5" fill="#fff"/><path d="M15 15v19M15 34l-7 17M15 34l7 17 M5 24h20"/></svg>')

# Achse (statisch)
W_.append(f'<svg width="{WW}" height="760" style="position:absolute;left:0;top:0;overflow:visible">'
          f'<line x1="0" y1="{AX}" x2="{WW}" y2="{AX}" stroke="{INK2}" stroke-width="2" stroke-dasharray="6 8"/>'
          f'<line x1="2880" y1="{AX}" x2="4120" y2="{AX}" stroke="{INK}" stroke-width="3"/>'
          + "".join(f'<line x1="{x}" y1="{AX - 10}" x2="{x}" y2="{AX + 10}" stroke="{INK}" stroke-width="3"/>' for x in (2900, 3200, 3510, 3820, 4100))
          + '</svg>')

# ---- Station 1: Uhr (x 0–920) ----
ticks = "".join(f'<line x1="0" y1="-178" x2="0" y2="{-160 if k % 3 else -150}" stroke="{INK}" stroke-width="{6 if k % 3 == 0 else 3.5}" stroke-linecap="round" transform="rotate({k * 30})"/>' for k in range(12))
nums = "".join(f'<text x="{(132 if k == 11 else 124) * math.sin(math.radians(k * 30)):.1f}" y="{-124 * math.cos(math.radians(k * 30)) + 13:.1f}" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="{38 if k == 11 else 34}" fill="{PUR if k == 11 else INK}">{k if k else 12}</text>' for k in (0, 3, 6, 9, 11))
clock = (f'<svg width="400" height="400" viewBox="-200 -200 400 400"><circle r="192" fill="#fff" stroke="{INK}" stroke-width="5"/>'
         f'<circle id="c11" r="192" fill="none" stroke="{PUR}" stroke-width="10" opacity="0"/>{ticks}{nums}'
         f'<line id="hh" x1="0" y1="14" x2="0" y2="-92" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
         f'<line id="mh" x1="0" y1="18" x2="0" y2="-150" stroke="{PUR}" stroke-width="7" stroke-linecap="round"/>'
         f'<circle r="11" fill="{INK}"/></svg>')
wel(clock, 260, 125, A("p1", "p6", -0.6) + ' data-sfx="none"')
wel(f'<div class="cal"><div class="calh mono">NOVEMBER</div><div class="calb">11</div></div>', 690, 70, A("p1@Elften", "p6", -0.1))
wel(f'<div class="chip pu mono" style="font-size:34px;padding:10px 20px;font-weight:700;background:#fff">11:11 UHR</div>', 360, 552, A("p1@Uhr", "p6", 0.0))
wel(f'<div class="qbig" style="position:static;font-size:200px;line-height:1">?</div>', 70, 150, A("p2@niemand", "p3", -0.2))
wmk("KEINE SICHERE ANTWORT", 20, 470, "p2@niemand", "p3", 0.1, RED)
wmk("DIE BESTE SPUR", 500, 650, "p2@Spur", "p3", 0.1)

# ---- Station 2: 10 · 11 · 12 (x 950–1850) ----
tabs = (P("M10 150 V45 a30 30 0 0 1 60 0 V150 Z", 2.6) + P("M80 150 V45 a30 30 0 0 1 60 0 V150 Z", 2.6)
        + "".join(D(f"M{x} {y} h36", 1.6) for x in (22, 92) for y in (60, 82, 104, 126)))
wsk(tabs, 150, 160, 1025, 60, "p4@zehn", -0.15, 0.9)
wel('<div class="num" style="color:#8A8F99">10</div>', 1000, 245, A("p4@zehn", "p6", -0.15))
wmk("10 GEBOTE", 1015, 450, "p4@Gebote", "p6", -0.1, INK)
wel(f'<div class="chip tq mono" style="font-size:34px;padding:6px 16px;font-weight:700">+1</div>', 1200, 190, A("p4@mehr", "p6", 0) + ' data-sfx="plop"')
ring = "".join(C(70 + 62 * math.sin(math.radians(k * 30)), 70 - 62 * math.cos(math.radians(k * 30)), 9, 2.2, PUR) for k in range(12))
wsk(ring, 140, 140, 1630, 70, "p4@zwölf", -0.1, 0.9)
wel('<div class="num" style="color:#8A8F99">12</div>', 1600, 245, A("p4@zwölf", "p6", -0.1))
wmk("12 APOSTEL", 1615, 450, "p4@Apostel", "p6", -0.1, INK)
wel(f'<div class="chip pu mono" style="font-size:34px;padding:6px 16px;font-weight:700">−1</div>', 1530, 190, A("p4@weniger", "p6", 0) + ' data-sfx="plop"')
wel(f'<div id="w11" style="position:relative;width:260px;height:420px"><div style="position:absolute;left:30px;top:0">{hat(200)}</div>'
    f'<div class="num" style="position:absolute;left:0;top:150px;width:260px;text-align:center;font-size:230px;color:{PUR}">11</div></div>',
    1270, 30, A("p3@Narrenzahl", "p6", -0.25))
wmk("NARRENZAHL", 1310, 450, "p3@Narrenzahl", "p6", 0.3)

# ---- Station 3: Elferrat (x 1950–2750) ----
stg = (P("M2010 30 q30 120 0 260 q-20 150 10 300", 3) + P("M2690 30 q-30 120 0 260 q20 150 -10 300", 3) + P("M1990 30 H2710", 3)
       + "".join(D(f"M{2020 + 14 * k} 40 q10 140 -4 540", 1.2) for k in range(4)) + "".join(D(f"M{2680 - 14 * k} 40 q-10 140 4 540", 1.2) for k in range(4))
       + R(2020, 575, 660, 45, 4, 2.6))
wsk(stg, WW, 760, 0, 0, "p6", -0.1, 1.2)
for k in range(11):
    W_.append(f'<div class="el aa" {A("p6@Elferrat", "p7", round(-0.1 + k * 0.07, 2))} style="left:{2078 + k * 50}px;top:338px;width:44px">'
              f'<div style="position:absolute;left:-6px;top:-34px">{hat(56, PUR if k % 2 else TQ, YEL if k % 2 else PUR)}</div>{fig(INK, 1.4)}</div>')
W_.append(f'<div class="el" {A("p6@Elferrat", "p7", -0.15)} data-sfx="none" style="left:2050px;top:440px;width:600px;height:110px;border:3px solid {INK};border-radius:8px;'
          f'background:repeating-linear-gradient(90deg,#fff 0 30px,rgba(123,63,228,.14) 30px 60px)"></div>')
wel(f'<div class="chip mono row" style="font-size:30px;gap:14px;padding:10px 20px;font-weight:700;background:#fff">ELFERRAT = <span class="bignum" style="font-size:54px;color:{PUR}">{cnt(11, "p6@Elferrat", 0, 0.1)}</span> NARREN</div>', 2120, 150, A("p6@Elferrat", "p7", 0.1) + ' data-sfx="glass"')
wmk("AUF DER BÜHNE", 2240, 640, "p6@Bühne", "p7", 0.0, INK)

# ---- Station 4: Zeitstrahl 11.11. → Aschermittwoch (x 2880–4120, 10 px/Tag) ----
for x, m in [(2900, "NOV"), (3200, "DEZ"), (3510, "JAN"), (3820, "FEB"), (4100, "MÄR")]:
    wel(f'<span class="mono" style="font-size:24px;font-weight:700;color:{INK2}">{m}</span>', x - 24, 700, A("p7", "end", -0.2) + ' data-sfx="none"')
wel(f'<div style="width:0;height:{AX-170}px;border-left:3px dashed {PUR}"></div>', 2998, 170, A("p7@Martinstag", "end", -0.2) + ' data-sfx="none"')
wel(f'<div style="width:0;height:{AX-380}px;border-left:3px dashed {RED}"></div>', 3910, 380, A("p11@Aschermittwoch", "end", -0.1) + ' data-sfx="none"')
wel(f'<div class="cal" style="width:130px;height:120px"><div class="calh mono" style="font-size:18px">NOV</div><div class="calb" style="font-size:64px">11</div></div>', 2935, 40, A("p7@Martinstag", "end", -0.2))
wmk("MARTINSTAG", 3030, 175, "p7@Martinstag", "end", 0.15)
lan = (P("M0 10 H70", 2.6) + P("M40 10 V34", 1.8) + R(20, 34, 40, 56, 10, 2.6) + D("M20 50 h40 M20 74 h40", 1.4)
       + f'<circle cx="40" cy="62" r="11" fill="{YEL}" class="mesh" style="opacity:0"/>')
wsk(lan, 80, 100, 3070, 230, "p7@November", -0.2, 0.9)
goose = (P("M20 82 q-8 -34 40 -38 q34 -2 52 22 q8 14 -10 22 q-30 14 -70 4 q-10 -2 -12 -10z", 2.6)
         + P("M100 64 q12 -26 4 -48 q-4 -14 10 -16 q10 0 12 10 l16 4 l-16 6 q-6 18 4 40", 2.6) + D("M40 66 q20 10 46 0", 1.4) + P("M54 92 v14 M74 92 v14", 2.2))
wsk(goose, 150, 110, 2770, 420, "p9@gegessen", -0.3, 0.8)
wmk("MARTINSGANS", 2760, 560, "p9@gegessen", "p10", 0.1, INK)
wel(f'<div class="chip tq mono" style="font-size:26px;padding:8px 14px">ESSEN</div>', 2770, 300, A("p9@gegessen", "p10", 0) + ' data-sfx="plop"')
wel(f'<div class="chip pu mono" style="font-size:26px;padding:8px 14px">FEIERN</div>', 2780, 360, A("p9@gefeiert", "p10", 0) + ' data-sfx="plop"')
W_.append(f'<div class="el" {A("p8@Fastenzeit", "end", -0.2)} data-sfx="none" style="left:3000px;top:640px;width:430px;height:50px">'
          f'<div class="grow" data-ga="p8@Fastenzeit" style="position:absolute;inset:0;border-radius:8px;border:2px solid #8A8F99;background:repeating-linear-gradient(45deg,#E9EBF0 0 8px,#fff 8px 16px);transform-origin:left">'
          f'<span class="mono" style="position:absolute;left:12px;top:9px;font-size:22px;font-weight:700;color:#5D616B;white-space:nowrap">FASTENZEIT (FRÜHER)</span></div></div>')
tree = P("M35 0 L60 40 H46 L70 80 H54 L80 120 H-10 L16 80 H0 L24 40 H10 Z", 2.4) + P("M28 120 v16 h14 v-16", 2.2) + f'<circle cx="35" cy="-6" r="7" fill="{YEL}" class="mesh" style="opacity:0"/>'
wsk(tree, 80, 140, 3395, 420, "p8@Weihnachten", -0.2, 0.9)
wmk("WEIHNACHTEN", 3320, 360, "p8@Weihnachten", "end", 0.1, INK)
wmk("RUHIGER", 3180, 520, "p10@ruhiger", "end", -0.1, INK2)
wmk("HÖHEPUNKT IM FEBRUAR", 3540, 230, "p11@Februar", "end", 0.0)
# Stimmungskurve
def hx(x):
    if x < 2950: return 0
    if x < 3000: return 230 * math.sin(math.pi / 2 * (x - 2950) / 50)
    if x < 3060: u = (x - 3000) / 60; return 25 + 205 * (1 - u) ** 2
    if x < 3510: return 25 + 5 * math.sin((x - 3060) / 28)
    if x < 3850: u = (x - 3510) / 340; return 25 + 125 * u * u
    if x < 3895: return 150 + 150 * math.sin(math.pi / 2 * (x - 3850) / 45)
    if x < 3912: return 300 * (1 - (x - 3895) / 17)
    return 0
CURVE = [[x, round(AX - hx(x), 1)] for x in range(0, WW + 1, 5)]
W_.append(f'<svg width="{WW}" height="760" style="position:absolute;left:0;top:0;overflow:visible">'
          f'<polyline id="trail" points="" fill="none" stroke="{PUR}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 14"/>'
          f'<polyline id="mood" points="" fill="none" stroke="{PUR}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>')
# Konfetti
KC = [PUR, TQ, YEL, RED, PUR, TQ]
for bi, (cx, cy, anc) in enumerate([(3000, 390, "p9@gefeiert"), (3895, 320, "p11@Februar")]):
    for j in range(28):
        a = (j * 137.5 + bi * 40) % 360; v = 120 + (j * 53) % 140
        W_.append(f'<div class="konf" data-ka="{anc}" data-cx="{cx}" data-cy="{cy}" data-vx="{v * math.cos(math.radians(a)):.0f}" data-vy="{v * math.sin(math.radians(a)) - 150:.0f}" data-r="{(j * 47) % 360}" '
                  f'style="left:0;top:0;width:{10 + j % 3 * 4}px;height:{7 + j % 2 * 5}px;background:{KC[j % 6]};border-radius:{2 if j % 3 else 6}px"></div>')
W_.append('<div id="tip" style="position:absolute;left:0;top:0;opacity:0"><div class="tipring"></div><div class="tipdot"></div></div>')

chips = (el('<div class="chip mono" style="font-size:19px;padding:8px 12px">KARNEVAL · 11.11.</div>', 18, 18, A("p1", "p7", -0.6) + ' data-sfx="none"')
         + el(f'<div class="chip mono" style="font-size:19px;padding:8px 12px;color:#8A8F99;border-color:#C9CCD3">STIMMUNG · SCHEMATISCH</div>', 18, 18, A("p9", "p12", 0) + ' data-sfx="none"'))
world = f'<div id="world" style="position:absolute;left:0;top:0;width:{WW}px;height:760px;transform-origin:0 0">{"".join(W_)}</div>'
stage.append(mm(world + chips, 80, 460, 920, 760, A("p1", "end", -0.6)))

# ---- Overlays ----
stage.append(el('<div class="stamp mono" style="font-size:52px;color:#7B3FE4;border-color:#7B3FE4">PERFEKT FÜR NARREN</div>', 80, 1085, A("p5@perfekt", "p6", -0.1), 920, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:46px">ASCHERMITTWOCH: VORBEI</div>', 80, 545, A("p11@vorbei", "p12", -0.2), 920, CENTER))
stage.append(card(f'<div class="row" style="gap:30px;height:100%;justify-content:center">{hat(150)}<div class="qbig" style="position:static;font-size:150px;line-height:1">?</div></div>', 260, 500, 560, 210, "active", A("p12@Und", "end")))
stage.append(el('<div class="row" style="gap:24px;justify-content:center"><div class="chip tq mono" style="font-size:40px;padding:14px 34px">JECK</div><div class="chip mono" style="font-size:40px;padding:14px 34px">MUFFEL</div></div>', 200, 735, f'{A("p12@Jeck", "end")} data-sfx="plop"', 680))
stage.append(el('<div class="chip pu mono" style="font-size:22px">SCHREIB\'S IN DIE KOMMENTARE</div>', 260, 850, f'{A("p12@Karnevalsmuffel", "end", 0.2)} data-sfx="plop"', 560, CENTER))

cam = [("p1", 0, 460, 1.06, 380), ("p2", 0, 460, 1.0, 380), ("p2@Spur", 0.1, 460, 1, 380), ("p3", 0.1, 1400, 1, 380), ("p6", -0.1, 1400, 1, 380),
       ("p6@Elferrat", 0.1, 2350, 1, 380), ("p7", -0.2, 2350, 1, 380), ("p7@Martinstag", 0.2, 3020, 1, 380), ("p8@Fastenzeit", -0.2, 3020, 1, 380),
       ("p8@Weihnachten", 0.2, 3200, 0.92, 380), ("p9", -0.1, 3200, 0.92, 380), ("p9@kräftig", 0.1, 3000, 1, 380), ("p10", -0.1, 3000, 1, 380),
       ("p10@ruhiger", 0.2, 3350, 0.92, 380), ("p11", 0, 3350, 0.92, 380), ("p11@Februar", 0.3, 3780, 0.9, 380), ("p11@Aschermittwoch", 0.3, 3850, 0.9, 380),
       ("p12", -0.1, 3850, 0.9, 380), ("p12@Jeck", 0.3, 2100, 0.215, 620)]
tipk = [("p2@Spur", 0, 460), ("p3", 0.3, 1400), ("p6", -0.1, 1400), ("p6@Elferrat", 0.2, 2350), ("p7", -0.2, 2350), ("p7@Martinstag", 0.3, 2950),
        ("p9@kräftig", -0.1, 2950), ("p9@gefeiert", 0.3, 3010), ("p10@Auftakt", -0.1, 3010), ("p10@ruhiger", 0.3, 3500), ("p11@Höhepunkt", -0.1, 3500),
        ("p11@Februar", 0.3, 3895), ("p11@Aschermittwoch", 0, 3895), ("p11@vorbei", 0.1, 3925)]
PANJS = dict(cam=cam, tip=tipk, curve=CURVE)


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
.konf{{position:absolute;opacity:0}}
.num{{font-family:Unbounded;font-weight:600;font-size:170px;letter-spacing:-6px;line-height:1}}
.cal{{width:190px;height:170px;border-radius:16px;border:3px solid #0B0B10;background:#fff;overflow:hidden;box-shadow:0 6px 14px rgba(26,31,51,.12)}}
.calh{{background:#7B3FE4;color:#fff;font-size:22px;font-weight:700;text-align:center;padding:8px 0}}
.calb{{font-family:Unbounded;font-weight:600;font-size:92px;text-align:center;line-height:1.2}}
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
 // ---- Panorama: Narren-Zeitstrahl ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const ks=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],z:k[3],fy:k[4]}}));
  function base(tt){{ if(tt<=ks[0].t) return ks[0]; for(let i=0;i<ks.length-1;i++){{ const k0=ks[i],k1=ks[i+1]; if(tt>=k0.t&&tt<k1.t){{ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e),fy:k0.fy+(k1.fy-k0.fy)*e}}; }} }} return ks[ks.length-1]; }}
  const bs=base(t);
  document.getElementById('world').style.transform=`translate(460px,${{bs.fy}}px) scale(${{bs.z}}) translate(${{-bs.x}}px,-380px)`;
  const tk=PAN.tip.map(k=>({{t:TS(k[0],k[1]),x:k[2]}}));
  function tipx(tt){{ if(tt<=tk[0].t) return tk[0].x; for(let i=0;i<tk.length-1;i++){{ const a=tk[i],c=tk[i+1]; if(tt>=a.t&&tt<c.t){{ const u=(tt-a.t)/Math.max(1e-6,c.t-a.t); return a.x+(c.x-a.x)*u*u*(3-2*u); }} }} return tk[tk.length-1].x; }}
  const CV=PAN.curve; const cy=x=>{{ const i=Math.max(0,Math.min(CV.length-2,Math.floor(x/5))); const q=(x-CV[i][0])/5; return CV[i][1]+(CV[i+1][1]-CV[i][1])*q; }};
  const t0=tk[0].t, on=ease(pr(t,t0,0.4)); const tx=tipx(t), mv=Math.abs(tipx(t+0.05)-tx)>0.4;
  const TP=document.getElementById('tip'); TP.style.left=tx+'px'; TP.style.top=(cy(tx)-(mv&&tx<2900?Math.abs(Math.sin(t*14))*8:0))+'px'; TP.style.opacity=on*(1-pr(t,S['p12@Jeck'],0.3));
  const rg=TP.querySelector('.tipring'); const ph=(t%1.1)/1.1; rg.style.transform=`scale(${{0.5+1.1*ph}})`; rg.style.opacity=1-ph;
  let pts=[],mp=[]; if(t>=t0){{ for(let x=tk[0].x;x<Math.min(tx,2950);x+=24) pts.push(x.toFixed(0)+','+cy(x).toFixed(1)); pts.push(Math.min(tx,2950).toFixed(0)+','+cy(Math.min(tx,2950)).toFixed(1));
    if(tx>2950){{ for(let x=2950;x<tx;x+=5) mp.push(x.toFixed(0)+','+cy(x).toFixed(1)); mp.push(tx.toFixed(1)+','+cy(tx).toFixed(1)); }} }}
  document.getElementById('trail').setAttribute('points',pts.join(' ')); document.getElementById('mood').setAttribute('points',mp.join(' '));
  // Uhr: Zeiger laufen auf 11:11
  {{ const q=ease(pr(t,0,Math.max(0.5,S['p1@elf']-0.1))); const m=9*60+25+(11*60+11-(9*60+25))*q;
    document.getElementById('hh').setAttribute('transform',`rotate(${{(m/60%12)*30}})`); document.getElementById('mh').setAttribute('transform',`rotate(${{(m%60)*6}})`);
    document.getElementById('c11').setAttribute('opacity',(pr(t,S['p1@elf']-0.1,0.2)*(0.55+0.45*Math.sin(t*9))).toFixed(2)); }}
  // 11 wackelt
  {{ const w=document.getElementById('w11'); const a=pr(t,S['p5@daneben'],0.2)*(1-pr(t,S['p6'],0.3)); w.style.transform=`rotate(${{9*a*Math.sin((t-S['p5@daneben'])*7)}}deg)`; w.style.transformOrigin='50% 90%'; }}
  // Fastenband wächst
  for(const g of document.querySelectorAll('.grow')) g.style.transform=`scaleX(${{ease(pr(t,S[g.dataset.ga],1.0))}})`;
  // Konfetti
  for(const k of document.querySelectorAll('.konf')){{ const ka=S[k.dataset.ka]; const p=t-ka; if(p<0||p>2.2){{k.style.opacity=0;continue;}}
    const x=+k.dataset.cx+(+k.dataset.vx)*p*(1-0.25*p), y=+k.dataset.cy+(+k.dataset.vy)*p+170*p*p;
    k.style.opacity=1-pr(p,1.5,0.6); k.style.transform=`translate(${{x.toFixed(1)}}px,${{y.toFixed(1)}}px) rotate(${{+k.dataset.r+p*420}}deg)`; }}
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
