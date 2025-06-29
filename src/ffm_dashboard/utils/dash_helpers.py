"""Hilfsfunktionen für Plotly Dash Elemente."""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def get_infobox(header: str, info: str):
    """
    Erstellt eine optisch hervorgehobene Infobox im Stil einer Karte.

    Die Box besteht aus einem Titel (fett) und einem kurzen Informationstext.

    :param header: Überschrift der Infobox (z.B. "Letztes Update")
    :type header: str
    :param info: Inhalt bzw. Informationstext (z.B. "15 Minuten alt")
    :type info: str
    :return: Eine gestylte dmc.Paper-Komponente zur Anzeige der Info
    :rtype: dash_mantine_components.Paper
    """

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
    """
    Erstellt ein DashIconify-Icon.

    :param icon: Icon-Identifier im Format "iconset:icon-name", z.B. "bi:cpu-fill"
    :type icon: str
    :param height: Höhe des Icons in Pixeln
    :type height: int
    :return: DashIconify-Komponente mit gewünschtem Icon und Größe
    :rtype: DashIconify
    """

    return DashIconify(icon=icon, height=height)
