"""Orthographische Erde (Natural Earth 50m, Public Domain), Zentrum 105E/36N, R=400 -> geo.json. Mauerverlauf SCHEMATISCH."""
import json, os, math
NE = os.path.expanduser("~/mw/geo/ne/geojson"); R = 400.0; L0, P0 = math.radians(105), math.radians(36)
def pj(lon, lat):
    l, p = math.radians(lon), math.radians(lat)
    cosc = math.sin(P0)*math.sin(p) + math.cos(P0)*math.cos(p)*math.cos(l-L0)
    x = R*math.cos(p)*math.sin(l-L0); y = -R*(math.cos(P0)*math.sin(p) - math.sin(P0)*math.cos(p)*math.cos(l-L0))
    if cosc < 0:
        n = math.hypot(x, y) or 1; x, y = x/n*R, y/n*R
    return x, y, cosc
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def simp(r, eps):
    out = [r[0]]
    for p in r[1:]:
        if abs(p[0]-out[-1][0]) + abs(p[1]-out[-1][1]) >= eps: out.append(p)
    return out
def d_of(rs, close=True):
    s = ""
    for r in rs:
        pts = [pj(lo, la) for lo, la in r]
        if all(c < 0 for _, _, c in pts) or len(pts) < 3: continue
        s += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y, _ in pts) + ("Z" if close else "")
    return s
land = json.load(open(f"{NE}/ne_50m_land.geojson"))
lr = []
for f in land["features"]:
    for r in rings(f["geometry"]): lr.append(simp(r, 0.25))
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
cn, br = [], []
for f in cty["features"]:
    p = f["properties"]
    for r in rings(f["geometry"]):
        rr = simp(r, 0.2)
        if p["ADMIN"] == "China": cn.append(rr)
        else: br.append(rr)
W = {
 "ming": [(98.2,39.8),(100.4,38.9),(102.6,37.9),(104.0,37.4),(106.2,38.5),(107.5,38.0),(109.7,38.3),(111.2,39.4),(113.3,40.1),(114.9,40.8),(116.0,40.4),(117.2,40.7),(118.6,40.4),(119.8,40.0)],
 "han": [(93.8,40.4),(95.8,40.3),(98.2,39.8)],
 "nord": [(106.5,41.0),(108.5,41.4),(110.0,40.8),(111.7,41.0),(114.0,41.8),(116.5,42.3),(119.0,42.4),(121.5,42.2),(123.4,41.6),(124.4,40.4)],
 "jin": [(110.5,44.5),(114.0,45.5),(117.5,47.5),(119.5,49.0)],
}
def wig(pts, seed):
    # dichter abtasten + leichte Zacken (Mauer folgt Bergkämmen)
    import random; rr = random.Random(seed); out = []
    for (a, b), (c, d) in zip(pts, pts[1:]):
        n = 6
        for k in range(n):
            u = k/n; out.append((a+(c-a)*u + rr.uniform(-.12,.12), b+(d-b)*u + rr.uniform(-.12,.12)))
    out.append(pts[-1]); return out
walls = {k: "M" + "L".join(f"{pj(lo,la)[0]:.2f} {pj(lo,la)[1]:.2f}" for lo, la in wig(v, i)) for i, (k, v) in enumerate(W.items())}
bx, by, _ = pj(116.0, 40.4)
json.dump(dict(R=R, land=d_of(lr), cn=d_of(cn), br=d_of(br, False), walls=walls, bad=[bx, by],
               china=list(pj(104, 35)[:2])), open("geo.json", "w"))
print("ok", os.path.getsize("geo.json"), bx, by)
