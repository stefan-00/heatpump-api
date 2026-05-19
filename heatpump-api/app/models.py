from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class HeatPumpUnit(BaseModel):
    on: bool
    heating: bool
    outlet_temp: float
    return_temp: float
    frequency: int
    error_code: str


class HeatingCircuit(BaseModel):
    flow_setpoint: float
    flow_temp: float
    room_setpoint: float
    pump_on: bool


class DomesticHotWater(BaseModel):
    setpoint: float
    actual_temp: float


class SystemStatus(BaseModel):
    operating_mode: str
    outdoor_temp: float
    heat_pump: HeatPumpUnit
    heating_circuit_1: HeatingCircuit
    domestic_hot_water: DomesticHotWater


class ErrorResponse(BaseModel):
    detail: str


class HcSetpoints(BaseModel):
    roomOT1: float | None = None
    roomOT2: float | None = None
    roomOT3: float | None = None
    roomOT4: float | None = None
    roomNO: float | None = None
    roomSNOT: float | None = None


class HcSetpointsPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    roomOT1: float | None = None
    roomOT2: float | None = None
    roomOT3: float | None = None
    roomOT4: float | None = None
    roomNO: float | None = None
    roomSNOT: float | None = None
