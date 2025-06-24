from abc import ABC, abstractmethod

import numpy as np
import torch
import torch.nn as nn


class IModelPredictor(ABC):
    @abstractmethod
    def predict(self, X_input):
        pass


class LSTMModelPredictor(IModelPredictor):
    def __init__(self, model: nn.Module) -> None:
        self.model = model

    def predict(self, X_input: np.ndarray) -> np.ndarray:
        X_input_tensor = torch.tensor(X_input, dtype=torch.float32)
        self.model.eval()
        with torch.no_grad():
            y_pred = self.model(X_input_tensor).squeeze().numpy()
        return y_pred
