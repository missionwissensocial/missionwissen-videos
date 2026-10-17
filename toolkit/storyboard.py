import os, re, json, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
GF=os.path.abspath("../fonts/gf/ofl")
h=open("video.html").read()
beats=json.loads(re.search(r"const BEATS=(\[.*?\]);\nconst S=",h,re.S).group(1))
only=[int(x) for x in sys.argv[1:]]  # optional scene numbers
os.makedirs("sb",exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--allow-file-access-from-files"]); pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+os.path.abspath("video.html")); pg.wait_for_timeout(700)
    for i,bt in enumerate(beats):
        if only and i+1 not in only: continue
        t=bt["e"]-0.15
        pg.evaluate(f"render({t})"); pg.screenshot(path=f"sb/s{i+1:02d}.png")
    b.close()
F=ImageFont.truetype(f"{GF}/inter/Inter[opsz,wght].ttf",22); FB=ImageFont.truetype(f"{GF}/unbounded/Unbounded[wght].ttf",30)
FM=ImageFont.truetype(f"{GF}/jetbrainsmono/JetBrainsMono[wght].ttf",19)
W,H=360,640; CW=W+30; CH=H+190; cols=5
def wrap(txt,width=34):
    out=[];line=""
    for w in txt.split():
        if len(line)+len(w)+1>width: out.append(line); line=w
        else: line=(line+" "+w).strip()
    out.append(line); return out[:5]
idx=list(range(len(beats))) if not only else [n-1 for n in only]
pages=[idx[k:k+10] for k in range(0,len(idx),10)]
for pi,page in enumerate(pages):
    rows=(len(page)+cols-1)//cols
    sh=Image.new("RGB",(cols*CW+30,rows*CH+30),"#F4F4F6"); d=ImageDraw.Draw(sh)
    for j,i in enumerate(page):
        bt=beats[i]; x=30+(j%cols)*CW; y=30+(j//cols)*CH
        im=Image.open(f"sb/s{i+1:02d}.png").resize((W,H)); sh.paste(im,(x,y))
        d.rectangle([x,y,x+W-1,y+H-1],outline="#D5D9E1",width=2)
        d.text((x,y+H+14),f"{i+1:02d}",font=FB,fill="#7B3FE4")
        d.text((x+70,y+H+22),f"{bt['s']:.1f}–{bt['e']:.1f} s",font=FM,fill="#8A8F99")
        txt=" ".join(w[0] for w in bt["words"])
        for k,l in enumerate(wrap(txt)): d.text((x,y+H+60+k*26),l,font=F,fill="#0B0B10")
    name=f"storyboard-{pi+1}.png" if not only else f"storyboard-update-{pi+1}.png"
    sh.save(name); print(name, sh.size)
