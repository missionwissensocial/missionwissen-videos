# 🏘️ Wem gehört in Wien jede fünfte Wohnung?

Geplant: Do 19.11.2026, 18:00 (Instagram Reel, TikTok, YouTube Short) – **Handbetrieb** (Metricool-Kontingent November 19/20, Alex lädt selbst hoch) · Wahl Alex 19.11. (Thema 8, Nachbar-Format „Warum wohnt man in Wien so günstig?“) · 40,4 s · 122 Wörter · Stimme Theo (eleven_v4), 1,3x

## Sprechtext
Wem gehört in Wien jede fünfte Wohnung – und warum ist das gut für die Miete? Der Stadt Wien selbst. Diese Wohnungen heißen Gemeindewohnungen. Seit rund hundert Jahren baut Wien sie – und hat sie nie an Firmen verkauft. Viele deutsche Städte haben dagegen Wohnungen verkauft. Dresden 2006 sogar alle – an einen Finanzinvestor, der Gewinn machen will. Und warum ist eine Gemeindewohnung günstig? Die Stadt will mit der Miete keinen Gewinn machen. Und das Gesetz deckelt, wie viel Miete sie verlangen darf. Einziehen dürfen nicht nur Menschen mit wenig Geld. Auch wer normal verdient und eine Wohnung braucht, kann sich bewerben. So zahlen viele Wiener deutlich weniger als bei privaten Vermietern. Und im teuren München? Dort gehört der Stadt nicht mal jede zehnte Wohnung.

## Belege
| Aussage | Bewertung (unabh. Faktencheck) | Quelle |
|---|---|---|
| Wien: rund 220.000 Gemeindewohnungen (Wiener Wohnen, Stadt Wien) | korrekt | Wohnberatung Wien, Folder 2026 https://wohnberatung-wien.at/fileadmin/wohnberatung/downloads/broschueren/2026/wbw_folder2026_fin.pdf ; https://www.geschichtewiki.wien.gv.at/Wiener_Wohnen |
| „jede fünfte“: 21 % aller Wiener Haushalte wohnen in einer Gemeindewohnung (2024) | vereinfacht-vertretbar (Haushalte ≈ Wohnungen) | Statistik Austria, Wohnen 2024 https://www.statistik.at/fileadmin/publications/Wohnen_2024_Web-barrierefrei.pdf |
| seit rund 100 Jahren (Wohnbauprogramm 1923; Pause 2004–2015) | vereinfacht-vertretbar | https://socialhousing.wien/tools/municipal-housing-in-vienna |
| nie an Firmen verkauft (keine Privatisierung; Volksbefragung 2013) | vereinfacht-vertretbar | https://www.vienna.at/diskussion-um-verkauf-der-gemeindewohnungen-in-wien/4128120 |
| Viele deutsche Städte haben Wohnungen verkauft (Kiel 1999, Berlin GSW 2004, Dresden 2006) | vereinfacht-vertretbar | https://www.bpb.de/themen/stadt-land/stadt-und-gesellschaft/64428/nicht-jede-rechnung-geht-auf/ |
| Dresden 2006: WOBA mit gesamtem Bestand (~48.000 Wohnungen) an Fortress | korrekt | Amtsblatt Dresden 2006/KW11 https://www.dresden.de/media/pdf/amtsblatt/archiv/2006/ddamt-2006-kw11.pdf |
| Kein Gewinnziel + gesetzlicher Mietdeckel (MRG Richtwert/Kategoriemiete) | vereinfacht-vertretbar (Formulierung nach Faktencheck angepasst) | https://www.vienna.at/miete-im-wiener-gemeindebau-nachste-zwei-jahre-keine-index-anpassung/8397718 |
| Auch Normalverdiener mit Bedarf (Einkommensgrenze 1 Person 61.280 € netto/Jahr, 2 J. Hauptwohnsitz, begründeter Wohnbedarf) | vereinfacht-vertretbar | Wohnberatung Wien Folder 2026 / Aufnahmeblatt 2026 |
| Gemeindewohnung Ø 5,4 € vs. private Hauptmiete Ø 9,1 € pro m² ohne BK (Österreich 2024, im Bild gekennzeichnet) | korrekt (Österreich-Wert) | Statistik Austria, Wohnen 2024, Übersicht 4.4 |
| München: rund 75.000 städtische Wohnungen von 842.907 (≈ 8,9 %) | korrekt | https://stadt.muenchen.de/news/260616_wohnen.html ; Wohnungsmarktflyer 2025 |
Bild: Straßenszene „SZENE SCHEMATISCH“ gekennzeichnet.

## Gates
- Faktencheck (separater Agent): nichts schlechter als „vereinfacht-vertretbar“. Übernommen: „nie verkauft“ → „nie an Firmen verkauft“, „ihre Wohnungen“ → „Wohnungen“, Gesetzesdeckel ergänzt, „wenn er Bedarf hat“ → „und eine Wohnung braucht“.
- Erstzuhörer-Test: 2 Runden. Runde 1: 2× hoch (fehlende Mietzahl im Hook, Dresden ohne Folge) → Hook umgebaut (Rätsel „Wem gehört …?“), München-Vergleich als Auflösung, Investor „der Gewinn machen will“. Runde 2: kein „hoch“. Bewusst belassen (mittel): keine konkrete Mietzahl im Sprechtext (Länge/Zahlen-Regel – im Bild als Balken 5,40 € vs. 9,10 €), keine Aussage, ob Stadtwohnungen den ganzen Markt dämpfen (nicht sauber belegbar).
- Transkript = Script (Scribe, 122 Wörter identisch).

## Build
toolkit/build_wien.py + geo_wien.py + sfx_wien.py (auf Basis build_pfand.py): Karte DE/AT mit Wien + 5 Häusern (1 lila) → Kameraflug in Wiener Straße (5 Häuser, lila Gemeindebau als Hauptdarsteller mit rot-weiß-roter Fahne + Schild GEMEINDEWOHNUNGEN) → Zähler 100 JAHRE, Gemeindebauten wachsen im Hintergrund, „ZU VERKAUFEN“ wird durchgestrichen, Stempel NIE VERKAUFT → Flug nach Deutschland: Kiel/Berlin/Dresden verkauft → Dresden 2006, 10 Häuser werden grau → Finanzinvestor → zurück nach Wien: Miete = Kosten + Gewinn, Gewinn fällt weg, Deckel „Gesetz“ → Menschen gehen in den Gemeindebau → Balken 5,40 € vs. 9,10 € → Flug nach München → Auflösung WIEN JEDE 5. vs. MÜNCHEN NICHT MAL JEDE 10. (Häuserreihen füllen sich).
