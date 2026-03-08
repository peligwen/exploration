"""Player controller. Delegates behavior to the state machine.
Provides shared state and utilities that all player states access.
"""
from ursina import Entity, Vec3, Vec2, held_keys, mouse, time, lerp, color
import math

from scripts.autoload.event_bus import event_bus, PLAYER_HEALTH_CHANGED, PLAYER_DIED
from scripts.autoload.input_manager import input_manager
from scripts.autoload.game_manager import game_manager
from scripts.components.state_machine import StateMachine
from scripts.components.health_component import HealthComponent
from scenes.player.camera_controller import CameraController, CameraMode


class Player(Entity):
    """Player character with state machine, health, and camera."""

    def __init__(self, **kwargs):
        super().__init__(
            model='cube',
            color=color.azure,
            scale=(0.8, 1.8, 0.8),
            collider='box',
            **kwargs
        )

        # Movement tuning
        self.move_speed = 6.0
        self.sprint_speed = 10.0
        self.aim_speed = 3.0
        self.jump_force = 8.0
        self.gravity_strength = 20.0
        self.dodge_speed = 14.0
        self.dodge_duration = 0.4
        self.coyote_time = 0.1
        self.jump_buffer_time = 0.12

        # Runtime state (shared between states)
        self.is_aiming = False
        self.is_sprinting = False
        self.is_dodging = False
        self.is_invincible = False
        self.current_speed = 0.0
        self.move_direction = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.last_grounded_time = 0.0
        self.jump_buffer_timer = 0.0
        self.facing_direction = Vec3(0, 0, -1)
        self.grounded = True

        # Weapon mount point (offset from player)
        self.weapon_mount_offset = Vec3(0.3, 0.5, -0.5)
        self.current_weapon = None

        # Model (visual child for rotation separate from physics)
        self.model_pivot = Entity(parent=self, model='cube', color=color.azure,
                                  scale=(1, 1, 1), origin=(0, -0.5, 0))
        self.model = None  # Use model_pivot directly

        # Camera controller
        self.camera_controller = CameraController(self)

        # Health component
        self.health = HealthComponent(max_hp=100.0)
        self.health.owner = self
        self.health.on_health_changed = self._on_health_changed
        self.health.on_died = self._on_died

        # State machine (states are added by the arena/scene setup)
        self.state_machine = StateMachine(owner=self)

        # Register as saveable
        game_manager.register_saveable(self)

        # Mouse capture
        mouse.locked = True
        mouse.visible = False

    def update(self):
        dt = time.dt
        if dt <= 0:
            return

        # Mouse look
        if mouse.locked:
            sensitivity = input_manager.mouse_sensitivity
            dx = mouse.velocity[0] * sensitivity
            dy = mouse.velocity[1] * sensitivity
            if input_manager.invert_y_mouse:
                dy *= -1
            self.camera_controller.apply_mouse_motion(dx, dy)

        # Update health i-frames
        self.health.update(dt)

        # Update state machine
        self.state_machine.update(dt)

        # Update camera
        self.camera_controller.update(dt)

        # Ground check
        self._check_grounded()

        # Apply physics
        self._apply_physics(dt)

    def input(self, key):
        """Handle input events."""
        self.state_machine.handle_input(key, True)

    def get_camera_relative_input(self) -> Vec3:
        """Returns movement input relative to camera facing direction."""
        move = input_manager.get_move_vector()
        if abs(move.x) < 0.1 and abs(move.y) < 0.1:
            return Vec3(0, 0, 0)

        forward = self.camera_controller.get_camera_forward()
        right = self.camera_controller.get_camera_right()
        direction = (forward * move.y + right * move.x)
        if direction.length() > 0:
            direction = direction.normalized()
        return direction

    def apply_gravity(self, delta: float):
        """Apply gravity when not on floor."""
        if not self.grounded:
            self.velocity.y -= self.gravity_strength * delta

    def rotate_model_to_direction(self, direction: Vec3, delta: float):
        """Smoothly rotate the player to face movement direction."""
        if direction.length() < 0.1:
            return
        self.facing_direction = direction
        target_angle = math.degrees(math.atan2(direction.x, direction.z))
        current_y = self.rotation_y
        # Lerp rotation
        diff = (target_angle - current_y + 180) % 360 - 180
        self.rotation_y += diff * min(delta * 12.0, 1.0)

    def _check_grounded(self):
        """Simple ground check using raycast."""
        from ursina import raycast, Vec3
        ray = raycast(
            self.position + Vec3(0, 0.1, 0),
            Vec3(0, -1, 0),
            distance=0.3,
            ignore=[self, self.model_pivot]
        )
        self.grounded = ray.hit

    def _apply_physics(self, delta: float):
        """Apply velocity to position with simple collision."""
        # Clamp fall speed
        if self.velocity.y < -50:
            self.velocity.y = -50

        # Apply velocity
        movement = self.velocity * delta

        # Simple collision: try to move, check for ground
        self.position += movement

        # Floor clamping
        if self.position.y < 0.9:
            self.position = Vec3(self.position.x, 0.9, self.position.z)
            self.velocity.y = 0
            self.grounded = True

    def _on_health_changed(self, current: float, maximum: float):
        event_bus.emit(PLAYER_HEALTH_CHANGED, current, maximum)

    def _on_died(self):
        event_bus.emit(PLAYER_DIED)
        self.state_machine.transition_to("Dead")

    def get_save_data(self) -> dict:
        return {
            "id": "player",
            "position": [self.position.x, self.position.y, self.position.z],
            "health": self.health.get_save_data(),
        }

    def load_save_data(self, data: dict):
        pos = data.get("position", [0, 0.9, 0])
        self.position = Vec3(pos[0], pos[1], pos[2])
        if "health" in data:
            self.health.load_save_data(data["health"])
