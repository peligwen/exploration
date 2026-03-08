"""Player Idle state — standing still, waiting for input."""
from ursina import held_keys, time
from scripts.components.state import State


class PlayerIdle(State):
    def __init__(self):
        super().__init__("Idle")

    def enter(self, previous_state: str):
        self.owner.is_sprinting = False
        self.owner.current_speed = 0.0

    def process_state(self, delta: float):
        player = self.owner
        player.apply_gravity(delta)

        # Decelerate to stop
        player.velocity.x *= max(0, 1.0 - delta * 10.0)
        player.velocity.z *= max(0, 1.0 - delta * 10.0)

        # Track grounded for coyote time
        if player.grounded:
            player.last_grounded_time = time.time()

        # Transitions
        direction = player.get_camera_relative_input()
        if direction.length() > 0.1:
            self.transition_to("Run")
            return

        if held_keys['space']:
            self.transition_to("Jump")
            return

        if held_keys['left control']:
            self.transition_to("Dodge")
            return

        if held_keys['right mouse']:
            self.transition_to("Aim")
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
