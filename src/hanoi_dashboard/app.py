import dash
import dash_mantine_components as dmc
from dash import Dash, dcc

from src.hanoi_dashboard.callbacks import register_home_callbacks

app = Dash(__name__, use_pages=True, external_stylesheets=dmc.styles.ALL)
app.title = "Hanoi Sensor Data Dashboard"
app.layout = dmc.MantineProvider(
    children=[
        dash.page_container,
        # automatische Abfrage neuer Daten alle 10 Minuten
        dcc.Interval(
            id="interval-component",
            interval=10 * 60 * 1000,  # 10min in Millisekunden
            n_intervals=0,
        ),
        # Speicher für die Graph-Daten (JSON format)
        dcc.Store(id="graph-data-store"),
    ]
)

# Register callbacks
register_home_callbacks(app)
