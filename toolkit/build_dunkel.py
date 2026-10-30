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
CH = ["01 DIE FRAGE", "02 DIE ACHSE", "03 SOMMER", "04 WINTER", "05 DIE UHR", "06 AUSBLICK", "07 UND DU?"]
B = [
 ("p1", 0, "Kaum Feierabend – schon dunkel", "Kaum *Feierabend,* schon *dunkel.*", None),
 ("p2", 0, "Warum so früh Nacht?", "Warum wird es im *November* so früh *Nacht?*", None),
 ("p3", 1, "Die Erdachse ist schief", "Schuld ist die *Erde* *selbst:* Ihre *Achse* steht *schief.*", None),
 ("p4", 1, "Einmal im Jahr um die Sonne", "Und diese *Schräglage* *bleibt,* während die *Erde* *einmal* im *Jahr* um die *Sonne* *kreist.*", None),
 ("p5", 2, "Sommer: zur Sonne hin", "Im *Sommer* neigt sich unser *Teil* der *Erde* zur *Sonne* *hin:*", None),
 ("p6", 2, "Hoch und lang", "Sie steht *hoch* und zieht einen *langen* *Bogen* über den *Himmel.*", None),
 ("p7", 3, "Winter: von der Sonne weg", "Im *Winter* neigt er sich *weg:*", None),
 ("p8", 3, "Tief und kurz", "Die *Sonne* steht *tief* und ist *schnell* wieder *untergegangen.*", None),
 ("p9", 3, "7,5 statt 17 Stunden", "Am *kürzesten* *Tag,* dem *einundzwanzigsten* *Dezember,* gibt es in *Berlin* nur gut *siebeneinhalb* *Stunden* *Tageslicht,* im *Juni* fast *siebzehn.*", None),
 ("p10", 4, "Dazu: Zeitumstellung", "Dazu kommt die *Zeitumstellung:* Seit *Ende* *Oktober* sind die *Uhren* eine *Stunde* *zurückgestellt.*", None),
 ("p11", 4, "Eine Stunde früher dunkel", "Deshalb geht die *Sonne* laut *Uhr* noch eine *Stunde* *früher* *unter.*", None),
 ("p12", 5, "Bald wird's wieder heller", "Die *gute* *Nachricht:* Kurz vor *Weihnachten* *dreht* sich das, dann werden die *Tage* wieder *länger.*", None),
 ("p13", 6, "Freust du dich?", "*Freust* du dich schon auf den *Sommer,* *ja* oder *nein?*", None),
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


# ================= Bühne "Erde um die Sonne + Blick aus Deutschland" (durchgehend) =================
import math
I.update(
 sun='<circle cx="24" cy="24" r="8"/><path d="M24 6v5M24 37v5M6 24h5M37 24h5M11 11l3.5 3.5M33.5 33.5L37 37M11 37l3.5-3.5M33.5 14.5L37 11"/>',
 moon='<path d="M33 30A14 14 0 0 1 19 9a15 15 0 1 0 14 21z"/>',
 clock='<circle cx="24" cy="24" r="18"/><path d="M24 13v11l7 5"/>',
)
CENTER = "display:flex;justify-content:center"
SUNC = "#FFC23D"
CX, CY, RX, RY, ER = 460, 222, 340, 112, 40          # Umlaufbahn (Panel-Koordinaten)
HZ = 702                                             # Horizont im Himmelsausschnitt
# --- Weltraum-Ebene ---
earth = (f'<g id="earth"><g id="etilt" transform="rotate(23.4)">'
         f'<circle r="{ER}" fill="#E3F7F4" stroke="{INK}" stroke-width="2.4"/>'
         f'<path id="ncap" d="M{-ER} 0 A{ER} {ER} 0 0 1 {ER} 0 Z" fill="{PUR}" opacity="0"/>'
         f'<path d="M{-ER} 0 H{ER}" stroke="{INK2}" stroke-width="1.6" stroke-dasharray="4 4"/>'
         f'<path d="M-27 -18 q12 -6 22 2 q8 6 18 -2 M-30 14 q14 4 26 -4 q10 -6 22 2" stroke="#7AA9A3" stroke-width="2" fill="none" stroke-linecap="round"/>'
         f'<line x1="0" y1="-66" x2="0" y2="66" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
         f'<text x="7" y="-58" font-family="JBM" font-weight="700" font-size="16" fill="{INK}">N</text>'
         f'<circle id="de" cx="11" cy="-31" r="6.5" fill="{PUR}" stroke="#fff" stroke-width="2.4"/></g>'
         f'<path id="night" d="M0 {-ER} A{ER} {ER} 0 0 0 0 {ER} Z" fill="#141634" opacity=".5"/></g>')
sun = (f'<g id="sung"><circle cx="{CX}" cy="{CY}" r="70" fill="{SUNC}" opacity=".18"/><circle cx="{CX}" cy="{CY}" r="54" fill="{SUNC}" opacity=".25"/>'
       f'<circle id="sunc" cx="{CX}" cy="{CY}" r="40" fill="{SUNC}" stroke="#E8A21A" stroke-width="2"/></g>')
angle = (f'<g id="ang" style="opacity:0"><line x1="0" y1="-78" x2="0" y2="0" stroke="{INK2}" stroke-width="2" stroke-dasharray="5 5"/>'
         f'<path d="M0 -60 A60 60 0 0 1 23.8 -55.1" stroke="{RED}" stroke-width="3" fill="none"/></g>')
space = (f'<svg width="920" height="440" style="position:absolute;left:0;top:0;overflow:visible"><g id="space">'
         f'<ellipse cx="{CX}" cy="{CY}" rx="{RX}" ry="{RY}" fill="none" stroke="{INK2}" stroke-width="2" stroke-dasharray="7 7"/>'
         f'{sun}{earth}<g id="angw">{angle}</g></g></svg>')
# --- Himmelsausschnitt "Blick aus Deutschland" ---
stars = "".join(f'<div class="star" style="left:{(j * 137) % 880 + 20}px;top:{455 + (j * 53) % 200}px;width:{3 + j % 3}px;height:{3 + j % 3}px"></div>' for j in range(24))
houses = ""
for hx, hw, hh in [(30, 90, 70), (130, 70, 100), (215, 100, 60), (650, 80, 90), (745, 110, 66), (865, 60, 84)]:
    houses += (f'<path d="M{hx} {HZ} V{HZ - hh} L{hx + hw / 2} {HZ - hh - 34} L{hx + hw} {HZ - hh} V{HZ} Z" fill="#E9EBF0" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    for wx in range(hx + 14, hx + hw - 22, 30):
        for wy in range(HZ - hh + 14, HZ - 26, 30):
            houses += f'<rect class="win" x="{wx}" y="{wy}" width="16" height="18" rx="2" fill="#C9CCD3"/>'
sky = (f'<div id="skyb" style="position:absolute;left:0;top:440px;width:920px;height:{HZ - 440}px"></div>{stars}'
       f'<svg width="920" height="760" style="position:absolute;left:0;top:0;overflow:visible">'
       f'<line x1="0" y1="440" x2="920" y2="440" stroke="{INK2}" stroke-width="1.6" stroke-dasharray="6 6"/>'
       f'<path id="arcF" d="" fill="none" stroke="{INK2}" stroke-width="2.2" stroke-dasharray="3 9" stroke-linecap="round"/>'
       f'<path id="arcT" d="" fill="none" stroke="{PUR}" stroke-width="5" stroke-linecap="round"/>'
       f'<g id="ssun"><circle r="34" fill="{SUNC}" opacity=".25"/><circle r="22" fill="{SUNC}" stroke="#E8A21A" stroke-width="2"/></g>'
       f'<rect x="0" y="{HZ}" width="920" height="{760 - HZ}" fill="#F1F2F5"/>{houses}'
       f'<line x1="0" y1="{HZ}" x2="920" y2="{HZ}" stroke="{INK}" stroke-width="2.6"/></svg>'
       f'<div id="smoon" style="position:absolute;left:770px;top:470px;opacity:0">{ic(I["moon"], 62, "#FFFFFF", 3)}</div>')
chips = (el(f'<div class="chip mono" style="font-size:19px;padding:7px 12px">BLICK AUS DEUTSCHLAND</div>', 18, 456, A("p1", "p13", -0.6) + ' data-sfx="none"')
         + f'<div class="el" {A("p1", "end", -0.6)} data-sfx="none" style="right:18px;top:18px"><div class="chip mono" style="font-size:22px;padding:8px 14px"><span id="mon">NOVEMBER</span></div></div>'
         + f'<div id="clk" class="chip mono" style="position:absolute;right:18px;top:456px;font-size:30px;padding:8px 16px;font-weight:700">16:00</div>'
         + f'<div id="dl" class="chip mono" style="position:absolute;left:18px;top:512px;font-size:20px;padding:7px 12px;opacity:0">TAGESLICHT ≈ 9 STD</div>'
         + el('<div class="chip mono" style="font-size:16px;padding:5px 9px;color:#8A8F99;border-color:#C9CCD3">SCHEMATISCH · NICHT MASSSTABSGETREU</div>', 18, 18, A("p3", "p9", 0) + ' data-sfx="none"'))
# Labels, die der Erde folgen
def ea(text, dx, dy, i, o, col=PUR, d=0.1):
    return (f'<div class="ea" data-dx="{dx}" data-dy="{dy}" style="position:absolute;left:0;top:0"><div class="el mk" {A(i, o, d)} style="left:0;top:-16px;gap:8px">'
            f'<span class="mono lab" style="color:{col};border-color:{col}">{text}</span></div></div>')
follow = (ea("ERDE", 50, 40, "p2@November", "p3", INK, 0.2)
          + ea("ACHSE SCHIEF: 23,4°", 26, -112, "p3@Achse", "p4", RED, 0.1)
          + ea("NORDEN ZUR SONNE", -50, -112, "p5@Sonne", "p7", "#0E8C80", 0)
          + ea("NORDEN VON DER SONNE WEG", -330, -112, "p7@weg", "p9", PUR, 0))
sunlab = el(f'<span class="mono lab" style="color:#B7770A;border-color:#E8A21A">SONNE</span>', CX - 50, CY + 78, A("p2@November", "p3", 0.4) + ' data-sfx="marker"')
keep = el(f'<div class="chip mono" style="font-size:20px;padding:7px 12px;border-color:{RED};color:{RED}">SCHRÄGLAGE BLEIBT GLEICH</div>', 18, 70, A("p4@bleibt", "p5", 0) + ' data-sfx="marker"')
arcl1 = el(f'<span class="mono lab" style="color:#0E8C80;border-color:#19C6B4">HOCH &amp; LANGER BOGEN</span>', 330, 470, A("p6@langen", "p7", 0) + ' data-sfx="marker"')
arcl2 = el(f'<span class="mono lab" style="color:{PUR};border-color:{PUR}">TIEF &amp; KURZ</span>', 380, 600, A("p8@tief", "p9", 0) + ' data-sfx="marker"')
stage.append(mm(space + sky + follow + sunlab + keep + arcl1 + arcl2 + chips, 80, 460, 920, 760, A("p1", "end", -0.6)))

# ---- Overlays ----
stage.append(el('<div class="stamp mono" style="font-size:50px">SCHON DUNKEL?!</div>', 80, 1010, A("p1@dunkel", "p2@November", -0.1), 920, CENTER))
# p9: Tageslicht Dezember vs. Juni
def hb(lbl, hours, col, anchor, d):
    return (f'<div class="col" style="align-items:flex-start;gap:8px;width:100%"><div class="row" style="justify-content:space-between;width:100%"><span class="mono" style="font-size:24px;font-weight:700">{lbl}</span>'
            f'<span class="bignum" style="font-size:44px;letter-spacing:-1px">≈ {cnt(hours, anchor, 1 if hours % 1 else 0, d)} Std.</span></div>'
            f'<div class="hbar"><div class="gbar2" data-ga="{anchor}" data-gd="{d}" style="width:{hours / 24 * 100:.1f}%;background:{col}"></div></div></div>')
scale = '<div class="row mono" style="justify-content:space-between;width:790px;font-size:17px;color:#8A8F99"><span>0 UHR</span><span>6</span><span>12</span><span>18</span><span>24</span></div>'
stage.append(card(f'<div class="col" style="gap:20px;align-items:flex-start;height:100%;justify-content:center"><div class="mono small grey">TAGESLICHT IN BERLIN</div>'
                  + hb("21. DEZEMBER", 7.5, PUR, "p9@siebeneinhalb", 0) + hb("21. JUNI", 17, TQ, "p9@Juni", 0) + scale + '</div>',
                  110, 880, 860, 330, "active", A("p9@kürzesten", "p10", 0)))
# p10/p11: Zeitumstellung
clockface = (f'<svg width="120" height="120" viewBox="-60 -60 120 120"><circle r="54" fill="#fff" stroke="{INK}" stroke-width="4"/>'
             + "".join(f'<line x1="0" y1="-46" x2="0" y2="-40" stroke="{INK}" stroke-width="3" transform="rotate({k * 30})"/>' for k in range(12))
             + f'<line class="hh" data-ra="p10@Uhren" x1="0" y1="0" x2="0" y2="-28" stroke="{INK}" stroke-width="6" stroke-linecap="round" transform="rotate(165)"/>'
             + f'<line class="mh" data-ra="p10@Uhren" x1="0" y1="0" x2="0" y2="-42" stroke="{PUR}" stroke-width="4" stroke-linecap="round" transform="rotate(324)"/>'
             + f'<circle r="5" fill="{INK}"/></svg>')
row = lambda a, b_, c, col: (f'<div class="row" style="justify-content:space-between;width:100%;padding:10px 18px;border-radius:12px;background:{col}">'
                             f'<span class="mono" style="font-size:22px;font-weight:700">{a}<br><span style="font-size:18px;color:#5D616B">{b_}</span></span>'
                             f'<span class="bignum" style="font-size:52px;letter-spacing:-1px">{c}</span></div>')
stage.append(card(f'<div class="row" style="gap:26px;height:100%;align-items:center"><div class="spinclock">{clockface}</div>'
                  f'<div class="col" style="gap:12px;flex:1;align-items:flex-start"><div class="mono small grey">SONNENUNTERGANG IN BERLIN</div>'
                  f'{row("SA 24.10.", "SOMMERZEIT", "17:54", "#F0F1F4")}'
                  f'<div class="el2" {A("p10@zurückgestellt", None, 0)} data-sfx="glass" style="width:100%">{row("SO 25.10.", "WINTERZEIT", "16:52", "rgba(123,63,228,.12)")}</div></div></div>',
                  110, 880, 860, 330, "active", A("p10@Zeitumstellung", "p12", 0)))
stage.append(el('<div class="stamp mono" style="font-size:46px;color:#7B3FE4;border-color:#7B3FE4">1 STUNDE FRÜHER DUNKEL</div>', 80, 770, A("p11@früher", "p12", -0.1), 920, CENTER))
# p12: Wende
stage.append(el(f'<div class="chip tq mono row" style="font-size:26px;gap:12px;padding:12px 20px;background:rgba(255,255,255,.95)"><span class="okc" style="width:48px;height:48px;font-size:28px">✓</span>AB 22. DEZEMBER: TAGE WERDEN LÄNGER</div>',
                80, 1120, A("p12@länger", "p13", -0.2), 920, CENTER))
# p13: Frage
stage.append(card(f'<div class="row" style="gap:30px;height:100%;justify-content:center">{ic(I["sun"], 120, "#E8A21A", 3.2)}<div class="qbig" style="position:static;font-size:150px;line-height:1">?</div></div>', 260, 520, 560, 240, "active", A("p13@Freust", "end")))
stage.append(el('<div class="row" style="gap:24px;justify-content:center"><div class="chip tq mono" style="font-size:40px;padding:14px 34px">JA</div><div class="chip mono" style="font-size:40px;padding:14px 34px">NEIN</div></div>', 260, 790, f'{A("p13@ja", "end")} data-sfx="plop"', 560))
stage.append(el('<div class="chip pu mono" style="font-size:22px">SCHREIB\'S IN DIE KOMMENTARE</div>', 260, 900, f'{A("p13@nein", "end", 0.2)} data-sfx="plop"', 560, CENTER))

# ---- Keyframes (Anker, Offset, Wert) ----
PHI0 = 49   # 1. November (Grad vor der Wintersonnenwende)
KF = dict(
 phi=[("p1", 0, PHI0), ("p4@einmal", -0.2, PHI0), ("p4@kreist", 0.5, PHI0 - 360), ("p5", 0, PHI0 - 360), ("p5@hin", 0, -540),
      ("p7", 0, -540), ("p7@weg", 0.1, -720), ("p12@Weihnachten", 0, -720), ("p12@länger", 0.6, -728)],
 z=[("p1", 0, 1), ("p3", 0, 1), ("p3@Achse", 0.2, 2.1), ("p4", -0.1, 2.1), ("p4@einmal", -0.2, 1)],
 u=[("p1", 0, 0.96), ("p1@dunkel", 0.3, 1.1), ("p2@Nacht", 0, 1.13), ("p3", -0.1, 1.13), ("p3@Schuld", 0.4, 0.5), ("p5", 0, 0.5),
    ("p6", -0.15, -0.02), ("p6@Himmel", 0.4, 1.0), ("p7", 0, 1.0), ("p7@Winter", 0.2, 0.5), ("p8", -0.15, -0.02), ("p8@untergegangen", 0.3, 1.1),
    ("p9", 0, 1.1), ("p12", 0, 1.1), ("p12@gute", 0.3, 0.5)],
)
# Uhr / Tageslicht-Chip sichtbar (Anker-Paare)
VIS = dict(clk=[("p1", -1, "p2@Nacht", 0.4), ("p6", -0.2, "p7", 0), ("p8", -0.2, "p9", 0)],
           dl=[("p5@hin", 0, "p9", 0), ("p12@gute", 0, "p13", 0)], ncap=[("p5@Sonne", -0.1, "p9", 0)], ang=[("p3@Achse", 0.2, "p4", 0)])
PANJS = dict(kf=KF, vis=VIS, geo=dict(cx=CX, cy=CY, rx=RX, ry=RY, hz=HZ))


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
.ea{{width:0;height:0}} .ea .el{{white-space:nowrap}}
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
 // ---- Bühne: Erde um die Sonne + Himmel über Deutschland ----
 {{
  const TS=(a,o)=>(S[a]??(console.log('missing '+a),0))+o;
  const KF=(name)=>PAN.kf[name].map(k=>({{t:TS(k[0],k[1]),v:k[2]}}));
  if(!window._kf) window._kf={{phi:KF('phi'),z:KF('z'),u:KF('u')}};
  const val=(ks,tt)=>{{ if(tt<=ks[0].t) return ks[0].v; for(let i=0;i<ks.length-1;i++){{ const a=ks[i],c=ks[i+1]; if(tt>=a.t&&tt<c.t){{ const q=(tt-a.t)/Math.max(1e-6,c.t-a.t), e=q*q*(3-2*q); return a.v+(c.v-a.v)*e; }} }} return ks[ks.length-1].v; }};
  const vis=(id,fade=0.25)=>{{ let o=0; for(const [a,ao,b,bo] of PAN.vis[id]){{ const t0=TS(a,ao), t1=TS(b,bo); o=Math.max(o,pr(t,t0,fade)*(1-pr(t,t1-0.05,fade))); }} return o; }};
  const G=PAN.geo, rad=Math.PI/180;
  const phi=val(_kf.phi,t), z=val(_kf.z,t), u=val(_kf.u,t);
  const ex=G.cx+G.rx*Math.cos(phi*rad), ey=G.cy+G.ry*Math.sin(phi*rad);
  // Kamera (Zoom auf die Erde)
  const w=(z-1)/1.1, fx=G.cx+(ex-G.cx)*w, fy=G.cy+(ey-G.cy)*w;
  const SP=document.getElementById('space'); SP.setAttribute('transform',`translate(${{G.cx}},${{G.cy}}) scale(${{z}}) translate(${{-fx}},${{-fy}})`);
  const pj=(x,y)=>[G.cx+(x-fx)*z, G.cy+(y-fy)*z];
  const E=document.getElementById('earth'); E.setAttribute('transform',`translate(${{ex.toFixed(1)}},${{ey.toFixed(1)}})`);
  const sg=document.getElementById('sung'); if(Math.sin(phi*rad)<0) SP.insertBefore(E,sg); else SP.insertBefore(E,sg.nextSibling);
  const sa=Math.atan2(G.cy-ey,G.cx-ex)/rad;
  const N=document.getElementById('night'); N.setAttribute('transform',`rotate(${{sa.toFixed(1)}})`);
  N.setAttribute('opacity',(0.42+0.2*Math.max(0,Math.sin(phi*rad))).toFixed(2));
  document.getElementById('ncap').setAttribute('opacity',(0.32*vis('ncap')).toFixed(2));
  const AW=document.getElementById('angw'); AW.setAttribute('transform',`translate(${{ex.toFixed(1)}},${{ey.toFixed(1)}})`); document.getElementById('ang').style.opacity=vis('ang');
  for(const a of document.querySelectorAll('.ea')){{ const p=pj(ex,ey); a.style.left=(p[0]+(+a.dataset.dx))+'px'; a.style.top=(p[1]+(+a.dataset.dy))+'px'; }}
  // Monat aus Bahnposition (0° = 21. Dez., je 30° ein Monat)
  const MON=['DEZEMBER','JANUAR','FEBRUAR','MÄRZ','APRIL','MAI','JUNI','JULI','AUGUST','SEPTEMBER','OKTOBER','NOVEMBER'];
  const mf=((-phi)/30%12+12+0.67)%12; document.getElementById('mon').textContent=MON[Math.floor(mf)%12];
  // Jahreszeit -> Sonnendeklination, Tageslänge, Mittagshöhe (Berlin 52,5° N)
  const dec=-23.44*Math.cos(phi*rad), lat=52.5;
  const H=2*Math.acos(Math.max(-1,Math.min(1,-Math.tan(lat*rad)*Math.tan(dec*rad))))/rad/15+0.25;
  const alt=90-lat+dec;
  const AWd=40+22*H, AH=Math.max(30,alt*3.4), cx=460;
  let d='M'+(cx-AWd).toFixed(1)+' '+G.hz; for(let k=1;k<=40;k++){{ const q=k/40; d+=' L'+(cx-AWd+2*AWd*q).toFixed(1)+' '+(G.hz-AH*Math.sin(Math.PI*q)).toFixed(1); }}
  document.getElementById('arcF').setAttribute('d',d);
  const uc=Math.max(0,Math.min(1,u)); let dt='M'+(cx-AWd).toFixed(1)+' '+G.hz; const nk=Math.max(1,Math.round(40*uc));
  if(u>0){{ for(let k=1;k<=nk;k++){{ const q=uc*k/nk; dt+=' L'+(cx-AWd+2*AWd*q).toFixed(1)+' '+(G.hz-AH*Math.sin(Math.PI*q)).toFixed(1); }} }} else dt='';
  const showT=vis('dl',0.3)>0||(t>S['p6']-0.2&&t<S['p9']);
  document.getElementById('arcT').setAttribute('d',showT?dt:'');
  // Sonne auf dem Bogen (unter dem Horizont: verschwindet)
  const uq=u, sx=cx-AWd+2*AWd*Math.max(-0.08,Math.min(1.08,uq)), sy=G.hz-AH*Math.sin(Math.PI*uq);
  const SS=document.getElementById('ssun'); SS.setAttribute('transform',`translate(${{sx.toFixed(1)}},${{Math.min(G.hz+40,sy).toFixed(1)}})`);
  // Dunkelheit
  const night=cl(Math.max((uq-0.97)/0.12,(0.03-uq)/0.12),0,1);
  const r_=Math.round(214+(20-214)*night), g_=Math.round(236+(22-236)*night), b_=Math.round(250+(52-250)*night);
  document.getElementById('skyb').style.background=`linear-gradient(rgba(${{r_}},${{g_}},${{b_}},${{0.55+0.4*night}}),rgba(${{r_}},${{g_}},${{b_}},${{0.25+0.6*night}}))`;
  document.querySelectorAll('.star').forEach((s,i)=>s.style.opacity=night*(0.55+0.45*Math.sin(t*3+i*1.7)));
  document.getElementById('smoon').style.opacity=night;
  document.querySelectorAll('.win').forEach((wn,i)=>wn.setAttribute('fill',night>0.4&&((i*7)%5)!==0?'#FFD45E':'#C9CCD3'));
  // Uhr (MEZ, im Sommer MESZ) aus Tagesphase
  const summer=Math.cos(phi*rad)<-0.25; let mins=12*60+(uq-0.5)*H*60+(summer?60:0)-10;
  mins=((Math.round(mins)%1440)+1440)%1440; const CK=document.getElementById('clk');
  CK.textContent=String(Math.floor(mins/60)).padStart(2,'0')+':'+String(mins%60).padStart(2,'0'); CK.style.opacity=vis('clk',0.2);
  const DL=document.getElementById('dl'); DL.style.opacity=vis('dl'); DL.textContent='TAGESLICHT ≈ '+H.toFixed(1).replace('.',',')+' STD';
  // Zeiger der Uhr (Zeitumstellung)
  for(const e of document.querySelectorAll('.hh,.mh')){{ const q=ease(pr(t,S[e.dataset.ra]+0.2,1.1)); const base=e.classList.contains('hh')?165:324; const dd=e.classList.contains('hh')?-30:-360; e.setAttribute('transform',`rotate(${{base+dd*q}})`); }}
  for(const e of document.querySelectorAll('.gbar2')) e.style.transform=`scaleX(${{ease(pr(t,S[e.dataset.ga]+(+e.dataset.gd||0),0.9))}})`;
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
