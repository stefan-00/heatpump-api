from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

from ..client import client

router = APIRouter(prefix="/api/v1/control")


class PowerCommand(BaseModel):
    value: bool


class ModeCommand(BaseModel):
    value: Literal["heat", "cool", "auto", "dry", "fan"]


class TemperatureCommand(BaseModel):
    value: float

    @field_validator("value")
    @classmethod
    def validate_range(cls, v: float) -> float:
        # TODO: confirm min/max from web UI after reverse-engineering
        if not (16.0 <= v <= 30.0):
            raise ValueError("Temperature must be between 16 and 30°C")
        return v


class FanSpeedCommand(BaseModel):
    value: Literal["auto", "1", "2", "3", "4", "5"]


@router.post("/power")
async def set_power(cmd: PowerCommand) -> dict:
    return await client.send_command("power", cmd.value)


@router.post("/mode")
async def set_mode(cmd: ModeCommand) -> dict:
    return await client.send_command("mode", cmd.value)


@router.post("/temperature")
async def set_temperature(cmd: TemperatureCommand) -> dict:
    return await client.send_command("temperature", cmd.value)


@router.post("/fan-speed")
async def set_fan_speed(cmd: FanSpeedCommand) -> dict:
    return await client.send_command("fan-speed", cmd.value)
