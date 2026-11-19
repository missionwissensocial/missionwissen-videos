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
CH = ["", "", "", "", ""]
HOOK = 'Wem gehört in Wien jede <span style="color:#7B3FE4">fünfte</span> Wohnung?'
B = [
 ("p1", 0, HOOK, "Wem *gehört* in *Wien* jede *fünfte* *Wohnung* – und warum ist das *gut* für die *Miete?*", "staunt"),
 ("p2", 1, "", "Der *Stadt* *Wien* *selbst.*", None),
 ("p3", 1, "", "Diese Wohnungen heißen *Gemeindewohnungen.*", None),
 ("p4", 1, "", "Seit rund *hundert* *Jahren* baut Wien sie – und hat sie *nie* an *Firmen* *verkauft.*", None),
 ("p5", 2, "", "Viele *deutsche* *Städte* haben dagegen Wohnungen *verkauft.*", None),
 ("p6", 2, "", "*Dresden* *2006* sogar *alle* – an einen *Finanzinvestor,* der *Gewinn* machen will.", None),
 ("p7", 3, "", "Und *warum* ist eine *Gemeindewohnung* *günstig?*", None),
 ("p8", 3, "", "Die Stadt will mit der Miete *keinen* *Gewinn* machen.", None),
 ("p9", 3, "", "Und das *Gesetz* *deckelt,* wie viel Miete sie verlangen darf.", None),
 ("p10", 4, "", "Einziehen dürfen *nicht* *nur* Menschen mit *wenig* *Geld.*", None),
 ("p11", 4, "", "Auch wer *normal* *verdient* und eine Wohnung *braucht,* kann sich *bewerben.*", None),
 ("p12", 4, "", "So zahlen viele *Wiener* *deutlich* *weniger* als bei *privaten* *Vermietern.*", None),
 ("p13", 2, "", "Und im *teuren* *München?*", None),
 ("p14", 2, "", "Dort gehört der Stadt *nicht* *mal* jede *zehnte* *Wohnung.*", None),
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

# ================= Bühne: Karte DE/AT -> Kameraflug in eine Wiener Straße -> Deutschland/Dresden -> Wien -> München =================
GEO = json.load(open("geo.json")); L0, B0, KX, KY = GEO["L0"], GEO["B0"], GEO["KX"], GEO["KY"]
def WX(lon): return (lon - L0) * KX
def WY(lat): return (B0 - lat) * KY
TQ = "#19C6B4"; PUR = "#7B3FE4"; RED = "#E5484D"; TQD = "#0E8C80"; PURS = "#5B2BB5"; GR = "#3F434C"; INK = "#2B2D35"
FX0, FY0 = 540, 880
WIEN = (WX(16.37), WY(48.21)); MUC = (WX(11.58), WY(48.14)); DRE = (WX(13.74), WY(51.05))
BER = (WX(13.40), WY(52.52)); KIEL = (WX(10.13), WY(54.32))
HX, HY = WX(13.0), WY(50.0)
GX, GY = WX(11.6), WY(52.0)
SX, SY = round(WIEN[0], 1), round(WIEN[1], 1)
ZS = 50.0
def SC(x, y): return [round(SX + x / ZS, 3), round(SY + y / ZS, 3)]
FIN = [round((WIEN[0] + MUC[0]) / 2, 1), round(WIEN[1] + 30, 1)]
cam = [
 ["p1", -0.2, HX, HY, 1.0], ["p1@Miete", 0.25, HX + 12, HY + 8, 1.05],
 ["p2@selbst", 0.0, *SC(0, -40), 28],
 ["p3", -0.1, *SC(0, -40), 28], ["p3@Gemeindewohnungen", 0.2, *SC(0, -70), 40],
 ["p4", 0.05, *SC(0, -70), 40], ["p4@Jahren", 0.3, *SC(0, -150), 24],
 ["p4@verkauft", 0.35, *SC(0, -150), 24], ["p5@Städte", 0.1, GX, GY, 1.3],
 ["p5@verkauft", 0.1, GX + 10, GY + 8, 1.34], ["p6@2006", 0.0, DRE[0], DRE[1] + 70, 2.4],
 ["p6@Gewinn", 0.3, DRE[0] + 6, DRE[1] + 72, 2.5], ["p7@günstig", 0.0, *SC(0, 60), 44],
 ["p13@teuren", -0.1, *SC(-30, 60), 46], ["p13@München", 0.3, MUC[0] + 40, MUC[1] - 40, 2.0],
 ["p14", 0.3, FIN[0], FIN[1] - 120, 1.25], ["end", 0, FIN[0], FIN[1] - 120, 1.25],
]
hero_kf = {}
def path(d, fill, stroke, cls="ol", extra=""): return f'<path class="{cls}" d="{d}" fill="{fill}" stroke="{stroke}" stroke-linejoin="round" {extra}/>'
other = "".join(path(d, "#FFFFFF", "#9AA0AA") for d in GEO["other"])

# ---- Straßenszene Wien (Szenen-px; Boden bei y=260) ----
def house(cx, w, h, fill, stroke=INK, win="#DDE2EA", roof=True, idd=""):
    x0 = cx - w / 2; y0 = 260 - h
    s = f'<g {f"id={chr(34)}{idd}{chr(34)}" if idd else ""}>'
    s += f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="4"/>'
    if roof: s += f'<path d="M{x0-12} {y0} L{x0+20} {y0-34} H{x0+w-20} L{x0+w+12} {y0} Z" fill="#B9BDC6" stroke="{stroke}" stroke-width="4" stroke-linejoin="round"/>'
    cols = max(2, int(w // 62)); rows = max(2, int((h - 90) // 78))
    gx = w / cols
    for r in range(rows):
        for c in range(cols):
            wx = x0 + c * gx + gx / 2 - 15; wy = y0 + 26 + r * 78
            s += f'<rect x="{wx:.0f}" y="{wy:.0f}" width="30" height="44" rx="3" fill="{win}" stroke="{stroke}" stroke-width="2.5"/>'
    s += f'<rect x="{cx-26}" y="{200}" width="52" height="60" fill="#8A8F99" stroke="{stroke}" stroke-width="3"/></g>'
    return s
# Gemeindebau (Hauptdarsteller): breiter Block mit Torbogen, Fahne, Schild
GW, GH = 460, 470
gx0 = -GW / 2; gy0 = 260 - GH
gem = f'<g id="gemb"><rect id="gemfill" x="{gx0}" y="{gy0}" width="{GW}" height="{GH}" fill="#FFFFFF" stroke="{INK}" stroke-width="5"/>'
for r in range(4):
    for c in range(6):
        if r == 3 and c in (2, 3): continue
        gem += f'<rect x="{gx0+22+c*72}" y="{gy0+30+r*86}" width="34" height="50" rx="3" fill="#E9E1FB" stroke="{INK}" stroke-width="2.5"/>'
gem += (f'<path d="M-62 260 V176 Q-62 120 0 120 Q62 120 62 176 V260" fill="#5B2BB5" stroke="{INK}" stroke-width="4"/>'
        f'<path d="M-40 260 V182 Q-40 142 0 142 Q40 142 40 182 V260" fill="#2B1660"/>'
        f'<g id="gsign" style="opacity:0"><rect x="-205" y="{gy0+8}" width="410" height="0"/>'
        f'<rect x="-290" y="-150" width="580" height="84" rx="8" fill="#FFFFFF" stroke="{PUR}" stroke-width="6"/>'
        f'<text x="0" y="-94" text-anchor="middle" font-family="JBM" font-weight="800" font-size="46" fill="{PURS}">GEMEINDEWOHNUNGEN</text></g>'
        f'<path d="M0 {gy0} V{gy0-120}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
        f'<g id="gflag" style="opacity:0"><path d="M0 {gy0-120} H150 V{gy0-78} H0 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>'
        f'<rect x="0" y="{gy0-120}" width="150" height="14" fill="{RED}"/><rect x="0" y="{gy0-92}" width="150" height="14" fill="{RED}"/></g>'
        f'</g>')
# Hintergrund: Wien baut weitere Gemeindebauten (Silhouetten hinter der Straße)
bg = ""
BGX = [-1180, -940, -700, -560, 560, 700, 940, 1180, -320, 320]
for k, x in enumerate(BGX):
    h_ = 300 + (k * 53) % 140
    bg += (f'<g class="bgb" data-k="{k}" style="opacity:0"><g transform="translate({x},-40)"><g class="bgs">'
           f'<rect x="-90" y="{-h_}" width="180" height="{h_}" fill="#EFE7FD" stroke="{PUR}" stroke-width="4"/>'
           + "".join(f'<rect x="{-66+c*48}" y="{-h_+22+r*60}" width="22" height="32" fill="#D6C6F7"/>' for r in range(int(h_ // 60) - 1) for c in range(3))
           + '</g></g></g>')
houses = (house(-860, 340, 380, "#F4F5F7") + house(-440, 320, 420, "#F7F4EE") + gem
          + house(440, 330, 400, "#EEF2F5") + house(860, 340, 360, "#F6F2F0"))
# ZU VERKAUFEN-Schild (wird durchgestrichen)
sale = (f'<g id="sale" style="opacity:0"><g transform="translate(300,262) scale(1.9) translate(-300,-262)"><path d="M300 262 V150" stroke="#7A5A3A" stroke-width="8" stroke-linecap="round"/>'
        f'<rect x="196" y="70" width="210" height="84" rx="6" fill="#FFF7D6" stroke="{INK}" stroke-width="4"/>'
        f'<text x="301" y="104" text-anchor="middle" font-family="JBM" font-weight="800" font-size="25" fill="{INK}">ZU</text>'
        f'<text x="301" y="136" text-anchor="middle" font-family="JBM" font-weight="800" font-size="25" fill="{INK}">VERKAUFEN</text>'
        f'<path id="salex" d="M188 62 L414 162 M414 62 L188 162" stroke="{RED}" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></g></g>')
# Menschen, die zur Tür gehen (p10/p11)
def person(col, tie=False, idd=""):
    s = (f'<g id="{idd}" style="opacity:0"><circle cx="0" cy="-118" r="22" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>'
         f'<path d="M-30 -2 V-70 Q-30 -92 0 -92 Q30 -92 30 -70 V-2 Z" fill="{col}" stroke="{INK}" stroke-width="4"/>'
         f'<g class="legs"><path class="lg1" d="M-12 -4 V40" stroke="{INK}" stroke-width="9" stroke-linecap="round"/><path class="lg2" d="M12 -4 V40" stroke="{INK}" stroke-width="9" stroke-linecap="round"/></g>')
    if tie: s += f'<path d="M0 -90 L-7 -70 L0 -40 L7 -70 Z" fill="{PUR}" stroke="{INK}" stroke-width="2"/>'
    return s + '</g>'
people = person("#9AD7CF", False, "pa") + person("#F2C230", True, "pb") + person("#C9CCD3", False, "pc")
scene = (
  '<defs><pattern id="mmp" width="50" height="50" patternUnits="userSpaceOnUse"><rect width="50" height="50" fill="#FCFCFD"/>'
  '<path d="M0 0.5H50M0.5 0V50" stroke="rgba(11,11,16,.09)" stroke-width="1"/>'
  + "".join(f'<path d="M0 {k*10+.5}H50M{k*10+.5} 0V50" stroke="rgba(11,11,16,.035)" stroke-width="1"/>' for k in range(1, 5)) + '</pattern></defs>'
  '<rect x="-2400" y="-1800" width="4800" height="3400" fill="url(#mmp)"/>'
  + bg +
  f'<rect x="-2400" y="260" width="4800" height="1200" fill="#EEF0F4"/><path d="M-2400 260 H2400" stroke="{INK}" stroke-width="3"/>'
  + houses + sale + f'<g id="ppl" transform="translate(0,200)">{people}</g>'
)
mapsvg = (f'<svg id="world" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">'
          f'<g id="camg"><g id="mapl">{other}'
          + path(GEO["at"], "#FFFFFF", INK, "ol", 'id="atp"') + path(GEO["de"], "#FFFFFF", INK, "ol", 'id="dep"')
          + f'</g><g id="scn" transform="translate({SX},{SY}) scale({1/ZS})" style="opacity:0">{scene}</g></g></svg>')
stage.append(mapsvg); stage.append('<div id="headbg"></div>')

# --- Labels, die an der Karte hängen ---
def glab(x, y, inner, i, o, d=0, idd="", sfx="none"):
    ii = f' id="{idd}"' if idd else ""
    return (f'<div class="geo" data-x="{x:.1f}" data-y="{y:.1f}"><div class="el"{ii} {A(i, o, d)} data-sfx="{sfx}" style="left:0;top:0;transform-origin:0 0">'
            f'<div style="transform:translate(-50%,-50%)">{inner}</div></div></div>')
def maplab(t, col): return f'<span class="mono lab" style="color:{col};border-color:{col}">{t}</span>'
FLAG_DE = '<span class="flag v"><i style="background:#111"></i><i style="background:#D33A3A"></i><i style="background:#F2C230"></i></span>'
FLAG_AT = '<span class="flag v"><i style="background:#D33A3A"></i><i style="background:#fff"></i><i style="background:#D33A3A"></i></span>'
def hic(col, w=46, stroke=INK):
    return (f'<svg viewBox="0 0 48 48" width="{w}" height="{w}"><path d="M6 22 L24 7 L42 22 V43 H6 Z" fill="{col}" stroke="{stroke}" stroke-width="3.2" stroke-linejoin="round"/>'
            f'<rect x="19" y="29" width="10" height="14" fill="#fff" stroke="{stroke}" stroke-width="2.4"/></svg>')
FIVE = ('<div class="col" style="gap:6px"><div class="huge" id="q5" style="font-size:90px;color:' + PUR + ';letter-spacing:0">?</div><div class="row" style="gap:6px;background:rgba(255,255,255,.94);border-radius:12px;padding:8px 10px;box-shadow:0 2px 10px rgba(26,31,51,.18)">'
        + "".join(f'<span class="h5" data-k="{k}">{hic(PUR if k == 2 else "#E6E7EB", 66)}</span>' for k in range(5)) + '</div></div>')
def redtag(t): return f'<span class="mono lab" style="color:#fff;background:{RED};border-color:{RED}">✕ {t}</span>'
geo = (glab(WX(10.2), WY(52.2), maplab("DEUTSCHLAND", GR), "p1", "p6", -0.6)
       + glab(WX(14.4), WY(47.35), maplab("ÖSTERREICH", GR), "p1", "p2", -0.6)
       + glab(WIEN[0] - 40, WIEN[1] - 150, FIVE, "p1", "p2@selbst", -0.6, "", "none")
       + glab(WIEN[0], WIEN[1] + 34, maplab("WIEN", PURS), "p1", "p2@selbst", -0.6)
       + glab(KIEL[0], KIEL[1], redtag("KIEL"), "p5@Städte", "p6", -0.05, "", "marker")
       + glab(BER[0], BER[1], redtag("BERLIN, TEILE"), "p5@Städte", "p6", 0.25, "", "marker")
       + glab(DRE[0], DRE[1], redtag("DRESDEN"), "p5@verkauft", "p7", -0.2, "", "marker")
       + glab(MUC[0], MUC[1], maplab("MÜNCHEN", GR), "p13@München", "end", -0.1, "", "marker")
       + glab(WIEN[0], WIEN[1], maplab("WIEN", PURS), "p14", "end", -0.1, "", "none"))
stage.append(f'<div id="geol">{geo}</div>')

def chip_(txt, i, o, col=PURS, sfx="marker", y=1150, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;font-weight:800;gap:12px;padding:12px 22px;border-color:{col};color:{col};background:rgba(255,255,255,.97);white-space:nowrap">{txt}</div>', 80, y, A(i, o, d) + f' data-sfx="{sfx}"', 920, CENTER)
# p2: Eigentümerin
stage.append(chip_(f'{FLAG_AT}&nbsp;EIGENTÜMERIN: STADT WIEN', "p2@Stadt", "p3@Gemeindewohnungen", PURS, "glass", 250, 38))
# p4: 100 Jahre
YRS = (f'<div class="col" style="gap:4px"><div class="row" style="gap:18px;align-items:baseline"><div class="huge num" style="font-size:170px;color:{PURS}">{cnt(100, "p4@hundert", 0, 0)}</div>'
       f'<div class="mono" style="font-size:44px;font-weight:800;color:{PURS}">JAHRE</div></div>'
       f'<div class="mono" style="font-size:26px;font-weight:800;color:#5D616B;white-space:nowrap">STADT WIEN BAUT SELBST · SEIT 1923</div></div>')
stage.append(el(YRS, 80, 210, A("p4@hundert", "p4@nie", -0.2) + ' data-sfx="glass"', 920, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:52px;padding:14px 30px;color:' + TQD + ';border-color:' + TQD + '">NIE VERKAUFT</div>', 80, 290, A("p4@verkauft", "p5", -0.1), 920, CENTER))
# p6: Dresden 2006 -> Finanzinvestor
BRIEF = (f'<svg viewBox="0 0 64 56" width="96" height="84"><rect x="4" y="14" width="56" height="38" rx="6" fill="{GR}" stroke="{INK}" stroke-width="3"/>'
         f'<path d="M22 14 V8 Q22 4 26 4 H38 Q42 4 42 8 V14" fill="none" stroke="{INK}" stroke-width="3"/>'
         f'<text x="32" y="42" text-anchor="middle" font-family="Unbounded" font-weight="700" font-size="22" fill="#F2C230">€</text></svg>')
DRES = (f'<div class="col" style="gap:10px"><div class="row" style="gap:20px;align-items:baseline"><div class="mono" style="font-size:34px;font-weight:800;color:{RED}">DRESDEN</div>'
        f'<div class="huge" style="font-size:120px;color:{INK};letter-spacing:-3px">2006</div></div>'
        f'<div class="row" style="gap:22px"><div class="row" id="dh" style="gap:4px;flex-wrap:wrap;width:330px">'
        + "".join(f'<span class="h10" data-k="{k}">{hic(PUR, 58)}</span>' for k in range(10)) + '</div>'
        f'<div class="mono" id="darr" style="font-size:60px;color:{GR}">→</div><div class="col" id="dinv" style="gap:4px">{BRIEF}<div class="mono" style="font-size:22px;font-weight:800;color:{GR}">FINANZINVESTOR</div></div></div>'
        f'<div class="mono" style="font-size:24px;font-weight:800;color:#5D616B;white-space:nowrap">ALLE STÄDTISCHEN WOHNUNGEN VERKAUFT</div>'
        f'<div class="chip mono" id="dgew" style="font-size:28px;font-weight:800;color:{RED};border-color:{RED};background:#fff;opacity:0">ZIEL: GEWINN</div></div>')
stage.append(card(DRES, 120, 190, 840, 470, "", A("p6@2006", "p7", -0.15) + ' data-sfx="glass"'))
# p7: Frage
stage.append(chip_('WARUM GÜNSTIG?', "p7@warum", "p8", PURS, "marker", 250, 44))
# p8/p9: Miete = Kosten (+ Gewinn) ; Deckel
MIE = (f'<div class="row" style="gap:46px;align-items:flex-end;height:440px">'
       f'<div class="col" style="gap:8px;justify-content:flex-end;height:440px;position:relative">'
       f'<div id="lid" style="position:absolute;left:-20px;width:300px;height:20px;border-radius:8px;background:{PUR};box-shadow:0 4px 12px rgba(91,43,181,.4);opacity:0"></div>'
       f'<div id="gew" style="width:260px;height:130px;background:repeating-linear-gradient(45deg,{RED} 0 10px,#F07A7E 10px 20px);border:3px solid {INK};border-bottom:none;display:flex;align-items:center;justify-content:center;position:relative">'
       f'<span class="mono" style="font-size:34px;font-weight:800;color:#fff">GEWINN</span><span id="gx" class="mono" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:110px;color:{INK};font-weight:800;opacity:0">✕</span></div>'
       f'<div style="width:260px;height:240px;background:{TQ};border:3px solid {INK};display:flex;align-items:center;justify-content:center">'
       f'<span class="mono" style="font-size:32px;font-weight:800;color:#fff;text-align:center">KOSTEN<br>BAU UND<br>PFLEGE</span></div>'
       f'<div class="mono" style="font-size:36px;font-weight:800;color:{INK}">MIETE</div></div>'
       f'<div class="col" style="gap:30px;align-items:flex-start;width:420px;padding-bottom:120px">'
       f'<div class="mono" id="mt1" style="font-size:36px;font-weight:800;color:{RED};opacity:0">✕ KEIN GEWINN NÖTIG</div>'
       f'<div class="mono" id="mt2" style="font-size:36px;font-weight:800;color:{PURS};opacity:0">▬ GESETZ: OBERGRENZE<br>FÜR DIE MIETE</div></div></div>')
stage.append(card(MIE, 90, 160, 900, 540, "", A("p8", "p10", -0.1) + ' data-sfx="glass"'))
# p10/p11
stage.append(chip_('NICHT NUR MIT WENIG GELD', "p10@nicht", "p11", GR, "marker", 250, 40))
stage.append(chip_('✓ AUCH NORMALVERDIENER – BEI BEDARF', "p11@normal", "p12", TQD, "success", 250, 34))
# p12: Vergleich Miete pro m²
def hbar(lbl, val, w, col, anchor, d):
    return (f'<div class="col" style="align-items:flex-start;gap:8px;width:780px"><div class="mono" style="font-size:26px;font-weight:800;color:#5D616B">{lbl}</div>'
            f'<div class="row" style="gap:18px"><div class="mbar" data-w="{w}" data-a="{anchor}" data-dd="{d}" style="height:64px;width:0;background:{col};border-radius:12px"></div>'
            f'<div class="huge" style="font-size:66px;letter-spacing:-1px;color:{col}">{cnt(val, anchor, 2, d)}&nbsp;€</div></div></div>')
CMP = (f'<div class="col" style="gap:24px;align-items:flex-start">'
       + hbar("GEMEINDEWOHNUNG", 5.4, 300, TQD, "p12@Wiener", 0)
       + hbar("PRIVAT VERMIETET", 9.1, 505, RED, "p12@deutlich", 0)
       + f'<div class="mono" style="font-size:20px;font-weight:700;color:#8A8F99">MIETE PRO M² OHNE BETRIEBSKOSTEN · Ø ÖSTERREICH 2024</div></div>')
stage.append(card(CMP, 90, 190, 900, 470, "", A("p12", "p13", -0.1) + ' data-sfx="glass"'))
# p14: Auflösung
def row10(rid, col):
    return f'<div class="row" id="{rid}" style="gap:4px">' + "".join(f'<span class="r10" data-k="{k}" style="position:relative;display:inline-block;width:66px;height:66px">{hic("#E6E7EB", 66, "#9AA0AA")}<span class="fillc" style="position:absolute;left:0;top:0;height:66px;overflow:hidden;width:0">{hic(col, 66)}</span></span>' for k in range(10)) + '</div>'
FIN_ = (f'<div class="col" style="gap:22px">'
        f'<div class="col" style="gap:6px"><div class="row" style="gap:14px">{FLAG_AT}<div class="mono" style="font-size:30px;font-weight:800;color:{PURS}">WIEN</div></div>'
        f'<div class="huge" style="font-size:96px;color:{PURS};letter-spacing:-2px">JEDE 5.</div>{row10("rw", PUR)}</div>'
        f'<div class="col" style="gap:6px"><div class="row" style="gap:14px">{FLAG_DE}<div class="mono" style="font-size:30px;font-weight:800;color:{GR}">MÜNCHEN</div></div>'
        f'<div class="huge" style="font-size:66px;color:{GR};letter-spacing:-1px;white-space:nowrap">NICHT MAL JEDE 10.</div>{row10("rm", "#8A8F99")}</div>'
        f'<div class="mono" style="font-size:22px;font-weight:800;color:#5D616B">WOHNUNGEN IM BESITZ DER STADT</div></div>')
stage.append(card(FIN_, 60, 150, 960, 700, "active", A("p14", "end", -0.1) + ' data-sfx="glass"'))
# dezente Hinweise
stage.append(el('<div class="note mono">SZENE SCHEMATISCH</div>', 40, 1252, A("p2@selbst", "p5", 0.2) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">VERKÄUFE: KIEL 1999, BERLIN (GSW) 2004, DRESDEN (WOBA) 2006</div>', 40, 1252, A("p5", "p7", 0.2) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">QUELLE: STATISTIK AUSTRIA, WOHNEN 2024</div>', 40, 1252, A("p12", "p13", 0.2) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">QUELLEN: STATISTIK AUSTRIA 2024 (21 % DER HAUSHALTE) · STADT MÜNCHEN 2026 (≈ 75.000 VON 843.000)</div>', 40, 1252, A("p14", "end", 0.2) + ' data-sfx="none"'))
CAMJS = json.dumps(cam)

SCENE_JS = r''' // ---- Bühne ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const K=PAN.cam.map(k=>[TS(k[0],k[1]),k[2],k[3],k[4]]);
  const sm=u=>u*u*(3-2*u);
  let C=K[0]; if(t>=K[K.length-1][0]) C=K[K.length-1]; else if(t>K[0][0]) for(let i=0;i<K.length-1;i++){ const a=K[i],q=K[i+1]; if(t>=a[0]&&t<q[0]){ const u=sm((t-a[0])/Math.max(1e-6,q[0]-a[0]));
     const z=Math.exp(Math.log(a[3])+(Math.log(q[3])-Math.log(a[3]))*u);
     const w=(1/z-1/a[3])/((1/q[3]-1/a[3])||1e-9); const v=(Math.abs(q[3]-a[3])<1e-6)?u:cl(w,0,1);
     C=[t,a[1]+(q[1]-a[1])*v,a[2]+(q[2]-a[2])*v,z]; break; } }
  const fx=C[1], fy=C[2], z=C[3];
  const FX0=PAN.FX0, FY0=PAN.FY0;
  document.getElementById('camg').setAttribute('transform',`translate(${FX0},${FY0}) scale(${z}) translate(${-fx},${-fy})`);
  const pj=(x,y)=>[FX0+(x-fx)*z, FY0+(y-fy)*z];
  document.querySelectorAll('.ol').forEach(e=>e.setAttribute('stroke-width',(1.8/z).toFixed(4)));
  const sA=pr(z,7,12); const ML=document.getElementById('mapl');
  ML.style.opacity=(1-pr(z,20,8)); ML.style.display=z>30?'none':'';
  const SCN=document.getElementById('scn'); SCN.style.opacity=sA; SCN.style.display=sA<0.005?'none':'';
  // Länderflächen
  const pulse=0.5+0.5*Math.sin(t*2*Math.PI/1.2);
  const atOn=1-pr(t,TS('p5',-0.3),0.4)+pr(t,TS('p14',-0.2),0.4);
  document.getElementById('atp').setAttribute('fill',`rgba(123,63,228,${(0.06+0.16*cl(atOn,0,1)).toFixed(3)})`);
  const deOn=pr(t,TS('p5',-0.2),0.4)*(1-pr(t,TS('p7',0),0.3));
  document.getElementById('dep').setAttribute('fill',`rgba(229,72,77,${(0.04+0.10*deOn).toFixed(3)})`);
  // Hook: 5 Häuser, das dritte pulsiert
  document.querySelectorAll('.h5').forEach(h=>{ const k=+h.dataset.k; const u=pr(t,-0.2+k*0.12,0.25); h.style.opacity=0.35+0.65*u; h.style.display='inline-block';
    h.style.transform=k===2?`translateY(${(-6*pulse).toFixed(1)}px) scale(${(1.12+0.08*pulse).toFixed(3)})`:'none'; });
  document.getElementById('q5').style.transform=`scale(${(1+0.08*pulse).toFixed(3)})`;
  // Szene: Fahne, Schild, Füllung
  const own=pr(t,TS('p2@Stadt',-0.1),0.3);
  document.getElementById('gflag').style.opacity=own;
  document.getElementById('gflag').setAttribute('transform',`translate(0,${(0).toFixed(1)}) skewY(${(2*Math.sin(t*5)).toFixed(2)})`);
  document.getElementById('gemfill').setAttribute('fill',`rgba(123,63,228,${(0.05+0.14*own).toFixed(3)})`);
  document.getElementById('gsign').style.opacity=pr(t,TS('p3@Gemeindewohnungen',-0.15),0.25);
  // Hintergrund-Gemeindebauten wachsen
  document.querySelectorAll('.bgb').forEach(g=>{ const k=+g.dataset.k; const u=pr(t,TS('p4@hundert',-0.1)+k*0.11,0.3); g.style.opacity=u>0?1:0;
    g.querySelector('.bgs').setAttribute('transform',`scale(1,${(0.02+0.98*(1-Math.pow(1-u,3))).toFixed(3)})`); });
  // Verkaufsschild + Kreuz
  const so=pr(t,TS('p4@Firmen',-0.25),0.2)*(1-pr(t,TS('p5',0),0.2)); document.getElementById('sale').style.opacity=so;
  document.getElementById('salex').setAttribute('stroke-dashoffset',(1-ease(pr(t,TS('p4@verkauft',-0.15),0.3))).toFixed(3));
  // Menschen gehen zur Tür
  const P3=[['pa','p10@nicht',-560],['pb','p11@normal',-620],['pc','p10@wenig',-700]];
  P3.forEach(([id,a,x0],i)=>{ const t0=TS(a,-0.3); const u=pr(t,t0,1.6); const x=x0+(x0<0?-x0:0)*sm(u)-(i===1?0:0);
    const e=document.getElementById(id); const vis=t>t0-0.1&&t<TS('p12',0);
    const gone=pr(t,t0+1.45,0.25); e.style.opacity=vis?(1-gone):0;
    const step=Math.sin((t-t0)*11)*(u<1?1:0);
    e.setAttribute('transform',`translate(${x.toFixed(1)},${(Math.abs(step)*-6).toFixed(1)}) scale(${(1.5*(1-0.25*gone)).toFixed(3)})`);
    e.querySelector('.lg1').setAttribute('transform',`rotate(${(18*step).toFixed(1)} -12 -4)`);
    e.querySelector('.lg2').setAttribute('transform',`rotate(${(-18*step).toFixed(1)} 12 -4)`); });
  // Dresden: Häuser werden grau und wandern zum Investor
  document.querySelectorAll('.h10').forEach(h=>{ const k=+h.dataset.k; const u=pr(t,TS('p6@Finanzinvestor',-0.3)+k*0.05,0.3);
    h.style.display='inline-block'; h.style.filter=`grayscale(${u.toFixed(2)})`; h.style.opacity=1-0.45*u;
    h.style.transform=`translateX(${(40*ease(u)).toFixed(1)}px)`; });
  document.getElementById('dinv').style.opacity=pr(t,TS('p6@Finanzinvestor',-0.2),0.25);
  document.getElementById('darr').style.opacity=pr(t,TS('p6@Finanzinvestor',-0.35),0.25);
  document.getElementById('dgew').style.opacity=pr(t,TS('p6@Gewinn',-0.15),0.2);
  // Miete: Gewinn fällt weg, Deckel kommt
  const gk=pr(t,TS('p8@keinen',0.0),0.25), gs=ease(pr(t,TS('p8@Gewinn',0.2),0.45));
  document.getElementById('gx').style.opacity=gk*(1-gs);
  const G=document.getElementById('gew'); G.style.height=(130*(1-gs)).toFixed(1)+'px'; G.style.opacity=1-gs;
  document.getElementById('mt1').style.opacity=gk;
  const ld=pr(t,TS('p9@deckelt',-0.25),0.22); const L_=document.getElementById('lid');
  L_.style.opacity=ld; L_.style.bottom=(50+240+4+300*(1-ease(ld))).toFixed(1)+'px';
  document.getElementById('mt2').style.opacity=pr(t,TS('p9@Gesetz',-0.1),0.25);
  // Balken p12
  document.querySelectorAll('.mbar').forEach(b=>{ b.style.width=(+b.dataset.w*ease(pr(t,TS(b.dataset.a,+b.dataset.dd),0.8))).toFixed(1)+'px'; });
  // Auflösung: Häuserreihen füllen sich
  for(const [rid,v,a] of [['rw',2,'p14'],['rm',0.89,'p14@zehnte']]){
    const f=v*ease(pr(t,TS(a,-0.1),0.9));
    document.querySelectorAll('#'+rid+' .r10').forEach(r=>{ const k=+r.dataset.k; const w=cl(f-k,0,1); r.querySelector('.fillc').style.width=(66*w).toFixed(1)+'px'; });
  }
  // Labels an der Karte
  document.getElementById('geol').style.opacity=(1-pr(z,3.2,2.5))*(1-pr(t,END,0.3));
  for(const gg of document.querySelectorAll('.geo')){ const [sx,sy]=pj(+gg.dataset.x,+gg.dataset.y); gg.style.left=sx+'px'; gg.style.top=sy+'px'; }
  document.getElementById('world').style.opacity=1-pr(t,END,0.35);
  const RB=document.getElementById('robot'); RB.style.left=(t>=END?40:770)+'px'; RB.style.top=(t>=END?790:470)+'px';
  document.getElementById('headbg').style.opacity=1-pr(t,TS('p2',-0.15),0.3);
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
#persp{{position:absolute;left:0;top:0;width:1080px;height:1920px;perspective:1150px;perspective-origin:540px 640px;overflow:hidden;background:linear-gradient(#ECEEF8,#FFFFFF 55%)}}
#plane{{position:absolute;transform-style:preserve-3d;transform-origin:50% 50%;
background:linear-gradient(rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(90deg,rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,
linear-gradient(rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,linear-gradient(90deg,rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,#FCFCFD}}
.pop{{position:absolute;left:0;top:0;transform-origin:50% 100%;transform-style:preserve-3d}}
.orb{{width:100%;height:100%;border-radius:50%;background:radial-gradient(circle,#FFFFFF 0 22%,#19C6B4 45%,rgba(25,198,180,0) 72%)}}
#headbg{{position:absolute;left:0;top:0;width:1080px;height:560px;background:linear-gradient(rgba(255,255,255,.97) 60%,rgba(255,255,255,0))}}
#head{{top:200px;z-index:3}}
.geo{{position:absolute;width:0;height:0}}
.lab{{font-size:26px;font-weight:800;background:rgba(255,255,255,.94);border:2.5px solid;border-radius:8px;padding:5px 12px;white-space:nowrap}}
.flag{{display:inline-flex;width:54px;height:36px;border-radius:5px;overflow:hidden;box-shadow:0 0 0 2px rgba(26,31,51,.25);vertical-align:middle}} .flag i{{flex:1}}
.flag.v{{flex-direction:column}}
.col .flag{{width:96px;height:64px;margin-bottom:6px}}
.num{{font-size:150px;letter-spacing:-6px;white-space:nowrap;text-shadow:0 0 18px #fff,0 0 8px #fff}} .pc{{font-size:76px;letter-spacing:0;margin-left:6px}}
#y30{{text-shadow:0 0 18px #fff,0 0 8px #fff}}
.hero{{position:absolute;left:0;top:0;transform-origin:50% 100%;z-index:2}}
.grid{{display:grid;grid-template-columns:repeat(10,38px);gap:8px;margin-top:10px}} .grid i{{width:38px;height:38px;border-radius:50%;background:#E6E7EB;display:block}}
#headbg{{height:470px}}
.note{{font-size:16px;color:#8A8F99;background:rgba(255,255,255,.9);border:1.5px solid #C9CCD3;border-radius:8px;padding:5px 9px;white-space:nowrap}}
</style></head><body><div id="v">
<div id="chap" class="mono"></div><div id="prog">{"".join("<div></div>" for _ in CH)}</div><div id="wm">{mono}</div>
<div id="head"></div>
{"".join(stage)}
{endcard}
<div id="robot">{robots}</div>
<div id="cap"><div id="pill"></div></div>
</div>
<script>
const PAN={json.dumps(dict(cam=cam,FX0=FX0,FY0=FY0,hero=hero_kf), ensure_ascii=False)};
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
 const H=document.getElementById('head'); H.innerHTML=b.head; H.style.fontSize='64px'; if(BEATS.indexOf(b)===0) hs=-1; const hp=ease(pr(t,hs,.3));
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
