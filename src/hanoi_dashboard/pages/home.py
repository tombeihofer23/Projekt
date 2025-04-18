import dash
import dash_mantine_components as dmc
from dash import dcc, html

dash.register_page(__name__, path="/")

layout = dmc.Box(
    children=[
        dmc.Box(
            mt=15,
            mx=15,
            children=[
                dmc.Center(
                    dmc.Title(
                        children=f"OpenSenseMap Sensor Data (Box: {'6252afcfd7e732001bb6b9f7'})",
                        order=1,
                    ),
                ),
                dmc.Text(
                    id="output-status",
                    children="Dashboard loaded. Click button to fetch initial data.",
                ),
                # Interval component for automatic refresh (optional)
                # dcc.Interval(
                #     id='interval-component',
                #     interval=5*60*1000, # in milliseconds (e.g., 5 minutes)
                #     n_intervals=0
                # ),
                # Store for holding graph data (JSON format)
                dcc.Store(id="graph-data-store"),
                # Container where graphs will be dynamically added
                dmc.Box(
                    id="graph-container",
                    children=[
                        dmc.Grid(
                            id="graph-grid",
                            gutter="md",
                            children=[
                                html.P("Graphs will appear here after fetching data.")
                            ],
                        )
                    ],
                ),
                dmc.Divider(variant="solid"),
                html.Footer("Dashboard End"),
            ],
        ),
    ]
)
