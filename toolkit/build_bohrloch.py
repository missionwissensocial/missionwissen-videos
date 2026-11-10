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
B = [
 ("s1", 0, HOOK, "Das *tiefste* *Loch* der *Welt* ist über *zwölf* *Kilometer* tief.", "staunt"),
 ("s2", 0, HOOK, "Und es ist nur so *breit* wie ein *Teller.*", None),
 ("s3", 1, "", "Warum ging es *nicht* *tiefer?*", None),
 ("s4", 1, "", "Und wie *winzig* das Loch für die *ganze* *Erde* ist, zeige ich dir am *Ende.*", None),
 ("s5", 2, "", "*1970* beginnen *sowjetische* *Forscher* ganz im *Norden* *Russlands* zu bohren, auf der *Halbinsel* *Kola.*", None),
 ("s6", 2, "", "Sie wollen wissen, wie die *Erde* *tief* *unten* aussieht.", None),
 ("s7", 3, "", "Ein *Bohrkopf* frisst sich durch *uraltes* *Gestein.*", None),
 ("s8", 3, "", "Nach fast *zwanzig* *Jahren* ist er *zwölf* *Kilometer* tief.", None),
 ("s9", 4, "", "Doch dort unten ist es *180* *Grad* *heiß,* fast *doppelt* so heiß wie *erwartet.*", None),
 ("s10", 4, "", "*Hitze* und *Druck* machen das Gestein *zäh* wie *Knete.*", None),
 ("s11", 4, "", "Es *drückt* ins *Loch* und *klemmt* den *Bohrer* ein.", None),
 ("s12", 4, "", "*Tiefer* schaffen sie es *nie.*", None),
 ("s13", 5, "", "Wäre die *Erde* so groß wie ein *Fußball,* wäre das Loch nur so *tief,* wie *zwei* *Blatt* *Papier* dick sind.", None),
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
PURS = "#5B2BB5"; GR = "#3F434C"; TQD = "#0E8C80"; WAT = "#4BA3D9"; HOT = "#E5484D"
STOP = 300; STH = 980          # Bühne (lokal 0..980)
SC = 0.25                       # px pro Meter (Weltkoordinaten Querschnitt)
DM = 12262; DY = DM * SC        # 3065.5
W0, W1 = -6000, 6000            # Weltbreite

# ---------- Erd-Querschnitt (Welt) ----------
def wavy(y0, amp, seed, step=120):
    rr = _r.Random(seed); pts = []
    ph = [rr.uniform(0, 6.28) for _ in range(3)]
    for x in range(W0, W1 + step, step):
        y = y0 + amp * (0.6 * math.sin(x / 900 + ph[0]) + 0.3 * math.sin(x / 330 + ph[1]) + 0.15 * math.sin(x / 140 + ph[2]))
        pts.append((x, y))
    return pts
LAY = [  # (Oberkante m, Farbe, Muster)
    (0,    "#EADFC8", "sed"),
    (1500, "#DCCBAA", "lava"),
    (4500, "#CDB894", "lava2"),
    (6842, "#C9B6B4", "gneis"),
    (9500, "#BDA6A6", "gneis2"),
]
bounds = [wavy(m * SC, 0 if m == 0 else 26, 3 + k) for k, (m, c, p) in enumerate(LAY)] + [[(x, 3900) for x in range(W0, W1 + 120, 120)]]
def band(top, bot):
    return "M" + "L".join(f"{x:.0f} {y:.1f}" for x, y in top) + "L" + "L".join(f"{x:.0f} {y:.1f}" for x, y in reversed(bot)) + "Z"
pats = '''<pattern id="p_sed" width="60" height="22" patternUnits="userSpaceOnUse"><path d="M0 11h26M34 4h20M8 18h14" stroke="#B9A57E" stroke-width="2.2" stroke-linecap="round"/></pattern>
<pattern id="p_lava" width="44" height="44" patternUnits="userSpaceOnUse"><circle cx="10" cy="12" r="3.2" fill="#B49A72"/><circle cx="32" cy="30" r="2.4" fill="#B49A72"/><path d="M26 8l6 4" stroke="#A58B63" stroke-width="2"/></pattern>
<pattern id="p_lava2" width="56" height="40" patternUnits="userSpaceOnUse"><path d="M4 30l10-12 9 8 12-14 14 16" stroke="#A88E68" stroke-width="2.2" fill="none" stroke-linejoin="round"/></pattern>
<pattern id="p_gneis" width="140" height="46" patternUnits="userSpaceOnUse"><path d="M0 14q35-14 70 0t70 0M0 34q35-12 70 0t70 0" stroke="#A48C8C" stroke-width="3" fill="none"/></pattern>
<pattern id="p_gneis2" width="120" height="40" patternUnits="userSpaceOnUse"><path d="M0 12q30 12 60 0t60 0M0 30q30 10 60 0t60 0" stroke="#977D7F" stroke-width="3.2" fill="none"/><circle cx="40" cy="22" r="3" fill="#8E7476"/></pattern>
<linearGradient id="g_heat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E5484D" stop-opacity="0"/><stop offset="0.55" stop-color="#F08A3C" stop-opacity="0.35"/><stop offset="1" stop-color="#E5484D" stop-opacity="0.75"/></linearGradient>
<linearGradient id="g_fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FCFCFD" stop-opacity="0"/><stop offset="0.04" stop-color="#FCFCFD" stop-opacity="0.93"/><stop offset="1" stop-color="#FCFCFD" stop-opacity="0.97"/></linearGradient>
<pattern id="p_fogq" width="420" height="380" patternUnits="userSpaceOnUse"><text x="60" y="160" font-family="Unbounded" font-weight="600" font-size="150" fill="#7B3FE4" opacity=".16">?</text><text x="270" y="350" font-family="Unbounded" font-weight="600" font-size="110" fill="#7B3FE4" opacity=".12">?</text></pattern>'''
bands = ""
for k, (m, col, p) in enumerate(LAY):
    d = band(bounds[k], bounds[k + 1])
    bands += f'<path d="{d}" fill="{col}"/><path d="{d}" fill="url(#p_{p})" opacity=".8"/>'
for k in range(1, len(LAY)):
    bands += f'<path d="M' + "L".join(f"{x:.0f} {y:.1f}" for x, y in bounds[k]) + f'" fill="none" stroke="#6E5E4E" stroke-width="3" vector-effect="non-scaling-stroke" opacity=".55"/>'
# Oberfläche: Tundra-Hügel + Schnee
surf = wavy(0, 0, 1)
hill = "M" + f"{W0} 0" + "".join(f"L{x} {-14 - 10 * math.sin(x / 260) - 6 * math.sin(x / 90):.1f}" for x in range(W0, W1 + 60, 60)) + f"L{W1} 0Z"
bands += f'<path d="{hill}" fill="#F4F6F8" stroke="#2B2D35" stroke-width="2.4" vector-effect="non-scaling-stroke"/>'
# Everest (umgedreht, gestrichelt) – Vergleich
EVX = -760; EVD = 8849 * SC
ev_d = f"M{EVX-760} 0L{EVX-420} {EVD*0.35:.0f}L{EVX-300} {EVD*0.42:.0f}L{EVX-150} {EVD*0.78:.0f}L{EVX-60} {EVD*0.86:.0f}L{EVX} {EVD:.0f}L{EVX+90} {EVD*0.8:.0f}L{EVX+230} {EVD*0.6:.0f}L{EVX+330} {EVD*0.52:.0f}L{EVX+760} 0Z"
everest = f'<g id="ev" style="opacity:0"><path d="{ev_d}" fill="rgba(123,63,228,.12)" stroke="{PUR}" stroke-width="5" stroke-dasharray="14 10" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></g>'
# Maßlinie (Hook)
ruler = (f'<g id="ruler"><path d="M-560 0V{DY:.1f}" stroke="{PUR}" stroke-width="4" vector-effect="non-scaling-stroke"/>'
         f'<path d="M-610 0H-510M-610 {DY:.1f}H-510" stroke="{PUR}" stroke-width="4" vector-effect="non-scaling-stroke"/>'
         + "".join(f'<path d="M-580 {k*1000*SC:.0f}H-540" stroke="{PUR}" stroke-width="2.5" vector-effect="non-scaling-stroke"/>' for k in range(1, 13)) + '</g>')
xs_svg = (f'<svg width="1080" height="{STH}" style="position:absolute;left:0;top:0;overflow:hidden"><defs>{pats}</defs><g id="xsg">{bands}'
          f'<rect id="heat" x="{W0}" y="{1500*SC*1.2:.0f}" width="{W1-W0}" height="{3900-1500*SC*1.2:.0f}" fill="url(#g_heat)" opacity="0"/>'
          f'{everest}{ruler}'
          f'<rect id="hole" x="-10" y="0" width="20" height="10" fill="#1E1F25"/>'
          f'<rect id="pipe" x="-3" y="-60" width="6" height="10" fill="#8A8F99"/>'
          f'<g id="fog"><rect id="fogr" x="{W0}" y="0" width="{W1-W0}" height="4200" fill="url(#g_fog)"/><rect id="fogq" x="{W0}" y="0" width="{W1-W0}" height="4200" fill="url(#p_fogq)"/></g>'
          '</g></svg>')

# ---------- Bohrturm (eigene schlichte Zeichnung, im Weltraum verankert) ----------
lat = "".join(f'<path d="M{48+k*5} {300-k*58}L{152-k*5} {300-(k+1)*58}M{152-k*5} {300-k*58}L{48+(k+1)*5} {300-(k+1)*58}" stroke="#2B2D35" stroke-width="3"/>' for k in range(5))
rig_svg = ('<svg width="200" height="330" viewBox="0 0 200 330" style="position:absolute;left:-100px;top:-318px;overflow:visible">'
           '<path d="M100 0L100 -14" stroke="#2B2D35" stroke-width="4"/><circle cx="100" cy="-20" r="7" fill="#7B3FE4"/>'
           f'<path d="M48 300L84 12H116L152 300" fill="none" stroke="#2B2D35" stroke-width="6" stroke-linejoin="round"/>{lat}'
           '<rect x="78" y="0" width="44" height="16" rx="3" fill="#7B3FE4" stroke="#2B2D35" stroke-width="3"/>'
           '<rect x="-60" y="248" width="110" height="64" rx="6" fill="#ECEEF3" stroke="#2B2D35" stroke-width="4"/><path d="M-50 270h30M-50 286h30" stroke="#2B2D35" stroke-width="3"/>'
           '<rect x="150" y="262" width="80" height="50" rx="6" fill="#DCDFE6" stroke="#2B2D35" stroke-width="4"/>'
           '<path d="M-80 314H280" stroke="#2B2D35" stroke-width="5" stroke-linecap="round"/></svg>')
def wgeo(wx, wy, inner, gid="", zs=None, smax=2.0, smin=0.0):
    idd = f' id="{gid}"' if gid else ""
    z_ = f' data-zs="{zs}" data-smax="{smax}" data-smin="{smin}"' if zs else ""
    return f'<div class="xg"{idd} data-x="{wx}" data-y="{wy}"{z_}>{inner}</div>'
def wlab(wx, wy, text, gid, col=PURS, right=False):
    tr = "translate(-100%,-50%)" if right else "translate(0,-50%)"
    return wgeo(wx, wy, f'<div class="mono lab" style="position:absolute;left:0;top:0;transform:{tr};color:{col};border-color:{col}">{text}</div>', gid)
# Bohrkopf (Hauptdarsteller, Bildschirmgröße)
teeth = "".join(f'<path class="tooth" d="M{x} 40l7 12 7-12" fill="#5D616B" stroke="#2B2D35" stroke-width="2"/>' for x in range(-8, 112, 16))
bit_svg = ('<svg width="110" height="150" viewBox="0 0 110 150" style="position:absolute;left:-55px;top:-128px;overflow:visible">'
           '<defs><clipPath id="bitc"><path d="M10 52H100L80 112Q55 132 30 112Z"/></clipPath>'
           '<linearGradient id="bitg" x1="0" x2="1"><stop offset="0" stop-color="#6E7480"/><stop offset=".45" stop-color="#D9DCE3"/><stop offset="1" stop-color="#5D616B"/></linearGradient></defs>'
           '<rect x="44" y="-200" width="22" height="210" fill="url(#bitg)" stroke="#2B2D35" stroke-width="2.5"/>'
           '<rect x="22" y="8" width="66" height="44" rx="6" fill="url(#bitg)" stroke="#2B2D35" stroke-width="3"/>'
           '<path d="M10 52H100L80 112Q55 132 30 112Z" fill="url(#bitg)" stroke="#2B2D35" stroke-width="3"/>'
           f'<g clip-path="url(#bitc)"><g id="bitstr">' + "".join(f'<path d="M{x} 50l-26 70" stroke="#2B2D35" stroke-width="5" opacity=".55"/>' for x in range(-60, 200, 20)) + '</g></g>'
           '<g id="bitteeth">' + "".join(f'<path d="M{x} 104l7 13 7-13Z" fill="#7B3FE4" stroke="#2B2D35" stroke-width="2"/>' for x in (26, 41, 56, 71)) + '</g></svg>')
debris = "".join(f'<div class="deb" style="opacity:0"></div>' for _ in range(16))
bit = (f'<div id="bitw" class="xs-screen"><div id="glow"></div>{debris}'
       f'<div id="blobL" class="blob"><svg width="140" height="120" viewBox="0 0 140 120"><path d="M0 10Q70 -6 118 40Q140 62 112 86Q66 128 0 112Z" fill="#B88F8A" stroke="#2B2D35" stroke-width="4"/><path d="M14 40q30-8 56 6M10 74q34 4 70-6" stroke="#8E6C68" stroke-width="4" fill="none"/></svg></div>'
       f'<div id="blobR" class="blob"><svg width="140" height="120" viewBox="0 0 140 120"><path d="M140 10Q70 -6 22 40Q0 62 28 86Q74 128 140 112Z" fill="#B88F8A" stroke="#2B2D35" stroke-width="4"/><path d="M126 40q-30-8-56 6M130 74q-34 4-70-6" stroke="#8E6C68" stroke-width="4" fill="none"/></svg></div>'
       f'<div id="bitb">{bit_svg}</div>'
       + "".join(f'<div class="parr" data-k="{k}"><svg width="90" height="44" viewBox="0 0 90 44"><path d="M4 22H66" stroke="{HOT}" stroke-width="9" stroke-linecap="round"/><path d="M56 6L86 22L56 38Z" fill="{HOT}"/></svg></div>' for k in range(4))
       + f'<div id="qbit"><div class="qb">?</div></div><div id="stuck" class="mono">✕</div></div>')
xs_ov = (wgeo(0, 0, f'<div id="rig" class="pop">{rig_svg}</div>', "rigw", 1.0, 1.6, 0.35)
         + wlab(70, 4500 * SC * 0.5 + 60, "VULKAN- UND<br>SEDIMENTGESTEIN", "lab1", "#6E5E4E", False)
         + wlab(70, (6842 + 1200) * SC, "GRANIT UND GNEIS", "lab2", "#6E4E50", False)
         + wlab(EVX + 90, EVD - 70, "MOUNT EVEREST<br>8.849 M", "labev", PUR)
         + wlab(0, -150, "BOHRLOCH SG-3", "labhole", PURS))
note = el('<div class="note mono">QUERSCHNITT SCHEMATISCH · NICHT MASSSTÄBLICH IN DER BREITE</div>', 18, STH - 46, A("s1", "s13", -1) + ' data-sfx="none"')
stage.append(f'<div class="el" id="xswrap" data-in="s1" data-d="-1" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px">'
             f'<div class="xsbg">{xs_svg}</div>{xs_ov}{bit}{note}</div>')

# ---------- Karte Nordeuropa ----------
GEO = json.load(open("geo.json")); K = GEO["K"]; CXF = GEO["CX"]
def WX(lon): return (lon + 180) * K * CXF
def WY(lat): return (90 - lat) * K
KLAT, KLON = 69.396, 30.61
KX, KY = WX(KLON), WY(KLAT)
land = f'<path d="{GEO["land"]}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
de = f'<path id="mde" d="{GEO["de"]}" fill="rgba(25,198,180,.22)" stroke="{TQD}" stroke-width="2" vector-effect="non-scaling-stroke"/>'
ru = f'<path id="mru" d="{GEO["ru"]}" fill="rgba(123,63,228,.10)" stroke="none"/>'
cty = f'<path d="{GEO["cty"]}" fill="none" stroke="#C3C7CF" stroke-width="1" stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/>'
map_svg = f'<svg width="1080" height="{STH}" style="position:absolute;left:0;top:0;overflow:hidden"><g id="mapg">{land}{ru}{de}{cty}</g></svg>'
def mlab(lat, lon, text, i, o, col=PUR, pin=True, dx=0, dy=0, sfx="marker", lid=""):
    p = f'<span class="pin" style="background:{col}"></span>' if pin else ""
    idd = f' id="{lid}"' if lid else ""
    return (f'<div class="geo" data-x="{WX(lon):.3f}" data-y="{WY(lat):.3f}"><div class="el mk"{idd} {A(i, o)} data-sfx="{sfx}" style="left:{(-11 if pin else -70) + dx}px;top:{-14 + dy}px;gap:8px">{p}'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
map_ov = (mlab(51.0, 10.2, "DEUTSCHLAND", "s5", "s6", TQD, False, -40, 0, "none")
          + mlab(60.5, 50.0, "RUSSLAND", "s5@Russlands", "s6", PURS, False, -40, 0, "marker")
          + mlab(KLAT, KLON, "HALBINSEL KOLA", "s5@Halbinsel", "s6", PURS, True, 0, -10, "marker"))
stage.append(f'<div class="el mapwrap" id="mapw" data-in="s5" data-d="-0.35" data-out="s6@wollen" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px">{map_svg}{map_ov}'
             + el('<div class="note mono">KARTE: NATURAL EARTH</div>', 18, STH - 46, A("s5", "s6", -0.3) + ' data-sfx="none"') + '</div>')

# ---------- Erde -> Fußball (Auflösung) ----------
ER = 300; ECX, ECY = 540, 440
pent = lambda cx, cy, r, rot: "M" + "L".join(f"{cx + r*math.cos(math.radians(rot + 72*k - 90)):.1f} {cy + r*math.sin(math.radians(rot + 72*k - 90)):.1f}" for k in range(5)) + "Z"
ball_p = pent(0, 0, 70, 0) + "".join(pent(205*math.cos(math.radians(72*k - 90 + 36)), 205*math.sin(math.radians(72*k - 90 + 36)), 74, 36) for k in range(5))
seams = "".join(f'<path d="M{70*math.cos(math.radians(72*k-90+36)):.1f} {70*math.sin(math.radians(72*k-90+36)):.1f}L{(205-74)*math.cos(math.radians(72*k-90+36)):.1f} {(205-74)*math.sin(math.radians(72*k-90+36)):.1f}" stroke="#2B2D35" stroke-width="3"/>' for k in range(5))
earth_svg = (f'<svg width="1080" height="{STH}" style="position:absolute;left:0;top:0;overflow:visible"><defs>'
             '<radialGradient id="g_man" cx=".5" cy=".5" r=".5"><stop offset=".5" stop-color="#F4B860"/><stop offset="1" stop-color="#E9894A"/></radialGradient>'
             '<radialGradient id="g_core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF3C4"/><stop offset="1" stop-color="#F7C948"/></radialGradient>'
             '<radialGradient id="g_ball" cx=".38" cy=".32" r=".75"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".7" stop-color="#EEF0F4"/><stop offset="1" stop-color="#C9CDD6"/></radialGradient>'
             f'<clipPath id="bclip"><circle cx="0" cy="0" r="{ER}"/></clipPath></defs>'
             f'<g id="earth" transform="translate({ECX} {ECY})"><circle r="{ER}" fill="url(#g_man)"/><circle r="{ER*0.55:.0f}" fill="#F08A3C" opacity=".55"/>'
             f'<circle r="{ER*0.42:.0f}" fill="url(#g_core)"/><circle r="{ER*0.19:.0f}" fill="#FFF8DE" stroke="#E0B23A" stroke-width="3"/>'
             f'<circle r="{ER-3}" fill="none" stroke="#6E5E4E" stroke-width="7"/><circle r="{ER}" fill="none" stroke="#2B2D35" stroke-width="3"/>'
             f'<text x="0" y="{-ER*0.70:.0f}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="#7A4A1E">MANTEL</text>'
             f'<text x="0" y="{-ER*0.22:.0f}" text-anchor="middle" font-family="JBM" font-weight="800" font-size="26" fill="#8A6A12">KERN</text></g>'
             f'<g id="ball" transform="translate({ECX} {ECY})" style="opacity:0"><circle r="{ER}" fill="url(#g_ball)"/>'
             f'<g clip-path="url(#bclip)"><path d="{ball_p}" fill="#2B2D35"/>{seams}</g><circle r="{ER}" fill="none" stroke="#2B2D35" stroke-width="4"/>'
             f'<path d="M-200 -170Q-150 -235 -60 -262" stroke="#fff" stroke-width="14" stroke-linecap="round" fill="none" opacity=".7"/></g>'
             f'<g id="emark" transform="translate({ECX} {ECY-ER})"><path d="M0 -6V-70" stroke="{HOT}" stroke-width="5" stroke-linecap="round"/><path d="M-14 -24L0 -4L14 -24" fill="none" stroke="{HOT}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></g>'
             '</svg>')
lens = ('<div id="lens"><svg width="300" height="300" viewBox="0 0 300 300"><defs><clipPath id="lc"><circle cx="150" cy="150" r="140"/></clipPath></defs>'
        '<g clip-path="url(#lc)"><rect width="300" height="300" fill="#F7F8FA"/><path d="M-20 170Q150 140 320 170V320H-20Z" fill="#E6E8EE" stroke="#2B2D35" stroke-width="4"/>'
        f'<path d="M140 156.6h20" stroke="{HOT}" stroke-width="2.5"/><circle cx="150" cy="157" r="22" fill="none" stroke="{HOT}" stroke-width="4" stroke-dasharray="6 5"/></g>'
        '<circle cx="150" cy="150" r="140" fill="none" stroke="#2B2D35" stroke-width="8"/></svg>'
        f'<div class="mono" id="lenst" style="position:absolute;left:-20px;top:-50px;width:340px;text-align:center;font-size:24px;font-weight:800;color:{HOT};background:rgba(255,255,255,.95);border:2.5px solid {HOT};border-radius:8px;padding:4px 0">KAUM ZU SEHEN: DAS LOCH</div></div>')
stage.append(f'<div class="el" id="earthw" data-in="s13" data-d="0.2" data-out="end" data-sfx="none" style="left:0;top:{STOP}px;width:1080px;height:{STH}px">{earth_svg}'
             f'<div id="lensw" style="position:absolute;left:{ECX+120}px;top:{ECY-ER-90}px;width:0;height:0">{lens}</div></div>')

# ---------- Overlays (max. eins gleichzeitig) ----------
OY = 1150
def chip_(txt, i, o, col=PURS, sfx="marker", icon="", y=OY, fs=30, d=0, bg="rgba(255,255,255,.97)"):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;gap:12px;padding:12px 20px;border-color:{col};color:{col};background:{bg};font-weight:700">{icon}{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
I.update(globe2='<circle cx="24" cy="24" r="18"/><path d="M6 24h36M24 6c-7 8-7 28 0 36M24 6c7 8 7 28 0 36"/>',
         therm='<path d="M20 30V9a4 4 0 0 1 8 0v21a8 8 0 1 1-8 0z"/><path d="M24 14v20"/>',
         flag='<path d="M10 42V6M10 8h24l-5 7 5 7H10"/>')
# Hook: große Tiefe ab Frame 0
stage.append(el(f'<div class="col" style="align-items:flex-start"><div class="mono" style="font-size:30px;font-weight:800;color:{PURS};background:rgba(255,255,255,.9);padding:2px 10px;border-radius:8px">ÜBER</div>'
                f'<div class="huge2" style="color:{PURS};font-size:140px">12 KM</div><div class="mono" style="font-size:28px;font-weight:800;color:{PURS};background:rgba(255,255,255,.9);padding:2px 10px;border-radius:8px">SENKRECHT IN DIE ERDE</div></div>',
                600, 720, A("s1", "s2@breit", -1) + ' data-sfx="none"', 480))
# s2: Teller-Vergleich (Draufsicht)
plate = ('<svg width="420" height="300" viewBox="0 0 420 300"><ellipse cx="210" cy="150" rx="190" ry="128" fill="#FFFFFF" stroke="#2B2D35" stroke-width="4"/>'
         '<ellipse cx="210" cy="150" rx="140" ry="92" fill="none" stroke="#B7BCC6" stroke-width="3"/>'
         '<ellipse cx="210" cy="150" rx="120" ry="80" fill="#1E1F25"/><ellipse cx="210" cy="150" rx="120" ry="80" fill="none" stroke="#7B3FE4" stroke-width="5"/>'
         '<path d="M90 150H330" stroke="#B79BFF" stroke-width="3" stroke-dasharray="8 6"/></svg>')
stage.append(el(f'<div class="cardx col" style="gap:6px">{plate}<div class="mono" style="font-size:30px;font-weight:800;color:{PURS}">LOCH Ø ≈ 23 CM ≈ TELLER</div></div>',
                40, 560, A("s2@breit", "s3", -0.15) + ' data-sfx="glass"', 470, CENTER))
stage.append(chip_("LOCH VS. GANZE ERDE: AM ENDE", "s4@winzig", "s5", PURS, "glass", ic(I["globe2"], 40, PURS, 3), OY, 30))
stage.append(chip_("1970 · DAMALS SOWJETUNION", "s5", "s6", PURS, "glass", ic(I["flag"], 40, PURS, 3), OY, 32, 0.2))
stage.append(chip_("WIE SIEHT DIE ERDE TIEF UNTEN AUS?", "s6@wissen", "s7", PURS, "glass", "", OY, 30))
stage.append(chip_("URALTES GESTEIN · ÜBER 2,5 MRD. JAHRE", "s7@uraltes", "s8", "#6E4E50", "marker", "", 340, 29))
# Tiefen-Zähler (große Zahl) + Jahr
stage.append(el(f'<div class="col" style="align-items:center"><div class="mono" style="font-size:28px;font-weight:800;color:{PURS};background:rgba(255,255,255,.92);padding:2px 12px;border-radius:8px">TIEFE</div>'
                f'<div class="huge2" id="dnum" style="color:{PURS};font-size:150px">0 M</div>'
                f'<div class="mono" id="ynum" style="font-size:34px;font-weight:800;color:#fff;background:{PURS};padding:4px 16px;border-radius:10px">1970</div></div>',
                0, 985, A("s7", "s9", -0.2) + ' data-sfx="none"', 1080, CENTER))
# Thermometer s9
stage.append(el(f'<div class="cardx row" style="gap:22px;padding:18px 28px">{ic(I["therm"], 84, HOT, 3.2)}<div class="col" style="align-items:flex-start">'
                f'<div class="huge2" style="color:{HOT};font-size:120px;letter-spacing:-4px"><span id="tnum">0</span> °C</div>'
                f'<div class="mono" id="texp" style="font-size:28px;font-weight:800;color:#5D616B;border-top:3px dashed #8A8F99;padding-top:6px;opacity:0">ERWARTET: ETWA 100 °C</div></div></div>',
                0, 1030, A("s9", "s10", -0.1) + ' data-sfx="none"', 1080, CENTER))
stage.append(chip_("HITZE + DRUCK → GESTEIN WIRD ZÄH", "s10@Hitze", "s11", HOT, "marker", "", OY, 30))
stage.append(chip_("DER BOHRER KLEMMT FEST", "s11@klemmt", "s12", HOT, "fail", "", OY, 32))
stage.append(el(f'<div class="stamp mono" style="font-size:46px;white-space:nowrap">ENDSTATION: 12.262 M</div>', 40, OY - 30, A("s12@Tiefer", "s13", 0.1), 1000, CENTER))
# Auflösung
paper = ('<svg width="120" height="110" viewBox="0 0 120 110"><path d="M18 14h62l16 16v70H18z" fill="#fff" stroke="#2B2D35" stroke-width="4" stroke-linejoin="round" transform="translate(10 -6)"/>'
         '<path d="M18 14h62l16 16v70H18z" fill="#fff" stroke="#2B2D35" stroke-width="4" stroke-linejoin="round"/><path d="M80 14v16h16M30 50h50M30 64h50M30 78h34" stroke="#2B2D35" stroke-width="3" fill="none"/></svg>')
stage.append(el(f'<div class="row" style="gap:28px;align-items:center"><div class="col" style="align-items:center"><div class="huge2" style="color:{HOT};font-size:150px">0,2 MM</div>'
                f'<div class="mono" style="font-size:28px;font-weight:800;color:{GR};background:rgba(255,255,255,.92);padding:2px 10px;border-radius:8px">TIEF – BEI EINEM FUSSBALL</div></div>'
                f'<div class="col" id="papw" style="align-items:center;opacity:0">{paper}<div class="mono" style="font-size:24px;font-weight:800;color:{GR}">= 2 BLATT</div></div></div>',
                0, 1060, A("s13@Loch", "end", 0.1) + ' data-sfx="glass"', 1080, CENTER))

PANJS = dict(DM=DM, SC=SC, DY=DY, K=[KX, KY],
    cx=[("s1",-1, 0, 1533, 0.25, 583), ("s2",-0.1, 0, 1533, 0.27, 583), ("s2@breit",0.15, -130, -70, 1.8, 620), ("s3",-0.05, -130, -70, 1.8, 620),
        ("s3@tiefer",0.35, 0, 3066, 1.25, 470), ("s4",0.1, 0, 3066, 1.25, 470), ("s4@ganze",0.25, 0, 1533, 0.25, 583), ("s5",0, 0, 1533, 0.25, 583),
        ("s6",0, 0, -10, 1.45, 520), ("s7",0.2, 0, 0, 1.25, 330), ("s8",0, 0, 3066, 0.8, 330), ("s8@zwanzig",0, 0, 3066, 0.42, 340), ("s8@tief",0.4, 0, 3066, 0.42, 380),
        ("s9",-0.1, 0, 3066, 1.05, 470), ("s10",0, 0, 3066, 1.7, 470), ("s11",0, 0, 3066, 2.4, 470), ("s12",0.2, 0, 3066, 2.2, 470),
        ("s13",0, 0, 3066, 2.2, 470), ("s13@Erde",0.3, 0, 1533, 0.22, 583)],
    mp=[("s5",-0.4, WX(17), WY(60.5), 7.2, 470), ("s5@Norden",0, WX(22), WY(63.5), 9.0, 470), ("s5@Halbinsel",0, KX, KY, 26, 470), ("s5@Kola",0.6, KX, KY, 60, 470), ("s6",0.3, KX, KY, 700, 470)])
SCENE_JS = r''' // ---- Bühne: Erd-Querschnitt / Karte / Erde ----
 {
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const sm=u=>u*u*(3-2*u);
  function kf(arr,tt){ const ks=arr.map(k=>({t:TS(k[0],k[1]),v:k.slice(2)})); if(tt<=ks[0].t) return ks[0].v;
    for(let i=0;i<ks.length-1;i++){ const a=ks[i],b=ks[i+1]; if(tt>=a.t&&tt<b.t){ const e=sm((tt-a.t)/Math.max(1e-6,b.t-a.t));
      const za=a.v[2], zb=b.v[2], z=Math.exp(Math.log(za)+(Math.log(zb)-Math.log(za))*e);
      // Zoom-korrigierte Interpolation: Bildpunkt-Bewegung gleichmäßig
      const w=(Math.abs(zb-za)<1e-6)?e:(1/za-1/z)/(1/za-1/zb);
      return [a.v[0]+(b.v[0]-a.v[0])*w, a.v[1]+(b.v[1]-a.v[1])*w, z, a.v[3]+(b.v[3]-a.v[3])*e]; } }
    return ks[ks.length-1].v; }
  const DM=PAN.DM, SC=PAN.SC;
  // Bohrtiefe
  let D=0; const a0=TS('s7',0), a1=TS('s8',0), a2=TS('s8@tief',0.15);
  if(t<TS('s5',-0.2)) D=DM; else if(t<a0) D=0; else if(t<a1) D=2400*Math.pow(pr(t,a0,a1-a0),1.15); else if(t<a2) D=2400+(DM-2400)*sm(pr(t,a1,a2-a1)); else D=DM;
  // Kamera Querschnitt
  const c=kf(PAN.cx,t); let cx=c[0], cy=c[1], z=c[2], FY=c[3];
  const fw=t>=TS('s7',0.2)&&t<TS('s9',-0.1); if(fw) cy=D*SC;
  if(t>=TS('s7',0)&&t<TS('s7',0.2)) cy=cy*(1-pr(t,TS('s7',0),0.2))+D*SC*pr(t,TS('s7',0),0.2);
  document.getElementById('xsg').setAttribute('transform',`translate(540,${FY}) scale(${z}) translate(${-cx},${-cy})`);
  const pj=(x,y)=>[540+(x-cx)*z, FY+(y-cy)*z];
  for(const g of document.querySelectorAll('.xg')){ const p=pj(+g.dataset.x,+g.dataset.y); g.style.left=p[0]+'px'; g.style.top=p[1]+'px';
    if(g.dataset.zs){ g.style.transform=`scale(${Math.max(+g.dataset.smin,Math.min(+g.dataset.smax, z/+g.dataset.zs))})`; } }
  // Loch + Gestänge (Bildschirm-konstante Breite)
  const hw=Math.max(7, 11*Math.min(1.6,z))/z; const hole=document.getElementById('hole'); hole.setAttribute('x',-hw); hole.setAttribute('width',2*hw); hole.setAttribute('height',Math.max(0,D*SC));
  const pp=document.getElementById('pipe'); const pw=3.2/z; pp.setAttribute('x',-pw); pp.setAttribute('width',2*pw); pp.setAttribute('y',-60); pp.setAttribute('height',Math.max(0,D*SC+60));
  const inXS=t<TS('s5',-0.2)||t>=TS('s6',0);
  // Nebel: unbekannte Tiefe
  const fogA=(t>=TS('s6',-0.2)?1:0)*(1-pr(t,TS('s8@zwölf',0),0.6)); const fg=document.getElementById('fog'); fg.style.opacity=fogA; fg.setAttribute('transform',`translate(0,${D*SC+18/z})`);
  // Hitze
  const heatA=(t<TS('s5',-0.2)?0.25:0)+(t>=TS('s8',0)?0.25*pr(t,TS('s8@zwölf',0),1):0)+0.55*pr(t,TS('s9@heiß',-0.3),0.8)*(1-pr(t,TS('s13',0.2),0.5))*(0.85+0.15*Math.sin(t*6));
  document.getElementById('heat').setAttribute('opacity',Math.min(0.9,heatA));
  // Everest + Lineal
  document.getElementById('ev').style.opacity=pr(t,TS('s8@zwanzig',-0.2),0.5)*(1-pr(t,TS('s9',-0.2),0.4));
  document.getElementById('labev').style.opacity=pr(t,TS('s8@zwanzig',0.3),0.4)*(1-pr(t,TS('s9',-0.2),0.4));
  document.getElementById('ruler').style.opacity=1-pr(t,TS('s2@breit',-0.2),0.3)+pr(t,TS('s4@ganze',0),0.4)*(1-pr(t,TS('s5',-0.2),0.2))+pr(t,TS('s13@Erde',0),0.3)*0;
  const ol=(id,v)=>{document.getElementById(id).style.opacity=cl(v,0,1);};
  ol('lab1', pr(t,TS('s7@Bohrkopf',0.2),0.3)*(1-pr(t,TS('s8',0),0.3)));
  ol('lab2', pr(t,TS('s8',0.4),0.3)*(1-pr(t,TS('s8@zwanzig',0.1),0.3)));
  ol('labhole', pr(t,TS('s6',0.3),0.3)*(1-pr(t,TS('s7',0.3),0.3)));
  // Bohrturm
  const rg=document.getElementById('rig'); const ra=t<TS('s5',-0.2)?1:pr(t,TS('s6',0.05),0.4); rg.style.opacity=Math.min(1,ra*2);
  rg.style.transform=`scaleY(${t<TS('s5',-0.2)?1:(0.2+0.8*(1+2.2*Math.pow(ra-1,3)+1.2*Math.pow(ra-1,2)))})`; rg.style.transformOrigin='0 0';
  // Bohrkopf (Hauptdarsteller)
  const bw=document.getElementById('bitw'); const bp=pj(0,D*SC); bw.style.left=bp[0]+'px'; bw.style.top=bp[1]+'px';
  const bs=cl(0.55+0.35*z,0.55,1.5); document.getElementById('bitb').style.transform=`scale(${bs})`;
  const vis=inXS&&(t<TS('s5',-0.2)||t>=TS('s6',0.2)); const ba=vis?(t<TS('s5',-0.2)?1-pr(t,TS('s5',-0.5),0.3):pr(t,TS('s6',0.3),0.3)):0;
  bw.style.opacity=ba*(1-pr(t,TS('s13',0.3),0.4));
  const stuckT=TS('s11@klemmt',0); const spd=t<stuckT?1:Math.max(0,1-(t-stuckT)/0.35);
  const spin=(t<stuckT?t:stuckT+0.35*0.5)*spd+(t>=stuckT?stuckT:0)*(1-spd);
  const ph=((t<stuckT?t:stuckT)*260)%20; document.getElementById('bitstr').setAttribute('transform',`translate(${ph},0)`);
  const jit=(t>=stuckT&&t<stuckT+0.5)?Math.exp(-(t-stuckT)*8)*6*Math.sin(t*95):0; document.getElementById('bitb').style.marginLeft=jit+'px';
  // Bohrstaub
  const drilling=(t<TS('s5',-0.2))||(t>=TS('s7',0)&&t<stuckT);
  document.querySelectorAll('.deb').forEach((d,i)=>{ const ph2=((t*1.7+i*0.137)%1); const ang=(i%2?1:-1)*(0.4+0.9*((i*0.37)%1));
    const r=ph2*70*bs; d.style.left=(Math.sin(ang)*r)+'px'; d.style.top=(-10*bs-ph2*50*bs+Math.abs(Math.cos(ang))*8)+'px';
    d.style.opacity=drilling?(1-ph2)*0.9:0; d.style.transform=`scale(${bs*(0.6+0.6*((i*0.53)%1))})`; });
  // Glühen
  const gl=document.getElementById('glow'); const ga=pr(t,TS('s9@heiß',-0.3),0.6)*(1-pr(t,TS('s13',0.2),0.4)); gl.style.opacity=ga*(0.75+0.25*Math.sin(t*7)); gl.style.transform=`scale(${bs*(1+0.08*Math.sin(t*5))})`;
  // Druckpfeile
  document.querySelectorAll('.parr').forEach((e,k)=>{ const a=pr(t,TS('s10@Druck',-0.1+k*0.08),0.25)*(1-pr(t,TS('s12',0),0.3)); const L=k<2; const yy=(k%2?-150:-40)*bs;
    const pulse=12*Math.sin(t*9+k); e.style.opacity=a; e.style.left=(L?(-210*bs+pulse):(120*bs-pulse))+'px'; e.style.top=(yy-22)+'px'; e.style.transform=L?'none':'scaleX(-1)'; });
  // Knete-Blobs drücken ins Loch
  const sq=ease(pr(t,TS('s11@drückt',-0.1),0.9)); const wob=Math.sin(t*6)*4*(1-sq*0.5);
  const bl=document.getElementById('blobL'), br=document.getElementById('blobR'); const ba2=pr(t,TS('s10@zäh',-0.2),0.4)*(1-pr(t,TS('s13',0.2),0.4));
  bl.style.opacity=ba2; br.style.opacity=ba2;
  bl.style.transform=`translate(${(-200+128*sq+wob)*bs}px,${-120*bs}px) scale(${bs*(1+0.06*Math.sin(t*5))})`; br.style.transform=`translate(${(60-128*sq-wob)*bs}px,${-120*bs}px) scale(${bs*(1+0.06*Math.sin(t*5+1))})`;
  ol('stuck', pr(t,stuckT,0.2)*(1-pr(t,TS('s13',0.2),0.3))); document.getElementById('stuck').style.transform=`translate(-50%,-50%) scale(${1+0.6*(1-ease(pr(t,stuckT,0.25)))})`;
  // Fragezeichen am Bohrkopf
  const qb=document.getElementById('qbit'); const qa=pr(t,TS('s3@tiefer',0.2),0.3)*(1-pr(t,TS('s4@ganze',0),0.3)); qb.style.opacity=qa; qb.style.transform=`translate(${80*bs}px,${-170*bs}px) rotate(${8*Math.sin(t*2.3)}deg) scale(${0.8+0.2*ease(qa)})`;
  // Zähler
  document.getElementById('dnum').textContent=Math.round(D).toLocaleString('de-DE')+' M';
  const yr=t<a0?1970:(t<a2?1970+19*pr(t,a0,a2-a0):1989); document.getElementById('ynum').textContent=Math.floor(yr);
  document.getElementById('tnum').textContent=Math.round(20+160*ease(pr(t,TS('s9',0),TS('s9@Grad',0)-TS('s9',0))));
  ol('texp', pr(t,TS('s9@erwartet',-0.1),0.3));
  // Querschnitt ein/aus (Karte dazwischen, Erde am Ende)
  const xsA=(t<TS('s5',-0.2)?1:pr(t,TS('s6',0.0),0.35))*(1-pr(t,TS('s13@Erde',0.1),0.35))+(t>=TS('s5',-0.2)&&t<TS('s5',0.15)?1-pr(t,TS('s5',-0.2),0.35):0);
  const xb=document.querySelector('#xswrap'); xb.style.opacity=Math.min(1,xsA)*(+xb.style.opacity||1);
  const xo=pr(t,TS('s13@Erde',-0.1),0.45); xb.style.transform=`scale(${1-0.85*ease(xo)})`; xb.style.transformOrigin=`540px ${FY}px`;
  // Karte
  const m=kf(PAN.mp,t); const M=document.getElementById('mapg'); M.setAttribute('transform',`translate(540,${m[3]}) scale(${m[2]}) translate(${-m[0]},${-m[1]})`);
  for(const g of document.querySelectorAll('#mapw .geo')){ g.style.left=(540+(+g.dataset.x-m[0])*m[2])+'px'; g.style.top=(m[3]+(+g.dataset.y-m[1])*m[2])+'px'; }
  const mw=document.getElementById('mapw'); mw.style.transform=`scale(${1})`;
  // Erde -> Fußball
  const ew=document.getElementById('earthw'); const ein=ease(pr(t,TS('s13@Erde',0),0.5)); ew.style.transform=`scale(${3.2-2.2*ein})`; ew.style.transformOrigin=`540px 140px`;
  const mb=pr(t,TS('s13@Fußball',-0.25),0.4); document.getElementById('earth').style.opacity=1-mb; const ball=document.getElementById('ball'); ball.style.opacity=mb;
  ball.setAttribute('transform',`translate(540 440) rotate(${-30*ease(mb)+6*Math.sin(t*1.3)}) scale(${0.92+0.08*ease(mb)})`);
  document.getElementById('emark').style.opacity=pr(t,TS('s13@groß',0),0.3)*(1-pr(t,TS('s13@Loch',0),0.3))*(0.7+0.3*Math.sin(t*8));
  const lw=document.getElementById('lens'); const la=pr(t,TS('s13@Loch',-0.15),0.35); lw.style.opacity=la; lw.style.transform=`scale(${0.4+0.6*(1+2.7*Math.pow(la-1,3)+1.7*Math.pow(la-1,2))})`;
  ol('papw', pr(t,TS('s13@zwei',-0.1),0.3));
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
