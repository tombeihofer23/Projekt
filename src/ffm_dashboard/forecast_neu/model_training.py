import os
from pathlib import Path

import joblib
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.multioutput import MultiOutputRegressor
from sqlalchemy import text

from ffm_dashboard.forecast_neu.components.data_preparation import (
    MultiStepPreprocessor,  # DataPreprocessor,
)
from ffm_dashboard.forecast_neu.components.train_test_split import (
    MultiTrainTestSplitter,  # TrainTestSplitter,
)
from src.ffm_dashboard.db import DbCon

db_con = DbCon()
with db_con.get_session()() as session:
    query_str: str = "select * from temperature_view"
    query = text(query_str)
    df: pd.DataFrame = pd.read_sql(query, session.bind, parse_dates=["timestamp"])

# prepr = DataPreprocessor(df)
# # pre_df = prepr.apply()

# # y = pre_df.pop("target")

# train_test_splitter = TrainTestSplitter(pre_df, y)
# # X_train, y_train, X_test, y_test = train_test_splitter.split()

# print("startet Training")
# model = LGBMRegressor()
# # model.fit(X_train, y_train)

# # 9. Evaluation auf Testset
# y_pred = model.predict(X_test)
# mae = mean_absolute_error(y_test, y_pred)
# print(f"Mean Absolute Error (MAE): {mae:.3f}")

# model_path: Path = Path(__file__).parent / "trained_models"
# os.makedirs(model_path, exist_ok=True)
# joblib.dump(model, model_path / "lgbm_model.pkl")

multi_preprocessor = MultiStepPreprocessor(df, horizon=30)
prep_df = multi_preprocessor.prepare_for_training()

multi_tts = MultiTrainTestSplitter(prep_df)
X_train, y_train, X_test, y_test = multi_tts.split()

print(X_train.columns.tolist())

multi_model = MultiOutputRegressor(LGBMRegressor())
multi_model.fit(X_train, y_train)

y_pred = multi_model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE über alle 30 Schritte: {mae:.3f}")

model_path: Path = Path(__file__).parent / "trained_models"
os.makedirs(model_path, exist_ok=True)
joblib.dump(multi_model, model_path / "multi_lgbm_model.pkl")
