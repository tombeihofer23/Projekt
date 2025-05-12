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

from src.hanoi_dashboard.db import DbCon, SensorData, SensorMetadata
from src.hanoi_dashboard.plots import PlotData
from src.hanoi_dashboard.utils import SensorDataModel


class SensorDataWriteService:
    def __init__(self, db_con: DbCon) -> None:
        self.db_con = db_con

    @staticmethod
    def exists_sensor_data_point(
        sensor_data_point: SensorData, session: Session
    ) -> bool:
        statement: Final = select(func.count()).where(  # pylint: disable=not-callable
            (SensorData.measurement == sensor_data_point.measurement)
            & (SensorData.box_id == sensor_data_point.box_id)
            & (SensorData.sensor_id == sensor_data_point.sensor_id)
        )
        num_of_rows: Final = session.scalar(statement)
        return num_of_rows is not None and num_of_rows > 0

    def write_new_sensor_data(self, data: pd.DataFrame, box_id: str) -> int:
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
        logger.info("Processed {} rows for box_id {}", insert_count, box_id)
        return insert_count

    def bulk_write_sensor_data_to_db(self, data_dir_path: Path) -> None:
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


class SensorDataQueryService:
    def __init__(self, db_con: DbCon) -> None:
        self.db_con = db_con

    def query_all_data(self, box_id: str) -> pd.DataFrame:
        logger.info("Querying all data for box_id {}.", box_id)
        try:
            query = select(SensorData).where(SensorData.box_id == box_id)
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
        # logger.info("Query sensor metadata for box_id {}.", box_id)
        try:
            query = select(SensorMetadata)
            with self.db_con.get_session()() as session:
                df: pd.DataFrame = pd.read_sql(query, session.bind)
                return df
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error while querying data: {}", e)

    def query_data_from_a_date_on(self, box_id: str, from_date: date) -> pd.DataFrame:
        logger.info(
            "Querying data for box_id {} from {} to now.",
            box_id,
            from_date.strftime("%Y-%m-%d"),
        )
        try:
            query = select(SensorData).where(
                cast(SensorData.timestamp, Date) > from_date
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
                    query_str: str = f"select * from \"{table}\" where \"timestamp\"::date between date '{date_range[0].strftime('%Y-%m-%d')}' and date '{date_range[1].strftime('%Y-%m-%d')}'"
                    query = text(query_str)
                    df: pd.DataFrame = pd.read_sql(
                        query, session.bind, parse_dates=["timestamp"]
                    )
                    sensor_metadata = sensors_metadata[
                        sensors_metadata["sensor_id"] == sensor_id
                    ]
                    plot_data: PlotData = PlotData(
                        df.timestamp,
                        df.measurement,
                        sensor_metadata.title,
                        sensor_metadata.unit,
                    )
                    plot_data_dict[sensor_id] = plot_data
                return plot_data_dict
        except SQLAlchemyError as e:
            logger.error("SQLAlchemy error while querying data: {}", e)
        except ValueError as e:
            logger.error("ValueError while parsing result: {}", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error while querying data: {}", e)

    # def query_data_date_range(
    #     self, box_id: str, start_date: str, end_date: str
    # ) -> pd.DataFrame:
    #     logger.info(
    #         "Querying data for box_id {} from {} to {}.", box_id, start_date, end_date
    #     )
    #     try:
    #         query = select(SensorData).where(
    #             (SensorData.box_id == box_id)
    #             & (SensorData.timestamp.between(start_date, end_date))
    #         )
    #         with self.db_con.get_session()() as session:
    #             df = pd.read_sql(query, session.bind, parse_dates=["timestamp"])
    #         logger.info("Retrieved {} data points from db.", len(df))
    #         return df
    #     except Exception as e:
    #         logger.error("Error querying data: {}", e)
    #         return None


class SensorDataDbService:
    def __init__(self, db_con: DbCon) -> None:
        self.db_con = db_con

        self.sensor_data_write_service = SensorDataWriteService(self.db_con)
        self.sensor_data_query_servive = SensorDataQueryService(self.db_con)

    # Write data in db
    def write_new_sensor_data(self, data: pd.DataFrame, box_id: str) -> int:
        return self.sensor_data_write_service.write_new_sensor_data(data, box_id)

    def bulk_write_sensor_data_to_db(self, data_dir_path: Path) -> None:
        self.sensor_data_write_service.bulk_write_sensor_data_to_db(data_dir_path)

    # Get data from db
    def query_all_data(self, box_id: str) -> pd.DataFrame:
        return self.sensor_data_query_servive.query_all_data(box_id)

    def query_data_from_a_date_on(self, box_id: str, from_date: date) -> pd.DataFrame:
        return self.sensor_data_query_servive.query_data_from_a_date_on(
            box_id, from_date
        )

    def query_plot_data(
        self, sensor_ids: list[str], date_range: list[pd.Timestamp]
    ) -> Dict[str, PlotData]:
        return self.sensor_data_query_servive.query_plot_data(sensor_ids, date_range)

    # def query_data_date_range(
    #     self, box_id: str, start_date: str, end_date: str
    # ) -> pd.DataFrame:
    #     return self.sensor_data_query_servive.query_data_date_range(
    #         box_id, start_date, end_date
    #     )


if __name__ == "__main__":
    db_service = SensorDataDbService(DbCon())

    tdf = db_service.query_data_from_a_date_on(
        "5d6d5269953683001ae46adc", date(2025, 4, 15)
    )
    print(tdf.head())
    print(len(tdf))
    # data_path = (
    #     Path(__file__).parent.parent.parent.parent / "data/5d6d5269953683001ae46adc"
    # )
    # db_service.bulk_write_sensor_data_to_db(data_path)
