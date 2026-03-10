"""Integration tests for player state machine + player states.

Tests that PlayerIdle, PlayerDead, and the StateMachine wire together
correctly.  A lightweight mock owner replaces the full Player to avoid
spinning up the camera, mouse lock, and game_manager registration.
"""
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, call
from ursina import Vec3

from scripts.components.state import State
from scripts.components.state_machine import StateMachine
from scenes.player.states.player_idle import PlayerIdle
from scenes.player.states.player_dead import PlayerDead
from scenes.player.camera_controller import CameraMode
from scripts.autoload.event_bus import event_bus, PLAYER_DIED


# ---------------------------------------------------------------------------
# Mock player owner
# ---------------------------------------------------------------------------

def _make_mock_player() -> SimpleNamespace:
    """Minimal owner that satisfies PlayerIdle and PlayerDead attr access."""
    p = SimpleNamespace()
    p.is_sprinting = False
    p.is_aiming = False
    p.is_dodging = False
    p.is_invincible = False
    p.current_speed = 0.0
    p.grounded = True
    p.last_grounded_time = 0.0
    p.jump_buffer_timer = 0.0
    p.velocity = Vec3(0, 0, 0)
    p.camera_controller = MagicMock()
    # Methods called by states
    p.decelerate_horizontal = MagicMock()
    p.get_camera_relative_input = MagicMock(return_value=Vec3(0, 0, 0))
    return p


def _build_sm(*states: State, owner=None, start: str = None) -> StateMachine:
    if owner is None:
        owner = _make_mock_player()
    sm = StateMachine(owner=owner)
    for s in states:
        sm.add_state(s)
    if start:
        sm.start(start)
    return sm


# ---------------------------------------------------------------------------
# PlayerIdle tests
# ---------------------------------------------------------------------------

def test_idle_enter_resets_sprinting_and_speed():
    owner = _make_mock_player()
    owner.is_sprinting = True
    owner.current_speed = 9.9
    sm = _build_sm(PlayerIdle(), owner=owner, start="Idle")
    assert owner.is_sprinting is False
    assert owner.current_speed == 0.0


def test_idle_starts_as_current_state():
    sm = _build_sm(PlayerIdle(), start="Idle")
    assert sm.get_current_state_name() == "Idle"


def test_idle_handle_input_space_transitions_to_jump():
    jump = State("Jump")
    sm = _build_sm(PlayerIdle(), jump, start="Idle")
    sm.handle_input("space", True)
    assert sm.get_current_state_name() == "Jump"


def test_idle_handle_input_ctrl_transitions_to_dodge():
    dodge = State("Dodge")
    sm = _build_sm(PlayerIdle(), dodge, start="Idle")
    sm.handle_input("left control", True)
    assert sm.get_current_state_name() == "Dodge"


def test_idle_handle_input_right_mouse_transitions_to_aim():
    aim = State("Aim")
    sm = _build_sm(PlayerIdle(), aim, start="Idle")
    sm.handle_input("right mouse", True)
    assert sm.get_current_state_name() == "Aim"


def test_idle_process_calls_decelerate():
    owner = _make_mock_player()
    sm = _build_sm(PlayerIdle(), owner=owner, start="Idle")
    sm.update(0.016)
    owner.decelerate_horizontal.assert_called_once_with(0.016)


# ---------------------------------------------------------------------------
# PlayerDead tests
# ---------------------------------------------------------------------------

def test_dead_enter_zeroes_velocity():
    owner = _make_mock_player()
    owner.velocity = Vec3(5, 3, 2)
    idle = PlayerIdle()
    dead = PlayerDead()
    sm = _build_sm(idle, dead, owner=owner, start="Idle")
    sm.transition_to("Dead")
    assert owner.velocity == Vec3(0, 0, 0)


def test_dead_enter_sets_death_camera_mode():
    owner = _make_mock_player()
    idle = PlayerIdle()
    dead = PlayerDead()
    sm = _build_sm(idle, dead, owner=owner, start="Idle")
    sm.transition_to("Dead")
    owner.camera_controller.set_mode.assert_called_once_with(CameraMode.DEATH)


def test_dead_state_name():
    dead = PlayerDead()
    assert dead.name == "Dead"


# ---------------------------------------------------------------------------
# State machine transitions across states
# ---------------------------------------------------------------------------

def test_transition_idle_to_dead_and_back_is_impossible():
    """Dead state has no transitions out — current state stays Dead."""
    idle = PlayerIdle()
    dead = PlayerDead()
    sm = _build_sm(idle, dead, start="Idle")
    sm.transition_to("Dead")
    sm.update(1.0)  # Dead.process_state is a no-op
    assert sm.get_current_state_name() == "Dead"


def test_on_state_changed_callback_fires_for_idle_to_dead():
    changes = []
    idle = PlayerIdle()
    dead = PlayerDead()
    sm = _build_sm(idle, dead, start="Idle")
    sm._on_state_changed = lambda old, new: changes.append((old, new))
    sm.transition_to("Dead")
    assert changes == [("Idle", "Dead")]
