import pandas as pd


class TrainTestSplitter:
    def __init__(
        self, X: pd.DataFrame, y: pd.DataFrame, train_ratio: float = 0.8
    ) -> None:
        self.X = X
        self.y = y
        self.train_ratio = train_ratio

    def split(self):
        split_idx: int = int(len(self.X) * self.train_ratio)
        X_train, X_test = self.X[:split_idx], self.X[split_idx:]
        y_train, y_test = self.y[:split_idx], self.y[split_idx:]
        return X_train, y_train, X_test, y_test


class MultiTrainTestSplitter:
    def __init__(self, df: pd.DataFrame, train_ratio: float = 0.8) -> None:
        self.df = df
        self.train_ratio = train_ratio

    def split(self):
        split_idx: int = int(len(self.df) * self.train_ratio)
        train_df = self.df.iloc[:split_idx]
        test_df = self.df.iloc[split_idx:]

        X_train = train_df.drop(
            columns=[col for col in train_df.columns if col.startswith("target_")]
        )
        y_train = train_df[
            [col for col in train_df.columns if col.startswith("target_")]
        ]

        X_test = test_df.drop(
            columns=[col for col in test_df.columns if col.startswith("target_")]
        )
        y_test = test_df[[col for col in test_df.columns if col.startswith("target_")]]
        return X_train, y_train, X_test, y_test
