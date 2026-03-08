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


INPUT_DEADZONE = 0.1
AIR_CONTROL_FACTOR = 0.8
DECEL_FACTOR = 10.0


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

        # Apply gravity before state update
        if not self.grounded:
            self.velocity.y -= self.gravity_strength * dt

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
        # TODO(migration): Always passes is_press=True. Ursina calls input() for both press
        # and release — release keys end with " up" (e.g. "space up"). Detect release:
        #   is_press = not key.endswith(' up')
        #   actual_key = key.replace(' up', '') if not is_press else key
        # Without this, states never see key releases (sprint toggle, aim release, etc.).
        self.state_machine.handle_input(key, True)

    def get_camera_relative_input(self) -> Vec3:
        """Returns movement input relative to camera facing direction."""
        move = input_manager.get_move_vector()
        if abs(move.x) < INPUT_DEADZONE and abs(move.y) < INPUT_DEADZONE:
            return Vec3(0, 0, 0)

        forward = self.camera_controller.get_camera_forward()
        right = self.camera_controller.get_camera_right()
        # TODO(migration): Y-axis is not inverted here. GDScript uses (forward * -input.y)
        # because Godot's input Y-axis points down. Ursina's held_keys w/s may already be
        # correct, but verify — if forward/backward movement is inverted, negate move.y.
        direction = (forward * move.y + right * move.x)
        if direction.length() > 0:
            direction = direction.normalized()
        return direction

    def apply_air_control(self, delta: float):
        """Shared air movement logic used by Jump and Fall states."""
        direction = self.get_camera_relative_input()
        air_speed = self.sprint_speed if self.is_sprinting else self.move_speed
        if direction.length() > INPUT_DEADZONE:
            self.velocity.x = direction.x * air_speed * AIR_CONTROL_FACTOR
            self.velocity.z = direction.z * air_speed * AIR_CONTROL_FACTOR
            self.rotate_model_to_direction(direction, delta)

    def decelerate_horizontal(self, delta: float, rate: float = -1.0):
        """Smoothly decelerates horizontal velocity toward zero."""
        # TODO(migration): GDScript uses move_toward() (linear deceleration toward zero).
        # This multiplicative approach (exponential decay) feels different and can overshoot
        # to negative values with large delta*rate > 1.0. Replace with:
        #   self.velocity.x = move_toward(self.velocity.x, 0, rate * delta)
        #   self.velocity.z = move_toward(self.velocity.z, 0, rate * delta)
        if rate < 0.0:
            rate = self.move_speed * DECEL_FACTOR
        factor = max(0, 1.0 - rate * delta)
        self.velocity.x *= factor
        self.velocity.z *= factor

    def apply_aim_physics(self, delta: float):
        """Shared aim/shoot movement: strafe at aim_speed, face camera direction."""
        direction = self.get_camera_relative_input()
        if direction.length() > INPUT_DEADZONE:
            self.velocity.x = direction.x * self.aim_speed
            self.velocity.z = direction.z * self.aim_speed
        else:
            self.decelerate_horizontal(delta, self.aim_speed * DECEL_FACTOR)
        cam_forward = self.camera_controller.get_camera_forward()
        self.rotate_model_to_direction(cam_forward, delta)
        # Controller look input
        look = input_manager.get_look_vector()
        if abs(look.x) > 0.01 or abs(look.y) > 0.01:
            self.camera_controller.rotate_camera(look.x, look.y, delta)

    def rotate_model_to_direction(self, direction: Vec3, delta: float):
        """Smoothly rotate the player to face movement direction."""
        # TODO(migration): This rotates self.rotation_y (the Entity itself), which also
        # rotates the collider. GDScript rotates model.rotation.y (a child node) separately
        # from the physics body. Rotate self.model_pivot.rotation_y instead of self.rotation_y
        # to keep the collider axis-aligned.
        if direction.length() < INPUT_DEADZONE:
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
        # TODO(migration): No wall collision at all — player walks through all walls and
        # pillars. GDScript uses CharacterBody3D.move_and_slide() which handles wall sliding
        # automatically. Implement horizontal raycasts or use Ursina's collider system to
        # prevent walking through geometry. Floor clamping at y=0.9 is also hardcoded and
        # won't work for multi-level terrain.
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
        # TODO(migration): GDScript version triggers heartbeat haptic feedback when HP drops
        # below 25%. Add:
        #   if current / maximum < 0.25:
        #       input_manager.request_haptic("heartbeat", ...)
        event_bus.emit(PLAYER_HEALTH_CHANGED, current, maximum)

    def _on_died(self):
        event_bus.emit(PLAYER_DIED)
        self.state_machine.transition_to("Dead")

    def get_save_data(self) -> dict:
        return {
            "id": "player",
            # TODO(migration): GDScript uses global_position. self.position in Ursina is
            # local if parented. Use self.world_position for correct save data.
            "position": [self.position.x, self.position.y, self.position.z],
            "health": self.health.get_save_data(),
        }

    def load_save_data(self, data: dict):
        pos = data.get("position", [0, 0.9, 0])
        self.position = Vec3(pos[0], pos[1], pos[2])
        if "health" in data:
            self.health.load_save_data(data["health"])
