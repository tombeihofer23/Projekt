"""Datenvorverarbeitungs-Klasse für LGBM-Modell."""

import numpy as np
import pandas as pd

# class DataPreprocessor:
#     def __init__(self, df: pd.DataFrame) -> None:
#         df = df.copy()
#         if "timestamp" in df.columns:
#             df = df.set_index("timestamp")
#         self.df = df

#     def apply_features(self, df: pd.DataFrame) -> pd.DataFrame:
#         return df.assign(
#             sin_hour=np.sin(2 * np.pi * (df.index.hour / 24)),
#             cos_hour=np.cos(2 * np.pi * (df.index.hour / 24)),
#             sin_month=np.sin(2 * np.pi * (df.index.month / 12)),
#             cos_month=np.cos(2 * np.pi * (df.index.month / 12)),
#             lag_1=df["measurement"].shift(1),
#             lag_6=df["measurement"].shift(6),
#             lag_20=df["measurement"].shift(20),
#             rolling_mean_20=df["measurement"].rolling(window=20).mean(),
#             rolling_std_20=df["measurement"].rolling(window=20).std(),
#         )

#     def prepare_for_training(self) -> pd.DataFrame:
#         df_feat = self.apply_features(self.df)
#         df_feat["target"] = self.df["measurement"].shift(-1)
#         return df_feat.dropna()

#     def prepare_latest_for_prediction(self) -> pd.DataFrame:
#         if len(self.df) < 20:
#             raise ValueError("Mindestens 20 Datenpunkte nötig.")

#         df_feat = self.apply_features(self.df)
#         return df_feat.dropna().iloc[[-1]]  # nur die letzte vollständige Zeile


class MultiStepPreprocessor:
    """
    Preprocessing-Klasse zur Vorbereitung von Zeitreihendaten für Multi-Step-Vorhersagemodelle.

    Diese Klasse berechnet zeitliche und statistische Features sowie Zielwerte (Targets)
    für mehrere Zeitschritte in die Zukunft (multi-step forecasting).

    :param df: Zeitreihen-DataFrame mit einer 'timestamp'-Spalte und einer 'measurement'-Spalte.
    :type df: pd.DataFrame
    :param horizon: Anzahl der Zeitschritte in die Zukunft, für die Vorhersageziele erzeugt werden sollen.  # pylint: disable=line-too-long
    :type horizon: int
    """

    def __init__(self, df: pd.DataFrame, horizon: int = 30):
        self.df = df.copy().set_index("timestamp").sort_index()
        self.horizon = horizon

    def prepare_for_training(self) -> pd.DataFrame:
        """
        Erstellt ein Trainings-Feature-Set für ein Multi-Step-Zeitreihenmodell.

        Features:
        - Zeitliche Features: sin/cos von Stunde und Monat
        - Lag-Features: Messwerte bei t-1, t-6, t-20
        - Rollende Statistik: gleitender Mittelwert und Standardabweichung über 20 Schritte
        - Targets: Messwerte für die nächsten `horizon` Zeitschritte (t+1 bis t+horizon)

        :return: Vorverarbeiteter DataFrame mit Features und Zielwerten.
        :rtype: pd.DataFrame
        """

        df = self.df

        # Features
        df_feat = df.assign(
            sin_hour=np.sin(2 * np.pi * (df.index.hour / 24)),
            cos_hour=np.cos(2 * np.pi * (df.index.hour / 24)),
            sin_month=np.sin(2 * np.pi * (df.index.month / 12)),
            cos_month=np.cos(2 * np.pi * (df.index.month / 12)),
            lag_1=df["measurement"].shift(1),
            lag_6=df["measurement"].shift(6),
            lag_20=df["measurement"].shift(20),
            rolling_mean_20=df["measurement"].rolling(window=20).mean(),
            rolling_std_20=df["measurement"].rolling(window=20).std(),
        )

        # Targets: 30 Schritte in die Zukunft
        for i in range(1, self.horizon + 1):
            df_feat[f"target_t+{i}"] = df["measurement"].shift(-i)

        return df_feat.dropna()

    def prepare_latest_for_prediction(self) -> pd.DataFrame:
        """
        Bereitet den letzten bekannten Datenpunkt für die Vorhersage vor.

        Verwendet die letzten Werte zur Berechnung der notwendigen Features,
        um diesen Punkt an ein trainiertes Vorhersagemodell zu übergeben.

        Anforderungen:
        - Der DataFrame muss mindestens 20 Datenpunkte enthalten.

        Features:
        - Letzter Messwert
        - Zeitliche Features: sin/cos von Stunde und Monat
        - Lag-Features: t-1, t-6, t-20
        - Rollende Statistik (20er Fenster): Mittelwert und Standardabweichung

        :return: DataFrame mit einer Zeile, die alle notwendigen Features für Vorhersage enthält.
        :rtype: pd.DataFrame
        :raises ValueError: Wenn weniger als 20 Datenpunkte vorhanden sind.
        """

        df = self.df.copy()

        # Sicherstellen, dass genug Werte vorhanden sind
        if len(df) < 20:
            raise ValueError("Mindestens 20 Datenpunkte nötig für Feature-Berechnung.")

        # Letzter bekannter Zeitpunkt
        latest_ts = df.index[-1]

        # Zeitmerkmale berechnen (einmalig, weil nur aktuelle Zeit relevant)
        features = {
            "measurement": df["measurement"].iloc[-1],
            "sin_hour": np.sin(2 * np.pi * (latest_ts.hour / 24)),
            "cos_hour": np.cos(2 * np.pi * (latest_ts.hour / 24)),
            "sin_month": np.sin(2 * np.pi * (latest_ts.month / 12)),
            "cos_month": np.cos(2 * np.pi * (latest_ts.month / 12)),
            "lag_1": df["measurement"].iloc[-1],
            "lag_6": df["measurement"].iloc[-6],
            "lag_20": df["measurement"].iloc[-20],
            "rolling_mean_20": df["measurement"].rolling(window=20).mean().iloc[-1],
            "rolling_std_20": df["measurement"].rolling(window=20).std().iloc[-1],
        }

        return pd.DataFrame([features])
