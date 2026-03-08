"""Global signal bus for cross-system communication.
Systems connect to these signals instead of calling each other directly.
"""
from collections import defaultdict


class _EventBus:
    """Singleton event bus using callback-based signals."""

    def __init__(self):
        self._listeners = defaultdict(list)

    def connect(self, signal_name: str, callback):
        """Connect a callback to a signal."""
        if callback not in self._listeners[signal_name]:
            self._listeners[signal_name].append(callback)

    def disconnect(self, signal_name: str, callback):
        """Disconnect a callback from a signal."""
        if callback in self._listeners[signal_name]:
            self._listeners[signal_name].remove(callback)

    def emit(self, signal_name: str, *args, **kwargs):
        """Emit a signal, calling all connected callbacks."""
        for callback in self._listeners[signal_name]:
            callback(*args, **kwargs)


# Signal name constants
DAMAGE_DEALT = "damage_dealt"
ENTITY_DIED = "entity_died"
ITEM_PICKED_UP = "item_picked_up"
WEAPON_SWITCHED = "weapon_switched"
QUEST_UPDATED = "quest_updated"
PLAYER_LEVELED_UP = "player_leveled_up"
XP_GAINED = "xp_gained"
ZONE_ENTERED = "zone_entered"
DESTRUCTIBLE_BROKEN = "destructible_broken"
PLAYER_HEALTH_CHANGED = "player_health_changed"
PLAYER_AMMO_CHANGED = "player_ammo_changed"
PLAYER_DIED = "player_died"
PLAYER_RESPAWNED = "player_respawned"

# Global singleton
event_bus = _EventBus()
