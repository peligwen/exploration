"""Enemy Dead state — die and despawn."""
from ursina import Vec3, destroy
from scripts.autoload.game_manager import game_manager
from scripts.components.state import State


class EnemyDead(State):
    def __init__(self):
        super().__init__("Dead")
        self._despawn_timer = 3.0

    def enter(self, previous_state: str):
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
            # TODO(migration): destroy() removes the entity but state machine and state
            # objects still hold references to self.owner. On the next frame, state_machine.
            # update() will call self.current_state.process_state() on this dead state whose
            # self.owner is now destroyed. Guard against this by setting state_machine.
            # current_state = None before destroying, or disable updates on the owner first.
            destroy(self.owner)
