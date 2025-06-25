import os
from abc import ABC, abstractmethod
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class IModelTrainer(ABC):
    @abstractmethod
    def train(self, X_train, y_train):
        pass


class LSTMModelTrainer(IModelTrainer):
    def __init__(self, model: nn.Module, lr: float = 0.001, epochs: int = 10) -> None:
        self.model = model
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        self.epochs = epochs

    def train(self, X_train: torch.Tensor, y_train: torch.Tensor):
        train_loader = DataLoader(
            TensorDataset(X_train, y_train), batch_size=32, shuffle=True
        )
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0
            for xb, yb in train_loader:
                pred = self.model(xb).squeeze()
                loss = self.criterion(pred, yb)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            print(f"EPOCH {epoch + 1}/{self.epochs}, Loss: {total_loss:.4f}")

        model_path: Path = Path(__file__).parent.parent / "trained_models"
        os.makedirs(model_path, exist_ok=True)
        torch.save(self.model.state_dict(), model_path / "lstm_model.pth")
