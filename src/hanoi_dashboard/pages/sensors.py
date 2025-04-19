import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/sensors")

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=[
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
