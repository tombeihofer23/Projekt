import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/forecasts")

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=[
                dmc.Title(
                    "Temperaturvorhersagen für die nächsten 1.5 Stunden", order=2
                ),
                dmc.Button(
                    "New Forecast",
                    id="fetch-forecast-button",
                    variant="filled",
                    color="red",
                ),
                dmc.Box(
                    children=[dmc.Box(id="forecast-graph-container", children=[])],
                ),
            ],
        ),
    ],
)
