import dash
import dash_mantine_components as dmc
from dash import dcc

dash.register_page(__name__, path="/sensors")

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=[
                dmc.Grid(
                    id="sensor-select-grid",
                    justify="center",
                    mb=20,
                    children=[
                        dmc.GridCol(
                            dmc.MultiSelect(
                                id="sensors-multi-select",
                                label="Sensoren",
                                data=[],
                            ),
                            span={"base": 4, "xs": 12, "sm": 6, "md": 4},
                        ),
                        dmc.GridCol(
                            dmc.DatePickerInput(
                                id="date-input-range-picker",
                                label="Zeitspanne",
                                type="range",
                            ),
                            span={"base": 4, "xs": 12, "sm": 6, "md": 4},
                        ),
                    ],
                ),
                dmc.Notification(
                    id="output-status-notification",
                    action="hide",
                    message="",
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
