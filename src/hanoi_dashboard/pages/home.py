import dash
from dash import dcc, html

dash.register_page(__name__, path="/")

layout = html.Div(
    children=[
        html.H1(
            children=f"OpenSenseMap Sensor Data (Box: {'6252afcfd7e732001bb6b9f7'})"
        ),
        html.Button("Fetch Latest Data & Update Graphs", id="fetch-button", n_clicks=0),
        html.Div(
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
        html.Div(
            id="graph-container",
            children=[html.P("Graphs will appear here after fetching data.")],
        ),
        html.Hr(),
        html.Footer("Dashboard End"),
    ]
)
