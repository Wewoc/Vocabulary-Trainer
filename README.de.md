# Vocabulary-Trainer

[English](README.md) · **Deutsch**

Ein Vokabeltrainer für Schulkinder, der **mit deinen eigenen Listen** übt.
Er bringt keine Vokabeln mit: Die Eltern holen die Wörter aus dem Schulbuch,
von der Lehrkraft oder aus einer Excel-Tabelle und **importieren sie als
CSV**. Der Import zeigt vorher eine Vorschau, was hinzugefügt wird, und
überschreibt nie vorhandene Einträge. Jedes Kind bekommt einen eigenen
Programmordner mit eigener Liste und eigenem Lernstand.

Lokal und offline: keine Cloud, kein Konto, keine Drittanbieter. Die App
selbst verbindet sich nie mit dem Internet. Das Netz berührt sie nur, wenn man
einen Link zu den Projektseiten auf GitHub anklickt — im **Info**-Fenster oder
in der dort geöffneten Dokumentation —, dann öffnet sich der Browser.

> **Stand:** Entwicklungsversion `0.0.18`. Der letzte gebaute Release ist
> `v0.1.0` (erste Beta, ein eigenständiges Windows-Programm, auf einem echten
> Windows-PC getestet). Alles, was seitdem dazukam — PIN, Protokoll und
> Absturzberichte, Import-Vorschau, Report-Export, Suche, Artikel-Sprachen,
> Info-Fenster — ist durch automatische Tests abgedeckt, wurde aber **noch
> nicht als Programm gebaut und auf einem echten PC von Hand geprüft**. Bitte
> vor dem Einsatz mit einem Kind die [Grenzen](#bekannte-grenzen) lesen.

---

## Eigene Vokabeln mitbringen

Der Trainer hat keinen eingebauten Kurs und keine Wörterbuchdaten — die Listen
gehören dir:

1. Die Wörter in Excel eintragen (zwei Spalten, eine je Sprache) oder aus dem
   Schulbuch übernehmen. Aus Fotos einer Buchseite kann ein KI-Assistent eine
   solche Liste machen; eine fertige Vorlage dafür steht in der Anleitung
   (Abschnitt 4). Dieser Schritt passiert außerhalb der App.
2. Die Tabelle als **CSV UTF-8** speichern und im Reiter Verwaltung auf
   **Import aus CSV** klicken.
3. Die **Vorschau** prüfen, bestätigen — die Wörter sind bereit zum Üben.

Zellen mit mehreren Bedeutungen (`dein/deine; euer/eure`, `I'm (= I am)`,
Hinweise in Klammern) werden in je einen Eintrag pro Bedeutung zerlegt; ein
Häkchen in der Vorschau schaltet das ab.

---

## Was die App kann

**Üben (Reiter Test)**

- Tests mit 1–999 Wörtern (Standard 20) — genau so viele, wie eingestellt
  sind, oder alle, wenn es weniger gibt. Richtung A → B oder B → A, optionale
  Filter (*nur neueste Vokabeln*, *nur Vokabeln mit Fehlern*)
- Die dringendsten Wörter zuerst: noch nie getestet, dann die neuesten, dann
  Fehlerquote, Fehlerzahl und letzter Test; gefragt wird in zufälliger
  Reihenfolge
- Einstellbare Antwortprüfung: Groß-/Kleinschreibung, Akzente, optional ein
  führender Artikel (Deutsch, Englisch, Spanisch oder Französisch)
- Mehrere richtige Antworten je Wort: Eine gültige Alternative löst eine
  Rückfrage aus (*„Richtig, aber nicht die gesuchte Lösung — es gibt noch
  eine zweite.“*)
- Eine Auswertung nach jedem Test und eine motivierende Übersicht (Tests,
  Serien, gemeisterte Wörter, Wochenvergleich)

**Bereich für die Eltern (Reiter Verwaltung, PIN-geschützt)**

- CSV-Import eigener Listen mit Vorschau, Direkteingabe, Live-Suche,
  Bearbeiten und Löschen
- Export der Wortliste und eines lesbaren Reports (CSV für Excel)
- Einstellungen: Sprache (Deutsch/Englisch), Farbdesign, Namen der beiden
  Sprachen, Antwortprüfung, PIN, optionales Debug-Protokoll

**Daten und Datenschutz**

- Die Vokabeln liegen in einfachen CSV-Dateien, der Lernfortschritt
  verschlüsselt neben dem Programm. Jede Installation ist portabel: alles
  liegt in einem Ordner (nur Absturzberichte gehen nach `%LOCALAPPDATA%`)
- Die PIN ist nur ein Zugangscode für die Verwaltung — eine vergessene PIN
  kostet nie Lerndaten
- `logs/app.log` enthält nur technische Ereignisse, nie Vokabeln im Klartext

---

## Installation

Windows, ohne Python:

1. Die Release-ZIP (`Vocabulary_trainer.zip`) herunterladen.
2. In einen Ordner nach Wahl entpacken.
3. `Vocabulary_trainer.exe` starten.

Für eine zweite Kopie (eine je Kind) oder ein Update `update.exe` aus dem
entpackten Ordner starten und den Zielordner wählen. Es werden nur die
Programmdateien und die Dokumentation ersetzt — Vokabeln, Lernstand,
Einstellungen und PIN bleiben unberührt.

---

## Dokumentation

- **In der App:** README und Anleitung (Deutsch und Englisch) liegen dem
  Programm bei — **Info** → **Dokumentation**.
- **Anleitung:** [Deutsch](docs/Bedienungsanleitung.md) · [English](docs/User_Guide.md)
- **Für Entwickler** (aus dem Quellcode starten, Tests, Build, Dateiformate):
  [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) (englisch)

## Fragen und Probleme

Bitte ein Issue öffnen: <https://github.com/Wewoc/Vocabulary-Trainer/issues>.
Dazu die Version (Knopf **Info**) angeben und, wenn die App ein Fehlerfenster
gezeigt hat, die dort genannte Berichtsdatei.

---

## Bekannte Grenzen

- **Die PIN ist ein einfacher Zugangscode, kein Schloss.** Sie hält ein Kind
  aus der Verwaltung fern; gegen jemanden, der `config.json` ändert oder das
  Programm kennt, schützt sie nicht. Die Lerndaten sind verschlüsselt, damit
  man sie nicht mit einem Texteditor lesen oder ändern kann — gegen eine
  technisch versierte Person schützt das nichts.
- **Eine Liste in der Verwaltung.** Import, Export, Suche und Direkteingabe
  arbeiten auf der ersten vorhandenen Vokabelliste.
- **Eine Fremdsprache je Instanz beim Ignorieren von Artikeln.** Die
  Artikellisten sind kurz (`the`, `der/die/das`, `el/la/los/las`,
  `le/la/les`) — kein `a/an`, `un/una`, `l'` oder `ein/eine`.
- **Der Import lässt Hinweise in Klammern weg** (`Herr (Anrede)` wird zu
  `Herr`).
- **Fehler, bevor das Fenster erscheint,** fängt der Absturz-Handler nicht ab.
- **Nur Windows** für das gebaute Programm.

---

## Lizenz

GPL-3.0-or-later — siehe [LICENSE](LICENSE).

Copyright (C) 2026 Wewoc ([github.com/wewoc](https://github.com/wewoc))
