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
HOOK = 'Black Friday: −50&nbsp;% – aber <span style="color:#7B3FE4">wovon?</span>'
B = [
 ("s1", 0, HOOK, "*Minus* *fünfzig* *Prozent* am *Black* *Friday* – aber fünfzig Prozent *wovon?*", "staunt"),
 ("s2", 0, HOOK, "In Deutschland gilt: Der *Rabatt* muss vom *niedrigsten* *Preis* der letzten *30* *Tage* gerechnet werden.", None),
 ("s3", 0, "", "Und diesen Preis muss der Shop *angeben.*", None),
 ("s4", 0, "", "Den Preis kurz vorher *hochsetzen,* damit der Rabatt *größer* aussieht?", None),
 ("s5", 0, "", "*Klappt* also *nicht.*", None),
 ("s6", 0, "", "Steht da „statt *UVP*“, gilt diese Regel *meistens* *nicht.*", None),
 ("s7", 0, "", "*UVP* heißt *unverbindliche* *Preisempfehlung* – der Preis, den der *Hersteller* vorschlägt.", None),
 ("s8", 0, "", "Den *verlangen* viele Shops *sowieso* *nicht.*", None),
 ("s9", 0, "", "Ein *Beispiel:* UVP *100* *Euro.*", None),
 ("s10", 0, "", "Der Shop verlangt sonst *70* *Euro,* jetzt *50.*", None),
 ("s11", 0, "", "Auf dem Schild steht *minus* *50* *Prozent.*", None),
 ("s12", 0, "", "Gespart hast du aber nur *20* *Euro.*", None),
 ("s13", 0, "", "Und wie viel spart man am Black Friday *wirklich?*", None),
 ("s14", 0, "", "Laut dem Preisvergleich *idealo* letztes Jahr im Schnitt nur *8* *Prozent,* verglichen mit dem *Oktober.*", None),
 ("s15", 0, "", "Also: vor dem Kauf im Preisvergleich den *Preisverlauf* *checken.*", None),
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



# ================= Bühne "Preisverlauf Okt → Black Friday" (durchgehende SVG-Kamera, Hauptdarsteller: Preisschild) =================
import math
CENTER = "display:flex;justify-content:center"
G = []
def g(inner, wi=None, wo=None, extra=""):
    a = (f' data-wi="{wi}"' if wi else "") + (f' data-wo="{wo}"' if wo else "")
    return f'<g class="wg"{a} {extra}>{inner}</g>'
def dr(d, w=2.2, c=INK, a="s1", dur=1.0, dl=0.0, extra=""):
    return f'<path class="dr" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="{d}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round" data-a="{a}" data-dl="{dl}" data-dur="{dur}" {extra}/>'
def X(d): return 110 + d * 14.5
def Y(p): return 720 - p * 4.6
# Preis-Reihe (BEISPIELPREISE): Shop verlangt sonst ca. 70–74 €, Tiefstpreis 70 €
pr_ = [70 + max(0.0, 2.2 + 1.6 * math.sin(d * 0.6) + 0.9 * math.sin(d * 1.9)) for d in range(57)]
for d in (12, 24, 38, 47): pr_[d] = 70.0
base_d = "M" + " L".join(f"{X(d):.1f} {Y(p):.1f}" for d, p in enumerate(pr_))
# Achsen + Beschriftung
ax = (f'<line x1="100" y1="{Y(0)-1}" x2="950" y2="{Y(0)-1}" stroke="{INK}" stroke-width="3"/>'
      f'<line x1="100" y1="{Y(0)}" x2="100" y2="200" stroke="{INK}" stroke-width="3"/>'
      + "".join(f'<line x1="{X(d):.1f}" y1="{Y(0)-8}" x2="{X(d):.1f}" y2="{Y(0)+6}" stroke="{INK2}" stroke-width="2"/>' for d in range(0, 57, 7))
      + f'<text x="{X(0)}" y="{Y(0)+42}" font-family="JBM" font-weight="800" font-size="26" fill="{INK2}">OKT</text>'
      + f'<text x="{X(31)}" y="{Y(0)+42}" font-family="JBM" font-weight="800" font-size="26" fill="{INK2}">NOV</text>'
      + f'<line x1="{X(57)}" y1="{Y(0)}" x2="{X(57)}" y2="220" stroke="{PUR}" stroke-width="3" stroke-dasharray="8 8"/>'
      + f'<text x="{X(57)}" y="{Y(0)+42}" text-anchor="end" font-family="JBM" font-weight="800" font-size="26" fill="{PUR}">BLACK FRIDAY</text>'
      + f'<text x="88" y="{Y(70)+9}" text-anchor="end" font-family="JBM" font-weight="800" font-size="24" fill="{INK2}">70</text>'
      + f'<text x="88" y="{Y(0)+8}" text-anchor="end" font-family="JBM" font-weight="800" font-size="24" fill="{INK2}">0 €</text>')
G.append(f'<g id="chart">{ax}')
# UVP-Linie (s6) – liegt hinter dem Preis
G.append(g(f'<rect x="{X(0)}" y="{Y(100)}" width="{X(57)-X(0):.0f}" height="{Y(70)-Y(100):.0f}" fill="rgba(229,72,77,.10)" id="gap" opacity="0"/>'
           + dr(f"M{X(0)} {Y(100)} H{X(57)}", 4, INK, "s6@UVP", 0.8, -0.1, 'stroke-dasharray="1"')
           + f'<text x="88" y="{Y(100)+9}" text-anchor="end" font-family="JBM" font-weight="800" font-size="24" fill="{INK}">100</text>', "s6@UVP", "s13"))
# Preislinie
G.append(dr(base_d, 6, INK, "s1", 1.3, -0.4, 'id="pline"'))
# 30-Tage-Fenster (s2)
G.append(g(f'<rect x="{X(27)}" y="262" width="{X(57)-X(27):.0f}" height="{Y(0)-262:.0f}" fill="rgba(123,63,228,.07)"/>'
           + dr(f"M{X(27)} 280 V262 H{X(57)} V280", 4, PUR, "s2@letzten", 0.6, -0.1)
           + f'<text x="{X(27)+8:.0f}" y="250" text-anchor="start" font-family="JBM" font-weight="800" font-size="30" fill="{PUR}">LETZTE 30 TAGE</text>', "s2@letzten", "s6"))
# Tiefstpreis-Punkt
G.append(g(f'<circle cx="{X(38)}" cy="{Y(70)}" r="20" fill="{PUR}" opacity=".25" class="lowpulse"/><circle cx="{X(38)}" cy="{Y(70)}" r="11" fill="{PUR}" stroke="#fff" stroke-width="3"/>'
           + f'<text x="{X(38)}" y="{Y(70)+56}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="28" fill="{PUR}">TIEFSTPREIS 70 €</text>', "s2@niedrigsten", "s6"))
# Preis-Sprung kurz vorher (s4)
spike = f"M{X(49)} {Y(pr_[49]):.1f} L{X(50)} {Y(95)} H{X(56)} L{X(57)} {Y(57):.1f}"
G.append(g(dr(spike, 6, RED, "s4@hochsetzen", 0.7, -0.15, 'stroke-dasharray="1"')
           + f'<text x="{X(53)}" y="{Y(95)-22}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="28" fill="{RED}">95 €?</text>', "s4@hochsetzen", "s6"))
# Pfeil: Rabatt zählt trotzdem ab 70
G.append(g(f'<path d="M{X(38)+22} {Y(70)-4} C {X(46)} {Y(70)-70}, {X(52)} {Y(70)-60}, {X(56)} {Y(70)-18}" stroke="{TQ}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="10 9"/>'
           + f'<path d="M{X(56)-14} {Y(70)-30} L{X(56)} {Y(70)-14} L{X(56)-22} {Y(70)-10}" stroke="{TQ}" stroke-width="5" fill="none" stroke-linecap="round"/>'
           + f'<text x="{X(42)}" y="{Y(70)-80}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="{TQ}">ZÄHLT AB 70 €</text>', "s5", "s6"))
# Beispiel: Absturz auf 50 am Black Friday (s10)
G.append(dr(f"M{X(56)} {Y(pr_[56]):.1f} L{X(57)} {Y(50)}", 7, PUR, "s10@50", 0.4, -0.15))
G.append(g(f'<circle cx="{X(57)}" cy="{Y(50)}" r="12" fill="{PUR}" stroke="#fff" stroke-width="3"/>'
           + f'<text x="{X(57)-24}" y="{Y(50)+50}" text-anchor="end" font-family="Unbounded" font-weight="600" font-size="40" fill="{PUR}">50 €</text>', "s10@50", "s13"))
G.append(g(f'<text x="{X(44)}" y="{Y(73)-18}" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="40" fill="{INK}">70 €</text>', "s10@70", "s13"))
# Klammer UVP -> 50 (grau, „−50 %“) und 70 -> 50 (türkis, „20 €“)
bx1 = X(57) + 26
G.append(g(f'<path d="M{bx1-10} {Y(100)} H{bx1} V{Y(50)} H{bx1-10}" stroke="{INK2}" stroke-width="4" fill="none"/>', "s11@minus", "s13"))
bx2 = X(57) - 40
G.append(g(f'<rect x="{X(50)}" y="{Y(70)}" width="{X(57)-X(50):.0f}" height="{Y(50)-Y(70):.0f}" fill="rgba(25,198,180,.22)"/>'
           + f'<path d="M{bx2-12} {Y(70)} H{bx2} V{Y(50)} H{bx2-12}" stroke="{TQ}" stroke-width="5" fill="none"/>', "s12@20", "s13"))
G.append('</g>')
# Lupe (s15)
G.append(f'<g id="lupe" opacity="0"><circle r="70" fill="rgba(255,255,255,.25)" stroke="{INK}" stroke-width="9"/><line x1="50" y1="50" x2="120" y2="120" stroke="{INK}" stroke-width="16" stroke-linecap="round"/></g>')
# Preisschild (Hauptdarsteller) – hängt am Black-Friday-Strich
tag = (f'<g id="tag"><path id="tagbg" d="M0 0 L60 -60 H300 Q318 -60 318 -42 V122 Q318 140 300 140 H60 Z" fill="{PUR}" stroke="#fff" stroke-width="4"/>'
       f'<circle cx="46" cy="0" r="10" fill="#fff"/>'
       f'<text id="tagt" x="190" y="45" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="64" fill="#fff">−50%</text>'
       f'<g id="tags1" opacity="0"><text x="190" y="88" text-anchor="middle" font-family="JBM" font-weight="800" font-size="20" fill="#fff">TIEFSTPREIS 30 TAGE:</text><text x="190" y="122" text-anchor="middle" font-family="JBM" font-weight="800" font-size="28" fill="#fff">70 €</text></g>'
       f'<text id="tags2" x="190" y="100" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="#fff" opacity="0">STATT UVP 100 €</text>'
       f'<text id="tagq" x="-125" y="70" font-family="Unbounded" font-weight="600" font-size="120" fill="{PUR}">?</text>'
       f'<line id="tagx" x1="80" y1="-20" x2="300" y2="80" stroke="{RED}" stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
       f'</g>')
G.append(tag)
world = f'<svg id="wsvg" width="1000" height="800" viewBox="0 0 1000 800" style="position:absolute;left:0;top:0"><g id="camg">{"".join(G)}</g></svg>'

# --- Spar-Bilanz (s13–s14): große Zahl + 2 Balken ---
bil = (f'<div id="bil" style="position:absolute;left:0;top:0;width:1000px;height:800px;opacity:0;background:rgba(252,252,253,.93)">'
       f'<div class="num" id="bnum" style="position:absolute;left:0;width:1000px;top:70px;text-align:center;font-size:220px;color:{PUR}">−8%</div>'
       f'<div class="mono" style="position:absolute;left:0;width:1000px;top:310px;text-align:center;font-size:30px;font-weight:800;color:#5D616B">Ø ERSPARNIS AM BLACK FRIDAY 2025</div>'
       f'<div style="position:absolute;left:220px;top:380px;width:560px;height:330px">'
       f'<div class="bar" id="bo" style="position:absolute;left:40px;bottom:60px;height:260px;background:#DDE0E6"></div>'
       f'<div class="bar" id="bb" style="position:absolute;right:40px;bottom:60px;height:239px;background:{PUR}"></div>'
       f'<div class="barl" style="position:absolute;left:35px;bottom:12px">OKTOBER</div><div class="barl" style="position:absolute;right:35px;bottom:12px">BLACK FRIDAY</div>'
       f'<div class="barv" style="position:absolute;left:35px;bottom:180px;color:#5D616B">100</div><div class="barv" style="position:absolute;right:35px;bottom:160px;color:#fff">92</div></div>'
       f'<div class="note mono" style="position:absolute;right:24px;bottom:20px">QUELLE: IDEALO-PREISSTUDIE · ≈ 10.000 PRODUKTE · PREIS VS. OKTOBER</div></div>')
panel = world + bil
stage.append(mm(panel, 40, 440, 1000, 800, A("s1", "end", -0.6) + ' data-sfx="none"'))

# ---- Overlays (höchstens eins gleichzeitig) ----
def omk(text, x, y, i, o, d=0.0, col=PUR):
    stage.append(f'<div class="el mk" {A(i, o, d)} style="left:{x}px;top:{y}px;gap:10px"><span class="pin" style="background:{col}"></span><span class="mono lab" style="color:{col};border-color:{col};font-size:30px">{text}</span></div>')
omk("🇩🇪 REGEL SEIT 2022", 360, 1172, "s2@Rabatt", "s3", -0.1, INK)
omk("SHOP MUSS ES ANGEBEN", 340, 1172, "s3@angeben", "s4", -0.2, PUR)
stage.append(el('<div class="stamp mono" style="font-size:56px">KLAPPT NICHT</div>', 40, 1080, A("s5@Klappt", "s6", -0.05), 1000, CENTER))
omk("⚠ AUSNAHME: „STATT UVP“", 300, 1172, "s6@UVP", "s7", -0.1, RED)
omk("🏭 VORSCHLAG VOM HERSTELLER", 270, 1172, "s7@Hersteller", "s8", -0.2, INK)
omk("KAUM EIN SHOP VERLANGT DAS", 270, 1172, "s8@verlangen", "s9", -0.1, RED)
omk("BEISPIEL", 450, 1172, "s9@Beispiel", "s11", -0.1, INK)
stage.append(el(f'<div class="chip mono" style="font-size:40px;padding:12px 24px;font-weight:800;background:#fff;border-color:{TQ};color:#0E8C80">GESPART: NUR 20 €</div>', 40, 1150, A("s12@20", "s13", -0.1) + ' data-sfx="glass"', 1000, CENTER))
stage.append(el(f'<div class="chip mono" style="font-size:34px;padding:12px 22px;font-weight:800;background:#fff;border-color:{TQ}">🔍 PREISVERLAUF CHECKEN ✓</div>', 40, 1160, A("s15@Preisverlauf", "end", -0.1), 1000, CENTER))
stage.append(el('<div class="note mono">BEISPIELPREISE · SCHEMATISCH</div>', 60, 1206, A("s2", "s13", 0.3) + ' data-sfx="none"'))
stage.append(el(f'<div class="num" style="font-size:0px">{cnt(8, "s14@8", 0, 0.0)}</div>', 0, 0, A("s14@8", "s15") + ' data-sfx="none"'))

cam = [("s1", 0, 700, 230, 1.3), ("s1", 2.6, 680, 280, 1.2), ("s2", -0.1, 600, 380, 1.08), ("s2@letzten", 0.2, 540, 420, 1.0),
       ("s4", -0.1, 540, 420, 1.0), ("s4", 0.7, 740, 330, 1.3), ("s5", 0.4, 700, 360, 1.22), ("s6", -0.1, 560, 420, 1.0),
       ("s8", 0.2, 520, 420, 1.0), ("s9", -0.1, 540, 400, 1.02), ("s10", 0.4, 740, 330, 1.3), ("s12", 0.3, 750, 340, 1.38),
       ("s13", -0.1, 600, 400, 1.1), ("s13", 0.6, 500, 400, 1.0), ("s15", -0.1, 500, 400, 1.0), ("end", 0, 520, 420, 1.0)]
PANJS = dict(cam=cam, x50=X(50), x57=X(57), y70=Y(70), y50=Y(50), y100=Y(100), pts=[[round(X(d),1), round(Y(p),1)] for d, p in enumerate(pr_)])

# ---- End card (identisch zum Template) ----
logo = open("../brand/out/missionwissen-logo-transparent-dunkel.svg").read()
logo = re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="820" height="253"', logo, count=1)
endcard = f'<div class="el" {A("end",None,0.1)} style="left:130px;top:470px">{logo}</div>' + f'<div class="el" {A("end",None,0.5)} style="left:0;width:1080px;top:790px;display:flex;justify-content:center"><div class="row" style="gap:28px"><div class="follow">+&nbsp;Folgen</div><div class="follow">🔖&nbsp;Speichern</div></div></div>' + f'<div class="el" {A("end",None,0.7)} style="left:0;width:1080px;top:935px;text-align:center"><div class="mono small grey">JEDEN TAG EIN BISSCHEN SCHLAUER</div></div>'
robots = "".join(f'<div class="pose" data-pose="{n}">{robot_svg("r"+n[:2]+"-", **k)}</div>' for n, k in POSES.items())
mono = '<svg width="72" height="72" viewBox="0 0 80 80" fill="none"><g stroke="#0B0B10" stroke-width="6" stroke-linecap="round"><path d="M20 32 V24 a10 10 0 0 1 20 0 V32 M40 24 a10 10 0 0 1 20 0 V32"/><path d="M20 48 V56 a10 10 0 0 0 20 0 V48 M40 56 a10 10 0 0 0 20 0 V48"/></g><circle cx="40" cy="40" r="3.2" fill="#7B3FE4"/></svg>'

STAGEJS = open("part_js.js").read()
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
.flake{{position:absolute;top:0;color:#8FD9D0;font-weight:700;opacity:0}}
.gcard{{background:#fff;border:2px solid #0B0B10;border-radius:18px;padding:14px 10px 12px;box-shadow:0 8px 18px rgba(26,31,51,.12)}}
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
 const top=cl(1-pr(t,END,.3),0,1); const hf=1-pr(t,S['s3']-0.3,0.35); document.getElementById('headbg').style.opacity=hf; document.getElementById('head').style.opacity=top*hf;
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
{STAGEJS}
 // robot
 let pose=b.pose; if(end) pose='winkt';
 const R=document.getElementById('robot');
 let rop=0; if(pose&&!end){{const prevHad=BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose; rop=prevHad?1:ease(pr(t,b.s-(BEATS.indexOf(b)===0?0.3:0),.3)); const nb=BEATS[BEATS.indexOf(b)+1]; if(nb&&!nb.pose) rop*=1-pr(t,nb.s-0.2,.2); if(!nb) rop*=1-pr(t,END-0.2,.2);}}
 if(end){{rop=ease(pr(t,END+0.3,.35));}}
 R.style.opacity=rop; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');
 let prevPose=null; const bi=BEATS.indexOf(b); if(bi>0) prevPose=BEATS[bi-1].pose; const pf=bi===0?1:pr(t,b.s,.15);
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
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))
