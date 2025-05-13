from datetime import datetime, timedelta

import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Dash, Input, Output, ctx, dcc
from loguru import logger

from src.hanoi_dashboard.components import SenseBoxApi
from src.hanoi_dashboard.db import SensorDataDbService
from src.hanoi_dashboard.plots import Plot2D, PlotType2D


def register_sensors_callbacks(
    app: Dash, sense_box_api: SenseBoxApi, db_service: SensorDataDbService
) -> None:
    @app.callback(
        Output("output-status-notification-container", "children"),
        Input("interval-component", "n_intervals"),
        Input("fetch-data-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_db_and_status(n_intervals: int, n_clicks: int) -> str:
        trigger_id = ctx.triggered_id
        if trigger_id == "interval-component":
            logger.info(
                "Fetching new data automatically ({} times) from API...", n_intervals
            )
        else:
            logger.info(
                "Fetch button clicked ({} times). Fetching data from API...", n_clicks
            )

        data: pd.DataFrame = sense_box_api.fetch_new_sensor_data_for_one_box()

        if data is not None and not data.empty:
            inserted_cols = db_service.write_new_sensor_data(data)
            return dmc.Notification(
                title="Daten geladen!",
                autoClose=5000,
                action="show",
                message=f"API Fetch successful. Processed {inserted_cols} readings.",
                position="bottom-left",
            )
        else:
            return dmc.Notification(
                title="Fehler!",
                autoClose=5000,
                action="show",
                message="Failed to fetch data.",
                position="bottom-left",
            )

    @app.callback(
        Output("graph-grid", "children"),
        Input("sensors-multi-select", "value"),
        Input("date-input-range-picker", "value"),
    )
    def update_graphs(sensors: list, date_range: list):
        min_date: datetime = datetime.now().date() - timedelta(days=2)
        max_date: datetime = datetime.now().date()

        if not sensors:
            sensors = [
                "5d6d5269953683001ae46ae1",
                "5d6d5269953683001ae46add",
                "5d6d5269953683001ae46ade",
                "607fe08260979a001bd13188",
                "5d6d5269953683001ae46ae0",
                "5e7f6fecf7afec001bf5b1a3",
            ]

        if date_range:
            if None not in date_range:
                min_date: pd.Timestamp = pd.to_datetime(date_range[0])
                max_date: pd.Timestamp = pd.to_datetime(date_range[1])
            else:
                dash.no_update  # pylint: disable=pointless-statement

        grid_columns: list = []

        plot_data: dict = db_service.query_plot_data(sensors, [min_date, max_date])
        for sensor, data in plot_data.items():
            plot = Plot2D(data, PlotType2D.SENSOR)
            graph = dcc.Graph(
                figure=plot.fig,
                id={"type": "dynamic-graph", "index": sensor},
            )

            grid_column = dmc.GridCol(
                span={"base": 4, "xs": 12, "sm": 6, "md": 4}, children=graph
            )
            grid_columns.append(grid_column)

        logger.info("Generated {} graph components.", len(grid_columns))
        return grid_columns
