# Bedienungsanleitung — Vocabulary-Trainer

**Deutsch** · [English](User_Guide.md)

Der Vocabulary-Trainer hilft beim Lernen von Vokabeln. Die Eltern (oder die
Lehrkraft) pflegen die Wortliste, das Kind übt im Test. Alles läuft auf dem
eigenen Computer, ohne Internet und ohne Konto.

> **Zu den Bildern:** Sie zeigen die **englische** Oberfläche, mit der die App
> startet. Im Text stehen die Bezeichnungen der **deutschen** Oberfläche (nach
> dem Umstellen, siehe [Abschnitt 2](#2-sprache-und-aussehen-einstellen)); die
> englischen Namen stehen jeweils im Bild.

---

## Inhalt

1. [Installation und erster Start](#1-installation-und-erster-start)
2. [Sprache und Aussehen einstellen](#2-sprache-und-aussehen-einstellen)
3. [Vokabeln eintragen](#3-vokabeln-eintragen)
4. [Vokabeln aus einer Excel-Datei importieren](#4-vokabeln-aus-einer-excel-datei-importieren)
5. [Vokabeln suchen, bearbeiten und löschen](#5-vokabeln-suchen-bearbeiten-und-löschen)
6. [Vokabeln und Report exportieren](#6-vokabeln-und-report-exportieren)
7. [Einen Test machen](#7-einen-test-machen)
8. [Antworten richtig bewerten](#8-antworten-richtig-bewerten)
9. [Die Statistik im Test-Bereich](#9-die-statistik-im-test-bereich)
10. [PIN, Datenschutz und Sicherheit](#10-pin-datenschutz-und-sicherheit)
11. [Ein zweites Kind, Update und Sicherung](#11-ein-zweites-kind-update-und-sicherung)
12. [Hilfe bei Problemen](#12-hilfe-bei-problemen)

---

## 1. Installation und erster Start

1. Die Datei `Vocabulary_trainer.zip` in einen Ordner entpacken, z. B.
   `Dokumente\Vokabeltrainer`.
2. Im entpackten Ordner auf `Vocabulary_trainer.exe` doppelklicken.
3. Beim ersten Start legt die App die Datei `config.json` und den Ordner
   `logs\` an. Der Ordner `daten\` (Vokabeln) entsteht mit dem ersten
   gespeicherten Wort, `metadaten\` (Lernstand) mit dem ersten
   abgeschlossenen Test. Diese Dateien und Ordner nicht umbenennen oder
   verschieben, solange die App genutzt wird.

Die App ist portabel: Alle Daten liegen im Programmordner selbst. Der ganze
Ordner kann kopiert werden (z. B. auf einen USB-Stick oder als Sicherung).

Die App hat zwei Bereiche (Reiter oben): **Test** für das Kind und
**Verwaltung** für die Eltern. Die **Verwaltung** ist durch eine **PIN**
geschützt. Solange keine eigene PIN gesetzt ist, lautet sie **`1234`** —
bitte gleich ändern (siehe [Abschnitt 10](#10-pin-datenschutz-und-sicherheit)).

Oben rechts in der Leiste gibt es außerdem den Knopf **Info**: Er zeigt die
**Version**, das Copyright, den Lizenzhinweis und den Link zum Quellcode — und
vier Knöpfe unter **Dokumentation**, die **README** und diese **Anleitung** (je
Deutsch und Englisch) im Fenster öffnen. Er braucht keine PIN.

So sieht der Reiter **Test** aus (Bezeichnungen hier englisch, die App startet
auf Englisch):

![Reiter Test](bilder/test-panel.png)

---

## 2. Sprache und Aussehen einstellen

Im Reiter **Verwaltung** ganz unten bei den Einstellungen:

- **Sprache (DE/EN):** `de` oder `en`. Die Änderung wirkt nach einem
  Neustart der App.
- **Design:** ozean, sonne, dschungel, beere, pink oder nacht. Die Änderung
  wirkt sofort.
- **Name Sprache A / Name Sprache B:** Die beiden Lernsprachen werden in der
  Oberfläche mit eigenen Namen angezeigt, z. B. *Deutsch* und *Englisch*.
  Auch hier wirkt die Änderung nach einem Neustart.
- **Artikel-Sprache A / B:** siehe [Abschnitt 8](#8-antworten-richtig-bewerten).

---

## 3. Vokabeln eintragen

Der Reiter **Verwaltung** (nach Eingabe der PIN) fasst alles für die Eltern
zusammen: oben die Eingabe, darunter die Wortliste mit Suche, dann Import und
Export, ganz unten die Einstellungen.

![Reiter Verwaltung](bilder/management.png)

Die Eingabe oben:

1. Das Wort in das erste Feld eintragen (z. B. *Haus*) — das Feld zeigt den
   Namen der ersten Sprache.
2. Die Übersetzung in das zweite Feld eintragen (z. B. *house*).
3. Auf **Hinzufügen** klicken.

Die neue Vokabel erscheint sofort in der Tabelle darunter. Ein Wort, das
schon vorhanden ist, wird nicht doppelt angelegt.

### Mehrere richtige Antworten

Wird dasselbe Wort mit zwei verschiedenen Übersetzungen eingetragen, gelten
beide als richtig. Beispiel:

| Deutsch | Englisch |
|---|---|
| groß | big |
| groß | large |

Beim Test wird dann auch *large* akzeptiert, wenn nach *big* gefragt wird.
Gibt das Kind die andere Lösung ein, kommt die Rückfrage:
*„Richtig, aber nicht die gesuchte Lösung — es gibt noch eine zweite. Wie
lautet sie?“* So lernt das Kind beide Bedeutungen.

> **Achtung:** Ein Wort mit zwei **verschiedenen Bedeutungen** (z. B.
> *Schloss* = *castle* und *Schloss* = *lock*) wird genauso verknüpft. Das
> ist bewusst so gewählt. Bei solchen Fällen die Rückfrage im Test
> beachten.

---

## 4. Vokabeln aus einer Excel-Datei importieren

Statt einzeln einzutragen, können viele Vokabeln auf einmal aus einer
Excel-Tabelle übernommen werden.

### So sieht die Datei aus

Die erste Zeile enthält die Spaltenköpfe, z. B. so:

| Deutsch | Englisch | Datum |
|---|---|---|
| Haus | house | 2026-09-01 |
| Hund | dog | 2026-09-01 |
| groß | big | 2026-09-02 |

- Die Spaltenköpfe dürfen die Namen der Sprachen sein (wie oben, so wie in
  den Einstellungen eingetragen) oder die technischen Namen `Sprache_A` /
  `Sprache_B`. Welche Spalte vorn steht, ist egal.
- Die Spalte **Datum** ist optional und wird bei selbst gemachten Dateien
  **nicht gelesen**: Es gilt immer das Datum des Imports. Das Datum
  bestimmt, welche Wörter als „neu“ gelten.

### So wird gespeichert

In Excel: **Datei → Speichern unter → Dateityp „CSV UTF-8 (durch Trennzeichen
getrennt)“** (in der englischen Excel-Version: *CSV UTF-8 (Comma delimited)*).
Wichtig ist die Option **mit UTF-8**, damit Umlaute richtig ankommen. Ob die
Datei Semikolon oder Komma als Trennzeichen hat, erkennt die App selbst.

### So wird importiert

Im Reiter **Verwaltung** auf **Import aus CSV** klicken und die Datei wählen.
Danach öffnet sich die **Import-Vorschau**. Sie zeigt, was **noch nichts
gespeichert** ist:

- oben: wie viele Einträge neu sind, wie viele schon vorhanden und wie viele
  ungültig (mit den Zeilennummern, die in Excel unter der Kopfzeile gezählt
  werden: Zeile 1 ist die erste Vokabelzeile)
- darunter die Liste der neuen Einträge, mit der Zeilennummer aus der Datei

![Import-Vorschau](bilder/import-preview.png)

**Importieren** speichert genau das, was gezeigt wird. **Abbrechen**
speichert nichts. Einzelne Zeilen lassen sich nicht abwählen. Gibt es
nichts Neues, erscheint kein Fenster, sondern nur die Ergebniszeile.

- Bereits vorhandene Vokabeln werden **nie überschrieben**.
- Doppelte Zeilen werden übersprungen.
- Es werden nur neue Wörter hinzugefügt. Eine geänderte Datei lässt sich
  also gefahrlos erneut importieren.

### Mehrere Bedeutungen in einer Zelle

Bücher und Listen aus dem Internet schreiben oft mehrere Bedeutungen in eine
Zelle (`dein/deine; euer/eure`) oder hängen Hinweise an (`Herr (Anrede)`).
Die App löst das beim Import auf, **eine Bedeutung pro Eintrag**:

| In der Datei | Daraus wird |
|---|---|
| `pink; rosa` oder `dein/deine` | je ein eigener Eintrag pro Bedeutung |
| `I'm (= I am)` | zwei Einträge: `I'm` und `I am` |
| `Herr (Anrede)`, `welcome (to)` | `Herr`, `welcome` — der Hinweis fällt weg |
| `Sei(d) still.` | `Sei still.` und `Seid still.` |
| `life, lives` | bleibt ein Eintrag — das **Komma trennt nie** |

Die Vorschau hat dafür ein Häkchen **Klammern und Trennzeichen (; /)
auflösen**, standardmäßig **an**. Wer es abschaltet, importiert die Zellen
genau so, wie sie in der Datei stehen — sinnvoll, wenn ein Eintrag wirklich
einen Schrägstrich enthält (`und/oder`). Ein Satz oben in der Vorschau sagt,
wie viele Zeilen aufgelöst wurden („Aus 39 Zeilen wurden 97 Paare gebildet.“).

Ein Hinweis in Klammern geht dabei **verloren** (er steht dann nicht mehr im
Test).

**Bitte prüfen:** Hat eine Zeile mehrere Bedeutungen auf **beiden** Seiten
(z. B. `it's (= it is)` und `er/sie/es ist`), werden alle Kombinationen
gebildet — darunter können Paare sein, die nicht zusammengehören. Die Vorschau
nennt solche Zeilen („Bitte prüfen … Zeilen 54“). Abbrechen, die Zeile in der
Datei in einzelne Zeilen aufteilen und neu importieren.

Die eigene Export-Datei der App (siehe Abschnitt 6) wird beim Wiedereinlesen
**nie** zerlegt.

### Vokabeln aus Fotos vom Schulbuch mit einer KI vorbereiten

Ein KI-Assistent (z. B. Gemini oder ChatGPT) kann aus Fotos der
Vokabelseiten eines Schulbuchs eine fertige Datei machen. Wer der KI genau
sagt, wie die Datei aussehen soll, spart sich das Aufräumen: eine Bedeutung
pro Zeile, keine Klammern. So geht es:

1. Den Text unten kopieren und der KI zusammen mit den Fotos geben. In der
   zweiten Zeile die beiden Sprachen anpassen.
2. Die Antwort der KI (nur der Text im Codeblock) in eine Textdatei kopieren
   und mit der Endung `.csv` speichern (Zeichenkodierung UTF-8).
3. Die Datei einmal in Excel öffnen und Zeilen mit `???` prüfen — dort war
   etwas auf dem Foto nicht lesbar.
4. Wie oben importieren.

Die App kommt auch mit Dateien zurecht, die **nicht** so vorbereitet wurden
(siehe oben), aber eine Liste mit einer Bedeutung pro Zeile braucht keine
Nachprüfung.

```text
Du bekommst Fotos von Vokabelseiten eines Schulbuchs. Erstelle daraus eine CSV-Datei
für den Vokabeltrainer. Sprache A = Deutsch, Sprache B = Englisch.  (anpassen)

Format:
- Kopfzeile genau: Sprache_A;Sprache_B
- Trennzeichen Semikolon, Zeichenkodierung UTF-8, eine Vokabelbedeutung pro Zeile.
- Gib nur den CSV-Text in einem Codeblock aus, ohne Erklärung davor oder danach.

Regeln:
1. Hat ein Wort mehrere Übersetzungen, schreibe für JEDE eine eigene Zeile und
   wiederhole das Wort: "pink;pink" und "pink;rosa" (nicht "pink;pink; rosa").
2. Keine Schrägstriche und keine Mehrfachangaben in einer Zelle. "mein/meine" werden zwei
   Zeilen; "er/sie/es ist" werden drei Zeilen: "er ist", "sie ist", "es ist".
3. Keine Klammern. Steht in der Klammer eine Langform ("I'm (= I am)"), schreibe beide
   Formen als eigene Zeilen. Reine Hinweise wie (Anrede) oder (auch Pl.) lässt du weg.
   Hängt die Klammer am Wort ("Sei(d) still"), schreibe beide Varianten als Zeilen.
4. Behalte bei Nomen den Artikel wie im Buch ("der Waschbär"), außer das Buch nennt ihn nicht.
5. Behalte Satzzeichen bei Sätzen und Redewendungen ("Thank you.", "Auf Wiedersehen.").
6. Gehören zwei Formen paarweise zusammen (Einzahl/Mehrzahl: "life, lives" /
   "das Leben, die Leben"), mache daraus zwei Zeilen: "life;das Leben" und "lives;die Leben".
7. Lass Überschriften, Seitenzahlen, Beispielsätze und Lernhinweise weg.
8. Ist etwas unleserlich, schreibe an die Stelle ??? statt zu raten.
9. Enthält eine Zelle ein Semikolon oder Anführungszeichen, setze die Zelle in Anführungszeichen.
```

---

## 5. Vokabeln suchen, bearbeiten und löschen

Im Reiter **Verwaltung** steht über der Tabelle ein **Suchfeld**. Beim
Tippen bleiben nur die Zeilen sichtbar, in denen der Text in einer der beiden
Sprachen vorkommt — Groß-/Kleinschreibung und Akzente spielen dabei keine
Rolle. Daneben steht „x von y“, ohne Suche die Zahl der Einträge.

Die Tabelle selbst lässt sich nicht direkt beschreiben. Eine Zeile anklicken
(sie wird farbig hervorgehoben), danach werden die Schaltflächen
**Bearbeiten** und **Löschen** aktiv.

- **Bearbeiten:** öffnet ein kleines Fenster mit beiden Texten der Zeile.
  Nach der Korrektur auf **Speichern** klicken. Die Korrektur gilt für das
  Wort in **allen** Zeilen, in denen es vorkommt (auch bei verknüpften
  Wörtern), und der Lernstand des Wortes bleibt erhalten.
- **Löschen:** Nur die gewählte Zeile wird entfernt (andere Zeilen mit
  demselben Wort bleiben). Vorher kommt eine Rückfrage, die bestätigt werden
  muss.

---

## 6. Vokabeln und Report exportieren

Im Reiter **Verwaltung** steht neben **Import aus CSV** der Knopf **Export**,
darunter zwei Häkchen:

- **Wortliste** — alle Vokabeln der Liste im technischen Format. Zum
  Sichern, zum Weitergeben oder zum späteren Wiedereinlesen (auch in eine
  andere Instanz).
- **Report** — ein lesbarer Bericht mit dem Lernstand, zum Öffnen in Excel.

Beide Häkchen sind standardmäßig gesetzt. Nach einem Klick auf **Export**
einen **Ordner** wählen. Jeder angehakte Punkt wird eine eigene Datei, mit
Datum und Uhrzeit im Namen (es wird nichts überschrieben):

- `wortliste_<Liste>_<Datum>_<Uhrzeit>.csv`
- `report_<Datum>_<Uhrzeit>.csv`

Danach öffnet die App den Ordner.

Der **Report** enthält oben die Gesamtzahlen (abgeschlossene und abgebrochene
Tests, Zeitraum, beantwortete Fragen, verschiedene Wörter, Fehler,
Trefferquote, Testzeit) und darunter eine Tabelle pro Vokabel (Tests, Fehler,
Trefferquote, Datum des letzten Fehlers) mit den **fehlerreichsten Wörtern
zuerst**. Zeit und Zeitraum zählen nur abgeschlossene Tests. Ein Wort, das
nach einem Test gelöscht wurde, steht als „(entfernt)“ in der Tabelle, damit
die Summen stimmen. Trennzeichen und Dezimalzeichen folgen der Sprache der
Oberfläche (deutsch: Semikolon und Komma, englisch: Komma und Punkt), damit
Excel die Spalten richtig trennt. Erscheint der Report bei dir in einer
einzigen Spalte, die Sprache der App passend zu deinem Excel einstellen
(Einstellungen, dann Neustart) oder in Excel *Daten → Text in Spalten*
benutzen.

> **Hinweis:** Der Report enthält die Wörter **im Klartext** und liegt
> dort, wo er gespeichert wurde. Er ist für die Eltern gedacht.

---

## 7. Einen Test machen

Im Reiter **Test** (für das Kind, ohne PIN) wird zuerst eingestellt, was
geübt werden soll:

| Einstellung | Bedeutung |
|---|---|
| **Liste** (Auswahlfeld) | Welche Vokabelliste verwendet wird |
| **Richtung** | Von der ersten zur zweiten Sprache oder umgekehrt (mit den Namen der Sprachen beschriftet) |
| **Anzahl Fragen** | Wie viele Wörter abgefragt werden: beliebig von 1 bis 999 (Standard: 20) |
| **Nur neueste Vokabeln** | Nur die zuletzt eingetragenen Wörter; die Zahl daneben sagt, wie viele „neueste“ gemeint sind (Standard: 25) |
| **Nur Vokabeln mit Fehlern** | Nur Wörter, bei denen es früher Fehler gab |

Danach auf **Test starten** klicken.

### Ablauf

1. Das Wort wird angezeigt. Die Übersetzung eintippen.
2. Auf **Prüfen** klicken. Die App zeigt „Richtig!“ oder „Falsch. Richtig
   wäre: …“.
3. Mit **Weiter** geht es zur nächsten Vokabel.
4. Am Ende erscheint die **Auswertung**: wie viele Wörter richtig waren und
   welche falsch.

Die Auswertung mit **Beenden – Erfolge übernehmen** schließen (das
Fenster-X schließt sie ebenso). **Erst damit wird die Sitzung gespeichert.**

![Auswertung](bilder/evaluation.png)

> **Wichtig:** Wird der Test mit **Abbrechen** oder über das Fenster-X
> beendet, wird **nichts** gespeichert (es zählt nur als „abgebrochen“).

### Wie die Wörter ausgewählt werden

Es werden **genau so viele Wörter** gefragt, wie bei **Anzahl Fragen**
eingestellt ist (gibt es weniger Vokabeln, alle). Die App nimmt dafür die
Wörter, die am dringendsten dran sind, in dieser Reihenfolge:

1. Wörter, die noch nie getestet wurden
2. die zuletzt eingetragenen
3. Wörter mit hoher Fehlerquote
4. Wörter mit vielen Fehlern
5. Wörter, die schon lange nicht mehr getestet wurden

Gefragt wird in zufälliger Reihenfolge. Wer nur **wenige** Fragen einstellt
und schon alle Wörter geübt hat, bekommt vor allem die Wörter mit hoher
Fehlerquote — das ist Absicht.

---

## 8. Antworten richtig bewerten

Im Reiter **Verwaltung**, bei den Einstellungen, lässt sich festlegen, wie
streng die Antworten geprüft werden. Eine Änderung gilt sofort bei der
nächsten Antwort:

- **Case-sensitiv:** Standardmäßig aus. *Haus* und *haus* gelten dann als
  gleich.
- **Akzente streng:** Standardmäßig an. *año* und *ano* gelten als
  verschieden.
- **Artikel ignorieren:** Standardmäßig aus. Wenn an, wird ein **führender**
  Artikel beim Vergleich ignoriert: *Haus* gilt als richtig für *das Haus*.

Damit „Artikel ignorieren“ die richtigen Artikel kennt, gibt es zwei
Auswahlfelder, **Artikel-Sprache A** und **Artikel-Sprache B**. Eingestellt
werden **Deutsch, Englisch, Spanisch, Französisch** oder **keine**
(Standard: A = Deutsch, B = Englisch). Es zählt die Sprache, die das Kind
gerade **tippt**: bei Richtung A → B die von B, bei B → A die von A. Das
gilt ab dem nächsten Test. Die Listen sind bewusst kurz:

| Sprache | Artikel |
|---|---|
| Deutsch | der, die, das |
| Englisch | the |
| Spanisch | el, la, los, las |
| Französisch | le, la, les |

Nicht erkannt werden z. B. *a/an*, *un/una*, *l'* und *ein/eine*.

Leerzeichen am Anfang und Ende sowie doppelte Leerzeichen werden immer
ignoriert.

Die Einstellungen gelten für alle Tests und sollten nicht ständig geändert
werden, damit die Auswertung vergleichbar bleibt.

---

## 9. Die Statistik im Test-Bereich

Oben im Reiter **Test** zeigt eine Übersicht den Lernstand. Sie
aktualisiert sich nach jedem abgeschlossenen Test von selbst:

- **Absolvierte Tests** — Anzahl der abgeschlossenen Sitzungen
- **Richtig beantwortet** — richtige Antworten von allen gegebenen Antworten
- **Letzter Test** — Datum der letzten abgeschlossenen Sitzung
- **Tage-Serie** (mit Rekord) — an wie vielen aufeinanderfolgenden Tagen
  geübt wurde
- **Fehlerfreie Serie** (mit Rekord) — wie viele Antworten hintereinander
  richtig waren
- **Gemeisterte Wörter** — Wörter, die 10-mal hintereinander richtig
  beantwortet wurden
- **Diese Woche (letzte Woche)** — Anzahl der Tests im Vergleich

Die Übersicht ist im Reiter **Test** ohne PIN sichtbar. Sie ist für das Kind
gedacht und soll motivieren. Nicht sichtbar für das Kind sind die einzelnen
Wörter mit ihren Fehlern und der Report — beides liegt hinter der PIN in der
**Verwaltung** beziehungsweise im Export.

---

## 10. PIN, Datenschutz und Sicherheit

### Die PIN

- Der Reiter **Verwaltung** ist durch eine **PIN** geschützt: Beim ersten
  Öffnen fragt die App danach. Ist sie einmal richtig eingegeben, bleibt der
  Bereich **bis zum Beenden der App** offen. Bei einer falschen PIN geht der
  Reiter nicht auf.
- Solange keine eigene PIN gesetzt ist, lautet sie **`1234`**.
- **PIN ändern:** in der **Verwaltung** bei den Einstellungen auf **PIN
  ändern** — alte PIN, neue PIN (mindestens 4 Zeichen), neue PIN wiederholen.
- Die PIN ist nur ein **Zugangscode** und gehört zur Instanz (sie steht, als
  nicht lesbarer Hash, in `config.json`). Jedes Kind hat damit seine eigene
  PIN. Sie ist **nicht** der Schlüssel für die Lerndaten: eine **vergessene
  PIN kostet nie Daten.**

![PIN-Abfrage](bilder/pin-prompt.png) ![PIN ändern](bilder/pin-change.png)

**PIN vergessen — zurücksetzen auf `1234`:**

1. Die App schließen.
2. Die Datei `config.json` im Programmordner mit dem Editor öffnen
   (Rechtsklick → *Öffnen mit* → *Editor*).
3. Die Zeile mit `"pin_hash"` suchen. Sie sieht so aus:
   `"pin_hash": "…lange Zeichenfolge…",`
4. Die Zeichenfolge samt Anführungszeichen durch `null` ersetzen, sodass dort
   steht: `"pin_hash": null,` (das Komma am Ende bleibt, falls es da war).
5. Speichern, App starten. Die PIN ist wieder `1234` — gleich eine neue setzen.

### Was geschützt ist — und was nicht

- **Keine Verbindung ins Internet.** Die App sendet keine Daten. Einzige
  Ausnahme: Ein Link zu den Projektseiten auf GitHub (im **Info**-Fenster oder
  in der dort geöffneten Dokumentation) öffnet, **nur wenn man ihn anklickt**,
  den Browser — die App selbst sendet dabei nichts. Andere Adressen öffnet sie
  nicht.
- **Vokabeln** liegen als normale CSV-Datei im Ordner `daten\vokabeln\` und
  können mit Excel geöffnet werden.
- **Lernfortschritt** liegt verschlüsselt in `metadaten\tracking.enc`. Die
  Datei lässt sich nicht mit einem Texteditor lesen oder verändern. Die
  Verschlüsselung hängt **nicht** an der PIN.
- Der Schutz ist bewusst einfach: Er hält ein neugieriges Kind von der
  Verwaltung und von der Lernstatistik fern. Gegen jemanden, der die App
  selbst aufbricht oder volle Administratorrechte auf dem PC hat, schützt er
  nicht.

### Protokoll und Fehlermeldungen

- Im Ordner `logs\` liegt `app.log`, ein technisches Protokoll (Start,
  Import, Export, falsche PIN-Eingaben ohne die PIN). Es enthält **keine
  Vokabeln im Klartext** und bleibt auf höchstens wenige MB begrenzt.
- In der **Verwaltung** bei den Einstellungen gibt es das Häkchen
  **Debug-Protokoll (bis zum Beenden)**. Es schreibt mehr Einzelheiten, wenn
  ein Fehler gezielt nachgestellt werden soll, und gilt nur bis die App
  geschlossen wird.
- Tritt ein unerwarteter Fehler auf, erscheint ein Fenster **Unerwarteter
  Fehler**. Die App läuft weiter. Der Fehlerbericht wird unter
  `%LOCALAPPDATA%\Vokabeltrainer\crash` gespeichert (der Pfad steht im
  Fenster) — **nicht** im Programmordner. Die Wörter sind darin
  unkenntlich gemacht. Diese Datei und `logs\app.log` kann man beim
  Melden eines Problems mitgeben, im Issues-Bereich des Projekts:
  <https://github.com/Wewoc/Vocabulary-Trainer/issues> (dazu die Version
  nennen, siehe Knopf **Info**).

---

## 11. Ein zweites Kind, Update und Sicherung

Jedes Kind bekommt einen **eigenen Ordner** mit eigener Vokabelliste, eigenem
Lernfortschritt und eigener PIN. Dafür:

1. `update.exe` aus dem entpackten Ordner starten.
2. Einen neuen, leeren Zielordner wählen.
3. Die App aus dem neuen Ordner starten.

`update.exe` hat nur eine englische Oberfläche: Es fragt nach dem Zielordner
(*target folder*) und meldet am Ende „Done.“. Zeigt es „Is the target app still
running?“, ist die App noch geöffnet — schließen und erneut versuchen.

> **Wichtig:** Den Ordner eines Kindes **nicht** als Vorlage für das nächste
> kopieren. Er enthält Kennung, Lernstand und PIN des ersten Kindes. Ein
> Ordner-Kopie ist als **Sicherung** gedacht (siehe unten), nicht als zweite
> Instanz.

**Update einer bestehenden Installation:** Dieselbe Prozedur mit dem
Ordner der bestehenden Installation. Dabei werden **nur** die Programmdateien
und die Dokumentation ersetzt. Vokabeln, Lernfortschritt, Einstellungen, PIN
und Protokoll bleiben erhalten.

> **Wichtig:** Vorher die App schließen. Läuft sie noch, bricht das Update
> mit einer Meldung ab.

**Sicherung:** Die App schließen und den **ganzen Ordner** kopieren (z. B. auf
einen USB-Stick). Mindestens gesichert werden sollten `daten\` und
`metadaten\tracking.enc` — die Wörter und der Lernstand. Zum Zurückspielen den
Ordner wieder an die alte Stelle kopieren.

**Vokabeln zwischen zwei Geräten** überträgt man über **Export**
(Häkchen *Wortliste*) auf dem einen und **Import aus CSV** auf dem anderen
Gerät. Der Lernstand wandert so nicht mit, nur die Wörter.

---

## 12. Hilfe bei Problemen

| Problem | Was tun |
|---|---|
| Die App startet nicht | Prüfen, ob alle Dateien aus dem ZIP entpackt sind, insbesondere der Ordner `_internal`. |
| Die Verwaltung öffnet sich nicht | Die PIN stimmt nicht. Vergessen? Siehe Abschnitt 10, „PIN vergessen“. |
| Der Import meldet „Datei konnte nicht gelesen werden“ | Die Datei in Excel als **CSV UTF-8** speichern und erneut versuchen. |
| Umlaute sind falsch dargestellt | Dieselbe Speicheroption wählen: **CSV UTF-8**. |
| Ein importiertes Wort fehlt | Die Spaltenköpfe prüfen. Stimmen sie mit den Sprachnamen oder `Sprache_A`/`Sprache_B` überein? Zeilen ohne Text in einer der beiden Spalten werden als ungültig übersprungen. |
| Der Import sagt „0 hinzugefügt“ | Alle Wörter sind schon vorhanden, oder die Zeilen sind ungültig. Die Zahlen in der Meldung zeigen, was davon zutrifft. |
| Zeilen sind in der Vorschau anders als in der Datei | Die App hat Klammern und Trennzeichen aufgelöst (Abschnitt 4). Mit dem Häkchen in der Vorschau lässt sich das abschalten. |
| Im Test fehlt ein Wort, das ich eingetragen habe | Mit **Nur neueste Vokabeln** oder **Nur Vokabeln mit Fehlern** werden nicht alle Wörter gefragt. Auch die **Anzahl Fragen** begrenzt den Test. |
| Ein Fenster „Unerwarteter Fehler“ erscheint | Die App läuft weiter. Die Datei aus dem Fenster (Ordner `crash`) und `logs\app.log` aufbewahren und beim Melden im Issues-Bereich (<https://github.com/Wewoc/Vocabulary-Trainer/issues>) mitgeben. |
| Die Texte sind in der falschen Sprache | In den Einstellungen die Sprache (`de`/`en`) ändern und die App neu starten. |
| Das Update meldet, die App laufe noch | Die App schließen und das Update erneut starten. |
| Welche Version habe ich? | Oben rechts auf **Info** klicken. Die Version beim Melden eines Problems mitschicken. |
