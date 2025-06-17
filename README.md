# 🌍 Frankfurt Dashboard – Umweltmonitoring mit Dash

Ein interaktives Dashboard zur Visualisierung und Analyse von Umweltdaten aus Frankfurt am Main. Die Daten stammen aus sechs senseBox-Sensoren im Stadtgebiet. Zusätzlich können Vorhersagen auf Basis der erfassten Messwerte berechnet und angezeigt werden.

## 📸 Features

- Live-Datenvisualisierung von 6 senseBox-Sensoren (Luftqualität, Temperatur, Feinstaub etc.)
- Auswahl von Sensor und Zeitraum
- Zeitreihendarstellungen mit Plotly
- Vorhersage-Modul für bestimmte Umweltkennzahlen
- Entwickelt mit [`uv`](https://docs.astral.sh/uv/) + [Plotly Dash](https://dash.plotly.com/) + [TimescaleDB](https://www.timescale.com/)

## 📡 Datenquelle

Die Daten werden in Echtzeit über die [senseBox API](https://docs.opensensemap.org/) bezogen, in eine TimescaleDB-Datenbank geladen und im Dashboard dargestellt.

## 🛠️ Installation

### 1. `uv` installieren

[`uv`](https://docs.astral.sh/uv/) ist ein schneller Python-Paketmanager und -Runner (ähnlich wie `pip` + `venv`), geschrieben in Rust.

#### macOS / Linux (Bash)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Mit Homebrew natürlich auch möglich

#### Windows (Powershell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Installation prüfen

```bash
uv --version
```

Möglichweise muss Terminal neu gestartert werden

### 2. Projekt klonen

```bash
git clone https://github.com/tombeihofer23/Projekt.git
```

### 3. Projekt-Setup

Die benötigten Python-Packages können nun mit `uv` installiert werden. Dafür in Projektordner wechseln und folgenden Befehl ausführen:

```bash
uv sync
```

### 4. Dashboard starten

Jetzt muss der Docker-Container, in dem die Datenbank und das Programm läuft, gestartet werden. 

```bash
docker-compose up --build
```

>**Achtung**: Beim ersten Start des Dashboards werden alle historischen Daten der SenseBox geladen und in die Datenbank geschrieben. Dies kann bis zu **einer Stunde** dauern.

# Noch nicht fertig!!!