from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class IDataPreprocessor(ABC):
    @abstractmethod
    def apply(self):
        pass


class TemperaturDataPreprocessor(IDataPreprocessor):
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy().set_index("timestamp")

    def apply(self) -> pd.DataFrame:
        processed_df: pd.DataFrame = self.df.assign(
            sin_hour=np.sin(2 * np.pi * (self.df.index.hour / 24)),
            cos_hour=np.cos(2 * np.pi * (self.df.index.hour / 24)),
            sin_month=np.sin(2 * np.pi * (self.df.index.month / 12)),
            cos_month=np.cos(2 * np.pi * (self.df.index.month / 12)),
        )
        return processed_df
