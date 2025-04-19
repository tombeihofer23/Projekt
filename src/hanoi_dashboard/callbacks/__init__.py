"""Modul für Dash Callbacks."""

from src.hanoi_dashboard.callbacks.app_callbacks import register_app_callbacks
from src.hanoi_dashboard.callbacks.sensors_callbacks import register_sensors_callbacks

__all__: list[str] = ["register_sensors_callbacks", "register_app_callbacks"]
