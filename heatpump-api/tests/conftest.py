import os
from pathlib import Path

# app.config reads its settings at import time; tests never reach a device.
os.environ.setdefault("HEATPUMP_URL", "http://hpm.invalid")
os.environ.setdefault("HEATPUMP_USERNAME", "test")
os.environ.setdefault("HEATPUMP_PASSWORD", "test")

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def page():
    """Load a captured HPM view page (e.g. page("v30")), decoded as the device serves it."""
    def load(name: str) -> str:
        return (FIXTURES / f"{name}.html").read_text(encoding="latin-1")
    return load
