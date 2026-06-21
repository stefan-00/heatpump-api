from fastapi import APIRouter, HTTPException

from ..client import client
from ..models import FlowLimit, FlowLimitPatch, HcSetpoints, HcSetpointsPatch

router = APIRouter(prefix="/api/v1/circuits/{circuit_id}")

_VALID_CIRCUITS = {"hc1", "hc2"}


def _validate_circuit(circuit_id: str) -> None:
    if circuit_id not in _VALID_CIRCUITS:
        raise HTTPException(status_code=404, detail=f"Unknown circuit: {circuit_id!r}")


@router.get("/setpoints", response_model=HcSetpoints)
async def get_setpoints(circuit_id: str) -> HcSetpoints:
    _validate_circuit(circuit_id)
    return await client.get_hc_setpoints(circuit_id)


@router.patch("/setpoints", response_model=HcSetpoints)
async def patch_setpoints(circuit_id: str, body: HcSetpointsPatch) -> HcSetpoints:
    _validate_circuit(circuit_id)
    updates = body.model_dump(exclude_none=True)
    for field, value in updates.items():
        await client.set_hc_setpoint(circuit_id, field, value)
    return await client.get_hc_setpoints(circuit_id)


def _require_hc2(circuit_id: str) -> None:
    _validate_circuit(circuit_id)
    if circuit_id != "hc2":
        raise HTTPException(
            status_code=400,
            detail="flow-limit is only supported for circuit 'hc2'",
        )


@router.get("/flow-limit", response_model=FlowLimit)
async def get_flow_limit(circuit_id: str) -> FlowLimit:
    _require_hc2(circuit_id)
    return await client.get_flow_limit()


@router.patch("/flow-limit", response_model=FlowLimit)
async def patch_flow_limit(circuit_id: str, body: FlowLimitPatch) -> FlowLimit:
    _require_hc2(circuit_id)
    await client.set_flow_limit(body.flow_setpoint)
    return await client.get_flow_limit()
