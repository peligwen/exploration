"""Standard rifle. Medium damage, moderate fire rate, low spread."""
from scenes.weapons.weapon_base import WeaponBase


class Rifle(WeaponBase):
    def __init__(self, owner_entity=None, **kwargs):
        super().__init__(owner_entity=owner_entity, **kwargs)
        self.weapon_name = "Rifle"
        self.damage = 15.0
        self.fire_rate = 0.12
        self.max_ammo = 30
        self.reload_time = 1.8
        self.spread = 0.5
        self.range_distance = 150.0
        self._init_ammo()
