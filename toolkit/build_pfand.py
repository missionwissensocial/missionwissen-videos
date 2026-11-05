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
HOOK = 'Beim Pfand ist <span style="color:#19C6B4">Deutschland</span> mal Vorbild'
B = [
 ("p1", 0, HOOK, "Beim *Pfand* auf *Plastikflaschen* und *Dosen* ist *Deutschland* mal das *Vorbild.*", "staunt"),
 ("p2", 0, HOOK, "*Österreich* hat dieses Pfand erst *Anfang* *zweitausendfünfundzwanzig* eingeführt.", None),
 ("p3", 0, HOOK, "Wie *viele* *Flaschen* dort *zurückkommen* – und wie viele bei *uns* – zeige ich dir am *Ende.*", None),
 ("p4", 1, "", "Vor dem *Pfand* kamen *leere* *Plastikflaschen* in *Österreich* in den *gelben* *Sack.*", None),
 ("p5", 1, "", "*Viele* landeten aber im *Restmüll* oder in der *Natur.*", None),
 ("p6", 1, "", "Nur etwa *siebzig* von *hundert* *Plastikflaschen* wurden so *gesammelt.*", None),
 ("p7", 2, "", "Jetzt *zahlst* du dort auf fast *jede* *Plastikflasche* und *Dose* *fünfundzwanzig* *Cent* *Pfand.*", None),
 ("p8", 2, "", "*Genauso* *viel* wie bei *uns.*", None),
 ("p9", 2, "", "Bringst du sie *leer* in den *Laden* zurück, bekommst du das *Geld* *wieder.*", None),
 ("p10", 3, "", "Bei *uns* gibt es Pfand auf die meisten Plastikflaschen und Dosen schon seit *zweitausenddrei* – also seit über *zwanzig* *Jahren.*", None),
 ("p11", 4, "", "*Heute* kommen bei uns rund *siebenundneunzig* von *hundert* Flaschen und Dosen *zurück.*", None),
 ("p12", 4, "", "In *Österreich* waren es im ersten Jahr gut *achtzig* von *hundert.*", None),
 ("p13", 4, "", "Ein *guter* *Start* – aber noch *nicht* so viele wie bei *uns.*", None),
 ("p14", 4, "", "*Österreichs* *Ziel* bis *zweitausendsiebenundzwanzig:* *neunzig* von *hundert.*", None),
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

# ================= Bühne: Karte DE/AT -> Kameraflug hinunter in eine österreichische Straße -> zurück zur Karte =================
GEO = json.load(open("geo.json")); L0, B0, KX, KY = GEO["L0"], GEO["B0"], GEO["KX"], GEO["KY"]
def WX(lon): return (lon - L0) * KX
def WY(lat): return (B0 - lat) * KY
TQ = "#19C6B4"; PUR = "#7B3FE4"; RED = "#E5484D"; TQD = "#0E8C80"; PURS = "#5B2BB5"; GR = "#3F434C"; INK = "#2B2D35"
FX0, FY0 = 540, 880
MX, MY = round(WX(11.0), 1), round(WY(50.7), 1)
DEC = (round(WX(10.4), 1), round(WY(51.2), 1))
SX, SY = round(WX(14.3), 1), round(WY(47.5), 1)   # Straßenszene (in Österreich)
ZS = 50.0                                            # Zoom, bei dem 1 Szenen-px = 1 Bildschirm-px
def SC(x, y): return [round(SX + x / ZS, 3), round(SY + y / ZS, 3)]
SL = SC(-270, 0); SH = SC(1050, 0)
cam = [
 ["p1", -0.2, MX, MY, 0.92], ["p3@Ende", 0.2, MX + 6, MY + 4, 0.95],
 ["p4", -0.15, MX + 6, MY + 4, 0.95], ["p4@Plastikflaschen", 0.25, SL[0], SL[1], ZS],
 ["p7", -0.25, SL[0], SL[1], ZS], ["p7@jede", 0.1, SH[0], SH[1], ZS],
 ["p10", -0.3, SH[0], SH[1], ZS], ["p10@Pfand", 0.2, DEC[0], DEC[1] + 20, 1.2],
 ["p10@Jahren", 0.3, DEC[0], DEC[1] + 20, 1.25], ["p11", 0.2, MX, MY, 0.92], ["end", 0, MX, MY, 0.92],
]
def path(d, fill, stroke, cls="ol", extra=""): return f'<path class="{cls}" d="{d}" fill="{fill}" stroke="{stroke}" stroke-linejoin="round" {extra}/>'
other = "".join(path(d, "#FFFFFF", "#9AA0AA") for d in GEO["other"])
# ---- Straßenszene (Szenen-px; Boden bei y=260) ----
def bottle_svg(w=80, cap=TQ, body="rgba(185,232,226,.85)"):
    return (f'<svg viewBox="0 0 80 190" width="{w}" height="{w*190/80:.0f}" style="overflow:visible">'
            f'<rect x="28" y="2" width="24" height="16" rx="4" fill="{cap}" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M30 18 H50 V34 Q70 50 70 78 V176 Q70 186 60 186 H20 Q10 186 10 176 V78 Q10 50 30 34 Z" fill="{body}" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<rect x="10" y="96" width="60" height="40" fill="{PUR}" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M20 60 Q18 120 22 170" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" fill="none" opacity=".8"/></svg>')
def can_svg(w=70):
    return (f'<svg viewBox="0 0 70 130" width="{w}" height="{w*130/70:.0f}" style="overflow:visible">'
            f'<path d="M8 14 Q8 4 18 4 H52 Q62 4 62 14 V116 Q62 126 52 126 H18 Q8 126 8 116 Z" fill="#D5D8DF" stroke="{INK}" stroke-width="3.5"/>'
            f'<rect x="8" y="40" width="54" height="50" fill="{TQ}" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M16 10 H54" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M18 22 V108" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity=".8"/></svg>')
MB = lambda: (f'<rect x="-11" y="-30" width="22" height="7" rx="2" fill="{TQ}" stroke="{INK}" stroke-width="2"/>'
              f'<path d="M-9 -23 H9 V-16 Q16 -10 16 0 V26 Q16 30 12 30 H-12 Q-16 30 -16 26 V0 Q-16 -10 -9 -16 Z" fill="rgba(185,232,226,.9)" stroke="{INK}" stroke-width="2.5"/>'
              f'<rect x="-16" y="2" width="32" height="12" fill="{PUR}"/>')
scene = (
  '<defs><pattern id="mmp" width="50" height="50" patternUnits="userSpaceOnUse"><rect width="50" height="50" fill="#FCFCFD"/>'
  '<path d="M0 0.5H50M0.5 0V50" stroke="rgba(11,11,16,.09)" stroke-width="1"/>'
  + "".join(f'<path d="M0 {k*10+.5}H50M{k*10+.5} 0V50" stroke="rgba(11,11,16,.035)" stroke-width="1"/>' for k in range(1, 5)) + '</pattern></defs>'
  '<rect x="-1800" y="-1200" width="4000" height="2400" fill="url(#mmp)"/>'
  f'<rect x="-1800" y="260" width="4000" height="900" fill="#EEF0F4"/><path d="M-1800 260 H2200" stroke="{INK}" stroke-width="3"/>'
  # gelber Sack
  f'<g id="sack"><path d="M-695 258 Q-730 130 -660 50 L-628 12 Q-600 -6 -572 12 L-540 50 Q-470 130 -505 258 Z" fill="#F2C230" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
  f'<path d="M-620 14 Q-600 -26 -580 14" fill="none" stroke="{INK}" stroke-width="4"/><path d="M-660 120 Q-600 140 -545 118" stroke="#C99A12" stroke-width="3" fill="none"/></g>'
  f'<text x="-600" y="310" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="#9A7A10">GELBER SACK</text>'
  # Restmüll-Tonne
  f'<rect x="-360" y="44" width="160" height="216" rx="10" fill="#8A8F99" stroke="{INK}" stroke-width="4"/>'
  f'<path d="M-320 80 V230 M-280 80 V230 M-240 80 V230" stroke="#6B707A" stroke-width="4"/>'
  f'<g id="binlid"><rect x="-376" y="18" width="192" height="30" rx="8" fill="#6B707A" stroke="{INK}" stroke-width="4"/></g>'
  f'<text x="-280" y="310" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="#5D616B">RESTMÜLL</text>'
  # Natur
  f'<path d="M40 260 V160" stroke="#7A5A3A" stroke-width="12" stroke-linecap="round"/>'
  f'<circle cx="40" cy="120" r="62" fill="#BFE5C8" stroke="#3E8E5A" stroke-width="4"/><circle cx="-5" cy="158" r="38" fill="#BFE5C8" stroke="#3E8E5A" stroke-width="4"/><circle cx="88" cy="158" r="40" fill="#BFE5C8" stroke="#3E8E5A" stroke-width="4"/>'
  + "".join(f'<path d="M{x} 262 l-8 -26 M{x} 262 l0 -32 M{x} 262 l9 -24" stroke="#3E8E5A" stroke-width="4" stroke-linecap="round"/>' for x in (-90, -60, 120, 150))
  + f'<text x="40" y="310" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="#3E8E5A">NATUR</text>'
  # fliegende Flaschen (p5)
  + "".join(f'<g id="fb{i}" style="opacity:0">{MB()}</g>' for i in range(3))
  + f'<text id="x1" x="-280" y="-20" text-anchor="middle" font-family="Inter" font-weight="800" font-size="70" fill="{RED}" style="opacity:0">✕</text>'
  + f'<text id="x2" x="40" y="215" text-anchor="middle" font-family="Inter" font-weight="800" font-size="70" fill="{RED}" style="opacity:0">✕</text>'
  # Supermarkt + Rückgabeautomat
  + f'<rect x="840" y="-150" width="520" height="410" fill="#FCFCFD" stroke="{INK}" stroke-width="4"/>'
  f'<rect x="826" y="-212" width="548" height="70" rx="8" fill="{PUR}" stroke="{INK}" stroke-width="4"/>'
  f'<text x="1100" y="-165" text-anchor="middle" font-family="JBM" font-weight="800" font-size="36" fill="#FFFFFF">SUPERMARKT</text>'
  f'<rect x="870" y="-110" width="300" height="140" fill="#E6F6F4" stroke="{INK}" stroke-width="3"/><path d="M1020 -110 V30" stroke="{INK}" stroke-width="3"/>'
  f'<rect x="1010" y="70" width="0" height="0"/>'
  f'<rect x="1225" y="0" width="130" height="260" rx="10" fill="#E4E6EB" stroke="{INK}" stroke-width="4"/>'
  f'<rect x="1242" y="18" width="96" height="46" rx="6" fill="#0B0B10"/><text id="adisp" x="1290" y="51" text-anchor="middle" font-family="JBM" font-weight="800" font-size="24" fill="{TQ}">0,00 €</text>'
  f'<rect x="1254" y="98" width="72" height="24" rx="12" fill="{INK}"/><rect id="slotglow" x="1250" y="94" width="80" height="32" rx="16" fill="none" stroke="{TQ}" stroke-width="5" style="opacity:0"/>'
  f'<rect x="1262" y="170" width="56" height="10" rx="5" fill="#9AA0AA"/>'
  f'<text x="1290" y="310" text-anchor="middle" font-family="JBM" font-weight="800" font-size="24" fill="#5D616B">RÜCKGABE</text>'
  
)
mapsvg = (f'<svg id="world" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">'
          f'<g id="camg"><g id="mapl">{other}'
          + path(GEO["at"], "#FFFFFF", INK, "ol", 'id="atp"') + path(GEO["de"], "#FFFFFF", INK, "ol", 'id="dep"')
          + f'</g><g id="scn" transform="translate({SX},{SY}) scale({1/ZS})" style="opacity:0">{scene}</g></g></svg>')
stage.append(mapsvg); stage.append('<div id="headbg"></div>')
# --- Hauptdarsteller (Bildschirm-Ebene, Weltkoordinaten -> Projektion) ---
DEb = [352, 470]; DEc = [418, 470]; ATb = [640, 805]; ATc = [690, 805]
hero_kf = {
 "hb": [["p1", -1, *DEb, 1.0, 0, 1, 0], ["p2@Österreich", 0.0, *DEb, 1.0, 0, 1, 0], ["p2@eingeführt", -0.1, *ATb, 1.0, 0, 1, 260],
        ["p4", -0.1, *ATb, 1.0, 0, 1, 0], ["p4@Plastikflaschen", 0.25, *SC(-270, -120), 1.5, 0, 1, 0],
        ["p4@gelben", -0.1, *SC(-270, -120), 1.5, 0, 1, 0], ["p4@Sack", 0.05, *SC(-600, 60), 0.9, 25, 1, 160], ["p4@Sack", 0.4, *SC(-600, 120), 0.6, 25, 0, 0],
        ["p7@Plastikflasche", -0.35, *SC(760, 262), 1.2, 0, 0, 0], ["p7@Plastikflasche", 0.0, *SC(760, 262), 1.2, 0, 1, 0],
        ["p9@leer", 0.0, *SC(760, 262), 1.2, 0, 1, 0], ["p9@Laden", 0.3, *SC(1290, 140), 0.5, -90, 1, 180], ["p9@zurück", 0.05, *SC(1300, 140), 0.4, -90, 0, 0]],
 "hc": [["p1", -1, *DEc, 1.0, 0, 1, 0], ["p2@Österreich", 0.25, *DEc, 1.0, 0, 1, 0], ["p2@eingeführt", 0.15, *ATc, 1.0, 0, 1, 230],
        ["p4", -0.1, *ATc, 1.0, 0, 1, 0], ["p4@Plastikflaschen", 0.0, *ATc, 1.0, 0, 0, 0],
        ["p7@Dose", -0.35, *SC(870, 262), 1.2, 0, 0, 0], ["p7@Dose", 0.0, *SC(870, 262), 1.2, 0, 1, 0],
        ["p9@Laden", 0.1, *SC(870, 262), 1.2, 0, 1, 0], ["p9@zurück", 0.0, *SC(1290, 140), 0.5, -90, 1, 160], ["p9@zurück", 0.35, *SC(1300, 140), 0.4, -90, 0, 0]],
 "hm": [["p9@bekommst", -0.1, *SC(1290, 150), 0.3, 0, 0, 0], ["p9@bekommst", 0.05, *SC(1290, 150), 0.4, 0, 1, 0], ["p9@Geld", 0.3, *SC(820, -260), 1.0, 360, 1, 220],
        ["p10", -0.3, *SC(820, -260), 1.0, 360, 1, 0], ["p10", 0.0, *SC(820, -260), 0.8, 360, 0, 0]],
}
COIN = (f'<svg viewBox="0 0 120 120" width="120" height="120"><circle cx="60" cy="60" r="54" fill="#F2C230" stroke="{INK}" stroke-width="5"/>'
        f'<circle cx="60" cy="60" r="40" fill="none" stroke="#C99A12" stroke-width="4"/><text x="60" y="74" text-anchor="middle" font-family="Unbounded" font-weight="700" font-size="40" fill="{INK}">25</text></svg>')
STICK = f'<div id="stick" class="mono" style="position:absolute;left:50%;top:44%;transform:translate(-50%,-50%) rotate(-8deg);background:#fff;border:3px solid {PUR};color:{PUR};font-weight:800;font-size:22px;padding:2px 8px;border-radius:8px;white-space:nowrap;opacity:0">25 CT</div>'
stage.append(f'<div class="hero" id="hb" style="width:80px;height:190px">{bottle_svg()}{STICK}</div>')
stage.append(f'<div class="hero" id="hc" style="width:70px;height:130px">{can_svg()}</div>')
stage.append(f'<div class="hero" id="hm" style="width:120px;height:120px">{COIN}</div>')
# --- Labels, die an der Karte hängen ---
def glab(lon, lat, inner, i, o, d=0, idd="", sfx="none", wx=None, wy=None):
    ii = f' id="{idd}"' if idd else ""
    x = WX(lon) if wx is None else wx; y = WY(lat) if wy is None else wy
    return (f'<div class="geo" data-x="{x:.1f}" data-y="{y:.1f}"><div class="el"{ii} {A(i, o, d)} data-sfx="{sfx}" style="left:0;top:0;transform-origin:0 0">'
            f'<div style="transform:translate(-50%,-50%)">{inner}</div></div></div>')
def maplab(t, col): return f'<span class="mono lab" style="color:{col};border-color:{col}">{t}</span>'
FLAG_DE = '<span class="flag v"><i style="background:#111"></i><i style="background:#D33A3A"></i><i style="background:#F2C230"></i></span>'
FLAG_AT = '<span class="flag v"><i style="background:#D33A3A"></i><i style="background:#fff"></i><i style="background:#D33A3A"></i></span>'
geo = (glab(10.0, 53.3, maplab("DEUTSCHLAND", GR), "p1", "p4", -0.6)
       + glab(14.6, 46.75, maplab("ÖSTERREICH", GR), "p1", "p4", -0.6)
       + glab(9.6, 50.1, f'<div class="chip mono" style="font-size:34px;font-weight:800;color:#fff;background:{TQD};border-color:{TQD};white-space:nowrap">✓ VORBILD</div>', "p1@Vorbild", "p4", -0.1, "", "success")
       + glab(10.0, 47.15, f'<div class="chip mono" style="font-size:30px;font-weight:800;color:{PURS};border-color:{PURS};background:rgba(255,255,255,.96);white-space:nowrap">PFAND ERST SEIT 2025</div>', "p2@zweitausendfünfundzwanzig", "p4", -0.2, "", "marker")
       + glab(10.4, 51.6, f'<div class="col"><div class="mono" style="font-size:28px;font-weight:800;color:{TQD};letter-spacing:.06em">PFAND IN DEUTSCHLAND</div><div class="huge" id="yr" style="font-size:180px;color:{TQD}">2003</div><div class="mono" id="yr20" style="font-size:34px;font-weight:800;color:#fff;background:{TQD};border-radius:10px;padding:6px 16px;white-space:nowrap;opacity:0">ÜBER 20 JAHRE</div></div>', "p10@zweitausenddrei", "p11", -0.15, "", "glass"))
stage.append(f'<div id="geol">{geo}</div>')
# --- Overlays (höchstens eines gleichzeitig) ---
def chip_(txt, i, o, col=PURS, sfx="marker", y=1150, fs=30, d=0):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 22px;border-color:{col};color:{col};background:rgba(255,255,255,.97);white-space:nowrap">{txt}</div>', 80, y, A(i, o, d) + f' data-sfx="{sfx}"', 920, CENTER)
stage.append(chip_(f'{FLAG_AT}&nbsp;?? von 100&nbsp;&nbsp;<span style="color:#8A8F99">vs.</span>&nbsp;&nbsp;{FLAG_DE}&nbsp;?? von 100&nbsp;&nbsp;<span style="font-size:22px;color:#8A8F99">AM ENDE</span>', "p3@viele", "p4", GR, "glass", 445, 32))
stage.append(chip_(f'{FLAG_AT}&nbsp;ÖSTERREICH · VOR DEM PFAND', "p4@Österreich", "p5", PURS, "marker", 260, 34))
def bot_ic(on): return (f'<svg viewBox="-20 -34 40 68" width="54" height="92">'
                        + MB().replace("rgba(185,232,226,.9)", "rgba(185,232,226,.95)" if on else "#E6E7EB").replace(PUR, PUR if on else "#B4B8C1").replace(f'fill="{TQ}"', f'fill="{TQ if on else "#B4B8C1"}"') + '</svg>')
SEVEN = (f'<div class="col" style="gap:10px"><div class="row" style="gap:16px"><div class="huge num" style="font-size:150px;color:{PURS}">{cnt(70, "p6@siebzig", 0, 0)}</div>'
         f'<div class="mono" style="font-size:40px;font-weight:800;color:{PURS};line-height:1.1">VON<br>100</div></div>'
         f'<div class="row" style="gap:12px">' + "".join(f'<span class="b10" data-k="{k}">{bot_ic(k < 7)}</span>' for k in range(10)) + '</div>'
         f'<div class="mono" style="font-size:26px;font-weight:800;color:#5D616B;white-space:nowrap">PLASTIKFLASCHEN WURDEN GESAMMELT</div></div>')
stage.append(card(SEVEN, 90, 200, 900, 420, "active", A("p6", "p7", -0.05) + ' data-sfx="glass"'))
COINB = COIN.replace('width="120" height="120"', 'width="170" height="170"')
CENT = (f'<div class="row" style="gap:26px">{COINB}'
        f'<div class="col" style="align-items:flex-start"><div class="huge" style="font-size:150px;color:{PURS}">{cnt(25, "p7@fünfundzwanzig", 0, 0)}<span style="font-size:70px;letter-spacing:0"> CENT</span></div>'
        f'<div class="mono" style="font-size:26px;font-weight:800;color:#5D616B">PFAND PRO FLASCHE ODER DOSE</div></div></div>')
stage.append(el(CENT, 80, 230, A("p7@fünfundzwanzig", "p8", -0.15) + ' data-sfx="plop"', 920, CENTER))
stage.append(chip_(f'{FLAG_AT}&nbsp;25 CENT&nbsp;&nbsp;=&nbsp;&nbsp;{FLAG_DE}&nbsp;25 CENT', "p8@Genauso", "p9", TQD, "success", 300, 40))
# --- Auflösung: zwei 10x10-Raster ---
def grid(gid, ziel=False):
    return f'<div class="grid" id="{gid}">' + "".join(f'<i data-i="{k}"></i>' for k in range(100)) + '</div>'
COL_DE = (f'<div class="col" style="gap:8px">{FLAG_DE}<div class="mono" style="font-size:24px;font-weight:800;color:#5D616B">DEUTSCHLAND · HEUTE</div>'
          f'<div class="row" style="gap:10px;align-items:baseline"><div class="huge num" id="nde" style="font-size:150px;color:{TQD}">{cnt(97, "p11@kommen", 0, 0)}</div><div class="mono" style="font-size:30px;font-weight:800;color:{TQD}">VON 100</div></div>'
          f'{grid("gde")}<div class="mono" style="font-size:22px;font-weight:800;color:#5D616B;margin-top:6px">KOMMEN ZURÜCK</div></div>')
COL_AT = (f'<div class="col" style="gap:8px">{FLAG_AT}<div class="mono" style="font-size:24px;font-weight:800;color:#5D616B">ÖSTERREICH · 1. JAHR</div>'
          f'<div class="row" style="gap:10px;align-items:baseline"><div class="huge num" id="nat" style="font-size:140px;color:{PURS}">{cnt(81.5, "p12@waren", 1, 0)}</div><div class="mono" style="font-size:30px;font-weight:800;color:{PURS};white-space:nowrap">VON 100</div></div>'
          f'{grid("gat", True)}<div class="mono" style="font-size:22px;font-weight:800;color:#5D616B;margin-top:6px">KAMEN ZURÜCK (2025)</div></div>')
stage.append(el(COL_DE, 40, 330, A("p11", "end", 0.0) + ' data-sfx="glass"', 500, CENTER))
stage.append(el(COL_AT, 540, 330, A("p12", "end", -0.1) + ' data-sfx="glass"', 500, CENTER))
def rchip(txt, col, i, o, d, sfx, dash=False):
    return el(f'<div class="chip mono" style="font-size:32px;font-weight:800;color:{col};border-color:{col};background:rgba(255,255,255,.97);white-space:nowrap;{"border-style:dashed" if dash else ""}">{txt}</div>', 80, 1165, A(i, o, d) + f' data-sfx="{sfx}"', 920, CENTER)
stage.append(rchip("✓ GUTER START", TQD, "p13@guter", "p13@nicht", -0.1, "success"))
stage.append(rchip(f"{FLAG_AT}&nbsp;NOCH NICHT SO VIELE WIE BEI UNS", GR, "p13@nicht", "p14", -0.1, "marker"))
stage.append(rchip(f"{FLAG_AT}&nbsp;ZIEL 2027: 90 VON 100", PURS, "p14@Ziel", "end", -0.05, "marker", True))
# dezente Hinweise
stage.append(el('<div class="note mono">SZENE SCHEMATISCH</div>', 40, 1252, A("p4@Plastikflaschen", "p10@Pfand", 0.3) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">QUELLEN: UMWELTBUNDESAMT 2026 (DE: 96–99 %, JE NACH QUELLE) · EWP RECYCLING PFAND ÖSTERREICH (2025: 81,5 %)</div>', 40, 1252, A("p11", "end", 0.2) + ' data-sfx="none"'))
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
  const sA=pr(z,7,14); const ML=document.getElementById('mapl');
  const dim=1-0.82*pr(t,TS('p11',-0.1),0.5);
  ML.style.opacity=(1-pr(z,28,10))*dim; ML.style.display=z>40?'none':'';
  const SCN=document.getElementById('scn'); SCN.style.opacity=sA; SCN.style.display=sA<0.005?'none':'';
  // Länderflächen
  const deOn=Math.max(pr(t,TS('p1@Vorbild',-0.1),0.4)*(1-pr(t,TS('p4',0),0.4)), pr(t,TS('p10@zweitausenddrei',-0.2),0.5)*(1-pr(t,TS('p11',0),0.4)));
  const pulse=0.5+0.5*Math.sin(t*2*Math.PI/1.2);
  document.getElementById('dep').setAttribute('fill',`rgba(25,198,180,${(0.10+0.32*deOn+0.08*deOn*pulse).toFixed(3)})`);
  const atOn=pr(t,TS('p2@zweitausendfünfundzwanzig',-0.2),0.4)*(1-pr(t,TS('p4',0),0.4));
  document.getElementById('atp').setAttribute('fill',`rgba(123,63,228,${(0.05+0.25*atOn).toFixed(3)})`);
  // Hauptdarsteller
  const bo2=x=>1+2.70158*Math.pow(x-1,3)+1.70158*Math.pow(x-1,2);
  for(const id of ['hb','hc','hm']){
    const H=document.getElementById(id); const KF=PAN.hero[id].map(k=>[TS(k[0],k[1]),...k.slice(2)]);
    let s=KF[0];
    if(t<KF[0][0]) s=KF[0]; else if(t>=KF[KF.length-1][0]) s=KF[KF.length-1];
    else for(let i=0;i<KF.length-1;i++){ const a=KF[i],q=KF[i+1]; if(t>=a[0]&&t<q[0]){ const u=sm((t-a[0])/Math.max(1e-6,q[0]-a[0]));
       s=[t,a[1]+(q[1]-a[1])*u,a[2]+(q[2]-a[2])*u,a[3]+(q[3]-a[3])*u,a[4]+(q[4]-a[4])*u,a[5]+(q[5]-a[5])*u]; s.arc=4*u*(1-u)*q[6]; break; } }
    const [px,py]=pj(s[1],s[2]); const arc=s.arc||0;
    const W=H.offsetWidth, Hh=H.offsetHeight;
    const bob=(id==='hm')?0:4*Math.sin(t*2*Math.PI/1.1+(id==='hc'?1.3:0));
    const sq=(arc>0)?1:1;
    H.style.transform=`translate(${(px-W/2).toFixed(1)}px,${(py-Hh-arc+bob).toFixed(1)}px) rotate(${s[4].toFixed(1)}deg) scale(${s[3].toFixed(3)})`;
    H.style.opacity=cl(s[5],0,1)*(1-pr(t,END,0.3));
  }
  document.getElementById('stick').style.opacity=pr(t,TS('p7@fünfundzwanzig',-0.1),0.25);
  // p5: Flaschen landen im Restmüll und in der Natur
  const fb=[[-480,-420,-280,20,0,0],[-260,-470,-60,246,0,90],[-40,-430,130,244,0,-78]];
  fb.forEach((f,i)=>{ const t0=TS(i===0?'p5@Restmüll':'p5@Natur',-0.45+(i===2?0.25:0)); const u=pr(t,t0,0.5); const e=document.getElementById('fb'+i);
    const x=f[0]+(f[2]-f[0])*u, y=f[1]+(f[3]-f[1])*u*u, r=f[5]*ease(u)+u*200*(i===0?1:0.4);
    const vis=t>t0&&t<TS('p7',0)&&!(i===0&&u>=1);
    e.setAttribute('transform',`translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${(i===0?r:f[5]*ease(u)).toFixed(1)}) scale(2.6)`); e.style.opacity=vis?1:0; });
  const lidHit=TS('p5@Restmüll',0.05); const lh=t>lidHit&&t<lidHit+0.6?Math.exp(-(t-lidHit)*8)*Math.sin((t-lidHit)*40)*10:0;
  document.getElementById('binlid').setAttribute('transform',`rotate(${lh.toFixed(2)} -280 30)`);
  document.getElementById('x1').style.opacity=pr(t,TS('p5@Restmüll',0.1),0.15)*(1-pr(t,TS('p6',0),0.2));
  document.getElementById('x2').style.opacity=pr(t,TS('p5@Natur',0.15),0.15)*(1-pr(t,TS('p6',0),0.2));
  const sk=t>TS('p4@Sack',0.0)&&t<TS('p4@Sack',0.6)?Math.exp(-(t-TS('p4@Sack',0))*7)*Math.sin((t-TS('p4@Sack',0))*30)*3:0;
  document.getElementById('sack').setAttribute('transform',`rotate(${sk.toFixed(2)} -600 258)`);
  // 7 von 10 Flaschen: nacheinander einblenden
  document.querySelectorAll('.b10').forEach(b=>{ const k=+b.dataset.k; const u=pr(t,TS('p6@siebzig',-0.1)+k*0.08,0.2); b.style.opacity=u; b.style.transform=`translateY(${(20*(1-ease(u))).toFixed(1)}px)`; });
  // Automat
  const g=pr(t,TS('p9@Laden',-0.1),0.2)*(1-pr(t,TS('p9@bekommst',0.1),0.3)); document.getElementById('slotglow').style.opacity=g*(0.6+0.4*Math.sin(t*14));
  document.getElementById('adisp').textContent=t>TS('p9@bekommst',0)?(t>TS('p9@zurück',0.1)?'+0,50 €':'+0,25 €'):(t>TS('p9@zurück',-0.3)?'+0,25 €':'0,00 €');
  // Jahreszähler
  document.getElementById('yr').textContent=2003+Math.round(23*ease(pr(t,TS('p10@zweitausenddrei',0.35),1.5)));
  document.getElementById('yr20').style.opacity=pr(t,TS('p10@zwanzig',-0.1),0.25);
  // Raster der Auflösung
  for(const [gid,nid,col] of [['gde','nde','#19C6B4'],['gat','nat','#7B3FE4']]){
    const v=parseFloat(document.getElementById(nid).textContent.replace(',','.'))||0;
    const zl=gid==='gat'?pr(t,TS('p14@neunzig',-0.2),0.4):0;
    document.querySelectorAll('#'+gid+' i').forEach(d=>{ const k=+d.dataset.i; const on=k<Math.floor(v+0.001), half=(k===Math.floor(v)&&v%1>0.2);
      d.style.background=on?col:(half?`linear-gradient(90deg,${col} 50%,#E6E7EB 50%)`:'#E6E7EB');
      d.style.outline=(!on&&k<90&&zl>0)?`3px dashed rgba(91,43,181,${zl.toFixed(2)})`:'none'; d.style.outlineOffset='-3px'; });
  }
  // Labels an der Karte
  document.getElementById('geol').style.opacity=(1-pr(z,2.2,1.5))*(1-pr(t,END,0.3));
  for(const gg of document.querySelectorAll('.geo')){ const [sx,sy]=pj(+gg.dataset.x,+gg.dataset.y); gg.style.left=sx+'px'; gg.style.top=sy+'px'; }
  // Szene im Abspann ausblenden
  document.getElementById('world').style.opacity=1-pr(t,END,0.35);
  // Roboter (Hook rechts, CTA wie Template)
  const RB=document.getElementById('robot'); RB.style.left=(t>=END?40:760)+'px'; RB.style.top=(t>=END?790:520)+'px';
  document.getElementById('headbg').style.opacity=1-pr(t,TS('p4',-0.15),0.3);
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
