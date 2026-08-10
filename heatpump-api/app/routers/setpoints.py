import logging

from fastapi import APIRouter, HTTPException

from ..client import client
from ..models import FlowLimit, FlowLimitPatch, HcSetpoints, HcSetpointsPatch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/circuits/{circuit_id}")

_VALID_CIRCUITS = {"hc1", "hc2"}


def _validate_circuit(circuit_id: str) -> None:
    if circuit_id not in _VALID_CIRCUITS:
        raise HTTPException(status_code=404, detail=f"Unknown circuit: {circuit_id!r}")


@router.get("/setpoints", response_model=HcSetpoints)
async def get_setpoints(circuit_id: str) -> HcSetpoints:
    _validate_circuit(circuit_id)
    return await client.get_hc_setpoints(circuit_id)


# The device returns a 302 redirect for both accepted and rejected writes, so a
# write is only known to have taken effect once it is read back.
_CONFIRM_TOLERANCE = 0.05


@router.patch("/setpoints", response_model=HcSetpoints)
async def patch_setpoints(circuit_id: str, body: HcSetpointsPatch) -> HcSetpoints:
    _validate_circuit(circuit_id)
    updates = body.model_dump(exclude_none=True)
    logger.info("PATCH %s/setpoints %s", circuit_id, updates)
    for field, value in updates.items():
        await client.set_hc_setpoint(circuit_id, field, value)

    result = await client.get_hc_setpoints(circuit_id)
    mismatched = {
        field: {"requested": value, "actual": getattr(result, field, None)}
        for field, value in updates.items()
        if getattr(result, field, None) is None
        or abs(getattr(result, field) - value) > _CONFIRM_TOLERANCE
    }
    if mismatched:
        logger.error(
            "Setpoint write not confirmed for %s: %s", circuit_id, mismatched
        )
        raise HTTPException(
            status_code=502,
            detail=f"Setpoint write not confirmed by device: {mismatched}",
        )
    return result


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
    logger.info(
        "PATCH %s/flow-limit %s", circuit_id, body.model_dump(exclude_none=True)
    )
    written = await client.set_flow_limit(
        flow_setpoint=body.flow_setpoint, active=body.active
    )

    result = await client.get_flow_limit()
    actual = {
        "minFl": result.min_flow,
        "maxFl": result.max_flow,
        "active": float(result.active),
    }
    mismatched = {
        field: {"requested": value, "actual": actual[field]}
        for field, value in written.items()
        if abs(actual[field] - value) > _CONFIRM_TOLERANCE
    }
    if mismatched:
        logger.error("Flow-limit write not confirmed: %s", mismatched)
        raise HTTPException(
            status_code=502,
            detail=f"Flow-limit write not confirmed by device: {mismatched}",
        )
    return result
