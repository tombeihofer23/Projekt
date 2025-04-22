import plotly.io as pio
from dash import ALL, Dash, Input, Output, Patch, State, clientside_callback


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

    @app.callback(
        Output({"type": "dynamic-graph", "index": ALL}, "figure"),
        Input("color-scheme-toggle", "checked"),
        State({"type": "dynamic-graph", "index": ALL}, "id"),
    )
    def update_figures_template(switch_on: bool, ids):
        template = (
            pio.templates["mantine_light"]
            if not switch_on
            else pio.templates["mantine_dark"]
        )
        patched_figures = []
        for _ in ids:
            patched_fig = Patch()
            patched_fig["layout"]["template"] = template
            patched_figures.append(patched_fig)

        return patched_figures
