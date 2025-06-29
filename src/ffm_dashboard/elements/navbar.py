"""Navigations-Element für Dashboard."""

import dash_mantine_components as dmc

from src.ffm_dashboard.utils import get_icon


def create_navbar():
    """
    Erstellt die Navigationsleiste (Navbar) für das SenseBox-Dashboard.

    Die Navbar enthält folgende Navigationslinks:

    - **Home**: Startseite des Dashboards.
    - **Sensors**: Ansicht der verfügbaren Sensordaten.
    - **Forecast**: Darstellung von Vorhersagemodellen.

    Jeder Link ist mit einem Icon auf der linken und einem Chevron-Rechts-Pfeil
    auf der rechten Seite versehen, um die Navigation optisch zu unterstützen.

    :return: Ein `AppShellNavbar`-Komponentenobjekt von Dash Mantine Components.
    :rtype: dmc.AppShellNavbar
    """

    return dmc.AppShellNavbar(
        id="navbar",
        children=[
            dmc.NavLink(
                label="Home",
                href="/",
                leftSection=get_icon("bi:house-door-fill", 20),
                rightSection=get_icon("tabler-chevron-right", 20),
            ),
            dmc.NavLink(
                label="Sensors",
                href="/sensors",
                leftSection=get_icon("bi:cpu-fill", 20),
                rightSection=get_icon("tabler-chevron-right", 20),
            ),
            dmc.NavLink(
                label="Forecast",
                href="/forecasts",
                leftSection=get_icon("bi:graph-up-arrow", 20),
                rightSection=get_icon("tabler-chevron-right", 20),
            ),
        ],
    )
