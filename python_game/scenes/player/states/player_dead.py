"""Player Dead state — disable input, death camera orbit."""
from ursina import Vec3
from scripts.components.state import State
from scripts.autoload.game_manager import game_manager
from scenes.player.camera_controller import CameraMode

RESPAWN_POSITION = Vec3(0, 0.9, 0)


class PlayerDead(State):
    def __init__(self):
        super().__init__("Dead")

    def enter(self, previous_state: str, msg: dict = None):
        self.owner.camera_controller.set_mode(CameraMode.DEATH)
        self.owner.velocity = Vec3(0, 0, 0)

    def process_state(self, delta: float):
        # Gravity is applied by Player.update()
        pass

    def handle_input(self, key, is_press):
        if key == 'r' and is_press:
            self._respawn()

    def _respawn(self):
        player = self.owner
        player.health.reset()
        player.position = RESPAWN_POSITION
        player.velocity = Vec3(0, 0, 0)
        player.camera_controller.set_mode(CameraMode.FOLLOW)
        self.transition_to("Idle")
