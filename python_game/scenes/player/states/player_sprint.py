"""Player Sprint state — moving at sprint speed."""
from ursina import held_keys, time
from scripts.components.state import State


class PlayerSprint(State):
    def __init__(self):
        super().__init__("Sprint")

    def enter(self, previous_state: str):
        self.owner.is_sprinting = True
        self.owner.current_speed = self.owner.sprint_speed

    def exit(self):
        self.owner.is_sprinting = False

    def process_state(self, delta: float):
        player = self.owner
        player.apply_gravity(delta)

        direction = player.get_camera_relative_input()
        if direction.length() < 0.1:
            self.transition_to("Idle")
            return

        player.velocity.x = direction.x * player.sprint_speed
        player.velocity.z = direction.z * player.sprint_speed
        player.rotate_model_to_direction(direction, delta)

        if player.grounded:
            player.last_grounded_time = time.time()

        if not held_keys['left shift']:
            self.transition_to("Run")
            return

        if not player.grounded:
            self.transition_to("Fall")

    def handle_input(self, key, is_press):
        if key == 'space':
            self.transition_to("Jump")
        elif key == 'left control':
            self.transition_to("Dodge")
