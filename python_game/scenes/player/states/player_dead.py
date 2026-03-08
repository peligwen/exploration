"""Player Dead state — disable input, death camera orbit."""
from ursina import Vec3
from scripts.components.state import State
from scenes.player.camera_controller import CameraMode


class PlayerDead(State):
    def __init__(self):
        super().__init__("Dead")

    def enter(self, previous_state: str):
        self.owner.camera_controller.set_mode(CameraMode.DEATH)
        self.owner.velocity = Vec3(0, 0, 0)

    def process_state(self, delta: float):
        # Gravity is applied by Player.update()
        pass
