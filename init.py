from pathlib import Path
from typing import Final

from src.hanoi_dashboard.app import DB_SERVICE, SENSE_BOX_API

DB_PATH: Final = Path("data/...")


def data_already_exists():
    return DB_PATH.exists()


def load_and_store_data():
    SENSE_BOX_API.fetch_all_historical_data_for_one_box(DB_PATH)
    DB_SERVICE.bulk_write_sensor_data_to_db(DB_PATH)


if __name__ == "__main__":
    if data_already_exists():
        print("Datenbank existiert bereits – Initialisierung wird übersprungen.")
    else:
        load_and_store_data()
