from fastapi import APIRouter

from ..client import client
from ..models import SystemStatus

router = APIRouter(prefix="/api/v1")


@router.get("/status", response_model=SystemStatus)
async def get_status() -> SystemStatus:
    return await client.get_status()
