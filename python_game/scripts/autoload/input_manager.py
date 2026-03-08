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
        # TODO(migration): GDScript uses mouse_sensitivity = 0.002 (radians per pixel).
        # This value of 40.0 is on a completely different scale. Verify Ursina's mouse
        # delta units and calibrate so camera rotation feels equivalent to the Godot version.
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
        # TODO(migration): Only KB glyphs exist. GDScript version has full controller glyph
        # mappings (A/B/X/Y, triggers, bumpers, sticks). Add _controller_glyphs dict and
        # return the right set based on self.current_device.
        return self._kb_glyphs.get(action_name, action_name)

    def get_move_vector(self) -> Vec2:
        """Returns movement input as Vec2 (x=right, y=forward)."""
        x = float(held_keys['d']) - float(held_keys['a'])
        y = float(held_keys['w']) - float(held_keys['s'])
        return Vec2(x, y)

    def get_look_vector(self) -> Vec2:
        """Returns camera look input. For KB+M, mouse delta is handled separately."""
        # TODO(migration): This is a stub — always returns zero. GDScript version reads
        # controller right stick (joy_axis 2/3) with deadzone and sensitivity applied.
        # Controller camera look is completely non-functional without this.
        return Vec2(0, 0)

    # TODO(migration): Missing device_changed callback/signal. GDScript emits device_changed
    # when input source switches between KB+M and controller. UI elements (HUD, pause menu)
    # need this to swap button prompts. Implement device detection in an input handler.

    # TODO(migration): Missing request_haptic() method. GDScript version supports named
    # haptic patterns (fire, damage, explosion, heartbeat, radial_tick) scaled by
    # vibration_intensity setting. Implement using Ursina's gamepad rumble API if available,
    # or stub it out with pass for now.


# Global singleton
input_manager = _InputManager()
