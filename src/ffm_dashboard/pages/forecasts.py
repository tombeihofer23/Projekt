import dash
import dash_mantine_components as dmc

from src.ffm_dashboard.utils import get_infobox

dash.register_page(__name__, path="/forecasts")

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=[
                dmc.Flex(
                    justify="space-between",
                    mb=20,
                    children=[
                        dmc.Title(
                            "Temperaturentwicklung", order=2, id="forecast-title"
                        ),
                        dmc.Button(
                            "New Forecast",
                            id="fetch-forecast-button",
                            variant="filled",
                            color="#a81b00",
                        ),
                    ],
                ),
                dmc.Box(
                    mb=20,
                    children=[dmc.Box(id="forecast-graph-container")],
                ),
                dmc.Card(
                    shadow="sm",
                    padding="lg",
                    radius="md",
                    withBorder=True,
                    children=[
                        dmc.Title("Modellinformationen", order=4),
                        dmc.Group(
                            # align="space-around",
                            grow=True,
                            children=[
                                get_infobox("Modell", "MultiOutputLGBM"),
                                get_infobox("Trainingsdaten", "364.433 Samples"),
                                get_infobox("Testdaten", "91.109 Samples"),
                                get_infobox("Features", "10"),
                                get_infobox("MAE", "0.184 °C"),
                            ],
                        ),
                        dmc.Divider(mb=15),
                        dmc.Text("Letztes Training: 2025-06-27 14:22", size="sm"),
                    ],
                ),
            ],
        ),
    ],
)
