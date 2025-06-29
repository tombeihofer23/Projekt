"""Klassen für die Plot-Erstellung."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import yaml


class PlotType2D(Enum):
    """
    Enum zur Auswahl des Plot-Typs.

    - SENSOR: Reine Sensordaten
    - FORECAST: Messwerte + Vorhersage
    """

    SENSOR = 1
    FORECAST = 2


@dataclass
class PlotData:
    """
    Datenträger für 2D-Plotinformationen.

    :param x: Zeitachse
    :type x: pd.Series
    :param y: Messwerte (Sensor oder Forecast)
    :type y: pd.Series | pd.DataFrame
    :param title: Titel des Plots (wird aus YAML übernommen)
    :type title: str
    :param unit: Einheit der Messgröße (z.B. °C)
    :type unit: str
    """

    x: pd.Series
    y: pd.Series | pd.DataFrame
    title: str
    unit: str


class Plot2D:
    """
    Generiert interaktive 2D-Liniendiagramme für Sensorwerte oder Vorhersagedaten.

    Unterstützt zwei Typen:
    - Sensorplots (Echtzeitdaten)
    - Forecastplots (Prognosedaten mit Trennung real/pred)

    Die Konfigurationen werden aus YAML-Dateien gelesen, um Layout und Trace-Stil
    flexibel anpassbar zu halten.

    :param data: Plotdaten inklusive x/y-Werten, Titel und Einheit
    :type data: PlotData
    :param plot_type: Art des zu erzeugenden Plots (SENSOR oder FORECAST)
    :type plot_type: PlotType2D
    """

    def __init__(self, data: PlotData, plot_type: PlotType2D) -> None:
        self.data = data
        self.plot_type = plot_type
        self.fig = go.Figure()
        self.config_path: Path

        if self.plot_type == PlotType2D.FORECAST:
            func = self.create_2D_forecast_plot
            self.config_path = (
                Path(__file__).parent / "config/2D_forecast_plot_config.yaml"
            )
        else:
            func = self.create_2D_sensor_plot
            self.config_path = (
                Path(__file__).parent / "config/2D_sensor_plot_config.yaml"
            )

        func()

    def create_2D_sensor_plot(self) -> None:  # pylint: disable=invalid-name
        """
        Erstellt ein Standard-Sensorplot bestehend aus einem Trace
        und angepasstem Layout gemäß YAML-Konfiguration.
        """

        self.update_layout_sensor()
        self.update_traces_sensor()

    def create_2D_forecast_plot(self) -> None:  # pylint: disable=invalid-name
        """
        Erstellt ein Plot mit realen und prognostizierten Werten.
        Reale Messwerte werden im Plot versteckt angezeigt (via Legendeneintrag),
        Vorhersagen direkt dargestellt.
        """

        self.update_layout_forecast()
        self.update_traces_forecast()

    def update_layout_sensor(self) -> None:
        """
        Lädt Layout-Einstellungen für Sensorplots aus YAML und
        konfiguriert Titel, Achsentitel, Größe und Rand.
        """

        with self.config_path.open("r", encoding="utf-8") as c:
            config: dict = yaml.safe_load(c)
        self.fig.update_layout(
            title=config["title"][self.data.title].format(self.data.unit),
            xaxis_title=config["layout"]["xaxis"],
            yaxis_title=f"{self.data.title} ({self.data.unit})",
            margin=config["layout"]["margin"],
            height=config["layout"]["height"],
        )

    def update_traces_sensor(self) -> None:
        """Fügt einen Plotly-Trace für Sensordaten gemäß Konfiguration hinzu."""

        with self.config_path.open("r", encoding="utf-8") as c:
            config: dict = yaml.safe_load(c)
        self.fig.add_trace(
            go.Scattergl(
                x=self.data.x,
                y=self.data.y,
                mode=config["trace"]["mode"],
                name=self.data.title,
                line=dict(color=config["trace"]["color"]),
            )
        )

    def update_layout_forecast(self) -> None:
        """Lädt das Layout für Forecastplots und setzt Beschriftungen, Ränder und Legende."""

        with self.config_path.open("r", encoding="utf-8") as c:
            config: dict = yaml.safe_load(c)
        self.fig.update_layout(
            # title=config["title"],
            xaxis_title=config["layout"]["xaxis"],
            yaxis_title=f"{self.data.title} ({self.data.unit})",
            margin=config["layout"]["margin"],
            height=config["layout"]["height"],
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="left",
                x=0,
                font=dict(size=20),
            ),
        )

    def update_traces_forecast(self) -> None:
        """
        Trennt die Daten in reale und prognostizierte Werte basierend auf der Spalte `q`
        und erstellt jeweils einen separaten Trace mit unterschiedlichen Farben und
        Legendenbezeichnungen.
        """

        with self.config_path.open("r", encoding="utf-8") as c:
            config: dict = yaml.safe_load(c)
        y = self.data.y
        x = self.data.x
        y_real = y[y["q"] == "real"]
        x_real = x[: len(y_real)]
        y_pred = y[y["q"] == "pred"]
        x_pred = x[len(y_real) :]

        self.fig.add_trace(
            go.Scatter(
                x=x_real,
                y=y_real["measurement"],
                mode=config["trace"]["mode"],
                name=config["trace"]["real"]["legende"],
                line=dict(color=config["trace"]["real"]["color"]),
                hovertemplate=config["trace"]["hover"],
                visible="legendonly",
            )
        )
        self.fig.add_trace(
            go.Scatter(
                x=x_pred,
                y=y_pred["measurement"],
                mode=config["trace"]["mode"],
                name=config["trace"]["pred"]["legende"],
                line=dict(color=config["trace"]["pred"]["color"]),
                hovertemplate=config["trace"]["hover"],
            )
        )


if __name__ == "__main__":
    plot_data = PlotData(
        [
            "2025-03-31 23:59:49.630000+00:00",
            "2025-03-31 23:55:15.559000+00:00",
            "2025-03-31 23:49:51.364000+00:00",
        ],
        [0.29, 0.03, 0.02],
        "test_sensor",
        "mm",
    )

    fig = Plot2D(plot_data, PlotType2D.SENSOR).fig
    fig.show()
