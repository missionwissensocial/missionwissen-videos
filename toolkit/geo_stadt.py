"""Karte Naher Osten (Natural Earth 50m, Public Domain): Land, Flüsse (Nil, Euphrat, Tigris, Jordan), Seen (Totes Meer, See Genezareth) -> geo.json.
Plattkarte mit Breitenkorrektur CX=cos(31°)."""
import json, os, math
NE = os.path.expanduser("~/mw/geo/ne/geojson"); K = 3.0; CX = math.cos(math.radians(31))
X = lambda lon: (lon + 180) * K * CX; Y = lambda lat: (90 - lat) * K
BB = (14, 62, 8, 46)  # lon0, lon1, lat0, lat1
def inbb(r): return any(BB[0] <= lo <= BB[1] and BB[2] <= la <= BB[3] for lo, la in r)
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def d_of(rs, close=True): return "".join("M" + "L".join(f"{X(lo):.2f} {Y(la):.2f}" for lo, la in r) + ("Z" if close else "") for r in rs)
land = json.load(open(f"{NE}/ne_50m_land.geojson"))
lr = [r for f in land["features"] for r in rings(f["geometry"]) if inbb(r)]
lakes = json.load(open(f"{NE}/ne_50m_lakes.geojson"))
lk = [r for f in lakes["features"] if (f["properties"].get("name") or "") in ("Dead Sea", "Sea of Galilee", "Lake Nasser", "Lake Tharthar")
      for r in rings(f["geometry"]) if inbb(r)]
riv = json.load(open(f"{NE}/ne_50m_rivers_lake_centerlines.geojson"))
rv = {}
for f in riv["features"]:
    n = f["properties"].get("name") or ""
    if n in ("Nile", "Euphrates", "Tigris", "Jordan", "Shatt al Arab"):
        g = f["geometry"]; ls = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        rv.setdefault(n, []).extend(l for l in ls if inbb(l))
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
br = []
for f in cty["features"]:
    for r in rings(f["geometry"]):
        if inbb(r): br.append(r)
json.dump(dict(K=K, CX=CX, land=d_of(lr), lakes=d_of(lk), cty=d_of(br),
               rivers={k: d_of(v, False) for k, v in rv.items()}), open("geo.json", "w"))
print("ok", len(lr), len(lk), {k: len(v) for k, v in rv.items()}, os.path.getsize("geo.json"))
