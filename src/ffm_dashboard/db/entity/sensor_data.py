"""Entity-Klasse für die Sensordaten."""

from datetime import datetime
from typing import Any, Literal, Self

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from src.ffm_dashboard.db import Base


class SensorData(Base):
    """Entity-Klasse für Sensordaten."""

    __tablename__: Any = "sensor_data"

    timestamp: Mapped[datetime] = mapped_column(nullable=False, primary_key=True)
    """Der Timestamp (bei TimescaleDB der PK)."""

    box_id: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    """ID der Sensebox."""

    sensor_id: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    """ID des Sensors."""

    measurement: Mapped[float]
    """Messwert."""

    unit: Mapped[str]
    """Einheit des Messwerts."""

    sensor_type: Mapped[str]
    """Sensortyp."""

    icon: Mapped[str]
    """Icon der Messung."""

    title: Mapped[str]
    """Titel der Messung."""

    __table_args__: Any = (
        UniqueConstraint("timestamp", "box_id", "sensor_id", name="unique"),
    )

    @classmethod
    def from_dict(
        cls,
        sensor_data_dict: dict[
            Literal[
                "timestamp",
                "box_id",
                "sensor_id",
                "measurement",
                "unit",
                "sensor_tpye",
                "icon",
                "title",
            ],
            Any,
        ],
    ) -> Self:
        """Sensordatenpunkt aus DataFrame erstellen."""

        return cls(
            timestamp=sensor_data_dict["timestamp"],
            box_id=sensor_data_dict["box_id"],
            sensor_id=sensor_data_dict["sensor_id"],
            measurement=sensor_data_dict["measurement"],
            unit=sensor_data_dict["unit"],
            sensor_type=sensor_data_dict["sensor_type"],
            icon=sensor_data_dict["icon"],
            title=sensor_data_dict["title"],
        )

    def __repr__(self) -> str:
        """Ausgabe eines Sensordatenpunkts als String."""

        return (
            f"Sensordatenpunkt(ts={self.timestamp}, box_id={self.box_id}, "
            f"sensor_id={self.sensor_id}, measurement={self.measurement}, "
            f"unit={self.unit}, sensor_type={self.sensor_type}, icon={self.icon}, "
            f"title={self.title})"
        )
