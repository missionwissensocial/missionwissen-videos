"""Europakarte (Natural Earth 50m, Public Domain) + historische Umrisse (SCHEMATISCH, handgezeichnet) -> geo.json.
Projektion: Plattkarte, K=3, lon -180..180 (wie geo_reiche/geo_krieg). Historische Flächen werden im Build per Land-clipPath zugeschnitten."""
import json, os, random
import numpy as np
from scipy.spatial import Voronoi
from matplotlib.path import Path as MPath
NE = os.path.expanduser("~/mw/geo/ne/geojson"); K = 3.0; CX = 0.64  # Breitenkorrektur ~cos(50°) für Mitteleuropa
X = lambda lon: (lon + 180) * K * CX; Y = lambda lat: (90 - lat) * K
BOX = (-12, 33, 32, 62)  # lon0, lat0, lon1, lat1 (Ausschnitt Europa)
def rings(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
def inbox(r): return any(BOX[0] - 8 < lo < BOX[2] + 8 and BOX[1] - 8 < la < BOX[3] + 8 for lo, la in r)
def d_of(rs): return "".join("M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in r) + "Z" for r in rs)
land = json.load(open(f"{NE}/ne_50m_land.geojson"))
lr = [r for f in land["features"] for r in rings(f["geometry"]) if inbox(r)]
cty = json.load(open(f"{NE}/ne_50m_admin_0_countries.geojson"))
de = [r for f in cty["features"] if f["properties"]["NAME"] == "Germany" for r in rings(f["geometry"])]
assert de
poly = lambda pts: "M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in pts) + "Z"
# --- Vertrag von Verdun 843 (schematisch) ---
WEST = [(-1.8, 43.3), (-9, 43.5), (-6, 48.6), (1.5, 51), (3.3, 51.4), (4.5, 50.5), (4.8, 49.5), (5, 48), (4.8, 46.5), (4.8, 45), (4.6, 43.5),
        (3.3, 41.0), (2, 40.5), (0.5, 41.5)]
MID = [(3.3, 51.4), (4, 53.5), (7.2, 54.0), (7.0, 52), (7.6, 50.5), (8.2, 49.5), (8.0, 48), (9.5, 47.3), (10.5, 46.8), (13.7, 46.5), (13.9, 45.4),
       (15.5, 41.5), (14.5, 40.5), (12.0, 41.0), (10.5, 43.8), (8.5, 44.3), (7, 43.2), (4.6, 43.5), (4.8, 45), (4.8, 46.5), (5, 48), (4.8, 49.5), (4.5, 50.5)]
EAST = [(7.2, 54.0), (8.5, 55.0), (11, 54.6), (11.5, 53.2), (12, 51.5), (13.5, 50.3), (14, 49), (16, 48.2), (16.5, 47.5), (15.5, 46.5), (13.7, 46.5),
        (10.5, 46.8), (9.5, 47.3), (8.0, 48), (8.2, 49.5), (7.6, 50.5), (7.0, 52)]
# --- Heiliges Römisches Reich um 1789 (schematisch) ---
HRR = [(2.6, 51.1), (3.5, 51.6), (6.0, 51.9), (6.8, 53.6), (8.5, 54.0), (9.0, 54.3), (10.9, 54.6), (13, 54.8), (14.3, 54.2), (16.5, 54.7),
       (16.2, 53.2), (15.6, 52.4), (17.5, 51.5), (18.6, 50.0), (18.8, 49.5), (17.2, 48.6), (17.0, 48.0), (16.4, 47.0), (16.0, 46.4), (15.5, 45.4),
       (13.6, 45.3), (12.5, 46.6), (11.0, 45.8), (10.4, 46.5), (9.5, 47.1), (9.6, 47.5), (8.6, 47.7), (7.6, 47.6), (7.6, 48.3), (8.2, 49.0),
       (6.7, 49.2), (6.4, 49.5), (5.8, 49.5), (5.0, 49.8), (4.0, 50.3)]
# --- Deutsches Kaiserreich 1871 (schematisch) ---
KR = [(6.1, 50.7), (6.0, 51.85), (6.8, 52.2), (6.9, 53.8), (8.5, 54.0), (8.4, 55.5), (9.7, 55.5), (10.0, 55.0), (11.5, 54.6), (14.2, 54.3),
      (16.5, 54.8), (18.5, 55.0), (21.0, 55.9), (22.8, 55.0), (22.7, 54.3), (21.0, 54.2), (20.0, 53.2), (19.0, 53.0), (18.3, 52.7), (17.8, 52.0),
      (18.2, 51.3), (18.6, 50.5), (18.8, 50.0), (18.0, 50.0), (17.0, 50.2), (16.3, 50.6), (15.0, 50.8), (14.3, 50.9), (12.4, 50.3), (12.5, 49.7),
      (13.8, 48.8), (13.0, 47.5), (11.0, 47.4), (10.0, 47.5), (9.6, 47.5), (8.6, 47.7), (7.6, 47.6), (7.0, 47.5), (7.1, 48.4), (6.2, 49.0),
      (5.9, 49.5), (6.4, 49.5), (6.4, 50.3)]
# --- innerdeutsche Grenze 1949–1990 (schematisch) ---
BORDER = [(10.9, 54.6), (10.9, 53.95), (10.95, 53.6), (10.6, 53.35), (11.6, 53.05), (10.95, 52.6), (10.6, 51.8), (10.2, 51.3), (9.95, 50.9),
          (10.1, 50.55), (10.7, 50.35), (11.5, 50.4), (12.0, 50.3), (12.2, 50.2)]
EASTSIDE = BORDER + [(16, 50.2), (16, 55.5), (10.9, 55.5)]
WESTSIDE = BORDER + [(12.2, 49.0), (12.2, 47.0), (5, 47.0), (5, 55.5), (10.9, 55.5)]
# --- Flickenteppich: Voronoi-Zellen innerhalb HRR (≈ 300) ---
random.seed(7); np.random.seed(7)
hp = MPath(np.array(HRR))
pts = []
while len(pts) < 300:
    lo, la = random.uniform(2.5, 19), random.uniform(45.2, 55)
    if hp.contains_point((lo, la)): pts.append((lo, la))
far = [(lo, la) for lo in range(-20, 41, 5) for la in (30, 70)] + [(lo, la) for lo in (-20, 40) for la in range(35, 70, 5)]
vor = Voronoi(np.array(pts + far))
cells = []
for i in range(len(pts)):
    reg = vor.regions[vor.point_region[i]]
    if -1 in reg or not reg: continue
    vs = [tuple(vor.vertices[k]) for k in reg]
    cells.append(dict(d=poly(vs), x=round(X(pts[i][0]), 1), y=round(Y(pts[i][1]), 1)))
json.dump(dict(K=K, CX=CX, land=d_of(lr), de=d_of(de), west=poly(WEST), mid=poly(MID), east=poly(EAST), hrr=poly(HRR), kr=poly(KR),
               border="M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in BORDER), eside=poly(EASTSIDE), wside=poly(WESTSIDE),
               cells=cells, W=X(180), H=Y(-58)), open("geo.json", "w"))
print("ok", len(lr), len(cells))
