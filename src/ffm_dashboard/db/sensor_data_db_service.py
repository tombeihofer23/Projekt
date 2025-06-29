"""Klasse für das Schreiben und Lesen der Sensordaten."""

import os
from datetime import date
from pathlib import Path
from timeit import default_timer as timer
from typing import Dict, Final

import pandas as pd
from loguru import logger
from pandantic import Pandantic
from pydantic import ValidationError
from sqlalchemy import Date, cast, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.ffm_dashboard.components import SenseBoxApi
from src.ffm_dashboard.db import DbCon, SensorData, SensorMetadata
from src.ffm_dashboard.plots import PlotData
from src.ffm_dashboard.utils import SensorDataModel


class SensorDataWriteService:
    """
    Dienstklasse zum Schreiben von Sensordaten in eine Datenbank.
    Diese Klasse validiert und schreibt eingehende Sensordaten entweder einzeln oder
    in großen Mengen, sowie die zugehörigen Metadaten.

    :param db_con: Instanz der DbCon-Klasse zur Verwaltung der Datenbankverbindung.
    :type db_con: DbCon
    :param box_id: ID der SenseBox, zu der die Sensordaten gehören.
    :type box_id: str
    """

    def __init__(self, db_con: DbCon, box_id: str) -> None:
        self.db_con = db_con
        self.box_id = box_id

    @staticmethod
    def exists_sensor_data_point(
        sensor_data_point: SensorData, session: Session
    ) -> bool:
        """
        Prüft, ob ein Sensordatenpunkt mit gleichem Zeitstempel, SensorID und BoxID
        bereits existiert.

        :param sensor_data_point: Zu prüfender Datenpunkt.
        :type sensor_data_point: SensorData
        :param session: Aktive SQLAlchemy-Session.
        :type session: Session
        :return: True, wenn der Datensatz bereits existiert, sonst False.
        :rtype: bool
        """

        statement: Final = select(func.count()).where(  # pylint: disable=not-callable
            (SensorData.timestamp == sensor_data_point.timestamp)
            & (SensorData.box_id == sensor_data_point.box_id)
            & (SensorData.sensor_id == sensor_data_point.sensor_id)
        )
        num_of_rows: Final = session.scalar(statement)
        return num_of_rows is not None and num_of_rows > 0

    def write_new_sensor_data(self, data: pd.DataFrame) -> int:
        """
        Validiert und schreibt neue Sensordaten in die Datenbank, wenn sie noch nicht existieren.

        :param data: DataFrame mit den Sensordaten.
        :type data: pd.DataFrame
        :return: Anzahl erfolgreich geschriebener Datensätze.
        :rtype: int
        """

        if data is None or data.empty:
            logger.error("No data provided to write")

        insert_count: int = 0
        with self.db_con.get_session()() as session:
            for _, row in data.iterrows():
                try:
                    SensorDataModel.model_validate_json(row.to_json())
                except ValidationError as e:
                    logger.warning(
                        "Skipping row due to invalid data: {}\n{}", row.to_dict(), e
                    )
                else:
                    sensor_data_point: SensorData = SensorData.from_dict(row.to_dict())
                    if self.exists_sensor_data_point(sensor_data_point, session):
                        logger.error(
                            "Existierender Sensor-Datenpunkt: {}", sensor_data_point
                        )
                    else:
                        logger.debug("Neuer {}", sensor_data_point)
                        session.add(instance=sensor_data_point)
                        session.flush(objects=[sensor_data_point])
                        session.commit()
                        insert_count += 1
        logger.info("Processed {} rows for box_id {}", insert_count, self.box_id)
        return insert_count

    def bulk_write_sensor_data_to_db(self, data_dir_path: Path) -> None:
        """
        Führt einen Massenimport historischer Sensordaten im Parquet-Format durch.

        :param data_dir_path: Verzeichnis mit den Parquet-Dateien.
        :type data_dir_path: Path
        """

        df_validator = Pandantic(schema=SensorDataModel)
        paths: list = [name for name in os.listdir(data_dir_path)]
        logger.debug(
            "Start writing all historical data from '{}' in db.", data_dir_path
        )
        start = timer()
        for path in paths:
            sensor_id: str = path.split("=")[1]
            logger.debug("Try to write data for sensor '{}' in db.", sensor_id)
            df: pd.DataFrame = pd.read_parquet(data_dir_path.absolute() / path)
            df["measurement"] = pd.to_numeric(df["measurement"], errors="coerce")

            # Validate DataFrame with Pandantic
            validated_df: pd.DataFrame = df_validator.validate(df, errors="skip")

            with self.db_con.get_session()() as session:
                validated_df.to_sql(
                    name=SensorData.__tablename__,
                    con=session.bind,
                    if_exists="append",
                    index=False,
                    chunksize=5000,
                    method="multi",
                )
            logger.debug("Wrote data for sensor '{}' in db.", sensor_id)

        end = timer()
        logger.debug(
            "End writing all historical data from '{}' in db. Took {}s.",
            data_dir_path,
            end - start,
        )

    def write_sensor_metadata(self) -> None:
        """Ruft Sensormetadaten über die SenseBox API ab und schreibt sie in die Datenbank."""

        sense_box_api = SenseBoxApi(self.box_id)
        metadata_df: pd.DataFrame = sense_box_api.get_sensors_information_for_box()

        with self.db_con.get_session()() as session:
            try:
                metadata_df.to_sql(
                    name=SensorMetadata.__tablename__,
                    con=session.bind,
                    if_exists="fail",
                    index=False,
                )
                logger.info("Wrote metadata table to db.")
            except ValueError:
                logger.info("Metadata table already exists.")


class SensorDataQueryService:
    """
    Dienstklasse für Datenbankabfragen zu Sensordaten und Sensor-Metadaten.

    :param db_con: Instanz der DbCon-Klasse zur Verwaltung der Datenbankverbindung.
    :type db_con: DbCon
    :param box_id: ID der SenseBox, zu der die Sensordaten gehören.
    :type box_id: str
    """

    def __init__(self, db_con: DbCon, box_id: str) -> None:
        self.db_con = db_con
        self.box_id = box_id

    def query_all_data(self) -> pd.DataFrame:
        """
        Lädt alle Sensordaten für die angegebene Box-ID.

        :return: DataFrame mit allen Datenpunkten.
        :rtype: pd.DataFrame
        """

        logger.info("Querying all data for box_id {}.", self.box_id)
        try:
            query = select(SensorData).where(SensorData.box_id == self.box_id)
            with self.db_con.get_session()() as session:
                df = pd.read_sql(query, session.bind, parse_dates=["timestamp"])
            logger.info("Retrieved {} data points from db.", len(df))
            return df
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error while querying data: {}", e)
        except ValueError as e:
            logger.error("ValueError while parsing result: {}", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error while querying data: {}", e)
        return None

    def query_sensors_metadata(self) -> pd.DataFrame:
        """
        Lädt alle Sensor-Metadaten aus der Datenbank.

        :return: DataFrame mit Metadaten der Sensoren.
        :rtype: pd.DataFrame
        """

        logger.info("Query sensor metadata for box_id {}.", self.box_id)
        try:
            query = select(SensorMetadata)
            with self.db_con.get_session()() as session:
                df: pd.DataFrame = pd.read_sql(query, session.bind)
                return df
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error while querying data: {}", e)

    def query_data_from_a_date_on(self, from_date: date) -> pd.DataFrame:
        """
        Fragt alle Sensordaten ab einem bestimmten Datum ab.

        :param from_date: Startdatum der Abfrage.
        :type from_date: date
        :return: DataFrame mit den Sensordaten ab dem angegebenen Datum.
        :rtype: pd.DataFrame
        """

        logger.info(
            "Querying data for box_id {} from {} to now.",
            self.box_id,
            from_date.strftime("%Y-%m-%d"),
        )
        try:
            query = select(SensorData).where(
                (SensorData.box_id == self.box_id)
                & (cast(SensorData.timestamp, Date) > from_date)
            )
            with self.db_con.get_session()() as session:
                df = pd.read_sql(query, session.bind, parse_dates=["timestamp"])
            logger.info("Retrieved {} data points from db.", len(df))
            return df
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error while querying data: {}", e)
        except ValueError as e:
            logger.error("ValueError while parsing result: {}", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error while querying data: {}", e)
        return None

    def query_plot_data(
        self,
        sensor_ids: list[str],
        date_range: list[pd.Timestamp],
    ) -> Dict[str, PlotData]:
        """
        Abfrage aufbereiteter Plotdaten für bestimmte Sensoren in einem Zeitbereich.
        Die Daten werden abhängig vom Zeitraum aus unterschiedlichen aggregierten Tabellen geladen.

        :param sensor_ids: Liste der Sensor-IDs.
        :type sensor_ids: list[str]
        :param date_range: Zeitbereich im Format [Startdatum, Enddatum].
        :type date_range: list[pd.Timestamp]
        :return: Dictionary mit Sensor-ID als Schlüssel und `PlotData`-Objekten als Wert.
        :rtype: Dict[str, PlotData]
        """

        sensor_sql_dict: dict = {
            "5d6d5269953683001ae46ae1": "temperature",
            "5d6d5269953683001ae46add": "pm10",
            "5d6d5269953683001ae46ade": "pm25",
            "607fe08260979a001bd13188": "airpressure",
            "5d6d5269953683001ae46ae0": "humidity",
            "5e7f6fecf7afec001bf5b1a3": "illuminance",
        }
        delta: int = (date_range[1] - date_range[0]).days
        time_table: str = (
            "view" if delta <= 3 else "hourly_avg" if delta <= 31 else "daily_avg"
        )
        sensors_metadata: pd.DataFrame = self.query_sensors_metadata()
        plot_data_dict: dict = {}
        try:
            with self.db_con.get_session()() as session:
                for sensor_id in sensor_ids:
                    table: str = f"{sensor_sql_dict[sensor_id]}_{time_table}"
                    query_str: str = f"select * from \"{table}\" where \"timestamp\"::date between date '{date_range[0].strftime('%Y-%m-%d')}' and date '{date_range[1].strftime('%Y-%m-%d')}'"  # pylint: disable=line-too-long
                    query = text(query_str)
                    df: pd.DataFrame = pd.read_sql(
                        query, session.bind, parse_dates=["timestamp"]
                    )
                    df["timestamp"] = df["timestamp"].map(
                        lambda x: x.tz_convert("Europe/Berlin")
                    )
                    sensor_metadata = sensors_metadata[
                        sensors_metadata["sensor_id"] == sensor_id
                    ]
                    plot_data: PlotData = PlotData(
                        df.timestamp,
                        df.measurement,
                        sensor_metadata.title.iloc[0],
                        sensor_metadata.unit.iloc[0],
                    )
                    plot_data_dict[sensor_id] = plot_data
                return plot_data_dict
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error while querying data: {}", e)
        except ValueError as e:
            logger.error("ValueError while parsing result: {}", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error while querying data: {}", e)


class SensorDataDbService:
    """
    DB-Service-Klasse zur Verwaltung von Lese- und Schreiboperationen auf der Sensordatenbank.
    Diese Klasse vereint Funktionen des `SensorDataWriteService` und `SensorDataQueryService`.

    :param db_con: Datenbankverbindung.
    :type db_con: DbCon
    :param box_id: ID der SenseBox.
    :type box_id: str
    """

    def __init__(self, db_con: DbCon, box_id: str) -> None:
        self.db_con = db_con
        self.box_id = box_id

        self.sensor_data_write_service = SensorDataWriteService(
            self.db_con, self.box_id
        )
        self.sensor_data_query_servive = SensorDataQueryService(
            self.db_con, self.box_id
        )

    # Write data in db
    def write_new_sensor_data(self, data: pd.DataFrame) -> int:
        """Methode wird oben beschrieben."""
        return self.sensor_data_write_service.write_new_sensor_data(data)

    def bulk_write_sensor_data_to_db(self, data_dir_path: Path) -> None:
        """Methode wird oben beschrieben."""
        self.sensor_data_write_service.bulk_write_sensor_data_to_db(data_dir_path)

    def write_sensor_metadata(self) -> None:
        """Methode wird oben beschrieben."""
        self.sensor_data_write_service.write_sensor_metadata()

    # Get data from db
    def query_all_data(self) -> pd.DataFrame:
        """Methode wird oben beschrieben."""
        return self.sensor_data_query_servive.query_all_data()

    def query_data_from_a_date_on(self, from_date: date) -> pd.DataFrame:
        """Methode wird oben beschrieben."""
        return self.sensor_data_query_servive.query_data_from_a_date_on(from_date)

    def query_plot_data(
        self, sensor_ids: list[str], date_range: list[pd.Timestamp]
    ) -> Dict[str, PlotData]:
        """Methode wird oben beschrieben."""
        return self.sensor_data_query_servive.query_plot_data(sensor_ids, date_range)


if __name__ == "__main__":
    db_service = SensorDataDbService(DbCon(), "5d6d5269953683001ae46adc")

    db_service.write_sensor_metadata()
    # tdf = db_service.query_data_from_a_date_on(date(2025, 4, 15))
    # print(tdf.head())
    # print(len(tdf))
    # data_path = (
    #     Path(__file__).parent.parent.parent.parent / "data/5d6d5269953683001ae46adc"
    # )
    # db_service.bulk_write_sensor_data_to_db(data_path)
