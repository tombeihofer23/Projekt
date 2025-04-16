from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go


@dataclass
class PlotData:
    x: list[str]
    y: list[float]
    sensor_name: str
    unit: str
    title: str = ""

    def __post_init__(self):
        self.x: pd.DatetimeIndex = pd.to_datetime(self.x)
        self.title = f"{self.sensor_name} ({self.unit})"


class Plot2D:
    def __init__(self, data: PlotData) -> None:
        self.data = data
        self.fig = go.Figure()

        self.create_2D_sensor_plot()

    def create_2D_sensor_plot(self) -> go.Figure:
        self.update_layout()
        self.update_traces()
        self.fig.write_image("test.png")

    def update_layout(self) -> go.Figure:
        self.fig.update_layout(
            title=self.data.title,
            xaxis_title="Timestamp",
            yaxis_title=f"Value ({self.data.unit})",
            margin=dict(l=40, r=20, t=40, b=30),
            height=300,
        )

    def update_traces(self) -> go.Figure:
        self.fig.add_trace(
            go.Scatter(
                x=self.data.x,
                y=self.data.y,
                mode="lines+markers",
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

    fig = Plot2D(plot_data)
