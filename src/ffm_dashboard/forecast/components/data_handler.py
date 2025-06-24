from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from src.ffm_dashboard.forecast.components.data_preprocessor import (
    TemperaturDataPreprocessor,
)
from src.ffm_dashboard.forecast.components.data_scaler import MinMaxDataScaler
from src.ffm_dashboard.forecast.components.data_sequence_creator import SequenceCreator


class IDataHandler(ABC):
    @abstractmethod
    def get(self, df: pd.DataFrame):
        pass


class TemperaturDataHandler(IDataHandler):
    @abstractmethod
    def get(self):
        pass


class TemperaturTrainDataHandler(TemperaturDataHandler):
    temp_scaler: MinMaxDataScaler = None

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def get(self):
        preprocessor = TemperaturDataPreprocessor(self.df)
        preprocced_df: pd.DataFrame = preprocessor.apply()

        self.temp_scaler = MinMaxDataScaler(preprocced_df)
        scaled_data: np.ndarray = self.temp_scaler.fit_transform()

        seq_creator = SequenceCreator(scaled_data)
        out = seq_creator.create()
        X: np.array = out[0]
        y: np.array = out[1]
        return X, y


class TemperaturPredDataHandler(TemperaturDataHandler):
    def __init__(self, df: pd.DataFrame, temp_scaler: MinMaxDataScaler) -> None:
        self.df = df
        self.temp_scaler = temp_scaler

    def get(self):
        preprocessor = TemperaturDataPreprocessor(self.df)
        preprocced_df: pd.DataFrame = preprocessor.apply()

        scaled_data: np.ndarray = self.temp_scaler.transform(preprocced_df)

        seq_creator = SequenceCreator(scaled_data)
        out = seq_creator.create()
        X: np.array = out[0]
        # y: np.array = out[1]
        return X  # , y
