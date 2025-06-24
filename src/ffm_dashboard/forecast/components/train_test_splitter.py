from typing import Tuple

import numpy as np
import torch


class TrainTestSplitter:
    def __init__(self, X: np.array, y: np.array, train_ratio: float = 0.8) -> None:
        self.X = X
        self.y = y
        self.train_ratio = train_ratio

    def split(
        self,  # , X: np.ndarray, y: np.ndarray
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        split_idx: int = int(len(self.X) * self.train_ratio)
        X_train, y_train = (
            torch.tensor(self.X[:split_idx], dtype=torch.float32),
            torch.tensor(self.y[:split_idx], dtype=torch.float32),
        )
        X_test, y_test = (
            torch.tensor(self.X[split_idx:], dtype=torch.float32),
            torch.tensor(self.y[split_idx:], dtype=torch.float32),
        )
        return X_train, y_train, X_test, y_test
