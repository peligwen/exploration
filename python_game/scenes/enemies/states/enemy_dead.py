"""Enemy Dead state — die and despawn."""
from ursina import Vec3, destroy
from scripts.autoload.game_manager import game_manager
from scripts.components.state import State


class EnemyDead(State):
    def __init__(self):
        super().__init__("Dead")
        self._despawn_timer = 3.0

    def enter(self, previous_state: str, msg: dict = None):
        self._despawn_timer = 3.0
        self.owner.velocity = Vec3(0, 0, 0)
        # Disable collision
        self.owner.collider = None

    def process_state(self, delta: float):
        self._despawn_timer -= delta
        # Sink into ground
        if self._despawn_timer < 1.0:
            self.owner.y -= delta * 0.5
        if self._despawn_timer <= 0.0:
            game_manager.unregister_saveable(self.owner)
            self.owner.state_machine.current_state = None
            destroy(self.owner)
