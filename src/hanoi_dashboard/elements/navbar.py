import dash_mantine_components as dmc


def create_navbar():
    return dmc.AppShellNavbar(
        id="navbar",
        children=[
            "Navbar",
            dmc.NavLink(label="home", href="/"),
            dmc.NavLink(label="test", href="/test"),
        ],
        p="md",
    )
