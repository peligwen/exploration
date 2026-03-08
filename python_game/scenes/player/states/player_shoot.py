"""Player Shoot state — fire weapon continuously while held."""
from ursina import held_keys
from scripts.components.state import State
from scenes.player.camera_controller import CameraMode
from scripts.autoload.input_manager import input_manager


class PlayerShoot(State):
    def __init__(self):
        super().__init__("Shoot")
        self._shoot_timer = 0.0

    def enter(self, previous_state: str):
        self.owner.is_aiming = True
        self.owner.camera_controller.set_mode(CameraMode.AIM)
        self._fire()

    def process_state(self, delta: float):
        player = self.owner
        player.apply_gravity(delta)

        # Strafe while shooting
        direction = player.get_camera_relative_input()
        if direction.length() > 0.1:
            player.velocity.x = direction.x * player.aim_speed
            player.velocity.z = direction.z * player.aim_speed
        else:
            player.velocity.x *= max(0, 1.0 - delta * 10.0)
            player.velocity.z *= max(0, 1.0 - delta * 10.0)

        cam_forward = player.camera_controller.get_camera_forward()
        player.rotate_model_to_direction(cam_forward, delta)

        # Controller look
        look = input_manager.get_look_vector()
        if abs(look.x) > 0.01 or abs(look.y) > 0.01:
            player.camera_controller.rotate_camera(look.x, look.y, delta)

        self._shoot_timer -= delta

        # Continuous fire while held
        if held_keys['left mouse'] and self._shoot_timer <= 0.0:
            self._fire()
            return

        # Release fire
        if not held_keys['left mouse']:
            if held_keys['right mouse']:
                self.transition_to("Aim")
            else:
                self.transition_to("Idle")
            return

    def handle_input(self, key, is_press):
        if key == 'left control':
            self.transition_to("Dodge")

    def _fire(self):
        player = self.owner
        if player.current_weapon and hasattr(player.current_weapon, 'fire'):
            player.current_weapon.fire()

        player.camera_controller.add_shake(0.3)
        self._shoot_timer = 0.15
