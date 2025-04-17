from typing import Final

import dash
import pandas as pd
from dash import Dash, Input, Output, dcc, html
from loguru import logger

from src.hanoi_dashboard.components import SenseBoxApi
from src.hanoi_dashboard.data import DbCon, SensorDataDbService
from src.hanoi_dashboard.plots import Plot2D, PlotData, PlotType2D

DB_CON: Final = DbCon()


def register_home_callbacks(app: Dash) -> None:
    @app.callback(
        Output("output-status", "children"),
        Input("fetch-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_db_and_status(n_clicks: int) -> str:
        if n_clicks > 0:
            logger.info(
                "Fetch button clicked ({} times). Fetching data from API...", n_clicks
            )
            sense_box_api = SenseBoxApi("6252afcfd7e732001bb6b9f7")
            data: pd.DataFrame = sense_box_api.fetch_new_sensor_data()

            if data is not None and not data.empty:
                db_service = SensorDataDbService(DB_CON)
                db_service.write_new_sensor_data(data, "6252afcfd7e732001bb6b9f7")
                return f"API Fetch successful. Processed {len(data)} readings."
            else:
                return "Failed to fetch data"

        return dash.no_update

    @app.callback(
        Output("graph-data-store", "data"),
        Input("fetch-button", "n_clicks"),
        prevent_initial_call=False,
    )
    def update_graph_store(n_clicks: int) -> dict:
        ctx = dash.callback_context
        trigger_id = (
            ctx.triggered[0]["prop_id"].split(".")[0]
            if ctx.triggered
            else "initial load"
        )
        logger.info("Graph store update triggered by: {}", trigger_id)

        db_service = SensorDataDbService(DB_CON)
        data: pd.DataFrame = db_service.query_data(48, "6252afcfd7e732001bb6b9f7")

        if data is None or data.empty:
            logger.warning("No data retrieved from DB for graphs")
            return {}

        graph_data: dict = {}

        data["sensor_key"] = data.apply(
            lambda row: f"{row['box_id']}_{row['sensor_id']}"
            if pd.notna(row["sensor_id"])
            else f"{row['box_id']}_{row['sensor_type']}",
            axis=1,
        )

        grouped_data = data.groupby("sensor_key")

        for name, group in grouped_data:
            group = group.sort_values("timestamp")
            if len(group) > 500:
                group = group.tail(500)

            graph_data[name] = {
                "timestamps": group["timestamp"]
                .dt.strftime("%Y-%m-%dT%H:%M:%S")
                .tolist(),
                "values": group["measurement"].tolist(),
                "unit": group["unit"].iloc[0] if not group["unit"].empty else "",
            }

        logger.info("Prepared data for {} graphs.", len(graph_data))
        return graph_data

    @app.callback(
        Output("graph-container", "children"), Input("graph-data-store", "data")
    )
    def update_graphs(stored_data):
        if not stored_data:
            return html.P(
                "No data available to display graphs. Click 'Fetch' or wait for data."
            )

        logger.info("Updating graphs from stored data ({} series).", len(stored_data))
        graph_components = []
        sorted_keys = sorted(
            stored_data.keys()
        )  # Sort alphabetically for consistent order

        for sensor_key in sorted_keys:
            sensor_data = stored_data[sensor_key]
            timestamps = sensor_data.get("timestamps", [])
            values = sensor_data.get("values", [])
            unit = sensor_data.get("unit", "")

            if not timestamps or not values:
                logger.warning("Skipping graph for {} due to missing data.", sensor_key)
                continue

            plot_data: PlotData = PlotData(timestamps, values, sensor_key, unit)
            plot = Plot2D(plot_data, PlotType2D.SENSOR)
            fig = plot.fig

            graph_components.append(
                html.Div(
                    className="graph-item",
                    children=[  # Optional wrapper div
                        dcc.Graph(
                            figure=fig,
                            id={"type": "dynamic-graph", "index": sensor_key},
                        )  # Using pattern-matching ID is optional here
                    ],
                )
            )

        logger.info("Generated {} graph components.", len(graph_components))
        return graph_components
