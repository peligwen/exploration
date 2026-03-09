"""Player controller. Delegates behavior to the state machine.
Provides shared state and utilities that all player states access.
"""
from ursina import Entity, Vec3, Vec2, held_keys, mouse, time, lerp, color, raycast
import math

from scripts.autoload.event_bus import event_bus, PLAYER_HEALTH_CHANGED, PLAYER_DIED
from scripts.resources.collision_layers import LAYER_PLAYER
from scripts.autoload.input_manager import input_manager, DeviceType, CONTROLLER_KEY_MAP
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
                                  scale=(1, 1, 1), origin=(0, -0.5, 0),
                                  collision_group=LAYER_PLAYER)
        self.model = None  # Use model_pivot directly

        # Camera controller
        self.camera_controller = CameraController(self)

        # Health component
        self.health = HealthComponent(max_hp=100.0, iframe_duration=0.3)
        self.health.owner = self
        self.health.on_health_changed = self._on_health_changed
        self.health.on_damage_taken = self._on_damage_taken
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
            if dx != 0 or dy != 0:
                input_manager.notify_input(DeviceType.KB_MOUSE)
            if input_manager.invert_y_mouse:
                dy *= -1
            self.camera_controller.apply_mouse_motion(dx, dy)

        # Controller look (right stick) — runs every frame regardless of mouse
        look = input_manager.get_look_vector()  # notify_input called inside
        if look.x != 0 or look.y != 0:
            self.camera_controller.rotate_camera(look.x, look.y, dt)

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
        """Handle input events. Escape is reserved for the global pause handler."""
        if key in ('escape', 'escape up'):
            return

        # Remap controller button strings to their KB equivalents so that
        # state handle_input() methods only need to handle one set of key names.
        is_release = key.endswith(' up')
        base_key = key[:-3] if is_release else key
        if base_key in CONTROLLER_KEY_MAP:
            base_key = CONTROLLER_KEY_MAP[base_key]
            key = base_key + (' up' if is_release else '')

        is_press = not is_release
        self.state_machine.handle_input(base_key, is_press)

    def get_camera_relative_input(self) -> Vec3:
        """Returns movement input relative to camera facing direction."""
        move = input_manager.get_move_vector()
        if abs(move.x) < INPUT_DEADZONE and abs(move.y) < INPUT_DEADZONE:
            return Vec3(0, 0, 0)

        forward = self.camera_controller.get_camera_forward()
        right = self.camera_controller.get_camera_right()
        # Ursina w/s give positive/negative y as expected (no inversion needed)
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
        """Linearly decelerates horizontal velocity toward zero (move_toward behaviour)."""
        if rate < 0.0:
            rate = self.move_speed * DECEL_FACTOR
        step = rate * delta
        vx = self.velocity.x
        vz = self.velocity.z
        self.velocity.x = vx - max(-step, min(step, vx))
        self.velocity.z = vz - max(-step, min(step, vz))

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
        """Smoothly rotate the visual model pivot to face movement direction.
        The collider (self) is left axis-aligned."""
        if direction.length() < INPUT_DEADZONE:
            return
        self.facing_direction = direction
        target_angle = math.degrees(math.atan2(direction.x, direction.z))
        current_y = self.model_pivot.rotation_y
        diff = (target_angle - current_y + 180) % 360 - 180
        self.model_pivot.rotation_y += diff * min(delta * 12.0, 1.0)

    def _check_grounded(self):
        """Simple ground check using raycast."""
        ray = raycast(
            self.position + Vec3(0, 0.1, 0),
            Vec3(0, -1, 0),
            distance=0.3,
            ignore=[self, self.model_pivot]
        )
        self.grounded = ray.hit

    def _apply_physics(self, delta: float):
        """Apply velocity with move-and-slide wall collision."""
        if self.velocity.y < -50:
            self.velocity.y = -50

        # --- Horizontal wall collision (move-and-slide) ---
        horiz = Vec3(self.velocity.x, 0, self.velocity.z)
        if horiz.length() > 0.001:
            horiz_dir = horiz.normalized()
            step = horiz.length() * delta
            # Cast from chest height to avoid floor false-positives
            origin = self.position + Vec3(0, 0.6, 0)
            skin = 0.3  # capsule radius approximation
            hit = raycast(origin, horiz_dir, distance=step + skin,
                          ignore=[self, self.model_pivot])
            if hit.hit and hit.distance <= step + skin:
                wall_normal = Vec3(hit.world_normal.x, 0, hit.world_normal.z)
                if wall_normal.length() > 0.01:
                    wall_normal = wall_normal.normalized()
                    # Remove the velocity component going into the wall (slide)
                    dot = self.velocity.x * wall_normal.x + self.velocity.z * wall_normal.z
                    if dot < 0:
                        self.velocity.x -= dot * wall_normal.x
                        self.velocity.z -= dot * wall_normal.z

        # --- Apply full movement ---
        self.position += self.velocity * delta

        # --- Floor clamping ---
        if self.position.y < 0.9:
            self.position = Vec3(self.position.x, 0.9, self.position.z)
            self.velocity.y = 0
            self.grounded = True

    def _on_damage_taken(self, damage_info):
        if not self.health.is_dead:
            self.state_machine.transition_to("Hurt", {"damage_info": damage_info})

    def _on_health_changed(self, current: float, maximum: float):
        if maximum > 0 and (current / maximum) < 0.25:
            input_manager.request_haptic("heartbeat")
        event_bus.emit(PLAYER_HEALTH_CHANGED, current, maximum)

    def _on_died(self):
        event_bus.emit(PLAYER_DIED)
        self.state_machine.transition_to("Dead")

    def get_save_data(self) -> dict:
        wp = self.world_position
        return {
            "id": "player",
            "position": [wp.x, wp.y, wp.z],
            "health": self.health.get_save_data(),
        }

    def load_save_data(self, data: dict):
        pos = data.get("position", [0, 0.9, 0])
        self.position = Vec3(pos[0], pos[1], pos[2])
        if "health" in data:
            self.health.load_save_data(data["health"])
