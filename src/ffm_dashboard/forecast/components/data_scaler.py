from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class IDataScaler(ABC):
    @abstractmethod
    def fit_transform(self, df: pd.DataFrame):
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame):
        pass

    @abstractmethod
    def inverse_transform(self, data):
        pass


class MinMaxDataScaler(IDataScaler):
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.scaler = MinMaxScaler()

    def fit_transform(self) -> np.ndarray:
        return self.scaler.fit_transform(self.df)

    def transform(self, data):
        return self.scaler.transform(data)

    def inverse_transform(self, data) -> np.ndarray:
        shaped_data = np.repeat(data.reshape(-1, 1), 5, axis=1)
        return self.scaler.inverse_transform(shaped_data)[:, 0:1]
