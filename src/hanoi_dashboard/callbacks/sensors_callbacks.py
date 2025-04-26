from datetime import date, datetime
from io import StringIO
from typing import Final

import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Dash, Input, Output, ctx, dcc, html
from loguru import logger

from src.hanoi_dashboard.components import SenseBoxApi
from src.hanoi_dashboard.db import DbCon, SensorDataDbService
from src.hanoi_dashboard.plots import Plot2D, PlotData, PlotType2D

DB_CON: Final = DbCon()


def register_sensors_callbacks(app: Dash) -> None:
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
        sense_box_api = SenseBoxApi("5d6d5269953683001ae46adc")
        data: pd.DataFrame = sense_box_api.fetch_new_sensor_data_for_one_box()

        if data is not None and not data.empty:
            db_service = SensorDataDbService(DB_CON)
            inserted_cols = db_service.write_new_sensor_data(
                data, "5d6d5269953683001ae46adc"
            )
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
        Output("graph-data-store", "data"),
        Input("fetch-data-button", "n_clicks"),
        Input("interval-component", "n_intervals"),
        prevent_initial_call=True,
    )
    def update_graph_store(n_clicks: int, n_intervals: int) -> dict:  # pylint: disable=unused-argument
        trigger_id = ctx.triggered_id
        logger.info("Graph store update triggered by: {}", trigger_id)

        db_service = SensorDataDbService(DB_CON)
        data: pd.DataFrame = db_service.query_data_from_a_date_on(
            "5d6d5269953683001ae46adc", date(2025, 4, 15)
        )

        if data is None or data.empty:
            logger.warning("No data retrieved from DB for graphs")
            return {}

        return data.to_json(date_format="iso", orient="split")

    @app.callback(
        Output("sensors-multi-select", "data"),
        Output("date-input-range-picker", "minDate"),
        Output("date-input-range-picker", "maxDate"),
        Input("graph-data-store", "data"),
    )
    def fill_select_fields(stored_data: dict):
        if not stored_data:
            return [], "2025-01-01", datetime.now().date()

        data: pd.DataFrame = pd.read_json(StringIO(stored_data), orient="split")
        data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True).map(
            lambda x: x.tz_convert("Europe/Berlin")
        )

        sensors: list = list(set(data["sensor_id"]))
        min_date, max_date = data["timestamp"].agg(["min", "max"])
        return sensors, min_date, max_date

    @app.callback(
        Output("graph-grid", "children"),
        Input("graph-data-store", "data"),
        Input("sensors-multi-select", "value"),
        Input("date-input-range-picker", "value"),
    )
    def update_graphs(stored_data: dict, sensors: list, date_range: str):
        if not stored_data:
            return html.P(
                "No data available to display graphs. Click 'Fetch' or wait for data."
            )

        data: pd.DataFrame = pd.read_json(StringIO(stored_data), orient="split")
        data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True).map(
            lambda x: x.tz_convert("Europe/Berlin")
        )

        data["sensor_key"] = data.apply(
            lambda row: f"{row['box_id']}_{row['sensor_id']}"
            if pd.notna(row["sensor_id"])
            else f"{row['box_id']}_{row['sensor_type']}",
            axis=1,
        )

        if sensors:
            data = data[data["sensor_id"].isin(sensors)]

        if date_range:
            if None not in date_range:
                data = data[
                    (data["timestamp"] >= pd.to_datetime(date_range[0], utc=True))
                    & (
                        data["timestamp"]
                        <= pd.to_datetime(date_range[1], utc=True)
                        + pd.Timedelta(days=1)
                    )
                ]
            else:
                dash.no_update  # pylint: disable=pointless-statement

        grid_columns: list = []
        grouped_data = data.groupby("sensor_key")

        for name, group in grouped_data:
            group = group.sort_values("timestamp")
            # if len(group) > 500:
            #     group = group.tail(500)
            timestamps = group["timestamp"]
            values = group["measurement"]
            unit = group["unit"].iloc[0] if not group["unit"].empty else ""
            title = group["title"].iloc[0] if not group["title"].empty else ""
            if timestamps.empty or values.empty:
                logger.warning("Skipping graph for {} due to missing data.", name)
                continue

            plot_data: PlotData = PlotData(timestamps, values, title, unit)
            plot = Plot2D(plot_data, PlotType2D.SENSOR)
            graph = dcc.Graph(
                figure=plot.fig,
                id={"type": "dynamic-graph", "index": name},
            )

            grid_column = dmc.GridCol(
                span={"base": 4, "xs": 12, "sm": 6, "md": 4}, children=graph
            )
            grid_columns.append(grid_column)

        logger.info("Generated {} graph components.", len(grid_columns))
        return grid_columns
