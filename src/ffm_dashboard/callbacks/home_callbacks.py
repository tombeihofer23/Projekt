import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc

from src.ffm_dashboard.components import SenseBoxApi
from src.ffm_dashboard.utils import get_icon, get_infobox


def register_home_callbacks(app: Dash, sense_box_api: SenseBoxApi) -> None:
    @app.callback(Output("sensebox-info-group", "children"), Input("url", "pathname"))
    def load_sensebox_infos(path: str):
        if path != "/":
            return dash.no_update

        sensebox_info: dict = sense_box_api.get_box_information()
        lon, lat = sensebox_info["currentLocation"]["coordinates"][:2]
        fig = go.Figure(
            go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode="markers+text",  # auch Text anzeigen
                marker=go.scattermapbox.Marker(
                    size=12,  # Punktgröße
                    color="red",  # Farbe
                ),
                text=sensebox_info["name"],
                textposition="top left",
            )
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=14,
            mapbox_center={"lat": lat, "lon": lon},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )
        return dcc.Graph(figure=fig)

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
                                dmc.Title(
                                    f"{row['title']}-Sensor ({row['sensor_id']})",
                                    order=4,
                                ),
                                dmc.ActionIcon(
                                    get_icon(icon, 35),
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
                    dmc.Group(
                        [
                            get_infobox("gemessene Einheit", row["unit"]),
                            get_infobox("Sensor-Type", row["sensor_type"]),
                        ],
                        grow=True,
                    ),
                ],
                shadow="sm",
                padding="lg",
                radius="md",
                withBorder=True,
            )
            grid_column = dmc.GridCol(span=4, children=card)
            grid_columns.append(grid_column)
        return grid_columns
