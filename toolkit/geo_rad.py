"""Karte Niederlande/Deutschland (Natural Earth 50m, Public Domain) -> geo.json."""
import json, os
NE = os.path.expanduser("~/mw/geo/ne/geojson")
L0, B0, KX, KY = 1.0, 56.0, 64.0, 98.0
X = lambda lon: (lon - L0) * KX
Y = lambda lat: (B0 - lat) * KY
BOX = (-3, 44, 22, 59)
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def inbox(r): return any(BOX[0] < lo < BOX[2] and BOX[1] < la < BOX[3] for lo, la in r)
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in r) + "Z" for r in rs)
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
other = []; de = []; nl = []
for f in cty["features"]:
    n = f["properties"]["NAME"]
    rs = [r for r in rings(f["geometry"]) if inbox(r)]
    if not rs: continue
    if n == "France": rs = [r for r in rs if r[0][0] > -6 and r[0][1] > 41]
    if n == "Netherlands": rs = [r for r in rs if r[0][1] > 50]
    if n == "Germany": de = rs
    elif n == "Netherlands": nl = rs
    else: other.append(d_of(rs))
json.dump(dict(L0=L0, B0=B0, KX=KX, KY=KY, other=other, de=d_of(de), nl=d_of(nl)), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "geo.json"), "w"))
print("ok", len(other), len(de), len(nl))
