"""Karte Frankreich/Deutschland (Natural Earth 50m, Public Domain) -> geo.json.
Weltkoordinaten: X=(lon-L0)*KX, Y=(B0-lat)*KY (Breitenkorrektur ~cos 48°).
Glasfaser-Flächen sind SCHEMATISCH: Kreise, deren Vereinigung 95 % (FR) bzw. 62 % (DE) der Landfläche deckt."""
import json, os, math, random
import numpy as np
from matplotlib.path import Path as MPath
NE = os.path.expanduser("~/mw/geo/ne/geojson")
L0, B0, KX, KY = -6.0, 56.0, 48.0, 75.0
X = lambda lon: (lon - L0) * KX
Y = lambda lat: (B0 - lat) * KY
BOX = (-11, 38, 22, 60)
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def inbox(r): return any(BOX[0] < lo < BOX[2] and BOX[1] < la < BOX[3] for lo, la in r)
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in r) + "Z" for r in rs)
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
other = []; fr = []; de = []
for f in cty["features"]:
    n = f["properties"]["NAME"]
    rs = [r for r in rings(f["geometry"]) if inbox(r)]
    if not rs: continue
    if n == "France": fr = [r for r in rs if r[0][0] > -6 and r[0][1] > 41]
    elif n == "Germany": de = rs
    else: other.append(d_of(rs))
def area_pts(rs, n, seed):
    rnd = np.random.default_rng(seed); paths = [MPath(np.array(r)) for r in rs]
    a = np.array(rs[max(range(len(rs)), key=lambda i: len(rs[i]))])
    lo0, la0 = a.min(0); lo1, la1 = a.max(0); out = []
    while len(out) < n:
        p = (rnd.uniform(lo0, lo1), rnd.uniform(la0, la1))
        if any(P.contains_point(p) for P in paths): out.append(p)
    return np.array(out)
def cover(samples, cen, rad):
    # in Weltkoordinaten (px)
    sx = (samples[:, 0] - L0) * KX; sy = (B0 - samples[:, 1]) * KY
    hit = np.zeros(len(samples), bool)
    for (cx, cy), r in zip(cen, rad): hit |= (sx - cx) ** 2 + (sy - cy) ** 2 <= r * r
    return hit.mean()
def calib(samples, cen, base, target):
    lo, hi = 0.0, 5.0
    for _ in range(40):
        m = (lo + hi) / 2
        if cover(samples, cen, base * m) < target: lo = m
        else: hi = m
    return base * hi
# --- Frankreich: Glasfaser-Route (Hauptdarsteller) durch die Städte ---
CITIES_FR = [("Brest", -4.49, 48.39), ("Rennes", -1.68, 48.11), ("Nantes", -1.55, 47.22), ("Bordeaux", -0.58, 44.84), ("Toulouse", 1.44, 43.6),
             ("Montpellier", 3.88, 43.61), ("Marseille", 5.37, 43.3), ("Nizza", 7.26, 43.7), ("Lyon", 4.84, 45.76), ("Clermont", 3.08, 45.78),
             ("Orléans", 1.9, 47.9), ("Paris", 2.35, 48.86), ("Lille", 3.06, 50.63), ("Reims", 4.03, 49.26), ("Strasbourg", 7.75, 48.58), ("Dijon", 5.04, 47.32)]
route = [(X(lo), Y(la)) for _, lo, la in CITIES_FR]
seg = [math.dist(route[i], route[i + 1]) for i in range(len(route) - 1)]; L = sum(seg)
cum = [0]
for s in seg: cum.append(cum[-1] + s)
def nearest_frac(x, y):
    best = (1e9, 0)
    for i in range(len(route) - 1):
        (x0, y0), (x1, y1) = route[i], route[i + 1]; dx, dy = x1 - x0, y1 - y0
        u = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
        d = math.dist((x, y), (x0 + u * dx, y0 + u * dy))
        if d < best[0]: best = (d, (cum[i] + u * seg[i]) / L)
    return best[1]
sfr = area_pts(fr, 6000, 1)
cfr = [(X(lo), Y(la)) for lo, la in area_pts(fr, 70, 2)] + route
rfr = calib(sfr, cfr, np.ones(len(cfr)) * 30.0, 0.95)
circ_fr = [dict(x=round(x, 1), y=round(y, 1), r=round(r, 1), f=round(nearest_frac(x, y), 3)) for (x, y), r in zip(cfr, rfr)]
# --- Deutschland: 62 % (unregelmäßig, ballungsnah) ---
sde = area_pts(de, 6000, 3)
CITIES_DE = [(10.0, 53.55), (13.4, 52.52), (11.58, 48.14), (6.96, 50.94), (8.68, 50.11), (9.18, 48.78), (12.37, 51.34), (9.73, 52.37), (6.78, 51.23), (7.47, 51.51),
             (11.08, 49.45), (8.8, 53.08), (13.74, 51.05), (8.47, 49.49), (7.1, 50.73), (10.52, 52.26), (12.1, 54.09), (11.03, 50.98), (8.0, 52.27), (10.9, 48.37)]
rnd = random.Random(5)
cde = [(X(lo), Y(la)) for lo, la in CITIES_DE] + [(X(lo), Y(la)) for lo, la in area_pts(de, 26, 4)]
base = np.array([1.5 if i < len(CITIES_DE) else rnd.uniform(0.6, 1.1) for i in range(len(cde))]) * 20
rde = calib(sde, cde, base, 0.62)
circ_de = [dict(x=round(x, 1), y=round(y, 1), r=round(r, 1), f=round(rnd.random(), 3)) for (x, y), r in zip(cde, rde)]
print("FR cover", round(cover(sfr, cfr, rfr), 3), "DE cover", round(cover(sde, cde, rde), 3))
# --- Kupferleitungen (schematisch): Linien zwischen Städten ---
def wire(a, b, k):
    (x0, y0), (x1, y1) = a, b; mx, my = (x0 + x1) / 2, (y0 + y1) / 2; nx, ny = -(y1 - y0), x1 - x0; n = math.hypot(nx, ny) or 1
    o = (k % 2 * 2 - 1) * 0.08 * n
    return f"M{x0:.1f} {y0:.1f}Q{mx + nx / n * o:.1f} {my + ny / n * o:.1f} {x1:.1f} {y1:.1f}"
dep = [(X(lo), Y(la)) for lo, la in CITIES_DE]
DEW = [(0, 1), (0, 7), (7, 2), (2, 5), (5, 4), (4, 3), (3, 8), (8, 9), (9, 7), (1, 6), (6, 12), (6, 10), (10, 2), (4, 13), (1, 15), (0, 11), (11, 18), (16, 1), (17, 6), (19, 2), (14, 3)]
cu_de = [wire(dep[a], dep[b], k) for k, (a, b) in enumerate(DEW)]
cfp = [(X(lo), Y(la)) for _, lo, la in CITIES_FR]
FRW = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (6, 8), (8, 9), (9, 10), (10, 11), (11, 12), (11, 13), (13, 14), (14, 15), (15, 8), (1, 11), (3, 9), (12, 13)]
cu_fr = [wire(cfp[a], cfp[b], k) for k, (a, b) in enumerate(FRW)]
json.dump(dict(L0=L0, B0=B0, KX=KX, KY=KY, other=other, fr=d_of(fr), de=d_of(de), route=[[round(x, 1), round(y, 1)] for x, y in route],
               circ_fr=circ_fr, circ_de=circ_de, cu_de=cu_de, cu_fr=cu_fr), open("geo.json", "w"))
print("ok", len(other), len(circ_fr), len(circ_de))
