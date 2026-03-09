"""Player Aim state — over-the-shoulder view, slow strafe."""
from scripts.components.state import State
from scripts.autoload.input_manager import input_manager
from scenes.player.camera_controller import CameraMode
from scenes.player.player import INPUT_DEADZONE


class PlayerAim(State):
    def __init__(self):
        super().__init__("Aim")

    def enter(self, previous_state: str, msg: dict = None):
        self.owner.is_aiming = True
        self.owner.camera_controller.set_mode(CameraMode.AIM)

    def exit(self):
        self.owner.is_aiming = False
        self.owner.camera_controller.set_mode(CameraMode.FOLLOW)

    def process_state(self, delta: float):
        player = self.owner
        player.apply_aim_physics(delta)

        # Fire while aiming
        if input_manager.is_action_held('fire'):
            self.transition_to("Shoot")
            return

        if not input_manager.is_action_held('aim'):
            if player.get_camera_relative_input().length() > INPUT_DEADZONE:
                self.transition_to("Run")
            else:
                self.transition_to("Idle")
            return

        if not player.grounded:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if key == 'left mouse' and is_press:
            self.transition_to("Shoot")
        elif key == 'left control':
            self.transition_to("Dodge")
