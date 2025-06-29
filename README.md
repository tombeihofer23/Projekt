# 🌍 Frankfurt Dashboard – Umweltmonitoring mit Dash

Ein interaktives Dashboard zur Visualisierung und Analyse von Umweltdaten aus Frankfurt am Main. Die Daten stammen aus sechs senseBox-Sensoren im Stadtgebiet. Zusätzlich können Vorhersagen auf Basis der erfassten Messwerte berechnet und angezeigt werden.

## 📸 Features

- Live-Datenvisualisierung von 6 senseBox-Sensoren (Luftqualität, Temperatur, Feinstaub etc.)
- Auswahl von Sensor und Zeitraum
- Zeitreihendarstellungen mit Plotly
- Vorhersage-Modul für die Temperatur in den nächsten 1.5h
- Entwickelt mit [`uv`](https://docs.astral.sh/uv/) + [`Plotly Dash`](https://dash.plotly.com/) + [`TimescaleDB`](https://www.timescale.com/)

## 📡 Datenquelle

Die Daten werden in Echtzeit über die [senseBox API](https://docs.opensensemap.org/) bezogen, in eine TimescaleDB-Datenbank geladen und im Dashboard dargestellt.

## Start des Dashboards

Um das Dashboard zu starten muss Docker auf dem Computer installiert und einsatzbereit sein. Es gibt zwei Möglichkeiten, das Dashboard initial zu starten:
- beim ersten Start alle historischen Daten der SenseBox downloaden
- ohne historische Daten

### mit historischen Daten

>**Achtung**: Alle historischen Daten der SenseBox werden geladen und in die Datenbank geschrieben. Dies kann bis zu **einer Stunde** oder länger dauern.

In der `docker-compose.yaml` bei der App die Umgebungsvariable LOAD_DATA auf True setzen
```
app:
    ...
    environement:
        ...
        LOAD_DATA: true
```
Danach die Schritte so ausführen, wie sie auch ohne historische Daten beschrieben werden. Nachdem die Daten geladen worden sind, für alle weiteren Starts **LOAD_DATA** wieder auf **false** setzen.

### normaler Start

Beim ersten Start oder wenn etwas am Code verändert worden ist, muss das App-Image gebaut werden:
```bash
docker-compose build
```

Nun muss die Datenbank und das Dashboard nur noch gestartet werden:
```bash
docker-compose up
```

Wenn nichts am Code verändert wurde, kann so jedes weiter Mal die App gestartet werden. Um die App zu stoppen muss im Terminal, in dem die Container laufen, der Prozess mit <kbd>strg</kbd> + <kbd>C</kbd> unterbrochen werden. Danach dann noch:
```bash
docker-compose down
```

## Entwicklung

### 🛠️ Installation

#### 1. `uv` installieren

[`uv`](https://docs.astral.sh/uv/) ist ein schneller Python-Paketmanager und -Runner (ähnlich wie `pip` + `venv`), geschrieben in Rust.

##### macOS / Linux (Bash)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Mit Homebrew natürlich auch möglich

##### Windows (Powershell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

##### Installation prüfen

```bash
uv --version
```

Möglichweise muss Terminal neu gestartert werden

#### 2. Projekt klonen

```bash
git clone https://github.com/tombeihofer23/Projekt.git
```

#### 3. Projekt-Setup

Die benötigten Python-Packages können nun mit `uv` installiert werden. Dafür in Projektordner wechseln und folgenden Befehl ausführen:

```bash
uv sync
```

#### 4. Dashboard starten

Zum Entwickeln soll nur die Datenbank im Docker-Container laufen. Die App soll normal lokal gestartet werden, damit man Änderungen live sehen kann. Dafür kann der `app`-Abschnitt im docker-compose.yaml auskommentiert werden. Danach muss das Image neu gebaut und gestartet werden. Außerdem muss im config.yaml im `db/config`-Ordner der Host von *db* auf *localhost* gesetzt werden. Danach kann das Dashboard gestartet werden:
```python
uv run start.py
```