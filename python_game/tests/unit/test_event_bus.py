"""Unit tests for EventBus (scripts/autoload/event_bus.py).

The EventBus is pure Python — no Ursina Entity required.
"""
import pytest
from scripts.autoload.event_bus import _EventBus, DAMAGE_DEALT, ENTITY_DIED


@pytest.fixture
def bus():
    """Fresh EventBus instance isolated from the global singleton."""
    return _EventBus()


def test_connected_callback_fires_on_emit(bus):
    received = []
    bus.connect("signal", lambda: received.append(1))
    bus.emit("signal")
    assert received == [1]


def test_callback_receives_positional_args(bus):
    received = []
    bus.connect("signal", lambda a, b: received.append((a, b)))
    bus.emit("signal", 10, 20)
    assert received == [(10, 20)]


def test_callback_receives_kwargs(bus):
    received = []
    bus.connect("signal", lambda x=0: received.append(x))
    bus.emit("signal", x=42)
    assert received == [42]


def test_multiple_listeners_all_fire(bus):
    log = []
    bus.connect("signal", lambda: log.append("a"))
    bus.connect("signal", lambda: log.append("b"))
    bus.emit("signal")
    assert sorted(log) == ["a", "b"]


def test_disconnect_stops_callback(bus):
    received = []
    cb = lambda: received.append(1)  # noqa: E731
    bus.connect("signal", cb)
    bus.disconnect("signal", cb)
    bus.emit("signal")
    assert received == []


def test_disconnect_unknown_callback_no_crash(bus):
    bus.disconnect("signal", lambda: None)  # should not raise


def test_emit_unknown_signal_no_crash(bus):
    bus.emit("nonexistent_signal")  # should not raise


def test_double_connect_fires_only_once(bus):
    received = []
    cb = lambda: received.append(1)  # noqa: E731
    bus.connect("signal", cb)
    bus.connect("signal", cb)  # duplicate — should be ignored
    bus.emit("signal")
    assert received == [1]


def test_signal_constants_are_strings():
    assert isinstance(DAMAGE_DEALT, str)
    assert isinstance(ENTITY_DIED, str)


# NOTE: There is a known re-entrancy bug (see TODO in event_bus.py): if a
# callback connects or disconnects a listener *during* emission, the list
# mutates mid-iteration and will raise RuntimeError.  This is not tested here
# because the expected behaviour is a crash — fixing the bug is tracked
# separately.
