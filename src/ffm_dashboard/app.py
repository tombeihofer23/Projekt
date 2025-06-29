"""Instanziierung der Plotly Dash App."""

from typing import Final

import dash
import dash_mantine_components as dmc
from dash import Dash, dcc

from src.ffm_dashboard.callbacks import (
    register_app_callbacks,
    register_forecast_callbacks,
    register_home_callbacks,
    register_sensors_callbacks,
)
from src.ffm_dashboard.components import SenseBoxApi
from src.ffm_dashboard.db import DbCon, SensorDataDbService
from src.ffm_dashboard.elements import create_header, create_navbar

SENSE_BOX_ID: Final = "5d6d5269953683001ae46adc"

dmc.add_figure_templates(default="mantine_light")

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=dmc.styles.ALL,
    suppress_callback_exceptions=True,
)
app.title = "FFM Sensor Data Dashboard"

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
        dcc.Location(id="url", refresh=False),
        dmc.NotificationProvider(),
        dcc.Store(id="sensor-plot-update-trigger"),
        layout,
    ],
)

SENSE_BOX_API: Final = SenseBoxApi(SENSE_BOX_ID)
DB_CON: Final = DbCon()
DB_SERVICE: Final = SensorDataDbService(DB_CON, box_id=SENSE_BOX_ID)

# Register callbacks
register_app_callbacks(app)
register_home_callbacks(app, SENSE_BOX_API)
register_sensors_callbacks(app, SENSE_BOX_API, DB_SERVICE)
register_forecast_callbacks(app, SENSE_BOX_API)
