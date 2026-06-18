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
    room_setpoint: float  # nominal (roomNO)
    room_ot1: float | None = None
    room_ot2: float | None = None
    pump_on: bool


class HeatingCircuit2(BaseModel):
    """HC2 status (pool heating) from v3.rsp.

    flow_temp (27) and outdoor_temp (23, delOutT) are confirmed against the
    device. The remaining fields are parsed best-effort and resolve to None if
    the param is not present, so a missing/incorrect ID can never break the
    confirmed fields. room_setpoint is the nominal setpoint (roomNO = 32, per
    device verification)."""

    flow_temp: float
    outdoor_temp: float
    flow_setpoint: float | None = None
    room_setpoint: float | None = None
    room_ot1: float | None = None
    room_ot2: float | None = None
    pump_on: bool | None = None


class DomesticHotWater(BaseModel):
    setpoint: float
    actual_temp: float


class SystemStatus(BaseModel):
    operating_mode: str
    outdoor_temp: float
    heat_pump: HeatPumpUnit
    heating_circuit_1: HeatingCircuit
    heating_circuit_2: HeatingCircuit2 | None = None
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
