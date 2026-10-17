import os, re
from playwright.sync_api import sync_playwright
GF=os.path.abspath("../fonts/gf/ofl")
src=open("../robot3/soft.py").read().split("poses=")[0].replace("import os\n","").replace("os.chdir(os.path.dirname(os.path.abspath(__file__)))\n","")
ns={}; exec(src,ns)
logo=open("../brand/out/missionwissen-logo-transparent-dunkel.svg").read()
def sized(svg,w):
    W,H=map(float,re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',svg).groups())
    return re.sub(r'width="[\d.]+" height="[\d.]+"',f'width="{w}" height="{w*H/W:.0f}"',svg,count=1)
PUR="#7B3FE4"; INK="#2B2D35"; INK2="#7A7F8C"; TQ="#19C6B4"
def P(d,w=3.2,c=INK,f="none"): return f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{f}" stroke-linecap="round" stroke-linejoin="round"/>'
def T(x,y,s,sz,c=INK,fam="JBM",wt=700,a="start"): return f'<text x="{x}" y="{y}" text-anchor="{a}" font-family="{fam}" font-weight="{wt}" font-size="{sz}" fill="{c}">{s}</text>'
# ID card
idc=(P("M30 20 h320 a18 18 0 0 1 18 18 v170 a18 18 0 0 1 -18 18 h-320 a18 18 0 0 1 -18 -18 v-170 a18 18 0 0 1 18 -18 Z",3.4)
 +P("M40 60 h96 v124 h-96 Z",2.4)+'<circle cx="88" cy="104" r="22" fill="none" stroke="#2B2D35" stroke-width="2.4"/>'+P("M56 178 C58 146 118 146 120 178",2.4)
 +T(158,70,"AUSWEIS",22)+P("M158 104 H330 M158 132 H300 M158 160 H320",2,INK2)
 +f'<rect x="272" y="168" width="58" height="42" rx="6" fill="#F5F0FF" stroke="{PUR}" stroke-width="3"/>')
idsvg=f'<svg viewBox="0 0 380 250" width="330">{idc}</svg>'
waves=f'<svg viewBox="0 0 90 200" width="80">{P("M10 70 q22 30 0 60",4,PUR)+P("M34 50 q34 50 0 100",4,PUR)+P("M58 30 q46 70 0 140",4,PUR)}</svg>'
ph=(P("M46 10 h188 a32 32 0 0 1 32 32 v376 a32 32 0 0 1 -32 32 h-188 a32 32 0 0 1 -32 -32 v-376 a32 32 0 0 1 32 -32 Z",3.6)+P("M110 32 h60",3,INK2)
 +T(140,96,"POSTFACH",22,INK,"JBM",700,"middle")
 +f'<path d="M84 140 h86 l30 30 v150 h-116 Z" fill="#F5F0FF" stroke="{PUR}" stroke-width="3.4" stroke-linejoin="round"/>'+P("M170 140 v30 h30",3,PUR)
 +T(142,258,"PDF",40,PUR,"JBM",700,"middle")+f'<circle cx="226" cy="58" r="20" fill="#E5484D"/>'+T(226,66,"1",22,"#fff","JBM",700,"middle"))
phone=f'<svg viewBox="0 0 280 460" width="230">{ph}</svg>'
css=f'''@font-face{{font-family:Unbounded;src:url("file://{GF}/unbounded/Unbounded[wght].ttf");font-weight:200 900}}
@font-face{{font-family:JBM;src:url("file://{GF}/jetbrainsmono/JetBrainsMono[wght].ttf");font-weight:100 800}}
@font-face{{font-family:Inter;src:url("file://{GF}/inter/Inter[opsz,wght].ttf");font-weight:100 900}}
*{{box-sizing:border-box}} body{{margin:0}}
.bg{{position:relative;overflow:hidden;width:1080px;height:1920px;background:radial-gradient(circle at 70% 55%,rgba(123,63,228,.10),transparent 40%),radial-gradient(circle at 25% 75%,rgba(25,198,180,.10),transparent 35%),
linear-gradient(rgba(11,11,16,.045) 1px,transparent 1px) 0 0/48px 48px,linear-gradient(90deg,rgba(11,11,16,.045) 1px,transparent 1px) 0 0/48px 48px,linear-gradient(#fff 40%,#F4F4F6)}}
.a{{position:absolute}} .h1{{font-family:Unbounded;font-weight:600;color:#0B0B10;letter-spacing:-.035em;line-height:1}}
.mm{{position:absolute;border-radius:36px;border:1.5px solid rgba(26,31,51,.12);box-shadow:0 14px 30px rgba(26,31,51,.12);display:flex;align-items:center;justify-content:center;gap:24px;
background:linear-gradient(rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(90deg,rgba(11,11,16,.09) 1px,transparent 1px) 0 0/50px 50px,linear-gradient(rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,linear-gradient(90deg,rgba(11,11,16,.035) 1px,transparent 1px) 0 0/10px 10px,#FCFCFD}}
.stamp{{position:absolute;font-family:JBM;font-weight:700;font-size:56px;color:{PUR};border:5px solid {PUR};border-radius:16px;padding:14px 28px;transform:rotate(-7deg);background:rgba(255,255,255,.92)}}
.bub{{position:absolute;background:rgba(255,255,255,.92);border:2.5px solid {PUR};border-radius:34px;box-shadow:0 0 40px rgba(123,63,228,.22),0 14px 30px rgba(26,31,51,.12);font-family:Unbounded;font-weight:600;color:#0B0B10;letter-spacing:-.02em;line-height:1.18;padding:38px 44px;font-size:50px}}
.bub:before{{content:"";position:absolute;left:-19px;top:96px;width:34px;height:34px;background:#fff;border-left:2.5px solid {PUR};border-bottom:2.5px solid {PUR};transform:rotate(45deg)}}
.chips{{position:absolute;display:flex;gap:14px}} .chip{{font-family:JBM;font-weight:600;font-size:29px;padding:12px 20px;color:#0B0B10;border:2px solid #0B0B10;border-radius:14px;background:rgba(255,255,255,.85);white-space:nowrap}}
.chip.p{{color:{PUR};border-color:{PUR};background:#F5F0FF}}'''
html=f'''<div class="bg">
<div class="a" style="left:0;width:1080px;top:228px;display:flex;justify-content:center">{sized(logo,380)}</div>
<div class="a h1" style="left:0;width:1080px;top:330px;text-align:center;font-size:92px">Führungszeugnis</div>
<div class="a h1" style="left:0;width:1080px;top:440px;text-align:center;font-size:170px;letter-spacing:-.055em;color:{PUR};white-space:nowrap">als PDF?</div>
<div class="a h1" style="left:0;width:1080px;top:622px;text-align:center;font-size:92px">Seit 1.10.</div>
<div class="mm" style="left:60px;top:765px;width:960px;height:445px">{idsvg}{waves}{phone}<div class="stamp" style="left:60px;top:345px">KEIN AMT</div></div>
<div class="a" style="left:50px;top:1250px;width:280px">{sized(ns["robot"]("t-",eye="wow"),280)}</div>
<div class="bub" style="left:330px;top:1270px;width:690px">Ganz ohne <span style="color:{PUR}">Wartenummer?</span></div>
<div class="chips" style="left:332px;top:1560px">{"".join(f'<div class="chip{c}">{t}</div>' for t,c in [("13 €",""),("BundID",""),("PDF in Stunden"," p")])}</div></div>'''
open("thumb.html","w").write(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{html}</body></html>")
with sync_playwright() as p:
    b=p.chromium.launch(args=["--allow-file-access-from-files"]); pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+os.path.abspath("thumb.html")); pg.wait_for_timeout(700); pg.screenshot(path="out/missionwissen-fuehrungszeugnis-thumbnail-9x16.png"); b.close()
