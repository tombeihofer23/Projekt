# %%

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import yaml


class PlotType2D(Enum):
    SENSOR = 1
    FORECAST = 2


@dataclass
class PlotData:
    x: pd.Series
    y: pd.Series
    title: str
    unit: str
    # header: str = ""

    # def __post_init__(self):
    #     # self.x: pd.DatetimeIndex = pd.to_datetime(self.x)
    #     self.header = f"{self.title} ({self.unit})"


class Plot2D:
    def __init__(self, data: PlotData, plot_type: PlotType2D) -> None:
        self.data = data
        self.plot_type = plot_type
        self.fig = go.Figure()
        self.config_path: Path

        if self.plot_type == PlotType2D.FORECAST:
            func = self.create_2D_forecast_plot
            self.config_path = (
                Path(__file__).parent / "config/2D_forecast_plot_config.yaml"
            )
        else:
            func = self.create_2D_sensor_plot
            self.config_path = (
                Path(__file__).parent / "config/2D_sensor_plot_config.yaml"
            )

        func()

    def create_2D_sensor_plot(self) -> None:
        self.update_layout_sensor()
        self.update_traces_sensor()

    def create_2D_forecast_plot(self) -> None:
        self.update_layout_forecast()
        self.update_traces_forecast()

    def update_layout_sensor(self) -> None:
        with self.config_path.open("r", encoding="utf-8") as c:
            config: dict = yaml.safe_load(c)
        self.fig.update_layout(
            title=config["title"][self.data.title].format(self.data.unit),
            xaxis_title=config["layout"]["xaxis"],
            yaxis_title=f"{self.data.title} ({self.data.unit})",
            margin=config["layout"]["margin"],
            height=config["layout"]["height"],
        )

    def update_traces_sensor(self) -> None:
        with self.config_path.open("r") as c:
            config: dict = yaml.safe_load(c)
        self.fig.add_trace(
            go.Scattergl(
                x=self.data.x,
                y=self.data.y,
                mode=config["trace"]["mode"],
                name=self.data.title,
            )
        )

    def update_layout_forecast(self) -> None:
        with self.config_path.open("r", encoding="utf-8") as c:
            config: dict = yaml.safe_load(c)
        self.fig.update_layout(
            title=config["title"],
            xaxis_title=config["layout"]["xaxis"],
            yaxis_title=f"{self.data.title} ({self.data.unit})",
            margin=config["layout"]["margin"],
            height=config["layout"]["height"],
        )

    def update_traces_forecast(self) -> None:
        with self.config_path.open("r") as c:
            config: dict = yaml.safe_load(c)
        y = self.data.y
        x = self.data.x
        y_real = y[y["q"] == "real"]
        x_real = x[: len(y_real)]
        y_pred = y[y["q"] == "pred"]
        x_pred = x[len(y_real) :]
        self.fig.add_trace(
            go.Scatter(
                x=x_real,
                y=y_real["measurement"],
                mode=config["trace"]["mode"],
                name=self.data.title,
                line=dict(color="blue"),
            )
        )
        self.fig.add_trace(
            go.Scatter(
                x=x_pred,
                y=y_pred["measurement"],
                mode=config["trace"]["mode"],
                name=self.data.title,
                line=dict(color="red"),
            )
        )


if __name__ == "__main__":
    plot_data = PlotData(
        [
            "2025-03-31 23:59:49.630000+00:00",
            "2025-03-31 23:55:15.559000+00:00",
            "2025-03-31 23:49:51.364000+00:00",
        ],
        [0.29, 0.03, 0.02],
        "test_sensor",
        "mm",
    )

    fig = Plot2D(plot_data, PlotType2D.SENSOR).fig
    fig.show()

# %%
