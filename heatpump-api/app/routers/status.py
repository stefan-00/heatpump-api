from fastapi import APIRouter

from ..client import client
from ..models import HeatpumpState

router = APIRouter(prefix="/api/v1")


@router.get("/status", response_model=HeatpumpState)
async def get_status() -> HeatpumpState:
    return await client.get_status()
