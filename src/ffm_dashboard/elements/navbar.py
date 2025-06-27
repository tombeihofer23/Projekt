import dash_mantine_components as dmc

from src.ffm_dashboard.utils import get_icon


def create_navbar():
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
