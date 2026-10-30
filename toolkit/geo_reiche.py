"""Weltkarte (Natural Earth 110m, Public Domain) + Reichs-Umrisse (SCHEMATISCH) -> geo.json. Projektion: plattkarte, K=3, lon -180..180."""
import json, os
NE = os.path.expanduser("~/mw/geo/ne/geojson"); K = 3.0
X = lambda lon: (lon + 180) * K; Y = lambda lat: (90 - lat) * K
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in r) + "Z" for r in rs)
land = json.load(open(f"{NE}/ne_110m_land.geojson"))
lr = [r for f in land["features"] for r in rings(f["geometry"]) if max(la for _, la in r) > -58]
cty = json.load(open(f"{NE}/ne_110m_admin_0_countries.geojson"))
BRIT = ["United Kingdom", "Ireland", "Canada", "Australia", "New Zealand", "India", "Pakistan", "Bangladesh", "Myanmar", "Sri Lanka",
        "Malaysia", "Brunei", "Papua New Guinea", "Solomon Is.", "Fiji", "Egypt", "Sudan", "S. Sudan", "Kenya", "Uganda", "Tanzania", "Zambia",
        "Zimbabwe", "Malawi", "Botswana", "South Africa", "Lesotho", "eSwatini", "Namibia", "Nigeria", "Ghana", "Sierra Leone", "Gambia",
        "Somaliland", "Iraq", "Jordan", "Israel", "Palestine", "Kuwait", "Qatar", "United Arab Emirates", "Guyana", "Belize", "Jamaica",
        "Bahamas", "Trinidad and Tobago", "Cyprus", "Falkland Is."]
br = [r for f in cty["features"] if f["properties"]["NAME"] in BRIT for r in rings(f["geometry"])]
assert len({f["properties"]["NAME"] for f in cty["features"] if f["properties"]["NAME"] in BRIT}) == len(BRIT)
ROME = [(-10,36),(-10,44),(-5,48.5),(-5.8,50),(-5.4,54.9),(-2,55.8),(1,55.5),(4,51.8),(6.5,51.5),(7.5,50.3),(8.5,49.5),(9.5,49),(10.5,48.5),
        (13,48.2),(16.5,48.2),(19,47.7),(19,46),(21,45),(22.5,48),(26,48),(28,45.5),(29.8,45.3),(31,44),(36,42),(41.5,41.5),(45,41),(47,40),
        (48,37),(48.5,31),(48,29.5),(44,30),(40,31),(37,28),(35,27.5),(33.5,24),(31,24),(29,28),(25,30),(20,30.5),(15,31),(10,31.5),(8,32),
        (6,34),(2,35),(-2,34.5),(-6,33.5),(-10,34)]
MONG = [(130,34),(130,43),(135,48),(132,53),(120,53),(105,55),(90,56),(75,57),(60,58),(45,59),(36,58),(30,56),(25,52),(24,48),(27,46),(29,45),
        (33,44.5),(38,45),(40,43),(42,41.5),(36,40),(30,38),(33,36.5),(36,36),(38,34),(41,32.5),(45,30),(48,29.5),(51,28),(56,26),(60,25.5),
        (64,25.5),(67,27),(70,32),(73,34),(75,36),(78,36),(80,33),(80,30),(86,28),(92,27.5),(97,28),(98,24),(100,22),(106,22),(110,20),(117,23),
        (121,28),(122,31),(124,37),(126,34),(129,34.5)]
poly = lambda pts: "M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in pts) + "Z"
json.dump(dict(K=K, land=d_of(lr), brit=d_of(br), rome=poly(ROME), mong=poly(MONG), W=X(180), H=Y(-58)), open("geo.json", "w"))
print("ok", len(lr), len(br))
