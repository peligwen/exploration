"""Independent camera system. Follows a target entity.
Modes: Follow, Aim, Shake, Death.
"""
from ursina import Entity, camera, Vec3, lerp, raycast
from enum import Enum
import math
import random


class CameraMode(Enum):
    FOLLOW = 0
    AIM = 1
    SHAKE = 2
    DEATH = 3


class CameraController:
    """Third-person camera controller with multiple modes."""

    def __init__(self, target: Entity):
        self.target = target
        self.mode = CameraMode.FOLLOW

        # Follow mode settings
        self.follow_distance = 5.0
        self.follow_height = 2.0

        # Aim mode settings (right, up, back offsets)
        self.aim_offset = Vec3(0.8, 1.8, 3.0)
        self.aim_fov = 55.0
        self.default_fov = 70.0

        # General settings
        self.lerp_speed = 10.0
        self.auto_center_speed = 1.5

        # Rotation state
        self.pitch = 0.0  # Vertical rotation in degrees
        self.yaw = 0.0    # Horizontal rotation in degrees

        # Shake state
        self._shake_amount = 0.0
        self._shake_decay = 5.0

        # Death orbit
        self._death_orbit_speed = 15.0  # degrees per second

        # Set up camera
        camera.fov = self.default_fov

    def set_mode(self, new_mode: CameraMode):
        self.mode = new_mode

    def apply_mouse_motion(self, dx: float, dy: float):
        """Apply mouse delta to camera rotation."""
        self.yaw -= dx
        self.pitch -= dy
        self.pitch = max(-70, min(70, self.pitch))

    def rotate_camera(self, look_x: float, look_y: float, delta: float):
        """Apply controller stick input to camera rotation."""
        self.yaw -= look_x * delta * 60
        self.pitch -= look_y * delta * 60
        self.pitch = max(-70, min(70, self.pitch))

    def add_shake(self, amount: float):
        self._shake_amount = max(self._shake_amount, amount)

    def get_camera_forward(self) -> Vec3:
        """Returns the flat (Y=0) forward direction of the camera.
        Yaw-only by design so ground movement is always horizontal."""
        rad = math.radians(self.yaw)
        forward = Vec3(-math.sin(rad), 0, -math.cos(rad))
        return forward.normalized()

    def get_camera_right(self) -> Vec3:
        """Returns the flat (Y=0) right direction of the camera."""
        rad = math.radians(self.yaw)
        right = Vec3(-math.cos(rad), 0, math.sin(rad))
        return right.normalized()

    def update(self, delta: float):
        if not self.target:
            return

        target_pos = self.target.position

        if self.mode == CameraMode.FOLLOW:
            self._process_follow(target_pos, delta)
        elif self.mode == CameraMode.AIM:
            self._process_aim(target_pos, delta)
        elif self.mode == CameraMode.DEATH:
            self._process_death(target_pos, delta)

        # Apply shake on top of any mode
        if self._shake_amount > 0.01:
            self._apply_shake(delta)

    def _spring_arm(self, eye: Vec3, desired: Vec3) -> Vec3:
        """Shorten camera arm when geometry sits between player and camera.
        Mirrors GDScript SpringArm3D: raycast from eye to desired position and
        pull the camera forward from any hit point by a small margin."""
        direction = desired - eye
        distance = direction.length()
        if distance < 0.01:
            return desired
        ignore = [self.target]
        if hasattr(self.target, 'model_pivot'):
            ignore.append(self.target.model_pivot)
        hit = raycast(
            eye, direction.normalized(),
            distance=distance, ignore=ignore)
        if hit.hit:
            # Pull slightly away from the surface so the camera doesn't clip
            return hit.world_point - direction.normalized() * 0.15
        return desired

    def _process_follow(self, target_pos: Vec3, delta: float):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        # Calculate camera position behind and above player
        cos_p = math.cos(pitch_rad)
        dist = self.follow_distance
        offset_x = math.sin(yaw_rad) * cos_p * dist
        offset_y = math.sin(pitch_rad) * dist + self.follow_height
        offset_z = math.cos(yaw_rad) * cos_p * dist

        eye = target_pos + Vec3(0, 1.0, 0)
        offset = Vec3(offset_x, offset_y, offset_z)
        camera_pos = self._spring_arm(eye, target_pos + offset)
        t = delta * self.lerp_speed
        camera.position = lerp(camera.position, camera_pos, t)

        # Look at target with slight height offset
        look_target = target_pos + Vec3(0, 1.0, 0)
        camera.look_at(look_target)

        t = delta * self.lerp_speed
        camera.fov = lerp(camera.fov, self.default_fov, t)

    def _process_aim(self, target_pos: Vec3, delta: float):
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        # Over-the-shoulder offset
        right_dir = Vec3(-math.cos(yaw_rad), 0, math.sin(yaw_rad))
        back_dir = Vec3(math.sin(yaw_rad), 0, math.cos(yaw_rad))

        offset = (right_dir * self.aim_offset.x +
                  Vec3(0, self.aim_offset.y, 0) +
                  back_dir * self.aim_offset.z)

        # Apply pitch to vertical offset
        offset.y += math.sin(pitch_rad) * self.aim_offset.z * 0.5

        eye = target_pos + Vec3(0, self.aim_offset.y, 0)
        camera_pos = self._spring_arm(eye, target_pos + offset)
        t = delta * self.lerp_speed
        camera.position = lerp(camera.position, camera_pos, t)

        look_target = target_pos + Vec3(0, 1.2, 0)
        camera.look_at(look_target)

        camera.fov = lerp(camera.fov, self.aim_fov, t)

    def _process_death(self, target_pos: Vec3, delta: float):
        self.yaw += self._death_orbit_speed * delta

        yaw_rad = math.radians(self.yaw)
        distance = 8.0
        height = 3.0

        camera_pos = target_pos + Vec3(
            math.sin(yaw_rad) * distance,
            height,
            math.cos(yaw_rad) * distance
        )
        camera.position = lerp(camera.position, camera_pos, delta * 2.0)
        camera.look_at(target_pos + Vec3(0, 0.5, 0))

    def _apply_shake(self, delta: float):
        shake_offset = Vec3(
            random.uniform(-self._shake_amount, self._shake_amount),
            random.uniform(-self._shake_amount, self._shake_amount),
            0
        ) * 0.1
        camera.position += shake_offset
        decay = delta * self._shake_decay
        self._shake_amount = lerp(
            self._shake_amount, 0.0, decay)
        if self._shake_amount < 0.01:
            self._shake_amount = 0.0
            camera.position = Vec3(0, 0, 0)
