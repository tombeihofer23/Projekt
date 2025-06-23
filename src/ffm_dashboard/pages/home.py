import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path="/", redirect_from=["/home"])

layout = dmc.Box(
    children=[
        dmc.Box(
            m=15,
            children=["Home Page"],
        ),
    ],
)
