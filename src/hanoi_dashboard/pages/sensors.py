from datetime import date

import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/sensors")

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=[
                dmc.Grid(
                    id="sensor-select-grid",
                    justify="center",
                    children=[
                        dmc.GridCol(
                            dmc.MultiSelect(
                                id="sensors-multi-select",
                                label="Sensoren",
                                data=[
                                    {
                                        "value": "3453489234",
                                        "label": "Temperatur-Sensor",
                                    },
                                    {
                                        "value": "e454542343",
                                        "label": "Luftdruck-Sensor",
                                    },
                                    {
                                        "value": "3445652342",
                                        "label": "Luftfeuchtigkeits-Sensor",
                                    },
                                    {"value": "2342342356", "label": "Wind-Sensor"},
                                ],
                            ),
                            span={"base": 4, "xs": 12, "sm": 6, "md": 4},
                        ),
                        dmc.GridCol(
                            dmc.DatePickerInput(
                                id="date-input-range-picker",
                                label="Zeitspanne",
                                type="range",
                                minDate=date(2020, 1, 1),
                            ),
                            span={"base": 4, "xs": 12, "sm": 6, "md": 4},
                        ),
                    ],
                ),
                dmc.Text(
                    id="output-status",
                    children="Dashboard loaded. Click button to fetch initial data.",
                ),
                # Container where graphs will be dynamically added
                dmc.Box(
                    id="graph-container",
                    children=[
                        dmc.Grid(
                            id="graph-grid",
                            gutter="md",
                            children=[
                                dmc.Text("Graphs will appear here after fetching data.")
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
