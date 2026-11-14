"""Weltkarte (Natural Earth 50m, Public Domain), Plattkarte mit Breitenkorrektur CX=cos(40°) -> geo.json.
Europa-Ausschnitt fuer die Pest-Ausbreitung (SCHEMATISCH)."""
import json, os, math
NE = os.path.expanduser("~/mw/geo/ne/geojson"); K = 3.0; CX = math.cos(math.radians(40))
X = lambda lon: (lon + 180) * K * CX; Y = lambda lat: (90 - lat) * K
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def simp(r, eps):
    out = [r[0]]
    for p in r[1:]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) >= eps: out.append(p)
    return out
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in r) + "Z" for r in rs if len(r) > 3)
land = json.load(open(f"{NE}/ne_50m_land.geojson"))
EU = (-12, 46, 34.5, 72)
def ineu(r): return all(EU[0] - 8 <= lo <= EU[1] + 8 and EU[2] - 6 <= la <= EU[3] + 6 for lo, la in r)
world, eur = [], []
for f in land["features"]:
    for r in rings(f["geometry"]):
        if max(la for _, la in r) < -58: continue
        near = any(EU[0] <= lo <= EU[1] and EU[2] <= la <= EU[3] for lo, la in r)
        world.append(simp(r, 0.08 if near else 0.6))
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
EUC = {"Europe"}
for f in cty["features"]:
    p = f["properties"]
    if p["CONTINENT"] in EUC or p["NAME"] in ("Turkey", "Cyprus"):
        for r in rings(f["geometry"]):
            if any(EU[0] <= lo <= EU[1] and EU[2] <= la <= EU[3] for lo, la in r) and all(lo < 60 for lo, _ in r):
                eur.append(simp(r, 0.08))
json.dump(dict(K=K, CX=CX, land=d_of(world), eur=d_of(eur), W=X(180), H=Y(-58)), open("geo.json", "w"))
print("ok", len(world), len(eur), os.path.getsize("geo.json"))
