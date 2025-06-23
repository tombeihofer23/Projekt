from typing import Final

import dash
import dash_mantine_components as dmc
from dash import Dash, dcc

from src.ffm_dashboard.callbacks import (
    register_app_callbacks,
    register_home_callbacks,
    register_sensors_callbacks,
)
from src.ffm_dashboard.components import SenseBoxApi
from src.ffm_dashboard.db import DbCon, SensorDataDbService
from src.ffm_dashboard.elements import create_header, create_navbar

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
        # automatische Abfrage neuer Daten alle 4 Minuten
        dcc.Interval(
            id="interval-component",
            interval=4 * 60 * 1000,  # 4min in Millisekunden
            n_intervals=0,
        ),
        dcc.Location(id="url", refresh=False),
        dmc.NotificationProvider(),
        dcc.Store(id="sensor-plot-update-trigger"),
        layout,
    ],
)

SENSE_BOX_API: Final = SenseBoxApi("5d6d5269953683001ae46adc")
DB_CON: Final = DbCon()
DB_SERVICE: Final = SensorDataDbService(DB_CON, box_id="5d6d5269953683001ae46adc")

# Register callbacks
register_app_callbacks(app)
register_home_callbacks(app, SENSE_BOX_API)
register_sensors_callbacks(app, SENSE_BOX_API, DB_SERVICE)
