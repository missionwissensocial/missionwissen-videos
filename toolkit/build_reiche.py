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
CH = ["01 DIE FRAGE", "02 ROM", "03 MONGOLEN", "04 BRITEN", "05 UND DU?"]
B = [
 ("p1", 0, "Das größte Reich aller Zeiten?", "Welches *Reich* war das *größte* aller *Zeiten?*", None),
 ("p2", 1, "Das Römische Reich?", "Das *Römische* *Reich?*", None),
 ("p3", 1, "Nicht mal annähernd!", "*Nicht* mal *annähernd!*", None),
 ("p4", 1, "Rom: Atlantik bis Mesopotamien", "Auf seinem *Höhepunkt* reichte *Rom* vom *Atlantik* bis nach *Mesopotamien,* rund *fünf* *Millionen* *Quadratkilometer.*", None),
 ("p5", 2, "Viel größer: die Mongolen", "Viel *größer* wurde das *Reich* der *Mongolen:*", None),
 ("p6", 2, "Von Korea bis Osteuropa", "*Dschingis* *Khan* und seine *Nachfolger* eroberten im *dreizehnten* *Jahrhundert* ein *Gebiet* von *Korea* bis nach *Osteuropa.*", None),
 ("p7", 2, "Größtes Reich am Stück", "Das ist bis *heute* das *größte* *zusammenhängende* *Reich* der *Geschichte.*", None),
 ("p8", 3, "Der Rekord: eine Insel", "Doch den *Rekord* hält ein *Reich,* das von einer *Insel* aus *regiert* wurde: *Großbritannien.*", None),
 ("p9", 3, "Ein Viertel der Welt", "Um *neunzehnhundertzwanzig* gehörte zum *Britischen* *Weltreich* rund ein *Viertel* aller *Landflächen* der *Erde,* verteilt rund um den *Globus.*", None),
 ("p10", 3, "Die Sonne geht nie unter", "Deshalb hieß es: In diesem *Reich* geht die *Sonne* *nie* *unter.*", None),
 ("p11", 4, "Und dein Tipp?", "Und *welches* *Reich* hättest du *vorne* *gesehen?*", None),
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


# ================= Bühne: Weltkarte mit wachsenden Reichen + Größen-Balken (durchgehend) =================
CENTER = "display:flex;justify-content:center"
I.update(
 sun='<circle cx="24" cy="24" r="8"/><path d="M24 6v5M24 37v5M6 24h5M37 24h5M11 11l3.5 3.5M33.5 33.5L37 37M11 37l3.5-3.5M33.5 14.5L37 11"/>',
 crown='<path d="M7 36L5 14l11 9 8-13 8 13 11-9-2 22z"/><path d="M8 41h32"/>',
)
GEO = json.load(open("geo.json")); K = GEO["K"]; GW, GH = GEO["W"], GEO["H"]
def WX(lon): return (lon + 180) * K
def WY(lat): return (90 - lat) * K
def CAM(lat, lon, z, fy=270): return [round(WX(lon), 1), round(WY(lat), 1), z, fy]
FULL = [540, 205, 0.85, 270]
ROMV = CAM(40, 17, 2.5); MONV = CAM(42, 80, 1.45, 280); LONV = CAM(52.5, -1, 4.2, 270)
cam = [("p1", 0, *FULL), ("p2", 0, *FULL), ("p2@Römische", 0.1, *ROMV), ("p5", -0.2, *ROMV), ("p5@Mongolen", 0.3, *MONV),
       ("p8", 0, *MONV), ("p8@Insel", 0.1, *LONV), ("p9", 0, *LONV), ("p9@Weltreich", 0.2, *FULL)]
GROW = dict(rome=[12.5, 41.9, "p2@Römische", 0.2, 1.4], mong=[102.8, 47.2, "p5@Mongolen", -0.1, 4.0], brit=[-0.1, 51.5, "p9@Britischen", -0.2, 2.6])
GEOJS = dict(cam=cam, grow={k: [WX(v[0]), WY(v[1]), v[2], v[3], v[4]] for k, v in GROW.items()}, W=GW, H=GH,
             night=["p10@Sonne", -1.2, "p11", 0.2])
landp = f'<path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
def emp(eid, fill, stroke, clip=None, d=None):
    inner = (f'<path d="{d or GEO["land"]}" fill="{fill}" stroke="{stroke}" stroke-width="2.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>')
    g = f'<g clip-path="url(#gc_{eid})">{inner}</g>'
    if clip: g = f'<g clip-path="url(#pc_{eid})">{g}</g>'
    return f'<g id="e_{eid}" style="opacity:0">{g}</g>'
defs = (f'<defs><linearGradient id="ngr" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#141634" stop-opacity="0"/><stop offset=".12" stop-color="#141634" stop-opacity=".5"/><stop offset=".88" stop-color="#141634" stop-opacity=".5"/><stop offset="1" stop-color="#141634" stop-opacity="0"/></linearGradient><clipPath id="win"><rect x="0" y="0" width="{GW}" height="{GH}"/></clipPath>'
        f'<clipPath id="pc_rome"><path d="{GEO["rome"]}"/></clipPath><clipPath id="pc_mong"><path d="{GEO["mong"]}"/></clipPath>'
        + "".join(f'<clipPath id="gc_{k}"><circle id="gcc_{k}" cx="0" cy="0" r="0"/></clipPath>' for k in GROW) + '</defs>')
mapsvg = (f'<svg width="920" height="530" style="position:absolute;left:0;top:0;overflow:hidden">{defs}<g id="mapg"><g clip-path="url(#win)">{landp}'
          + emp("rome", "rgba(138,143,153,.55)", "#5D616B", True) + emp("mong", "rgba(25,198,180,.45)", "#0E8C80", True)
          + emp("brit", "rgba(123,63,228,.45)", PUR, False, GEO["brit"])
          + f'<g id="nightg" style="opacity:0"><rect id="n1" x="0" y="-20" width="{GW * 0.56}" height="{GH + 40}" fill="url(#ngr)"/><rect id="n2" x="0" y="-20" width="{GW * 0.56}" height="{GH + 40}" fill="url(#ngr)"/></g>'
          + '</g></g></svg>')
def lab(lat, lon, text, i, o, col=PUR, d=0, pin=True):
    p = f'<span class="pin" style="background:{col}"></span>' if pin else ""
    return (f'<div class="geo" data-x="{WX(lon):.1f}" data-y="{WY(lat):.1f}" style="position:absolute;left:0;top:0">'
            f'<div class="el mk" {A(i, o, d)} style="left:{-11 if pin else -40}px;top:-14px;gap:8px">{p}'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
ov = (lab(41.9, 12.5, "ROM", "p2@Reich", "p5", "#3F434C")
      + lab(43, -27, "ATLANTIK", "p4@Atlantik", "p5", "#3F434C", 0, False)
      + lab(33.3, 44.4, "MESOPOTAMIEN", "p4@Mesopotamien", "p5", "#3F434C")
      + lab(47.2, 102.8, "MONGOLEI", "p5@Mongolen", "p8", "#0E8C80", 0.3)
      + lab(37.5, 127.5, "KOREA", "p6@Korea", "p8", "#0E8C80")
      + lab(50.5, 30.5, "OSTEUROPA", "p6@Osteuropa", "p8", "#0E8C80")
      + lab(51.5, -0.1, "LONDON", "p8@Insel", "p9@Weltreich", PUR, 0.2)
      + lab(58, -100, "KANADA", "p9@Globus", "p11", PUR, 0, False)
      + lab(22, 79, "INDIEN", "p9@Globus", "p11", PUR, 0.15, False)
      + lab(-25, 134, "AUSTRALIEN", "p9@Globus", "p11", PUR, 0.3, False)
      + lab(-8, 20, "AFRIKA", "p9@Globus", "p11", PUR, 0.45, False))
# Größen-Balken (bildschirmfest, unten im Panel)
def brow(name, val, col, anchor, dec):
    return (f'<div class="el" {A(anchor, None, 0)} data-sfx="glass" style="position:relative">'
            f'<div class="row" style="justify-content:space-between;width:868px"><span class="mono" style="font-size:22px;font-weight:700">{name}</span>'
            f'<span class="mono" style="font-size:24px;font-weight:700">≈ {cnt(val, anchor, dec, 0.1)} MIO. KM²</span></div>'
            f'<div class="hbar" style="width:868px;height:22px;margin-top:6px"><div class="gbar2" data-ga="{anchor}" style="width:{val / 35.5 * 100:.1f}%;background:{col}"></div></div></div>')
bars = (f'<div style="position:absolute;left:0;top:530px;width:920px;height:230px;background:rgba(255,255,255,.93);border-top:1px solid rgba(26,31,51,.12);padding:16px 26px">'
        f'<div class="col" style="gap:10px;align-items:flex-start">'
        + brow("RÖMISCHES REICH · 117 N. CHR.", 5, "#8A8F99", "p4@fünf", 0)
        + brow("MONGOLISCHES REICH · UM 1300", 24, TQ, "p7@zusammenhängende", 0)
        + brow("BRITISCHES WELTREICH · 1920", 35.5, PUR, "p9@Viertel", 1) + '</div></div>')
chips = (el('<div class="chip mono" style="font-size:19px;padding:8px 12px">MENSCHHEITSGESCHICHTE · FOLGE 4</div>', 18, 18, A("p1", "p3", -0.6) + ' data-sfx="none"')
         + f'<div class="el" {A("p2@Reich", "p11", 0)} data-sfx="none" style="right:18px;top:18px"><div class="chip mono" style="font-size:22px;padding:8px 14px;background:rgba(255,255,255,.95)"><span id="yr">117 N. CHR.</span></div></div>'
         + el('<div class="chip mono" style="font-size:16px;padding:5px 9px;color:#8A8F99;border-color:#C9CCD3;background:rgba(255,255,255,.9)">GRENZEN SCHEMATISCH · FLÄCHEN: SCHÄTZUNG (TAAGEPERA)</div>', 18, 492, A("p2@Reich", "end", 0.3) + ' data-sfx="none"'))
stage.append(mm(mapsvg + ov + bars + chips, 80, 460, 920, 760, A("p1", "end", -0.6)))

# ---- Overlays ----
stage.append(el(f'<div class="chip mono row" style="font-size:30px;gap:14px;padding:12px 22px;background:rgba(255,255,255,.95);border-color:{PUR}">{ic(I["crown"], 40, PUR, 3.2)}DAS GRÖSSTE REICH?</div>', 80, 1070, A("p1", "p2@Römische", -0.6) + ' data-sfx="none"', 920, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:52px">NICHT MAL ANNÄHERND!</div>', 80, 760, A("p3@Nicht", "p4"), 920, CENTER))
stage.append(el(f'<div class="chip mono" style="font-size:26px;padding:10px 18px;border-color:{TQ};background:rgba(255,255,255,.95)">DSCHINGIS KHAN &amp; NACHFOLGER · 13. JH.</div>', 80, 860, A("p6@Dschingis", "p7", 0) + ' data-sfx="marker"', 920, CENTER))
stage.append(el(f'<div class="stamp mono" style="font-size:40px;color:#0E8C80;border-color:#19C6B4">GRÖSSTES ZUSAMMENHÄNGENDES REICH</div>', 80, 860, A("p7@größte", "p8"), 920, CENTER))
stage.append(el(f'<div class="chip mono row" style="font-size:28px;gap:12px;padding:12px 20px;border-color:{PUR};background:rgba(255,255,255,.95)">≈ ¼ ALLER LANDFLÄCHEN DER ERDE</div>', 80, 880, A("p9@Viertel", "p10", 0) + ' data-sfx="glass"', 920, CENTER))
stage.append(el(f'<div class="chip mono row" style="font-size:28px;gap:12px;padding:12px 20px;border-color:#E8A21A;background:rgba(255,255,255,.95)">{ic(I["sun"], 40, "#E8A21A", 3.2)}„DIE SONNE GEHT NIE UNTER“</div>', 80, 880, A("p10@Sonne", "p11", 0) + ' data-sfx="marker"', 920, CENTER))
# p11 Frage
stage.append(card(f'<div class="col" style="gap:16px;height:100%;justify-content:center"><div class="mono small grey">WELCHES REICH HÄTTEST DU VORNE GESEHEN?</div>'
                  f'<div class="row" style="gap:16px"><div class="chip mono" style="font-size:30px;border-color:#8A8F99">ROM</div><div class="chip tq mono" style="font-size:30px">MONGOLEN</div><div class="chip pu mono" style="font-size:30px">BRITEN</div></div></div>',
                  130, 560, 820, 220, "active", A("p11@welches", "end")))
stage.append(el('<div class="chip pu mono" style="font-size:22px;background:rgba(255,255,255,.95)">SCHREIB\'S IN DIE KOMMENTARE</div>', 260, 800, f'{A("p11@gesehen", "end", 0.1)} data-sfx="plop"', 560, CENTER))
YEARS = [("p2@Reich", "117 N. CHR."), ("p5@Mongolen", "UM 1300"), ("p8@Rekord", "UM 1920")]
GEOJS["years"] = YEARS
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
 // ---- Bühne: Weltkarte mit wachsenden Reichen ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const M=document.getElementById('mapg');
  const keys=PAN.cam.map(k=>({{t:TS(k[0],k[1]),x:k[2],y:k[3],z:k[4],fy:k[5]}}));
  function base(tt){{ if(tt<=keys[0].t) return keys[0]; for(let i=0;i<keys.length-1;i++){{ const k0=keys[i],k1=keys[i+1]; if(tt>=k0.t&&tt<k1.t){{ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e),fy:k0.fy+(k1.fy-k0.fy)*e}}; }} }} return keys[keys.length-1]; }}
  const bs=base(t), z=bs.z, cx=bs.x, cy=bs.y, FX=460, FY=bs.fy;
  M.setAttribute('transform',`translate(${{FX}},${{FY}}) scale(${{z}}) translate(${{-cx}},${{-cy}})`);
  const pj=(x,y)=>[FX+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('.geo')){{ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }}
  // Reiche wachsen kreisförmig vom Zentrum aus
  for(const [k,v] of Object.entries(PAN.grow)){{ const t0=TS(v[2],v[3]), q=ease(pr(t,t0,v[4]));
    const C=document.getElementById('gcc_'+k); C.setAttribute('cx',v[0]); C.setAttribute('cy',v[1]); C.setAttribute('r',(1400*q).toFixed(1));
    const E=document.getElementById('e_'+k); E.style.opacity=pr(t,t0,0.2);
    if(k==='rome') E.style.opacity=pr(t,t0,0.2)*(1-0.45*pr(t,S['p5@Mongolen'],0.6))*(1-0.6*pr(t,S['p9@Britischen'],0.6));
    if(k==='mong') E.style.opacity=pr(t,t0,0.2)*(1-0.65*pr(t,S['p9@Britischen'],0.6)); }}
  // Weltreich pulsiert leicht, wenn fertig
  // Jahr-Chip
  let yr=PAN.years[0][1]; for(const [a,s] of PAN.years) if(t>=S[a]) yr=s; document.getElementById('yr').textContent=yr;
  // Tag/Nacht wandert über die Karte (p10)
  const nt0=TS(PAN.night[0],PAN.night[1]), nt1=TS(PAN.night[2],PAN.night[3]);
  const NG=document.getElementById('nightg'); NG.style.opacity=pr(t,nt0,0.4)*(1-pr(t,nt1,0.4));
  const off=((t-nt0)*PAN.W/3.2)%PAN.W; const x1=PAN.W-off;
  document.getElementById('n1').setAttribute('x',x1.toFixed(1)); document.getElementById('n2').setAttribute('x',(x1-PAN.W).toFixed(1));
  for(const e of document.querySelectorAll('.gbar2')) e.style.transform=`scaleX(${{ease(pr(t,S[e.dataset.ga]+0.1,0.9))}})`;
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
