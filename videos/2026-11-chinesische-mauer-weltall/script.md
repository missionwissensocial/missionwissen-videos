# Kann man die Chinesische Mauer vom Weltall aus sehen? (Post: 16.11.2026, 18:00)

## Sprechtext (Theo, eleven_v4, 1 Variante, 1,3x → 39,9 s, Video 43,9 s)
Kann man die Chinesische Mauer vom Weltall aus sehen? Fast jeder hat schon mal gehört: Ja, das geht.
Die Mauer ist zwar über 20.000 Kilometer lang – alle Abschnitte zusammengezählt. Aber meist nicht mal sechs Meter breit.
Die Raumstation ISS kreist rund 400 Kilometer über der Erde. Von dort die Mauer zu entdecken ist so, als würdest du ein Haar aus sieben Metern Entfernung suchen.
Und die Mauer ist aus Steinen und Erde der Umgebung gebaut. Sie hat also fast dieselbe Farbe wie der Boden.
Chinas erster Astronaut sagte 2003: „Ich habe sie nicht gesehen.“
Und vom Mond aus? Der Mond ist fast tausendmal weiter weg als die ISS. Keine Chance.
Der Irrtum stand schon 1932 in einem Zeitungs-Comic. Damals konnte das niemand überprüfen. Seitdem wird er einfach weitererzählt.

(128 Wörter; Transkript-Gate: Scribe-Text identisch. Wahl Alex 15.11.: Backlog-Vorschlag „Kann man die Chinesische Mauer vom Weltall aus sehen?“)

## Gates
- Faktencheck (separater Agent): alle Aussagen korrekt bzw. vereinfacht-vertretbar. Haar-Analogie nachgerechnet: 6 m / 400 km = 1,5·10⁻⁵ rad ≈ Haar 0,1 mm / 7 m (1,4·10⁻⁵ rad). Mond 384.400 km / 400 km ≈ 960 → „fast tausendmal“. Idee ist älter als 1932 (Stukeley 1754) – Script sagt nur, dass sie 1932 im Comic stand.
- Erstzuhörer-Test (2 Runden): Runde 1 „mittel“ behoben (Bezugsgröße „tausendmal weiter weg als die ISS“, Bogen Comic ↔ Mythos). Runde 2 „mittel“ (warum glaubt es jeder, wenn nur Comic?) behoben mit „Damals konnte das niemand überprüfen. Seitdem wird er einfach weitererzählt.“ Rest nur „gering“.

## Bühne
Durchgehende Kamera über eine orthografische Erde (Natural Earth 50m), Mauer lila ab Frame 0 → Zoom auf Nordchina, Mauerabschnitte zeichnen sich (SCHEMATISCH), Zähler 21.196 KM → Sturzflug nach Badaling → Querschnitt Mauer (6 M) vs. Auto (4,5 M) → zurück auf den Globus: ISS-Bahn massstabsgetreu (400 KM), ISS als Hauptdarsteller fährt auf der Bahn → Zoom in die ISS: Bullauge mit Suchring, Mauer als Haarlinie → Haar-Vergleich Auge – 7 M – Haar (Lupe 0,1 MM) → Bullauge nah: Steine fliegen in die Mauer, Farbfelder MAUER ≈ BODEN → Globus mit Kapsel, Zitat Yang Liwei → durchgehender Rauszoom bis zum Mond (massstabsgetreu), ≈ 1.000 × mit Balken → Stempel „VOM MOND: KEINE CHANCE“ → eigene Zeitung 1932 mit Comic-Panel, Zeitstrahl 1932 → 1961 → Mythos verbreitet sich (Icons). Build: toolkit/build_mauer.py + geo_mauer.py + sfx_mauer.py (nur kurze Akzente; Dauerton-Gate bestanden, längste gleichförmige Strecke 0,9 s). Lautheit −14,3 LUFS.

## Belege
| Aussage | Quelle |
|---|---|
| 21.196 km, alle Abschnitte (Survey 2012, Staatl. Kulturerbe-Verwaltung) | https://www.cbc.ca/news/world/great-wall-of-china-even-longer-than-previously-thought-1.1263111 |
| meist unter 6 m breit; ISS ≈ 400 km; Comic 1932 | https://www.livescience.com/34212-great-wall-of-china-only-manmade-object-visible-from-space.html |
| Aus niedriger Umlaufbahn mit bloßem Auge i. d. R. nicht sichtbar, vom Mond sicher nicht; Material ähnlich gefärbt wie Umgebung | https://www.nasa.gov/wp-content/uploads/static/history/PDFs/great_wall_less_great_from_space.pdf |
| Yang Liwei 2003 (Shenzhou 5): Mauer nicht gesehen; Ripley's-Cartoon 1932 | https://www.scientificamerican.com/article/is-chinas-great-wall-visible-from-space/ · https://www.aljazeera.com/news/2003/10/17/chinas-spaceman-shatters-a-myth |
| Mondabstand 384.400 km; Gagarin 1961 | Standardwissen, Faktencheck-Agent |
| Karte | Natural Earth (Public Domain) |
