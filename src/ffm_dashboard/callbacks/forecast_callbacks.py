import pandas as pd
from dash import Dash, Input, Output, dcc

from src.ffm_dashboard.components import SenseBoxApi
from src.ffm_dashboard.forecast_neu import MultiLGBMForecastPipeline
from src.ffm_dashboard.plots import Plot2D, PlotData, PlotType2D


def register_forecast_callbacks(app: Dash, sense_box_api: SenseBoxApi) -> None:
    @app.callback(
        Output("forecast-graph-container", "children"),
        Input("fetch-forecast-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_graph(n_clicks: int):
        df: pd.DataFrame = sense_box_api.fetch_temp_data_for_forecast()
        if df is not None and not df.empty:
            forecast_pipe = MultiLGBMForecastPipeline(df)
            data: PlotData = forecast_pipe.get_forecast()
            plot = Plot2D(data, PlotType2D.FORECAST)
            graph = dcc.Graph(
                figure=plot.fig,
                id="forecast-plot",
            )
            return graph
        else:
            "Keine Daten da"
