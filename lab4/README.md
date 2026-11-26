# **Labor 4** - Namensauflösung im Chord-P2P-System

Das Thema im 4. Labor ist die Auflösung linearer Namen. Wir betrachten dazu die
Systemklasse *verteilter Hash-Tabellen* (Distributed Hash Table, DHT) und
konkret eine vereinfachte Implementierung des **Chord-Systems**. Die Aufgabe
behandelt dabei den Unterschied zwischen iterativer und rekursiver
Namensauflösung.

Allgemeine **Ziele** dieses Labors:

- praktische Vorstellung eines Chord-P2P-Systems bekommen
- Prozesse mit dem Python-Modul `multiprocessing` starten und koordinieren
- Funktionsweise von Namenssystem und Namensauflösung in Chord verstehen
- Konzepte rekursiver und iterativer Namensauflösung erarbeiten

## 1. Vorbereitung

### 1.1. Software installieren

Für diese Aufgabe werden keine neuen Installationen benötigt. Sie arbeiten in der
Umgebung aus den vorherigen Aufgaben (optimalerweise Visual Studio Code mit dem
Dev Container, in dem Redis bereits installiert ist). Wir brauchen aber wieder
eine laufende Redis-Instanz. Der Redis-Server wird wie folgt gestartet:

```bash
redis-server
```

Außerhalb des Dev Containers orientieren Sie sich zur Einrichtung an der
[Beschreibung im VS2Lab README](../README.md#222-redis-erst-ab-aufgabe-2).

### 1.2. Projekt aktualisieren

Aktualisieren Sie die Kopie des VS2Lab-Repositorys auf Ihrem Arbeitsrechner (alle Beispiele für Linux/Mac):

```bash
cd ~/git/vs2lab # angenommen hier liegt das vs2lab Repo
git add . # ggf. eigene Änderungen vormerken
git commit -m 'update' # ggf. eigene Änderungen per Commit festschreiben
git checkout main # Branch auswählen (falls nicht schon aktiv)
git pull # aktualisieren
```

Bei Problemen siehe Troubleshooting im [VS2Lab README](../README.md#25-tipps-und-troubleshooting).

### 1.3. Python-Umgebung installieren

Wechseln Sie in das Verzeichnis des Repositorys. In Visual Studio Code tun Sie dies bitte im Dev Container (d.h. Sie führen für den Ordner `vs2lab` vorher „Reopen in Container“ aus). Im Container liegt das Repository unter `/workspaces/vs2lab`; verwenden Sie dort diesen Pfad statt `~/git/vs2lab`. Die Umgebung hat sich gegenüber den vorherigen Aufgaben nicht geändert. Führen Sie `pipenv install` aus, falls Sie dies noch nicht getan haben oder die Pipfile durch das Update geändert wurde:

```bash
cd ~/git/vs2lab # angenommen hier liegt das vs2lab Repo
pipenv install
```

### 1.4. Beispielcode für diese Aufgabe

Wechseln Sie auf Ihrem Arbeitsrechner (bzw. im Dev Container) in das Unterverzeichnis dieser Aufgabe:

```bash
cd ~/git/vs2lab # angenommen hier liegt das vs2lab Repo
cd lab4/chord
```

## 2. Beispiel: Implementierung von Chord-Ringknoten

Als Startpunkt des Labors dient eine Implementierung von Chord-Knoten im
Verzeichnis `vs2lab/lab4/chord`. Hier sind zwei Skripte interessant:

- `chordnode.py` ist die eigentliche Implementierung der Knoten.
- `doit.py` organisiert mehrere Knoten als P2P-Anwendung.

### Chord-Knoten `chordnode.py`

Die Klasse `ChordNode` verwendet das `lab_channel`-Framework, [das wir schon aus
Aufgabe 2
kennen](https://github.com/zirpins/vs2lab/tree/main/lab2#221-kommunikation-per-lab_channel).
Hier wird *Redis* (eigentlich ein (NoSQL-)Key-Value-Store) als
Message-Oriented-Middleware verwendet.

#### Knoten-Management

Alle Knoten melden sich an der Gruppe `node` an, die vom zentralen
Channel abgefragt werden kann. Dies ist eine Vereinfachung gegenüber echten
Peer-to-Peer-Systemen, in denen man keine zentrale Registry aller Knoten hat.
Die Verwaltung von kommenden und gehenden Knoten ist jedoch ein Aspekt, der in
diesem Labor nicht im Mittelpunkt steht. Daher wird der zentrale Channel beim
Knoten-Management zu Hilfe genommen.

#### Namenssystem

(Lineare) Namen werden vom zentralen Channel bei der Anmeldung zufällig aus
einem konfigurierbaren Wertebereich vergeben. Die Namen unterscheiden sich
daher bei jedem Start des Systems. Jeder Knoten unterstützt die Auflösung von
Schlüsseln `key` zum Namen des zuständigen Knotens `succ(key)` mit der Operation
`LOOKUP`. Hierbei wird der bestmögliche nächste Knoten auf dem Weg zum Ziel aus
einer internen *Finger-Tabelle* abgeleitet.

Bei einer Namensauflösung müssen mehrere Knoten in einer Sequenz von
`LOOKUP`-Aufrufen bis zum letztendlichen Ziel traversiert werden. Dies kann
entweder iterativ durch einen Client-Prozess 'von außen' oder rekursiv durch
eine Erweiterung der Knotenlogik realisiert werden. Momentan ist die Steuerung
der Namensauflösung noch nicht implementiert, denn dies wird Inhalt der
Programmieraufgabe sein.

#### Notation

Die Notation folgt der üblichen Darstellung von Chord (Finger-Tabellen mit
`succ`), mit einer Besonderheit des Labors:

- Der Namensraum umfasst die Namen `0` bis `2^m - 1`; `m` ist die Anzahl der
  Bits (`n_bits`), `MAXPROC` ist `2^m`.
- Die Finger-Tabelle `finger_table` eines Knotens `p` hat die Einträge
  `finger_table[i] = succ(p + 2^(i-1))` für `i = 1, ..., m` (modulo `2^m`). Die
  Indizes sind 1-basiert.
- **Zusätzlich** steht in `finger_table[0]` der Name des *Vorgängers* von `p`
  im Ring. Dieser Eintrag ist eine Konvention des Labors und gehört nicht zur
  üblichen Finger-Tabelle. Der Knoten braucht ihn, um festzustellen, ob er
  selbst für einen Schlüssel zuständig ist.
- Die Methode `local_successor_node(key)` liest nur die lokale Finger-Tabelle
  und liefert den Namen eines Knotens zurück: den eigenen Namen, falls der Knoten
  selbst zuständig ist, sonst den Namen des Nachfolgers (falls dieser zuständig
  ist) oder den des bestmöglichen nächsten Knotens auf dem Weg zum Ziel. Die
  Auswahl folgt der Regel: Liegt der Schlüssel `k` im Bereich
  `FT_p[j] <= k < FT_p[j+1]`, ist `FT_p[j]` der nächste Knoten.

#### Datenverwaltung

In einer DHT speichern die beteiligten Knoten Datenwerte für die verwendeten
Schlüssel. Die dazu notwendige Datenverwaltung ist in diesem Beispiel nicht
realisiert.

### Chord-Anwendung `doit.py`

Das zweite Skript nutzt die Implementierung von Chord-Knoten zum Aufbau eines
Ring-Systems. Hierzu können die Größe des Adressraums in Bit (`m`) und die
Anzahl der Knoten (`n`) als Konstanten oder als Kommandozeilenparameter
angegeben werden. Da auch der Client einen Namen aus dem Wertebereich bekommt,
muss `n + 1 <= 2^m` gelten.

Das Skript verwendet das [Python-`multiprocessing`-Modul](https://docs.python.org/3/library/multiprocessing.html),
um die Knoten (und einen Client) als separate Prozesse zu starten. Prozesse
können per `fork` oder `spawn` erzeugt werden. `doit.py` verwendet `spawn`, das
auch unter Windows verfügbar ist: Der neue Prozess startet dabei neu und führt
die übergebene Funktion mit den übergebenen Argumenten aus. Zwei Barrieren
(`Barrier`) sorgen dafür, dass zuerst alle Prozesse am Channel angemeldet und
dann alle Knoten in den Ring aufgenommen sind, bevor die Knoten und der Client
ihre Arbeit beginnen.

Der verwendete `DummyChordClient` ist nur eine Schablone ohne Logik für den
Aufruf einer Namensauflösung auf einem der Knoten. Dieser Client soll in der
Programmieraufgabe fertiggestellt werden.

### Starten des Systems

Das System baut im aktuellen Zustand lediglich einen Ring auf und beendet diesen
dann sofort wieder. Die Durchführung von Namensauflösungen wird erst in der
Programmieraufgabe realisiert. Am Ende werden die Finger-Tabellen aller Knoten
ausgegeben (jeweils mit dem Vorgänger an Position 0). Einen Test führt man wie
folgt aus (Beispiel für Linux/Mac OS; nicht vergessen, vorher Redis zu starten):

```bash
cd ~/git/vs2lab/lab4/chord # angenommen hier liegt das vs2lab Repo
pipenv run python doit.py
```

Mit zwei Parametern lassen sich `m` und `n` vorgeben, z.B. für einen
kleinen Ring mit 4 Bit und 5 Knoten:

```bash
pipenv run python doit.py 4 5
```

## 3. Aufgabe

In der Programmieraufgabe soll die Namensauflösung mit dem Chord-System
fertiggestellt werden.

### 3.1. Übersicht

Die Namensauflösung mit Chord erfolgt schrittweise über eine Reihe von Aufrufen
der `LOOKUP`-Funktion einzelner Knoten, die jeweils den besten bekannten Knoten
auf dem Weg zum Ziel liefern, bis dieses Ziel am Ende erreicht ist.

Die Steuerung der einzelnen Schritte kann entweder durch einen zentralen
Client-Prozess von außen (iterativ) koordiniert werden oder sich durch die
verteilten Knotenprozesse selbst rekursiv fortsetzen.
**Die Aufgabe besteht darin, die rekursive Variante zu implementieren.**

### 3.2. Aufgabe und Anforderungen kurz und knapp

- Erweitern Sie die `LOOKUP`-Operation von `ChordNode` so, dass diese für eine
  Anfrage nach Schlüssel `key` direkt `succ(key)` zurückgibt. Falls der
  angefragte Knoten nicht selbst der gesuchte Knoten ist, soll er zu dessen
  Bestimmung eine rekursive `LOOKUP`-Anfrage an den besten bekannten Knoten
  machen usw.
- Erweitern Sie ebenfalls die Klasse `DummyChordClient`. Hier soll eine
  `LOOKUP`-Anfrage nach einem zufälligen gültigen Schlüssel (`0` bis `2^m - 1`)
  an einen ebenfalls zufälligen existierenden Knoten erfolgen und der gefundene
  Name ausgegeben werden.

### 3.3. Tipps

- Bei einer einfachen Rekursion werden alle beteiligten Knoten (bis auf den
  letzten) zu Clients, die jeweils auf eine Antwort warten und diese dann
  weiterreichen, bis am Ende der ursprüngliche Client die Antwort bekommt.
  Alternativ kann die Implementierung endrekursiv erfolgen, dann sendet der
  letzte Knoten die Antwort direkt zum ursprünglichen Client zurück.
- Testen Sie zunächst mit einem kleinen Ring (z.B. `python doit.py 4 5`). Die am
  Ende ausgegebenen Finger-Tabellen erlauben es, den erwarteten Weg einer
  Anfrage von Hand nachzuvollziehen. Die Knoten
  protokollieren empfangene `LOOKUP`-Anfragen auf der Konsole.
- `doit.py` leert beim Start die Redis-Datenbank. Nach fehlerhaften Requests
  können alte Nachrichten oder Zustände im Channel zu Problemen führen; starten
  Sie dann `doit.py` neu, im Zweifel auch den Redis-Server.

### 3.4. Abgabe

Laden Sie den kompletten Code vor dem Abgabetermin als Zip-Archiv in ILIAS hoch. Die Abgabe erfolgt dann durch persönliche Abnahme im Labortermin (Zeitslot über den ILIAS-Buchungspool); ohne Upload erfolgt keine Abnahme. Bei der Abnahme muss jedes Gruppenmitglied den Code erklären können. Den Abgabetermin finden Sie im Ablaufplan.
