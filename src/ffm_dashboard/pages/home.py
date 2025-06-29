"""Layout der Home-Page."""

import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/", redirect_from=["/home"])

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=[
                dmc.Title(
                    "Information über die SenseBox in Frankfurt Westend Süd", order=2
                ),
                dmc.Box(
                    children=[
                        dmc.Group(
                            id="sensebox-info-group", justify="space-evenly", grow=True
                        ),
                    ]
                ),
                dmc.Title("Sensorinformationen", order=2, mb=15),
                dmc.Box(
                    children=[
                        dmc.Grid(
                            id="sensor-info-grid",
                            gutter="md",
                        )
                    ]
                ),
            ],
        ),
    ],
)
