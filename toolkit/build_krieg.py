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
CH = ["01 DIE FRAGE", "02 1939", "03 WELTKRIEG", "04 DIE BILANZ", "05 DIE LEHRE"]
B = [
 ("p1", 0, "Der größte Krieg der Geschichte?", "Welcher *Krieg* war der *größte* der *Geschichte?*", None),
 ("p2", 0, "Der Zweite Weltkrieg", "Es ist der *Zweite* *Weltkrieg.*", None),
 ("p3", 1, "1939: Überfall auf Polen", "Er begann im *September* *neunzehnhundertneununddreißig* mit dem *deutschen* *Überfall* auf *Polen.*", None),
 ("p4", 1, "Krieg in ganz Europa", "Bald wurde in *ganz* *Europa* *gekämpft.*", None),
 ("p5", 2, "1941: ein echter Weltkrieg", "Ab *neunzehnhunderteinundvierzig* wurde daraus ein *echter* *Weltkrieg:* *Japan* griff die *USA* an, gekämpft wurde in *Asien,* *Afrika* und auf den *Ozeanen.*", None),
 ("p6", 3, "Rund 60 Staaten", "Am *Ende* waren rund *sechzig* *Staaten* *beteiligt.*", None),
 ("p7", 3, "Rund 60 Millionen Tote", "Etwa *sechzig* *Millionen* *Menschen* *starben,* die *meisten* von ihnen *Zivilisten.*", None),
 ("p8", 3, "1945: endlich vorbei", "*Neunzehnhundertfünfundvierzig* war der *Krieg* *endlich* *vorbei.*", None),
 ("p9", 4, "Die Vereinten Nationen", "Noch im *selben* *Jahr* wurden die *Vereinten* *Nationen* *gegründet,* damit so etwas *nie* *wieder* *passiert.*", None),
 ("p10", 4, "Die wichtigste Lehre", "Denn das ist die *wichtigste* *Lehre:* *Krieg* bringt *immer* *Leid,* egal wer am *Ende* *gewinnt.*", None),
 ("p11", 4, "Und was denkst du?", "Was *denkst* du: Kann es eine *Welt* *ohne* *Krieg* geben?", None),
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


# ================= Bühne: Weltkarte, Krieg breitet sich aus 1939 -> 1945, danach Frieden (durchgehend) =================
CENTER = "display:flex;justify-content:center"
I.update(
 dove='<path d="M8 30c6 0 10-3 13-8l4-9c2-4 7-5 10-2l5 1-4 3c0 9-6 17-17 18l-6 5v-6c-3 0-5-1-5-2z"/><path d="M21 22c-4-5-9-7-14-6 2 5 6 8 12 8"/>',
 un='<circle cx="24" cy="24" r="17"/><path d="M7 24h34M24 7c-6 7-6 27 0 34M24 7c6 7 6 27 0 34M10 14c4 3 24 3 28 0M10 34c4-3 24-3 28 0"/>',
 flag='<path d="M10 43V6M10 8h26l-5 8 5 8H10"/>',
)
GEO = json.load(open("geo.json")); K = GEO["K"]; GW, GH = GEO["W"], GEO["H"]
def WX(lon): return (lon + 180) * K
def WY(lat): return (90 - lat) * K
def CAM(lat, lon, z, fy=270): return [round(WX(lon), 1), round(WY(lat), 1), z, fy]
FULL = [540, 205, 0.85, 270]
HOOK = [560, 200, 1.05, 270]
EUV = CAM(51, 17, 3.4, 255); EUW = CAM(50, 14, 2.2, 265)
cam = [("p1", 0, *HOOK), ("p2", 0.1, *FULL), ("p3", 0, *FULL), ("p3@September", 0.1, *EUV), ("p4", 0, *EUV), ("p4@Europa", 0, *EUW),
       ("p5", 0, *EUW), ("p5@Weltkrieg", -0.3, *FULL)]
# Wachstum: Liste von Zentren (Kreis-Union), Anker, Offset, Dauer
GROW = dict(
 eu=dict(c=[[WX(13.4), WY(52.5)]], a="p4@Europa", o=-0.3, d=1.8, r=260),
 world=dict(c=[[WX(37.6), WY(55.7)], [WX(139.7), WY(35.7)], [WX(-77), WY(38.9)], [WX(31), WY(30)], [WX(100), WY(15)]], a="p5@Japan", o=-0.3, d=4.6, r=420),
)
GEOJS = dict(cam=cam, grow=GROW, W=GW, H=GH,
             de=["p3@deutschen", -0.1], pl=["p3@Überfall", 0], peace=["p8@vorbei", -0.6], dim=["p10", -0.2, "p11", 0.0])
landp = f'<path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
def layer(lid, d, fill, stroke, clip=True):
    inner = f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="1.8" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    g = f'<g clip-path="url(#gc_{lid})">{inner}</g>' if clip else inner
    return f'<g id="e_{lid}" style="opacity:0">{g}</g>'
WARF, WARS = "rgba(229,72,77,.38)", "#B8383C"
defs = (f'<defs><clipPath id="win"><rect x="0" y="0" width="{GW}" height="{GH}"/></clipPath>'
        + "".join(f'<clipPath id="gc_{k}">' + "".join(f'<circle class="gcc" data-k="{k}" cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="0"/>' for c in v["c"]) + '</clipPath>' for k, v in GROW.items())
        + '</defs>')
mapsvg = (f'<svg width="920" height="530" style="position:absolute;left:0;top:0;overflow:hidden">{defs}<g id="mapg"><g clip-path="url(#win)">{landp}'
          + layer("eu", GEO["eu"], WARF, WARS) + layer("world", GEO["world"], WARF, WARS)
          + layer("de", GEO["de"], "rgba(63,67,76,.55)", "#2B2D35", False) + layer("pl", GEO["pl"], "rgba(229,72,77,.6)", "#B8383C", False)
          + layer("peace", GEO["eu"] + GEO["world"], "rgba(25,198,180,.35)", "#0E8C80", False)
          + f'<path id="arrow" d="M{WX(13.4):.1f} {WY(52.5):.1f} Q{WX(17.5):.1f} {WY(54.2):.1f} {WX(20.6):.1f} {WY(52.3):.1f}" fill="none" stroke="#B8383C" stroke-width="3.5" stroke-linecap="round" vector-effect="non-scaling-stroke" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
          + '</g></g></svg>')
def lab(lat, lon, text, i, o, col=PUR, d=0, pin=True):
    p = f'<span class="pin" style="background:{col}"></span>' if pin else ""
    return (f'<div class="geo" data-x="{WX(lon):.1f}" data-y="{WY(lat):.1f}" style="position:absolute;left:0;top:0">'
            f'<div class="el mk" {A(i, o, d)} style="left:{-11 if pin else -40}px;top:-14px;gap:8px">{p}'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
GR = "#3F434C"; RD = "#B8383C"; TQD = "#0E8C80"
ov = (lab(47.6, 9.5, "DEUTSCHLAND", "p3@deutschen", "p4", GR, 0, False)
      + lab(52.2, 21.0, "POLEN", "p3@Polen", "p5", RD, 0)
      + lab(48.9, 2.3, "PARIS", "p4@gekämpft", "p5", RD, 0)
      + lab(51.5, -0.1, "LONDON", "p4@gekämpft", "p5", RD, 0.15)
      + lab(35.7, 139.7, "JAPAN", "p5@Japan", "p6", RD, 0)
      + lab(38.9, -77.0, "USA", "p5@USA", "p6", RD, 0)
      + lab(34, 100, "ASIEN", "p5@Asien", "p6", RD, 0, False)
      + lab(8, 18, "AFRIKA", "p5@Afrika", "p6", RD, 0, False)
      + lab(10, -160, "PAZIFIK", "p5@Ozeanen", "p6", "#3A6EA5", 0, False)
      + lab(18, -48, "ATLANTIK", "p5@Ozeanen", "p6", "#3A6EA5", 0.15, False)
      + lab(37.8, -122.4, "UNO · SAN FRANCISCO", "p9@Vereinten", "p10", TQD, 0))
# Zeitleiste 1939–1945 (bildschirmfest, unten im Panel)
YRS = [1939, 1940, 1941, 1942, 1943, 1944, 1945]
ticks = "".join(f'<div class="mono" style="position:absolute;left:{26 + i * 144 - 30}px;top:44px;width:60px;text-align:center;font-size:20px;font-weight:700;color:#5D616B">{y}</div>'
                f'<div style="position:absolute;left:{26 + i * 144 - 1}px;top:24px;width:2px;height:16px;background:#8A8F99"></div>' for i, y in enumerate(YRS))
tline = (f'<div style="position:absolute;left:0;top:0;width:920px;height:84px">'
         f'<div style="position:absolute;left:26px;top:28px;width:864px;height:8px;border-radius:4px;background:#E6E7EB"></div>'
         f'<div id="tfill" style="position:absolute;left:26px;top:28px;width:864px;height:8px;border-radius:4px;background:{RED};transform-origin:left;transform:scaleX(0)"></div>'
         f'{ticks}<div id="tdot" style="position:absolute;left:26px;top:32px"><div class="tipdot" style="background:{RED}"></div></div></div>')
def stat(icon, val, unit, sub, anchor, col, x):
    return (f'<div class="el" {A(anchor, None, 0)} data-sfx="glass" style="left:{x}px;top:96px;width:420px">'
            f'<div class="row" style="gap:16px">{ic(I[icon], 54, col, 3.2)}<div class="col" style="align-items:flex-start;gap:2px">'
            f'<div class="mono" style="font-size:44px;font-weight:800;color:{col}">≈ {cnt(val, anchor, 0, 0.05)}{unit}</div>'
            f'<div class="mono" style="font-size:19px;color:#5D616B">{sub}</div></div></div></div>')
I.update(person='<circle cx="24" cy="15" r="7"/><path d="M10 42c0-8 6-13 14-13s14 5 14 13"/>')
bottom = (f'<div style="position:absolute;left:0;top:530px;width:920px;height:230px;background:rgba(255,255,255,.93);border-top:1px solid rgba(26,31,51,.12);padding:16px 0">'
          f'<div style="position:relative;width:920px;height:200px">{tline}'
          + stat("flag", 60, "", "STAATEN BETEILIGT", "p6@sechzig", GR, 40)
          + stat("person", 60, " MIO.", "TOTE · SCHÄTZUNG (55–70 MIO.)", "p7@sechzig", RD, 480)
          + '</div></div>')
chips = (el('<div class="chip mono" style="font-size:19px;padding:8px 12px">MENSCHHEITSGESCHICHTE · FOLGE 5</div>', 18, 18, A("p1", "p3", -0.6) + ' data-sfx="none"')
         + f'<div class="el" {A("p3", "p11", 0)} data-sfx="none" style="right:18px;top:18px"><div class="chip mono" style="font-size:24px;padding:8px 14px;background:rgba(255,255,255,.95)"><span id="yr">1939</span></div></div>'
         + el('<div class="chip mono" style="font-size:16px;padding:5px 9px;color:#8A8F99;border-color:#C9CCD3;background:rgba(255,255,255,.9)">KARTE SCHEMATISCH · HEUTIGE GRENZEN</div>', 18, 492, A("p3", "end", 0.3) + ' data-sfx="none"'))
stage.append(mm(mapsvg + ov + bottom + chips, 80, 460, 920, 760, A("p1", "end", -0.6)))

# ---- Overlays ----
stage.append(el(f'<div class="chip mono row" style="font-size:30px;gap:14px;padding:12px 22px;background:rgba(255,255,255,.95);border-color:{RED};color:{RD}">DER GRÖSSTE KRIEG?</div>', 80, 905, A("p1", "p2@Zweite", -0.6) + ' data-sfx="none"', 920, CENTER))
stage.append(el(f'<div class="stamp mono" style="font-size:40px;white-space:nowrap;color:#2B2D35;border-color:#2B2D35">ZWEITER WELTKRIEG · 1939–1945</div>', 80, 800, A("p2@Weltkrieg", "p3@September"), 920, CENTER))
stage.append(el(f'<div class="chip mono row" style="font-size:28px;gap:12px;padding:12px 20px;border-color:{RED};background:rgba(255,255,255,.95)">1. SEPTEMBER 1939</div>', 80, 905, A("p3@September", "p4", 0) + ' data-sfx="marker"', 920, CENTER))
stage.append(el(f'<div class="chip mono row" style="font-size:28px;gap:12px;padding:12px 20px;border-color:{RED};background:rgba(255,255,255,.95)">KÄMPFE AUF ALLEN KONTINENTEN AUSSER DER ANTARKTIS</div>', 80, 905, A("p5@Asien", "p6", 0) + ' data-sfx="marker"', 920, CENTER))
stage.append(el(f'<div class="chip mono row" style="font-size:28px;gap:12px;padding:12px 20px;border-color:{RED};background:rgba(255,255,255,.95)">DIE MEISTEN TOTEN: ZIVILISTEN</div>', 80, 905, A("p7@Zivilisten", "p8", 0) + ' data-sfx="marker"', 920, CENTER))
stage.append(el(f'<div class="chip mono row" style="font-size:30px;gap:14px;padding:12px 22px;border-color:{TQ};color:{TQD};background:rgba(255,255,255,.95)">{ic(I["dove"], 42, TQD, 3)}1945 · KRIEGSENDE</div>', 80, 905, A("p8@Krieg", "p9", 0) + ' data-sfx="success"', 920, CENTER))
stage.append(el(f'<div class="chip mono row" style="font-size:28px;gap:14px;padding:12px 22px;border-color:{TQ};color:{TQD};background:rgba(255,255,255,.95)">{ic(I["un"], 42, TQD, 3)}VEREINTE NATIONEN · ZIEL: FRIEDEN</div>', 80, 905, A("p9@gegründet", "p10", 0) + ' data-sfx="glass"', 920, CENTER))
# p10 Kernbotschaft (Alex): Krieg ist immer negativ
stage.append(card(f'<div class="col" style="gap:18px;height:100%;justify-content:center"><div class="mono small grey">DIE WICHTIGSTE LEHRE</div>'
                  f'<div style="font-family:Unbounded;font-weight:600;font-size:64px;line-height:1.1;text-align:center;letter-spacing:-1.5px">Krieg bringt<br><span style="color:{RED}">immer Leid.</span></div>'
                  f'<div class="mono" style="font-size:28px;color:#5D616B" id="egal">EGAL, WER GEWINNT.</div></div>',
                  130, 560, 820, 400, "active", A("p10@Lehre", "p11", 0)))
# p11 Frage
stage.append(card(f'<div class="col" style="gap:16px;height:100%;justify-content:center"><div class="mono small grey">KANN ES EINE WELT OHNE KRIEG GEBEN?</div>'
                  f'<div class="row" style="gap:20px"><div class="chip tq mono" style="font-size:34px">JA</div><div class="chip mono" style="font-size:34px;border-color:#8A8F99">NEIN</div></div></div>',
                  130, 560, 820, 220, "activeTQ", A("p11@denkst", "end")))
stage.append(el('<div class="chip pu mono" style="font-size:22px;background:rgba(255,255,255,.95)">SCHREIB\'S IN DIE KOMMENTARE</div>', 260, 800, f'{A("p11@Krieg", "end", 0.1)} data-sfx="plop"', 560, CENTER))
YEARS = [("p3", "1939"), ("p5", "1941"), ("p8", "1945")]
GEOJS["years"] = YEARS
GEOJS["tl"] = [["p3", 0.0], ["p5", 2 / 6], ["p8", 1.0]]
PANJS = GEOJS


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
 // ---- Bühne: Weltkarte, Krieg breitet sich aus ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const M=document.getElementById('mapg');
  const keys=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4],fy:k[5]}}));
  function base(tt){{ if(tt<=keys[0].t) return keys[0]; for(let i=0;i<keys.length-1;i++){{ const k0=keys[i],k1=keys[i+1]; if(tt>=k0.t&&tt<k1.t){{ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e),fy:k0.fy+(k1.fy-k0.fy)*e}}; }} }} return keys[keys.length-1]; }}
  const bs=base(t), z=bs.z, cx=bs.x, cy=bs.y, FX=460, FY=bs.fy;
  M.setAttribute('transform',`translate(${{FX}},${{FY}}) scale(${{z}}) translate(${{-cx}},${{-cy}})`);
  const pj=(x,y)=>[FX+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('.geo')){{ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }}
  const peace=pr(t,TS(PAN.peace[0],PAN.peace[1]),1.2);
  for(const [k,v] of Object.entries(PAN.grow)){{ const t0=TS(v.a,v.o), q=ease(pr(t,t0,v.d));
    document.querySelectorAll(`.gcc[data-k="${{k}}"]`).forEach(C=>C.setAttribute('r',(v.r*q).toFixed(1)));
    document.getElementById('e_'+k).style.opacity=pr(t,t0,0.2)*(1-peace); }}
  const tde=TS(PAN.de[0],PAN.de[1]), tpl=TS(PAN.pl[0],PAN.pl[1]);
  document.getElementById('e_de').style.opacity=pr(t,tde,0.3)*(1-peace);
  const pulse=t>tpl&&t<tpl+2.4?0.25*Math.sin((t-tpl)*2*Math.PI/0.8):0;
  document.getElementById('e_pl').style.opacity=cl(pr(t,tpl,0.3)*(0.85+pulse),0,1)*(1-pr(t,S['p5'],0.5))*(1-peace);
  document.getElementById('arrow').style.strokeDashoffset=1-ease(pr(t,tpl-0.2,0.7));
  document.getElementById('arrow').style.opacity=1-pr(t,S['p4@Europa'],0.4);
  document.getElementById('e_peace').style.opacity=peace;
  // Abdunkeln für die Kernbotschaft
  M.style.opacity=1-0.55*pr(t,TS(PAN.dim[0],PAN.dim[1]),0.5);
  let yr=PAN.years[0][1]; for(const [a,s] of PAN.years) if(t>=S[a]) yr=s; document.getElementById('yr').textContent=yr;
  // Zeitleiste
  let f=0, prv=0; for(const k of PAN.tl){{ const a=S[k[0]]; if(t>=a) {{ f=prv+(k[1]-prv)*ease(pr(t,a,1.2)); }} prv=k[1]; }}
  const tl=[[S[PAN.tl[0][0]]]];
  document.getElementById('tfill').style.transform=`scaleX(${{f}})`; document.getElementById('tfill').style.background=peace>0.5?'#19C6B4':'#E5484D';
  document.getElementById('tdot').style.left=(26+864*f)+'px'; document.getElementById('tdot').style.opacity=t>=tl[0][0]?1:0;
  document.querySelector('#tdot .tipdot').style.background=peace>0.5?'#19C6B4':'#E5484D';
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
