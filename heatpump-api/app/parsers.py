import re

from .models import DomesticHotWater, HeatingCircuit, HeatPumpUnit


def extract_param(html: str, param_id: str) -> str:
    """Return the stripped display text for a parameter by its numeric ID prefix.

    Values are embedded in the view page HTML as:
      <a class="infolink" href="vinfo.rsp?...&id=<id>:<path>">VALUE</a>
    """
    pattern = rf"id={re.escape(param_id)}:[^\"]+\">([^<]+)<"
    match = re.search(pattern, html)
    if not match:
        raise ValueError(f"Parameter {param_id!r} not found in HTML")
    return match.group(1).strip()


def parse_float(text: str) -> float:
    """Extract the first number from a value string such as ' 23 °C' or '22.6 °C'."""
    match = re.search(r"[-+]?\d+\.?\d*", text)
    if not match:
        raise ValueError(f"No numeric value in {text!r}")
    return float(match.group())


def parse_bool(text: str) -> bool:
    """Return True if the last whitespace-separated token is 'on'.

    HPM value strings are 'LABEL   value' or just 'value'; checking the last
    token handles both formats.
    """
    tokens = text.strip().split()
    return bool(tokens) and tokens[-1].lower() == "on"


def parse_last_token(text: str) -> str:
    """Return the last whitespace-separated token (strips any label prefix)."""
    tokens = text.strip().split()
    return tokens[-1] if tokens else ""


def parse_hp1(html: str) -> HeatPumpUnit:
    """Parse heat pump 1 status from v21.rsp HTML."""
    return HeatPumpUnit(
        on=parse_bool(extract_param(html, "114")),
        heating=parse_bool(extract_param(html, "115")),
        outlet_temp=parse_float(extract_param(html, "111")),
        return_temp=parse_float(extract_param(html, "112")),
        frequency=int(parse_float(extract_param(html, "126"))),
        error_code=parse_last_token(extract_param(html, "125")),
    )


def parse_hc1(html: str) -> HeatingCircuit:
    """Parse heating circuit 1 status from v30.rsp HTML."""
    return HeatingCircuit(
        flow_setpoint=parse_float(extract_param(html, "12")),
        flow_temp=parse_float(extract_param(html, "13")),
        room_setpoint=parse_float(extract_param(html, "18")),
        pump_on=parse_bool(extract_param(html, "15")),
    )


def parse_dhw(html: str) -> DomesticHotWater:
    """Parse domestic hot water status from v107000.rsp HTML."""
    return DomesticHotWater(
        setpoint=parse_float(extract_param(html, "37")),
        actual_temp=parse_float(extract_param(html, "38")),
    )


_HC_SETPOINT_FIELDS = ("roomOT1", "roomOT2", "roomOT3", "roomOT4", "roomNO", "roomSNOT")


def _mainpane(html: str) -> str:
    m = re.search(r'<!--\s*start_mainpane\s*-->(.*?)<!--\s*end_mainpane\s*-->', html, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else html


def parse_hc_setpoints(html: str) -> dict[str, float]:
    pane = _mainpane(html)
    result: dict[str, float] = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", pane, re.DOTALL | re.IGNORECASE):
        text = re.sub(r"<[^>]+>", " ", tr)
        text = re.sub(r"\s+", " ", text).strip()
        for name in _HC_SETPOINT_FIELDS:
            if name in text:
                after = text.split(name, 1)[1]
                m = re.search(r"[-+]?\d+\.?\d*", after)
                if m:
                    result[name] = float(m.group())
                break
    return result


def parse_operating_mode(html: str) -> str:
    """Return the current operating mode label from the MS0 selector in v0.rsp HTML.

    Note: v0.rsp does not contain outdoor temperature; that is sourced from v30.rsp
    via extract_param(hc1_html, "9") in the caller.
    """
    ms0_block = re.search(r'name="MS0".*?</select>', html, re.DOTALL)
    if not ms0_block:
        raise ValueError("MS0 operating mode selector not found in HTML")
    match = re.search(r"<option[^>]+selected[^>]*>([^<]+)</option>", ms0_block.group())
    if not match:
        raise ValueError("No selected option found in MS0 selector")
    return match.group(1).strip()
