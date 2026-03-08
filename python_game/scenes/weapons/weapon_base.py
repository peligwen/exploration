"""Base class for all weapons. Extend for specific weapon types."""
from ursina import Entity, Vec3, raycast, time, color
import random as rand
import math

from scripts.autoload.event_bus import event_bus, PLAYER_AMMO_CHANGED
from scripts.resources.damage_info import DamageInfo, DamageType


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

        # TODO(migration): Spread calculation is incorrect. GDScript modifies the raycast's
        # rotation angles (pitch and yaw) independently, producing uniform angular spread.
        # This approach adds random offsets to X/Y direction components but not Z, which
        # produces non-uniform spread biased toward the forward axis. Use quaternion rotation
        # or spherical coordinate offsets around the direction vector instead.
        # Apply spread
        if self.spread > 0:
            spread_rad = math.radians(self.spread)
            direction = Vec3(
                direction.x + rand.uniform(-spread_rad, spread_rad),
                direction.y + rand.uniform(-spread_rad, spread_rad),
                direction.z
            ).normalized()

        # TODO(migration): No collision layer filtering. GDScript sets collision_mask to
        # layers 1|4|128 (Environment, Enemy, Destructible). This raycast hits everything
        # including other weapons, UI entities, and the player's own model_pivot. Add
        # Ursina-compatible layer filtering or tag-based ignore list.
        hit = raycast(origin, direction, distance=self.range_distance,
                      ignore=[self, self.weapon_owner])
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
        event_bus.emit(PLAYER_AMMO_CHANGED, self.current_ammo, self.max_ammo)

    def _on_hit(self, entity, point, normal):
        # TODO(migration): GDScript checks collider.has_node("HealthComponent") and gets the
        # component from the scene tree. This checks hasattr(entity, 'health') which is a
        # different pattern — will miss entities where HealthComponent is stored under a
        # different attribute name. Standardize the health component access pattern.
        # TODO(migration): hit.world_normal from Ursina can be None when hitting certain
        # geometry. The fallback on line below handles it, but verify this doesn't produce
        # zero-length knockback vectors when it should have a direction.
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
