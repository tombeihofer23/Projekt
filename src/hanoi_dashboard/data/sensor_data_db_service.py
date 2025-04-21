import pandas as pd
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.hanoi_dashboard.data import DbCon, SensorData


class SensorDataWriteService:
    def __init__(self, db_con: DbCon) -> None:
        self.db_con = db_con

    @staticmethod
    def write(sensor_data: SensorData, session: Session) -> None:
        logger.debug("{}", sensor_data)
        session.add(instance=sensor_data)
        session.flush(objects=[sensor_data])

    def write_new_sensor_data(self, data: pd.DataFrame, box_id: str) -> None:
        if data is None or data.empty:
            logger.error("No data provided to write")

        insert_count: int = 0
        with self.db_con.get_session()() as session:
            for _, row in data.iterrows():
                measurement: float = row["measurement"]
                if pd.isna(measurement):
                    logger.warning(
                        "Skipping row due to NaN measurement: {}", row.to_dict()
                    )
                    continue

                timestamp: pd.Timestamp = row["timestamp"]
                if pd.isna(timestamp):
                    logger.warning(
                        "Skipping row due to invalid timestamp: {}", row.to_dict()
                    )
                    continue

                sensor_id: str = row["sensor_id"]
                if pd.isna(sensor_id):
                    logger.warning(
                        "Skipping row due to invalid sensor_id: {}", row.to_dict()
                    )
                    continue

                sensor_data_point: SensorData = SensorData.from_dict(row.to_dict())
                try:
                    self.write(sensor_data=sensor_data_point, session=session)
                    session.commit()
                    insert_count += 1
                except Exception as e:
                    logger.error(
                        "Error inserting row: {} - Error: {}", row.to_dict(), e
                    )
        logger.info("Attempted to process {} rows for box_id {}", insert_count, box_id)


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
        except Exception as e:
            logger.error("Error querying data: {}", e)
            return None

    def query_data_date_range(
        self, box_id: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        logger.info(
            "Querying data for box_id {} from {} to {}.", box_id, start_date, end_date
        )
        try:
            # cutoff_time = datetime.now(dt.timezone.utc) - timedelta(
            #     hours=time_window_hours
            # )
            query = select(SensorData).where(
                (SensorData.box_id == box_id)
                & (SensorData.timestamp.between(start_date, end_date))
            )
            with self.db_con.get_session()() as session:
                df = pd.read_sql(query, session.bind, parse_dates=["timestamp"])
            logger.info("Retrieved {} data points from db.", len(df))
            return df
        except Exception as e:
            logger.error("Error querying data: {}", e)
            return None


class SensorDataDbService:
    def __init__(self, db_con: DbCon) -> None:
        self.db_con = db_con

        self.sensor_data_write_service = SensorDataWriteService(self.db_con)
        self.sensor_data_query_servive = SensorDataQueryService(self.db_con)

    def write_new_sensor_data(self, data: pd.DataFrame, box_id: str) -> None:
        self.sensor_data_write_service.write_new_sensor_data(data, box_id)

    def query_all_data(self, box_id: str) -> pd.DataFrame:
        return self.sensor_data_query_servive.query_all_data(box_id)

    def query_data_date_range(
        self, box_id: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        return self.sensor_data_query_servive.query_data_date_range(
            box_id, start_date, end_date
        )


if __name__ == "__main__":
    db_service = SensorDataDbService(DbCon())
    qdata = db_service.query_all_data("6252afcfd7e732001bb6b9f7")
    print(qdata)
