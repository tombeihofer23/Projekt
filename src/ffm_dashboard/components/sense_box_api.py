import gc
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from timeit import default_timer as timer

import pandas as pd
import requests
from loguru import logger
from requests import Response
from requests.models import PreparedRequest


class NoDataFoundError(Exception):
    """Exception, falls ein API-Call keine Daten zurückliefert"""

    def __init__(self, url: str, params: dict | None) -> None:
        req = PreparedRequest()
        req.prepare_url(url, params)
        self.complete_url = req.url
        super().__init__(f"Keine Daten unter '{self.complete_url}' gefunden.")


class SenseBoxDataLoader:
    def __init__(self, base_url: str, box_id: str) -> None:
        self.base_url = base_url
        self.box_id = box_id

    @staticmethod
    def create_time_intervals(start_date: str, day_step: int = 10):
        start_date: datetime = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        end_date: datetime = datetime.now()
        intervals: list = []
        step: timedelta = timedelta(days=day_step)

        current_start = start_date
        while current_start <= end_date:
            current_end = current_start + timedelta(
                days=day_step - 1, hours=23, minutes=59, seconds=59
            )
            if current_end > end_date:
                current_end = end_date

            intervals.append(
                (
                    current_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    current_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
            )

            current_start += step
        return intervals

    def get_response(self, url: str, params: dict = None) -> dict | None:
        try:
            response: Response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data: dict = response.json()
            if not data:
                logger.warning("No data found for box_id {}", self.box_id)
                raise NoDataFoundError(url, params)
            return data

        except requests.exceptions.RequestException as e:
            logger.error("API request failed: {}", e)
            return None
        except (json.JSONDecodeError, KeyError, TypeError) as e:  # Added TypeError
            logger.error("Failed to parse or process API response: {}", e)
            return None

    def get_box_information(self) -> dict | None:
        data: dict = self.get_response(self.base_url)
        rename_map: dict = {"_id": "box_id", "loc": "location"}
        box_infos: dict = {
            rename_map.get(k, k): v
            for k, v in data.items()
            if k not in ["sensors", "updatedAt", "lastMeasurementAt"]
        }

        return box_infos

    def get_sensors_information_for_box(self) -> pd.DataFrame:
        data: dict = self.get_response(self.base_url)["sensors"]
        sensor_info_data: list[dict] = [
            {k: v for k, v in entry.items() if k != "lastMeasurement"} for entry in data
        ]

        sensor_infos: pd.DataFrame = pd.DataFrame(sensor_info_data).rename(
            columns={"_id": "sensor_id", "sensorType": "sensor_type"}
        )

        return sensor_infos

    def fetch_new_sensor_data_for_one_box(self) -> pd.DataFrame | None:
        data: dict = self.get_response(self.base_url)["sensors"]
        df: pd.DataFrame = pd.json_normalize(data)

        if "lastMeasurement.createdAt" not in df.columns:
            logger.warning(
                "Field 'lastMeasurement.createdAt' not found for all sensors in box_id {}.",
                self.box_id,
            )
            return None  # Can't proceed without timestamps

        # Filter out rows where timestamp or value might be missing *before* processing
        df = df.dropna(subset=["lastMeasurement.createdAt", "lastMeasurement.value"])
        if df.empty:
            logger.warning(
                "No valid sensor readings with timestamp and value found for {}.",
                self.box_id,
            )
            return None

        df_filtered = df.copy()
        df_filtered["timestamp"] = pd.to_datetime(
            df_filtered["lastMeasurement.createdAt"]
        )
        # Measurement conversion handled later during DB write preparation if needed

        required_cols = {
            "timestamp": "timestamp",
            "_id": "sensor_id",
            "lastMeasurement.value": "measurement",
            "unit": "unit",
            "sensorType": "sensor_type",
            "icon": "icon",
            "title": "title",
        }
        cols_to_select = {
            k: v for k, v in required_cols.items() if k in df_filtered.columns
        }
        df_final = df_filtered[list(cols_to_select.keys())].rename(
            columns=cols_to_select
        )

        # Attempt numeric conversion, keep track of failures
        original_len = len(df_final)
        df_final["measurement"] = pd.to_numeric(
            df_final["measurement"], errors="coerce"
        )
        df_final = df_final.dropna(
            subset=["measurement"]
        )  # Remove rows where conversion failed
        if len(df_final) < original_len:
            logger.warning(
                "Removed {} rows due to non-numeric 'measurement' values.",
                original_len - len(df_final),
            )

        df_final["box_id"] = self.box_id
        logger.info(
            "Successfully fetched and processed {} sensor readings.", len(df_final)
        )
        return df_final

    def fetch_historical_data_for_one_sensor(
        self, sensor_id: str, from_date: str, to_date: str
    ) -> pd.DataFrame | None:
        url: str = f"{self.base_url}/data/{sensor_id}"
        params: dict = {"from-date": from_date, "to-date": to_date}

        data: dict = self.get_response(url, params)
        df: pd.DataFrame = pd.json_normalize(data)

        if "createdAt" not in df.columns:
            logger.warning(
                "Field 'createdAt' not found for sensor {} in box_id {}.",
                sensor_id,
                self.box_id,
            )
            return None

        # Filter out rows where timestamp or value might be missing *before* processing
        df = df.dropna(subset=["createdAt", "value"])
        if df.empty:
            logger.warning(
                "No valid sensor data for sensor {} of box_id {} from {} to {}.",
                sensor_id,
                self.box_id,
                from_date,
                to_date,
            )
            return None

        df_filtered = df.copy()
        df_filtered["timestamp"] = pd.to_datetime(df_filtered["createdAt"])

        required_cols = {"timestamp": "timestamp", "value": "measurement"}
        cols_to_select = {
            k: v for k, v in required_cols.items() if k in df_filtered.columns
        }
        df_final = df_filtered[list(cols_to_select.keys())].rename(
            columns=cols_to_select
        )

        df_final = df_final.assign(box_id=self.box_id, sensor_id=sensor_id)

        return df_final

    def fetch_all_historical_data_for_one_box(self, output_dir_path: Path):
        sensors_info: pd.DataFrame = self.get_sensors_information_for_box()
        box_creation_date: str = (
            pd.to_datetime(self.get_box_information()["createdAt"])
            .floor(freq="D")
            .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        sensors: set = set(sensors_info["sensor_id"])
        time_intervals: list = self.create_time_intervals(box_creation_date)

        os.makedirs(output_dir_path, exist_ok=True)

        logger.debug("Start fetching all historical data for box {}", self.box_id)
        start = timer()
        for sensor in sensors:
            logger.debug("Start fetching historical data for sensor {}", sensor)
            sensor_dfs: list = []
            for i, (start_date, end_date) in enumerate(time_intervals):
                if i % 10 == 0:
                    logger.debug(
                        "{}th of {} iterations for sensor {}",
                        i,
                        len(time_intervals),
                        sensor,
                    )
                try:
                    sensor_data: pd.DataFrame = (
                        self.fetch_historical_data_for_one_sensor(
                            sensor, start_date, end_date
                        )
                    )
                    sensor_dfs.append(sensor_data)
                except NoDataFoundError as e:
                    logger.warning(e)

            if sensor_dfs:
                df: pd.DataFrame = pd.concat(sensor_dfs, ignore_index=True)
                sensor_info: pd.DataFrame = sensors_info[
                    sensors_info["sensor_id"] == sensor
                ]
                df = df.merge(sensor_info, on="sensor_id")

                df["sensor_partition"] = sensor

                df.to_parquet(
                    output_dir_path,
                    engine="pyarrow",
                    compression="snappy",
                    index=False,
                    partition_cols=["sensor_partition"],
                )

                del df, sensor_dfs
                gc.collect()

        end = timer()
        logger.debug(
            "Fetched all historical data for box {}. Took {}s. Saved data at {}",
            self.box_id,
            end - start,
            output_dir_path,
        )


class SenseBoxApi:
    def __init__(self, box_id: str) -> None:
        self.box_id = box_id
        self.base_url = f"https://api.opensensemap.org/boxes/{self.box_id}"

        self.data_loader = SenseBoxDataLoader(self.base_url, self.box_id)

    # Fetch new data from a sense box
    def fetch_new_sensor_data_for_one_box(self) -> pd.DataFrame:
        return self.data_loader.fetch_new_sensor_data_for_one_box()

    def fetch_historical_data_for_one_sensor(
        self, sensor_id: str, from_date: str, to_date: str
    ) -> pd.DataFrame:
        return self.data_loader.fetch_historical_data_for_one_sensor(
            sensor_id, from_date, to_date
        )

    def fetch_all_historical_data_for_one_box(self, output_dir_path: Path) -> None:
        return self.data_loader.fetch_all_historical_data_for_one_box(output_dir_path)

    # Get informations about the sense box
    def get_box_information(self) -> dict:
        return self.data_loader.get_box_information()

    def get_sensors_information_for_box(self) -> pd.DataFrame:
        return self.data_loader.get_sensors_information_for_box()


if __name__ == "__main__":
    sense_box_api = SenseBoxApi("5d6d5269953683001ae46adc")
    # sdf = sense_box_api.fetch_historical_data_for_one_sensor(
    #     "5d6d5269953683001ae46ae1",
    #     from_date="2022-03-30T00:00:00Z",
    #     to_date="2022-04-03T23:59:59Z",
    # )
    # print(sdf.head())
    # print(len(sdf))

    # dff = sense_box_api.fetch_new_sensor_data_for_one_box()

    # binfo = sense_box_api.get_box_information()
    # df = sense_box_api.get_sensors_information_for_box()
    # dff = df.merge(sdf, on="sensor_id")
    # print(dff.head())
    # print(df)
    # print(binfo)

    # hdf = sense_box_api.fetch_all_historical_data_for_one_box(
    #     "2025-04-01T00:00:00Z", "2025-04-10T00:00:00Z"
    # )
    # print(hdf.head())
    # print(len(hdf))

    # intr = sense_box_api.data_loader.create_time_intervals("2025-01-01T00:00:00.000Z")
    # print(intr)

    # sense_box_api.fetch_all_historical_data_for_one_box()
