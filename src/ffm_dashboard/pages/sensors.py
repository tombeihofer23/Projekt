from datetime import date, datetime

import dash
import dash_mantine_components as dmc
from dash import dcc

dash.register_page(__name__, path="/sensors")

layout = dmc.Box(
    children=[
        dcc.Interval(
            id="interval-component",
            interval=4 * 60 * 1000,  # 4min in Millisekunden
            n_intervals=0,
        ),
        dmc.Box(
            m=15,
            children=[
                dmc.Flex(
                    justify="space-between",  # Platz zwischen linker und rechter Seite
                    align="center",
                    style={"width": "100%"},
                    mb=30,
                    children=[
                        dmc.Box(),  # Leeres Element links, damit wir zentrieren können
                        dmc.Group(  # Deine zentrierten Selects
                            children=[
                                dmc.MultiSelect(
                                    id="sensors-multi-select",
                                    placeholder="Sensoren",
                                    data=[
                                        {
                                            "value": "5d6d5269953683001ae46ae1",
                                            "label": "Temperatur",
                                        },
                                        {
                                            "value": "5d6d5269953683001ae46add",
                                            "label": "PM10",
                                        },
                                        {
                                            "value": "5d6d5269953683001ae46ade",
                                            "label": "PM2.5",
                                        },
                                        {
                                            "value": "607fe08260979a001bd13188",
                                            "label": "Luftdruck",
                                        },
                                        {
                                            "value": "5d6d5269953683001ae46ae0",
                                            "label": "rel. Luftfeuchte",
                                        },
                                        {
                                            "value": "5e7f6fecf7afec001bf5b1a3",
                                            "label": "Beleuchtungsstärke",
                                        },
                                    ],
                                    style={
                                        "width": 450,
                                        "minWidth": 250,
                                        "maxWidth": 450,
                                    },
                                ),
                                dmc.DatePickerInput(
                                    id="date-input-range-picker",
                                    placeholder="Zeitspanne",
                                    type="range",
                                    minDate=date(2022, 8, 1),
                                    maxDate=datetime.now().date(),
                                    style={
                                        "width": 450,
                                        "minWidth": 250,
                                        "maxWidth": 450,
                                    },
                                ),
                            ],
                        ),
                        dmc.Button(
                            "Fetch Data",
                            id="fetch-data-button",
                            variant="filled",
                            color="#a81b00",
                        ),  # Rechts außen
                    ],
                ),
                dmc.Box(
                    id="output-status-notification-container",
                    # children="Dashboard loaded. Click button to fetch initial data.",
                ),
                # Container where graphs will be dynamically added
                dmc.Box(
                    id="graph-container",
                    children=[
                        dcc.Loading(
                            dmc.Grid(
                                id="graph-grid",
                                gutter="md",
                                children=[
                                    dmc.Text(
                                        "Graphs will appear here after fetching data."
                                    )
                                ],
                            ),
                            delay_hide=1000,
                            color="#a81b00",
                        ),
                    ],
                ),
            ],
        ),
    ],
)
