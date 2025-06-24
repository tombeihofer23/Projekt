from abc import ABC, abstractmethod

import torch
import torch.nn as nn


class IModelEvaluator(ABC):
    @abstractmethod
    def evaluate(self, X_test, y_test):
        pass


class LSTMModelEvaluator(IModelEvaluator):
    def __init__(self, model: nn.Module, criterion: nn.Module = nn.MSELoss()) -> None:
        self.model = model
        self.criterion = criterion

    def evaluate(self, X_test: torch.Tensor, y_test: torch.Tensor) -> float:
        self.model.eval()
        with torch.no_grad():
            y_pred = self.model(X_test).squeeze()
            loss = self.criterion(y_pred, y_test)
        return loss.item()
