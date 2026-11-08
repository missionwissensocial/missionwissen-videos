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
HOOK = 'Warum radeln die <span style="color:#7B3FE4">Niederländer</span> so viel mehr?'
B = [
 ("r1", 0, HOOK, "In den *Niederlanden* wird viel *mehr* *Fahrrad* gefahren als bei *uns.*", "staunt"),
 ("r2", 0, HOOK, "Und das liegt *nicht* *nur* daran, dass das Land so *flach* ist.", None),
 ("r3", 0, HOOK, "Wie *groß* der *Unterschied* zu *Deutschland* ist, zeige ich dir am *Ende.*", None),
 ("r4", 1, "", "In den *Fünfziger-* und *Sechzigerjahren* kauften die Niederländer, wie wir, immer *mehr* *Autos.*", None),
 ("r5", 1, "", "*Radfahrer* mussten *mitten* im *Autoverkehr* fahren.", None),
 ("r6", 1, "", "Anfang der *Siebzigerjahre* starben dort jedes Jahr über *dreitausend* *Menschen* im *Straßenverkehr.*", None),
 ("r7", 1, "", "Darunter *Hunderte* *Kinder.*", None),
 ("r8", 1, "", "*Eltern* *protestierten* auf der *Straße.*", None),
 ("r9", 1, "", "Ihr *Motto:* *Stoppt* den *Kindermord.*", None),
 ("r10", 2, "", "Dazu kam *neunzehnhundertdreiundsiebzig* die *Ölkrise.*", None),
 ("r11", 2, "", "*Benzin* wurde *knapp.*", None),
 ("r12", 2, "", "An *zehn* *Sonntagen* war *Autofahren* sogar *verboten.*", None),
 ("r13", 2, "", "*Proteste* und *Ölkrise* brachten die *Wende:* Die *Politik* setzte aufs *Fahrrad.*", None),
 ("r14", 3, "", "Ab *Mitte* der *Siebziger* bauten Städte wie *Den* *Haag* und *Delft* eigene *Radrouten.*", None),
 ("r15", 3, "", "Heute gibt es dort rund *achtunddreißigtausend* *Kilometer* *Radwege,* die durch einen *Bordstein* oder *Grünstreifen* von den *Autos* *getrennt* sind.", None),
 ("r16", 3, "", "Fast *einmal* um die *ganze* *Erde.*", None),
 ("r17", 3, "", "Denn wer sich *sicher* fühlt, fährt *eher* *Rad.*", None),
 ("r18", 3, "", "Also: Nicht nur die *Landschaft* macht den Unterschied, sondern vor allem *sichere* *Radwege.*", None),
 ("r19", 4, "", "Und wie *groß* ist der *Unterschied?*", None),
 ("r20", 4, "", "Von *hundert* *Wegen* im *Alltag* machen die *Niederländer* *achtundzwanzig* mit dem *Fahrrad.*", None),
 ("r21", 4, "", "Wir in *Deutschland:* *elf.*", None),
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

# ================= Bühne: Karte NL/DE -> Kameraflug in eine niederländische Straße -> Den Haag/Delft -> Straße -> Karte =================
GEO = json.load(open("geo.json")); L0, B0, KX, KY = GEO["L0"], GEO["B0"], GEO["KX"], GEO["KY"]
def WX(lon): return (lon - L0) * KX
def WY(lat): return (B0 - lat) * KY
TQ = "#19C6B4"; PUR = "#7B3FE4"; RED = "#E5484D"; TQD = "#0E8C80"; PURS = "#5B2BB5"; GR = "#3F434C"; INK = "#2B2D35"
FX0, FY0 = 540, 880
MX, MY = round(WX(9.0), 1), round(WY(51.6), 1)
SX, SY = round(WX(5.9), 1), round(WY(52.25), 1)   # Straßenszene (in den Niederlanden)
ZS = 50.0
def SC(x, y): return [round(SX + x / ZS, 3), round(SY + y / ZS, 3)]
SF = SC(0, 70); SF2 = SC(40, 70); ZC = ZS * 1.15
DH = (round(WX(4.30), 1), round(WY(52.08), 1)); DL = (round(WX(4.36), 1), round(WY(52.01), 1))
HF = (round(WX(4.9), 1), round(WY(52.15), 1))
cam = [
 ["r1", -0.2, MX, MY, 1.2], ["r3@Ende", 0.2, MX + 5, MY + 3, 1.25],
 ["r4", -0.2, MX + 5, MY + 3, 1.25], ["r4@Sechzigerjahren", 0.1, SF[0], SF[1], ZC],
 ["r13", 0.0, SF2[0], SF2[1], ZC],
 ["r14", -0.15, SF2[0], SF2[1], ZC], ["r14@Siebziger", 0.1, HF[0], HF[1], 5.0],
 ["r15", -0.35, HF[0] + 0.4, HF[1], 5.2], ["r15@Kilometer", 0.0, SF[0], SF[1], ZC],
 ["r19", -0.2, SF2[0], SF2[1], ZC], ["r19@Unterschied", 0.0, MX, MY, 1.2], ["end", 0, MX, MY, 1.2],
]
def path(d, fill, stroke, cls="ol", extra=""): return f'<path class="{cls}" d="{d}" fill="{fill}" stroke="{stroke}" stroke-linejoin="round" {extra}/>'
other = "".join(path(d, "#FFFFFF", "#9AA0AA") for d in GEO["other"])

# ---- Figuren (Szenen-px, Grundlinie y=0) ----
def wheel(cx):
    return (f'<g class="wh" data-cx="{cx}"><circle cx="{cx}" cy="-26" r="25" fill="none" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M{cx-22} -26 H{cx+22} M{cx} -48 V-4" stroke="#9AA0AA" stroke-width="2.5"/></g>')
def bike(fc=PUR, jacket=PUR, kid=False, idd="", style=""):
    s = 0.78 if kid else 1.0
    ii = f' id="{idd}"' if idd else ""
    return (f'<g{ii} class="bk" style="{style}"><g transform="scale({s})">' + wheel(-42) + wheel(42) +
            f'<path d="M-42 -26 L0 -26 L-12 -70 Z M-12 -70 L30 -72 L0 -26 M30 -72 L42 -26" fill="none" stroke="{fc}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="M24 -84 L34 -82 M30 -72 L28 -84" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M-18 -74 H-4" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M-10 -74 L4 -50 L0 -26" fill="none" stroke="#3A3D46" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M-10 -76 L2 -128" stroke="{jacket}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M0 -120 L28 -86" stroke="{jacket}" stroke-width="9" stroke-linecap="round"/>'
            f'<circle cx="6" cy="-146" r="14" fill="#F3D6C2" stroke="{INK}" stroke-width="3"/>'
            '</g></g>')
def car(col, idd):
    return (f'<g id="{idd}" class="car"><path d="M-92 -20 Q-94 -50 -70 -52 L-48 -54 L-28 -82 L36 -82 L58 -54 L82 -50 Q94 -46 92 -20 Z" fill="{col}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M-40 -56 L-24 -76 L2 -76 L2 -56 Z M10 -56 L10 -76 L32 -76 L48 -56 Z" fill="#E6F6F4" stroke="{INK}" stroke-width="3"/>'
            f'<circle cx="-54" cy="-18" r="17" fill="{INK}"/><circle cx="-54" cy="-18" r="7" fill="#C9CCD3"/>'
            f'<circle cx="56" cy="-18" r="17" fill="{INK}"/><circle cx="56" cy="-18" r="7" fill="#C9CCD3"/></g>')
def person(x, col, arm_up=True):
    arms = f'<path d="M{x} -82 L{x-14} -128 M{x} -82 L{x+14} -128" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>' if arm_up else ""
    return (f'<path d="M{x} -40 L{x} -90" stroke="{col}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M{x} -40 L{x-9} 0 M{x} -40 L{x+9} 0" stroke="#3A3D46" stroke-width="7" stroke-linecap="round"/>{arms}'
            f'<circle cx="{x}" cy="-106" r="13" fill="#F3D6C2" stroke="{INK}" stroke-width="3"/>')
def house(x, w, h, col, k):
    roof = (f'M{x} {-h} L{x+w/2} {-h-60} L{x+w} {-h} Z' if k % 2 == 0 else
            f'M{x+10} {-h} V{-h-30} H{x+30} V{-h-55} H{x+w-30} V{-h-30} H{x+w-10} V{-h} Z')
    win = "".join(f'<rect x="{x+18+j*((w-36)/2):.0f}" y="{-h+30+i*70}" width="{(w-60)/2:.0f}" height="44" fill="#E6F6F4" stroke="{INK}" stroke-width="3"/>'
                  for i in range(max(1, int((h-60)//70))) for j in range(2))
    return (f'<rect x="{x}" y="{-h}" width="{w}" height="{h}" fill="{col}" stroke="{INK}" stroke-width="4"/>'
            f'<path d="{roof}" fill="{col}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>{win}'
            f'<rect x="{x+w/2-16}" y="-56" width="32" height="56" fill="#FFFFFF" stroke="{INK}" stroke-width="3"/>')
HC = ["#F1DDD3", "#E8E2F7", "#DDF1EE", "#F4E9CF", "#EADBD5"]
houses = "".join(house(-3800 + k * 150, 140, [210, 250, 190, 240, 220][k % 5], HC[k % 5], k) for k in range(52))
trees = "".join(f'<g class="tree" data-k="{k}" style="opacity:0"><path d="M{x} 150 V118" stroke="#7A5A3A" stroke-width="7" stroke-linecap="round"/>'
                f'<circle cx="{x}" cy="104" r="22" fill="#BFE5C8" stroke="#3E8E5A" stroke-width="4"/></g>' for k, x in enumerate(range(-3800, 3900, 190)))
CARC = ["#B9BDC6", "#9DA8C9", "#C9B7E8", "#A9D9D2", "#D9C3B6", "#B9BDC6"]
cars = "".join(car(CARC[k], f"car{k}") for k in range(6))
sunb = "".join(bike(fc, jk, idd=f"sb{k}", style="opacity:0") for k, (fc, jk) in enumerate([(TQ, TQD), ("#8A8F99", "#E5A33A"), (PUR, "#3E8E5A")]))
xb = bike(TQ, TQD, idd="xb0", style="opacity:0") + bike("#8A8F99", "#E5A33A", kid=True, idd="xb1", style="opacity:0") + bike(PURS, "#D97A6C", idd="xb2", style="opacity:0")
protest = (f'<g id="protest" style="opacity:0">' + "".join(person(200 + k * 52, ["#D97A6C", "#9DA8C9", "#E5A33A", "#3E8E5A", "#C9B7E8", "#D97A6C"][k], k in (1, 2, 3, 4)) for k in range(6)) +
           f'<rect x="232" y="-212" width="228" height="80" rx="6" fill="#FFFFFF" stroke="{INK}" stroke-width="4"/>'
           f'<text x="346" y="-180" text-anchor="middle" font-family="JBM" font-weight="800" font-size="24" fill="{RED}">STOP DE</text>'
           f'<text x="346" y="-150" text-anchor="middle" font-family="JBM" font-weight="800" font-size="24" fill="{RED}">KINDERMOORD</text></g>')
scene = (
  '<defs><pattern id="mmp" width="50" height="50" patternUnits="userSpaceOnUse"><rect width="50" height="50" fill="#FCFCFD"/>'
  '<path d="M0 0.5H50M0.5 0V50" stroke="rgba(11,11,16,.09)" stroke-width="1"/>'
  + "".join(f'<path d="M0 {k*10+.5}H50M{k*10+.5} 0V50" stroke="rgba(11,11,16,.035)" stroke-width="1"/>' for k in range(1, 5)) + '</pattern></defs>'
  '<rect x="-30000" y="-20000" width="60000" height="40000" fill="url(#mmp)"/>'
  + houses +
  f'<rect x="-8000" y="0" width="16000" height="40" fill="#E4E6EB"/><path d="M-8000 0 H8000" stroke="{INK}" stroke-width="3"/>'
  f'<rect x="-8000" y="40" width="16000" height="300" fill="#C9CDD5"/><path d="M-8000 40 H8000 M-8000 340 H8000" stroke="{INK}" stroke-width="3"/>'
  f'<path d="M-8000 255 H8000" stroke="#FFFFFF" stroke-width="6" stroke-dasharray="40 34"/>'
  f'<g id="newlane"><g id="rw" style="transform-origin:0 40px;transform:scaleY(0)"><rect x="-8000" y="40" width="16000" height="72" fill="#D98A7E"/>'
  f'<text x="-330" y="88" font-family="JBM" font-weight="800" font-size="26" fill="#FFFFFF" letter-spacing="3">RADWEG</text>'
  f'<text x="420" y="88" font-family="JBM" font-weight="800" font-size="26" fill="#FFFFFF" letter-spacing="3">RADWEG</text></g>'
  f'<g id="gs" style="transform-origin:0 112px;transform:scaleY(0)"><rect x="-8000" y="112" width="16000" height="44" fill="#BFE5C8"/>'
  f'<path d="M-8000 112 H8000 M-8000 156 H8000" stroke="#3E8E5A" stroke-width="4"/></g>'
  f'<path id="bord" d="M-8000 158 H8000" stroke="{INK}" stroke-width="7" style="opacity:0"/>{trees}'
  f'<text id="gslab" x="0" y="143" text-anchor="middle" font-family="JBM" font-weight="800" font-size="22" fill="#2E6B44" letter-spacing="2" style="opacity:0">GRÜNSTREIFEN</text></g>'
  + protest + sunb + xb + bike(PUR, PUR, idd="hero") + cars
)
mapsvg = (f'<svg id="world" width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">'
          f'<g id="camg"><g id="mapl">{other}'
          + path(GEO["de"], "#FFFFFF", INK, "ol", 'id="dep"') + path(GEO["nl"], "#FFFFFF", INK, "ol", 'id="nlp"')
          + f'</g><g id="scn" transform="translate({SX},{SY}) scale({1/ZS})" style="opacity:0">{scene}</g></g></svg>')
stage.append(mapsvg); stage.append('<div id="headbg"></div>')

# --- Labels an der Karte ---
def glab(lon, lat, inner, i, o, d=0, idd="", sfx="none", wx=None, wy=None):
    ii = f' id="{idd}"' if idd else ""
    x = WX(lon) if wx is None else wx; y = WY(lat) if wy is None else wy
    return (f'<div class="geo" data-x="{x:.1f}" data-y="{y:.1f}"><div class="el"{ii} {A(i, o, d)} data-sfx="{sfx}" style="left:0;top:0;transform-origin:0 0">'
            f'<div style="transform:translate(-50%,-50%)">{inner}</div></div></div>')
def maplab(t, col): return f'<span class="mono lab" style="color:{col};border-color:{col}">{t}</span>'
FLAG_DE = '<span class="flag v"><i style="background:#111"></i><i style="background:#D33A3A"></i><i style="background:#F2C230"></i></span>'
FLAG_NL = '<span class="flag v"><i style="background:#C8242E"></i><i style="background:#fff"></i><i style="background:#21468B"></i></span>'
BIKEIC = (f'<svg viewBox="-80 -175 160 180" width="150" height="169" style="overflow:visible">{bike(PUR, PUR)}</svg>')
PIN = lambda t, side: (f'<div class="row" style="gap:10px;flex-direction:{"row-reverse" if side=="l" else "row"}"><span class="pin" style="background:{PUR}"></span>'
                       f'<span class="mono lab" style="color:{PURS};border-color:{PURS}">{t}</span></div>')
geo = (glab(5.4, 53.75, maplab("NIEDERLANDE", PURS), "r1", "r4", -0.6)
       + glab(10.4, 50.9, maplab("DEUTSCHLAND", GR), "r1", "r4", -0.6)
       + glab(5.6, 52.35, f'<div id="mbike">{BIKEIC}</div>', "r1", "r4@Sechzigerjahren", -0.6, "", "none")
       + f'<div class="geo" data-x="{DH[0]}" data-y="{DH[1]}"><div class="el" {A("r14@Den","r15",-0.1)} data-sfx="marker" style="left:0;top:0"><div style="transform:translate(calc(-100% + 11px),-50%)">{PIN("DEN HAAG","l")}</div></div></div>'
       + f'<div class="geo" data-x="{DL[0]}" data-y="{DL[1]}"><div class="el" {A("r14@Delft","r15",-0.1)} data-sfx="marker" style="left:0;top:0"><div style="transform:translate(-11px,-50%)">{PIN("DELFT","r")}</div></div></div>'
       + f'<div class="geo" data-x="{(DH[0]+DL[0])/2+6}" data-y="{(DH[1]+DL[1])/2-26}"><div class="el" {A("r14@Radrouten","r15",-0.2)} data-sfx="plop" style="left:0;top:0"><div style="transform:translate(-50%,-50%) scale(.7)">{BIKEIC}</div></div></div>')
stage.append(f'<div id="geol">{geo}</div>')

# --- Overlays (höchstens eines gleichzeitig) ---
def chip_(txt, i, o, col=PURS, sfx="marker", y=1150, fs=30, d=0, dash=False):
    return el(f'<div class="chip mono row" style="font-size:{fs}px;font-weight:800;gap:12px;padding:12px 22px;border-color:{col};color:{col};background:rgba(255,255,255,.97);white-space:nowrap;{"border-style:dashed;" if dash else ""}">{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
stage.append(chip_("FLACHES LAND? DAS IST NICHT ALLES", "r2@flach", "r3", GR, "marker", 1150, 32, -0.2))
stage.append(chip_(f'{FLAG_NL}&nbsp;?? &nbsp;<span style="color:#8A8F99">vs.</span>&nbsp; {FLAG_DE}&nbsp;??&nbsp;&nbsp;<span style="font-size:22px;color:#8A8F99">AM ENDE</span>', "r3@Unterschied", "r4", GR, "glass", 1150, 34, -0.1))
CARIC = '<svg viewBox="-100 -90 200 95" width="92" height="44">' + car("#9DA8C9", "ci").replace('id="ci" ', '') + '</svg>'
YRS = (f'<div class="col" style="gap:4px"><div class="huge" id="yr" style="font-size:150px;color:{PURS}">1950</div>'
       f'<div class="mono" style="font-size:30px;font-weight:800;color:{GR}">IMMER MEHR AUTOS</div>'
       f'<div class="row" style="gap:10px;margin-top:10px">' + "".join(f'<span class="ca" data-k="{k}" style="opacity:0">{CARIC}</span>' for k in range(7)) + '</div></div>')
stage.append(el(YRS, 40, 170, A("r4@Fünfziger-", "r5", -0.2) + ' data-sfx="glass"', 1000, CENTER))
stage.append(chip_(f'<span style="color:{RED}">⚠</span>&nbsp;RADFAHRER MITTEN IM AUTOVERKEHR', "r5@Radfahrer", "r6", GR, "marker", 300, 32))
DEAD = (f'<div class="col" style="gap:6px"><div class="row" style="gap:16px;align-items:baseline"><div class="mono" style="font-size:44px;font-weight:800;color:{RED}">ÜBER</div>'
        f'<div class="huge num" id="dead" style="font-size:170px;color:{RED}">0</div></div>'
        f'<div class="mono" style="font-size:28px;font-weight:800;color:{GR};white-space:nowrap">VERKEHRSTOTE PRO JAHR</div>'
        f'<div class="mono" style="font-size:22px;font-weight:700;color:#8A8F99;white-space:nowrap">NIEDERLANDE · ANFANG DER 70ER-JAHRE</div></div>')
stage.append(el(DEAD, 40, 170, A("r6@dreitausend", "r7", -0.15) + ' data-sfx="glass"', 1000, CENTER))
stage.append(chip_("DARUNTER HUNDERTE KINDER", "r7@Hunderte", "r8", RED, "marker", 300, 40, -0.15))
stage.append(chip_(f'„STOP DE KINDERMOORD“&nbsp;<span style="color:#8A8F99">=</span>&nbsp;STOPPT DEN KINDERMORD', "r9@Stoppt", "r10", RED, "marker", 300, 30, -0.3))
GAUGE = (f'<svg viewBox="-110 -110 220 130" width="220" height="130"><path d="M-90 0 A90 90 0 0 1 90 0" fill="none" stroke="#E6E7EB" stroke-width="18" stroke-linecap="round"/>'
         f'<path d="M-90 0 A90 90 0 0 1 -64 -64" fill="none" stroke="{RED}" stroke-width="18" stroke-linecap="round"/>'
         f'<text x="-92" y="22" text-anchor="middle" font-family="JBM" font-weight="800" font-size="22" fill="{RED}">E</text><text x="92" y="22" text-anchor="middle" font-family="JBM" font-weight="800" font-size="22" fill="{GR}">F</text>'
         f'<g id="needle"><path d="M0 0 L0 -78" stroke="{INK}" stroke-width="7" stroke-linecap="round"/></g><circle r="11" fill="{INK}"/></svg>')
OIL = (f'<div class="row" style="gap:34px"><div class="col" style="gap:2px"><div class="huge" style="font-size:150px;color:{PURS}">1973</div>'
       f'<div class="mono" style="font-size:34px;font-weight:800;color:{GR}">ÖLKRISE</div></div>'
       f'<div class="col" style="gap:4px">{GAUGE}<div class="mono" style="font-size:24px;font-weight:800;color:{RED}" id="knapp">BENZIN</div></div></div>')
stage.append(el(OIL, 40, 180, A("r10@neunzehnhundertdreiundsiebzig", "r12", -0.15) + ' data-sfx="glass"', 1000, CENTER))
SUN = (f'<div class="col" style="gap:6px"><div class="row" style="gap:18px;align-items:baseline"><div class="huge num" style="font-size:170px;color:{TQD}">{cnt(10, "r12@zehn", 0, 0)}</div>'
       f'<div class="mono" style="font-size:36px;font-weight:800;color:{TQD};line-height:1.15">AUTOFREIE<br>SONNTAGE</div></div>'
       f'<div class="row" style="gap:10px">' + "".join(f'<span class="sun" data-k="{k}"></span>' for k in range(10)) + '</div>'
       f'<div class="mono" style="font-size:22px;font-weight:700;color:#8A8F99">NOV. 1973 – JAN. 1974</div></div>')
stage.append(el(SUN, 40, 170, A("r12@zehn", "r13", -0.15) + ' data-sfx="glass"', 1000, CENTER))
stage.append(chip_("✓ WENDE: DIE POLITIK SETZT AUFS FAHRRAD", "r13@Wende", "r14", TQD, "success", 300, 32, -0.1))
stage.append(chip_("AB MITTE DER 70ER: ERSTE RADROUTEN", "r14@Mitte", "r15", PURS, "marker", 300, 34, 0.1))
KM = (f'<div class="col" style="gap:6px"><div class="row" style="gap:16px;align-items:baseline"><div class="mono" style="font-size:40px;font-weight:800;color:{PURS}">RUND</div>'
      f'<div class="huge num" id="km" style="font-size:160px;color:{PURS}">0</div><div class="mono" style="font-size:44px;font-weight:800;color:{PURS}">KM</div></div>'
      f'<div class="mono" style="font-size:28px;font-weight:800;color:{GR};white-space:nowrap">RADWEGE, VON DEN AUTOS GETRENNT</div></div>')
stage.append(el(KM, 40, 170, A("r15@achtunddreißigtausend", "r16", -0.15) + ' data-sfx="glass"', 1000, CENTER))
EARTH = (f'<div class="row" style="gap:30px"><svg viewBox="-110 -110 220 220" width="230" height="230"><circle r="80" fill="#E6F6F4" stroke="{INK}" stroke-width="4"/>'
         f'<path d="M-40 -60 q20 10 10 30 q-20 10 -10 30 M30 -50 q-10 30 20 40 M10 30 q20 10 30 -10" fill="none" stroke="#3E8E5A" stroke-width="5" stroke-linecap="round"/>'
         f'<circle r="98" fill="none" stroke="#E6E7EB" stroke-width="10"/>'
         f'<circle id="ering" r="98" fill="none" stroke="{PUR}" stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" transform="rotate(-90)"/></svg>'
         f'<div class="col" style="align-items:flex-start;gap:6px"><div class="mono" style="font-size:34px;font-weight:800;color:{PURS}">38.000 KM</div>'
         f'<div class="mono" style="font-size:26px;font-weight:800;color:{GR}">ERDUMFANG: 40.000 KM</div>'
         f'<div class="mono" style="font-size:30px;font-weight:800;color:#fff;background:{PUR};border-radius:10px;padding:6px 14px">FAST 1× UM DIE ERDE</div></div></div>')
stage.append(el(EARTH, 40, 170, A("r16", "r17", -0.1) + ' data-sfx="glass"', 1000, CENTER))
stage.append(chip_("✓ NICHT NUR DIE LANDSCHAFT – SICHERE RADWEGE", "r18@Landschaft", "r19", TQD, "success", 300, 29, -0.1))
stage.append(chip_(f'{FLAG_NL}&nbsp;VS.&nbsp;{FLAG_DE}&nbsp; VON 100 WEGEN IM ALLTAG', "r19@Unterschied", "end", GR, "glass", 190, 32, 0.1))
# --- Auflösung: zwei 10x10-Raster ---
def grid(gid): return f'<div class="grid" id="{gid}">' + "".join(f'<i data-i="{k}"></i>' for k in range(100)) + '</div>'
COL_NL = (f'<div class="col" style="gap:8px">{FLAG_NL}<div class="mono" style="font-size:24px;font-weight:800;color:#5D616B">NIEDERLANDE</div>'
          f'<div class="row" style="gap:10px;align-items:baseline"><div class="huge num" id="nnl" style="font-size:150px;color:{PURS}">{cnt(28, "r20@Niederländer", 0, 0.1)}</div><div class="mono" style="font-size:30px;font-weight:800;color:{PURS}">VON 100</div></div>'
          f'{grid("gnl")}<div class="mono" style="font-size:22px;font-weight:800;color:#5D616B;margin-top:6px">WEGEN MIT DEM RAD</div></div>')
COL_DE = (f'<div class="col" style="gap:8px">{FLAG_DE}<div class="mono" style="font-size:24px;font-weight:800;color:#5D616B">DEUTSCHLAND</div>'
          f'<div class="row" style="gap:10px;align-items:baseline"><div class="huge num" id="nde" style="font-size:150px;color:{TQD}">{cnt(11, "r21@Deutschland", 0, -0.1)}</div><div class="mono" style="font-size:30px;font-weight:800;color:{TQD}">VON 100</div></div>'
          f'{grid("gde")}<div class="mono" style="font-size:22px;font-weight:800;color:#5D616B;margin-top:6px">WEGEN MIT DEM RAD</div></div>')
stage.append(el(COL_NL, 40, 300, A("r20@Wegen", "end", 0.0) + ' data-sfx="glass"', 500, CENTER))
stage.append(el(COL_DE, 540, 300, A("r21", "end", -0.1) + ' data-sfx="glass"', 500, CENTER))
# dezente Hinweise / Quellen
stage.append(el('<div class="note mono">SZENE SCHEMATISCH</div>', 40, 1252, A("r4@Sechzigerjahren", "r6@dreitausend", 0.3) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">QUELLE: CBS (HÖCHSTSTAND 1972: 3.264 VERKEHRSTOTE)</div>', 40, 1252, A("r6@dreitausend", "r10", 0.2) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">QUELLE: KiM FIETSFEITEN 2023 (≈ 38.000 KM SEPARATE RADWEGE) · SZENE SCHEMATISCH</div>', 40, 1252, A("r15@Kilometer", "r19", 0.3) + ' data-sfx="none"'))
stage.append(el('<div class="note mono">QUELLEN: KiM FIETSFEITEN 2023 (NL, DATEN 2022: 28 %) · MOBILITÄT IN DEUTSCHLAND 2023 (11 %)</div>', 40, 1252, A("r20", "end", 0.2) + ' data-sfx="none"'))
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
  const sA=pr(z,16,14); const ML=document.getElementById('mapl');
  const dim=1-0.82*pr(t,TS('r20',-0.2),0.5);
  ML.style.opacity=(1-pr(z,30,10))*dim; ML.style.display=z>42?'none':'';
  const SCN=document.getElementById('scn'); SCN.style.opacity=sA; SCN.style.display=sA<0.005?'none':'';
  const pulse=0.5+0.5*Math.sin(t*2*Math.PI/1.2);
  const nlOn=Math.max(1-pr(t,TS('r4',0),0.4), pr(t,TS('r14',0),0.4)*(1-pr(t,TS('r15',0),0.3)), pr(t,TS('r19',0),0.4));
  document.getElementById('nlp').setAttribute('fill',`rgba(123,63,228,${(0.10+0.28*nlOn+0.08*nlOn*pulse).toFixed(3)})`);
  const deOn=Math.max(pr(t,TS('r3@Deutschland',-0.2),0.4)*(1-pr(t,TS('r4',0),0.4)), pr(t,TS('r19',0.2),0.4));
  document.getElementById('dep').setAttribute('fill',`rgba(25,198,180,${(0.04+0.24*deOn).toFixed(3)})`);
  const mb=document.getElementById('mbike'); mb.style.transform=`translateY(${(4*Math.sin(t*2*Math.PI/1.1)).toFixed(1)}px)`;
  // ---- Straße ----
  const tA=TS('r10@Ölkrise',0), tB=TS('r11',0.6);
  const dist=x=>{ if(x<tA) return x; const sp=u=>1-0.6*cl((u-tA)/(tB-tA),0,1); let s=tA, d=0.04; for(let u=tA;u<x;u+=d){ s+=sp(u)*Math.min(d,x-u);} return s; };
  const D=dist(t);
  const carsOut=pr(t,TS('r12@Sonntagen',-0.1),0.5)*(1-pr(t,TS('r15',-0.3),0.05));
  const sep=pr(t,TS('r15@Radwege',-0.2),0.45);
  const CL=[[-700,300,1],[-200,300,1],[350,300,1],[-500,420,-1],[150,420,-1],[700,420,-1]];
  CL.forEach((c,i)=>{ const e=document.getElementById('car'+i); const v=c[2]>0?300:260; let x=c[0]+c[2]*v*D; x=((x+1300)%2600+2600)%2600-1300;
    const y=c[1]===300?(260-30*(1-sep)):340-10; e.setAttribute('transform',`translate(${x.toFixed(1)},${(c[1]===300?240:330)}) scale(${c[2]},1)`); e.style.opacity=1-carsOut; });
  const ang=t*420;
  document.querySelectorAll('#scn .wh').forEach(w=>{ const cx=+w.dataset.cx; w.setAttribute('transform',`rotate(${ang.toFixed(1)} ${cx} -26)`); });
  const hb=document.getElementById('hero'); const hy=150-55*sep; const hx=-150+18*Math.sin(t*0.6);
  hb.setAttribute('transform',`translate(${hx.toFixed(1)},${(hy+1.5*Math.sin(t*9)).toFixed(1)})`);
  // Protest
  const pin=pr(t,TS('r8@Eltern',-0.15),0.35), pout=pr(t,TS('r10',-0.1),0.3);
  const P_=document.getElementById('protest'); P_.style.opacity=pin*(1-pout); P_.setAttribute('transform',`translate(0,${(8*Math.sin(t*6)).toFixed(1)}) translate(0,${(1-ease(pin))*40})`);
  // Sonntags-Räder auf der Fahrbahn
  [[150,240],[420,330],[-420,330]].forEach((p,i)=>{ const e=document.getElementById('sb'+i); const u=pr(t,TS('r12@Autofahren',-0.3+i*0.2),0.3)*(1-pr(t,TS('r14',0.2),0.1));
    const x=p[0]+60*(t-TS('r12',0)); e.setAttribute('transform',`translate(${x.toFixed(1)},${p[1]})`); e.style.opacity=u; });
  // neue Radwege
  document.getElementById('rw').style.transform=`scaleY(${ease(sep).toFixed(3)})`;
  const gsp=pr(t,TS('r15@Grünstreifen',-0.3),0.4); document.getElementById('gs').style.transform=`scaleY(${ease(gsp).toFixed(3)})`;
  document.getElementById('gslab').style.opacity=pr(t,TS('r15@Grünstreifen',0.1),0.3);
  document.getElementById('bord').style.opacity=pr(t,TS('r15@Bordstein',-0.15),0.25);
  document.querySelectorAll('#scn .tree').forEach(tr=>{ const k=+tr.dataset.k; const u=pr(t,TS('r15@Grünstreifen',0.05)+k*0.05,0.25); tr.style.opacity=u; tr.setAttribute('transform',`translate(0,${(20*(1-ease(u))).toFixed(1)})`); });
  // mehr Räder auf dem Radweg
  [[-430,105],[-650,105],[160,105]].forEach((p,i)=>{ const e=document.getElementById('xb'+i); const u=pr(t,TS('r17@sicher',-0.1+i*0.3),0.35);
    e.setAttribute('transform',`translate(${(p[0]+14*Math.sin(t*0.6+i)).toFixed(1)},${(p[1]+1.5*Math.sin(t*9+i)).toFixed(1)})`); e.style.opacity=u*(1-pr(t,TS('r19',0.3),0.2)); });
  // Overlays: Zähler und Anzeigen
  document.getElementById('yr').textContent=1950+Math.round(19*ease(pr(t,TS('r4@Fünfziger-',0),TS('r4@Autos',0)-TS('r4@Fünfziger-',0))));
  document.querySelectorAll('.ca').forEach(c=>{ const k=+c.dataset.k; c.style.opacity=pr(t,TS('r4@kauften',0)+k*0.18,0.15); });
  document.getElementById('dead').textContent=Math.round(3000*ease(pr(t,TS('r6@dreitausend',-0.1),0.9))).toLocaleString('de-DE');
  document.getElementById('km').textContent=Math.round(38000*ease(pr(t,TS('r15@achtunddreißigtausend',-0.1),1.0))).toLocaleString('de-DE');
  const na=-60+(-75+60)*0; const nd=ease(pr(t,TS('r11@knapp',-0.4),0.6)); document.getElementById('needle').setAttribute('transform',`rotate(${(40-120*nd-6*(t>TS('r11@knapp',0.2)?Math.sin(t*18)*Math.exp(-(t-TS('r11@knapp',0.2))*4):0)).toFixed(1)})`);
  document.getElementById('knapp').textContent=t>TS('r11@knapp',-0.1)?'BENZIN KNAPP':'BENZIN';
  document.querySelectorAll('.sun').forEach(s=>{ const k=+s.dataset.k; const u=pr(t,TS('r12@zehn',-0.1)+k*0.08,0.12); s.style.background=u>0.5?'#19C6B4':'#E6E7EB'; s.style.transform=`scale(${0.8+0.2*ease(u)})`; });
  document.getElementById('ering').style.strokeDashoffset=(1-0.95*ease(pr(t,TS('r16@einmal',-0.1),1.0))).toFixed(3);
  // Raster der Auflösung
  for(const [gid,nid,col] of [['gnl','nnl','#7B3FE4'],['gde','nde','#19C6B4']]){
    const v=parseFloat(document.getElementById(nid).textContent.replace(',','.'))||0;
    document.querySelectorAll('#'+gid+' i').forEach(d=>{ const k=+d.dataset.i; d.style.background=k<Math.round(v)?col:'#E6E7EB'; });
  }
  // Labels an der Karte
  document.getElementById('geol').style.opacity=(1-pr(z,14,6))*(1-pr(t,END,0.3))*(1-pr(t,TS('r19',0),0.2));
  for(const gg of document.querySelectorAll('.geo')){ const [sx,sy]=pj(+gg.dataset.x,+gg.dataset.y); gg.style.left=sx+'px'; gg.style.top=sy+'px'; }
  document.getElementById('world').style.opacity=1-pr(t,END,0.35);
  const RB=document.getElementById('robot'); RB.style.left=(t>=END?40:760)+'px'; RB.style.top=(t>=END?790:900)+'px';
  document.getElementById('headbg').style.opacity=1-pr(t,TS('r4',-0.15),0.3);
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
.sun{{width:40px;height:40px;border-radius:8px;display:inline-block;background:#E6E7EB}}
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
const PAN={json.dumps(dict(cam=cam,FX0=FX0,FY0=FY0), ensure_ascii=False)};
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
