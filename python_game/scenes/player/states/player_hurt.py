"""Player Hurt state — brief stun after taking damage."""
from scripts.components.state import State

HURT_DURATION = 0.3


class PlayerHurt(State):
    def __init__(self):
        super().__init__("Hurt")
        self._timer = 0.0

    def enter(self, previous_state: str):
        self._timer = HURT_DURATION
        self.owner.camera_controller.add_shake(0.5)

    def process_state(self, delta: float):
        player = self.owner
        player.apply_gravity(delta)

        # Slow to a stop during hurt stun
        player.velocity.x *= max(0, 1.0 - 20.0 * delta)
        player.velocity.z *= max(0, 1.0 - 20.0 * delta)

        self._timer -= delta
        if self._timer <= 0.0:
            if player.health.is_dead:
                self.transition_to("Dead")
            elif player.get_camera_relative_input().length() > 0.1:
                self.transition_to("Run")
            else:
                self.transition_to("Idle")
