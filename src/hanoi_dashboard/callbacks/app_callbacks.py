from dash import Dash, Input, Output, State


def register_app_callbacks(app: Dash) -> None:
    @app.callback(
        Output("appshell", "navbar"),
        Input("burger-button", "opened"),
        State("appshell", "navbar"),
    )
    def toggle_navbar(opened, navbar):
        navbar["collapsed"] = {"desktop": not opened}
        return navbar
