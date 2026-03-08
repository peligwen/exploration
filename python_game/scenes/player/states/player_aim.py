"""Player Aim state — over-the-shoulder view, slow strafe."""
from ursina import held_keys
from scripts.components.state import State
from scenes.player.camera_controller import CameraMode
from scripts.autoload.input_manager import input_manager


class PlayerAim(State):
    def __init__(self):
        super().__init__("Aim")

    def enter(self, previous_state: str):
        self.owner.is_aiming = True
        self.owner.camera_controller.set_mode(CameraMode.AIM)

    def exit(self):
        self.owner.is_aiming = False
        self.owner.camera_controller.set_mode(CameraMode.FOLLOW)

    def process_state(self, delta: float):
        player = self.owner
        player.apply_gravity(delta)

        # Slow strafe movement while aiming
        direction = player.get_camera_relative_input()
        if direction.length() > 0.1:
            player.velocity.x = direction.x * player.aim_speed
            player.velocity.z = direction.z * player.aim_speed
        else:
            player.velocity.x *= max(0, 1.0 - delta * 10.0)
            player.velocity.z *= max(0, 1.0 - delta * 10.0)

        # Face camera direction while aiming
        cam_forward = player.camera_controller.get_camera_forward()
        player.rotate_model_to_direction(cam_forward, delta)

        # Controller look
        look = input_manager.get_look_vector()
        if abs(look.x) > 0.01 or abs(look.y) > 0.01:
            player.camera_controller.rotate_camera(look.x, look.y, delta)

        # Fire while aiming
        if held_keys['left mouse']:
            self.transition_to("Shoot")
            return

        if not held_keys['right mouse']:
            direction = player.get_camera_relative_input()
            if direction.length() > 0.1:
                self.transition_to("Run")
            else:
                self.transition_to("Idle")
            return

        if not player.grounded:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if key == 'left mouse down':
            self.transition_to("Shoot")
        elif key == 'left control':
            self.transition_to("Dodge")
