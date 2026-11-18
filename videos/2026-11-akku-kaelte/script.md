# 🔋 Warum geht dein Handy-Akku in der Kälte so schnell leer?

Gepostet: Mi 18.11.2026, 18:00 (Instagram Reel, TikTok, YouTube Short) · Wahl Alex 17.11. (Thema 7, Galileo-Stil/Backlog) · 39,8 s · 127 Wörter · Stimme Theo (eleven_v4), 1,3x

## Sprechtext
Warum geht dein Handy-Akku in der Kälte so schnell leer? Im Akku wandern winzige Teilchen hin und her: Lithium-Ionen. Nur wenn sie wandern, bekommt dein Handy Strom. Dabei schwimmen sie durch eine Flüssigkeit. Bei Kälte wird diese Flüssigkeit zäh, fast wie Honig. Die Teilchen kommen nur noch langsam voran. Die Folge? Die Spannung sinkt – also der Druck, der den Strom ins Handy schiebt. An dieser Spannung schätzt das Handy die Prozente. Es zeigt weniger an – oder schaltet ab, weil der Druck nicht reicht. Dabei ist noch Energie drin. Wird der Akku wieder warm, kommen die Prozente zurück. Im Winter also: Handy in die Innentasche. Und lade es erst, wenn es wieder warm ist. Sonst stauen sich die langsamen Teilchen und bleiben kleben – der Akku speichert dauerhaft weniger.

## Belege
| Aussage | Bewertung (unabh. Faktencheck) | Quelle |
|---|---|---|
| Lithium-Ionen wandern im Akku, nur dann fließt Strom | korrekt / vereinfacht | https://en.wikipedia.org/wiki/Lithium_polymer_battery |
| Ionen bewegen sich durch flüssigen Elektrolyt (auch Gel-Polymer enthält Flüssigkeit) | vereinfacht-vertretbar | ebd. |
| Kälte: Elektrolyt zäher, Ionen langsamer | vereinfacht-vertretbar | RSC-Review 2025 https://pubs.rsc.org/en/content/articlehtml/2025/eb/d5eb00013k ; wissen.de |
| Innenwiderstand steigt, Spannung sinkt | vereinfacht-vertretbar | Battery University BU-410 https://batteryuniversity.com/article/bu-410-charging-at-high-and-low-temperatures |
| Abschalten trotz Restladung, vorübergehend; bei Wärme wieder normal | korrekt | Apple https://support.apple.com/118431 |
| Nicht unter 0 °C laden – Lithium-Plating, dauerhafter Kapazitätsverlust | korrekt | BU-410 |
Bild: Temperaturen (20° / −10°) und Prozentwerte sind Beispiele, Bühne „SCHEMATISCH“ gekennzeichnet.

## Gates
- Faktencheck (separater Agent): Freigabe ja; „Strom ist nicht weg“ → „Energie“ übernommen.
- Erstzuhörer-Test: 3 Runden. Letzte Runde: kein „hoch“ offen nach Umformulierung („An dieser Spannung …“, „weil der Druck nicht reicht“, „stauen sich … bleiben kleben“). Bewusst belassen (mittel): Warum langsame Teilchen gerade die *Spannung* senken – bewusst nicht vertieft (Länge 40–45 s), im Bild per Manometer gezeigt.
- Transkript = Script (Scribe), Länge 39,8 s ≤ 45 s, −14,2 LUFS, kein Dauerton (nur kurze Akzente), Frame 0 = Hook (kein Thumbnail eingebrannt).

## Build
toolkit/build_akku.py + toolkit/sfx_akku.py: durchgehende SVG-Kamera Handy → Röntgenblick → Akkuzelle (Minus-/Plus-Seite, Elektrolyt, Draht mit Mini-Handy), Hauptdarsteller Ion „Li+“, Tempo-Integration (Ionen werden bei Kälte langsamer), Flüssigkeit färbt sich honiggelb, Schnee, große Temperatur-Zahl 20° → −10° → 20°, Manometer „Spannung“, Prozent-Anzeige 80 → 31 → 10 → AUS → 46, Mantel mit Innentasche, Ladekabel, Belag an der Minus-Seite.
