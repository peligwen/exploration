"""Unit tests for HealthComponent (scripts/components/health_component.py)."""
import pytest
from scripts.components.health_component import HealthComponent
from scripts.resources.damage_info import DamageInfo
from scripts.autoload.event_bus import event_bus, DAMAGE_DEALT, ENTITY_DIED


def _dmg(amount: float) -> DamageInfo:
    return DamageInfo.create(amount)


# ---------------------------------------------------------------------------
# Damage / HP
# ---------------------------------------------------------------------------

def test_initial_hp_equals_max():
    hc = HealthComponent(max_hp=80.0)
    assert hc.current_hp == 80.0


def test_take_damage_reduces_hp():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(30.0))
    assert hc.current_hp == 70.0


def test_hp_does_not_go_below_zero():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(999.0))
    assert hc.current_hp == 0.0


def test_lethal_damage_sets_dead():
    hc = HealthComponent(max_hp=50.0)
    hc.take_damage(_dmg(50.0))
    assert hc.is_dead is True


def test_non_lethal_damage_does_not_set_dead():
    hc = HealthComponent(max_hp=50.0)
    hc.take_damage(_dmg(49.0))
    assert hc.is_dead is False


def test_damage_while_dead_is_ignored():
    hc = HealthComponent(max_hp=50.0)
    hc.take_damage(_dmg(50.0))  # kill
    hc.take_damage(_dmg(10.0))  # should be ignored
    assert hc.current_hp == 0.0


# ---------------------------------------------------------------------------
# i-frames
# ---------------------------------------------------------------------------

def test_iframe_blocks_second_hit():
    hc = HealthComponent(max_hp=100.0, iframe_duration=1.0)
    hc.take_damage(_dmg(10.0))
    hc.take_damage(_dmg(10.0))  # within i-frame window
    assert hc.current_hp == 90.0


def test_iframe_timer_decrements_on_update():
    hc = HealthComponent(max_hp=100.0, iframe_duration=1.0)
    hc.take_damage(_dmg(10.0))
    hc.update(0.5)
    assert hc._iframe_timer == pytest.approx(0.5)


def test_iframe_expires_after_update():
    hc = HealthComponent(max_hp=100.0, iframe_duration=0.1)
    hc.take_damage(_dmg(10.0))
    hc.update(0.2)
    hc.take_damage(_dmg(10.0))  # i-frame expired
    assert hc.current_hp == 80.0


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

def test_on_health_changed_fires_on_damage():
    calls = []
    hc = HealthComponent(max_hp=100.0)
    hc.on_health_changed = lambda cur, mx: calls.append((cur, mx))
    hc.take_damage(_dmg(40.0))
    assert calls == [(60.0, 100.0)]


def test_on_died_fires_on_lethal_damage():
    calls = []
    hc = HealthComponent(max_hp=100.0)
    hc.on_died = lambda: calls.append(True)
    hc.take_damage(_dmg(100.0))
    assert calls == [True]


def test_on_damage_taken_receives_damage_info():
    received = []
    hc = HealthComponent(max_hp=100.0)
    hc.on_damage_taken = lambda info: received.append(info)
    dmg = _dmg(25.0)
    hc.take_damage(dmg)
    assert received == [dmg]


# ---------------------------------------------------------------------------
# EventBus integration
# ---------------------------------------------------------------------------

def test_damage_dealt_event_emitted():
    events = []
    event_bus.connect(DAMAGE_DEALT, lambda info: events.append(info))
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(10.0))
    assert len(events) == 1


def test_entity_died_event_emitted_on_death():
    deaths = []
    event_bus.connect(ENTITY_DIED, lambda owner, src: deaths.append(owner))
    owner = object()
    hc = HealthComponent(max_hp=10.0)
    hc.owner = owner
    hc.take_damage(_dmg(10.0))
    assert deaths == [owner]


def test_entity_died_not_emitted_for_non_lethal():
    deaths = []
    event_bus.connect(ENTITY_DIED, lambda owner, src: deaths.append(owner))
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(1.0))
    assert deaths == []


# ---------------------------------------------------------------------------
# Heal
# ---------------------------------------------------------------------------

def test_heal_increases_hp():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(50.0))
    hc.heal(20.0)
    assert hc.current_hp == 70.0


def test_heal_clamps_to_max():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(10.0))
    hc.heal(999.0)
    assert hc.current_hp == 100.0


def test_heal_when_dead_is_ignored():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(100.0))
    hc.heal(50.0)
    assert hc.current_hp == 0.0


def test_on_health_changed_fires_on_heal():
    calls = []
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(50.0))
    hc.on_health_changed = lambda cur, mx: calls.append(cur)
    hc.heal(10.0)
    assert calls == [60.0]


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

def test_reset_restores_full_hp():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(70.0))
    hc.reset()
    assert hc.current_hp == 100.0


def test_reset_clears_dead_flag():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(100.0))
    hc.reset()
    assert hc.is_dead is False


# ---------------------------------------------------------------------------
# get_hp_percent
# ---------------------------------------------------------------------------

def test_get_hp_percent_full():
    hc = HealthComponent(max_hp=100.0)
    assert hc.get_hp_percent() == pytest.approx(1.0)


def test_get_hp_percent_half():
    hc = HealthComponent(max_hp=100.0)
    hc.take_damage(_dmg(50.0))
    assert hc.get_hp_percent() == pytest.approx(0.5)


def test_get_hp_percent_zero_max_returns_zero():
    hc = HealthComponent(max_hp=0.0)
    assert hc.get_hp_percent() == 0.0


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------

def test_save_data_roundtrip():
    hc = HealthComponent(max_hp=80.0)
    hc.take_damage(_dmg(30.0))
    data = hc.get_save_data()

    hc2 = HealthComponent(max_hp=80.0)
    hc2.load_save_data(data)

    assert hc2.current_hp == pytest.approx(50.0)
    assert hc2.max_hp == pytest.approx(80.0)
    assert hc2.is_dead is False


def test_save_data_preserves_dead_flag():
    hc = HealthComponent(max_hp=50.0)
    hc.take_damage(_dmg(50.0))
    data = hc.get_save_data()

    hc2 = HealthComponent(max_hp=50.0)
    hc2.load_save_data(data)

    assert hc2.is_dead is True
