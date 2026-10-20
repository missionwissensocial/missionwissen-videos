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
CH = ["01 DIE FRIST", "02 DIE REGEL", "03 DAS RISIKO", "04 SO GEHT'S", "05 UND DU?"]
B = [
 ("p1", 0, "Stichtag 30. November", "Bis zum *dreißigsten* *November* entscheidest du, ob du nächstes Jahr *zu* *viel* für dein *Auto* zahlst.", "staunt"),
 ("p2", 0, "Warum gerade dieser Tag?", "Warum gerade dieser *Tag?*", "denkt"),
 ("p3", 1, "Vertrag = Kalenderjahr", "Bei vielen *Autoversicherungen* läuft der Vertrag genau ein *Kalenderjahr,* also bis *Silvester.*", None),
 ("p4", 1, "Ein Monat Kündigungsfrist", "Kündigen kannst du mit *einem* *Monat* *Frist.*", None),
 ("p5", 1, "Eingang zählt – nicht Absenden", "Und wichtig: Die Kündigung muss bis dahin bei der Versicherung *angekommen* sein.", None),
 ("p6", 1, "Eingang zählt – nicht Absenden", "*Abschicken* am letzten Tag *reicht* *nicht.*", None),
 ("p7", 2, "Verpasst? Noch ein Jahr.", "Verpasst du den Termin, bleibst du automatisch ein *weiteres* *Jahr* im *alten* *Tarif.*", None),
 ("p8", 2, "Oft Hunderte Euro Unterschied", "Dabei liegen zwischen *teuren* und *günstigen* Tarifen oft *mehrere* *hundert* *Euro.*", None),
 ("p9", 3, "Erst neu, dann kündigen", "Der sichere Weg: Erst den *neuen* *Vertrag* abschließen und die *Zusage* abwarten.", None),
 ("p10", 3, "Erst neu, dann kündigen", "Dann *kündigst* du die *alte* Versicherung.", None),
 ("p11", 4, "Und du?", "Und du, hast du deinen Tarif dieses Jahr schon *verglichen,* oder zahlst du einfach *weiter?*", "winkt"),
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
 car='<path d="M6 30v-6l5-10h26l5 10v6z"/><circle cx="14" cy="32" r="4"/><circle cx="34" cy="32" r="4"/><path d="M12 16h24"/>',
 shield='<path d="M24 5l16 6v12c0 10-7 17-16 20C15 40 8 33 8 23V11z"/><path d="M17 24l5 5 9-10"/>',
 cal='<rect x="6" y="9" width="36" height="33" rx="4"/><path d="M6 18h36M15 4v9M33 4v9"/>',
 send='<path d="M5 24L43 6 33 42 22 28z"/><path d="M22 28L43 6"/>',
)
# ---------- sketches ----------
MON = ["J","F","M","A","M","J","J","A","S","O","N","D"]
def year_bar():
    o = ""
    for i, m in enumerate(MON):
        x = 20 + i * 60
        hl = i == 11
        o += R(x, 120, 52, 80, 6, 2.6 if hl else 2.0, PUR if hl else INK) + TX(x + 26, 172, m, 26, PUR if hl else INK, "JBM", 700, "middle")
    o += mesh("M20 120 h712 v80 h-712 Z", 760, 320)
    o += P("M20 240 v20 h712 v-20", 2.4, PUR) + TX(376, 300, "1 VERSICHERUNGSJAHR", 22, PUR, "JBM", 700, "middle")
    o += TX(20, 90, "1.1.", 22, INK2) + TX(732, 90, "31.12.", 22, PUR, "JBM", 700, "end")
    return o
def letter_inbox():
    env_ = "M40 130 h220 v150 h-220 Z"
    o = mesh(env_, 760, 360) + P(env_) + P("M40 130 L150 210 L260 130")
    o += P("M290 205 C350 180 400 180 450 200", 2.4, PUR) + P("M438 186 L452 202 L432 210", 2.4, PUR)
    bld = "M480 120 L610 50 L740 120 V320 H480 Z"
    o += P(bld) + R(530, 180, 160, 40, 6, 2.6, PUR) + D("M550 200 H670", 2, PUR)
    o += R(520, 250, 40, 70, 4, 1.6) + R(660, 250, 40, 70, 4, 1.6) + TX(610, 110, "VERSICHERUNG", 18, INK, "JBM", 700, "middle")
    return o

# ---------- scenes ----------
# p1 hook: Stichtag
stage.append(card(f'<div class="col" style="gap:8px;height:100%;justify-content:center"><div class="mono small grey">KÜNDIGEN BIS ZUM</div><div class="huge" style="font-size:190px">30.11.</div><div class="mono small grey">AUTOVERSICHERUNG · STICHTAG</div></div>', 80, 470, 920, 330, "active", A("p1","p2")))
stage.append(el(f'<div class="chip pu mono" style="font-size:30px;display:flex;align-items:center;gap:14px">{ic(I["car"],44,PUR)}DEIN AUTO</div>', 440, 860, f'{A("p1@Auto","p2")} data-sfx="plop"', 560, "display:flex;justify-content:center"))
stage.append(el('<div class="stamp mono" style="font-size:44px">ZU VIEL ZAHLEN?</div>', 440, 1000, A("p1@viel","p2"), 560, "display:flex;justify-content:center"))
# p2 question
stage.append(card('<div class="row" style="gap:30px;height:100%;justify-content:center"><div class="qbig" style="position:static;font-size:150px;line-height:1">?</div><div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">WARUM GENAU</div><div class="bignum" style="font-size:96px">30.11.</div></div></div>', 80, 470, 920, 300, "", A("p2","p3")))
# p3 calendar year
stage.append(mm(sketch(year_bar(), 760, 320, 80, 50, "p3", 0, 1.6, 1.0) + mk("VERTRAG", 40, 30, "p3@Autoversicherungen", 0, PUR), 80, 470, 920, 420, A("p3","p4")))
stage.append(el('<div class="chip pu mono" style="font-size:30px">LÄUFT BIS SILVESTER · 31.12.</div>', 80, 940, A("p3@Silvester","p4"), 920, "display:flex;justify-content:center"))
# p4 one month notice
stage.append(card(f'<div class="col" style="gap:10px;height:100%;justify-content:center"><div class="mono small grey">KÜNDIGUNGSFRIST</div><div class="bignum" style="font-size:120px">{cnt(1,"p4@einem",0,0)} Monat</div></div>', 80, 470, 920, 330, "active", A("p4","p5")))
stage.append(el('<div class="row" style="gap:22px;justify-content:center"><div class="chip mono" style="font-size:34px">30.11.</div><div class="mono" style="font-size:44px;color:#7B3FE4">⟶</div><div class="chip mono" style="font-size:34px">31.12.</div></div>', 80, 860, A("p4@Frist","p5"), 920, "display:flex;justify-content:center"))
# p5/p6 arrival counts
stage.append(mm(sketch(letter_inbox(), 760, 360, 80, 30, "p5", 0, 1.6, 1.0) + mk("EINGANG ZÄHLT", 560, 380, "p5@angekommen", 0, PUR), 80, 470, 920, 440, A("p5","p7")))
stage.append(card(f'<div class="row" style="gap:28px;height:100%">{ic(I["cal"],72,TQ)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">BIS 30.11.</div><div class="rowtitle" style="font-size:38px;margin:0">bei der Versicherung da</div></div><div class="okc" style="margin-left:auto">✓</div></div>', 80, 950, 920, 200, "activeTQ", A("p5@angekommen","p6")))
stage.append(card(f'<div class="row" style="gap:28px;height:100%">{ic(I["send"],72,"#8A8F99")}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">AM 30.11.</div><div class="rowtitle" style="font-size:38px;margin:0">erst abgeschickt</div></div></div>', 80, 950, 920, 200, "", A("p6","p7")))
stage.append(el('<div class="stamp mono" style="font-size:46px">ZU SPÄT</div>', 660, 990, A("p6@reicht","p7"), 320, "display:flex;justify-content:center"))
# p7 auto-renewal
stage.append(card(f'<div class="col" style="gap:10px;height:100%;justify-content:center"><div class="mono small grey">TERMIN VERPASST</div><div class="bignum" style="font-size:130px">+{cnt(1,"p7@weiteres",0,0)} Jahr</div><div class="mono small grey">IM ALTEN TARIF</div></div>', 80, 470, 920, 380, "", A("p7","p8")))
stage.append(el('<div class="stamp mono" style="font-size:42px">AUTOMATISCH VERLÄNGERT</div>', 80, 900, A("p7@Tarif","p8"), 920, "display:flex;justify-content:center"))
# p8 price gap
for i, (lab, h, col, key, cls) in enumerate([("TEUER", 330, "#8A8F99", "p8@teuren", ""), ("GÜNSTIG", 150, TQ, "p8@günstigen", "activeTQ")]):
    stage.append(card(f'<div class="col" style="height:100%;justify-content:flex-end;gap:18px"><div style="width:150px;height:{h}px;border-radius:14px;background:{col};opacity:.85"></div><div class="mono" style="font-size:30px">{lab}</div></div>', 80 + i * 470, 470, 450, 500, cls, A(key, "p9")))
stage.append(el('<div class="chip pu mono" style="font-size:30px">OFT MEHRERE 100 € UNTERSCHIED</div>', 80, 1010, A("p8@hundert","p9"), 920, "display:flex;justify-content:center"))
stage.append(el('<div class="mono small grey">SCHEMATISCH</div>', 80, 1100, f'{A("p8@hundert","p9",0.3)} data-sfx="none"', 920, "display:flex;justify-content:center"))
# p9/p10 order
stage.append(card(f'<div class="row" style="gap:28px;height:100%">{ic(I["shield"],80,TQ)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">ZUERST</div><div class="rowtitle" style="font-size:38px;margin:0">Neuen Vertrag abschließen</div></div></div>', 80, 470, 920, 210, "activeTQ", A("p9@neuen","p11")))
stage.append(el('<div class="chip tq mono" style="font-size:30px">ZUSAGE ABWARTEN ✓</div>', 80, 720, A("p9@Zusage","p11"), 920, "display:flex;justify-content:center"))
stage.append(el('<div class="mono" style="font-size:64px;color:#7B3FE4">↓</div>', 80, 810, f'{A("p10","p11")} data-sfx="none"', 920, "display:flex;justify-content:center"))
stage.append(card(f'<div class="row" style="gap:28px;height:100%">{ic(I["mail"],80,PUR)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">DANACH</div><div class="rowtitle" style="font-size:38px;margin:0">Alte Versicherung kündigen</div></div></div>', 80, 920, 920, 210, "active", A("p10@kündigst","p11")))
# p11 question
stage.append(card('<div class="col" style="gap:18px;height:100%;justify-content:center"><div class="mono small grey">DEIN TARIF 2027</div><div class="bignum" style="font-size:66px;letter-spacing:-2px;text-align:center">Schon<br>verglichen?</div></div>', 80, 470, 920, 330, "activeTQ", A("p11","end")))
stage.append(el('<div class="chip tq mono" style="font-size:30px">JA, GEWECHSELT ✓</div>', 440, 860, f'{A("p11@verglichen","end")} data-sfx="plop"', 560, "display:flex;justify-content:center"))
stage.append(el('<div class="chip mono" style="font-size:30px">NEIN, ZAHLE WEITER</div>', 440, 970, f'{A("p11@weiter","end")} data-sfx="plop"', 560, "display:flex;justify-content:center"))

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
