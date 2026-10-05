"""get_status against a stubbed session that serves captured view pages."""
import asyncio

import httpx
import pytest
from fastapi import HTTPException

from app.client import HeatpumpClient
from tests.conftest import FIXTURES


class FixtureSession:
    """Serves tests/fixtures/<page>.html for GET <base>/<page>.rsp."""

    def __init__(self, overrides=None, fail=None):
        self._overrides = overrides or {}
        self._fail = fail
        self.requested = []

    async def request(self, method, url, **kwargs):
        name = url.rsplit("/", 1)[-1].removesuffix(".rsp")
        self.requested.append((method, name))
        if name == self._fail:
            raise httpx.ConnectError("connection refused")
        body = self._overrides.get(name)
        if body is None:
            body = (FIXTURES / f"{name}.html").read_text(encoding="latin-1")
        return httpx.Response(200, content=body.encode("latin-1"))


def _status(session):
    return asyncio.run(HeatpumpClient(session).get_status())


def test_status_includes_new_values():
    status = _status(FixtureSession()).model_dump()
    assert status["heat_pump"]["hc_setpoint"] == 42.0
    assert status["heat_pump"]["operating_state"] == "normal"
    assert status["heat_pump"]["heat_demand"] == "dem. HC2"
    assert status["heat_pump"]["defrost"] is False
    assert status["buffer"] == {"temp": 35.7, "setpoint": 42.0}
    assert status["heating_circuit_1"]["valve_position"] == 0.0
    assert status["heating_circuit_2"]["valve_position"] == 100.0


def test_unparseable_buffer_page_gives_null_buffer():
    status = _status(FixtureSession(overrides={"v100100": "<html>unexpected</html>"}))
    assert status.buffer is None
    assert status.heat_pump.outlet_temp == 37.0


def test_unreachable_buffer_page_is_502():
    with pytest.raises(HTTPException) as exc:
        _status(FixtureSession(fail="v100100"))
    assert exc.value.status_code == 502


def test_status_includes_period_without_extra_device_traffic():
    session = FixtureSession()
    status = _status(session).model_dump()
    hc1, hc2 = status["heating_circuit_1"], status["heating_circuit_2"]
    assert (hc1["period"], hc1["active_room_setpoint"]) == ("OT2", 18.0)
    assert hc1["operating_status"] == "nom. oper. OT2"
    assert (hc2["period"], hc2["active_room_setpoint"]) == ("OT1", 27.0)
    assert hc2["timer_status"] == "timer-OT1 ------B---"
    # The same six view pages as before, and no WEB-RC navigation or writes.
    assert sorted(session.requested) == sorted(
        ("GET", page) for page in ("v21", "v30", "v3", "v107000", "v0", "v100100")
    )
