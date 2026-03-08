"""Player Fall state — airborne, descending."""
from ursina import time
from scripts.components.state import State


class PlayerFall(State):
    def __init__(self):
        super().__init__("Fall")

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

        # Jump buffering
        player.jump_buffer_timer -= delta

        if player.grounded:
            if player.jump_buffer_timer > 0.0:
                player.jump_buffer_timer = 0.0
                self.transition_to("Jump")
            elif direction.length() > 0.1:
                self.transition_to("Run")
            else:
                self.transition_to("Idle")

    def handle_input(self, key, is_press):
        if key == 'space':
            self.owner.jump_buffer_timer = self.owner.jump_buffer_time
