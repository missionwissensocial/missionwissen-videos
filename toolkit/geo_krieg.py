"""Weltkarte (Natural Earth 110m, Public Domain) + Länder-Sets WK2 (SCHEMATISCH, heutige Grenzen) -> geo.json."""
import json, os
NE = os.path.expanduser("~/mw/geo/ne/geojson"); K = 3.0
X = lambda lon: (lon + 180) * K; Y = lambda lat: (90 - lat) * K
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in r) + "Z" for r in rs)
land = json.load(open(f"{NE}/ne_110m_land.geojson"))
lr = [r for f in land["features"] for r in rings(f["geometry"]) if max(la for _, la in r) > -58]
cty = json.load(open(f"{NE}/ne_110m_admin_0_countries.geojson"))
names = {f["properties"]["NAME"] for f in cty["features"]}
EU = ["Poland", "Austria", "Czechia", "Slovakia", "France", "United Kingdom", "Belgium", "Netherlands", "Luxembourg", "Denmark",
      "Norway", "Italy", "Greece", "Albania", "Serbia", "Croatia", "Slovenia", "Bosnia and Herz.", "Montenegro", "North Macedonia", "Kosovo",
      "Hungary", "Romania", "Bulgaria", "Finland", "Estonia", "Latvia", "Lithuania", "Belarus", "Ukraine", "Moldova"]
WORLD = ["Russia", "Japan", "China", "Mongolia", "North Korea", "South Korea", "Taiwan", "Philippines", "Indonesia", "Malaysia", "Brunei",
         "Myanmar", "Thailand", "Vietnam", "Laos", "Cambodia", "India", "Bangladesh", "Pakistan", "Sri Lanka", "Papua New Guinea", "Solomon Is.",
         "Australia", "New Zealand", "United States of America", "Canada", "Mexico", "Brazil", "Egypt", "Libya", "Tunisia", "Algeria", "Morocco",
         "Ethiopia", "Eritrea", "Somalia", "Somaliland", "Kenya", "South Africa", "Iran", "Iraq", "Syria", "Lebanon", "Madagascar"]
for n in EU + WORLD + ["Germany"]: assert n in names, n
sel = lambda L: d_of([r for f in cty["features"] if f["properties"]["NAME"] in L for r in rings(f["geometry"])])
json.dump(dict(K=K, land=d_of(lr), de=sel(["Germany"]), pl=sel(["Poland"]), eu=sel(EU + ["Germany"]), world=sel(WORLD),
               W=X(180), H=Y(-58)), open("geo.json", "w"))
print("ok", len(EU), len(WORLD))
