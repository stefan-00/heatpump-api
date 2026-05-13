from typing import Any
from pydantic import BaseModel


class HeatpumpState(BaseModel):
    power: bool
    mode: str
    current_temp: float | None = None
    target_temp: float
    fan_speed: str


class ControlCommand(BaseModel):
    value: Any


class ErrorResponse(BaseModel):
    detail: str
