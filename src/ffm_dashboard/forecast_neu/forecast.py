"""Vorhersagepipeline-Klasse, um komplette Vorhersage zu bekommen."""

from datetime import timedelta

import pandas as pd

from src.ffm_dashboard.forecast_neu.components.data_preparation import (
    MultiStepPreprocessor,
)
from src.ffm_dashboard.forecast_neu.components.prediction import MultiLGBMPredictor
from src.ffm_dashboard.plots import PlotData


class MultiLGBMForecastPipeline:
    """
    Pipeline zur Erstellung einer 30-Schritte-Zeitreihenprognose mit einem
    LightGBM-Multi-Output-Modell.

    Der Ablauf umfasst:
    1. Feature-Engineering des aktuellsten Zeitpunkts via `MultiStepPreprocessor`.
    2. Vorhersage mit einem vorkonfigurierten Multi-LGBM-Modell (`MultiLGBMPredictor`).

    :param df: DataFrame mit historischen Messwerten (mind. 20 Zeilen).
               Muss eine Spalte `timestamp` und eine Spalte `measurement` enthalten.
    :type df: pd.DataFrame
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        data_processor = MultiStepPreprocessor(self.df)
        x_input: pd.DataFrame = data_processor.prepare_latest_for_prediction()
        predictor = MultiLGBMPredictor(x_input)
        self.y_pred = predictor.make_prediction()

    def get_forecast(self) -> PlotData:
        """
        Kombiniert reale Messwerte mit 30 Prognosepunkten in einem einzigen DataFrame
        zur weiteren Visualisierung oder Auswertung.

        Die Prognosepunkte starten 3 Minuten nach dem letzten Zeitstempel
        und sind in 3-Minuten-Schritten erzeugt.

        :return: Ein `PlotData`-Objekt, das sowohl reale als auch prognostizierte Werte enthält.
                 Die Spalte `q` kennzeichnet die Herkunft des Werts (real oder pred).
        :rtype: PlotData
        """

        start = self.df["timestamp"].iloc[-1]
        timestamps = [start + timedelta(minutes=3 * i) for i in range(1, 30 + 1)]

        pred_df = pd.DataFrame({"timestamp": timestamps})
        pred_df["measurement"] = self.y_pred
        pred_df["q"] = "pred"

        self.df["q"] = "real"
        forecast_df = pd.concat([self.df, pred_df], ignore_index=True)

        plot_data: PlotData = PlotData(
            x=forecast_df.timestamp,
            y=forecast_df[["measurement", "q"]],
            title="Temperatur",
            unit="°C",
        )

        return plot_data
