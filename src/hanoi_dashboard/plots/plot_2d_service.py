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
    sensor_name: str
    unit: str
    title: str = ""

    def __post_init__(self):
        # self.x: pd.DatetimeIndex = pd.to_datetime(self.x)
        self.title = f"{self.sensor_name} ({self.unit})"


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
        self.update_layout()
        self.update_traces()

    def create_2D_forecast_plot(self) -> None:
        self.update_layout()
        self.update_traces()

    def update_layout(self) -> None:
        with self.config_path.open("r") as c:
            config: dict = yaml.safe_load(c)
        self.fig.update_layout(
            title=self.data.title,
            xaxis_title=config["layout"]["xaxis"],
            yaxis_title=f"Value ({self.data.unit})",
            margin=config["layout"]["margin"],
            height=config["layout"]["height"],
        )

    def update_traces(self) -> None:
        with self.config_path.open("r") as c:
            config: dict = yaml.safe_load(c)
        self.fig.add_trace(
            go.Scatter(
                x=self.data.x,
                y=self.data.y,
                mode=config["trace"]["mode"],
                name=self.data.sensor_name,
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
