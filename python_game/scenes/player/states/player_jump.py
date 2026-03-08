"""Player Jump state — upward velocity, air control."""
from ursina import time
from scripts.components.state import State
from scenes.player.player import INPUT_DEADZONE


class PlayerJump(State):
    def __init__(self):
        super().__init__("Jump")

    def enter(self, previous_state: str):
        player = self.owner
        now = time.time()
        can_jump = player.grounded or (now - player.last_grounded_time) < player.coyote_time

        if can_jump:
            player.velocity.y = player.jump_force
            player.grounded = False
        else:
            player.jump_buffer_timer = player.jump_buffer_time
            self.transition_to("Fall")

    def process_state(self, delta: float):
        player = self.owner
        player.apply_air_control(delta)

        if player.velocity.y <= 0.0:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if key == 'left control':
            direction = self.owner.get_camera_relative_input()
            if direction.length() > INPUT_DEADZONE:
                self.transition_to("Dodge")
