"""Callbacks für die Home-Page."""

import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc

from src.ffm_dashboard.components import SenseBoxApi
from src.ffm_dashboard.utils import get_icon, get_infobox


def register_home_callbacks(app: Dash, sense_box_api: SenseBoxApi) -> None:
    """
    Registriert alle notwendigen Callback-Funktionen für die Home-Page.

    :param app: Die Instanz der Dash-Anwendung, zu der die Callbacks hinzugefügt werden sollen.
    :type app: Dash
    :param sense_box_api: Eine Instanz der SenseBoxApi zum Abrufen der Sensordaten
    :type sense_box_api: SenseBoxApi
    """

    @app.callback(Output("sensebox-info-group", "children"), Input("url", "pathname"))
    def load_sensebox_infos(path: str):
        """
        Lädt und zeigt Informationen zur aktuellen SenseBox auf der Startseite an,
        einschließlich Kartenansicht und Bild. Diese Funktion wird nur aufgerufen,
        wenn die URL der Seite auf ``"/"`` steht.

        :param path: Der aktuelle Pfad der URL.
        :type path: str
        :return: Eine Liste aus einem Kartenplot (Mapbox) und einem Bild der SenseBox-Installation.
        """

        if path != "/":
            return dash.no_update

        sensebox_info: dict = sense_box_api.get_box_information()
        lon, lat = sensebox_info["currentLocation"]["coordinates"][:2]
        fig = go.Figure(
            go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode="markers+text",
                marker=go.scattermapbox.Marker(
                    size=12,
                    color="red",
                ),
                text=sensebox_info["name"],
                textposition="top left",
            )
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=12,
            mapbox_center={"lat": lat, "lon": lon},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )

        img = dmc.Image(
            src=f"https://opensensemap.org/userimages/{sensebox_info['image']}",
            h=475,
            alt="Sensebox Installation",
        )

        return [dcc.Graph(figure=fig), img]

    @app.callback(Output("sensor-info-grid", "children"), Input("url", "pathname"))
    def load_sensor_info_cards(path: str):
        """
        Lädt Sensorinformationen zur aktuellen SenseBox und zeigt diese in einem Grid als Karten an.
        Diese Funktion wird nur aufgerufen, wenn die URL der Seite auf ``"/"`` steht.

        :param path: Der aktuelle Pfad der URL.
        :type path: str
        :return: Liste von Grid-Spalten, die jeweils eine Karte mit Sensorinformationen enthalten.
        """

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
                                    color="#a81b00",
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
