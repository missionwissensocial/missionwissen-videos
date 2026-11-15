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
HOOK = 'Das tiefste <span style="color:#7B3FE4">Loch</span> der Welt'

# ---------- beats ----------
CH = ["", "", "", "", "", ""]
HOOK = 'Chinesische Mauer: vom <span style="color:#7B3FE4">Weltall</span> aus sichtbar?'
B = [
 ("s1", 0, HOOK, "Kann man die *Chinesische* *Mauer* vom *Weltall* aus *sehen?*", "staunt"),
 ("s2", 0, HOOK, "Fast jeder hat schon mal gehört: *Ja,* *das* *geht.*", "denkt"),
 ("s3", 1, "", "Die Mauer ist zwar über *20.000* *Kilometer* lang – alle *Abschnitte* zusammengezählt.", None),
 ("s4", 1, "", "Aber meist *nicht* *mal* *sechs* *Meter* breit.", None),
 ("s5", 2, "", "Die *Raumstation* *ISS* kreist rund *400* *Kilometer* über der Erde.", None),
 ("s6", 2, "", "Von dort die Mauer zu *entdecken* ist so, als würdest du ein *Haar* aus *sieben* *Metern* Entfernung suchen.", None),
 ("s7", 3, "", "Und die Mauer ist aus *Steinen* und *Erde* der *Umgebung* gebaut.", None),
 ("s8", 3, "", "Sie hat also fast *dieselbe* *Farbe* wie der *Boden.*", None),
 ("s9", 4, "", "Chinas *erster* *Astronaut* sagte *2003:* „Ich habe sie *nicht* *gesehen.“", None),
 ("s10", 4, "", "Und vom *Mond* aus?", None),
 ("s11", 4, "", "Der Mond ist fast *tausendmal* weiter weg als die *ISS.*", None),
 ("s12", 4, "", "*Keine* *Chance.*", None),
 ("s13", 5, "", "Der *Irrtum* stand schon *1932* in einem *Zeitungs-Comic.*", None),
 ("s14", 5, "", "Damals konnte das *niemand* *überprüfen.*", None),
 ("s15", 5, "", "Seitdem wird er einfach *weitererzählt.*", None),
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
END=round(AUD+0.7,3); TOTAL=AUD+3.95
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
import math, random as _r
_r.seed(11)
PURS = "#5B2BB5"; GR = "#3F434C"; TQD = "#0E8C80"; HOT = "#E5484D"
STOP = 300; STH = 980
GEO = json.load(open("geo.json")); RE = GEO["R"]; BX, BY = GEO["bad"]
ORB = RE * 6771 / 6371          # ISS-Bahn, massstabsgetreu (400 km)
MOONX = RE * 384400 / 6371      # Mondabstand massstabsgetreu
MOONR = RE * 1737 / 6371
ISSA = -118.0                   # Winkel (Grad) der ISS beim Zoom (s6)
IX, IY = ORB * math.cos(math.radians(ISSA)), ORB * math.sin(math.radians(ISSA))
ZM = 0.034                      # Zoom Erde-Mond

# ---------- Welt (Globus + Mond, eine durchgehende Kamera) ----------
wall_paths = "".join(f'<path id="w{k}" class="wall" d="{GEO["walls"][n]}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0" fill="none" stroke="{PUR}" stroke-linecap="round" stroke-linejoin="round"/>'
                     for k, n in enumerate(["ming", "han", "nord", "jin"]))
world = (f'<svg id="wsvg" width="1080" height="{STH}" style="position:absolute;left:0;top:0;overflow:hidden"><defs>'
         '<radialGradient id="g_oc" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#F3F9FD"/><stop offset=".75" stop-color="#DDEBF5"/><stop offset="1" stop-color="#C9DCEB"/></radialGradient>'
         '<radialGradient id="g_moon" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#C9CDD6"/></radialGradient>'
         f'<clipPath id="gclip"><circle cx="0" cy="0" r="{RE}"/></clipPath></defs>'
         '<g id="wg">'
         f'<circle id="atmo" r="{RE+18}" fill="none" stroke="#19C6B4" stroke-opacity=".18" stroke-width="30" vector-effect="non-scaling-stroke"/>'
         f'<circle r="{RE}" fill="url(#g_oc)"/>'
         f'<g clip-path="url(#gclip)"><path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
         f'<path id="cn" d="{GEO["cn"]}" fill="rgba(123,63,228,.10)" stroke="{PURS}" stroke-width="1.6" vector-effect="non-scaling-stroke"/>'
         f'<path d="{GEO["br"]}" fill="none" stroke="#B5BAC4" stroke-width="1" stroke-dasharray="3 3" vector-effect="non-scaling-stroke"/>'
         f'{wall_paths}</g>'
         f'<circle r="{RE}" fill="none" stroke="{INK}" stroke-width="2.4" vector-effect="non-scaling-stroke"/>'
         f'<circle id="orb" r="{ORB:.1f}" fill="none" stroke="{TQD}" stroke-linecap="round"/>'
         f'<path id="dim" d="M{RE*math.cos(math.radians(-150)):.1f} {RE*math.sin(math.radians(-150)):.1f}L{ORB*math.cos(math.radians(-150)):.1f} {ORB*math.sin(math.radians(-150)):.1f}" stroke="{PUR}" stroke-linecap="round"/>'
         f'<path id="emline" d="M{RE+30} 0H{MOONX-MOONR-30:.0f}" stroke="#9AA0AA" stroke-dasharray="8 8" vector-effect="non-scaling-stroke" stroke-width="2"/>'
         f'<circle id="moon" cx="{MOONX:.1f}" cy="0" r="{MOONR:.1f}" fill="url(#g_moon)" stroke="{INK}" stroke-width="2" vector-effect="non-scaling-stroke"/>'
         '</g></svg>')
def wpt(wx, wy, inner, gid):
    return f'<div class="xg" id="{gid}" data-x="{wx:.2f}" data-y="{wy:.2f}">{inner}</div>'
iss_svg = ('<svg width="150" height="90" viewBox="-75 -45 150 90" style="position:absolute;left:-75px;top:-45px;overflow:visible">'
           '<path d="M-62 0H62" stroke="#2B2D35" stroke-width="5" stroke-linecap="round"/>'
           + "".join(f'<rect x="{x}" y="{y}" width="22" height="34" rx="2" fill="#7B3FE4" stroke="#2B2D35" stroke-width="2.5"/><path d="M{x} {y+11}h22M{x} {y+23}h22" stroke="#B79BFF" stroke-width="1.5"/>'
                     for x in (-66, -40, 18, 44) for y in (-38, 4))
           + '<rect x="-14" y="-10" width="28" height="20" rx="6" fill="#ECEEF3" stroke="#2B2D35" stroke-width="3"/><rect x="-6" y="-22" width="12" height="44" rx="5" fill="#DCDFE6" stroke="#2B2D35" stroke-width="2.5"/></svg>')
kap_svg = ('<svg width="110" height="90" viewBox="-55 -45 110 90" style="position:absolute;left:-55px;top:-45px;overflow:visible">'
           '<rect x="-52" y="-9" width="26" height="18" rx="2" fill="#19C6B4" stroke="#2B2D35" stroke-width="2.5"/><rect x="26" y="-9" width="26" height="18" rx="2" fill="#19C6B4" stroke="#2B2D35" stroke-width="2.5"/>'
           '<rect x="-26" y="-3" width="52" height="6" fill="#8A8F99"/>'
           '<path d="M-16 -26H16L22 20H-22Z" fill="#ECEEF3" stroke="#2B2D35" stroke-width="3" stroke-linejoin="round"/><path d="M-22 20Q0 30 22 20" fill="#7B3FE4" stroke="#2B2D35" stroke-width="3"/>'
           '<circle cx="0" cy="-6" r="6" fill="#20202E" stroke="#2B2D35" stroke-width="2"/></svg>')
def lab(text, col=PURS, gid="", tr="translate(-50%,-140%)"):
    return f'<div class="mono lab" style="position:absolute;left:0;top:0;transform:{tr};color:{col};border-color:{col}">{text}</div>'
w_ov = (wpt(0, 0, f'<div id="issb" class="pz">{iss_svg}</div>', "iss")
        + wpt(0, 0, f'<div id="kapb" class="pz">{kap_svg}</div>', "kap")
        + wpt(GEO["china"][0] + 40, GEO["china"][1] + 95, '<div id="qhook"><div class="qb">?</div></div>', "qw")
        + wpt(0, -RE - 10, lab("ERDE", INK, "", "translate(-50%,-160%)"), "labearth")
        + wpt(MOONX, -MOONR, lab("MOND", INK, "", "translate(-50%,-160%)"), "labmoon")
        + wpt(MOONX, 0, '<div class="mring"></div>', "mring")
        + wpt(0, 0, '<div class="mring"></div>', "ering")
        + wpt(ORB * math.cos(math.radians(-150)), ORB * math.sin(math.radians(-150)), lab("400 KM", PUR, "", "translate(-108%,-120%)"), "labdim"))
stage.append(f'<div class="el" id="wwrap" data-in="s1" data-d="-1" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px">'
             f'{world}{w_ov}'
             + el('<div class="note mono">KARTE: NATURAL EARTH · MAUERVERLAUF SCHEMATISCH</div>', 18, STH - 46, A("s1", "s5", -1) + ' data-sfx="none"')
             + el('<div class="note mono">ERDE, ISS-BAHN UND MOND MASSSTABSGETREU</div>', 18, STH - 46, A("s5", "s13", 0.3) + ' data-sfx="none"')
             + '</div>')

# ---------- Boden-Szene: Querschnitt Mauer + Auto (s4) ----------
U = 52  # px pro Meter
GYL = 800
wx0 = 600; wtop = 6 * U; wh = 7.5 * U
wall_cs = (f'<path d="M{wx0-14} {GYL}L{wx0} {GYL-wh:.0f}H{wx0+wtop}L{wx0+wtop+14} {GYL}Z" fill="#D9C7A4" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
           + "".join(f'<path d="M{wx0+8} {GYL-wh+30+k*44:.0f}h{wtop-16}" stroke="#B59E76" stroke-width="2.5"/>' for k in range(8))
           + "".join(f'<rect x="{xx}" y="{GYL-wh-34:.0f}" width="26" height="34" fill="#D9C7A4" stroke="{INK}" stroke-width="3.5"/>' for xx in (wx0 - 2, wx0 + 34, wx0 + wtop - 60, wx0 + wtop - 24)))
person = (f'<g transform="translate({wx0+wtop/2:.0f} {GYL-wh:.0f})"><circle cx="0" cy="{-1.7*U+12:.0f}" r="11" fill="#7B3FE4"/>'
          f'<path d="M0 {-1.7*U+24:.0f}V-40M0 -40L-12 0M0 -40L12 0M0 {-1.7*U+38:.0f}L-16 -50M0 {-1.7*U+38:.0f}L16 -50" stroke="#7B3FE4" stroke-width="7" stroke-linecap="round"/></g>')
cx0 = 150; cl_ = 4.5 * U
car = (f'<g transform="translate({cx0} {GYL})"><path d="M8 -26Q6 -58 40 -60L80 -62Q100 -88 140 -88H175Q200 -88 215 -62L{cl_-14:.0f} -56Q{cl_:.0f} -52 {cl_:.0f} -30V-22H8Z" fill="#19C6B4" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
       '<path d="M92 -62Q108 -82 138 -82H150V-62ZM160 -82H174Q194 -82 206 -62H160Z" fill="#EAF6F8" stroke="#2B2D35" stroke-width="3"/>'
       + "".join(f'<circle cx="{x}" cy="-20" r="20" fill="#2B2D35"/><circle cx="{x}" cy="-20" r="8" fill="#ECEEF3"/>' for x in (54, cl_ - 52))
       + '</g>')
brk = (f'<path d="M{wx0} {GYL-wh-70:.0f}H{wx0+wtop}M{wx0} {GYL-wh-86:.0f}V{GYL-wh-54:.0f}M{wx0+wtop} {GYL-wh-86:.0f}V{GYL-wh-54:.0f}" stroke="{PUR}" stroke-width="5" stroke-linecap="round"/>'
       f'<path d="M{cx0} {GYL+38}H{cx0+cl_:.0f}M{cx0} {GYL+26}V{GYL+50}M{cx0+cl_:.0f} {GYL+26}V{GYL+50}" stroke="{GR}" stroke-width="3.5" stroke-linecap="round"/>'
       f'<text x="{cx0+cl_/2:.0f}" y="{GYL+82}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="{GR}">AUTO ≈ 4,5 M</text>')
ground = (f'<path d="M-20 {GYL}Q200 {GYL-10} 400 {GYL}T1100 {GYL}V1000H-20Z" fill="#EFE6D3" stroke="{INK}" stroke-width="4"/>'
          + "".join(f'<circle cx="{_r.randint(0,1080)}" cy="{_r.randint(GYL+20,960)}" r="{_r.randint(3,8)}" fill="#C9B48E"/>' for _ in range(40)))
gnd_svg = f'<svg width="1080" height="{STH}" style="position:absolute;left:0;top:0">{ground}{wall_cs}{person}{car}{brk}</svg>'
stage.append(f'<div class="el mapwrap" id="gnd" data-in="s1" data-d="-1" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px;opacity:0">{gnd_svg}'
             f'<div class="col" style="position:absolute;left:0;top:60px;width:1080px"><div class="mono" style="font-size:30px;font-weight:800;color:{PURS}">MEIST NICHT MAL</div>'
             f'<div class="huge2" style="color:{PURS};font-size:170px">6 M</div><div class="mono" style="font-size:26px;font-weight:800;color:{PURS}">BREIT</div></div>'
             + f'<div class="note mono" style="position:absolute;left:18px;top:{STH-46}px">QUERSCHNITT · SCHEMATISCH</div></div>')

# ---------- Bullauge: Blick von der ISS ----------
BR_ = 380
def terrain(seed, n, rmin, rmax, cols):
    rr = _r.Random(seed); s = ""
    for _ in range(n):
        x, y, r = rr.uniform(-BR_, BR_), rr.uniform(-BR_, BR_), rr.uniform(rmin, rmax)
        s += f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r:.0f}" ry="{r*rr.uniform(.5,.9):.0f}" fill="{rr.choice(cols)}" opacity="{rr.uniform(.35,.8):.2f}" transform="rotate({rr.uniform(0,180):.0f} {x:.0f} {y:.0f})"/>'
    return s
ridges = "".join(f'<path d="M{-BR_-20} {y}Q{-150} {y-40} {0} {y+10}T{BR_+20} {y-10}" fill="none" stroke="#A8916B" stroke-width="2" opacity=".45"/>' for y in range(-330, 380, 70))
wall_far = "M-400 120Q-260 60 -150 90T60 20T230 -40T420 -120"
far = (f'<g id="bfar"><rect x="-{BR_}" y="-{BR_}" width="{2*BR_}" height="{2*BR_}" fill="#CBB792"/>{terrain(3, 70, 20, 90, ["#BFA982","#D6C4A0","#B8A07A","#C9B793"])}{ridges}'
       f'<path id="hair" d="{wall_far}" fill="none" stroke="#B49C74" stroke-width="1.3"/></g>')
stones_g = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{c}" stroke="#9C8662" stroke-width="2"/>'
                   for x, y, w, h, c in [(x, y, _r.randint(46, 70), _r.randint(28, 38), _r.choice(["#C2AC86", "#CDB892", "#BCA47C"])) for y in range(-60, 60, 40) for x in range(-430, 430, 74)])
pebbles = "".join(f'<ellipse class="peb" cx="{_r.uniform(-BR_,BR_):.0f}" cy="{_r.choice([_r.uniform(-BR_,-110), _r.uniform(110,BR_)]):.0f}" rx="{_r.randint(10,26)}" ry="{_r.randint(7,16)}" fill="{_r.choice(["#C2AC86","#CDB892","#BCA47C"])}" stroke="#9C8662" stroke-width="2"/>' for _ in range(46))
near = (f'<g id="bnear"><rect x="-{BR_}" y="-{BR_}" width="{2*BR_}" height="{2*BR_}" fill="#CDB892"/>{terrain(5, 40, 30, 90, ["#C4AE88","#D3C09C","#BEA67F"])}{pebbles}'
        f'<g transform="rotate(-18)"><rect x="-460" y="-70" width="920" height="140" fill="#C9B48E"/><g id="wstones">{stones_g}</g>'
        f'<path id="wedge" d="M-460 -70H460M-460 70H460" stroke="{INK}" stroke-width="3"/></g></g>')
fly = "".join(f'<div class="fst" data-k="{k}"></div>' for k in range(10))
bull = (f'<div id="bull"><svg width="{2*BR_}" height="{2*BR_}" viewBox="-{BR_} -{BR_} {2*BR_} {2*BR_}"><defs><clipPath id="bc"><circle r="{BR_-6}"/></clipPath></defs>'
        f'<g clip-path="url(#bc)"><g id="bfarw">{far}</g><g id="bnearw">{near}</g></g>'
        f'<circle r="{BR_-6}" fill="none" stroke="#2B2D35" stroke-width="16"/><circle r="{BR_-18}" fill="none" stroke="#ECEEF3" stroke-width="6"/>'
        + "".join(f'<circle cx="{(BR_-6)*math.cos(math.radians(a)):.0f}" cy="{(BR_-6)*math.sin(math.radians(a)):.0f}" r="6" fill="#8A8F99"/>' for a in range(0, 360, 30))
        + f'</svg>{fly}<div id="scan"><div class="scanr"></div><div class="qb qs">?</div></div></div>')
stage.append(f'<div class="el" id="bullw" data-in="s1" data-d="-1" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px;opacity:0">{bull}</div>')

# ---------- Haar-Vergleich (s6) ----------
eye = ('<svg width="160" height="110" viewBox="0 0 160 110"><path d="M8 55Q80 -10 152 55Q80 120 8 55Z" fill="#fff" stroke="#2B2D35" stroke-width="5" stroke-linejoin="round"/>'
       '<circle cx="80" cy="55" r="26" fill="#7B3FE4"/><circle cx="80" cy="55" r="11" fill="#0B0B10"/><circle cx="72" cy="47" r="5" fill="#fff"/></svg>')
hair_svg = (f'<svg width="1080" height="{STH}" style="position:absolute;left:0;top:0">'
            f'<path id="sight" d="M210 470H900" stroke="#9AA0AA" stroke-width="3" stroke-dasharray="12 10"/>'
            f'<path d="M936 260Q930 340 938 420T934 580T940 700" fill="none" stroke="#2B2D35" stroke-width="1.2"/>'
            f'<path d="M210 760H936M210 740V780M936 740V780" stroke="{PUR}" stroke-width="5" stroke-linecap="round"/></svg>')
lensh = (f'<div id="hlens" style="position:absolute;left:640px;top:250px;width:240px;height:240px">'
         f'<svg width="240" height="240" viewBox="0 0 240 240"><defs><clipPath id="hlc"><circle cx="120" cy="120" r="112"/></clipPath></defs>'
         f'<g clip-path="url(#hlc)"><rect width="240" height="240" fill="#F7F8FA"/><path d="M118 -10Q102 60 124 130T116 260" fill="none" stroke="#2B2D35" stroke-width="9" stroke-linecap="round"/></g>'
         f'<circle cx="120" cy="120" r="112" fill="none" stroke="#2B2D35" stroke-width="7"/><path d="M200 200L236 236" stroke="#2B2D35" stroke-width="12" stroke-linecap="round"/></svg>'
         f'<div class="mono" style="position:absolute;left:-30px;top:250px;width:300px;text-align:center;font-size:24px;font-weight:800;color:{GR}">HAAR ≈ 0,1 MM</div></div>')
stage.append(f'<div class="el mapwrap" id="hairw" data-in="s1" data-d="-1" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px;opacity:0">{hair_svg}'
             f'<div style="position:absolute;left:70px;top:415px">{eye}</div>{lensh}'
             f'<div class="col" style="position:absolute;left:0;top:800px;width:1080px"><div class="huge2" id="hnum" style="color:{PURS};font-size:120px">7 M</div></div></div>')

# ---------- Zeitung 1932 (s13-s15) ----------
paper = (f'<svg width="560" height="560" viewBox="0 0 560 560"><rect x="10" y="10" width="540" height="540" rx="6" fill="#FBFAF6" stroke="#2B2D35" stroke-width="5"/>'
         f'<text x="280" y="78" text-anchor="middle" font-family="Unbounded" font-weight="600" font-size="44" fill="#2B2D35">DIE ZEITUNG</text>'
         f'<path d="M30 96H530M30 104H530" stroke="#2B2D35" stroke-width="3"/>'
         f'<text x="40" y="136" font-family="JBM" font-weight="800" font-size="24" fill="#2B2D35">1932</text><text x="520" y="136" text-anchor="end" font-family="JBM" font-weight="700" font-size="20" fill="#8A8F99">KURIOSES</text>'
         f'<rect x="40" y="156" width="300" height="250" rx="4" fill="#fff" stroke="#2B2D35" stroke-width="4"/>'
         f'<circle cx="110" cy="230" r="44" fill="#ECEEF3" stroke="#2B2D35" stroke-width="4"/><circle cx="96" cy="218" r="8" fill="#C9CDD6"/><circle cx="124" cy="244" r="6" fill="#C9CDD6"/>'
         f'<path d="M150 236L290 330" stroke="#2B2D35" stroke-width="3" stroke-dasharray="10 8"/>'
         f'<path d="M210 370Q240 350 260 362T310 352" stroke="{PUR}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M60 392H320" stroke="#2B2D35" stroke-width="3"/>'
         + "".join(f'<path d="M360 {170+k*30}H{530 if k%3 else 500}" stroke="#B7BCC6" stroke-width="7" stroke-linecap="round"/>' for k in range(8))
         + "".join(f'<path d="M40 {440+k*28}H{530 if k%2 else 460}" stroke="#B7BCC6" stroke-width="7" stroke-linecap="round"/>' for k in range(4))
         + f'<rect x="30" y="418" width="500" height="0" fill="none"/></svg>')
bubble1932 = f'<div id="pbub" class="mono">„VOM MOND AUS ZU SEHEN!“</div>'
tl = (f'<div id="tl"><svg width="900" height="120" viewBox="0 0 900 120"><path d="M60 50H840" stroke="#DDE0E6" stroke-width="10" stroke-linecap="round"/>'
      f'<path id="tlbar" d="M60 50H840" stroke="{PUR}" stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
      f'<circle cx="60" cy="50" r="18" fill="{PUR}" stroke="#fff" stroke-width="5"/><circle id="tl61" cx="840" cy="50" r="18" fill="{TQ}" stroke="#fff" stroke-width="5"/></svg>'
      f'<div class="mono tll" style="left:0">1932</div><div class="mono tll" id="tl61l" style="left:620px;width:300px;text-align:right">1961: ERSTER<br>MENSCH IM ALL</div>'
      f'<div class="mono" id="tlmid" style="position:absolute;left:0;top:-58px;width:900px;text-align:center;font-size:30px;font-weight:800;color:{PURS}">29 JAHRE NIEMAND DA OBEN</div></div>')
I.update(book='<path d="M8 10h14a4 4 0 0 1 4 4v26a3 3 0 0 0-3-3H8zM40 10H26a4 4 0 0 0-4 4v26a3 3 0 0 1 3-3h15z"/>',
         phone='<rect x="13" y="4" width="22" height="40" rx="4"/><path d="M21 38h6"/>',
         speech='<path d="M6 10h36v22H22l-9 8v-8H6z"/>', news='<rect x="6" y="8" width="36" height="32" rx="2"/><path d="M12 16h24M12 23h10M12 30h10M26 23h10v10H26z"/>',
         tv='<rect x="5" y="10" width="38" height="26" rx="3"/><path d="M17 42h14M24 36v6"/>')
spread = "".join(f'<div class="spr0" data-k="{k}"><div class="spri">{ic(I[n], 64, PURS, 3.2)}</div></div>' for k, n in enumerate(["book", "phone", "speech", "news", "tv", "speech", "phone", "book"]))
stage.append(f'<div class="el" id="npw" data-in="s1" data-d="-1" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px;opacity:0">'
             f'<div id="paper" style="position:absolute;left:260px;top:40px">{paper}{bubble1932}</div>{spread}'
             f'<div style="position:absolute;left:90px;top:760px">{tl}</div></div>')

# ---------- große Zahlen / Overlays ----------
OY = 1150
def chip_(txt, i, o, col=PURS, sfx="marker", icon="", y=OY, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 20px;border-color:{col};color:{col};background:rgba(255,255,255,.97);font-weight:700">{icon}{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
stage.append(chip_("„JA, DAS GEHT!“ – SAGEN VIELE", "s2@Ja", "s3", PURS, "glass", "", OY, 32))
stage.append(el(f'<div class="col"><div class="huge2" style="color:{PURS};font-size:150px"><span id="lnum">0</span> KM</div>'
                f'<div class="mono" style="font-size:26px;font-weight:800;color:{PURS};background:rgba(255,255,255,.92);padding:2px 12px;border-radius:8px">ALLE ABSCHNITTE · VERMESSUNG 2012</div></div>',
                0, 1010, A("s3@Kilometer", "s4", -0.3) + ' data-sfx="none"', 1080, CENTER))
stage.append(el(f'<div class="col"><div class="huge2" style="color:{PURS};font-size:150px"><span id="anum">0</span> KM</div>'
                f'<div class="mono" style="font-size:26px;font-weight:800;color:{PURS};background:rgba(255,255,255,.92);padding:2px 12px;border-radius:8px">ÜBER DER ERDE · ISS</div></div>',
                0, 1040, A("s5@Raumstation", "s6", 0) + ' data-sfx="none"', 1080, CENTER))
stage.append(chip_("MAUER AUS 400 KM ≈ HAAR AUS 7 M", "s6@Haar", "s7", PURS, "glass", "", 330, 30))
stage.append(chip_("GEBAUT AUS STEINEN UND ERDE VON VOR ORT", "s7@Steinen", "s8", "#8E6C3E", "marker", "", OY, 29))
sw = lambda c, t: f'<div class="col" style="gap:8px"><div style="width:190px;height:120px;border-radius:14px;background:{c};border:3px solid #2B2D35"></div><div class="mono" style="font-size:26px;font-weight:800;color:{GR}">{t}</div></div>'
stage.append(el(f'<div class="cardx row" style="gap:30px;padding:18px 34px">{sw("#C4AE88","MAUER")}<div class="huge2" style="font-size:110px;color:{PURS}">≈</div>{sw("#CDB892","BODEN")}</div>',
                0, 1040, A("s8@Farbe", "s9", -0.1) + ' data-sfx="glass"', 1080, CENTER))
stage.append(el(f'<div class="cardx col" style="gap:10px;padding:18px 30px;align-items:center"><div class="mono" style="font-size:26px;font-weight:800;color:#fff;background:{PUR};padding:4px 14px;border-radius:8px">2003 · CHINAS ERSTER ASTRONAUT</div>'
                f'<div style="font-family:Unbounded;font-weight:600;font-size:46px;color:{INK};text-align:center">„Ich habe sie nicht gesehen.“</div>'
                f'<div class="mono" style="font-size:20px;color:#8A8F99">YANG LIWEI NACH SEINEM FLUG</div></div>',
                0, 1075, A("s9@2003", "s10", -0.2) + ' data-sfx="glass"', 1080, CENTER))
stage.append(el(f'<div class="cardx col" style="gap:8px;padding:18px 30px;width:960px"><div class="huge2" style="color:{PURS};font-size:130px">≈ <span id="mnum">1</span> ×</div>'
                f'<div class="mono" style="font-size:26px;font-weight:800;color:{GR}">SO WEIT WEG WIE DIE ISS</div>'
                f'<div class="mrow"><span class="mono ml">ISS</span><div class="mtrack"><div class="mfill" id="mf1" style="background:{TQ}"></div></div><span class="mono mv">400 KM</span></div>'
                f'<div class="mrow"><span class="mono ml">MOND</span><div class="mtrack"><div class="mfill" id="mf2" style="background:{PUR}"></div></div><span class="mono mv">384.400 KM</span></div></div>',
                60, 860, A("s11@tausendmal", "s13", -0.3) + ' data-sfx="none"', 960, CENTER))
stage.append(el(f'<div class="stamp mono" style="font-size:52px;white-space:nowrap">VOM MOND: KEINE CHANCE</div>', 40, 620, A("s12", "s13", 0.05), 1000, CENTER).replace("top:620px","top:440px"))
stage.append(chip_("BIS HEUTE WEITERERZÄHLT", "s15@weitererzählt", "end", PURS, "glass", "", OY, 32, -0.3))

PANJS = dict(BAD=[BX, BY], RE=RE, ORB=ORB, ISS=[IX, IY], MX=MOONX,
    cam=[("s1",-1, -70, 30, 0.95, 470), ("s3",-0.2, -58, 22, 1.08, 470), ("s3@Kilometer",0.1, 21, -50, 5.4, 430), ("s4",-0.15, 30, -45, 5.8, 430),
         ("s4",0.5, BX, BY, 90, 430), ("s5",-0.2, BX, BY, 90, 430), ("s5",0.35, 20, -60, 0.98, 500), ("s6",-0.25, IX*0.4, IY*0.4, 1.05, 500), ("s6",0.45, IX, IY, 3.4, 500),
         ("s9",-0.35, IX, IY, 3.4, 500), ("s9",0.15, 0, 0, 0.82, 450), ("s10",0, 0, 0, 0.8, 450), ("s11",0.1, 12000, 0, ZM, 450), ("s13",0.5, 12000, 0, ZM*0.9, 450)])
SCENE_JS = r''' // ---- Bühne: Globus/Mond, Boden, Bullauge, Haar, Zeitung ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const sm=u=>u*u*(3-2*u); const bo=x=>1+2.70158*Math.pow(x-1,3)+1.70158*Math.pow(x-1,2);
  function kf(arr,tt){ const ks=arr.map(k=>({t:TS(k[0],k[1]),v:k.slice(2)})); if(tt<=ks[0].t) return ks[0].v;
    for(let i=0;i<ks.length-1;i++){ const a=ks[i],b=ks[i+1]; if(tt>=a.t&&tt<b.t){ const e=sm((tt-a.t)/Math.max(1e-6,b.t-a.t));
      const za=a.v[2], zb=b.v[2], z=Math.exp(Math.log(za)+(Math.log(zb)-Math.log(za))*e);
      const w=(Math.abs(zb-za)<1e-6)?e:(1/za-1/z)/(1/za-1/zb);
      return [a.v[0]+(b.v[0]-a.v[0])*w, a.v[1]+(b.v[1]-a.v[1])*w, z, a.v[3]+(b.v[3]-a.v[3])*e]; } }
    return ks[ks.length-1].v; }
  const ol=(id,v)=>{document.getElementById(id).style.opacity=cl(v,0,1);};
  const H0=document.getElementById('head'); const hf=1-pr(t,TS('s3',-0.25),0.3); H0.style.opacity=cl(1-pr(t,END,.3),0,1)*hf; document.getElementById('headbg').style.opacity=hf;
  // Kamera Welt
  const c=kf(PAN.cam,t); let cx=c[0], cy=c[1], z=c[2], FY=c[3];
  cx+=6*Math.sin(t*0.7)/z; cy+=4*Math.cos(t*0.55)/z;   // leichter Drift ab Frame 0
  document.getElementById('wg').setAttribute('transform',`translate(540,${FY}) scale(${z}) translate(${-cx},${-cy})`);
  const pj=(x,y)=>[540+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('#wwrap .xg')){ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }
  // Mauer: Strichstaerke in Bildschirm-px, zeichnet sich in s3 nacheinander
  const wpx=(t<TS('s3',0)?7:4.2)*(1+0.12*Math.sin(t*5)); const ws=document.querySelectorAll('.wall');
  ws.forEach((p,k)=>{ p.setAttribute('stroke-width',wpx/z); let dr=1;
    if(t>=TS('s3',-0.2)){ dr=k===0?1:pr(t,TS('s3@Kilometer',0.1+0.35*(k-1)),0.7); }
    if(k>0&&t<TS('s3',-0.2)) dr=0;
    p.style.strokeDashoffset=1-dr; });
  // Sichtbarkeit Welt
  const wA=(1-pr(t,TS('s4',0.1),0.4)) + pr(t,TS('s5',-0.15),0.3)*(1-pr(t,TS('s6',0.25),0.25)) + pr(t,TS('s9',-0.35),0.3)*(1-pr(t,TS('s13',0),0.4));
  document.getElementById('wwrap').style.opacity=cl(wA,0,1)*cl(1-pr(t,END,0.3),0,1);
  ol('qw', (1-pr(t,TS('s3',-0.3),0.3))); document.getElementById('qhook').style.transform=`rotate(${8*Math.sin(t*2.3)}deg) scale(${1+0.06*Math.sin(t*4)})`;
  // ISS-Bahn + ISS
  const oA=pr(t,TS('s5',0.1),0.4)*(1-pr(t,TS('s9',0.2),0.4)); const orb=document.getElementById('orb');
  orb.setAttribute('stroke-width',3/z); orb.setAttribute('stroke-dasharray',`${10/z} ${8/z}`); orb.style.opacity=oA;
  const dm=document.getElementById('dim'); dm.setAttribute('stroke-width',5/z); dm.style.opacity=pr(t,TS('s5@400',-0.1),0.3)*(1-pr(t,TS('s6',-0.1),0.3)); ol('labdim', pr(t,TS('s5@400',0),0.3)*(1-pr(t,TS('s6',-0.1),0.3)));
  const ia=(-175+57*sm(pr(t,TS('s5',0),TS('s6',0.45)-TS('s5',0))))*Math.PI/180; const ip=[PAN.ORB*Math.cos(ia),PAN.ORB*Math.sin(ia)];
  const isw=document.getElementById('iss'); const ipp=pj(ip[0],ip[1]); isw.style.left=ipp[0]+'px'; isw.style.top=ipp[1]+'px';
  isw.style.opacity=pr(t,TS('s5@ISS',-0.2),0.3)*(1-pr(t,TS('s6',0.35),0.2));
  document.getElementById('issb').style.transform=`scale(${cl(0.55+0.25*z,0.55,1.6)}) rotate(${ia*180/Math.PI+90}deg)`;
  // Kapsel (s9)
  const ka=(-150+110*pr(t,TS('s9',-0.2),TS('s10',0)-TS('s9',-0.2)))*Math.PI/180; const kp=pj((PAN.RE+34)*Math.cos(ka),(PAN.RE+34)*Math.sin(ka));
  const kw=document.getElementById('kap'); kw.style.left=kp[0]+'px'; kw.style.top=kp[1]+'px'; kw.style.opacity=pr(t,TS('s9',0),0.3)*(1-pr(t,TS('s10',0),0.3));
  document.getElementById('kapb').style.transform=`rotate(${ka*180/Math.PI+90}deg)`;
  // Mond
  const mA=pr(t,TS('s10',0.2),0.5); document.getElementById('moon').style.opacity=t<TS('s9',-0.5)?0:1; document.getElementById('emline').style.opacity=mA;
  ol('labmoon', pr(t,TS('s11',-0.2),0.3)); ol('labearth', pr(t,TS('s11',-0.1),0.3)); ol('mring', pr(t,TS('s11',-0.2),0.3)); ol('ering', pr(t,TS('s11',-0.1),0.3));
  document.querySelectorAll('.mring').forEach(e=>e.style.transform=`translate(-50%,-50%) scale(${1+0.12*Math.sin(t*5)})`);
  document.getElementById('atmo').style.opacity=z>0.2?1:0;
  // Boden-Szene (s4)
  const g=document.getElementById('gnd'); const gin=pr(t,TS('s4',0.15),0.4), gout=pr(t,TS('s5',-0.2),0.4);
  g.style.opacity=gin*(1-gout); g.style.transform=`scale(${(0.3+0.7*bo(gin))*(1-0.94*sm(gout))})`; g.style.transformOrigin=`${600+156}px 420px`;
  // Bullauge (s6-s8)
  const bw=document.getElementById('bullw'); const bin=pr(t,TS('s6',0.25),0.45); const bout=pr(t,TS('s6@Haar',-0.15),0.25); const bin2=pr(t,TS('s7',-0.2),0.35); const bout2=pr(t,TS('s9',-0.35),0.3);
  const bA=bin*(1-bout)+bin2*(1-bout2); bw.style.opacity=cl(bA,0,1);
  const bs=t<TS('s6@Haar',-0.15)?(0.05+0.95*bo(bin)):(t<TS('s7',-0.2)?1:(0.85+0.15*bo(bin2))*(1-0.9*sm(bout2)));
  const bl=document.getElementById('bull'); bl.style.transform=`translate(-50%,-50%) scale(${bs})`;
  // Suchring
  const sc=document.getElementById('scan'); const sa=pr(t,TS('s6@entdecken',-0.1),0.3)*(1-pr(t,TS('s6@Haar',-0.2),0.2));
  const st_=t*1.3; sc.style.opacity=sa; sc.style.left=(380+170*Math.sin(st_*1.7))+'px'; sc.style.top=(380+150*Math.sin(st_*1.1+1))+'px';
  // nah/fern im Bullauge
  const nz=pr(t,TS('s7',-0.2),0.6); document.getElementById('bfarw').setAttribute('transform',`scale(${1+5*sm(nz)})`); document.getElementById('bfarw').style.opacity=1-sm(nz);
  document.getElementById('bnearw').setAttribute('transform',`scale(${0.35+0.65*sm(nz)})`); document.getElementById('bnearw').style.opacity=sm(nz);
  document.getElementById('hair').setAttribute('stroke-width',1.3+0.4*Math.sin(t*3));
  // Steine fliegen in die Mauer (s7), Kontur verschwindet (s8)
  document.querySelectorAll('.fst').forEach((e,k)=>{ const t0=TS('s7@Steinen',-0.1)+k*0.09; const u=pr(t,t0,0.45); const a=k*0.62+0.4;
    const x0=380+300*Math.cos(a), y0=380+300*Math.sin(a), x1=380+(k-4.5)*40, y1=380+(k%2?-12:14);
    e.style.left=(x0+(x1-x0)*sm(u))+'px'; e.style.top=(y0+(y1-y0)*sm(u)-60*Math.sin(Math.PI*u))+'px'; e.style.opacity=(u>0&&u<1)?1:0; });
  document.getElementById('wedge').style.opacity=1-0.85*pr(t,TS('s8@dieselbe',-0.1),0.9);
  // Haar-Vergleich (s6)
  const hw=document.getElementById('hairw'); const hin=pr(t,TS('s6@Haar',-0.2),0.3), hout=pr(t,TS('s7',-0.25),0.25);
  hw.style.opacity=hin*(1-hout); hw.style.transform=`scale(${0.9+0.1*sm(hin)})`;
  ol('hlens', pr(t,TS('s6@Entfernung',-0.3),0.3)); document.getElementById('hlens').style.transform=`scale(${0.5+0.5*bo(pr(t,TS('s6@Entfernung',-0.3),0.35))})`;
  document.getElementById('sight').style.strokeDashoffset=-t*40;
  ol('hnum', pr(t,TS('s6@sieben',-0.1),0.3));
  // Zeitung (s13-s15)
  const nw=document.getElementById('npw'); const nin=pr(t,TS('s13',-0.1),0.4); nw.style.opacity=nin*cl(1-pr(t,END,0.3),0,1);
  const pp=document.getElementById('paper'); pp.style.transform=`translateY(${-500*(1-bo(nin))}px) rotate(${-4+3*(1-sm(nin))+1.2*Math.sin(t*1.4)}deg) scale(${1-0.18*sm(pr(t,TS('s15',0),0.5))})`;
  ol('pbub', pr(t,TS('s13@Zeitungs-Comic',-0.1),0.3)); document.getElementById('pbub').style.transform=`rotate(-3deg) scale(${0.6+0.4*bo(pr(t,TS('s13@Zeitungs-Comic',-0.1),0.3))})`;
  const tlp=pr(t,TS('s14',0),TS('s14@überprüfen',0.4)-TS('s14',0)); document.getElementById('tlbar').style.strokeDashoffset=1-sm(tlp);
  ol('tl', pr(t,TS('s13@1932',-0.1),0.3)*(1-pr(t,TS('s15@weitererzählt',-0.45),0.25))); ol('tl61', tlp>0.97?1:0); ol('tl61l', pr(t,TS('s14@überprüfen',0.2),0.3)); ol('tlmid', pr(t,TS('s14@niemand',0),0.3));
  document.querySelectorAll('.spr0').forEach((e,k)=>{ const u=pr(t,TS('s15',0.1)+k*0.1,0.5); const a=(-90+k*45+22.5)*Math.PI/180;
    e.style.opacity=u>0?Math.min(1,u*3):0; e.style.left=(540+440*Math.cos(a)*bo(u))+'px'; e.style.top=(330+300*Math.sin(a)*bo(u))+'px';
    e.style.transform=`translate(-50%,-50%) scale(${0.4+0.6*bo(u)}) rotate(${6*Math.sin(t*3+k)}deg)`; });
  pp.style.filter=t>TS('s15',0)?`drop-shadow(0 10px 20px rgba(26,31,51,.2))`:'none';
  // Zaehler
  document.getElementById('lnum').textContent=Math.round(21196*sm(pr(t,TS('s3@Kilometer',-0.2),TS('s4',-0.6)-TS('s3@Kilometer',-0.2)))).toLocaleString('de-DE');
  document.getElementById('anum').textContent=Math.round(400*sm(pr(t,TS('s5@Raumstation',0),TS('s5@400',0.2)-TS('s5@Raumstation',0))));
  const mu=sm(pr(t,TS('s11@tausendmal',-0.3),0.9)); document.getElementById('mnum').textContent=Math.round(1+999*mu).toLocaleString('de-DE');
  document.getElementById('mf1').style.transform=`scaleX(${0.004*pr(t,TS('s11@tausendmal',-0.2),0.3)})`; document.getElementById('mf2').style.transform=`scaleX(${mu})`;
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
.ppl.g3{{background:#7B3FE4}}
.cmp{{position:relative;width:1000px;background:rgba(255,255,255,.96);border:1px solid rgba(26,31,51,.12);border-radius:22px;padding:18px 18px 14px;box-shadow:0 10px 26px rgba(26,31,51,.14)}}
.crow{{display:flex;align-items:center;height:96px;border:2px solid transparent;border-radius:14px;margin-bottom:4px}}
.clab{{width:236px;flex:none;padding-left:8px}}
.ctrack{{position:relative;flex:1;height:44px}}
.cfill{{position:absolute;left:0;top:0;height:44px;border-radius:10px;transform-origin:left}}
.cnum{{position:absolute;top:6px;font-size:26px;font-weight:800;white-space:nowrap}}
.xg{{position:absolute;width:0;height:0;z-index:5}}
.xsbg{{position:absolute;inset:0;background:#FCFCFD}}
#xswrap{{overflow:hidden}}
#bitw{{position:absolute;width:0;height:0;z-index:20}}
#bitb{{position:absolute;left:0;top:0;transform-origin:0 0;z-index:2}}
.blob{{position:absolute;left:0;top:0;transform-origin:0 0;z-index:3;opacity:0}}
.blob svg{{display:block}}
.deb{{position:absolute;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:3px;background:#8E7A66;border:2px solid #fff}}
#glow{{position:absolute;left:-170px;top:-230px;width:340px;height:340px;border-radius:50%;background:radial-gradient(circle,rgba(255,170,60,.95) 0,rgba(240,110,60,.55) 35%,rgba(229,72,77,0) 70%);opacity:0;transform-origin:50% 50%}}
.parr{{position:absolute;opacity:0;z-index:4}}
#qbit{{position:absolute;left:0;top:0;opacity:0;z-index:5}}
.qb{{width:92px;height:92px;margin:-46px 0 0 -46px;border-radius:50%;background:#7B3FE4;color:#fff;font-family:Unbounded;font-weight:600;font-size:58px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 6px rgba(123,63,228,.22),0 6px 16px rgba(26,31,51,.25)}}
#stuck{{position:absolute;left:0;top:-70px;font-size:120px;font-weight:800;color:#E5484D;opacity:0;z-index:6;text-shadow:0 0 12px #fff}}
.cardx{{background:rgba(255,255,255,.97);border:1px solid rgba(26,31,51,.12);border-radius:22px;padding:16px 22px;box-shadow:0 10px 26px rgba(26,31,51,.14)}}
#lens{{position:absolute;left:0;top:0;width:300px;height:300px;transform-origin:0 100%;opacity:0;filter:drop-shadow(0 8px 16px rgba(26,31,51,.25))}}
#earthw{{overflow:hidden}}

.geo{{z-index:4000}}

#wwrap,#gnd,#bullw,#hairw,#npw{{overflow:hidden}}
#wwrap{{background:#FCFCFD}}
.pz{{position:absolute;left:0;top:0;transform-origin:0 0}}
#qhook{{position:absolute;left:0;top:0}}
.qs{{position:absolute;left:52px;top:-52px;width:70px;height:70px;font-size:44px}}
#bull{{position:absolute;left:540px;top:490px;width:760px;height:760px;filter:drop-shadow(0 14px 26px rgba(26,31,51,.28))}}
#bull svg{{display:block}}
#scan{{position:absolute;width:0;height:0}}
.scanr{{position:absolute;left:-70px;top:-70px;width:140px;height:140px;border-radius:50%;border:5px dashed #7B3FE4;box-shadow:0 0 0 4px rgba(255,255,255,.5)}}
.fst{{position:absolute;width:44px;height:28px;margin:-14px 0 0 -22px;border-radius:6px;background:#C2AC86;border:2.5px solid #9C8662;opacity:0}}
.mring{{position:absolute;left:0;top:0;width:64px;height:64px;border-radius:50%;border:4px solid #7B3FE4;box-shadow:0 0 18px rgba(123,63,228,.5)}}
.spr0{{position:absolute;opacity:0}}
.spri{{width:104px;height:104px;border-radius:24px;background:#fff;border:3px solid #7B3FE4;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 18px rgba(26,31,51,.16)}}
#paper{{transform-origin:280px 280px}}
#pbub{{position:absolute;left:300px;top:150px;font-size:30px;font-weight:800;color:#fff;background:#7B3FE4;border-radius:16px;padding:12px 18px;white-space:nowrap;box-shadow:0 8px 18px rgba(26,31,51,.2);opacity:0}}
#tl{{position:relative;width:900px;height:170px}}
.tll{{position:absolute;top:80px;font-size:28px;font-weight:800;color:#3F434C}}
#hlens{{transform-origin:120px 120px;opacity:0}}
.mrow{{display:flex;align-items:center;gap:16px;width:880px;margin-top:6px}}
.ml{{width:110px;font-size:26px;font-weight:800;color:#3F434C}} .mv{{width:200px;text-align:right;font-size:24px;font-weight:800;color:#3F434C}}
.mtrack{{flex:1;height:30px;border-radius:15px;background:#F0F1F4;overflow:hidden}}
.mfill{{height:100%;border-radius:15px;transform-origin:left;transform:scaleX(0)}}
#hairw{{transform-origin:540px 490px}}
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
 let rop=0; if(pose&&!end){{const prevHad=BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose; rop=prevHad?1:(BEATS.indexOf(b)===0?1:ease(pr(t,b.s,.3))); const nb=BEATS[BEATS.indexOf(b)+1]; if(nb&&!nb.pose) rop*=1-pr(t,nb.s-0.2,.2); if(!nb) rop*=1-pr(t,END-0.2,.2);}}
 if(end){{rop=ease(pr(t,END+0.3,.35));}}
 R.style.opacity=rop; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');
 let prevPose=null; const bi=BEATS.indexOf(b); if(bi>0) prevPose=BEATS[bi-1].pose; const pf=bi===0?1:pr(t,b.s,.15);
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
