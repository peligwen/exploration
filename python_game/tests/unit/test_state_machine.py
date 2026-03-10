"""Unit tests for StateMachine + State (scripts/components/).

Uses lightweight test doubles — no Ursina Entity required.
"""
import pytest
from scripts.components.state import State
from scripts.components.state_machine import StateMachine


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------

class RecordingState(State):
    """State that records every lifecycle call in a shared log."""

    def __init__(self, name: str, log: list):
        super().__init__(name)
        self._log = log

    def enter(self, previous_state: str, msg: dict = None):
        self._log.append(f"{self.name}.enter({previous_state!r})")

    def exit(self):
        self._log.append(f"{self.name}.exit")

    def process_state(self, delta: float):
        self._log.append(f"{self.name}.process({delta})")

    def handle_input(self, key, is_press: bool):
        self._log.append(f"{self.name}.input({key!r}, {is_press})")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sm():
    return StateMachine(owner=None)


@pytest.fixture
def two_state_sm():
    log = []
    machine = StateMachine(owner=None)
    machine.add_state(RecordingState("A", log))
    machine.add_state(RecordingState("B", log))
    machine.start("A")
    return machine, log


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_add_state_registers_by_name(sm):
    state = RecordingState("Idle", [])
    sm.add_state(state)
    assert "Idle" in sm.states


def test_add_state_injects_machine_reference(sm):
    state = RecordingState("Idle", [])
    sm.add_state(state)
    assert state.state_machine is sm


def test_start_calls_enter_on_initial_state():
    log = []
    sm = StateMachine()
    sm.add_state(RecordingState("Idle", log))
    sm.start("Idle")
    assert "Idle.enter('')" in log


def test_start_sets_current_state(sm):
    sm.add_state(RecordingState("Idle", []))
    sm.start("Idle")
    assert sm.get_current_state_name() == "Idle"


def test_transition_calls_exit_then_enter_in_order(two_state_sm):
    machine, log = two_state_sm
    log.clear()
    machine.transition_to("B")
    assert log == ["A.exit", "B.enter('A')"]


def test_transition_updates_current_state(two_state_sm):
    machine, _ = two_state_sm
    machine.transition_to("B")
    assert machine.get_current_state_name() == "B"


def test_transition_to_same_state_is_noop(two_state_sm):
    machine, log = two_state_sm
    log.clear()
    machine.transition_to("A")
    assert log == []


def test_transition_to_unknown_state_does_not_crash(sm):
    sm.add_state(RecordingState("Idle", []))
    sm.start("Idle")
    sm.transition_to("DoesNotExist")  # should print a warning, not raise
    assert sm.get_current_state_name() == "Idle"


def test_on_state_changed_callback_fires(two_state_sm):
    machine, _ = two_state_sm
    changes = []
    machine._on_state_changed = lambda old, new: changes.append((old, new))
    machine.transition_to("B")
    assert changes == [("A", "B")]


def test_update_routes_to_current_state(two_state_sm):
    machine, log = two_state_sm
    log.clear()
    machine.update(0.016)
    assert "A.process(0.016)" in log


def test_handle_input_routes_to_current_state(two_state_sm):
    machine, log = two_state_sm
    log.clear()
    machine.handle_input("space", True)
    assert "A.input('space', True)" in log


def test_state_transition_to_delegates_to_machine(two_state_sm):
    machine, _ = two_state_sm
    # State.transition_to() should use the injected state_machine
    state_a = machine.states["A"]
    state_a.transition_to("B")
    assert machine.get_current_state_name() == "B"


def test_get_current_state_name_before_start():
    sm = StateMachine()
    assert sm.get_current_state_name() == ""
