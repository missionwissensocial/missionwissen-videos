# 📜 Wie und wo wurde die Schrift erfunden? – Menschheitsgeschichte #7

Geplant: Fr 20.11.2026, 16:00 (Freitags-Slot; Instagram Reel, TikTok, YouTube Short) – **Handbetrieb** (Metricool-Kontingent November 19/20, Alex lädt selbst hoch) · Wahl Alex 20.11. (Thema 2, mit seiner Änderung „wie und wo“ statt „wofür“) · 44,7 s · 118 Wörter · Stimme Theo (eleven_v4), 1,3x

## Sprechtext (wie im Video)
Wie und wo wurde die Schrift erfunden? Eine der ersten Schriften entstand vor rund 5.300 Jahren in Uruk – im heutigen Irak. Dort verwalteten Tempel riesige Vorräte: Gerste, Bier und Vieh. Aber wer hat wie viel geliefert? Zuerst halfen kleine Zählmarken aus Ton. Die Marken reisten mit der Ware mit – versiegelt in einer Tonkugel, damit keiner schummelt. Damit man trotzdem sah, was drin ist, drückte man jede Marke vorher außen in den weichen Ton. Die Abdrücke allein reichen ja! Also kamen die Zeichen direkt auf eine Tontafel. Die Abdrücke zeigten, wie viel. Kleine Bilder zeigten, was – ein Rinderkopf für Rind. Mit dem Schilfgriffel wurden daraus keilförmige Striche: die Keilschrift. Die Schrift begann also nicht mit Geschichten – sondern mit Lieferlisten.

Hinweis Audio: Vertont wurde eine 133-Wörter-Fassung (59,9 s → 46,1 s bei 1,3x, über dem 45-s-Ziel). Statt neu zu vertonen, wurden in echten Sprechpausen fünf Stellen herausgeschnitten („Eine Marke stand etwa für einen Korb Gerste.“, „Dann merkte man:“, „Neu war:“, „etwa“, „später“; Schnittpunkte in cuts.json des Builds, Crossfade 12 ms). Das Transkript-Gate lief auf der geschnittenen Datei: Scribe = Sprechtext oben (118 Wörter).

## Belege
| Aussage | Bewertung (unabh. Faktencheck) | Quelle |
|---|---|---|
| Eine der ersten Schriften, um 3300 v. Chr. (≈ 5.300 Jahre), Uruk im heutigen Irak | korrekt / vereinfacht-vertretbar – „eine der ersten“, weil Ägypten (Abydos, Grab U-j, ca. 3320–3150 v. Chr.) fast gleichzeitig ist | Zand, Heidelberg „5300 Jahre Schrift“ https://5300jahreschrift.mtk-online.urz.uni-heidelberg.de/artikel/5300jahre_schrift_zand_schriftentwicklung_mesopotamien.pdf ; Met https://www.metmuseum.org/essays/the-origins-of-writing ; https://www.historyofinformation.com/detail.php?id=3428 |
| Tempel/Institutionen verwalteten Gerste, Bier, Vieh | korrekt | Englund 2011 (CDLI) https://cdli.ucla.edu/staff/englund/publications/englund2011a.pdf ; Sauer https://5300jahreschrift.materiale-textkulturen.de/artikel/5300jahre_schrift_sauer_archaische_keilschriftlisten.pdf |
| Zählmarken (Tokens) aus Ton als Vorläufer | vereinfacht-vertretbar | Englund 2011; CDLJ 2023-2 https://cdli.earth/articles/cdlj/2023-2 |
| Marken versiegelt in Tonkugel (Bulle), außen abgedrückt; Schutz vor Manipulation | korrekt / vereinfacht-vertretbar (Zweck ist Deutung) | Englund 2011; Schmandt-Besserat 1977 https://undena.com/EL-UP/Schmandt_Besserat_1977_Archaic_Recording_System_-_SMS_1.2.pdf |
| Abdrücke reichen → Zeichen direkt auf Tontafel; Abdrücke = Menge | vereinfacht-vertretbar (für Zahlzeichen breit akzeptiert; weitergehende Token-These umstritten) | Englund 2011; Zimansky 1993 https://urkesh.org/attach/Zimansky1993.pdf |
| Bildzeichen, z. B. Rinderkopf für Rind (GU4) | korrekt | https://en.wiktionary.org/wiki/%F0%92%84%9E |
| Schilfgriffel → keilförmige Striche = Keilschrift | korrekt / vereinfacht-vertretbar | Met (s. o.); Zand (s. o.) |
| Erste Texte = Listen (ca. 80–85 % Verwaltung, Rest Wortlisten), keine Literatur | korrekt | Sauer (s. o.); Englund 2011 |
Bild: „DARSTELLUNG SCHEMATISCH · ZÄHLMARKEN UND ZEICHEN VEREINFACHT“, Karte Natural Earth.

## Gates
- Faktencheck (separater Agent): nichts schlechter als „vereinfacht-vertretbar“ nach Korrektur. Übernommen: „wurde in Uruk erfunden“ → „Eine der ersten Schriften entstand … in Uruk“ (Ägypten fast gleichzeitig); „ein Stein = ein Schaf“ → „eine Marke = ein Korb Gerste“ (später beim Kürzen ganz gestrichen).
- Erstzuhörer-Test: 3 Runden. R1: 3× hoch (Tonkugel-Satz: wer schummelt, warum Kugel, Bezug „sie“) → umgebaut. R2: 2× hoch (Kugel reist mit Ware, Bezug) → „Die Marken reisten mit der Ware mit …“, „jede Marke“. R3: kein „hoch“; mittel bewusst belassen: warum die Kugel Schummeln verhindert (wird im Bild gezeigt: Deckel + Siegelrolle + Stempel VERSIEGELT), Trennung „wie viel“/„was“ (im Bild: „5 × RIND“).
- Transkript (geschnittene Fassung) = Sprechtext.
- Storyboard-Selbstcheck + Zwischenframes (Kameraflug, Zoom in die Werkbank, Kugel → Tafel, Griffel) ok; Frame 0 = Hook-Szene mit Roboter, Headline, Serien-Chip.
- Dauerton-Gate: sfx.py ohne Abbruch, längste gleichbleibende Strecke 0,5 s.
- Länge 44,7 s (≤ 45), Lautheit −14,6 LUFS.

## Build
toolkit/build_schrift.py + sfx_schrift.py (Karte aus geo_stadt.py, Basis build_stadt.py): Karte Naher Osten mit Tontafel + „?“ bei Uruk (Hook) → Kameraflug nach Uruk, Zähler 5.300 JAHRE ALT → Tempel (Zikkurat) mit Gerstensack, Bierkrug, Rind; Lieferpunkte laufen aus den Dörfern zum Tempel, „?“ → Maßstabswechsel: Zoom in den Tempel auf eine Millimeterpapier-Werkbank → 5 Zählmarken (Hauptdarsteller lila) → fliegen in eine Tonkugel, Deckel, Siegelrolle, Stempel VERSIEGELT → eine Marke nach der anderen drückt außen Abdrücke → Marken innen verschwinden, Abdrücke leuchten → Kugel wird zur Tontafel, Abdrücke wandern mit → Zähler „5“ → Rinderkopf zeichnet sich, „5 × RIND“ → Schilfgriffel setzt Keile, Rinderkopf wird Keilschrift → Tafel wächst zur Liste, „✕ KEINE GESCHICHTEN“ → Stempel LIEFERLISTE → Endcard (+ Folgen / 🔖 Speichern).
