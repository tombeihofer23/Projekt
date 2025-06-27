import dash_mantine_components as dmc
from dash_iconify import DashIconify


def get_infobox(header: str, info: str):
    return dmc.Paper(
        withBorder=True,
        shadow="sm",
        radius="md",
        p="md",
        my=15,
        children=[
            dmc.Stack(
                align="center",
                gap="xs",
                children=[
                    dmc.Text(header, fw=700),
                    dmc.Text(info),
                ],
            ),
        ],
    )


def get_icon(icon: str, height: int) -> DashIconify:
    return DashIconify(icon=icon, height=height)
