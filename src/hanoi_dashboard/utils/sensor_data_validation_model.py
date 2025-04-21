"""Pydantic-Model für die Sensor-Daten."""

from pydantic import BaseModel, ValidationError
from pydantic.types import PastDatetime


class SensorDataModel(BaseModel):
    """Pydantic-Model für die Sensor-Daten."""

    timestamp: PastDatetime
    box_id: str
    sensor_id: str
    measurement: float

    unit: str | None = None
    sensor_type: str | None = None
    icon: str | None = None
    title: str | None = None


if __name__ == "__main__":
    from src.hanoi_dashboard.components import SenseBoxApi

    sense_box_api = SenseBoxApi("6252afcfd7e732001bb6b9f7")
    sdf = sense_box_api.fetch_new_sensor_data()[:10]
    sdf.at[1, "measurement"] = None

    for _, row in sdf.iterrows():
        try:
            SensorDataModel.model_validate_json(row.to_json())
            print(row.to_json())
        except ValidationError as e:
            print(e)
        else:
            print("test")
