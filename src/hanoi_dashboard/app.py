import dash
import dash_mantine_components as dmc
from dash import Dash

from src.hanoi_dashboard.callbacks import register_home_callbacks

app = Dash(__name__, use_pages=True, external_stylesheets=dmc.styles.ALL)
app.title = "Hanoi Sensor Data Dashboard"
app.layout = dmc.MantineProvider(dash.page_container)

# Register callbacks
register_home_callbacks(app)
