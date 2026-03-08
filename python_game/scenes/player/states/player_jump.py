"""Player Jump state — upward velocity, air control."""
from ursina import time
from scripts.components.state import State


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
        player.apply_gravity(delta)

        # Air control
        direction = player.get_camera_relative_input()
        air_speed = player.sprint_speed if player.is_sprinting else player.move_speed
        if direction.length() > 0.1:
            player.velocity.x = direction.x * air_speed * 0.8
            player.velocity.z = direction.z * air_speed * 0.8
            player.rotate_model_to_direction(direction, delta)

        if player.velocity.y <= 0.0:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if key == 'left control':
            direction = self.owner.get_camera_relative_input()
            if direction.length() > 0.1:
                self.transition_to("Dodge")
