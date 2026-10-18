# usage: python3 thumb_gen.py config.json  (run inside video folder; uses ../fonts etc.)
import os, re, json, sys, base64
from playwright.sync_api import sync_playwright
cfg=json.load(open(sys.argv[1]))
src=open("thumb.py").read()
css=re.search(r"css=f'''(.*?)'''",src,re.S).group(1)
GF=os.path.abspath("../fonts/gf/ofl"); PUR="#7B3FE4"
css=eval("f'''"+css+"'''")
rs=open("../robot3/soft.py").read().split("poses=")[0].replace("import os\n","").replace("os.chdir(os.path.dirname(os.path.abspath(__file__)))\n","")
ns={}; exec(rs,ns)
logo=open("../brand/out/missionwissen-logo-transparent-dunkel.svg").read()
def sized(svg,w):
    W,H=map(float,re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',svg).groups())
    return re.sub(r'width="[\d.]+" height="[\d.]+"',f'width="{w}" height="{w*H/W:.0f}"',svg,count=1)
from PIL import Image
im=Image.open(cfg["panel"]).crop(tuple(cfg["crop"])); im.save("/tmp/panel.png")
b64=base64.b64encode(open("/tmp/panel.png","rb").read()).decode()
pw,ph=im.size; scale=960/pw
l1,l2,l3=cfg["title"]
html=f'''<div class="bg">
<div class="a" style="left:0;width:1080px;top:228px;display:flex;justify-content:center">{sized(logo,380)}</div>
<div class="a h1" style="left:0;width:1080px;top:330px;text-align:center;font-size:92px;white-space:nowrap">{l1}</div>
<div class="a h1" style="left:0;width:1080px;top:440px;text-align:center;font-size:{cfg.get("big",170)}px;letter-spacing:-.055em;color:{PUR};white-space:nowrap">{l2}</div>
<div class="a h1" style="left:0;width:1080px;top:622px;text-align:center;font-size:92px;white-space:nowrap">{l3}</div>
<div class="mm" style="left:60px;top:765px;width:960px;height:445px;overflow:hidden"><img src="data:image/png;base64,{b64}" style="width:960px;height:{ph*scale:.0f}px;position:absolute;left:0;top:{(445-ph*scale)/2:.0f}px"/>{cfg.get("stamp","")}</div>
<div class="a" style="left:50px;top:1250px;width:280px">{sized(ns["robot"]("t-",eye="wow"),280)}</div>
<div class="bub" style="left:330px;top:1270px;width:690px">{cfg["bubble"]}</div>
<div class="chips" style="left:332px;top:1560px">{"".join(f'<div class="chip{c}">{t}</div>' for t,c in cfg["chips"])}</div></div>'''
open("thumb.html","w").write(f"<html><head><meta charset=utf-8><style>{css}</style></head><body>{html}</body></html>")
with sync_playwright() as p:
    b=p.chromium.launch(args=["--allow-file-access-from-files"]); pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+os.path.abspath("thumb.html")); pg.wait_for_timeout(700)
    w=pg.evaluate("Math.max(...[...document.querySelectorAll('.chips')].map(e=>e.getBoundingClientRect().right))")
    print("chips right edge",w)
    pg.screenshot(path=cfg["out"]); b.close()
