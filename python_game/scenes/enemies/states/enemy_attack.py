"""Enemy Attack state — melee strike at player."""
from scripts.components.state import State


class EnemyAttack(State):
    def __init__(self):
        super().__init__("Attack")
        self._attack_timer = 0.0
        self._has_dealt_damage = False

    def enter(self, previous_state: str, msg: dict = None):
        self._attack_timer = self.owner.attack_cooldown
        self._has_dealt_damage = False
        self.owner.velocity.x = 0
        self.owner.velocity.z = 0

    def process_state(self, delta: float):
        enemy = self.owner
        enemy.face_target(delta)

        # Deal damage partway through attack
        halfway = enemy.attack_cooldown * 0.5
        if not self._has_dealt_damage and self._attack_timer < halfway:
            if enemy.is_in_attack_range():
                enemy.deal_damage_to_target()
            self._has_dealt_damage = True

        self._attack_timer -= delta
        if self._attack_timer <= 0.0:
            if enemy.is_in_attack_range():
                # Attack again
                self._attack_timer = enemy.attack_cooldown
                self._has_dealt_damage = False
            elif enemy.can_see_target():
                self.transition_to("Chase")
            else:
                self.transition_to("Idle")
