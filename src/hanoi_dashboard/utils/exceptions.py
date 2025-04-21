from src.hanoi_dashboard.data import SensorData


class SensorDataPointExistsError(Exception):
    """Exception, falls ein Sensor-Datenpunkt bereits existiert."""

    def __init__(self, sensor_data_point: SensorData) -> None:
        super().__init__(f"Existierender Sensor-Datenpunkt: {sensor_data_point}")
        self.sensor_data_point = sensor_data_point
