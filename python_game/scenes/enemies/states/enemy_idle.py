"""Enemy Idle state — wait, check for player."""
from ursina import Vec3
import random
from scripts.components.state import State


class EnemyIdle(State):
    def __init__(self):
        super().__init__("Idle")
        self._idle_timer = 0.0

    def enter(self, previous_state: str, msg: dict = None):
        self._idle_timer = random.uniform(1.0, 3.0)
        self.owner.velocity.x = 0
        self.owner.velocity.z = 0

    def process_state(self, delta: float):
        if self.owner.can_see_target():
            self.transition_to("Chase")
            return

        self._idle_timer -= delta
        if self._idle_timer <= 0.0 and len(self.owner.patrol_points) > 0:
            self.transition_to("Patrol")
