"""Base class for all weapons. Extend for specific weapon types."""
from ursina import Entity, Vec3, raycast, time, color
import random as rand
import math

from scripts.autoload.event_bus import event_bus, PLAYER_AMMO_CHANGED
from scripts.resources.damage_info import DamageInfo, DamageType
from scripts.resources.collision_layers import (
    LAYER_PLAYER, PLAYER_WEAPON_HITTABLE)


class WeaponBase(Entity):
    """Base weapon with raycast-based firing."""

    def __init__(self, owner_entity=None, **kwargs):
        super().__init__(
            model='cube',
            color=color.dark_gray,
            scale=(0.08, 0.1, 0.6),
            **kwargs
        )
        self.weapon_owner = owner_entity  # The player holding this weapon
        self.collision_group = LAYER_PLAYER

        # Weapon stats
        self.weapon_name = "Weapon"
        self.damage = 10.0
        self.fire_rate = 0.15  # Seconds between shots
        self.max_ammo = 30
        self.reload_time = 1.5
        self.spread = 0.0  # Degrees of spread
        self.range_distance = 100.0

        # Runtime
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        self._fire_cooldown = 0.0
        self._reload_timer = 0.0

        # Callbacks
        self.on_fired = None
        self.on_reloaded = None

    def update(self):
        dt = time.dt
        if self._fire_cooldown > 0:
            self._fire_cooldown -= dt

        if self.is_reloading:
            self._reload_timer -= dt
            if self._reload_timer <= 0:
                self._finish_reload()

    def fire(self):
        if self.is_reloading or self._fire_cooldown > 0:
            return
        if self.current_ammo <= 0:
            self.start_reload()
            return

        self.current_ammo -= 1
        self._fire_cooldown = self.fire_rate

        # Raycast from camera forward
        from ursina import camera
        origin = camera.world_position
        direction = camera.forward

        # Apply spread via independent yaw/pitch offsets
        if self.spread > 0:
            spread_rad = math.radians(self.spread)
            yaw_offset = rand.uniform(-spread_rad, spread_rad)
            pitch_offset = rand.uniform(-spread_rad, spread_rad)
            # Rotate direction by yaw offset around world Y axis
            cos_y = math.cos(yaw_offset)
            sin_y = math.sin(yaw_offset)
            dx = direction.x * cos_y + direction.z * sin_y
            dz = -direction.x * sin_y + direction.z * cos_y
            direction = Vec3(dx, direction.y, dz)
            # Rotate direction by pitch offset around the right axis
            right = Vec3(direction.z, 0, -direction.x).normalized()
            cos_p = math.cos(pitch_offset)
            sin_p = math.sin(pitch_offset)
            direction = (
                direction * cos_p + right * sin_p
            ).normalized()

        # Build ignore list: skip entities tagged with
        # a non-hittable collision_group. Untagged entities
        # (arena geometry) remain hittable by default.
        from ursina import scene
        ignore_list = [
            e for e in scene.entities
            if getattr(e, 'collision_group', None) is not None
            and e.collision_group not in PLAYER_WEAPON_HITTABLE
        ]
        # Always exclude self and owner even if untagged
        if self not in ignore_list:
            ignore_list.append(self)
        if self.weapon_owner and self.weapon_owner not in ignore_list:
            ignore_list.append(self.weapon_owner)

        hit = raycast(origin, direction, distance=self.range_distance,
                      ignore=ignore_list)
        if hit.hit:
            self._on_hit(hit.entity, hit.world_point, hit.world_normal)

        if self.on_fired:
            self.on_fired()
        event_bus.emit(PLAYER_AMMO_CHANGED, self.current_ammo, self.max_ammo)

    def start_reload(self):
        if self.is_reloading or self.current_ammo == self.max_ammo:
            return
        self.is_reloading = True
        self._reload_timer = self.reload_time

    def _finish_reload(self):
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        if self.on_reloaded:
            self.on_reloaded()
        event_bus.emit(
            PLAYER_AMMO_CHANGED,
            self.current_ammo, self.max_ammo)

    def _on_hit(self, entity, point, normal):
        # Damageable entities expose .health by convention.
        # normal can be None; fallback Vec3 = zero knockback.
        if entity and hasattr(entity, 'health'):
            normal_vec = normal if normal else Vec3(0, 0, 0)
            info = DamageInfo.create(
                self.damage,
                self.weapon_owner,
                DamageType.PHYSICAL,
                point,
                -normal_vec * 2.0
            )
            entity.health.take_damage(info)

    def _init_ammo(self):
        """Call after setting stats to initialize ammo count."""
        self.current_ammo = self.max_ammo
