"""Player Idle state — standing still, waiting for input."""
from ursina import held_keys, time
from scripts.components.state import State
from scenes.player.player import INPUT_DEADZONE


class PlayerIdle(State):
    def __init__(self):
        super().__init__("Idle")

    def enter(self, previous_state: str, msg: dict = None):
        self.owner.is_sprinting = False
        self.owner.current_speed = 0.0

    def process_state(self, delta: float):
        player = self.owner
        player.decelerate_horizontal(delta)

        # Track grounded for coyote time
        if player.grounded:
            player.last_grounded_time = time.time()

        # Continuous transitions (held state checks only — discrete actions use handle_input)
        direction = player.get_camera_relative_input()
        if direction.length() > INPUT_DEADZONE:
            self.transition_to("Run")
            return

        if held_keys['right mouse']:
            self.transition_to("Aim")
            return

        if not player.grounded:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if not is_press:
            return
        if key == 'space':
            self.transition_to("Jump")
        elif key == 'left control':
            self.transition_to("Dodge")
        elif key == 'right mouse':
            self.transition_to("Aim")
