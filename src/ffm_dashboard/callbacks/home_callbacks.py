import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Dash, Input, Output
from dash_iconify import DashIconify

from src.ffm_dashboard.components import SenseBoxApi


def get_icon(icon: str) -> DashIconify:
    return DashIconify(icon=icon, height=35)


def register_home_callbacks(app: Dash, sense_box_api: SenseBoxApi) -> None:
    @app.callback(Output("sensor-info-grid", "children"), Input("url", "pathname"))
    def load_sensor_info_cards(path: str):
        if path != "/":
            return dash.no_update

        sensor_info: pd.DataFrame = sense_box_api.get_sensors_information_for_box()
        grid_columns: list = []

        for _, row in sensor_info.iterrows():
            icon: str = (
                "wi:hot"
                if row["icon"] == "osem-brightness"
                else f"wi:{row['icon'].split('-')[1]}"
            )
            card = dmc.Card(
                children=[
                    dmc.CardSection(
                        dmc.Group(
                            children=[
                                dmc.Title(f"{row['title']}-Sensor", order=4),
                                dmc.ActionIcon(
                                    get_icon(icon),
                                    color="red",
                                    variant="transparent",
                                ),
                            ],
                            justify="space-between",
                        ),
                        withBorder=True,
                        inheritPadding=True,
                        py="xs",
                    ),
                    dmc.Stack(
                        [
                            dmc.Title(f"ID: {row['sensor_id']}", order=6),
                            dmc.Title(f"gemessene Einheit: {row['unit']}", order=6),
                            dmc.Title(f"Sensor-Typ: {row['sensor_type']}", order=6),
                        ],
                        align="normal",
                        gap="xs",
                    ),
                    # dmc.Table(
                    #     data={"head": ["SensorID", "Einheit", "Sensor Typ"]},
                    #     body=[[row["sensor_id"], row["unit"], row["sensor_type"]]],
                    # ),
                ],
                shadow="sm",
                padding="lg",
                radius="md",
                withBorder=True,
            )
            grid_column = dmc.GridCol(span=4, children=card)
            grid_columns.append(grid_column)
        return grid_columns
