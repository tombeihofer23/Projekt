import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/")

layout = dmc.Box(
    children=[
        dmc.Box(
            mt=15,
            mx=15,
            children=[
                # dmc.Center(
                #     dmc.Title(
                #         children=f"OpenSenseMap Sensor Data (Box: {'6252afcfd7e732001bb6b9f7'})",
                #         order=1,
                #     ),
                #     pb=25,
                # ),
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
