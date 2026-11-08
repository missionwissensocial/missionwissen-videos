"""Karte für 9. November: Europa-Land, heutiges DE, Kaiserreich 1918 (schematisch), innerdeutsche Grenze, Synagogen-Punkte (schematisch)."""
import json, os, random, re, sys
sys.path.insert(0, "/home/claude/missionwissen-videos/toolkit")
src = open("/home/claude/missionwissen-videos/toolkit/geo_deutschland.py").read()
src = src.split("# --- Flickenteppich")[0]   # nur Daten/Projektion
ns = {}; exec(src, ns)
X, Y, de, lr, d_of, poly = ns["X"], ns["Y"], ns["de"], ns["lr"], ns["d_of"], ns["poly"]
import numpy as np
from matplotlib.path import Path as MPath
# Punkte in DE (größter Ring)
ring = max(de, key=len); mp = MPath(np.array(ring))
random.seed(11); pts = []
while len(pts) < 70:
    lo, la = random.uniform(6, 15), random.uniform(47.4, 54.9)
    if mp.contains_point((lo, la)) and all((lo-a)**2+(la-b)**2 > 0.28 for a, b in pts): pts.append((lo, la))
# Synagogen-Punkte: grob nach Größe der jüdischen Gemeinden gewichtet ist nicht belegt -> gleichmäßig, als SCHEMATISCH gekennzeichnet
json.dump(dict(K=ns["K"], CX=ns["CX"], land=d_of(lr), de=d_of(de), kr=poly(ns["KR"]),
               border="M" + "L".join(f"{X(lo):.1f} {Y(la):.1f}" for lo, la in ns["BORDER"]), eside=poly(ns["EASTSIDE"]), wside=poly(ns["WESTSIDE"]),
               syn=[[round(X(lo), 2), round(Y(la), 2)] for lo, la in pts]), open("geo.json", "w"))
print("ok", len(pts))
