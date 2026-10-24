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
CH = ["01 DIE FRAGE", "02 DIE QUELLE", "03 DIE PHYSIK", "04 SOFORT-HILFE", "05 VORBEUGEN"]
B = [
 ("p1", 0, "Plötzlich: null Sicht", "Du steigst ins *Auto,* und kurz darauf siehst du *nichts* mehr.", "staunt"),
 ("p2", 0, "Nicht die Kälte ist schuld", "Schuld ist *nicht* die *Kälte* draußen, sondern das *Wasser,* das du *mitbringst.*", "denkt"),
 ("p3", 1, "Du bringst das Wasser mit", "*Nasse* *Jacke,* nasse *Schuhe,* feuchte *Fußmatten* und dein *Atem.*", None),
 ("p4", 2, "Warme Luft nimmt Wasser auf", "Die *warme* *Luft* im Auto nimmt diese *Feuchtigkeit* auf.", None),
 ("p5", 2, "An der kalten Scheibe wird's nass", "Trifft sie auf die *kalte* *Scheibe,* kühlt sie ab und kann das Wasser *nicht* mehr *halten.*", None),
 ("p6", 2, "An der kalten Scheibe wird's nass", "Es setzt sich als feiner *Film* aufs *Glas.*", None),
 ("p7", 3, "Was hilft sofort?", "Was hilft *sofort?*", "zeigt"),
 ("p8", 3, "Sofort freie Sicht", "*Gebläse* *warm* und *stark* auf die *Frontscheibe.*", None),
 ("p9", 3, "Sofort freie Sicht", "*Klimaanlage* *an,* denn sie *trocknet* die *Luft.*", None),
 ("p10", 3, "Sofort freie Sicht", "Und *Umluft* *aus,* sonst kreist die *feuchte* Luft nur im Auto.", None),
 ("p11", 4, "So beugst du vor", "Vorbeugen geht auch: *Nasse* *Sachen* in den *Kofferraum,* *Fußmatten* *trocknen* und die *Scheibe* innen *sauber* halten.", None),
 ("p12", 4, "Hand oder Klima?", "Und *du?* Wischst du noch mit der *Hand,* oder machst du jetzt die *Klima* an?", "winkt"),
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
 snow='<path d="M24 4v40M7 14l34 20M7 34l34-20M18 7l6 5 6-5M18 41l6-5 6 5M8 21l2 6-6 3M40 21l-2 6 6 3"/>',
 drop='<path d="M24 5C16 17 11 24 11 30a13 13 0 0 0 26 0c0-6-5-13-13-25z"/>',
 jacket='<path d="M17 6l7 6 7-6 9 5 4 14-6 2v17H10V27l-6-2 4-14z"/><path d="M24 12v32"/>',
 shoe='<path d="M6 34V14h10l4 8 14 4c5 1 8 4 8 8v4H6z"/><path d="M6 32h36"/>',
 mat='<rect x="8" y="8" width="32" height="32" rx="4"/><path d="M14 16h20M14 22h20M14 28h20M14 34h20"/>',
 breath='<path d="M6 18h22a6 6 0 1 0-6-6M6 26h32a6 6 0 1 1-6 6M6 34h14"/>',
 fan='<circle cx="24" cy="24" r="4"/><path d="M24 20c-2-8 2-14 8-14 2 6-2 12-8 14zM28 24c8-2 14 2 14 8-6 2-12-2-14-8zM24 28c2 8-2 14-8 14-2-6 2-12 8-14zM20 24c-8 2-14-2-14-8 6-2 12 2 14 8z"/>',
 recirc='<path d="M38 20a15 15 0 0 0-28-4M10 28a15 15 0 0 0 28 4"/><path d="M10 8v8h8M38 40v-8h-8"/>',
 hand='<path d="M16 26V10a3 3 0 0 1 6 0v12V7a3 3 0 0 1 6 0v15V10a3 3 0 0 1 6 0v18c0 9-5 15-13 15-6 0-9-3-12-8l-5-8a3 3 0 0 1 5-3l3 4"/>',
 car='<path d="M4 32v-8l6-10h22l10 10h2v8z"/><circle cx="13" cy="33" r="4"/><circle cx="35" cy="33" r="4"/><path d="M38 24h6"/>',
 shield2='<path d="M6 36L12 12h24l6 24z"/><path d="M17 30l5-10M25 30l5-10"/>',
)
# ---------- sketches ----------
def windshield():
    o = P("M0 238 C220 212 540 212 760 238", 2.6)                 # Armaturenbrett
    o += P("M70 210 L130 20 L630 20 L690 210 Z", 3)               # Frontscheibe
    o += D("M200 120 H560", 1.4) + D("M380 205 L350 125 M380 205 L410 125", 1.8, INK)  # Horizont + Straße
    o += D("M240 120 L240 100 L262 100 L262 120 M500 120 L500 92 L530 92 L530 120", 1.4)
    o += C(200, 300, 74, 2.6) + C(200, 300, 18, 2)                # Lenkrad
    return o
def physics():
    o = ""
    return o
GLASS = "M700 40 L760 600"
def gx(y): return 700 + 60 * (y - 40) / 560
blob = "M70 300 C50 190 190 130 290 180 C370 110 510 160 490 260 C570 320 490 440 370 410 C310 490 130 470 130 410 C50 420 30 350 70 300 Z"
vap = [(130, 300), (190, 240), (250, 330), (300, 260), (360, 210), (420, 290), (200, 380), (330, 360), (440, 360), (110, 360), (270, 200), (390, 400)]
drops = [(110, 9), (170, 12), (240, 8), (300, 11), (370, 9), (430, 13), (500, 8), (550, 11)]

# ---------- scenes ----------
# p1 hook: Frontscheibe beschlägt
stage.append(mm(sketch(windshield(), 760, 260, 80, 20, "p1", -0.8, 1.2) , 80, 470, 920, 300, A("p1", "p2", -0.4)))
stage.append(el('<div style="width:620px;height:190px;clip-path:polygon(0 100%,60px 0,560px 0,620px 100%);'
                'background:radial-gradient(circle,rgba(255,255,255,.95) 2px,transparent 3px) 0 0/22px 22px,radial-gradient(circle,rgba(160,168,182,.55) 3px,transparent 4px) 11px 11px/26px 26px,rgba(222,226,233,.92)"></div>',
                230, 510, f'{A("p1@nichts", "p2")} data-sfx="bubble"'))
stage.append(el('<div class="stamp mono" style="font-size:46px">NULL SICHT</div>', 440, 880, A("p1@mehr", "p2"), 560, "display:flex;justify-content:center"))
# p2 nicht Kälte, sondern Wasser
def lvl(icon, col, small, title, right="", fs=40):
    return f'<div class="row" style="gap:28px;height:100%">{ic(I[icon],76,col)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">{small}</div><div class="rowtitle" style="font-size:{fs}px;margin:0">{title}</div></div>{right}</div>'
X = '<div class="okc" style="margin-left:auto;background:#E5484D;box-shadow:0 0 24px rgba(229,72,77,.4)">✕</div>'
stage.append(card(lvl("snow", "#8A8F99", "NICHT SCHULD", "Kälte draußen", X), 80, 470, 920, 150, "", A("p2@Kälte", "p3")))
stage.append(card(lvl("drop", TQ, "SONDERN", "Wasser von innen"), 80, 640, 920, 150, "activeTQ", A("p2@Wasser", "p3")))
stage.append(el('<div class="stamp mono" style="font-size:40px">DU BRINGST ES MIT</div>', 440, 900, A("p2@mitbringst", "p3"), 560, "display:flex;justify-content:center"))
# p3 vier Quellen
for i, (icn, small, title, anc) in enumerate([("jacket", "NASSE", "Jacke", "Jacke"), ("shoe", "NASSE", "Schuhe", "Schuhe"),
                                              ("mat", "FEUCHTE", "Fußmatten", "Fußmatten"), ("breath", "DEIN", "Atem", "Atem")]):
    x = 80 + (i % 2) * 480; y = 470 + (i // 2) * 250
    inner = f'<div class="col" style="gap:14px;height:100%;justify-content:center">{ic(I[icn],86,PUR)}<div class="mono small grey">{small}</div><div class="rowtitle" style="font-size:40px;margin:0">{title}</div></div>'
    stage.append(card(inner, x, y, 440, 220, "active" if i == 3 else "", f'{A("p3@" + anc, "p4")} data-sfx="plop"'))
stage.append(el('<div class="chip tq mono" style="font-size:30px">= WASSERDAMPF IM AUTO</div>', 80, 1000, f'{A("p3@Atem", "p4", 0.5)} data-sfx="plop"', 920, "display:flex;justify-content:center"))
# p4-p6 Physik-Panel
phys = mm(
    sketch(P(GLASS, 6, INK) + D("M716 40 L776 600", 1.4), 920, 640, 0, 0, "p4", 0, 0.8)
  + sketch(P(blob, 2.4, PUR), 920, 640, 0, 0, "p4@warme", 0, 1.0)
  + sketch("".join(C(x, y, 7, 2.4, TQ) for x, y in vap), 920, 640, 0, 0, "p4@Feuchtigkeit", 0, 0.9)
  + sketch(P("M500 300 C570 300 610 300 676 300 M654 284 L680 300 L654 316", 2.8, INK), 920, 640, 0, 0, "p5@Scheibe", 0, 0.6)
  + sketch("".join(C(gx(y) - 16, y, r, 2.6, TQ) for y, r in drops), 920, 640, 0, 0, "p5@halten", 0, 0.8)
  + sketch(P("M688 50 L746 600", 14, "rgba(25,198,180,.35)"), 920, 640, 0, 0, "p6@Film", 0, 0.7)
  + mk("WARME LUFT", 90, 120, "p4@warme", 0.3, PUR)
  + mk("WASSERDAMPF", 230, 505, "p4@Feuchtigkeit", 0.5, TQ)
  + mk("KALTE SCHEIBE", 560, 600, "p5@kalte", 0.1, INK)
  + mk("FEINER FILM", 430, 30, "p6@Film", 0.2, "#0E8C80"),
  80, 470, 920, 660, A("p4", "p7"))
stage.append(phys)
stage.append(el('<div class="stamp mono" style="font-size:44px;color:#0E8C80;border-color:#19C6B4">KONDENSWASSER</div>', 80, 1150, A("p6@Film", "p7", 0.3), 920, "display:flex;justify-content:center"))
# p7 Frage
stage.append(card('<div class="row" style="gap:30px;height:100%;justify-content:center"><div class="qbig" style="position:static;font-size:150px;line-height:1">?</div><div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">WAS HILFT</div><div class="bignum" style="font-size:96px">sofort</div></div></div>', 80, 470, 920, 300, "", A("p7", "p8")))
# p8-p10 Sofort-Hilfe
OK = lambda anc, y: el('<div class="okc">✓</div>', 870, y + 58, f'{A(anc, "p11")} data-sfx="success"')
stage.append(card(lvl("fan", PUR, "GEBLÄSE", "Warm + stark auf die Scheibe", fs=32), 80, 470, 920, 200, "active", A("p8@Gebläse", "p11")))
stage.append(OK("p8@Frontscheibe", 470))
stage.append(card(lvl("snow", TQ, "KLIMAANLAGE AN", "Trocknet die Luft", fs=34), 80, 700, 920, 200, "activeTQ", A("p9@Klimaanlage", "p11")))
stage.append(OK("p9@trocknet", 700))
stage.append(card(lvl("recirc", RED, "UMLUFT AUS", "Frische Luft rein", fs=34), 80, 930, 920, 200, "active", A("p10@Umluft", "p11")))
stage.append(OK("p10@aus", 930))
stage.append(el('<div class="chip mono" style="font-size:26px;color:#8A8F99;border-color:#8A8F99">SONST KREIST DIE FEUCHTE LUFT</div>', 80, 1160, A("p10@feuchte", "p11"), 920, "display:flex;justify-content:center"))
# p11 Vorbeugen
CB = lambda anc, y: el('<div class="cbox tq">✓</div>', 880, y + 63, f'{A(anc, "p12")} data-sfx="success"')
stage.append(card(lvl("jacket", PUR, "NASSE SACHEN", "Ab in den Kofferraum", fs=34), 80, 470, 920, 190, "", A("p11@Sachen", "p12")))
stage.append(CB("p11@Kofferraum", 470))
stage.append(card(lvl("mat", PUR, "FUSSMATTEN", "Trocknen lassen", fs=34), 80, 690, 920, 190, "", A("p11@Fußmatten", "p12")))
stage.append(CB("p11@trocknen", 690))
stage.append(card(lvl("shield2", TQ, "SCHEIBE INNEN", "Sauber halten", fs=34), 80, 910, 920, 190, "activeTQ", A("p11@Scheibe", "p12")))
stage.append(CB("p11@sauber", 910))
# p12 Frage
stage.append(card(f'<div class="row" style="gap:60px;height:100%;justify-content:center">{ic(I["hand"],120,"#8A8F99")}<div class="bignum" style="font-size:72px">oder</div>{ic(I["snow"],120,TQ)}</div>', 80, 470, 920, 300, "activeTQ", A("p12", "end")))
stage.append(el('<div class="chip mono" style="font-size:30px">MIT DER HAND WISCHEN?</div>', 440, 860, f'{A("p12@Hand", "end")} data-sfx="plop"', 560, "display:flex;justify-content:center"))
stage.append(el('<div class="chip pu mono" style="font-size:30px">ODER KLIMA AN?</div>', 440, 970, f'{A("p12@Klima", "end")} data-sfx="plop"', 560, "display:flex;justify-content:center"))

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
