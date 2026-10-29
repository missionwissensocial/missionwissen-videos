"""missionwissen SFX v2 – differentiated sound palette per element type + motion. (Kopie aus toolkit/sfx.py)"""
import re, json, wave
import numpy as np
from scipy.signal import butter, sosfilt
SR = 44100
rng = np.random.default_rng(7)

def T(d): return np.arange(int(d * SR)) / SR
def env(n, a=.004, d=.06):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)
def osc(freq, wave_="sin"):
    ph = 2 * np.pi * np.cumsum(freq) / SR
    if wave_ == "sin": return np.sin(ph)
    if wave_ == "tri": return 2 / np.pi * np.arcsin(np.sin(ph))
    if wave_ == "sq": return np.tanh(np.sin(ph) * 4)
    if wave_ == "saw": return 2 * ((ph / (2 * np.pi)) % 1) - 1
def filt(x, kind, f, order=2):
    if kind == "bp": sos = butter(order, [f[0] / (SR / 2), min(.99, f[1] / (SR / 2))], "band", output="sos")
    else: sos = butter(order, f / (SR / 2), kind, output="sos")
    return sosfilt(sos, x)
def sweep_bp(x, f0, f1, q=.6):
    out = np.zeros_like(x); B = 512; n = len(x)
    for i in range(0, n, B):
        fc = f0 * (f1 / f0) ** (i / max(1, n))
        sos = butter(2, [fc * (1 - q / 2) / (SR / 2), min(.98, fc * (1 + q / 2) / (SR / 2))], "band", output="sos")
        out[i:i + B] = sosfilt(sos, x[i:i + B])
    return out
def norm(x, g=1.0): return x / (np.abs(x).max() + 1e-9) * g
def noise(d): return rng.standard_normal(int(d * SR))
def fade(x, a=.003, r=.02):
    n = len(x); e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[n - nr:] *= np.linspace(1, 0, nr); return x * e
def cat(*xs): return np.concatenate(xs)
def at(base, x, i):
    j = min(len(base), i + len(x)); base[i:j] += x[:j - i]; return base

def bubble(p=1.0):
    t = T(.07); f = (380 + 900 * (t / .07) ** 1.6) * p
    return osc(f) * env(len(t), .002, .028) * .9
def plop(p=1.0):
    t = T(.14); f = (720 * np.exp(-t * 30) + 170) * p
    x = osc(f) + .25 * osc(2 * f)
    return fade(x * env(len(t), .002, .05) + filt(noise(.14), "hp", 2500) * env(len(t), .0005, .004) * .3)
def soft_pop(p=1.0):
    t = T(.09); f = (950 * np.exp(-t * 28) + 260) * p
    return osc(f) * env(len(t), .002, .03) * .8
def panel(p=1.0):
    d = .34; t = T(d)
    air = sweep_bp(noise(d), 500 * p, 2600 * p, .9) * np.sin(np.pi * np.clip(t / .3, 0, 1)) ** 1.5
    paper = filt(noise(d), "bp", (2500, 7000)) * (np.clip(t / .22, 0, 1) ** 2) * np.exp(-np.clip(t - .22, 0, None) * 40)
    tap = np.zeros(len(t)); k = int(.21 * SR); tt = T(.09)
    tap[k:k + len(tt)] = osc(150 * np.exp(-tt * 9) + 70) * env(len(tt), .001, .03)
    return fade(norm(air, .55) + norm(paper, .35) + tap * .8, .002, .03)
BELL = [1046.5, 1174.7, 1318.5, 1568.0, 1760.0, 2093.0]
def glass(note=0):
    t = T(.5); f0 = BELL[note % len(BELL)]
    bloop = osc(260 + 420 * (T(.09) / .09)) * env(int(.09 * SR), .004, .035)
    tink = (osc(np.full(len(t), f0)) + .45 * osc(np.full(len(t), f0 * 2.76)) + .22 * osc(np.full(len(t), f0 * 5.4))) * env(len(t), .001, .16)
    out = tink * .38; out[:len(bloop)] += bloop * .7
    return fade(out)
def marker(p=1.0):
    d = .11; t = T(d)
    tap = filt(noise(d), "bp", (1800, 5200)) * env(len(t), .0008, .012)
    sq = osc((1700 + 900 * t / d) * p, "tri") * np.sin(np.pi * np.clip(t / .07, 0, 1)) * (t < .07)
    return fade(norm(tap, .7) + sq * .22)
def stamp():
    d = .62; out = np.zeros(int(d * SR)); k = int(.17 * SR)
    pre = sweep_bp(noise(.17), 3000, 700, .9); pre = norm(pre, .35) * np.linspace(0, 1, len(pre)) ** 2
    out[:len(pre)] += pre
    tt = T(.45)
    boom = osc(120 * np.exp(-tt * 14) + 48) * env(len(tt), .001, .16)
    slap = filt(noise(.45), "bp", (900, 6000)) * env(len(tt), .0005, .018)
    rattle = filt(noise(.45), "bp", (300, 1200)) * env(len(tt), .002, .06) * .35
    hit = np.tanh((boom * 1.2 + norm(slap, .9) + norm(rattle, .4)) * 1.6)
    at(out, hit, k); return fade(out)
def zip_(d=.28):
    t = T(d); x = sweep_bp(noise(d), 1400, 4200, .5)
    am = .55 + .45 * np.sin(2 * np.pi * 38 * t)
    return fade(norm(x, .9) * am * np.sin(np.pi * t / d) ** .6)
def wahwah():
    out = []
    for f0, f1, d in ((392, 370, .2), (330, 262, .42)):
        t = T(d); f = f0 + (f1 - f0) * (t / d) + 6 * np.sin(2 * np.pi * 6 * t) * (t / d)
        x = filt(osc(f, "saw"), "lp", 1400) * (np.minimum(1, t / .02) * np.minimum(1, (d - t) / .05))
        x *= .6 + .4 * np.sin(2 * np.pi * 3.2 * t + 1.5) ** 2
        out.append(x)
    return fade(norm(cat(*out), .85))
def success():
    a = glass(0) * .9; b = glass(3)
    out = np.zeros(len(a) + int(.09 * SR)); at(out, a, 0); at(out, b, int(.09 * SR)); return out
def whoosh(kind):
    if kind == 0: d, f0, f1 = .3, 400, 3200
    elif kind == 1: d, f0, f1 = .36, 2600, 500
    else: d, f0, f1 = .24, 800, 5000
    t = T(d); x = sweep_bp(noise(d), f0, f1, .8)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * (1 + .6 * (t / d))
    return fade(norm(x * e, .7))
def tick(p=1.0):
    t = T(.03); return osc(np.full(len(t), 2400 * p)) * env(len(t), .0005, .006)
def scribble(d):
    t = T(d); x = filt(noise(d), "bp", (1800, 7500))
    rate = rng.uniform(9, 15); am = .5 + .5 * np.abs(np.sin(2 * np.pi * rate * t + rng.uniform(0, 6)))
    am *= .75 + .25 * np.sin(2 * np.pi * rate * .37 * t)
    e = np.minimum(1, t / .04) * np.minimum(1, (d - t) / .08)
    return norm(x, .5) * am * e
def click():                  # checkbox click (mouse-like tick + tiny pop)
    out = np.zeros(int(.12 * SR))
    at(out, filt(noise(.015), "hp", 3500) * env(int(.015 * SR), .0003, .002) * .9, 0)
    at(out, soft_pop(1.5) * .5, int(.008 * SR)); return fade(out)
def ding():                   # NEW: Postfach-Eingang (Benachrichtigungs-Ding, 2 Töne abwärts)
    out = np.zeros(int(.7 * SR))
    for k, f in enumerate((1568.0, 1174.7)):
        tt = T(.5); x = (osc(np.full(len(tt), f)) + .3 * osc(np.full(len(tt), f * 2))) * env(len(tt), .002, .14)
        at(out, x * .55, int(k * .12 * SR))
    return fade(out)
def blip(f, d=.07, w="sq"):
    t = T(d); return filt(osc(np.full(len(t), f), w), "lp", 3500) * np.minimum(1, t / .004) * np.minimum(1, (d - t) / .01)
def robot(pose):
    if pose == "staunt":
        t = T(.22); f = 520 * 2 ** (t / .22); return fade(filt(osc(f, "sq"), "lp", 3000) * .5)
    if pose == "denkt":
        return cat(blip(330, .09), np.zeros(int(.05 * SR)), blip(294, .14)) * .5
    if pose == "zeigt":
        return cat(blip(660, .05), np.zeros(int(.03 * SR)), blip(990, .08)) * .5
    if pose == "winkt":
        return cat(blip(784, .05), np.zeros(int(.025 * SR)), blip(988, .05), np.zeros(int(.025 * SR)), blip(1318, .09)) * .45
    return blip(700) * .4
def sparkle(d=.7):
    out = np.zeros(int(d * SR))
    for k in range(9):
        f = rng.choice(BELL) * rng.choice([2, 3])
        tt = T(.25); x = osc(np.full(len(tt), f)) * env(len(tt), .001, .06)
        at(out, x * rng.uniform(.25, .5), int(k * d / 11 * SR))
    return fade(out)
def button():
    out = np.zeros(int(.8 * SR))
    at(out, filt(noise(.02), "hp", 3000) * env(int(.02 * SR), .0003, .003) * .6, 0)
    at(out, plop(1.3), int(.01 * SR))
    at(out, glass(5) * 1.1, int(.07 * SR))
    return out

h = open("video.html").read()
S = json.loads(re.search(r"const S=(\{.*?\});", h).group(1))
beats = json.loads(re.search(r"const BEATS=(\[.*?\]);\nconst S=", h, re.S).group(1))
total = json.load(open("timing.json"))["total"]
ev = []
def add(t, x, v, pan=0.0, tag=""): ev.append((t, x, v, pan, tag))
def pan_of(attrs):
    l = re.search(r"left:(-?\d+)px", attrs); w = re.search(r"width:(\d+)px", attrs)
    if not l: return 0.0
    c = int(l.group(1)) + (int(w.group(1)) / 2 if w else 100)
    return float(np.clip((c - 540) / 540, -1, 1)) * .45

prev = None; wk = 0
for b in beats:
    if b["head"] != prev and b["head"]:
        add(max(0, b["s"] - .06), whoosh(wk % 3), .42, [-.25, .25, 0][wk % 3], "whoosh"); wk += 1
    prev = b["head"]
for i, b in enumerate(beats):
    if i == 0 and b["pose"]: add(.35, robot(b["pose"]), .28, .35, "robot")
    if i and b["pose"] and b["pose"] != beats[i - 1]["pose"] and b["head"]:
        add(b["s"] + .02, robot(b["pose"]), .28, .35, "robot")
add(S["end"] + .35, robot("winkt"), .28, .3, "robot")

seq = {}; note = 0
for m in re.finditer(r'<(div|svg)([^>]*?)data-in="([^"]+)"([^>]*)>', h):
    attrs = m.group(2) + m.group(4); key = m.group(3)
    cls = (re.search(r'class="([^"]*)"', attrs) or re.search("()", "")).group(1)
    d = re.search(r'data-d="([-\d.]+)"', attrs); t0 = S.get(key, 0) + (float(d.group(1)) if d else 0)
    inner = h[m.end():m.end() + 400]; txt = re.sub(r"<[^>]+>", " ", inner)
    pan = pan_of(attrs)
    ov = re.search(r'data-sfx="(\w+)"', attrs); ov = ov.group(1) if ov else None
    if ov == "none": continue
    if ov == "click": add(t0, click(), .45, pan, "click"); continue
    if ov == "ding": add(t0, ding(), .4, pan, "ding"); continue
    if ov == "plop":
        k = seq.get("prod", 0); seq["prod"] = k + 1
        add(t0, plop([1, 1.19, 1.41][k % 3]), .4, pan, "plop"); continue
    if ov == "success": add(t0, success(), .4, pan, "success"); continue
    if ov == "pop": add(t0, soft_pop(rng.uniform(.9, 1.2)), .28, pan, "pop"); continue
    if ov == "stamp" or "stamp" in inner[:160] or "stamp" in cls.split():
        add(t0, stamp(), .62, pan, "stamp")
    elif ov == "bubble" or "aa" in cls.split():
        k = seq.get("aa", 0); seq["aa"] = k + 1
        add(t0, bubble(1 + .09 * k), .32, pan, "bubble")
    elif ov == "panel" or "mm" in cls.split():
        add(t0, panel(rng.uniform(.85, 1.15)), .55, pan, "panel")
    elif ov == "glass" or cls.startswith("card"):
        add(t0, glass(note), .4, pan, "glass"); note += 2
    elif ov == "marker" or "mk" in cls.split():
        add(t0, marker(rng.uniform(.9, 1.15)), .38, pan, "marker")
    elif ov in ("zip", "fail") or "rline" in cls:
        add(t0, zip_(), .4, pan, "zip")
        if ov == "fail" or "✕" in txt[:120]: add(t0 + .3, wahwah(), .3, pan, "fail")
    elif key == "end":
        if "Folgen" in txt[:40]: add(t0 + .05, button(), .45, .2, "button")
        elif "SCHLAUER" in txt[:60]: add(t0, whoosh(2), .25, 0, "whoosh")
        else: add(t0, sparkle(), .35, 0, "sparkle")
    elif "✓" in txt[:80]:
        add(t0, success(), .4, pan, "success")
    else:
        add(t0, soft_pop(rng.uniform(.9, 1.2)), .28, pan, "pop")
for m in re.finditer(r'data-sin="([^"]+)" data-sd="([-\d.]+)" data-sdur="([\d.]+)"', h):
    dur = min(1.3, max(.35, float(m.group(3)) * .65))
    add(S.get(m.group(1), 0) + float(m.group(2)), scribble(dur), .3, rng.uniform(-.2, .2), "scribble")
for m in re.finditer(r'data-cin="([^"]+)" data-cd="([\d.]+)"', h):
    t0 = S.get(m.group(1), 0) + float(m.group(2))
    for k in range(8): add(t0 + k * .085, tick(1 + .06 * k), .22, 0, "tick")
    add(t0 + .7, glass(4) * .7, .3, 0, "glass")
add(S["end"] + 2.6, glass(3) * .6, .25, 0, "glass")

# ---- NEU (Steinzeit-Panorama): Schritte, Hufe, Speer, Feuer, Knochenflöte, Kamera-Fahrten ----
def steps(d, rate=6.5):
    out = np.zeros(int(d * SR)); k = 0; tt = 0.0
    while tt < d - .05:
        x = filt(noise(.03), "bp", (500, 2200)) * env(int(.03 * SR), .0008, .008)
        x += osc(np.full(int(.03 * SR), 170 + 40 * (k % 2))) * env(int(.03 * SR), .001, .01) * .5
        at(out, norm(x, .8) * (.75 + .25 * (k % 2)), int(tt * SR)); k += 1; tt += 1 / rate
    return out
def hooves(d):
    out = np.zeros(int(d * SR)); tt = 0.0; k = 0
    while tt < d - .1:
        for off in (0, .07):
            x = osc(np.full(int(.05 * SR), 120 + 25 * (k % 3))) * env(int(.05 * SR), .001, .02) + filt(noise(.05), "bp", (300, 1500)) * env(int(.05 * SR), .0005, .01) * .6
            at(out, x * .8, int((tt + off) * SR))
        tt += .26; k += 1
    t = T(d); return out * np.minimum(1, t / .3)[:len(out)] * np.minimum(1, (d - t) / .4)[:len(out)]
def spear():
    d = .55; t = T(d); x = sweep_bp(noise(d), 2500, 600, .7) * np.sin(np.pi * t / d) ** 2
    thud = np.zeros(len(t)); tt = T(.15); k = int(.48 * SR)
    seg = (osc(110 * np.exp(-tt * 12) + 60) * env(len(tt), .001, .04))[:len(t) - k]; thud[k:k + len(seg)] = seg
    return fade(norm(x, .6) + thud * .9)
def crackle(d):
    out = filt(noise(d), "bp", (200, 900)) * .12
    for k in range(int(d * 14)):
        tt = T(.012); at(out, filt(noise(.012), "hp", 1500) * env(len(tt), .0003, .003) * rng.uniform(.3, 1), int(rng.uniform(0, d - .02) * SR))
    t = T(d); return out * np.minimum(1, t / .6)[:len(out)] * np.minimum(1, (d - t) / .8)[:len(out)]
def flute():
    notes = [(587.3, .22), (659.3, .22), (784.0, .34), (659.3, .2), (587.3, .44)]
    out = []
    for f, d in notes:
        t = T(d); vib = 1 + .006 * np.sin(2 * np.pi * 5.5 * t)
        x = osc(f * vib) + .18 * osc(2 * f * vib) + filt(noise(d), "bp", (f * .8, f * 1.3)) * .25
        out.append(x * np.minimum(1, t / .04) * np.minimum(1, (d - t) / .06))
    return fade(norm(cat(*out), .8), .01, .08)
def wind(d):
    t = T(d); x = sweep_bp(noise(d), 300, 900, .8); return norm(x, .5) * np.sin(np.pi * t / d) ** 2
P = json.loads(re.search(r"const PAN=(\{.*?\});", h).group(1))
TS = lambda a, o: S.get(a, 0) + o
tk = [(TS(a, o), x) for a, o, x in P["tip"]]
for (t0, x0), (t1, x1) in zip(tk, tk[1:]):
    if x1 != x0 and t1 - t0 > .3: add(t0, steps(t1 - t0, 7), .22, rng.uniform(-.2, .2), "steps")
ck = [(TS(a, o), x, z) for a, o, x, z, fy in P["cam"]]
for (t0, x0, z0), (t1, x1, z1) in zip(ck, ck[1:]):
    if abs(x1 - x0) > 300 and t1 - t0 > .3: add(t0, wind(min(1.4, t1 - t0)), .22, .15 if x1 > x0 else -.15, "wind")
add(S["p4@Tieren"], hooves(2.6), .26, .25, "hooves")
add(S["p6@Speeren"] + .1, spear(), .45, .25, "spear")
add(S["p10@Feuer"] - .2, crackle(S["end"] - S["p10@Feuer"] + 2.5), .35, 0, "crackle")
add(S["p10@Musik"] + .1, flute() * .7, .3, -.1, "flute")
add(S["p11@Flöten"] + .1, flute(), .4, 0, "flute")
add(S["p14@tauschen"] + .2, whoosh(1), .4, 0, "whoosh2")

ev.sort(key=lambda e: e[0])
gap = dict(flute=.5, pop=.1, bubble=.07, plop=.1, marker=.1, glass=.12, panel=.25, whoosh=.25, stamp=.2, scribble=.5, tick=.05, click=.1)
last = {}; keep = []
for e in ev:
    t, tag = e[0], e[4]
    if t - last.get(tag, -9) < gap.get(tag, 0): continue
    last[tag] = t; keep.append(e)
n = int((total + 1.5) * SR); L = np.zeros(n); Rc = np.zeros(n)
for t, x, v, pan, tag in keep:
    i = int(max(0, t) * SR)
    if i >= n: continue
    x = x * v * rng.uniform(.9, 1.05)
    gl, gr = np.sqrt((1 - pan) / 2) * 1.414, np.sqrt((1 + pan) / 2) * 1.414
    at(L, x * gl, i); at(Rc, x * gr, i)
st = np.stack([L, Rc], 1); st = np.tanh(st * 1.15) * .85
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
from collections import Counter
print(len(keep), "events", dict(Counter(e[4] for e in keep)))
