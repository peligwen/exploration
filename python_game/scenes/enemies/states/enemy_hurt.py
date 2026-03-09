"""Enemy Hurt state — brief stun after taking damage."""
from scripts.components.state import State

HURT_DURATION = 0.3


class EnemyHurt(State):
    def __init__(self):
        super().__init__("Hurt")
        self._timer = 0.0

    def enter(self, previous_state: str, msg: dict = None):
        self._timer = HURT_DURATION
        self.owner.velocity.x = 0
        self.owner.velocity.z = 0

    def process_state(self, delta: float):
        self._timer -= delta
        if self._timer <= 0.0:
            if self.owner.health.is_dead:
                self.transition_to("Dead")
            elif self.owner.can_see_target():
                self.transition_to("Chase")
            else:
                self.transition_to("Idle")
