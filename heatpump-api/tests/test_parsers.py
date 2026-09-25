"""Parser tests against view pages captured from the live HPM on 2026-09-25.

Captured state: compressor at 41 Hz on HC2 (pool) demand, the HPM asking the
heat pump for 42 °C while the outlet reads 37 °C; HC1 valve closed and HC2 valve
fully open. setp.DHW reads the 2 °C no-demand placeholder.

Regenerate with research/probe_view_pages.py --save; the expected values below
then need updating to match.
"""
import re

import pytest

from app.parsers import (
    extract_param,
    parse_buffer,
    parse_dhw,
    parse_hc1,
    parse_hc2,
    parse_hp1,
    parse_text,
)


def _replace_value(html: str, param_id: str, value: str) -> str:
    """Replace one parameter's display text, leaving the rest of the page intact."""
    return re.sub(
        rf'(id={re.escape(param_id)}:[^"]+">)[^<]+(<)', rf"\g<1>{value}\g<2>", html, count=1
    )


def _drop_param(html: str, param_id: str) -> str:
    """Remove one parameter's anchor entirely, as a firmware change might."""
    return re.sub(rf'<a[^>]*id={re.escape(param_id)}:[^"]+"[^>]*>[^<]*</a>', "", html)


# --- 2.1 helpers ----------------------------------------------------------

def test_parse_text_keeps_multi_word_values():
    assert parse_text("  no   demand ") == "no demand"
    assert parse_text("Blocked / off") == "Blocked / off"


def test_param_16_does_not_match_169(page):
    html = page("v30")
    assert extract_param(html, "16") == "0 %"
    assert "roomOT2" in extract_param(html, "169")


def test_malformed_new_value_becomes_none(page):
    html = _replace_value(page("v21"), "109", "setpointHC   --- °C")
    assert parse_hp1(html).hc_setpoint is None


def test_malformed_defrost_becomes_none(page):
    html = _replace_value(page("v21"), "124", "Stat-Defrost   ???")
    assert parse_hp1(html).defrost is None


# --- 2.2 heat-source demand -----------------------------------------------

def test_hp1_heat_source_values(page):
    hp = parse_hp1(page("v21"))
    assert hp.hc_setpoint == 42.0
    assert hp.operating_state == "normal"
    assert hp.heat_demand == "dem. HC2"
    assert hp.defrost is False


# --- 2.3 mixing valves ----------------------------------------------------

def test_valve_positions(page):
    assert parse_hc1(page("v30")).valve_position == 0.0
    assert parse_hc2(page("v3")).valve_position == 100.0


# --- 2.4 buffer -----------------------------------------------------------

def test_buffer_values(page):
    buffer = parse_buffer(page("v100100"))
    assert buffer.temp == 35.7  # shown without a unit
    assert buffer.setpoint == 42.0  # 'SP-zone1 42.0 °C': last number, not the '1'


def test_buffer_with_one_param_missing(page):
    buffer = parse_buffer(_drop_param(page("v100100"), "61"))
    assert buffer.temp is None
    assert buffer.setpoint == 42.0


def test_buffer_with_no_params_raises(page):
    html = _drop_param(_drop_param(page("v100100"), "61"), "59")
    with pytest.raises(ValueError):
        parse_buffer(html)


# --- 2.5 existing fields unchanged ----------------------------------------

def test_existing_fields_still_populated(page):
    hp = parse_hp1(page("v21"))
    assert (hp.on, hp.heating) == (True, True)
    assert (hp.outlet_temp, hp.return_temp) == (37.0, 32.0)
    assert (hp.frequency, hp.error_code) == (41, "---")

    hc1 = parse_hc1(page("v30"))
    assert (hc1.flow_setpoint, hc1.flow_temp, hc1.room_setpoint) == (20.5, 20.2, 20.0)
    assert (hc1.room_ot1, hc1.room_ot2, hc1.pump_on) == (18.0, 18.0, True)

    hc2 = parse_hc2(page("v3"))
    assert (hc2.flow_temp, hc2.outdoor_temp, hc2.flow_setpoint) == (23.2, 12.0, 42.0)
    assert (hc2.room_setpoint, hc2.room_ot1, hc2.room_ot2, hc2.pump_on) == (10.0, 27.0, 27.0, True)


def test_missing_new_values_leave_core_fields_intact(page):
    html = page("v21")
    for param_id in ("109", "88", "89", "124"):
        html = _drop_param(html, param_id)
    hp = parse_hp1(html)
    assert (hp.hc_setpoint, hp.operating_state, hp.heat_demand, hp.defrost) == (None,) * 4
    assert hp.outlet_temp == 37.0

    hc1 = parse_hc1(_drop_param(page("v30"), "16"))
    assert hc1.valve_position is None
    assert hc1.flow_temp == 20.2
