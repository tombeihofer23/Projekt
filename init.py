import argparse
from pathlib import Path
from typing import Final

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from src.ffm_dashboard.app import DB_CON, DB_SERVICE  # , SENSE_BOX_API

DATA_PATH: Final = Path(__file__).parent / "data"


def is_database_ready():
    try:
        with DB_CON.get_session()() as session:
            session.execute(text("SELECT 1"))
        logger.info("Verbindung zur Datenbank erfolgreich!")
        return True
    except OperationalError:
        logger.error("Datenbank ist nicht erreichbar - abbruch des Vorgangs!")
        return False


# def load_and_store_data():
#     SENSE_BOX_API.fetch_all_historical_data_for_one_box(DB_PATH)
#     DB_SERVICE.bulk_write_sensor_data_to_db(DB_PATH)


def start_app():
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
        print("lade historische Daten")


if __name__ == "__main__":
    start_app()
