from dash import Dash, Input, Output, State, clientside_callback


def register_app_callbacks(app: Dash) -> None:
    @app.callback(
        Output("appshell", "navbar"),
        Input("burger-button", "opened"),
        State("appshell", "navbar"),
    )
    def toggle_navbar(opened, navbar):
        navbar["collapsed"] = {"desktop": not opened}
        return navbar

    clientside_callback(
        """ 
    (switchOn) => {
    document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'dark' : 'light');  
    return window.dash_clientside.no_update
    }
    """,
        Output("color-scheme-toggle", "id"),
        Input("color-scheme-toggle", "checked"),
    )
