"""Geodaten fuer Drei-Schluchten-Damm (Natural Earth, Public Domain) -> geo.json (lon/lat, Projektion im Browser)."""
import json, os, math
NE = os.path.expanduser("~/mw/geo/ne/geojson")
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def simp(r, eps):
    out = [r[0]]
    for p in r[1:]:
        if abs(p[0]-out[-1][0]) + abs(p[1]-out[-1][1]) >= eps: out.append(p)
    return [[round(a,3),round(b,3)] for a,b in out]
land = json.load(open(f"{NE}/ne_110m_land.geojson"))
L = [simp(r, 0.6) for f in land["features"] for r in rings(f["geometry"])]
L = [r for r in L if len(r) > 3]
land50 = json.load(open(f"{NE}/ne_50m_land.geojson"))
L50 = []
for f in land50["features"]:
    for r in rings(f["geometry"]):
        if any(85 < lo < 135 and 10 < la < 50 for lo, la in r):
            rr = simp(r, 0.12)
            if len(rr) > 3: L50.append(rr)
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
CN, DE = [], []
for f in cty["features"]:
    a = f["properties"]["ADMIN"]
    if a == "China": CN += [simp(r, 0.1) for r in rings(f["geometry"])]
    if a == "Germany": DE += [simp(r, 0.03) for r in rings(f["geometry"])]
CN = [r for r in CN if len(r) > 3]
riv = json.load(open(f"{NE}/ne_50m_rivers_lake_centerlines.geojson"))
seg = {}
for f in riv["features"]:
    n = f["properties"].get("name")
    if n in ("Chang Jiang", "Yangtze", "Jinsha"):
        for l in f["geometry"]["coordinates"]: seg[(round(l[0][0],2), round(l[0][1],2))] = l
start = (98.54, 31.69); Y = []
cur = start
while cur in seg:
    l = seg.pop(cur); Y += l if not Y else l[1:]
    cur = (round(l[-1][0],2), round(l[-1][1],2))
    if cur not in seg:
        # naechstes Segment mit Startpunkt in der Naehe
        near = [k for k in seg if abs(k[0]-cur[0]) + abs(k[1]-cur[1]) < 0.06 and len(seg[k]) > 2]
        if near: cur = near[0]
Y.append([121.85, 31.35])  # Muendung bei Shanghai
Y = [[round(a,3),round(b,3)] for a,b in Y]
def nearest(p): return min(range(len(Y)), key=lambda i: (Y[i][0]-p[0])**2 + (Y[i][1]-p[1])**2)
DAM = [111.003, 30.823]; CQ = [106.55, 29.56]; SH = [121.47, 31.23]
i_cq, i_dam = nearest(CQ), nearest(DAM)
def plen(pts):
    s = 0
    for (a,b),(c,d) in zip(pts, pts[1:]):
        s += 6371*math.acos(min(1, math.sin(math.radians(b))*math.sin(math.radians(d)) + math.cos(math.radians(b))*math.cos(math.radians(d))*math.cos(math.radians(c-a))))
    return s
print("Punkte", len(Y), "CQ", i_cq, Y[i_cq], "Damm", i_dam, Y[i_dam], "Stausee-km", round(plen(Y[i_cq:i_dam+1])), "Schiff-km", round(plen(Y[i_cq:])))
json.dump(dict(land=L, land50=L50, cn=CN, de=DE, yz=Y, icq=i_cq, idam=i_dam, dam=DAM, cq=CQ, sh=SH,
               hh=[9.99, 53.55], mu=[11.58, 48.14], decen=[10.4, 51.1]), open("geo.json", "w"))
print("ok", os.path.getsize("geo.json"))
