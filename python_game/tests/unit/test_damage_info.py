"""Unit tests for DamageInfo (scripts/resources/damage_info.py)."""
import pytest
from ursina import Vec3
from scripts.resources.damage_info import DamageInfo, DamageType


def test_create_sets_amount():
    info = DamageInfo.create(25.0)
    assert info.amount == 25.0


def test_create_default_damage_type_is_physical():
    info = DamageInfo.create(10.0)
    assert info.damage_type == DamageType.PHYSICAL


def test_create_default_hit_position_is_origin():
    info = DamageInfo.create(10.0)
    assert info.hit_position == Vec3(0, 0, 0)


def test_create_default_knockback_is_zero():
    info = DamageInfo.create(10.0)
    assert info.knockback_force == Vec3(0, 0, 0)


def test_create_default_not_critical():
    info = DamageInfo.create(10.0)
    assert info.is_critical is False


def test_create_default_source_is_none():
    info = DamageInfo.create(10.0)
    assert info.source is None


def test_create_with_all_fields():
    source = object()
    hit = Vec3(1, 2, 3)
    knock = Vec3(0, 1, 0)
    info = DamageInfo.create(50.0, source, DamageType.FIRE, hit, knock, crit=True)
    assert info.amount == 50.0
    assert info.source is source
    assert info.damage_type == DamageType.FIRE
    assert info.hit_position == hit
    assert info.knockback_force == knock
    assert info.is_critical is True


@pytest.mark.parametrize("dtype", list(DamageType))
def test_all_damage_types_accepted(dtype):
    info = DamageInfo.create(1.0, damage_type=dtype)
    assert info.damage_type == dtype


def test_default_constructor_zeroed():
    info = DamageInfo()
    assert info.amount == 0.0
    assert info.is_critical is False
    assert info.source is None
