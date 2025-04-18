import dash
import dash_mantine_components as dmc
from dash import Dash, dcc

from src.hanoi_dashboard.callbacks import register_home_callbacks

app = Dash(__name__, use_pages=True, external_stylesheets=dmc.styles.ALL)
app.title = "Hanoi Sensor Data Dashboard"
app.layout = dmc.MantineProvider(
    children=[
        dash.page_container,
        dcc.Interval(
            id="interval-component",
            interval=10 * 60 * 1000,  # 10min in Millisekunden
            n_intervals=0,
        ),
    ]
)

# Register callbacks
register_home_callbacks(app)
