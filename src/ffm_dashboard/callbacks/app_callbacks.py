"""Callbacks für die App."""

import plotly.io as pio
from dash import ALL, Dash, Input, Output, Patch, State, clientside_callback


def register_app_callbacks(app: Dash) -> None:
    """
    Registriert alle notwendigen Callback-Funktionen für die Dash-App.

    :param app: Die Instanz der Dash-Anwendung, zu der die Callbacks hinzugefügt werden sollen.
    :type app: Dash
    """

    @app.callback(
        Output("appshell", "navbar"),
        Input("burger-button", "opened"),
        State("appshell", "navbar"),
    )
    def toggle_navbar(opened: bool, navbar: dict):
        """
        Schaltet die Sichtbarkeit der Navigationsleiste um, abhängig vom Status des Burger-Menüs.

        :param opened: Gibt an, ob das Burger-Menü geöffnet ist.
        :type opened: bool
        :param navbar: Der aktuelle Zustand der Navigationsleiste.
        :type navbar: dict
        :return: Der aktualisierte Navbar-Zustand.
        """

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
    def update_figures_template(switch_on: bool, ids: list):
        """
        Aktualisiert das Template der dynamischen Diagramme, je nach gewähltem Farbschema.

        :param switch_on: Status des Dark-Mode-Toggles (True für Dark Mode, False für Light Mode).
        :type switch_on: bool
        :param ids: Liste von Komponenten-IDs der Diagramme, die aktualisiert werden sollen.
        :type ids: list
        :return: Liste von `Patch`-Objekten zur Aktualisierung der Diagramm-Templates.
        """

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
