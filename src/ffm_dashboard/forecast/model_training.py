import pandas as pd
from sqlalchemy import text

from src.ffm_dashboard.db import DbCon
from src.ffm_dashboard.forecast import (
    LSTMModel,
    LSTMModelEvaluator,
    LSTMModelTrainer,
    TemperaturTrainDataHandler,
    TrainTestSplitter,
)

db_con = DbCon()

with db_con.get_session()() as session:
    query_str: str = "select * from temperature_hourly_avg"
    query = text(query_str)
    df: pd.DataFrame = pd.read_sql(query, session.bind, parse_dates=["timestamp"])

train_data_handler = TemperaturTrainDataHandler(df)
X, y = train_data_handler.get()
train_test_splitter = TrainTestSplitter(X, y)
X_train, y_train, X_test, y_test = train_test_splitter.split()

lstm_model = LSTMModel(input_size=X_train.shape[2])
lstm_model_trainer = LSTMModelTrainer(lstm_model)
lstm_model_trainer.train(X_train, y_train)

lstm_model_evaluator = LSTMModelEvaluator(lstm_model)
loss = lstm_model_evaluator.evaluate(X_test, y_test)
print(loss)
