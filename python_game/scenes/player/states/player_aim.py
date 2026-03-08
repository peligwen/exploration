"""Player Aim state — over-the-shoulder view, slow strafe."""
from ursina import held_keys
from scripts.components.state import State
from scenes.player.camera_controller import CameraMode
from scenes.player.player import INPUT_DEADZONE


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
        player.apply_aim_physics(delta)

        # Fire while aiming
        if held_keys['left mouse']:
            self.transition_to("Shoot")
            return

        if not held_keys['right mouse']:
            if player.get_camera_relative_input().length() > INPUT_DEADZONE:
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
