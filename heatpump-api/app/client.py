import asyncio
import logging
import re
from typing import NamedTuple

import httpx
from fastapi import HTTPException

from .config import settings
from .models import FlowLimit, HcSetpoints, SystemStatus
from .parsers import PAGE_FLOW_LIMIT, PAGE_SETPOINTS, extract_param, page_matches, parse_dhw, parse_float, parse_flow_limit, parse_hc1, parse_hc2, parse_hc_setpoints, parse_hp1, parse_operating_mode, parse_page_title
from .session import SessionExpiredError, SessionManager, session_manager

logger = logging.getLogger(__name__)

# WEB-RC navigation label sequences from root to the setpoints page for each circuit.
# Label-based so the path is resilient to branchnr numbering differences across firmwares.
_HC1_SETPOINTS_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 1", "setpoints"]
_HC2_SETPOINTS_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 2", "setpoints"]

_CIRCUIT_LABELS = {"hc1": _HC1_SETPOINTS_LABELS, "hc2": _HC2_SETPOINTS_LABELS}

# HC2 flow-temperature limitation ("setpoint limitation" function, params
# 2.5.2.3.6.x). The page sits one level below the setpoints page (under
# "function"), so its params are addressed at level 5 (vs 4 for setpoints).
_HC2_FLOWLIMIT_LABELS = ["MCR-BMS", "heatCirc.", "heatC. 2", "function", "setpoint limitation"]
_FLOWLIMIT_LEVEL = "5"
_FLOWLIMIT_POSITION = {"active": 1, "minFl": 2, "maxFl": 3}
# Device default upper cap; max_flow must be strictly greater than min_flow.
_FLOWLIMIT_MAX_CAP = 65.0

# A write whose requested value already equals the stored value cannot be
# verified: the read-back afterwards passes whether the write landed on the
# intended parameter, a different one, or nowhere. Such writes are skipped, which
# is what makes read-back confirmation meaningful for the writes that remain.
# Matches the routers' read-back tolerance.
_ALREADY_SET_TOLERANCE = 0.05


class NavResult(NamedTuple):
    """A verified WEB-RC page plus the coordinates that select it.

    The coordinates let a caller re-confirm the position immediately before
    writing, without walking the whole path again.
    """

    response: httpx.Response
    branchnr: str
    level: str


_SETPOINT_POSITION = {
    "roomOT1": 1,
    "roomOT2": 2,
    "roomOT3": 3,
    "roomOT4": 4,
    "roomNO": 5,
    "roomSNOT": 6,
}


class HeatpumpClient:
    def __init__(self, session: SessionManager) -> None:
        self._session = session
        # Single lock for EVERY request to the device, not just WEB-RC ones. The
        # HPM keeps one stateful navigation position per session, and `execset`
        # addresses parameters relative to it — so any request that reaches the
        # device between a verified navigation and its dependent writes makes
        # those writes land on the wrong parameter. This previously excluded the
        # v*.rsp status fetches, on the assumption that view pages do not touch
        # navigation state; on 2026-08-13 a status poll interleaved between
        # info.rsp and execset and HC2 roomOT2 took the minFl value. What matters
        # is that a request shares the session, not what kind of request it is.
        self._device_lock: asyncio.Lock = asyncio.Lock()

    async def get_status(self) -> SystemStatus:
        base = settings.heatpump_url.rstrip("/")
        # Hold the device lock for the whole set of fetches. The five view pages
        # stay concurrent with each other — they perform no navigation — but they
        # must not slip between another operation's navigation and its writes.
        try:
            async with self._device_lock:
                hp1_resp, hc1_resp, hc2_resp, dhw_resp, sys_resp = await asyncio.gather(
                    self._session.request("GET", f"{base}/v21.rsp"),
                    self._session.request("GET", f"{base}/v30.rsp"),
                    self._session.request("GET", f"{base}/v3.rsp"),
                    self._session.request("GET", f"{base}/v107000.rsp"),
                    self._session.request("GET", f"{base}/v0.rsp"),
                )
        except httpx.RequestError as e:
            logger.warning("Heatpump unreachable during status fetch: %r", e)
            raise HTTPException(status_code=502, detail=f"Heatpump unreachable: {e!r}") from e

        hp1_html, hc1_html, hc2_html, dhw_html, sys_html = (
            r.content.decode("latin-1")
            for r in (hp1_resp, hc1_resp, hc2_resp, dhw_resp, sys_resp)
        )

        try:
            status = SystemStatus(
                operating_mode=parse_operating_mode(sys_html),
                outdoor_temp=parse_float(extract_param(hc1_html, "9")),
                heat_pump=parse_hp1(hp1_html),
                heating_circuit_1=parse_hc1(hc1_html),
                domestic_hot_water=parse_dhw(dhw_html),
            )
        except ValueError as e:
            logger.error(
                "Failed to parse heatpump status — %.300s",
                str(e),
            )
            raise HTTPException(
                status_code=502,
                detail=f"Unexpected response structure from heatpump: {e}",
            ) from e

        # HC2 (pool heating) is best-effort: a parse failure here must not break
        # the core status response, since HC2 param IDs are less certain.
        try:
            status.heating_circuit_2 = parse_hc2(hc2_html)
        except ValueError as e:
            logger.warning("Failed to parse HC2 status (v3.rsp) — %.200s", str(e))

        return status


    async def _webrc_operation(self, description: str, op):
        """Run a navigate-and-act operation under the device lock.

        Retries the operation exactly once if the session expired part-way
        through, so a routine expiry stays invisible to the caller while every
        write is still preceded by a freshly verified navigation. A verification
        failure is never retried — it would repeat the same deterministic
        mismatch — and neither is a validation error.
        """
        async with self._device_lock:
            for attempt in (1, 2):
                try:
                    return await op()
                except SessionExpiredError as e:
                    if attempt == 2:
                        logger.warning(
                            "Session expired twice during %s; giving up", description
                        )
                        raise HTTPException(
                            status_code=502,
                            detail=f"Session expired during {description}; retry failed",
                        ) from e
                    logger.info(
                        "Session expired during %s (%s); restarting from navigation",
                        description, e,
                    )
                except httpx.RequestError as e:
                    logger.warning("Heatpump unreachable during %s: %r", description, e)
                    raise HTTPException(
                        status_code=502, detail=f"Heatpump unreachable: {e!r}"
                    ) from e

    def _check_generation(self, gen: int, what: str) -> None:
        """Abort if the session was re-authenticated since navigation completed.

        A re-login repositions the device at the WEB-RC root, which makes the
        navigation-relative (branchnr, level) address of a pending write point at
        a different parameter. Raising SessionExpiredError here makes
        `_webrc_operation` re-navigate and try again rather than write blind.
        """
        if self._session.generation != gen:
            raise SessionExpiredError(
                f"Session re-authenticated after navigation; refusing to write {what} "
                f"against a stale navigation context"
            )

    @staticmethod
    def _parse_limits(html: str) -> tuple[float | None, float | None]:
        """Extract the device's (lower, upper) limit pair from an info.rsp page."""
        lo_match = re.search(r"Lower limit:.*?(-?\d+\.\d+)\s*°", html, re.DOTALL | re.I)
        hi_match = re.search(r"Upper limit:.*?(-?\d+\.\d+)\s*°", html, re.DOTALL | re.I)
        lo = float(lo_match.group(1)) if lo_match else None
        hi = float(hi_match.group(1)) if hi_match else None
        return lo, hi

    async def _reconfirm_page(
        self, base: str, nav: "NavResult", circuit: str, page: str
    ) -> None:
        """Re-check, immediately before writing, that we are still on the target page.

        Verifying only at the end of navigation cannot protect against anything
        that disturbs the session afterwards — which is exactly how the
        2026-08-13 leak happened, with a status poll landing between the range
        reads and the writes. Re-selecting the page at its own coordinates
        returns the same page if the position is intact, and something else if it
        moved.
        """
        resp = await self._session.request(
            "GET", f"{base}/menue.rsp",
            params={"branchnr": nav.branchnr, "level": nav.level},
            retry_on_expiry=False,
        )
        title = parse_page_title(resp.content.decode("latin-1"))
        if not page_matches(title, circuit, page):
            logger.warning(
                "WEB-RC position moved between navigation and write: wanted circuit=%s "
                "page=%s at (bn=%s, lv=%s), observed title %r. Refusing to write.",
                circuit, page, nav.branchnr, nav.level, title,
            )
            raise HTTPException(
                status_code=502,
                detail=(
                    f"WEB-RC position changed before write: expected {circuit} "
                    f"{page!r} page, found {title!r}"
                ),
            )

    async def _webrc_navigate(
        self, base: str, labels: list[str], circuit: str, page: str
    ) -> "NavResult":
        """Walk from the WEB-RC root to a target page and verify where we landed.

        Label matching alone cannot detect drift into the wrong circuit: HC1 and
        HC2 expose identical child labels ('setpoints', 'function', 'setpoint
        limitation'), so a mid-walk re-login can land the remainder of the walk
        in the wrong subtree and still match every label. The landed page's own
        title row is checked before the caller is allowed to use it.
        """
        final_params = {"branchnr": "1", "level": "0"}
        resp = await self._session.request(
            "GET", f"{base}/menue.rsp", params=final_params,
            retry_on_expiry=False,
        )
        for label in labels:
            html = resp.content.decode("latin-1")
            links = re.findall(
                r'href=["\']menue\.rsp\?([^"\']+)["\'][^>]*>\s*([^<]+)',
                html, re.IGNORECASE
            )
            matched_params = None
            for qs_str, link_text in links:
                if link_text.strip() == label:
                    qs = dict(p.split("=", 1) for p in qs_str.split("&") if "=" in p)
                    if "branchnr" in qs and "level" in qs:
                        matched_params = {"branchnr": qs["branchnr"], "level": qs["level"]}
                        break
            if matched_params is None:
                available = [t.strip() for _, t in links]
                raise HTTPException(
                    status_code=502,
                    detail=f"WEB-RC menu item {label!r} not found; available: {available}",
                )
            resp = await self._session.request(
                "GET", f"{base}/menue.rsp", params=matched_params,
                retry_on_expiry=False,
            )
            final_params = matched_params

        title = parse_page_title(resp.content.decode("latin-1"))
        if not page_matches(title, circuit, page):
            logger.warning(
                "WEB-RC navigation landed on an unexpected page: wanted circuit=%s "
                "page=%s, observed title %r (labels=%s). Refusing to use this page.",
                circuit, page, title, labels,
            )
            raise HTTPException(
                status_code=502,
                detail=(
                    f"WEB-RC navigation verification failed: expected {circuit} "
                    f"{page!r} page, landed on {title!r}"
                ),
            )
        return NavResult(
            response=resp,
            branchnr=final_params["branchnr"],
            level=final_params["level"],
        )

    async def get_hc_setpoints(self, circuit_id: str) -> HcSetpoints:
        base = settings.heatpump_url.rstrip("/")
        labels = _CIRCUIT_LABELS[circuit_id]

        async def op() -> HcSetpoints:
            nav = await self._webrc_navigate(base, labels, circuit_id, PAGE_SETPOINTS)
            values = parse_hc_setpoints(nav.response.content.decode("latin-1"))
            if not values:
                raise HTTPException(
                    status_code=502,
                    detail="Could not parse setpoints from heatpump response",
                )
            return HcSetpoints(**values)

        return await self._webrc_operation(f"{circuit_id} setpoint read", op)

    async def set_hc_setpoint(self, circuit_id: str, field: str, value: float) -> None:
        base = settings.heatpump_url.rstrip("/")
        labels = _CIRCUIT_LABELS[circuit_id]
        position = _SETPOINT_POSITION[field]

        async def op() -> None:
            nav = await self._webrc_navigate(base, labels, circuit_id, PAGE_SETPOINTS)
            gen = self._session.generation

            # Skip a write that would not change anything: it cannot be verified,
            # since the read-back would pass wherever the write actually landed.
            current = parse_hc_setpoints(nav.response.content.decode("latin-1"))
            if field in current and abs(current[field] - value) <= _ALREADY_SET_TOLERANCE:
                logger.info(
                    "%s %s already %.1f — skipping write (a no-op write cannot be verified)",
                    circuit_id, field, value,
                )
                return

            # Validate against device limits before writing. This is only
            # meaningful because navigation above verified the page — info.rsp is
            # addressed the same navigation-relative way as the write itself.
            info_resp = await self._session.request(
                "GET", f"{base}/info.rsp",
                params={"branchnr": str(position), "level": "4"},
                retry_on_expiry=False,
            )
            lo, hi = self._parse_limits(info_resp.content.decode("latin-1"))
            if lo is not None and hi is not None and not lo <= value <= hi:
                raise HTTPException(
                    status_code=422,
                    detail=f"Value {value} out of device range [{lo}, {hi}] for {field!r}",
                )

            self._check_generation(gen, f"{circuit_id} {field}")
            await self._reconfirm_page(base, nav, circuit_id, PAGE_SETPOINTS)
            await self._session.request(
                "POST",
                f"{base}/execset.rsp",
                data={
                    "val": f"{value:.1f}",
                    "Set": "OK",
                    "sessionid": self._session._session_id,
                    "branchnr": str(position),
                    "level": "4",
                    "id": str(position),
                },
                retry_on_expiry=False,
            )

        await self._webrc_operation(f"{circuit_id} {field} write", op)


    async def get_flow_limit(self) -> FlowLimit:
        base = settings.heatpump_url.rstrip("/")

        async def op() -> FlowLimit:
            nav = await self._webrc_navigate(
                base, _HC2_FLOWLIMIT_LABELS, "hc2", PAGE_FLOW_LIMIT
            )
            values = parse_flow_limit(nav.response.content.decode("latin-1"))
            if not all(k in values for k in ("active", "minFl", "maxFl")):
                raise HTTPException(
                    status_code=502,
                    detail="Could not parse flow limit from heatpump response",
                )
            return FlowLimit(
                active=bool(values["active"]),
                min_flow=values["minFl"],
                max_flow=values["maxFl"],
            )

        return await self._webrc_operation("HC2 flow-limit read", op)

    async def set_flow_limit(
        self, flow_setpoint: float | None = None, active: bool | None = None
    ) -> dict[str, float]:
        """Write the HC2 flow limitation and return the values actually written.

        When flow_setpoint is given, writes minFl = flow_setpoint and ensures
        maxFl > minFl (the device rejects maxFl <= minFl; maxFl is kept if
        already above the floor, otherwise raised to the default cap). The
        limitation is enabled/disabled per `active`; when `active` is None it
        defaults to enabled iff a floor was written, so a lone flow_setpoint
        both sets the floor and enables. At least one argument must be set.

        The returned dict maps each written parameter to its requested value so
        the caller can confirm it took effect — the device returns 302 for both
        accepted and rejected writes.
        """
        if flow_setpoint is None and active is None:
            raise HTTPException(status_code=422, detail="Nothing to set: provide flow_setpoint and/or active")

        base = settings.heatpump_url.rstrip("/")

        async def op() -> dict[str, float]:
            nav = await self._webrc_navigate(
                base, _HC2_FLOWLIMIT_LABELS, "hc2", PAGE_FLOW_LIMIT
            )
            gen = self._session.generation
            current = parse_flow_limit(nav.response.content.decode("latin-1"))
            # Never write using assumed current values: an unparseable page means
            # we cannot reason about the maxFl > minFl constraint at all.
            if not all(k in current for k in ("active", "minFl", "maxFl")):
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Could not parse the current HC2 flow limitation "
                        f"(got {sorted(current)}); refusing to write"
                    ),
                )

            desired_active = (
                active if active is not None else (flow_setpoint is not None)
            )
            active_matches = bool(current["active"]) == desired_active

            # Fast path for the overwhelmingly common case: the caller re-asserts
            # a floor the device already holds. Such a write cannot be verified —
            # the read-back passes wherever it landed — so issue nothing at all.
            # This also removes almost all device traffic, since the pool
            # controller re-asserts an unchanged floor continuously.
            if active_matches and (
                flow_setpoint is None
                or (
                    abs(current["minFl"] - flow_setpoint) <= _ALREADY_SET_TOLERANCE
                    and current["maxFl"] > flow_setpoint
                )
            ):
                logger.info(
                    "HC2 flow limit already minFl=%.1f maxFl=%.1f active=%d — "
                    "skipping all writes (a no-op write cannot be verified)",
                    current["minFl"], current["maxFl"], int(current["active"]),
                )
                return {
                    "minFl": current["minFl"],
                    "maxFl": current["maxFl"],
                    "active": float(int(desired_active)),
                }

            written: dict[str, float] = {}
            reconfirmed = False

            if flow_setpoint is not None:
                lo, hi = await self._flowlimit_range(base, "minFl")
                lo = 2.0 if lo is None else lo
                hi = 160.0 if hi is None else hi
                if not lo <= flow_setpoint <= hi:
                    raise HTTPException(
                        status_code=422,
                        detail=f"flow_setpoint {flow_setpoint} out of device range [{lo}, {hi}]",
                    )

                # Pick a max_flow strictly greater than the floor (device constraint).
                cur_max = current["maxFl"]
                target_max = cur_max if cur_max > flow_setpoint else _FLOWLIMIT_MAX_CAP
                if target_max <= flow_setpoint:
                    target_max = min(hi, flow_setpoint + 5.0)
                if not flow_setpoint < target_max <= hi:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"Cannot satisfy max_flow > min_flow within device range "
                            f"[{lo}, {hi}] for flow_setpoint {flow_setpoint}"
                        ),
                    )

                # maxFl gets its own range check — it is a separate device param
                # with its own limits, and is written just like the floor.
                max_lo, max_hi = await self._flowlimit_range(base, "maxFl")
                if (
                    max_lo is not None and max_hi is not None
                    and not max_lo <= target_max <= max_hi
                ):
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"Derived max_flow {target_max} out of device range "
                            f"[{max_lo}, {max_hi}]"
                        ),
                    )

                # Order matters: raise maxFl first (so minFl never transiently
                # exceeds maxFl), then set the floor. The generation is re-checked
                # before each write — a re-login between them would silently
                # retarget the remaining writes — and the page identity is
                # re-confirmed once, immediately before the first write, in case
                # anything moved the navigation position since it was verified.
                if abs(current["maxFl"] - target_max) > _ALREADY_SET_TOLERANCE:
                    self._check_generation(gen, "HC2 maxFl")
                    if not reconfirmed:
                        await self._reconfirm_page(base, nav, "hc2", PAGE_FLOW_LIMIT)
                        reconfirmed = True
                    await self._execset_flowlimit(base, "maxFl", f"{target_max:.1f}")
                else:
                    logger.info("HC2 maxFl already %.1f — skipping write", target_max)
                written["maxFl"] = target_max

                if abs(current["minFl"] - flow_setpoint) > _ALREADY_SET_TOLERANCE:
                    self._check_generation(gen, "HC2 minFl")
                    if not reconfirmed:
                        await self._reconfirm_page(base, nav, "hc2", PAGE_FLOW_LIMIT)
                        reconfirmed = True
                    await self._execset_flowlimit(base, "minFl", f"{flow_setpoint:.1f}")
                else:
                    logger.info("HC2 minFl already %.1f — skipping write", flow_setpoint)
                written["minFl"] = flow_setpoint

            # `active` is a 0/1 flag, not a temperature, so info.rsp publishes no
            # °C range for it; validate by construction instead.
            active_val = "1" if desired_active else "0"
            if active_matches:
                logger.info("HC2 active already %s — skipping write", active_val)
            else:
                self._check_generation(gen, "HC2 active")
                if not reconfirmed:
                    await self._reconfirm_page(base, nav, "hc2", PAGE_FLOW_LIMIT)
                    reconfirmed = True
                await self._execset_flowlimit(base, "active", active_val)
            written["active"] = float(active_val)

            return written

        return await self._webrc_operation("HC2 flow-limit write", op)

    async def _flowlimit_range(
        self, base: str, field: str
    ) -> tuple[float | None, float | None]:
        """Read the device's accepted range for one limitation parameter."""
        info_resp = await self._session.request(
            "GET", f"{base}/info.rsp",
            params={
                "branchnr": str(_FLOWLIMIT_POSITION[field]),
                "level": _FLOWLIMIT_LEVEL,
            },
            retry_on_expiry=False,
        )
        return self._parse_limits(info_resp.content.decode("latin-1"))

    async def _execset_flowlimit(self, base: str, field: str, val: str) -> None:
        position = _FLOWLIMIT_POSITION[field]
        await self._session.request(
            "POST",
            f"{base}/execset.rsp",
            data={
                "val": val,
                "Set": "OK",
                "sessionid": self._session._session_id,
                "branchnr": str(position),
                "level": _FLOWLIMIT_LEVEL,
                "id": str(position),
            },
            retry_on_expiry=False,
        )


client = HeatpumpClient(session_manager)
