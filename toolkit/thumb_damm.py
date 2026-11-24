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
from PIL import Image
im=Image.open("frames/f00660.jpg").crop((0,560,1080,1063)); im.save("panel.png")
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
<div class="a" style="left:0;width:1080px;top:150px;display:flex;justify-content:center">{sized(logo,360)}</div>
<div class="a" style="left:0;width:1080px;top:250px;display:flex;justify-content:center"><div class="chip p" style="font-size:30px">MEGA-PROJEKTE · FOLGE 1</div></div>
<div class="a h1" style="left:0;width:1080px;top:350px;text-align:center;font-size:84px;white-space:nowrap">Kann ein Staudamm</div>
<div class="a h1" style="left:0;width:1080px;top:455px;text-align:center;font-size:170px;letter-spacing:-.055em;color:{PUR};white-space:nowrap">die Erde</div>
<div class="a h1" style="left:0;width:1080px;top:637px;text-align:center;font-size:96px">bremsen?</div>
<div class="mm" style="left:60px;top:775px;width:960px;height:445px;overflow:hidden"><img src="panel.png" style="width:960px;height:447px"></div>
<div class="a" style="left:50px;top:1250px;width:280px">{sized(ns["robot"]("t-",eye="wow"),280)}</div>
<div class="bub" style="left:330px;top:1270px;width:690px">Jeder Tag <span style="color:{PUR}">länger?</span></div>
<div class="chips" style="left:332px;top:1560px">{"".join(f'<div class="chip{c}">{t}</div>' for t,c in [("China",""),("Jangtse",""),("NASA-Rechnung"," p")])}</div></div>'''
open("thumb.html","w").write(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{html}</body></html>")
with sync_playwright() as p:
    b=p.chromium.launch(args=["--allow-file-access-from-files"]); pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+os.path.abspath("thumb.html")); pg.wait_for_timeout(700); pg.screenshot(path="out/thumbnail.png"); b.close()
