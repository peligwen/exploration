"""Base enemy controller. Uses state machine for behavior."""
from ursina import Entity, Vec3, color, time, lerp
import math

from scripts.autoload.game_manager import game_manager
from scripts.components.state_machine import StateMachine
from scripts.components.health_component import HealthComponent
from scripts.resources.damage_info import DamageInfo, DamageType


class BaseEnemy(Entity):
    """Base enemy with state machine, health, and navigation."""

    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.red,
            scale=(1.0, 2.0, 1.0),
            collider='box',
            **kwargs
        )

        # Stats
        self.move_speed = 3.5
        self.chase_speed = 5.0
        self.attack_damage = 10.0
        self.attack_range = 2.5
        self.detection_range = 15.0
        self.attack_cooldown = 1.0

        # Patrol
        self.patrol_points: list[Vec3] = []
        self.patrol_wait_time = 2.0

        # Runtime
        self.target = None  # Usually the player
        self.gravity_strength = 20.0
        # TODO(migration): id(self) returns a memory address that changes every run. Not
        # stable for save/load across sessions. Use a deterministic ID like a UUID or an
        # auto-incrementing counter stored on the class.
        self.unique_id = str(id(self))
        self.velocity = Vec3(0, 0, 0)
        self.grounded = True

        # Health
        self.health = HealthComponent(max_hp=100.0)
        self.health.owner = self
        self.health.on_died = self._on_died
        self.health.on_damage_taken = self._on_damage_taken

        # State machine (states added by scene setup)
        self.state_machine = StateMachine(owner=self)

        # Register
        game_manager.register_saveable(self)

    def update(self):
        dt = time.dt
        if dt <= 0:
            return

        self.health.update(dt)

        # Gravity
        if not self.grounded:
            self.velocity.y -= self.gravity_strength * dt

        self.state_machine.update(dt)

        # TODO(migration): No wall collision — enemies walk through all walls and pillars.
        # Same issue as player._apply_physics(). Need horizontal raycasts or Ursina collider
        # integration to prevent enemies from walking through arena geometry.
        # Apply physics
        self.position += self.velocity * dt

        # Floor clamping
        if self.position.y < 1.0:
            self.position = Vec3(self.position.x, 1.0, self.position.z)
            self.velocity.y = 0
            self.grounded = True

    def get_distance_to_target(self) -> float:
        if self.target:
            return (self.position - self.target.position).length()
        return float('inf')

    def can_see_target(self) -> bool:
        # TODO(migration): No line-of-sight check — only checks distance. Enemy can "see"
        # the player through walls and pillars. Add a raycast from self.position to
        # target.position and verify no environment geometry blocks the line of sight.
        if not self.target:
            return False
        return self.get_distance_to_target() <= self.detection_range

    def is_in_attack_range(self) -> bool:
        return self.get_distance_to_target() <= self.attack_range

    def face_target(self, delta: float):
        if not self.target:
            return
        direction = (self.target.position - self.position)
        direction = Vec3(direction.x, 0, direction.z)
        if direction.length() > 0.01:
            target_angle = math.degrees(math.atan2(direction.x, direction.z))
            diff = (target_angle - self.rotation_y + 180) % 360 - 180
            self.rotation_y += diff * min(delta * 8.0, 1.0)

    def navigate_to(self, target_pos: Vec3, speed: float, delta: float):
        """Simple pathfinding — move directly toward target."""
        direction = target_pos - self.position
        direction = Vec3(direction.x, 0, direction.z)
        if direction.length() < 0.5:
            self.velocity.x = 0
            self.velocity.z = 0
            return

        direction = direction.normalized()
        self.velocity.x = direction.x * speed
        self.velocity.z = direction.z * speed

        # Face movement direction
        if direction.length() > 0.01:
            target_angle = math.degrees(math.atan2(direction.x, direction.z))
            diff = (target_angle - self.rotation_y + 180) % 360 - 180
            self.rotation_y += diff * min(delta * 8.0, 1.0)

    def deal_damage_to_target(self):
        if self.target and hasattr(self.target, 'health'):
            direction = (self.target.position - self.position).normalized()
            info = DamageInfo.create(
                self.attack_damage,
                self,
                DamageType.PHYSICAL,
                self.target.position,
                direction * 3.0
            )
            self.target.health.take_damage(info)

    def _on_died(self):
        self.state_machine.transition_to("Dead")

    def _on_damage_taken(self, damage_info):
        if not self.health.is_dead:
            self.state_machine.transition_to("Hurt")

    def get_save_data(self) -> dict:
        return {
            "id": self.unique_id,
            "position": [self.position.x, self.position.y, self.position.z],
            "health": self.health.get_save_data(),
        }

    def load_save_data(self, data: dict):
        pos = data.get("position", [0, 1, 0])
        self.position = Vec3(pos[0], pos[1], pos[2])
        if "health" in data:
            self.health.load_save_data(data["health"])
