import dash
import dash_mantine_components as dmc
from dash import dcc

dash.register_page(__name__, path="/sensors")

layout = dmc.Box(
    children=[
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
                                    data=[],
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
                            color="red",
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
                        ),
                    ],
                ),
            ],
        ),
    ],
)
