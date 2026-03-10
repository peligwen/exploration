"""Structured damage data passed through the EventBus."""
from ursina import Vec3
from enum import Enum


class DamageType(Enum):
    PHYSICAL = 0
    FIRE = 1
    EXPLOSIVE = 2
    FALL = 3


class DamageInfo:
    """Structured damage data resource."""

    def __init__(self):
        self.amount: float = 0.0
        self.damage_type: DamageType = DamageType.PHYSICAL
        self.hit_position: Vec3 = Vec3(0, 0, 0)
        self.knockback_force: Vec3 = Vec3(0, 0, 0)
        self.is_critical: bool = False
        self.source = None  # The entity that dealt damage

    @staticmethod
    def create(amount: float, source=None,
               damage_type=DamageType.PHYSICAL,
               hit_pos=None, knockback=None,
               crit: bool = False) -> 'DamageInfo':
        info = DamageInfo()
        info.amount = amount
        info.source = source
        info.damage_type = damage_type
        info.hit_position = hit_pos or Vec3(0, 0, 0)
        info.knockback_force = knockback or Vec3(0, 0, 0)
        info.is_critical = crit
        return info
