"""Reusable health component. Attach to any damageable entity.
Handles HP tracking, damage application, death, and i-frames.
"""
from scripts.autoload.event_bus import event_bus, DAMAGE_DEALT, ENTITY_DIED


class HealthComponent:
    """Reusable HP system."""

    def __init__(self, max_hp: float = 100.0, iframe_duration: float = 0.0):
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.is_dead = False
        self.iframe_duration = iframe_duration
        self._iframe_timer = 0.0
        self.owner = None  # Set by the entity that owns this component

        # TODO(migration): Single-callback pattern only supports one listener per event.
        # GDScript signals support multiple connections. Use a list of callbacks or emit
        # through EventBus so multiple systems (HUD, camera shake, etc.) can all react.
        # Callbacks
        self.on_health_changed = None  # (current, maximum)
        self.on_died = None  # ()
        self.on_damage_taken = None  # (damage_info)

    def update(self, delta: float):
        if self._iframe_timer > 0.0:
            self._iframe_timer -= delta

    def take_damage(self, damage_info):
        # TODO(migration): No invincibility check. GDScript player sets is_invincible=True
        # during dodge, but this method never checks owner.is_invincible. Add:
        #   if hasattr(self.owner, 'is_invincible') and self.owner.is_invincible: return
        # TODO(migration): No re-entrancy guard. on_died callback could trigger another
        # take_damage call before this one returns (e.g. explosion chain). Add a
        # _processing_damage flag to prevent nested calls.
        if self.is_dead:
            return
        if self._iframe_timer > 0.0:
            return

        self.current_hp -= damage_info.amount
        self.current_hp = max(self.current_hp, 0.0)

        if self.iframe_duration > 0.0:
            self._iframe_timer = self.iframe_duration

        if self.on_health_changed:
            self.on_health_changed(self.current_hp, self.max_hp)
        if self.on_damage_taken:
            self.on_damage_taken(damage_info)
        event_bus.emit(DAMAGE_DEALT, damage_info)

        if self.current_hp <= 0.0:
            self.is_dead = True
            if self.on_died:
                self.on_died()
            event_bus.emit(ENTITY_DIED, self.owner, damage_info.source)

    def heal(self, amount: float):
        if self.is_dead:
            return
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        if self.on_health_changed:
            self.on_health_changed(self.current_hp, self.max_hp)

    def reset(self):
        self.current_hp = self.max_hp
        self.is_dead = False
        self._iframe_timer = 0.0
        if self.on_health_changed:
            self.on_health_changed(self.current_hp, self.max_hp)

    def get_hp_percent(self) -> float:
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0.0

    def get_save_data(self) -> dict:
        return {
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "is_dead": self.is_dead,
        }

    def load_save_data(self, data: dict):
        self.current_hp = data.get("current_hp", self.max_hp)
        self.max_hp = data.get("max_hp", self.max_hp)
        self.is_dead = data.get("is_dead", False)
        if self.on_health_changed:
            self.on_health_changed(self.current_hp, self.max_hp)
