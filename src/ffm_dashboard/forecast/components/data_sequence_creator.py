from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np


class ISequenceCreator(ABC):
    @abstractmethod
    def create(self, data):
        pass


class SequenceCreator(ISequenceCreator):
    def __init__(self, data: np.ndarray, seq_length: int = 24) -> None:
        self.data = data
        self.seq_length = seq_length

    def create(self) -> Tuple[np.array, np.array]:
        X, y = [], []
        for i in range(len(self.data) - self.seq_length):
            X.append(self.data[i : i + self.seq_length])
            y.append(self.data[i + self.seq_length][0])
        return np.array(X), np.array(y)
