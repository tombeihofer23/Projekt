from dash import Dash

from src.hanoi_dashboard.callbacks import register_home_callbacks

app = Dash(__name__, use_pages=True)
app.title = "Hanoi Sensor Data Dashboard"

# Register callbacks
register_home_callbacks(app)
