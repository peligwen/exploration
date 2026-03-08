"""Player Hurt state — brief stun after taking damage."""
from scripts.components.state import State
from scenes.player.player import INPUT_DEADZONE

HURT_DURATION = 0.3
HURT_DECEL = 20.0


class PlayerHurt(State):
    def __init__(self):
        super().__init__("Hurt")
        self._timer = 0.0

    def enter(self, previous_state: str):
        self._timer = HURT_DURATION
        self.owner.camera_controller.add_shake(0.5)

    def process_state(self, delta: float):
        player = self.owner

        # Slow to a stop during hurt stun
        player.decelerate_horizontal(delta, HURT_DECEL)

        self._timer -= delta
        if self._timer <= 0.0:
            if player.health.is_dead:
                self.transition_to("Dead")
            elif player.get_camera_relative_input().length() > INPUT_DEADZONE:
                self.transition_to("Run")
            else:
                self.transition_to("Idle")
