import dash
import dash_mantine_components as dmc
from dash import Dash, dcc

from src.hanoi_dashboard.callbacks import (
    register_app_callbacks,
    register_sensors_callbacks,
)
from src.hanoi_dashboard.elements import create_header, create_navbar

dmc.add_figure_templates(default="mantine_light")

app = Dash(__name__, use_pages=True, external_stylesheets=dmc.styles.ALL)
app.title = "Hanoi Sensor Data Dashboard"

layout = dmc.AppShell(
    [
        create_header(),
        create_navbar(),
        dmc.AppShellMain(dash.page_container),
    ],
    header={"height": 60},
    navbar={
        "width": 300,
        "breakpoint": "sm",
        "collapsed": {"desktop": True},
    },
    id="appshell",
)

app.layout = dmc.MantineProvider(
    id="mantine-provider",
    forceColorScheme="light",
    children=[
        # automatische Abfrage neuer Daten alle 10 Minuten
        dcc.Interval(
            id="interval-component",
            interval=10 * 60 * 1000,  # 10min in Millisekunden
            n_intervals=0,
        ),
        # Speicher für die Graph-Daten (JSON format)
        dcc.Store(id="graph-data-store"),
        dmc.NotificationProvider(),
        layout,
    ],
)

# Register callbacks
register_app_callbacks(app)
register_sensors_callbacks(app)
