import json
import os
from pathlib import Path

from pydantic import BaseModel, ValidationError

_OPTIONS_PATH = Path("/data/options.json")


class Settings(BaseModel):
    heatpump_url: str
    username: str
    password: str  # sent to HPM as the 'code' form field (HPM "access code", max 8 chars)
    port: int = 8765


def _load() -> Settings:
    if _OPTIONS_PATH.exists():
        raw = json.loads(_OPTIONS_PATH.read_text())
        return Settings(**raw)
    try:
        return Settings(
            heatpump_url=os.environ["HEATPUMP_URL"],
            username=os.environ["HEATPUMP_USERNAME"],
            password=os.environ["HEATPUMP_PASSWORD"],
            port=int(os.environ.get("PORT", "8765")),
        )
    except KeyError as e:
        raise RuntimeError(
            f"Missing required configuration: {e}. "
            "Set via /data/options.json (HA add-on) or env vars "
            "HEATPUMP_URL, HEATPUMP_USERNAME, HEATPUMP_PASSWORD."
        ) from e


settings = _load()
