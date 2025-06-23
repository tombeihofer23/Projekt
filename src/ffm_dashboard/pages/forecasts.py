import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/forecasts")

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=[
                dmc.Title("Temperaturvorhersagen für die nächsten 6 Stunden", order=2),
                dmc.Box(
                    children=["Forecast-Plot"],
                ),
            ],
        ),
    ],
)
