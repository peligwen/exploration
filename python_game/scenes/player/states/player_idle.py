"""Player Idle state — standing still, waiting for input."""
from ursina import held_keys, time
from scripts.components.state import State
from scenes.player.player import INPUT_DEADZONE


class PlayerIdle(State):
    def __init__(self):
        super().__init__("Idle")

    def enter(self, previous_state: str):
        self.owner.is_sprinting = False
        self.owner.current_speed = 0.0

    def process_state(self, delta: float):
        player = self.owner
        player.decelerate_horizontal(delta)

        # Track grounded for coyote time
        if player.grounded:
            player.last_grounded_time = time.time()

        # Transitions
        direction = player.get_camera_relative_input()
        if direction.length() > INPUT_DEADZONE:
            self.transition_to("Run")
            return

        # TODO(migration): Double-transition risk — process_state() checks held_keys['space']
        # AND handle_input() also transitions on 'space'. Both can fire in the same frame,
        # causing a double transition. Remove the held_keys check here and rely solely on
        # handle_input() for discrete actions (jump, dodge), or add a guard in transition_to.
        if held_keys['space']:
            self.transition_to("Jump")
            return

        if held_keys['left control']:
            self.transition_to("Dodge")
            return

        # TODO(migration): Verify Ursina key name — 'right mouse' may not work for held
        # state. Ursina uses 'right mouse down' for press events and held_keys may use a
        # different key name. Test and confirm the correct held_keys key for right mouse.
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
