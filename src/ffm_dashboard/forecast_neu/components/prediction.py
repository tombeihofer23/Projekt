"""Vorhersage-Klasse für LGBM-Modell."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


class MultiLGBMPredictor:
    """
    Vorhersageklasse für ein LightGBM Multi-Step Forecasting Modell.

    Lädt ein vortrainiertes LightGBM-Modell und erzeugt Vorhersagen auf Basis
    eines vorbereiteten Feature-Sets.

    :param pred_input: DataFrame mit den vorbereiteten Eingabefeatures (eine Zeile).
    :type pred_input: pd.DataFrame
    :param model_path: Pfad zur Pickle-Datei des vortrainierten LightGBM-Modells.
    :type model_path: Path
    """

    def __init__(
        self,
        pred_input: pd.DataFrame,
        model_path: Path = Path(__file__).parent.parent
        / "trained_models/multi_lgbm_model.pkl",
    ) -> None:
        self.input = pred_input
        self.model = joblib.load(model_path)

    def make_prediction(self) -> np.ndarray:
        """
        Führt eine Vorhersage mit dem geladenen LightGBM-Modell durch.

        :return: Array mit Vorhersagen für alle zukünftigen Zeitschritte (z.B. t+1 bis t+30).
        :rtype: np.ndarray
        """

        y_pred = self.model.predict(self.input)[0]
        return y_pred
