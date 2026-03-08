"""Enemy Chase state — navigate toward player."""
from scripts.components.state import State


class EnemyChase(State):
    def __init__(self):
        super().__init__("Chase")

    def process_state(self, delta: float):
        enemy = self.owner

        if not enemy.target:
            self.transition_to("Idle")
            return

        if enemy.is_in_attack_range():
            self.transition_to("Attack")
            return

        if not enemy.can_see_target():
            self.transition_to("Idle")
            return

        enemy.navigate_to(enemy.target.position, enemy.chase_speed, delta)
