"""Shared pytest configuration and fixtures.

Initialises a headless Ursina application once per session so that Entity
subclasses can be instantiated in both unit and integration tests without
opening a window.  This import must run before any test module is loaded.
"""
import sys
import os

# Ensure python_game/ is on sys.path so game modules resolve correctly.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Headless Ursina — initialise once at collection time, before test modules
# are imported, so that `from ursina import Entity` works everywhere.
# ---------------------------------------------------------------------------
from ursina import Ursina, window as _ursina_window  # noqa: E402

_app = Ursina(development_mode=False)
_ursina_window.visible = False

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
import pytest  # noqa: E402
from scripts.autoload.event_bus import event_bus  # noqa: E402


@pytest.fixture(autouse=True)
def reset_event_bus():
    """Clear all EventBus listeners after every test to prevent cross-test leakage."""
    yield
    event_bus._listeners.clear()
