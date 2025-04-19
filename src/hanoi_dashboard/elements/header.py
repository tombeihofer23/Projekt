import dash_mantine_components as dmc


def create_header():
    return dmc.AppShellHeader(
        [
            dmc.Group(
                [
                    dmc.Burger(
                        id="burger-button",
                        size="sm",
                        # hiddenFrom="sm",
                        opened=False,
                    ),
                    # dmc.Image(src=logo, h=40),
                    dmc.Title(
                        children=f"OpenSenseMap Sensor Data (Box: {'6252afcfd7e732001bb6b9f7'})",
                        order=1,
                    ),
                ],
                h="100%",
                px="md",
            ),
        ],
    )
