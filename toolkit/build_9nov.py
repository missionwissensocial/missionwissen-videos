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
HOOK = 'Der <span style="color:#7B3FE4">9. November</span>: viermal Geschichte'
B = [
 ("n1", 0, HOOK, "Heute ist der *neunte* *November.*", "staunt"),
 ("n2", 0, HOOK, "An diesem Tag wurde in *Deutschland* *viermal* *Geschichte* geschrieben.", None),
 ("n3", 0, HOOK, "Und warum er trotzdem *kein* *Feiertag* ist, zeige ich dir am *Ende.*", None),
 ("n4", 1, "", "*Neunzehnhundertachtzehn.* In *Berlin* wird verkündet: Der *Kaiser* *dankt* *ab.*", None),
 ("n5", 1, "", "Der Politiker *Philipp* *Scheidemann* ruft die *Republik* aus.", None),
 ("n6", 1, "", "Deutschland wird zum *ersten* *Mal* eine *Demokratie.*", None),
 ("n7", 2, "", "*Neunzehnhundertdreiundzwanzig.* In *München* *scheitert* ein *Putsch,* also ein *gewaltsamer* *Umsturzversuch* gegen diese *junge* *Demokratie.*", None),
 ("n8", 2, "", "Angeführt hat ihn *Adolf* *Hitler.*", None),
 ("n9", 2, "", "Keine *zehn* *Jahre* später ist er trotzdem an der *Macht.*", None),
 ("n10", 3, "", "*Neunzehnhundertachtunddreißig.* Hitlers *Nationalsozialisten* *hetzen* seit Jahren gegen *Juden.*", None),
 ("n11", 3, "", "In dieser *Nacht* zünden ihre *Trupps* *überall* in *Deutschland* *Synagogen* an, also *jüdische* *Gotteshäuser.*", None),
 ("n12", 3, "", "*Jüdische* *Geschäfte* werden *zerstört,* *Menschen* *ermordet.*", None),
 ("n13", 3, "", "Rund *dreißigtausend* *jüdische* *Männer* kommen in *Konzentrationslager.*", None),
 ("n14", 4, "", "*Neunzehnhundertneunundachtzig.* Deutschland ist *geteilt,* in *West* und *Ost.*", None),
 ("n15", 4, "", "Mitten durch *Berlin* läuft eine *Mauer.*", None),
 ("n16", 4, "", "Die Menschen im *Osten* dürfen *nicht* *frei* in den *Westen* reisen.", None),
 ("n17", 4, "", "Am Abend verkündet ein Politiker aus dem Osten aus *Versehen* zu *früh:* Reisen sind *ab* *sofort* *möglich.*", None),
 ("n18", 4, "", "*Tausende* *strömen* zur *Grenze.*", None),
 ("n19", 4, "", "Kurz vor *Mitternacht* *öffnet* sich die *Mauer.*", None),
 ("n20", 5, "", "Den *Mauerfall* *feiern,* an dem Tag, an dem *Synagogen* *brannten?*", None),
 ("n21", 5, "", "Das *passt* *nicht.*", None),
 ("n22", 5, "", "Stattdessen feiern wir am *dritten* *Oktober.*", None),
 ("n23", 5, "", "An diesem Tag wurde *Deutschland* *neunzehnhundertneunzig* *wieder* ein *Land.*", None),
 ("n24", 5, "", "Der *neunte* *November* bleibt ein Tag des *Gedenkens.*", None),
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
GEO = json.load(open("geo.json")); K = GEO["K"]; CXF = GEO["CX"]
def WX(lon): return (lon + 180) * K * CXF
def WY(lat): return (90 - lat) * K
MAPTOP = 300; MAPH = 980
def CAMAT(lat, lon, z, sx, sy):
    """Kamera so, dass (lat,lon) bei Bildschirm (sx,sy) liegt."""
    return [round(WX(lon) + (540 - sx) / z, 2), round(WY(lat), 2), z, sy - MAPTOP]
BLAT, BLON = 52.52, 13.40; MLAT, MLON = 48.14, 11.58
BX, BY = WX(BLON), WY(BLAT)
HOOKC = CAMAT(51.2, 10.4, 27, 410, 850)
B18 = CAMAT(BLAT, BLON, 44, 400, 820)
M23 = CAMAT(MLAT, MLON, 44, 400, 820)
OVR = CAMAT(51.2, 10.4, 27, 400, 860)
BZ = CAMAT(BLAT, BLON, 560, 540, 830)
FIN = CAMAT(51.2, 10.4, 27, 540, 840)
cam = [("n1", 0, *HOOKC), ("n4", -0.15, *HOOKC), ("n4@Berlin", 0.2, *B18), ("n7", 0, *B18), ("n7@München", 0.3, *M23), ("n9", 0, *M23),
       ("n9@Jahre", 0.3, *OVR), ("n15", -0.1, *OVR), ("n15@Berlin", 0.45, *BZ), ("n20", 0, *BZ), ("n20@feiern", 0.4, *FIN)]
# Kalenderblatt (Hauptdarsteller, Bildschirm-Koordinaten Mitte)
kal = [("n1", 0, 840, 720, 1.1), ("n3", 0.3, 840, 720, 1.1), ("n4", 0.1, 730, 610, 0.9), ("n12", 0, 870, 610, 0.85), ("n13", -0.25, 905, 545, 0.6),
       ("n14", 0, 870, 600, 0.85), ("n15@Berlin", 0, 905, 545, 0.6), ("n20", 0, 905, 545, 0.6), ("n20@feiern", 0.3, 540, 770, 1.25), ("n21", 0.2, 540, 770, 1.25),
       ("n22@dritten", -0.3, 315, 770, 1.0), ("n24", -0.1, 315, 770, 1.0), ("n24@November", 0.2, 540, 740, 1.25)]
years = [("n4", "1918"), ("n7", "1923"), ("n10", "1938"), ("n14", "1989"), ("n20", "")]
# Personen (Berlin-Szene) in Weltkoordinaten
import random as _r; _r.seed(5)
RX, RY = 0.75, 0.62
ppl = []
while len(ppl) < 34:
    x, y = _r.uniform(0.14, 0.62), _r.uniform(-0.42, 0.42)
    if (x / RX) ** 2 + (y / RY) ** 2 < 0.8: ppl.append(dict(s=[round(BX + x, 3), round(BY + y, 3)]))
for i, p in enumerate(ppl):
    p["q"] = [round(BX + 0.07 + (i % 6) * 0.045, 3), round(BY + ((i // 6) - 2.5) * 0.045, 3)]
    wx_, wy_ = _r.uniform(0.15, 0.6), _r.uniform(-0.38, 0.38)
    p["w"] = [round(BX - wx_, 3), round(BY + wy_, 3)]
PANJS = dict(cam=cam, kal=kal, years=years, syn=GEO["syn"], ppl=ppl, B=[BX, BY], RX=RX, RY=RY)

PUR2 = "rgba(123,63,228,.30)"; PURS = "#5B2BB5"; GR = "#3F434C"; TQD = "#0E8C80"
land = f'<path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
def P_(d, fill, stroke, sw=1.8, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" vector-effect="non-scaling-stroke" {extra}/>'
def grp(lid, inner, clip=None):
    c = f' clip-path="url(#{clip})"' if clip else ""
    return f'<g id="e_{lid}" style="opacity:0"><g{c}>{inner}</g></g>'
defs = (f'<defs><clipPath id="landc"><path d="{GEO["land"]}"/></clipPath>'
        f'<clipPath id="ws"><path d="{GEO["wside"]}"/></clipPath><clipPath id="es"><path d="{GEO["eside"]}"/></clipPath>'
        f'<clipPath id="bw"><rect x="{BX-2:.2f}" y="{BY-2:.2f}" width="2" height="4"/></clipPath><clipPath id="be"><rect x="{BX:.2f}" y="{BY-2:.2f}" width="2" height="4"/></clipPath>'
        f'<radialGradient id="glow"><stop offset="0" stop-color="#FFB347" stop-opacity=".95"/><stop offset=".45" stop-color="#F28C28" stop-opacity=".55"/><stop offset="1" stop-color="#F28C28" stop-opacity="0"/></radialGradient>'
        '</defs>')
ell = f'M{BX-RX:.3f} {BY:.3f}A{RX} {RY} 0 1 0 {BX+RX:.3f} {BY:.3f}A{RX} {RY} 0 1 0 {BX-RX:.3f} {BY:.3f}Z'
wall_top = f'M{BX:.3f} {BY-RY-0.02:.3f}L{BX+0.03:.3f} {BY-0.3:.3f}L{BX-0.02:.3f} {BY-0.12:.3f}L{BX:.3f} {BY:.3f}'
wall_bot = f'M{BX:.3f} {BY:.3f}L{BX+0.025:.3f} {BY+0.18:.3f}L{BX-0.02:.3f} {BY+0.38:.3f}L{BX:.3f} {BY+RY+0.02:.3f}'
syn = "".join(f'<g class="syn" style="opacity:0"><circle class="sg" cx="{x}" cy="{y}" r="0.4" fill="url(#glow)"/><circle class="sc" cx="{x}" cy="{y}" r="0.12" fill="#F2A33A" stroke="#FFFFFF" stroke-width="1.5" vector-effect="non-scaling-stroke"/></g>' for x, y in GEO["syn"])
mapsvg = (f'<svg width="1080" height="{MAPH}" style="position:absolute;left:0;top:0;overflow:hidden">{defs}<g id="mapg">{land}'
          f'<g clip-path="url(#landc)">'
          + grp("kr", P_(GEO["kr"], PUR2, PURS, 2.2, 'id="f_kr"'))
          + grp("de", P_(GEO["de"], PUR2, PURS, 2.2, 'id="f_de"'))
          + grp("brd", P_(GEO["de"], "rgba(123,63,228,.40)", PURS, 2.2), "ws")
          + grp("ddr", P_(GEO["de"], "rgba(25,198,180,.40)", TQD, 2.2), "es")
          + '</g>'
          + f'<path id="bdr" d="{GEO["border"]}" fill="none" stroke="#2B2D35" stroke-width="0.2" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
          + f'<g id="e_syn">{syn}</g>'
          + f'<g id="e_ber" style="opacity:0"><path d="{ell}" fill="#FFFFFF"/>'
            f'<path d="{ell}" fill="rgba(123,63,228,.30)" clip-path="url(#bw)"/><path d="{ell}" fill="rgba(25,198,180,.32)" clip-path="url(#be)"/>'
            f'<path d="{ell}" fill="none" stroke="{INK}" stroke-width="2.2" vector-effect="non-scaling-stroke" stroke-dasharray="7 6"/>'
            f'<path id="wt" d="{wall_top}" fill="none" stroke="#3F434C" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
            f'<path id="wb" d="{wall_bot}" fill="none" stroke="#3F434C" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></g>'
          + '</g></svg>')
def lab(lat, lon, text, i, o, col=PUR, d=0, pin=True, lid="", wx=None, wy=None, dx=0, dy=0, sfx=""):
    p = f'<span class="pin" style="background:{col}"></span>' if pin else ""
    idd = f' id="{lid}"' if lid else ""
    gx = wx if wx is not None else WX(lon); gy = wy if wy is not None else WY(lat)
    sf = f' data-sfx="{sfx}"' if sfx else ""
    return (f'<div class="geo" data-x="{gx:.3f}" data-y="{gy:.3f}">'
            f'<div class="el mk"{idd} {A(i, o, d)}{sf} style="left:{(-11 if pin else -70) + dx}px;top:{-14 + dy}px;gap:8px">{p}'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
I.update(crown='<path d="M8 36l-2-22 10 9 8-13 8 13 10-9-2 22z"/><path d="M8 41h32"/>',
         mic='<rect x="18" y="5" width="12" height="22" rx="6"/><path d="M11 22a13 13 0 0 0 26 0M24 35v8M16 43h16"/>',
         ban='<circle cx="24" cy="24" r="18"/><path d="M11 11l26 26"/>',
         candle='<path d="M18 22h12v20H18z"/><path d="M24 22v-5"/><path d="M24 6c4 5 4 8 0 10c-4-2-4-5 0-10z"/>',
         clock='<circle cx="24" cy="24" r="18"/><path d="M24 12v12l-6 6"/>')
# Reichstag-Skizze (eigene, schlichte Zeichnung)
rt = (P("M10 120H250") + R(30, 60, 200, 60, 0, 2.4) + R(20, 48, 40, 72, 0, 2.2) + R(200, 48, 40, 72, 0, 2.2)
      + P("M95 60A35 30 0 0 1 165 60", 2.4) + P("M130 30V8", 2) + P("M130 8h22v12h-22", 2, PURS)
      + "".join(P(f"M{x} 72V112", 1.4, INK2) for x in (75, 95, 115, 145, 165, 185))
      + R(118, 80, 24, 26, 3, 2.2, PURS) + mesh("M30 60H230V120H30Z", 260, 130))
geo_ov = (lab(BLAT, BLON, "BERLIN", "n4@Berlin", "n7", PURS, 0.0, True, sfx="marker")
          + f'<div class="geo" data-x="{BX:.3f}" data-y="{BY:.3f}"><div id="crown" style="position:absolute;left:-46px;top:-120px;opacity:0">{ic(I["crown"], 92, "#B88A1A", 3.2)}'
            f'<div id="crx" style="position:absolute;left:-6px;top:44px;width:104px;height:7px;border-radius:4px;background:#E5484D;transform:rotate(-24deg) scaleX(0);transform-origin:left"></div></div></div>'
          + f'<div class="geo" data-x="{BX:.3f}" data-y="{BY:.3f}"><div class="el" {A("n5@Scheidemann", "n7", -0.1)} data-sfx="none" style="left:0;top:0">' + sketch(rt, 260, 130, -130, -175, "n5@Scheidemann", 0, 1.4) + '</div></div>'
          + lab(MLAT, MLON, "MÜNCHEN", "n7@München", "n9@Jahre", PURS, 0.0, True, sfx="marker")
          + lab(50.3, 7.6, "WEST", "n14@West", "n15@Berlin", PURS, 0, False, sfx="marker")
          + lab(51.9, 12.9, "OST", "n14@Ost", "n15@Berlin", TQD, 0, False, sfx="marker")
          + lab(0, 0, "WEST-BERLIN", "n15@Mauer", "n20", PURS, 0.3, False, wx=BX - 0.42, wy=BY - 0.36, dx=-40, sfx="none")
          + lab(0, 0, "OST-BERLIN", "n15@Mauer", "n20", TQD, 0.4, False, wx=BX + 0.3, wy=BY - 0.36, dx=-30, sfx="none")
          + lab(0, 0, "MAUER", "n15@Mauer", "n17", GR, 0.1, False, wx=BX + 0.02, wy=BY + 0.48, dx=-10, sfx="marker"))
note = el('<div class="note mono">KARTE SCHEMATISCH · GRENZEN VEREINFACHT</div>', 18, MAPH - 46, A("n4", "n20", 0.3) + ' data-sfx="none"')
note2 = el('<div class="note mono">ORTE SCHEMATISCH · ÜBER 1.200 SYNAGOGEN BETROFFEN</div>', 18, 170, A("n11@Synagogen", "n14", 0.4) + ' data-sfx="none"')
people = "".join(f'<div class="ppl" style="opacity:0"></div>' for _ in ppl)
stage.append(f'<div class="el mapwrap" data-in="n1" data-d="-0.6" data-out="end" data-sfx="none" style="left:0;top:{MAPTOP}px;width:1080px;height:{MAPH}px">{mapsvg}{geo_ov}<div id="pplw">{people}</div>{note}{note2}</div>')

# ---- Kalenderblatt (Hauptdarsteller) ----
kalhtml = (f'<div id="kal"><div class="kal"><div class="kalh mono">NOVEMBER</div><div class="kald">9</div>'
           f'<div id="kaly" class="kaly">1918</div>'
           f'<div id="kal2" class="col" style="gap:8px;margin-top:4px">'
           f'<div id="k89" class="krow" style="color:{TQD};border-color:#19C6B4;background:rgba(25,198,180,.10)">1989 · MAUERFALL</div>'
           f'<div id="k38" class="krow" style="color:#3F434C;border-color:#8A8F99;background:rgba(138,143,153,.12)">1938 · POGROMNACHT</div></div></div></div>')
kal3 = (f'<div class="el" {A("n22@dritten", "n24", -0.1)} data-sfx="glass" style="left:640px;top:600px;width:330px">'
        f'<div class="kal" style="border-color:#19C6B4"><div class="kalh mono" style="background:#19C6B4">OKTOBER</div><div class="kald" style="color:{TQD}">3</div>'
        f'<div class="kaly" style="color:{TQD};font-size:58px;opacity:0" id="k3y">1990</div>'
        f'<div class="krow" style="color:{TQD};border-color:#19C6B4;background:rgba(25,198,180,.12);margin-top:6px">FEIERTAG</div></div></div>')
stage.append(kalhtml)
stage.append(kal3)

# ---- Overlays (max. eins gleichzeitig) ----
OY = 1150
def chip_(txt, i, o, col=PURS, sfx="marker", icon="", y=OY, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 20px;border-color:{col};color:{col};background:rgba(255,255,255,.97);font-weight:700">{icon}{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
yrs = "".join(f'<div class="chip mono" data-yi="{k}" style="font-size:34px;font-weight:800;border-color:{PURS};color:{PURS};background:rgba(255,255,255,.97)">{y}</div>' for k, y in enumerate(["1918", "1923", "1938", "1989"]))
stage.append(el(f'<div class="row" style="gap:16px;justify-content:center" id="y4">{yrs}</div>', 40, OY, A("n2@viermal", "n3@kein", 0) + ' data-sfx="none"', 1000))
stage.append(chip_("KEIN FEIERTAG – WARUM?", "n3@kein", "n4", PURS, "glass", "", OY, 34))
stage.append(chip_("DER KAISER DANKT AB", "n4@Kaiser", "n5", "#B8383C", "marker", ic(I["crown"], 40, "#B8383C", 3)))
stage.append(chip_("PHILIPP SCHEIDEMANN RUFT DIE REPUBLIK AUS", "n5@Scheidemann", "n6", PURS, "marker", "", OY, 27))
stage.append(el(f'<div class="stamp mono" style="font-size:44px;white-space:nowrap;color:{TQD};border-color:#19C6B4">ERSTE DEMOKRATIE</div>', 40, OY - 20, A("n6@Demokratie", "n7"), 1000, CENTER))
stage.append(el(f'<div class="stamp mono" style="font-size:44px;white-space:nowrap;color:#2B2D35;border-color:#2B2D35">PUTSCH GESCHEITERT</div>', 40, OY - 20, A("n7@Putsch", "n7@gewaltsamer"), 1000, CENTER))
stage.append(chip_("PUTSCH = GEWALTSAMER UMSTURZVERSUCH", "n7@gewaltsamer", "n8", GR, "marker", "", OY, 29))
stage.append(chip_("ANFÜHRER: ADOLF HITLER", "n8@Adolf", "n9", GR, "marker"))
stage.append(chip_("1933: HITLER AN DER MACHT", "n9@Jahre", "n10", "#2B2D35", "marker"))
stage.append(chip_("HETZE GEGEN JUDEN", "n10@hetzen", "n11@Synagogen", "#2B2D35", "marker"))
stage.append(chip_("SYNAGOGEN IN BRAND GESETZT", "n11@Synagogen", "n12", "#B8383C", "none", "", OY, 30, 0.6))
stage.append(chip_("GESCHÄFTE ZERSTÖRT · MENSCHEN ERMORDET", "n12@Geschäfte", "n13", "#2B2D35", "marker", "", OY, 28))
stage.append(el(f'<div class="col" style="align-items:center"><div class="huge2">{cnt(30000, "n13@dreißigtausend", 0, -0.1)}</div>'
                f'<div class="mono" style="font-size:30px;font-weight:800;color:#2B2D35;margin-top:4px;background:rgba(255,255,255,.92);padding:6px 14px;border-radius:10px">JÜDISCHE MÄNNER IN KONZENTRATIONSLAGERN</div></div>',
                0, 760, A("n13@dreißigtausend", "n14", -0.15) + ' data-sfx="none"', 1080, CENTER))
stage.append(chip_("REISEN IN DEN WESTEN: VERBOTEN", "n16@nicht", "n17", "#B8383C", "marker", ic(I["ban"], 40, "#B8383C", 3)))
stage.append(chip_("„AB SOFORT“ – AUS VERSEHEN ZU FRÜH", "n17@Versehen", "n18", GR, "marker", ic(I["mic"], 40, GR, 3)))
stage.append(chip_("TAUSENDE STRÖMEN ZUR GRENZE", "n18@Tausende", "n19", TQD, "none"))
stage.append(chip_("KURZ VOR MITTERNACHT: DIE MAUER IST OFFEN", "n19@öffnet", "n20", TQD, "success", ic(I["clock"], 40, TQD, 3), OY, 27))
stage.append(el(f'<div class="stamp mono" style="font-size:46px;white-space:nowrap;color:#2B2D35;border-color:#2B2D35">PASST NICHT</div>', 40, OY + 10, A("n21@passt", "n22"), 1000, CENTER))
stage.append(chip_("1990 · WIEDERVEREINIGUNG", "n23@neunzehnhundertneunzig", "n24", TQD, "success", "", OY + 10))
stage.append(chip_("9. NOVEMBER: TAG DES GEDENKENS", "n24@Gedenkens", "end", "#2B2D35", "glass", ic(I["candle"], 42, "#B88A1A", 3), OY + 10, 30, -0.2))

SCENE_JS = r''' // ---- Bühne: Deutschlandkarte + Kalenderblatt ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const M=document.getElementById('mapg');
  const sm=u=>u*u*(3-2*u);
  function kf(arr,tt,n){ const ks=arr.map(k=>({t:TS(k[0],k[1]),v:k.slice(2)})); if(tt<=ks[0].t) return ks[0].v;
    for(let i=0;i<ks.length-1;i++){ const a=ks[i],b=ks[i+1]; if(tt>=a.t&&tt<b.t){ const e=sm((tt-a.t)/Math.max(1e-6,b.t-a.t)); return a.v.map((x,j)=> (n&&j===n)?Math.exp(Math.log(x)+(Math.log(b.v[j])-Math.log(x))*e):x+(b.v[j]-x)*e); } }
    return ks[ks.length-1].v; }
  const c=kf(PAN.cam,t,2); const cx=c[0], cy=c[1], z=c[2], FX=540, FY=c[3];
  M.setAttribute('transform',`translate(${FX},${FY}) scale(${z}) translate(${-cx},${-cy})`);
  const pj=(x,y)=>[FX+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('.geo')){ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px'; }
  const op=(id,v)=>{document.getElementById(id).style.opacity=cl(v,0,1);};
  const lerp=(a,b,u)=>a.map((v,i)=>v+(b[i]-v)*u);
  // Kaiserreich 1918
  const kIn=pr(t,TS('n4',-0.1),0.6), kOut=pr(t,TS('n7@München',-0.3),0.6);
  op('e_kr', kIn*(1-kOut));
  const dem=ease(pr(t,TS('n6@Demokratie',-0.1),0.6));
  const kc=lerp([123,63,228,.30],[25,198,180,.42],dem);
  document.getElementById('f_kr').setAttribute('fill',`rgba(${kc[0]|0},${kc[1]|0},${kc[2]|0},${kc[3]})`);
  // heutiges DE als Staatsfläche (Farbe = Zustand)
  let st=[123,63,228,.30];
  const g1=ease(pr(t,TS('n9@Macht',-0.2),0.6)), g2=ease(pr(t,TS('n10',0),0.6)), u1=ease(pr(t,TS('n20@feiern',0),0.8)), u2=ease(pr(t,TS('n23@Deutschland',0),0.6));
  st=lerp(st,[92,96,107,.50],g1); st=lerp(st,[43,45,53,.66],g2); st=lerp(st,[123,63,228,.30],u1); st=lerp(st,[123,63,228,.46],u2);
  document.getElementById('f_de').setAttribute('fill',`rgba(${st[0]|0},${st[1]|0},${st[2]|0},${st[3].toFixed(3)})`);
  document.getElementById('f_de').setAttribute('stroke', g2>0.5&&u1<0.5?'#2B2D35':'#5B2BB5');
  const deOp=Math.max(1-pr(t,TS('n4',-0.1),0.5), pr(t,TS('n7@München',-0.3),0.6)*(1-pr(t,TS('n14@geteilt',0),0.6)), pr(t,TS('n20@feiern',0),0.7));
  op('e_de', deOp);
  // 1989: BRD/DDR + Grenze
  const dv=pr(t,TS('n14@geteilt',-0.1),0.6)*(1-pr(t,TS('n20@feiern',0.2),0.6));
  op('e_brd', dv); op('e_ddr', pr(t,TS('n14@Ost',-0.3),0.6)*(1-pr(t,TS('n20@feiern',0.2),0.6)));
  const bd=document.getElementById('bdr'); bd.style.strokeDashoffset=1-ease(pr(t,TS('n14@West',-0.1),0.9));
  bd.style.opacity=(t>TS('n14@West',-0.1)?1:0)*(1-pr(t,TS('n20@feiern',0.2),0.6)); bd.setAttribute('stroke-width',(4/z).toFixed(4));
  // 1938: Synagogen-Punkte (schematisch)
  const s0=TS('n11@Synagogen',-0.35), sOut=pr(t,TS('n14',-0.1),0.5), sDim=pr(t,TS('n13',-0.2),0.5);
  const syns=document.querySelectorAll('#e_syn .syn');
  syns.forEach((g,i)=>{ const h=((i*7919)%70)/70; const a=pr(t,s0+h*1.5,0.25);
    const fl=0.85+0.15*Math.sin(t*9+i*1.7);
    g.style.opacity=a*(1-sOut)*(1-0.55*sDim);
    g.querySelector('.sg').setAttribute('r',(26*fl*(0.6+0.4*ease(a))/z).toFixed(3));
    g.querySelector('.sc').setAttribute('r',(6/z).toFixed(3)); });
  // Krone 1918
  const cr=document.getElementById('crown'); const ca=pr(t,TS('n4@Kaiser',-0.35),0.3), cs=pr(t,TS('n4@dankt',0),0.35), cf=pr(t,TS('n5',-0.1),0.5);
  cr.style.opacity=ca*(1-cf); cr.style.transform=`translateY(${60*ease(cf)}px) rotate(${25*ease(cf)}deg) scale(${0.7+0.3*ease(ca)})`;
  document.getElementById('crx').style.transform=`rotate(-24deg) scaleX(${ease(cs)})`;
  // Berlin 1989
  const bo=pr(t,TS('n15@Berlin',0.3),0.5)*(1-pr(t,TS('n20@feiern',0),0.5)); op('e_ber', bo);
  const ww=ease(pr(t,TS('n15@Mauer',-0.3),0.8)); const gap=ease(pr(t,TS('n19@öffnet',0),0.6))*0.11;
  for(const [id,s] of [['wt',-1],['wb',1]]){ const w=document.getElementById(id); w.style.strokeDashoffset=1-ww; w.setAttribute('stroke-width',(13/z).toFixed(4));
    w.setAttribute('transform',`translate(0,${s*gap})`); }
  const P=document.querySelectorAll('#pplw .ppl'); const tq=TS('n18@strömen',-0.2), to=TS('n19@öffnet',0.15);
  const pIn=TS('n16@Osten',-0.1), pOut=pr(t,TS('n20@feiern',-0.1),0.4);
  P.forEach((d,i)=>{ const pp=PAN.ppl[i]; const a=pr(t,pIn+i*0.03,0.3);
    let w=pp.s; const u=ease(pr(t,tq+i*0.02,0.9)); w=lerp(w,pp.q,u);
    const tg=to+i*0.045; const v=pr(t,tg,0.9);
    if(v>0){ const g=[PAN.B[0],PAN.B[1]+((i%5)-2)*0.012]; if(v<0.4){ w=lerp(pp.q,g,ease(v/0.4)); } else { w=lerp(g,pp.w,ease((v-0.4)/0.6)); } }
    const jig=(t<tq&&t>pIn)?Math.sin(t*6+i)*0.006:0;
    const p=pj(w[0]+jig,w[1]);
    d.style.left=p[0]+'px'; d.style.top=p[1]+'px'; d.style.opacity=a*(1-pOut)*(t>TS('n15',0)?1:0);
    d.style.background=v>0.55?'#7B3FE4':'#19C6B4'; });
  // Kalenderblatt
  const k=kf(PAN.kal,t,0); const K_=document.getElementById('kal');
  let yr=''; let yt=-9; for(const [a,s] of PAN.years) if(t>=S[a]) {yr=s; yt=S[a];}
  if(t<S['n4']){ const cyc=['1918','1923','1938','1989']; const ph=Math.floor((t+0.25)/0.55); yr=cyc[((ph%4)+4)%4]; yt=ph*0.55-0.25; }
  const fl=pr(t,yt,0.22); const y=document.getElementById('kaly'); y.textContent=yr;
  y.style.transform=`scaleY(${0.15+0.85*ease(fl)})`; y.style.display=yr?'block':'none';
  const k2=document.getElementById('kal2'); k2.style.display=t>=S['n20']?'flex':'none';
  op('k89', pr(t,TS('n20@Mauerfall',-0.1),0.3)); op('k38', pr(t,TS('n20@Synagogen',-0.1),0.3));
  document.getElementById('k3y').style.opacity=pr(t,TS('n23@neunzehnhundertneunzig',-0.1),0.3);
  const kin=ease(pr(t,-0.6,0.4)), kout=pr(t,END,0.3);
  K_.style.opacity=kin*(1-kout); K_.style.transform=`translate(${k[0]-150}px,${k[1]-160}px) scale(${k[2]})`;
  // Hook: Jahreszahl-Chips nacheinander
  document.querySelectorAll('#y4 .chip').forEach((cE,i)=>{ const a=pr(t,TS('n2@viermal',-0.1+i*0.18),0.25); cE.style.opacity=a; cE.style.transform=`scale(${0.6+0.4*ease(a)})`; });
  // Abdunkeln zum Schluss
  document.querySelector('.mapwrap svg').style.opacity=1-0.45*pr(t,TS('n20@feiern',0.3),0.6);
 }
'''
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
 const top=cl(1-pr(t,END,.3),0,1); ['chap','prog','head'].forEach(id=>document.getElementById(id).style.opacity=top); document.getElementById('headbg').style.opacity=1-pr(t,S['n4']-0.2,0.5); document.getElementById('head').style.opacity=top*(1-pr(t,S['n4']-0.2,0.3));
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
html = html.replace('/*SCENEJS*/', SCENE_JS)
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))
