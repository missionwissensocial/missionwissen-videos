# Warum radeln die Niederländer so viel mehr? (Post: 08.11.2026, 18:00) – Nachbar-Reihe Folge 3

## Sprechtext (Theo, eleven_v4, 1 Variante, 1,3x → 62,2 s, Video 65,7 s)
In den Niederlanden wird viel mehr Fahrrad gefahren als bei uns. Und das liegt nicht nur daran, dass das Land so flach ist. Wie groß der Unterschied zu Deutschland ist, zeige ich dir am Ende. In den Fünfziger- und Sechzigerjahren kauften die Niederländer, wie wir, immer mehr Autos. Radfahrer mussten mitten im Autoverkehr fahren. Anfang der Siebzigerjahre starben dort jedes Jahr über 3.000 Menschen im Straßenverkehr. Darunter Hunderte Kinder. Eltern protestierten auf der Straße. Ihr Motto: Stoppt den Kindermord. Dazu kam 1973 die Ölkrise. Benzin wurde knapp. An zehn Sonntagen war Autofahren sogar verboten. Proteste und Ölkrise brachten die Wende: Die Politik setzte aufs Fahrrad. Ab Mitte der Siebziger bauten Städte wie Den Haag und Delft eigene Radrouten. Heute gibt es dort rund 38.000 Kilometer Radwege, die durch einen Bordstein oder Grünstreifen von den Autos getrennt sind. Fast einmal um die ganze Erde. Denn wer sich sicher fühlt, fährt eher Rad. Also: Nicht nur die Landschaft macht den Unterschied, sondern vor allem sichere Radwege. Und wie groß ist der Unterschied? Von 100 Wegen im Alltag machen die Niederländer 28 mit dem Fahrrad. Wir in Deutschland: 11.

(183 Wörter; Zahlen in der Vertonung ausgeschrieben. Transkript-Gate: Scribe-Text identisch, 186 Wort-Token.)

## Gates
- Unabhängiger Faktencheck (separater Agent): nichts falsch. Umgesetzt: „Die Folge? Delft und Den Haag bauten Radwege“ (Kausalität zu eng) → „Proteste und Ölkrise brachten die Wende … Ab Mitte der Siebziger bauten Städte wie Den Haag und Delft eigene Radrouten“ (Den Haag Demonstrationsroute 1975–79, Delft Fietsroutenetwerk ab ca. 1979); „über 35.000 km“ → „rund 38.000 km“ (KiM 2023); „an mehreren Sonntagen“ → „an zehn Sonntagen“ (4.11.1973–6.1.1974). Hinweis: NL-Wert (KiM, Daten 2022) und DE-Wert (MiD 2023) stammen aus verschiedenen Erhebungen, beide nach Hauptverkehrsmittel je Weg – Größenordnung robust, Quellen im Bild.
- Erstzuhörer-Test: 2 Runden. Runde 1: „hoch“ Übergang Ölkrise→Radwege (behoben), „mittel“ Abstand/Versprechen, Bezugsgröße 35.000 km, „Wege“, Grund nie ausgesprochen (alle behoben: „Unterschied zu Deutschland“, „fast einmal um die Erde“, „im Alltag“, Fazitsatz). Runde 2: „hoch“ Bezug „zusammen sind das 38.000 km“ (behoben: „Radwege, die … getrennt sind“). Bewusst abgewogen (mittel): keine Vergleichszahl zu heutigen Verkehrstoten und keine Aussage, ob die Toten danach sanken (Ursache wäre nicht sauber allein den Radwegen zuzuschreiben; Länge).

## Bühne
Durchgehend: Karte NL/DE (Natural Earth 50m) mit Fahrrad als Hauptdarsteller über NL → Kameraflug hinunter in eine niederländische Straße (Maßstabswechsel): Jahreszähler 1950→1969 + Autos, Rad mitten im Verkehr, „über 3.000“ Verkehrstote, Eltern-Protest mit Schild „STOP DE KINDERMOORD“, 1973 Ölkrise mit Tankanzeige, 10 autofreie Sonntage (Autos weg, Räder auf der Fahrbahn) → Flug zurück auf die Karte nach Den Haag/Delft → wieder in die Straße: Radweg + Grünstreifen + Bordstein wachsen ein, 38.000-km-Zähler, Erde mit Ring (38.000 von 40.000 km), mehr Räder → Karte: 🇳🇱 28 vs. 🇩🇪 11 von 100 als 10×10-Raster. Build: toolkit/build_rad.py + geo_rad.py + sfx_rad.py (eigene Töne: Fahrradklingel, vorbeifahrende Autos, Menge, Tank-„Gluck“).

## Belege
| Aussage | Quelle |
|---|---|
| NL: 28 % aller Wege mit dem Rad (20 % Rad, 8 % E-Bike), Daten 2022 | KiM Fietsfeiten 2023, S. 3 |
| NL: ca. 38.000 km separate (Brom-)Fietspaden (von 153.000 km Radnetz) | KiM Fietsfeiten 2023, S. 12 |
| DE: 11 % aller Wege mit dem Rad (Hauptverkehrsmittel) | Mobilität in Deutschland 2023, Kurzreport S. 4 |
| NL Verkehrstote Höchststand 1972: 3.264; 1971–1973 jeweils > 3.000 | CBS, Tijdlijn verkeer 1972 |
| 1971: über 400 getötete Kinder | The Guardian (2015), Forbes (2019) via Wikipedia „Stop de Kindermoord“ |
| „Stop de Kindermoord“: Bewegung ab 1972 (Artikel Vic Langenhoff), getragen vor allem von Eltern | SWOV; Wikipedia |
| Ölkrise 1973: 10 autofreie Sonntage 4.11.1973–6.1.1974 | MAX Vandaag „De autoloze zondagen in 1973 en 1974“ |
| Den Haag Demonstrations-Fietsroute 1975–1979; Delft Fietsroutenetwerk ab ca. 1979 | SWOV „Hague cycleway pilot project 1975–1979“; TRID 203936 |
| Erdumfang ≈ 40.000 km | allgemein |
