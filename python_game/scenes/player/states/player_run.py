"""Player Run state — moving at walk speed."""
from ursina import held_keys, time
from scripts.components.state import State


class PlayerRun(State):
    def __init__(self):
        super().__init__("Run")

    def enter(self, previous_state: str):
        self.owner.is_sprinting = False
        self.owner.current_speed = self.owner.move_speed

    def process_state(self, delta: float):
        player = self.owner
        player.apply_gravity(delta)

        direction = player.get_camera_relative_input()
        if direction.length() < 0.1:
            self.transition_to("Idle")
            return

        player.velocity.x = direction.x * player.move_speed
        player.velocity.z = direction.z * player.move_speed
        player.rotate_model_to_direction(direction, delta)

        if player.grounded:
            player.last_grounded_time = time.time()

        # Transitions
        if held_keys['left shift']:
            self.transition_to("Sprint")
            return

        if not player.grounded:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if key == 'space':
            self.transition_to("Jump")
        elif key == 'left control':
            self.transition_to("Dodge")
        elif key == 'right mouse down':
            self.transition_to("Aim")
