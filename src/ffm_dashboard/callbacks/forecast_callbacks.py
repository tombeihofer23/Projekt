from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import dash_mantine_components as dmc
import pandas as pd
from dash import Dash, Input, Output, dcc, no_update

from src.ffm_dashboard.components import SenseBoxApi
from src.ffm_dashboard.forecast_neu import MultiLGBMForecastPipeline
from src.ffm_dashboard.plots import Plot2D, PlotData, PlotType2D


def register_forecast_callbacks(app: Dash, sense_box_api: SenseBoxApi) -> None:
    @app.callback(
        Output("forecast-title", "children"),
        Input("fetch-forecast-button", "n_clicks"),
    )
    def update_title(n_clicks: int):
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        then = now + timedelta(minutes=90)
        title_str: str = f"Temperaturentwicklung von {now.strftime('%H:%M')} bis {then.strftime('%H:%M')} Uhr"
        return title_str

    @app.callback(
        Output("forecast-graph-container", "children"),
        Input("fetch-forecast-button", "n_clicks"),
    )
    def update_graph(n_clicks: int):
        df: pd.DataFrame = sense_box_api.fetch_temp_data_for_forecast()
        if df is not None and not df.empty:
            forecast_pipe = MultiLGBMForecastPipeline(df)
            data: PlotData = forecast_pipe.get_forecast()
            plot = Plot2D(data, PlotType2D.FORECAST)
            graph_box = dmc.Box(
                children=[
                    dcc.Graph(
                        figure=plot.fig,
                        id="forecast-plot",
                    ),
                    dmc.Center(
                        dmc.Text(
                            "🟦 Interaktiv: Legende drücken für Live-Messwert",
                            size="xl",
                        )
                    ),
                ]
            )
            return graph_box
        else:
            no_update
