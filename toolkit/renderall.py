import os, sys, json, math
from multiprocessing import Process
from playwright.sync_api import sync_playwright
T=json.load(open("timing.json"))["total"]; N=int(math.ceil(T*30)); W=6
os.makedirs("frames",exist_ok=True)
def work(k):
    with sync_playwright() as p:
        b=p.chromium.launch(args=["--allow-file-access-from-files"]); pg=b.new_page(viewport={"width":1080,"height":1920})
        pg.goto("file://"+os.path.abspath("video.html")); pg.wait_for_timeout(600)
        for i in range(k,N,W):
            pg.evaluate(f"render({i/30})"); pg.screenshot(path=f"frames/f{i:05d}.jpg",type="jpeg",quality=94)
        b.close()
ps=[Process(target=work,args=(k,)) for k in range(W)]
[p.start() for p in ps]; [p.join() for p in ps]
print(N)
