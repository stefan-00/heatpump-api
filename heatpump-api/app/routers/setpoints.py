from fastapi import APIRouter, HTTPException

from ..client import client
from ..models import HcSetpoints, HcSetpointsPatch

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
