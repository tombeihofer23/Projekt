import dash_mantine_components as dmc
from dash_iconify import DashIconify

theme_toggle = dmc.Switch(
    offLabel=DashIconify(
        icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]
    ),
    onLabel=DashIconify(
        icon="radix-icons:moon",
        width=15,
        color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
    ),
    id="color-scheme-toggle",
    persistence=True,
    color="grey",
)


def create_header():
    return dmc.AppShellHeader(
        [
            dmc.Group(
                [
                    dmc.Group(
                        [
                            dmc.Burger(
                                id="burger-button",
                                size="sm",
                                # hiddenFrom="sm",
                                opened=False,
                            ),
                            dmc.Image(
                                src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Coat_of_arms_of_Frankfurt_%28temporarily_in_Weimar_Republic%29.svg/250px-Coat_of_arms_of_Frankfurt_%28temporarily_in_Weimar_Republic%29.svg.png",
                                h=40,
                            ),
                            dmc.Title(
                                children="FFM Westend Süd SenseBox Dashboard",
                                c="#a81b00",
                            ),
                        ],
                    ),
                    theme_toggle,
                ],
                justify="space-between",
                style={"flex": 1},
                h="100%",
                px="md",
            ),
        ],
    )
