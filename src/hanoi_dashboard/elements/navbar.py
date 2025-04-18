import dash_mantine_components as dmc


def create_navbar():
    return dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.TabsTab(
                        dmc.NavLink(label="home", href="/"),
                        value="home",
                    ),
                    dmc.TabsTab(
                        dmc.NavLink(label="test", href="/test"),
                        value="test",
                    ),
                ]
            )
        ],
        value="home",
    )
