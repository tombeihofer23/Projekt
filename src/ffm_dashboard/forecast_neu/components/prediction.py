from pathlib import Path

import joblib
import numpy as np
import pandas as pd


class MultiLGBMPredictor:
    def __init__(
        self,
        pred_input: pd.DataFrame,
        model_path: Path = Path(__file__).parent.parent
        / "trained_models/multi_lgbm_model.pkl",
    ) -> None:
        self.input = pred_input
        self.model = joblib.load(model_path)

    def make_prediction(self) -> np.ndarray:
        y_pred = self.model.predict(self.input)[0]
        return y_pred


# if __name__ == "__main__":
# sense_box_api = SenseBoxApi("5d6d5269953683001ae46adc")
# df = sense_box_api.fetch_historical_data_for_one_sensor(
#     "5d6d5269953683001ae46ae1",
#     from_date="2025-06-26T11:00:00Z",
#     to_date="2025-06-26T17:00:00Z",
# )

# df = (
#     df.sort_values("timestamp")
#     .reset_index(drop=True)
#     .drop(columns=["box_id", "sensor_id"])
# )
# df["measurement"] = df["measurement"].astype(float)

# multi_prepro = MultiStepPreprocessor(df)
# X_pred = multi_prepro.prepare_latest_for_prediction()

# mu = MultiLGBMForecast(X_pred)
# print(mu.make_prediction())
