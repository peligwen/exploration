"""Player Fall state — airborne, descending."""
from scripts.components.state import State
from scenes.player.player import INPUT_DEADZONE


class PlayerFall(State):
    def __init__(self):
        super().__init__("Fall")

    def process_state(self, delta: float):
        player = self.owner
        player.apply_air_control(delta)

        # Jump buffering
        player.jump_buffer_timer -= delta

        if player.grounded:
            if player.jump_buffer_timer > 0.0:
                player.jump_buffer_timer = 0.0
                self.transition_to("Jump")
            elif player.get_camera_relative_input().length() > INPUT_DEADZONE:
                self.transition_to("Run")
            else:
                self.transition_to("Idle")

    def handle_input(self, key, is_press):
        if key == 'space':
            self.owner.jump_buffer_timer = self.owner.jump_buffer_time
