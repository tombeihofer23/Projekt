"""Initialisierung der App im Docker-Container."""

import argparse
from pathlib import Path
from typing import Final

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from src.ffm_dashboard.app import DB_CON, DB_SERVICE, SENSE_BOX_API

DATA_PATH: Final = Path(__file__).parent / "data"


def is_database_ready():
    """
    Prüft, ob eine Verbindung zur Datenbank erfolgreich aufgebaut werden kann.

    Führt eine einfache SQL-Anfrage aus, um sicherzustellen, dass die Datenbank verfügbar ist.
    Im Fehlerfall wird ein Fehler geloggt und `False` zurückgegeben.

    :return: True, wenn Verbindung erfolgreich, sonst False.
    :rtype: bool
    """

    try:
        with DB_CON.get_session()() as session:
            session.execute(text("SELECT 1"))
        logger.info("Verbindung zur Datenbank erfolgreich!")
        return True
    except OperationalError:
        logger.error("Datenbank ist nicht erreichbar - abbruch des Vorgangs!")
        return False


def load_and_store_historical_data():
    """
    Lädt historische Sensordaten von der SenseBox API und speichert sie in die Datenbank.

    1. Holt alle historischen Daten von einer SenseBox.
    2. Speichert die Daten in der Datenbank via Bulk-Insertion.

    Achtung:
        Dieser Vorgang kann je nach Datenmenge mehrere Minuten bis Stunden dauern.
    """

    SENSE_BOX_API.fetch_all_historical_data_for_one_box(DATA_PATH)
    DB_SERVICE.bulk_write_sensor_data_to_db(DATA_PATH)


def start_app():
    """
    Initialisiert das Dashboard mit optionalem Laden historischer Daten.

    Schritte:
        1. Prüft, ob die Datenbank erreichbar ist.
        2. Liest Kommandozeilenargumente ein.
        3. Schreibt Metadaten der Sensoren in die Datenbank.
        4. Optional: Lädt historische Daten und schreibt sie in die Datenbank.
    """

    if not is_database_ready():
        return 0

    parser = argparse.ArgumentParser(description="Startet das Dashboard")
    parser.add_argument(
        "--with-historical",
        action="store_true",
        help="Zusätzlich zu den Metadaten auch historische Daten laden",
    )
    args = parser.parse_args()

    DB_SERVICE.write_sensor_metadata()

    if args.with_historical:
        logger.warning(
            "Alle historischen Daten der SenseBox werden geladen"
            "und in DB geschrieben. Kann bis zu 1h oder länger dauern!"
        )
        load_and_store_historical_data()


if __name__ == "__main__":
    start_app()
