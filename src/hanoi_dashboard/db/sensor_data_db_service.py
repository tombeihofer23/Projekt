from typing import Final

import pandas as pd
from loguru import logger
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.hanoi_dashboard.db import DbCon, SensorData
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

    def write_new_sensor_data(self, data: pd.DataFrame, box_id: str) -> int:
        return self.sensor_data_write_service.write_new_sensor_data(data, box_id)

    def query_all_data(self, box_id: str) -> pd.DataFrame:
        return self.sensor_data_query_servive.query_all_data(box_id)

    # def query_data_date_range(
    #     self, box_id: str, start_date: str, end_date: str
    # ) -> pd.DataFrame:
    #     return self.sensor_data_query_servive.query_data_date_range(
    #         box_id, start_date, end_date
    #     )


if __name__ == "__main__":
    db_service = SensorDataDbService(DbCon())
    qdata = db_service.query_all_data("6252afcfd7e732001bb6b9f7")
    print(qdata)
