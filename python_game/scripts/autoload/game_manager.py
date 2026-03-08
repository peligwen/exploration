"""Singleton managing game state and saveable object registry."""
from enum import Enum


class GameState(Enum):
    PLAYING = 0
    PAUSED = 1
    MENU = 2
    DEAD = 3


class _GameManager:
    """Singleton game manager."""

    def __init__(self):
        self.state = GameState.PLAYING
        self._saveables: set = set()

    def register_saveable(self, obj):
        self._saveables.add(obj)

    def unregister_saveable(self, obj):
        self._saveables.discard(obj)

    def get_all_save_data(self) -> list:
        data = []
        for obj in self._saveables:
            if obj is not None and hasattr(obj, 'get_save_data'):
                data.append(obj.get_save_data())
        return data

    def set_paused(self, paused: bool):
        from ursina import application
        if paused:
            self.state = GameState.PAUSED
            application.paused = True
        else:
            self.state = GameState.PLAYING
            application.paused = False

    def is_playing(self) -> bool:
        return self.state == GameState.PLAYING


# Global singleton
game_manager = _GameManager()
