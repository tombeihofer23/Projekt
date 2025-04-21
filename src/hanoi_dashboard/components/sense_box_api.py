import json

import pandas as pd
import requests
from loguru import logger
from requests import Response


class SenseBoxDataLoader:
    def __init__(self, base_url: str, box_id: str) -> None:
        self.base_url = base_url
        self.box_id = box_id

    def fetch_new_sensor_data(self) -> pd.DataFrame:
        try:
            response: Response = requests.get(self.base_url, timeout=15)
            response.raise_for_status()
            data: dict = response.json()["sensors"]
            if not data:
                logger.warning(
                    "No sensors found in the response for box_id {}", self.box_id
                )
                return None

            df = pd.json_normalize(data)

            if "lastMeasurement.createdAt" not in df.columns:
                logger.warning(
                    "Field 'lastMeasurement.createdAt' not found for all sensors in box_id {}.",
                    self.box_id,
                )
                return None  # Can't proceed without timestamps

            # Filter out rows where timestamp or value might be missing *before* processing
            df = df.dropna(
                subset=["lastMeasurement.createdAt", "lastMeasurement.value"]
            )
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

        except requests.exceptions.RequestException as e:
            logger.error("API request failed: {}", e)
            return None
        except (json.JSONDecodeError, KeyError, TypeError) as e:  # Added TypeError
            logger.error("Failed to parse or process API response: {}", e)
            return None

    def fetch_historical_sensor_data(
        self, sensor_id: str, from_date: str, to_date: str
    ) -> pd.DataFrame:
        try:
            url: str = f"{self.base_url}/data/{sensor_id}"
            response: Response = requests.get(
                url, params={"from-date": from_date, "to-date": to_date}, timeout=15
            )
            response.raise_for_status()
            data: dict = response.json()
            if not data:
                logger.warning(
                    "No sensors found in the response for box_id {}", self.box_id
                )
                return None

            df = pd.json_normalize(data)

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

            required_cols = {"timestamp": "timestamp", "value": "value"}
            cols_to_select = {
                k: v for k, v in required_cols.items() if k in df_filtered.columns
            }
            df_final = df_filtered[list(cols_to_select.keys())].rename(
                columns=cols_to_select
            )

            df_final = df_final.assign(box_id=self.box_id, sensor_id=sensor_id)

            return df_final

        except requests.exceptions.RequestException as e:
            logger.error("API request failed: {}", e)
            return None
        except (json.JSONDecodeError, KeyError, TypeError) as e:  # Added TypeError
            logger.error("Failed to parse or process API response: {}", e)
            return None


class SenseBoxApi:
    def __init__(self, box_id: str) -> None:
        self.box_id = box_id
        self.base_url = f"https://api.opensensemap.org/boxes/{self.box_id}"

        self.data_loader = SenseBoxDataLoader(self.base_url, self.box_id)

    def fetch_new_sensor_data(self) -> pd.DataFrame:
        return self.data_loader.fetch_new_sensor_data()

    def fetch_historical_sensor_data(
        self, sensor_id: str, from_date: str, to_date: str
    ) -> pd.DataFrame:
        return self.data_loader.fetch_historical_sensor_data(
            sensor_id, from_date, to_date
        )


if __name__ == "__main__":
    sense_box_api = SenseBoxApi("6252afcfd7e732001bb6b9f7")
    # sensor_df = sense_box_api.fetch_historical_sensor_data(
    #     "6252afcfd7e732001bb6b9f8",
    #     from_date="2025-03-12T00:00:00Z",
    #     to_date="2025-04-01T00:00:00Z",
    # )
    # print(sensor_df[:10])
    sdf = sense_box_api.fetch_new_sensor_data()
    print(sdf[:10])
