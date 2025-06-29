"""Start der App."""

from src.ffm_dashboard.app import app


def main():
    """
    Startet die Dash-Anwendung im Debug-Modus auf allen Netzwerk-Interfaces.

    Die Anwendung wird lokal auf Port 8050 verfügbar gemacht.
    Dies ist besonders nützlich für die Entwicklung und das lokale Testen
    im Netzwerk (z.B. auf mobilen Geräten oder anderen Rechnern im LAN).
    """

    app.run(debug=True, host="0.0.0.0", port=8050)
