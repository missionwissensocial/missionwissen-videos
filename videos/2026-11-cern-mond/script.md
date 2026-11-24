# 🌙 Mega-Projekte #2: Die größte Maschine der Welt – vom Mond gedehnt? (LHC am CERN)

Wahl Alex (24.11.2026): Vorschlag 2 aus der Mega-Projekte-Ideenliste (Teilchenbeschleuniger CERN). Länge nicht vorgegeben → Damm-Format.
Länge: 94,2 s (Sprechtext 90,8 s nach 1,3x + Endcard), 278 Wörter. Stimme: Theo Teacher (eleven_v4, 1 Variante).
Slot: Mi 25.11.2026, 18:00 – Handbetrieb (Metricool-Kontingent Nov. 20/20 verbraucht, Alex lädt selbst hoch).

## Sprechtext
Die größte Maschine der Welt wird vom Mond gedehnt. Wie kann das sein?
Die Maschine ist ein Ring, 27 Kilometer lang, rund 100 Meter unter der Erde. Er liegt an der Grenze zwischen der Schweiz und Frankreich, am Forschungszentrum CERN.
Es ist ein Teilchenbeschleuniger. Er bringt Protonen, winzige Bausteine von Atomen, fast auf Lichtgeschwindigkeit. Über 11.000 Mal pro Sekunde fliegen sie einmal ganz um den Ring.
Damit sie in der Kurve bleiben, lenken über 1.200 riesige Magnete sie. Diese Magnete werden auf minus 271 Grad gekühlt, kälter als im Weltall. Nur so fließt der Strom in ihnen ohne Verlust, und sie werden stark genug.
Zwei Teilchenstrahlen rasen in entgegengesetzte Richtungen. An vier Stellen lässt man sie frontal zusammenprallen. Aus der Wucht des Aufpralls entstehen für einen winzigen Moment ganz neue Teilchen. So wollen Forscher herausfinden, woraus unsere Welt besteht. 2012 haben sie so das berühmte Higgs-Teilchen entdeckt.
Und der Mond? Er zieht nicht nur am Meer, sondern auch am festen Boden. Der Boden wölbt sich dabei um bis zu 25 Zentimeter. Der Ring wölbt sich mit und wird dabei gedehnt und wieder gestaucht, um etwa einen Millimeter.
Klingt nach nichts. Aber die Magnete rücken dadurch ein winziges Stück auseinander. Die Teilchen fliegen nicht mehr genau mittig hindurch, und ihre Energie ändert sich ein kleines bisschen. Die Forscher müssen aber genau wissen, mit welcher Wucht die Teilchen zusammenprallen. Deshalb wird die Maschine laufend nachgeregelt, damit die Teilchen in der Mitte bleiben.
Übrigens: Als der Ring 2008 startete, hatten viele Angst, er könnte ein schwarzes Loch erzeugen. Doch aus dem Weltall prasseln seit Milliarden Jahren Teilchen mit noch mehr Wucht auf die Erde. Und die Erde gibt es immer noch.

## Belege
| Aussage | Quelle |
|---|---|
| Größte Maschine der Welt; 26.659 m Umfang; ~100 m tief (50–175 m); Grenze CH/FR | home.cern FAQ „Facts and figures about the LHC“; Guinness World Records „Largest machine“ |
| 11.245 Umläufe/s, 99,9999991 % c | home.cern FAQ |
| 1.232 Dipolmagnete; 1,9 K = −271,3 °C, kälter als das Weltall (2,7 K); Supraleitung | home.cern FAQ |
| 4 Kollisionspunkte (ATLAS, CMS, ALICE, LHCb) | home.cern |
| Higgs-Entdeckung 4.7.2012 | home.cern Higgs-FAQ |
| Erdgezeiten bis 25 cm, Umfang ~1 mm, Energieänderung (LEP-Messung im selben Tunnel); LHC: 1,1 mm Spitze-Spitze | J. Wenninger, LEP-Gezeitenbericht (jwenning.web.cern.ch/documents/EnergyCal/tide_slrep.pdf); Wenninger PRAB „LHC beam energy“ |
| LHC wird laufend nachgeregelt (Radial-Loop/Orbit-Korrektur) | home.cern 2012 „Full moon pulls on the LHC“; OMC-Vortrag 2025 (indico.cern.ch) |
| Schwarzes-Loch-Angst 2008, kosmische Strahlung mit höheren Energien | LSAG-Bericht 2008 (arXiv:0806.3414); CERN Public Archive „Safety“ |
| Karte, Querschnitt, Magnet-Nahansicht, Erde/Mond | SCHEMATISCH, stark übertrieben (gekennzeichnet) |

## Gates
- Faktencheck (2 unabhängige Agenten): alles korrekt oder vereinfacht-vertretbar. Umgesetzt: „ein paar Dezimeter“ → „bis zu 25 Zentimeter“, „verbogen“ → „gedehnt“, „je nachdem wo der Mond steht“ → „laufend nachgeregelt, damit die Teilchen in der Mitte bleiben“, Schluss „schwarzes Loch nie entstanden“ → „die Erde gibt es immer noch“. Bewusst vereinfacht: „Magnete rücken auseinander“ (eigentlich Umfangsänderung, Bahn außermittig durch Quadrupole), Sonne trägt ~1/3 zu den Gezeiten bei (Hook nennt nur den Mond).
- Erstzuhörer-Test: 3 Runden. R1: 2× hoch (Energieänderung unerklärt, schwarzes Loch ohne Bezug) → behoben. R2: 4× hoch im Mond-Teil → Kausalkette ausformuliert. R3: keine „hoch“; 3× mittel → umgesetzt (Zweck „woraus unsere Welt besteht“, „wölbt sich mit … gedehnt und gestaucht“, „Forscher müssen genau wissen, mit welcher Wucht …“).
- Transkript (Scribe) = Script, 278 Wörter.
- SFX-Gate: kein Sound > 1,5 s; längste Strecke ohne Pause 1,4 s.
- Lautheit −14,2 LUFS. Frame 0 = Hook-Szene (kein eingebranntes Thumbnail).
- Länge 94 s: bewusst im Damm-Format (Alex: „mehr solcher Videos wie Drei-Schluchten-Damm“), über der 45-s-Regel.

Build: toolkit/build_cern.py (+ stage_cern.js, sfx_cern.py, thumb_cern.py). Bühne: 4 Ebenen (Karte, Querschnitt, Magnet-Nahansicht, Erde+Mond) mit Zoom-Überblendungen.
