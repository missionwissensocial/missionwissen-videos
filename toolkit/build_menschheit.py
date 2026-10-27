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
CH = ["01 DIE FRAGE", "02 URSPRUNG", "03 AUFBRUCH", "04 EUROPA", "05 AMERIKA", "06 UND DU?"]
B = [
 ("p1", 0, "Woher kommen wir alle?", "Alle *Menschen* auf der *Erde* haben *dieselbe* *Ur-Heimat.*", None),
 ("p2", 0, "In Afrika!", "Weißt du, *wo?* In *Afrika!*", None),
 ("p3", 1, "Die ältesten Knochen", "Die *ältesten* *Knochen* unserer *Art* sind rund *dreihunderttausend* *Jahre* alt und stammen aus *Marokko.*", None),
 ("p4", 1, "Lange nur in Afrika", "*Lange* blieben unsere *Vorfahren* auf diesem *Kontinent.*", None),
 ("p5", 2, "Der große Aufbruch", "Die *große* *Auswanderung* begann erst vor etwa *sechzigtausend* *Jahren:* über die *Arabische* *Halbinsel* nach *Asien.*", None),
 ("p6", 2, "Bis nach Australien", "Von dort ging es an den *Küsten* entlang bis nach *Australien,* übers *Meer,* vermutlich mit *Booten* oder *Flößen.*", None),
 ("p7", 3, "Ab nach Europa", "Andere zogen nach *Europa* und trafen dort auf die *Neandertaler.*", None),
 ("p8", 3, "Steckt noch in uns", "Ein *kleines* *Stück* von ihnen steckt bis *heute* im *Erbgut* vieler *Menschen.*", None),
 ("p9", 4, "Zuletzt: Amerika", "*Zuletzt* kam *Amerika* dran: über eine *eiszeitliche* *Landbrücke* von *Sibirien* nach *Alaska* und bis ganz in den *Süden.*", None),
 ("p10", 4, "Alle aus Afrika", "Wir *alle* stammen also aus *Afrika,* nur mit ziemlich *langem* *Umweg.*", None),
 ("p11", 5, "Hättest du's gewusst?", "*Hättest* du das *gewusst,* *ja* oder *nein?*", "winkt"),
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
 bone='<path d="M13 19a5 5 0 1 1 6-7l17 17a5 5 0 1 1 7 6 5 5 0 1 1-7 6L19 24a5 5 0 1 1-6-5z"/>',
 dna='<path d="M15 4c0 13 18 13 18 20S15 31 15 44M33 4c0 13-18 13-18 20s18 7 18 20M19 11h10M18 37h12M21 17h6M21 31h6"/>',
 boat='<path d="M5 30h38l-6 9H11z"/><path d="M24 7v23M24 9l13 17H24"/>',
 walk='<circle cx="26" cy="8" r="4"/><path d="M24 15l-5 13 7 6 3 10M19 28l-6 14M22 18l9 6 6-2M21 19l-8 6"/>',
)
CENTER = "display:flex;justify-content:center"
GEO = json.load(open("geo.json")); K = GEO["K"]
def WX(lon): return ((lon + 360 if lon < -27 else lon) + 180) * K
def WY(lat): return (90 - lat) * K
def CAM(lat, lon, z, fy=450): return [round(WX(lon), 1), round(WY(lat), 1), z, fy]
FULL = CAM(11, 153, 0.85, 380)
AFR = CAM(3, 18, 2.5, 450); MOR = CAM(24, 2, 3.1, 470)
cam = [("p1", 0, *FULL), ("p2@Afrika", -0.5, *FULL), ("p2@Afrika", 0.6, *AFR), ("p3@ältesten", 0, *AFR),
       ("p3@dreihunderttausend", 0.3, *MOR), ("p4", 0, *MOR), ("p4@Vorfahren", 0.2, *AFR), ("p5", 0, *AFR),
       ("p5@Auswanderung", 0.5, *CAM(18, 50, 2.4)), ("p6", 0, *CAM(20, 80, 2.1)), ("p6@Australien", 0.3, *CAM(-5, 115, 1.9)),
       ("p7", 0, *CAM(32, 38, 2.3)), ("p8", 0.2, *CAM(44, 15, 2.6, 520)), ("p9", 0, *CAM(44, 15, 2.2)),
       ("p9@Amerika", 0.2, *CAM(35, 95, 1.7)), ("p9@Landbrücke", 0, *CAM(62, 180, 2.0)), ("p9@Alaska", 0.3, *CAM(45, -125, 1.6)),
       ("p9@Süden", 0, *CAM(-20, -70, 1.5)), ("p10", -0.1, *CAM(-20, -70, 1.5)), ("p10@stammen", 0.4, *CAM(11, 153, 0.85, 360))]
segdef = [("A0", ("p4@Lange", 0), ("p4@Kontinent", 0.3), 0, 0), ("A", ("p5@Auswanderung", 0.2), ("p5@Asien", 0.3), 0, 0),
          ("B1", ("p6@Küsten", -0.2), ("p6@Meer", -0.1), 0, 0), ("B2", ("p6@Meer", -0.1), ("p6@Flößen", 0), 1, 1),
          ("B3", ("p6@Flößen", 0), ("p6@Flößen", 0.9), 0, 0), ("C", ("p7@zogen", 0), ("p7@Neandertaler", 0), 0, 0),
          ("D1", ("p9@Amerika", 0), ("p9@Sibirien", 0.2), 0, 0), ("D2", ("p9@Sibirien", 0.2), ("p9@Alaska", 0.3), 0, 0),
          ("D3", ("p9@Alaska", 0.3), ("p9@Süden", 0.6), 0, 0)]
GEOJS = dict(cam=cam, segs=[dict(id=k, a=a, b=b, lin=l, dash=d, pts=GEO["seg"][k]) for k, a, b, l, d in segdef],
             follow=[["A", "B1", "B2", "B3"], ["C"], ["D1", "D2", "D3"]], fend=[("p6@Flößen", 0.6), ("p7@Neandertaler", 0.4), ("p9@Süden", 0.7)],
             hook=GEO["hook"], afr=GEO["afr_pts"])
# --- Karten-Panel (durchgehend p1..p10) ---
lines = ""
for k, a, b, l, d in segdef:
    dash = 'stroke-dasharray="1 13"' if d else ""
    lines += (f'<polyline id="c_{k}" points="" fill="none" stroke="#FFFFFF" stroke-width="13" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" {"" if not d else 'opacity="0"'}/>'
              f'<polyline id="t_{k}" points="" fill="none" stroke="{PUR}" stroke-width="{8 if d else 6}" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" {dash}/>')
bx, by = WX(180), WY(65.5)
mapsvg = (f'<svg width="920" height="760" style="position:absolute;left:0;top:0;overflow:hidden"><defs><clipPath id="win"><rect x="459" y="0" width="1080" height="460"/></clipPath></defs>'
          f'<g id="mapg"><g clip-path="url(#win)"><path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
          f'<path id="afr" d="{GEO["afr"]}" fill="rgba(123,63,228,.16)" stroke="{PUR}" stroke-width="2.4" stroke-linejoin="round" vector-effect="non-scaling-stroke" style="opacity:0"/>'
          f'<ellipse id="bering" cx="{bx:.1f}" cy="{by:.1f}" rx="27" ry="12" fill="rgba(25,198,180,.30)" stroke="{TQ}" stroke-width="2.4" stroke-dasharray="6 6" vector-effect="non-scaling-stroke" style="opacity:0"/></g>'
          f'{lines}</g></svg>')
ov = ""
for i in range(len(GEO["hook"])):
    ov += f'<div class="hdot" data-i="{i}" style="position:absolute;left:0;top:0"><div class="el aa" {A("p1", "end", round(0.05 + i * 0.075, 3))} style="left:-10px;top:-10px"><div class="dot"></div></div></div>'
def lab(lat, lon, text, i, o, col=PUR, d=0, dx=18, cls="mk", icon=None):
    pin = f'<span class="pin" style="background:{col}"></span>' if not icon else f'<span class="ipin">{ic(I[icon], 40, col, 3.4)}</span>'
    return (f'<div class="geo" data-x="{WX(lon):.1f}" data-y="{WY(lat):.1f}" style="position:absolute;left:0;top:0">'
            f'<div class="el {cls}" {A(i, o, d)} style="left:{-11 if not icon else -26}px;top:{-14 if not icon else -26}px;gap:10px">{pin}'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
ov += lab(31.9, -8.9, "MAROKKO", "p3@Marokko", "p5", d=-0.1)
ov += lab(21, 46, "ARABIEN", "p5@Arabische", "p10")
ov += lab(23, 77, "ASIEN", "p5@Asien", "p10")
ov += lab(-25.5, 134.5, "AUSTRALIEN", "p6@Australien", "p10")
ov += lab(-11, 128, "ÜBERS MEER", "p6@Meer", "p7", TQ, icon="boat")
ov += lab(48, 10, "EUROPA", "p7@Europa", "p10")
ov += lab(43.5, 3, "NEANDERTALER", "p7@Neandertaler", "p9", "#8A8F99", icon="walk")
ov += lab(62, 128, "SIBIRIEN", "p9@Sibirien", "p10")
ov += lab(68.5, -178, "EISZEIT-LANDBRÜCKE", "p9@Landbrücke", "p10", "#0E8C80", icon=None)
ov += lab(64, -152, "ALASKA", "p9@Alaska", "p10")
ov += lab(-52, -70, "BIS GANZ IN DEN SÜDEN", "p9@Süden", "p10")
ov += '<div id="tip" style="position:absolute;left:0;top:0;opacity:0"><div class="tipring"></div><div class="tipdot"></div></div>'
ov += el('<div class="chip mono" style="font-size:19px;padding:8px 12px">MENSCHHEITSGESCHICHTE · FOLGE 1</div>', 22, 22, A("p1", "p2@Afrika", 0.2) + ' data-sfx="none"')
ov += el('<div class="chip mono" style="font-size:17px;padding:6px 10px;color:#8A8F99;border-color:#C9CCD3">ROUTE SCHEMATISCH</div>', 670, 708, A("p4@Lange", "p11", 0.4) + ' data-sfx="none"')
stage.append(mm(mapsvg + f'<div id="ov" style="position:absolute;inset:0">{ov}</div>', 80, 460, 920, 760, A("p1", "p11", -0.4)))
# --- Overlays über der Karte ---
stage.append(el('<div class="stamp mono" style="font-size:52px;color:#7B3FE4;border-color:#7B3FE4">1 UR-HEIMAT?</div>', 80, 1075, A("p1@Ur-Heimat", "p2"), 920, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:60px;color:#0E8C80;border-color:#19C6B4">AFRIKA!</div>', 80, 495, A("p2@Afrika", "p3"), 920, CENTER))
stage.append(card(f'<div class="row" style="gap:28px;height:100%">{ic(I["bone"],80,PUR)}<div class="col" style="gap:4px;align-items:flex-start"><div class="mono small grey">ÄLTESTE FUNDE · MAROKKO</div><div class="bignum" style="font-size:58px;letter-spacing:-1.5px">≈ {cnt(300, "p3@dreihunderttausend")}.000 Jahre</div></div></div>', 110, 490, 860, 160, "active", A("p3@Knochen", "p4")))
stage.append(card(f'<div class="row" style="gap:28px;height:100%">{ic(I["walk"],80,PUR)}<div class="col" style="gap:4px;align-items:flex-start"><div class="mono small grey">AUFBRUCH VOR ETWA</div><div class="bignum" style="font-size:58px;letter-spacing:-1.5px">{cnt(60, "p5@sechzigtausend")}.000 Jahren</div></div></div>', 110, 490, 860, 160, "active", A("p5@sechzigtausend", "p6", -0.3)))
stage.append(card(f'<div class="row" style="gap:28px;height:100%">{ic(I["dna"],80,TQ)}<div class="col" style="gap:4px;align-items:flex-start"><div class="mono small grey">IM ERBGUT VIELER MENSCHEN</div><div class="bignum" style="font-size:52px;letter-spacing:-1.5px">ein Stück Neandertaler</div></div></div>', 110, 490, 860, 160, "activeTQ", A("p8@Stück", "p9")))
stage.append(el('<div class="stamp mono" style="font-size:52px;color:#7B3FE4;border-color:#7B3FE4">ALLE AUS AFRIKA</div>', 80, 1075, A("p10@Afrika", "p11"), 920, CENTER))
# p11 Frage (Roboter winkt)
stage.append(card(f'<div class="row" style="gap:30px;height:100%;justify-content:center">{ic(I["globe"],130,PUR)}<div class="qbig" style="position:static;font-size:150px;line-height:1">?</div></div>', 440, 470, 560, 300, "active", A("p11@Hättest", "end")))
stage.append(el('<div class="row" style="gap:24px;justify-content:center"><div class="chip tq mono" style="font-size:40px;padding:14px 34px">JA</div><div class="chip mono" style="font-size:40px;padding:14px 34px">NEIN</div></div>', 440, 820, f'{A("p11@ja", "end")} data-sfx="plop"', 560))
stage.append(el('<div class="chip pu mono" style="font-size:22px">SCHREIB\'S IN DIE KOMMENTARE</div>', 440, 960, f'{A("p11@nein", "end", 0.2)} data-sfx="plop"', 560, CENTER))

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
</style></head><body><div id="v">
<div id="chap" class="mono"></div><div id="prog">{"".join("<div></div>" for _ in CH)}</div><div id="wm">{mono}</div>
<div id="head"></div>
{"".join(stage)}
{endcard}
<div id="robot">{robots}</div>
<div id="cap"><div id="pill"></div></div>
</div>
<script>
const GEO={json.dumps(GEOJS, ensure_ascii=False)};
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
 // ---- Weltkarte + Spur ----
 {{
  const M=document.getElementById('mapg');
  const TS=k=>(S[k[0]]??0)+k[1];
  const qe=p=>p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2;
  const SG={{}}; for(const s of GEO.segs) SG[s.id]=s;
  const segProg=(s,tt)=>{{const p=cl((tt-TS(s.a))/(TS(s.b)-TS(s.a)),0,1); return s.lin?p:qe(p);}};
  const ptAt=(s,q)=>{{const n=s.pts.length, f=q*(n-1), i=Math.floor(f), j=Math.min(n-1,i+1), u=f-i; return [s.pts[i][0]*(1-u)+s.pts[j][0]*u, s.pts[i][1]*(1-u)+s.pts[j][1]*u];}};
  function tipOf(ids,tt){{let tip=null; for(const id of ids){{const s=SG[id]; if(tt<TS(s.a)) continue; tip=ptAt(s,segProg(s,tt));}} return tip;}}
  const keys=GEO.cam.map(k=>({{t:(S[k[0]]??0)+k[1],x:k[2],y:k[3],z:k[4],fy:k[5]}}));
  function base(tt){{ if(tt<=keys[0].t) return keys[0]; for(let i=0;i<keys.length-1;i++){{ const k0=keys[i],k1=keys[i+1]; if(tt>=k0.t&&tt<k1.t){{ const u=(tt-k0.t)/Math.max(1e-6,k1.t-k0.t), e=u*u*(3-2*u); return {{x:k0.x+(k1.x-k0.x)*e,y:k0.y+(k1.y-k0.y)*e,z:Math.exp(Math.log(k0.z)+(Math.log(k1.z)-Math.log(k0.z))*e),fy:k0.fy+(k1.fy-k0.fy)*e}}; }} }} return keys[keys.length-1]; }}
  const bs=base(t); let cx=bs.x, cy=bs.y;
  GEO.follow.forEach((ids,gi)=>{{ const a=TS(SG[ids[0]].a), z=TS(GEO.fend[gi]); const w=ease(pr(t,a,0.6))*(1-ease(pr(t,z,0.7))); if(w<=0) return;
    let sx=0,sy=0,nn=0; for(let k=0;k<6;k++){{ const p=tipOf(ids,t-k*0.1); if(p){{sx+=p[0];sy+=p[1];nn++;}} }}
    if(nn){{ cx+=(sx/nn-cx)*w; cy+=(sy/nn-cy)*w; }} }});
  const z=bs.z, FX=460, FY=bs.fy;
  M.setAttribute('transform',`translate(${{FX}},${{FY}}) scale(${{z}}) translate(${{-cx}},${{-cy}})`);
  const pj=(x,y)=>[FX+(x-cx)*z, FY+(y-cy)*z];
  let tip=null, tipOn=0;
  for(const s of GEO.segs){{ const t0=TS(s.a); let str='';
    if(t>=t0){{ const q=segProg(s,t), n=s.pts.length, f=q*(n-1), i=Math.floor(f); const arr=s.pts.slice(0,i+1); arr.push(ptAt(s,q)); str=arr.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' '); tip=ptAt(s,q); tipOn=1; }}
    document.getElementById('c_'+s.id).setAttribute('points',str); document.getElementById('t_'+s.id).setAttribute('points',str); }}
  const TP=document.getElementById('tip');
  if(tip){{ const p=pj(tip[0],tip[1]); TP.style.left=p[0]+'px'; TP.style.top=p[1]+'px'; }}
  TP.style.opacity=tipOn*(1-pr(t,S['p10'],0.3));
  const rg=TP.querySelector('.tipring'); const ph=(t%1.1)/1.1; rg.style.transform=`scale(${{0.5+1.1*ph}})`; rg.style.opacity=1-ph;
  // Menschen-Punkte: Welt -> Afrika -> Welt
  const ta=S['p2@Afrika']-0.5, tb=S['p10']+0.2;
  for(const d of document.querySelectorAll('.hdot')){{ const i=+d.dataset.i, h=GEO.hook[i], a=GEO.afr[i];
    const u1=ease(pr(t,ta+i*0.012,0.9)), u2=ease(pr(t,tb+i*0.03,1.3)); let u=u1*(1-u2);
    const wob=u1*(1-u2); const x=h[0]+(a[0]-h[0])*u+wob*1.3*Math.sin(t*2.1+i), y=h[1]+(a[1]-h[1])*u+wob*1.3*Math.cos(t*1.7+i*1.3);
    const p=pj(x,y); d.style.left=p[0]+'px'; d.style.top=p[1]+'px'; }}
  for(const g of document.querySelectorAll('.geo')){{ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }}
  const AF=document.getElementById('afr'); AF.style.opacity=pr(t,S['p2@Afrika']-0.2,0.4)*(t>S['p10']?0.65+0.35*Math.sin((t-S['p10'])*5):1);
  document.getElementById('bering').style.opacity=pr(t,S['p9@eiszeitliche'],0.4)*(1-pr(t,S['p10'],0.4));
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
