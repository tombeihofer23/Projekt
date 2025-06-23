"""Entity-Klasse für die Sensor-Metadaten."""

from typing import Any

from sqlalchemy.orm import Mapped, mapped_column

from src.ffm_dashboard.db import Base


class SensorMetadata(Base):
    """Entity-Klasse für Sensordaten."""

    __tablename__: Any = "sensor_metadata"

    sensor_id: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    """ID des Sensors."""

    unit: Mapped[str]
    """Einheit des Messwerts."""

    sensor_type: Mapped[str]
    """Sensortyp."""

    icon: Mapped[str]
    """Icon der Messung."""

    title: Mapped[str]
    """Titel der Messung."""
