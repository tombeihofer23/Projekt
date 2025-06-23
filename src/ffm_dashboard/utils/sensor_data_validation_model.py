"""Pydantic-Model für die Sensor-Daten."""

from pydantic import BaseModel
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
