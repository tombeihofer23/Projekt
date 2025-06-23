from dash import Dash, Input, Output


def register_forecast_callbacks(app: Dash) -> None:
    @app.callback(Output("test", "test"), Input("test", "test"))
    def dummy():
        pass
