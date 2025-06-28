from datetime import timedelta

import pandas as pd

from src.ffm_dashboard.forecast_neu.components.data_preparation import (
    MultiStepPreprocessor,
)
from src.ffm_dashboard.forecast_neu.components.prediction import MultiLGBMPredictor
from src.ffm_dashboard.plots import PlotData


class MultiLGBMForecastPipeline:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        data_processor = MultiStepPreprocessor(self.df)
        x_input: pd.DataFrame = data_processor.prepare_latest_for_prediction()
        predictor = MultiLGBMPredictor(x_input)
        self.y_pred = predictor.make_prediction()

    def get_forecast(self) -> pd.DataFrame:
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
