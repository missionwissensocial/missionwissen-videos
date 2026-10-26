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
CH = ["01 DIE FRAGE", "02 DER RICHTWERT", "03 DEIN RECHT", "04 DIE FRIST", "05 UND DU?"]
B = [
 ("p1", 0, "Wird deine Kasse 2027 teurer?", "Wird deine *Krankenkasse* nächstes *Jahr* *teurer?*", "staunt"),
 ("p2", 1, "Offiziell: 2,9 %", "Die *offizielle* *Zahl* klingt erst mal *beruhigend:* Der *durchschnittliche* *Zusatzbeitrag* bleibt bei *zwei* *Komma* *neun* *Prozent.*", None),
 ("p3", 1, "Aber: nur ein Richtwert", "Aber *Achtung:* Das ist nur ein *Richtwert.*", "denkt"),
 ("p4", 1, "Jede Kasse entscheidet selbst", "Jede *Kasse* legt ihren *eigenen* *Beitrag* fest, meistens erst im *Dezember.*", None),
 ("p5", 1, "Viele liegen schon drüber", "Und *viele* verlangen schon *heute* *mehr* als den *Durchschnitt.*", None),
 ("p6", 2, "Dein Recht: Sonderkündigung", "*Erhöht* deine *Kasse* zum *Januar,* hast du ein *Sonderkündigungsrecht.*", "zeigt"),
 ("p7", 2, "Wechseln – auch als Neuling", "Dann darfst du *wechseln,* auch wenn du erst *kurz* *Mitglied* bist.", None),
 ("p8", 3, "Frist: Ende Januar", "Wichtig ist nur die *Frist:* Bis *Ende* *Januar* musst du dir eine *neue* *Kasse* aussuchen.", None),
 ("p9", 3, "Kündigen? Macht die neue Kasse", "*Kündigen* musst du dabei *nicht* *selbst,* das *erledigt* die *neue* *Kasse* für dich.", None),
 ("p10", 4, "Im Dezember checken", "Also: *Schau* im *Dezember* kurz *nach,* was deine *Kasse* *verlangt.*", "zeigt"),
 ("p11", 4, "Bleiben oder wechseln?", "*Bleibst* du bei deiner *Kasse* – oder *wechselst* du?", "winkt"),
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
 cal='<rect x="6" y="9" width="36" height="33" rx="4"/><path d="M6 18h36M15 5v8M33 5v8M14 26h6M22 26h6M30 26h4M14 33h6M22 33h6"/>',
 up='<path d="M24 40V10M12 22l12-12 12 12"/>',
 swap='<path d="M8 16h30l-7-7M40 32H10l7 7"/>',
 cross='<rect x="6" y="6" width="36" height="36" rx="8"/><path d="M24 14v20M14 24h20"/>',
 search='<circle cx="21" cy="21" r="13"/><path d="M31 31l11 11"/>',
)
def hcard(size=110, col=PUR):
    return ic('<rect x="4" y="10" width="40" height="28" rx="4"/><path d="M4 18h40"/><path d="M14 27h6M17 24v6" />', size, col)
def bars_sk():
    o = P("M40 270 H720", 2.4)
    hs = [150, 215, 115, 245]
    for i, h in enumerate(hs):
        x = 80 + i * 140
        o += mesh(f"M{x} {270-h} H{x+100} V270 H{x} Z", 760, 300)
        o += P(f"M{x} 270 V{270-h} H{x+100} V270", 2.6, PUR if h > 135 else INK)
        o += TX(x + 50, 296, f"KASSE {'ABCD'[i]}", 18, INK2, anchor="middle")
    o += P("M40 135 H740", 3, TQ)
    o += TX(740, 122, "Ø 2,9 %", 26, "#0E8C80", anchor="end")
    return o
def lvl(icon, col, small, title, right="", fs=40):
    return f'<div class="row" style="gap:28px;height:100%">{ic(I[icon],76,col)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">{small}</div><div class="rowtitle" style="font-size:{fs}px;margin:0">{title}</div></div>{right}</div>'
X = '<div class="okc" style="margin-left:auto;background:#E5484D;box-shadow:0 0 24px rgba(229,72,77,.4)">✕</div>'
OKI = '<div class="okc" style="margin-left:auto">✓</div>'
CENTER = "display:flex;justify-content:center"

# p1 Hook (Roboter staunt links -> Inhalte rechts)
stage.append(card(f'<div class="col" style="gap:14px;height:100%;justify-content:center">{hcard(120)}<div class="mono small grey">KRANKENKASSE</div><div class="bignum" style="font-size:104px">2027</div></div>', 440, 470, 560, 380, "active", A("p1", "p2", -0.4)))
stage.append(el('<div class="stamp mono" style="font-size:54px;color:#7B3FE4;border-color:#7B3FE4">TEURER?</div>', 440, 920, A("p1@teurer", "p2"), 560, CENTER))
# p2 Offizieller Wert
stage.append(card(f'<div class="col" style="gap:10px;height:100%;justify-content:center"><div class="mono small grey">Ø ZUSATZBEITRAG 2027 · OFFIZIELL</div><div class="bignum" style="font-size:170px">{cnt(2.9, "p2@zwei", 1)} %</div></div>', 80, 470, 920, 380, "activeTQ", A("p2@offizielle", "p3")))
stage.append(el('<div class="chip tq mono" style="font-size:32px">WIE 2026</div>', 80, 900, A("p2@Zusatzbeitrag", "p3"), 920, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:48px;color:#0E8C80;border-color:#19C6B4">UNVERÄNDERT</div>', 80, 1030, A("p2@Prozent", "p3"), 920, CENTER))
# p3 Nur Richtwert (Roboter denkt)
stage.append(card(f'<div class="col" style="gap:8px;height:100%;justify-content:center"><div class="mono small grey">BUNDESWEITER SCHNITT</div><div class="bignum" style="font-size:96px">2,9 %</div></div>', 440, 470, 560, 260, "", A("p3", "p4")))
stage.append(el('<div class="stamp mono" style="font-size:44px">NUR RICHTWERT</div>', 440, 800, A("p3@Richtwert", "p4"), 560, CENTER))
# p4/p5 Balken-Skizze
stage.append(mm(sketch(bars_sk(), 760, 300, 80, 40, "p4@Kasse", 0, 1.6) + mk("SCHEMATISCH", 30, 375, "p4@Kasse", 0.6, INK) + mk("3 VON 4 ÜBER Ø", 600, 22, "p5@viele", 0, RED), 80, 470, 920, 420, A("p4@Kasse", "p6")))
stage.append(card(lvl("cal", PUR, "FESTGELEGT MEIST", "im Dezember", fs=40), 80, 930, 920, 190, "active", A("p4@Dezember", "p5")))
stage.append(card(lvl("up", RED, "VIELE KASSEN", "schon heute drüber", fs=38), 80, 930, 920, 190, "", A("p5@mehr", "p6")))
# p6 Sonderkündigungsrecht (Roboter zeigt)
stage.append(card(lvl("up", RED, "ERHÖHUNG ZUM", "Januar", fs=46), 440, 470, 560, 210, "", A("p6@Erhöht", "p7")))
stage.append(el('<div class="stamp mono" style="font-size:30px;color:#0E8C80;border-color:#19C6B4">SONDERKÜNDIGUNGSRECHT</div>', 440, 760, A("p6@Sonderkündigungsrecht", "p7"), 560, CENTER))
# p7 Wechseln
stage.append(card(f'<div class="row" style="gap:30px;height:100%;justify-content:center"><div class="col" style="gap:8px">{hcard(110, "#8A8F99")}<div class="mono small grey">ALTE KASSE</div></div>{ic(I["swap"],96,PUR)}<div class="col" style="gap:8px">{hcard(110, TQ)}<div class="mono small" style="color:#0E8C80">NEUE KASSE</div></div></div>', 80, 470, 920, 300, "active", A("p7@wechseln", "p8")))
stage.append(el('<div class="chip tq mono" style="font-size:30px">AUCH NACH KURZER MITGLIEDSCHAFT ✓</div>', 80, 830, f'{A("p7@Mitglied", "p8")} data-sfx="success"', 920, CENTER))
# p8 Frist
stage.append(card(f'<div class="row" style="gap:34px;height:100%;justify-content:center">{ic(I["cal"],130,PUR)}<div class="col" style="gap:6px;align-items:flex-start"><div class="mono small grey">NEUE KASSE WÄHLEN BIS</div><div class="bignum" style="font-size:92px">31. Jan.</div></div></div>', 80, 470, 920, 320, "active", A("p8@Frist", "p9")))
stage.append(el('<div class="chip mono" style="font-size:28px">BEI ERHÖHUNG ZUM 1. JANUAR</div>', 80, 840, A("p8@Januar", "p9"), 920, CENTER))
stage.append(el('<div class="stamp mono" style="font-size:46px">FRIST!</div>', 80, 960, A("p8@aussuchen", "p9"), 920, CENTER))
# p9 Kündigen nicht selbst
stage.append(card(lvl("doc", RED, "ALTE KASSE KÜNDIGEN?", "Nicht selbst", X, fs=40), 80, 470, 920, 210, "", A("p9@Kündigen", "p10")))
stage.append(card(lvl("cross", TQ, "DAS ERLEDIGT", "die neue Kasse", OKI, fs=40), 80, 710, 920, 210, "activeTQ", A("p9@erledigt", "p10")))
# p10 Dezember checken (Roboter zeigt)
stage.append(card(lvl("cal", PUR, "IM DEZEMBER", "Beitrag checken", fs=32), 440, 470, 560, 210, "active", A("p10@Dezember", "p11")))
stage.append(card(lvl("search", INK, "WO?", "Website der Kasse", fs=28), 440, 710, 560, 190, "", A("p10@verlangt", "p11")))
# p11 Frage (Roboter winkt)
stage.append(el('<div class="chip pu mono" style="font-size:40px">BLEIBEN</div>', 440, 520, f'{A("p11@Bleibst", "end")} data-sfx="plop"', 560, CENTER))
stage.append(el('<div class="qbig" style="position:static;font-size:90px;line-height:1;text-align:center">oder</div>', 440, 630, A("p11@oder", "end"), 560, CENTER))
stage.append(el('<div class="chip tq mono" style="font-size:40px">WECHSELN</div>', 440, 760, f'{A("p11@wechselst", "end")} data-sfx="plop"', 560, CENTER))
stage.append(el('<div class="chip mono" style="font-size:22px">SCHREIB\'S IN DIE KOMMENTARE</div>', 440, 900, f'{A("p11@wechselst", "end", 0.4)} data-sfx="plop"', 560, CENTER))

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
