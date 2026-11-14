"""missionwissen – „Die wichtigste Entdeckung der Menschheit – ein Grashalm?“ (14.11.2026)
Erster Pilot im FILMREIFEN Look (Wunsch Alex 13./14.11.): vollflächige Canvas-Bühne statt Millimeterpapier,
Gegenlicht/Golden Hour, Tiefenunschärfe (Fokus-Zug), Parallax-Ebenen, Bokeh, Vignette, Filmkorn, Zeitraffer.
Kamera-Übergänge ohne harte Schnitte: Makro-Ähre -> Karte Naher Osten -> Landschaft -> Makro (Ähre zerfällt) ->
Boden-Querschnitt (Aussaat, Zeitraffer) -> Rauszoom Feld -> Dorf/Stadt in der Dämmerung -> Whip-Pan „heute“ ->
1/5-Ring -> Brötchen. Szenen-JS in scene.js (canvas 2D, deterministisch: render(t)); Teil vor /*FRAME*/ = Init.
Overlays (Chips, große Zahl) bleiben HTML-Elemente -> Engine dyn_ws.py + sfx-Erkennung funktionieren unverändert."""
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
HOOK = 'Die wichtigste <span style="color:#FFD27A">Entdeckung</span> der Menschheit – ein Grashalm?'
B = [
 ("s1", 0, HOOK, "Die *wichtigste* *Entdeckung* der *Menschheit* – ein *Grashalm?*", "staunt"),
 ("s2", 0, HOOK, "Was er mit deinem *Frühstück* zu tun hat, verrate ich dir am *Ende.*", None),
 ("s3", 1, "", "Vor etwa *elftausend* *Jahren,* im heutigen *Nahen* *Osten.*", None),
 ("s4", 1, "", "Die Menschen *sammeln* die *Körner* von *wildem* *Weizen* – einem *Gras.*", None),
 ("s5", 2, "", "Das *Problem:* Ist der Weizen *reif,* *zerfällt* seine *Ähre.*", None),
 ("s6", 2, "", "Die *Körner* *fallen* zu *Boden* und sind *kaum* *aufzusammeln.*", None),
 ("s7", 3, "", "Aber bei *manchen* *Halmen* *bleiben* die Körner *hängen.*", None),
 ("s8", 3, "", "Beim *Ernten* landen deshalb *besonders* *viele* dieser Körner im *Korb.*", None),
 ("s9", 4, "", "Dann die *Idee:* Man *sät* diese *Körner* *selbst* aus.", None),
 ("s10", 4, "", "Daraus *wächst* wieder Weizen, der seine Körner *festhält.*", None),
 ("s11", 4, "", "Über *Jahrhunderte* wird das die *Regel.*", None),
 ("s12", 5, "", "Und *dann?*", None),
 ("s13", 5, "", "Wer ein *Feld* hat, *bleibt* in der *Nähe.*", None),
 ("s14", 5, "", "*Dörfer* werden *größer,* später entstehen *Städte.*", None),
 ("s15", 5, "", "Und *heute?*", None),
 ("s16", 5, "", "Weizen liefert rund *ein* *Fünftel* aller *Kalorien* *weltweit.*", None),
 ("s17", 5, "", "Auch dein *Frühstücksbrötchen* stammt von *genau* *diesen* *Halmen* ab.", None),
]

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
    cid=0; cur=0; cnt_=0
    for w in b["words"]:
        L=len(w[0])
        if cnt_ and (cur+1+L>22 or cnt_>=3): cid+=1; cur=0; cnt_=0
        cur+=(1 if cnt_ else 0)+L; cnt_+=1; w.append(cid)
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
rows = ["| Zeit | Headline | Sprechtext | Roboter |", "|---|---|---|---|"]
for b in beats:
    rows.append(f"| {b['s']:.1f}–{b['e']:.1f} s | {re.sub('<[^>]+>','',b['head'])} | {' '.join(w[0] for w in b['words'])} | {b['pose'] or '–'} |")
open("out/beats.md", "w").write("\n".join(rows) + f"\n\nGesamtlänge: {TOTAL:.1f} s\n")

# ---------- helpers ----------
TQ = "#19C6B4"; PUR = "#7B3FE4"; RED = "#E5484D"; PURL = "#B79BFF"; GOLD = "#FFD27A"; GOLDD = "#B07A1E"
stage = []
A = lambda i, o=None, d=0: f'data-in="{i}"' + (f' data-out="{o}"' if o else '') + (f' data-d="{d}"' if d else '')
def el(inner, x, y, attrs, w=None, style=""):
    ws = f"width:{w}px;" if w else ""
    return f'<div class="el" {attrs} style="left:{x}px;top:{y}px;{ws}{style}">{inner}</div>'
def cnt(v, anchor, dec=0, d=0):
    return f'<span class="count" data-count="{v}" data-dec="{dec}" data-cin="{anchor}" data-cd="{d}">0</span>'
CENTER = "display:flex;justify-content:center"
OY = 1150
def chip_(txt, i, o, col=PUR, sfx="marker", y=OY, fs=34, d=0):
    fs = 34
    return el(f'<div class="chip mono" style="font-size:{fs}px;border-color:{col};color:{col}">{txt}</div>', 40, y, A(i, o, d) + f' data-sfx="{sfx}"', 1000, CENTER)
def note_(txt, i, o, y=1236, d=0):
    y = 1420
    return el(f'<div class="note mono">{txt}</div>', 24, y, A(i, o, d) + ' data-sfx="none"')

stage.append(chip_("☕ WAS HAT ER MIT DEINEM FRÜHSTÜCK ZU TUN?", "s2@Frühstück", "s2@verrate", PUR, "glass", OY, 27, -0.1))
stage.append(chip_("AUFLÖSUNG AM ENDE", "s2@verrate", "s3", PUR, "marker", OY, 32, 0))
stage.append(el(f'<div class="col"><div class="mono kick">VOR ETWA</div><div class="huge2">{cnt(11000, "s3@elftausend", 0, 0)}</div><div class="mono kick">JAHREN</div></div>',
                0, 900, A("s3@elftausend", "s3@Nahen", -0.15) + ' data-sfx="none"', 1080, CENTER))
stage.append(chip_("HEUTE: NAHER OSTEN", "s3@Nahen", "s4", "#2E7D4F", "marker", OY, 32, -0.05))
stage.append(note_("KARTE: NATURAL EARTH · GRÜN = FRUCHTBARER HALBMOND", "s3@Nahen", "s4", 1236, -0.05))
stage.append(chip_("WILDER WEIZEN = EIN GRAS", "s4@Weizen", "s5", GOLDD, "marker", OY, 32, 0))
stage.append(chip_("REIF → DIE ÄHRE ZERFÄLLT", "s5@zerfällt", "s6@kaum", RED, "marker", OY, 32, -0.1))
stage.append(chip_("KAUM AUFZUSAMMELN", "s6@kaum", "s7", RED, "marker", OY, 32, -0.05))
stage.append(chip_("LILA LEUCHTEND = KÖRNER BLEIBEN HÄNGEN", "s7@bleiben", "s8", PUR, "glass", OY, 27, -0.15))
stage.append(chip_("IM KORB: BESONDERS VIELE LILA KÖRNER", "s8@besonders", "s9", PUR, "marker", OY, 27, -0.1))
stage.append(chip_("💡 DIE IDEE: SELBST AUSSÄEN", "s9@Idee", "s10", PUR, "glass", OY, 32, -0.05))
stage.append(chip_("NEUER WEIZEN HÄLT SEINE KÖRNER FEST", "s10@Weizen", "s11", PUR, "marker", OY, 27, 0))
stage.append(el('<div class="barbox"><div class="mono barl">ANTEIL HALME, DIE FESTHALTEN</div><div class="bart"><div id="barf" class="barf"></div></div>'
                '<div class="row" style="justify-content:space-between;width:100%"><span class="mono barn" id="barn">25 %</span><span class="mono barn" style="color:#8A8F99">SCHEMATISCH</span></div></div>',
                90, 1165, A("s11", "s12", -0.05) + ' data-sfx="glass"', 900))
stage.append(chip_("FELD → HÄUSER DANEBEN", "s13@bleibt", "s14", GOLDD, "marker", OY, 30, -0.1))
stage.append(chip_("DÖRFER WACHSEN", "s14@Dörfer", "s14@später", GOLDD, "marker", OY, 32, 0))
stage.append(chip_("SPÄTER: ERSTE STÄDTE", "s14@später", "s15", PUR, "marker", OY, 32, 0.1))
stage.append(note_("ILLUSTRATION · SCHEMATISCH", "s4", "s15", 1236, 0))
stage.append(el('<div class="col"><div class="huge3"><span style="color:#FFD27A">1</span>/5</div>'
                '<div class="mono kick" style="margin-top:6px">ALLER KALORIEN WELTWEIT</div></div>',
                0, 610, A("s16@Fünftel", "s17", -0.2) + ' data-sfx="glass"', 1080, CENTER))
stage.append(note_("QUELLE: FAOSTAT (≈ 20 %)", "s16@Fünftel", "s17", 1236, 0))
stage.append(chip_("WILDER WEIZEN → DEIN BRÖTCHEN", "s17@genau", "end", GOLDD, "glass", OY, 31, -0.2))

# Karte (Natural Earth 50m, Public Domain) -> geo.json via geo_stadt.py
GEO = json.load(open("geo.json"))
GEOJS = dict(K=GEO["K"], CX=GEO["CX"], land=GEO["land"], lakes=GEO["lakes"], cty=GEO["cty"], rivers=list(GEO["rivers"].values()))

SCENE_JS = open("scene.js").read()  # im Repo: toolkit/scene_grashalm.js -> als scene.js neben build.py kopieren

# ---- End card (CTA-Update 10.11.: + Folgen UND Speichern) ----
logo = open("../brand/out/missionwissen-logo-transparent-dunkel.svg").read()
logo = re.sub(r'width="[\d.]+" height="[\d.]+"', 'width="820" height="253"', logo, count=1)
endcard = (f'<div class="el" {A("end",None,0.1)} style="left:130px;top:470px">{logo}</div>'
           f'<div class="el" {A("end",None,0.5)} style="left:0;width:1080px;top:790px;display:flex;justify-content:center"><div class="row" style="gap:28px"><div class="follow">+&nbsp;Folgen</div><div class="follow">🔖&nbsp;Speichern</div></div></div>'
           f'<div class="el" {A("end",None,0.7)} style="left:0;width:1080px;top:935px;text-align:center"><div class="mono small grey">JEDEN TAG EIN BISSCHEN SCHLAUER</div></div>')
robots = "".join(f'<div class="pose" data-pose="{n}">{robot_svg("r"+n[:2]+"-", **k)}</div>' for n, k in POSES.items())
mono = '<svg width="72" height="72" viewBox="0 0 80 80" fill="none"><g id="wmg" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"><path d="M20 32 V24 a10 10 0 0 1 20 0 V32 M40 24 a10 10 0 0 1 20 0 V32"/><path d="M20 48 V56 a10 10 0 0 0 20 0 V48 M40 56 a10 10 0 0 0 20 0 V48"/></g><circle cx="40" cy="40" r="3.2" fill="#7B3FE4"/></svg>'

html = f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><style>
@font-face{{font-family:Unbounded;src:url("file://{GF}/unbounded/Unbounded[wght].ttf");font-weight:200 900}}
@font-face{{font-family:Inter;src:url("file://{GF}/inter/Inter[opsz,wght].ttf");font-weight:100 900}}
@font-face{{font-family:JBM;src:url("file://{GF}/jetbrainsmono/JetBrainsMono[wght].ttf");font-weight:100 800}}
*{{box-sizing:border-box}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif;color:#0B0B10;background:#000}}
#v{{position:relative;width:1080px;height:1920px;overflow:hidden;
background:linear-gradient(rgba(11,11,16,.04) 1px,transparent 1px) 0 0/48px 48px,linear-gradient(90deg,rgba(11,11,16,.04) 1px,transparent 1px) 0 0/48px 48px,linear-gradient(#FFFFFF 40%,#F4F4F6)}}
#cv{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
.mono{{font-family:JBM,monospace;font-weight:500;letter-spacing:.02em}}
.small{{font-size:24px}} .grey{{color:#8A8F99}}
#chap,#prog{{display:none}}
#wm{{position:absolute;left:924px;top:112px;opacity:.5;z-index:4}}
#headbg{{position:absolute;left:0;top:0;width:1080px;height:560px;z-index:2;background:linear-gradient(rgba(8,6,14,.78) 30%,rgba(8,6,14,0))}}
#head{{position:absolute;left:70px;top:190px;width:940px;font-family:Unbounded;font-weight:600;font-size:64px;line-height:1.13;letter-spacing:-1.5px;z-index:3;color:#FFFFFF!important;text-shadow:0 4px 24px rgba(0,0,0,.55)}}
.el{{position:absolute}}
.row{{display:flex;align-items:center}} .col{{display:flex;flex-direction:column;align-items:center}}
.chip{{font-weight:800;border:3px solid;border-radius:12px;padding:12px 22px;background:rgba(255,255,255,.96);box-shadow:0 10px 30px rgba(0,0,0,.35);white-space:nowrap}}
.note{{font-size:16px;color:rgba(255,255,255,.75);background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.25);border-radius:8px;padding:5px 9px;white-space:nowrap}}
.kick{{font-size:32px;font-weight:800;color:#FFFFFF;text-shadow:0 2px 12px rgba(0,0,0,.7);letter-spacing:.08em}}
.huge2{{font-family:Unbounded;font-weight:600;font-size:200px;letter-spacing:-6px;line-height:1;color:#FFFFFF;text-shadow:0 0 40px rgba(255,190,90,.55),0 6px 30px rgba(0,0,0,.6)}}
.huge3{{font-family:Unbounded;font-weight:600;font-size:250px;letter-spacing:-8px;line-height:1;color:#FFFFFF;text-shadow:0 0 50px rgba(255,190,90,.5),0 6px 30px rgba(0,0,0,.6)}}
.barbox{{width:900px;background:rgba(255,255,255,.96);border:3px solid #7B3FE4;border-radius:16px;padding:16px 22px 12px;box-shadow:0 10px 30px rgba(0,0,0,.35);display:flex;flex-direction:column;gap:10px}}
.barl{{font-size:24px;font-weight:800;color:#5B2BB5}} .barn{{font-size:22px;font-weight:800;color:#5B2BB5}}
.bart{{width:100%;height:30px;border-radius:15px;background:#ECE7F7;overflow:hidden}}
.barf{{height:100%;width:25%;border-radius:15px;background:linear-gradient(90deg,#B79BFF,#7B3FE4)}}
.follow{{font-family:Unbounded;font-weight:600;font-size:42px;color:#fff;background:#7B3FE4;border-radius:999px;padding:24px 56px;box-shadow:0 0 30px rgba(123,63,228,.4),0 8px 18px rgba(26,31,51,.15)}}
#robot{{position:absolute;z-index:5;left:40px;top:790px;width:357px;height:500px}}
#robot .pose{{position:absolute;inset:0}} #robot svg{{width:357px;height:500px}}
.eyes{{transform-box:fill-box;transform-origin:center}}
#cap{{position:absolute;left:0;width:1080px;top:1300px;display:flex;justify-content:center;z-index:6}}
#pill{{background:rgba(11,11,16,.88);border-radius:16px;padding:14px 24px;font-weight:700;font-size:50px;color:#fff;max-width:920px;text-align:center;line-height:1.2;box-shadow:0 8px 30px rgba(0,0,0,.35)}}
#pill span{{opacity:.45}} #pill span.on{{opacity:1}} #pill span.kw{{color:#FFD27A}} #pill span.kw2{{color:#B79BFF}}
</style></head><body><div id="v">
<canvas id="cv" width="1080" height="1920"></canvas>
<div id="chap" class="mono"></div><div id="prog">{"".join("<div></div>" for _ in CH)}</div><div id="wm">{mono}</div>
<div id="headbg"></div><div id="head"></div>
{"".join(stage)}
{endcard}
<div id="robot">{robots}</div>
<div id="cap"><div id="pill"></div></div>
</div>
<script>
const GEO={json.dumps(GEOJS)};
const BEATS={json.dumps(beats, ensure_ascii=False)};
const S={json.dumps(S, ensure_ascii=False)}; const CH={json.dumps(CH, ensure_ascii=False)}; const END={END:.3f}; const AUD={AUD:.3f};
const cl=(x,a,b)=>Math.max(a,Math.min(b,x)); const ease=p=>1-Math.pow(1-p,3); const pr=(t,t0,d)=>cl((t-t0)/d,0,1);
const els=[...document.querySelectorAll('[data-in]')];
function beatAt(t){{let b=BEATS[0];for(const x of BEATS) if(t>=x.s) b=x; return b;}}
/*SCENEINIT*/
window.render=function(t){{
 const end=t>=END; const b=beatAt(t);
 document.getElementById('chap').textContent=CH[b.ch];
 [...document.querySelectorAll('#prog div')].forEach((d,i)=>d.className=i<=b.ch?'on':'');
 const top=cl(1-pr(t,END,.3),0,1); ['chap','prog','head'].forEach(id=>document.getElementById(id).style.opacity=top); document.getElementById('headbg').style.opacity=1-pr(t,S['s3']-0.2,0.5); document.getElementById('head').style.opacity=top*(1-pr(t,S['s3']-0.2,0.3));
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
 for(const c of document.querySelectorAll('.count')){{const t0=(S[c.dataset.cin]??0)+(+c.dataset.cd||0); const dd=+c.dataset.dec||0; const v=+c.dataset.count*ease(pr(t,t0,0.8)); c.textContent=(dd===0&&+c.dataset.count>=1000)?Math.round(v).toLocaleString('de-DE'):v.toFixed(dd).replace('.',',');}}
 // sketches
 for(const sk of document.querySelectorAll('.sketch')){{const t0=(S[sk.dataset.sin]??0)+(+sk.dataset.sd||0); const p=ease(pr(t,t0,+sk.dataset.sdur||1.5)); sk.querySelectorAll('.ink').forEach(e=>e.style.strokeDashoffset=1-p); sk.querySelectorAll('.mesh').forEach(e=>e.style.opacity=pr(t,t0+(+sk.dataset.sdur||1.5)*0.6,0.6));}}
/*SCENEJS*/
 // robot
 let pose=b.pose; if(end) pose='winkt';
 const R=document.getElementById('robot');
 let rop=0; if(pose&&!end){{const prevHad=BEATS.indexOf(b)>0&&BEATS[BEATS.indexOf(b)-1].pose; rop=prevHad?1:ease(pr(t,b.s,.3)); const nb=BEATS[BEATS.indexOf(b)+1]; if(nb&&!nb.pose) rop*=1-pr(t,nb.s-0.2,.2); if(!nb) rop*=1-pr(t,END-0.2,.2);}}
 if(end){{rop=ease(pr(t,END+0.3,.35));}}
 if(BEATS.indexOf(b)===0&&!end) rop=1;
 R.style.opacity=rop; R.style.transform=`translateY(${{6*Math.sin(t*2*Math.PI/2.4)}}px)`+(end?' translate(321px,90px) scale(0.62)':'');
 let prevPose=null; const bi=BEATS.indexOf(b); if(bi>0) prevPose=BEATS[bi-1].pose; const pf=pr(t,b.s,.15);
 for(const p of R.querySelectorAll('.pose')){{const n=p.dataset.pose; p.style.opacity=end?(n==='winkt'?1:0):(n===pose?pf:(n===prevPose&&prevPose!==pose?1-pf:0)); if(pose===prevPose&&n===pose) p.style.opacity=1; if(bi===0&&!end) p.style.opacity=(n===pose?1:0);}}
 const bl=(t%3.7); const sy=bl<0.12?0.2:1; R.querySelectorAll('.eyes').forEach(e=>e.style.transform=`scaleY(${{sy}})`);
 R.querySelectorAll('.pulse').forEach(e=>e.setAttribute('opacity',0.3+0.1*Math.sin(t*2*Math.PI/1.8)));
 // captions
 const P=document.getElementById('pill'); const W=b.words; let wi=0; W.forEach((w,i)=>{{if(t>=w[1]) wi=i;}});
 const cid=W[wi][3]; P.innerHTML=W.map((w,i)=>[w,i]).filter(x=>x[0][3]===cid).map(([w,i])=>`<span class="${{i<=wi?'on':''}} ${{w[2]?(b.ch%2?'kw2':'kw'):''}}">${{w[0]}}</span>`).join(' ');
 document.getElementById('cap').style.opacity=t<AUD+0.3?1:1-pr(t,AUD+0.3,.3);
 document.getElementById('wmg').setAttribute('stroke', t>=END?'#0B0B10':'#FFFFFF');
}};
render(0);
</script></body></html>'''
init, frame = SCENE_JS.split("/*FRAME*/")
html = html.replace('/*SCENEINIT*/', init).replace('/*SCENEJS*/', frame)
open("video.html", "w").write(html)
json.dump(dict(total=TOTAL, end=END, beats=[(b["id"], b["s"], b["e"]) for b in beats]), open("timing.json", "w"))
print("total", round(TOTAL, 2))
