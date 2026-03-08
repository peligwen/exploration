"""Singleton that wraps all input handling.
Tracks device type, manages settings, provides glyph lookup.
Uses Ursina's held_keys and input system.
"""
from ursina import held_keys, Vec2, mouse
from enum import Enum


class DeviceType(Enum):
    KB_MOUSE = 0
    CONTROLLER = 1


class _InputManager:
    """Singleton input manager."""

    def __init__(self):
        self.current_device = DeviceType.KB_MOUSE

        # Input settings
        self.mouse_sensitivity = 40.0
        self.stick_sensitivity = 3.0
        self.stick_deadzone = 0.2
        self.invert_y_mouse = False
        self.invert_y_controller = False
        self.aim_assist_strength = 0.5
        self.vibration_intensity = 0.7
        self.sprint_is_toggle = False
        self.auto_center_camera = True

        # Glyph mappings for UI prompts
        self._kb_glyphs = {
            "jump": "Space",
            "dodge": "Ctrl",
            "interact": "E",
            "reload": "R",
            "melee": "V",
            "fire": "LMB",
            "aim": "RMB",
            "weapon_wheel": "Q",
            "item_wheel": "Tab",
            "sprint": "Shift",
            "pause": "Esc",
        }

    def is_controller(self) -> bool:
        return self.current_device == DeviceType.CONTROLLER

    def get_action_glyph(self, action_name: str) -> str:
        return self._kb_glyphs.get(action_name, action_name)

    def get_move_vector(self) -> Vec2:
        """Returns movement input as Vec2 (x=right, y=forward)."""
        x = float(held_keys['d']) - float(held_keys['a'])
        y = float(held_keys['w']) - float(held_keys['s'])
        return Vec2(x, y)

    def get_look_vector(self) -> Vec2:
        """Returns camera look input. For KB+M, mouse delta is handled separately."""
        return Vec2(0, 0)


# Global singleton
input_manager = _InputManager()
