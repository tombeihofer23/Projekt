import dash_mantine_components as dmc


def create_navbar():
    return dmc.AppShellNavbar(
        id="navbar",
        children=[
            dmc.NavLink(label="Home", href="/"),
            dmc.NavLink(label="Sensors", href="/sensors"),
        ],
        p="md",
    )
