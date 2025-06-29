"""TrainTestSplitter Klasse für LGBM-Modell."""

import pandas as pd

# class TrainTestSplitter:
#     def __init__(
#         self, X: pd.DataFrame, y: pd.DataFrame, train_ratio: float = 0.8
#     ) -> None:
#         self.X = X
#         self.y = y
#         self.train_ratio = train_ratio

#     def split(self):
#         split_idx: int = int(len(self.X) * self.train_ratio)
#         X_train, X_test = self.X[:split_idx], self.X[split_idx:]
#         y_train, y_test = self.y[:split_idx], self.y[split_idx:]
#         return X_train, y_train, X_test, y_test


class MultiTrainTestSplitter:
    """
    Teilt ein Feature-Target-DataFrame für Multi-Step-Zeitreihenprognosen
    in Trainings- und Testdaten auf.

    Die Spalten, deren Namen mit 'target_' beginnen, werden als Zielvariablen
    betrachtet, alle anderen als Eingabefeatures.

    :param df: Ein DataFrame mit vorbereiteten Features und Zielspalten
    :type df: pd.DataFrame
    :param train_ratio: Anteil der Daten, die für das Training verwendet werden (zwischen 0 und 1).
    :type train_ratio: float
    """

    def __init__(self, df: pd.DataFrame, train_ratio: float = 0.8) -> None:
        self.df = df
        self.train_ratio = train_ratio

    def split(self):
        """
        Führt den Trainings-Test-Datensplit durch.

        Spalten, deren Namen mit ``target_`` beginnen, werden als Zielvariablen (y)
        verwendet. Der Rest wird als Eingabefeature (X) interpretiert.

        :return: Tupel bestehend aus (X_train, y_train, X_test, y_test)
        :rtype: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        """

        split_idx: int = int(len(self.df) * self.train_ratio)
        train_df = self.df.iloc[:split_idx]
        test_df = self.df.iloc[split_idx:]

        X_train = train_df.drop(  # pylint: disable=invalid-name
            columns=[col for col in train_df.columns if col.startswith("target_")]
        )
        y_train = train_df[
            [col for col in train_df.columns if col.startswith("target_")]
        ]

        X_test = test_df.drop(  # pylint: disable=invalid-name
            columns=[col for col in test_df.columns if col.startswith("target_")]
        )
        y_test = test_df[[col for col in test_df.columns if col.startswith("target_")]]
        return X_train, y_train, X_test, y_test
