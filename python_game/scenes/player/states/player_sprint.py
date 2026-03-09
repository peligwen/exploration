"""Player Sprint state — moving at sprint speed."""
from ursina import time
from scripts.components.state import State
from scripts.autoload.input_manager import input_manager
from scenes.player.player import INPUT_DEADZONE


class PlayerSprint(State):
    def __init__(self):
        super().__init__("Sprint")

    def enter(self, previous_state: str, msg: dict = None):
        self.owner.is_sprinting = True
        self.owner.current_speed = self.owner.sprint_speed

    def exit(self):
        self.owner.is_sprinting = False

    def process_state(self, delta: float):
        player = self.owner

        direction = player.get_camera_relative_input()
        if direction.length() < INPUT_DEADZONE:
            self.transition_to("Idle")
            return

        player.velocity.x = direction.x * player.sprint_speed
        player.velocity.z = direction.z * player.sprint_speed
        player.rotate_model_to_direction(direction, delta)

        if player.grounded:
            player.last_grounded_time = time.time()

        if not input_manager.is_action_held('sprint'):
            self.transition_to("Run")
            return

        if not player.grounded:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if key == 'space':
            self.transition_to("Jump")
        elif key == 'left control':
            self.transition_to("Dodge")
