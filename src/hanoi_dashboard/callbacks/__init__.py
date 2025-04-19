"""Modul für Dash Callbacks."""

from src.hanoi_dashboard.callbacks.app_callbacks import register_app_callbacks
from src.hanoi_dashboard.callbacks.home_callbacks import register_home_callbacks

__all__: list[str] = ["register_home_callbacks", "register_app_callbacks"]
