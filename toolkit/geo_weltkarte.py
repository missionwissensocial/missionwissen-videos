"""Weltkarte (Natural Earth 110m, Public Domain) + Wanderungsspur -> geo.json (Weltkoordinaten, K=3, Fenster lon -27..333)."""
import json, os, numpy as np
from matplotlib.path import Path
NE = os.path.expanduser("~/mw/geo/ne/geojson")
K = 3.0; LON0 = -27
def wl(lon): return lon + 360 if lon < LON0 else lon
def X(lon): return (wl(lon) + 180) * K
def Xraw(lon): return (lon + 180) * K
def Y(lat): return (90 - lat) * K

def rings(geom):
    if geom["type"] == "Polygon": return [geom["coordinates"][0]]
    return [p[0] for p in geom["coordinates"]]
def d_of(rs, off=0.0):
    out = []
    for r in rs:
        out.append("M" + "L".join(f"{Xraw(lo)+off:.1f} {Y(la):.1f}" for lo, la in r) + "Z")
    return "".join(out)

land = json.load(open(f"{NE}/ne_110m_land.geojson"))
lr = []
for f in land["features"]:
    for r in rings(f["geometry"]):
        if max(la for _, la in r) < -58: continue  # Antarktis raus
        lr.append(r)
land_d = d_of(lr, 0) + d_of(lr, 360 * K)

cty = json.load(open(f"{NE}/ne_110m_admin_0_countries.geojson"))
cont = {}
for f in cty["features"]:
    c = f["properties"].get("CONTINENT")
    cont.setdefault(c, []).extend(rings(f["geometry"]))
afr_d = d_of(cont["Africa"], 0)

rng = np.random.default_rng(4)
def sample(cname, n, box=None, mind=6.0):
    paths = [Path(np.array(r)) for r in cont[cname]]
    allp = np.concatenate([np.array(r) for r in cont[cname]])
    lo0, la0 = allp.min(0); lo1, la1 = allp.max(0)
    if box: lo0, lo1, la0, la1 = box
    pts = []; tries = 0
    while len(pts) < n and tries < 20000:
        tries += 1
        p = (rng.uniform(lo0, lo1), rng.uniform(la0, la1))
        if not any(pa.contains_point(p) for pa in paths): continue
        if any((p[0]-q[0])**2 + (p[1]-q[1])**2 < mind**2 for q in pts): continue
        pts.append(p)
    return pts
hook = []
for c, n, box, md in (("Africa", 3, None, 10), ("Europe", 4, (-10, 40, 36, 62), 6), ("Asia", 8, (60, 140, 10, 62), 9),
                      ("North America", 4, (-125, -70, 25, 60), 9), ("South America", 3, None, 10), ("Oceania", 2, (115, 152, -38, -15), 8)):
    hook += sample(c, n, box, md)
afr = sample("Africa", len(hook), None, 6.5)
# Reihenfolge der Pop-ins mischen
order = rng.permutation(len(hook)); hook = [hook[i] for i in order]

def cr(pts, step=2.0):
    P = np.array([[X(lo), Y(la)] for la, lo in pts])
    P = np.vstack([P[0], P, P[-1]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        n = max(2, int(np.linalg.norm(p2 - p1) / step))
        for k in range(n):
            t = k / n; t2, t3 = t*t, t*t*t
            out.append(0.5 * ((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t2 + (-p0+3*p1-3*p2+p3)*t3))
    out.append(P[-2]); return [[round(a, 1), round(b, 1)] for a, b in out]

SEG = {
 "A0": [(31.9,-8.9),(28,-5),(23,2),(17,12),(12,22),(8,30),(3,36)],
 "A":  [(3,36),(9,40),(12.6,43.3),(18,46),(24,50),(26,56),(26,62),(25,68),(22,73)],
 "B1": [(22,73),(17,74),(12,75.5),(8.5,77),(10,80),(15,81),(20,86.5),(21.5,90),(18,94),(14,97.5),(9,98.5),(4,101),(1,104),(-3,106),(-6.5,108),(-7.5,113),(-8.4,117),(-8.6,121),(-9,124.5)],
 "B2": [(-9,124.5),(-11,128),(-12.4,130.8)],
 "B3": [(-12.4,130.8),(-16,133),(-21,134),(-25.5,134.5)],
 "C":  [(24,50),(30,46),(33,40),(34,36),(37,35),(39,32),(41,27),(43,23),(46,17),(48,11),(47,4)],
 "D1": [(22,73),(27,84),(30,98),(33,108),(38,116),(45,124),(52,130),(58,138),(62,150),(65,165)],
 "D2": [(65,165),(66,175),(66,-170),(65,-160)],
 "D3": [(65,-160),(62,-150),(59,-140),(54,-131),(48,-124),(40,-121),(32,-115),(24,-106),(17,-97),(12,-87),(8,-79),(2,-77),(-8,-78),(-17,-71),(-27,-70),(-37,-72),(-46,-72),(-52,-70)],
}
seg = {k: cr(v) for k, v in SEG.items()}
json.dump(dict(K=K, win=[X(LON0)+0.0, Xraw(333-360)+360*K if False else (333+180)*K], land=land_d, afr=afr_d,
               hook=[[X(lo), Y(la)] for lo, la in hook], afr_pts=[[X(lo), Y(la)] for lo, la in afr], seg=seg),
          open("geo.json", "w"))
print("hook", len(hook), {k: len(v) for k, v in seg.items()}, "land chars", len(land_d))
