"""Enemy Patrol state — walk between patrol points."""
from scripts.components.state import State


class EnemyPatrol(State):
    def __init__(self):
        super().__init__("Patrol")
        self._current_point_index = 0
        self._wait_timer = 0.0
        self._waiting = False

    def enter(self, previous_state: str, msg: dict = None):
        self._waiting = False
        if len(self.owner.patrol_points) == 0:
            self.transition_to("Idle")

    def process_state(self, delta: float):
        enemy = self.owner

        if enemy.can_see_target():
            self.transition_to("Chase")
            return

        if len(enemy.patrol_points) == 0:
            self.transition_to("Idle")
            return

        if self._waiting:
            self._wait_timer -= delta
            enemy.velocity.x = 0
            enemy.velocity.z = 0
            if self._wait_timer <= 0.0:
                self._waiting = False
                n = len(enemy.patrol_points)
                self._current_point_index = (
                    self._current_point_index + 1) % n
            return

        target_point = enemy.patrol_points[self._current_point_index]
        dist = (enemy.position - target_point).length()

        if dist < 1.0:
            self._waiting = True
            self._wait_timer = enemy.patrol_wait_time
            return

        enemy.navigate_to(target_point, enemy.move_speed, delta)
