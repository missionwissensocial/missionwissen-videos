"""Karte Nordeuropa (Natural Earth 50m, Public Domain) -> geo.json. Plattkarte mit Breitenkorrektur CX=cos(62°)."""
import json, os, math
NE = os.path.expanduser("~/mw/geo/ne/geojson"); K = 3.0; CX = math.cos(math.radians(62))
X = lambda lon: (lon + 180) * K * CX; Y = lambda lat: (90 - lat) * K
BB = (-12, 60, 44, 78)
def inbb(r): return any(BB[0] <= lo <= BB[1] and BB[2] <= la <= BB[3] for lo, la in r)
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.2f} {Y(la):.2f}" for lo, la in r) + "Z" for r in rs)
land = json.load(open(f"{NE}/ne_50m_land.geojson"))
lr = [r for f in land["features"] for r in rings(f["geometry"]) if inbb(r)]
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
br = []; de = []; ru = []
for f in cty["features"]:
    n = f["properties"].get("ADMIN")
    for r in rings(f["geometry"]):
        if inbb(r):
            br.append(r)
            if n == "Germany": de.append(r)
            if n == "Russia": ru.append(r)
json.dump(dict(K=K, CX=CX, land=d_of(lr), cty=d_of(br), de=d_of(de), ru=d_of(ru)), open("geo.json", "w"))
print("ok", len(lr), len(br), len(de), len(ru), os.path.getsize("geo.json"))
