import dash_mantine_components as dmc
from dash_iconify import DashIconify


def get_icon(icon: str) -> DashIconify:
    return DashIconify(icon=icon, height=20)


def create_navbar():
    return dmc.AppShellNavbar(
        id="navbar",
        children=[
            dmc.NavLink(
                label="Home",
                href="/",
                leftSection=get_icon("bi:house-door-fill"),
                rightSection=get_icon("tabler-chevron-right"),
            ),
            dmc.NavLink(
                label="Sensors",
                href="/sensors",
                leftSection=get_icon("bi:cpu-fill"),
                rightSection=get_icon("tabler-chevron-right"),
            ),
            dmc.NavLink(
                label="Forecast",
                href="/forecasts",
                leftSection=get_icon("bi:graph-up-arrow"),
                rightSection=get_icon("tabler-chevron-right"),
            ),
        ],
    )
