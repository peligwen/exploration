"""Singleton that wraps all input handling.
Tracks device type, manages settings, provides glyph lookup.
Uses Ursina's held_keys and input system.
"""
from ursina import held_keys, Vec2, mouse
from enum import Enum
from typing import Callable


class DeviceType(Enum):
    KB_MOUSE = 0
    CONTROLLER = 1


# Named haptic patterns scaled by vibration_intensity.
# Ursina has no gamepad rumble API, so these are stubs ready for a
# platform-specific backend (e.g. pygame.joystick.rumble).
_HAPTIC_PATTERNS: dict[str, tuple[float, float, float]] = {
    # name: (low_freq, high_freq, duration_sec)
    "fire":        (0.0,  0.6, 0.08),
    "damage":      (0.7,  0.4, 0.25),
    "explosion":   (1.0,  0.8, 0.5),
    "heartbeat":   (0.5,  0.0, 0.4),
    "radial_tick": (0.0,  0.3, 0.05),
}


class _InputManager:
    """Singleton input manager."""

    def __init__(self):
        self.current_device = DeviceType.KB_MOUSE
        self._device_changed_callbacks: list[Callable[[DeviceType], None]] = []

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

    # ------------------------------------------------------------------
    # Device detection
    # ------------------------------------------------------------------

    def on_device_changed(self, callback: Callable[[DeviceType], None]) -> None:
        """Register a callback invoked whenever the active input device changes."""
        self._device_changed_callbacks.append(callback)

    def notify_input(self, source: DeviceType) -> None:
        """Call from input handlers whenever a KB+M or controller event fires.
        Switches current_device and fires device_changed callbacks if needed."""
        if source != self.current_device:
            self.current_device = source
            for cb in self._device_changed_callbacks:
                cb(self.current_device)

    # ------------------------------------------------------------------
    # Glyph lookup
    # ------------------------------------------------------------------

    # TODO(migration): Only KB glyphs exist. GDScript version has full controller glyph
    # mappings (A/B/X/Y, triggers, bumpers, sticks). Add _controller_glyphs dict and
    # return the right set based on self.current_device.
    def get_action_glyph(self, action_name: str) -> str:
        return self._kb_glyphs.get(action_name, action_name)

    # ------------------------------------------------------------------
    # Movement / look vectors
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Haptic feedback
    # ------------------------------------------------------------------

    def request_haptic(self, pattern_name: str, intensity_scale: float = 1.0) -> None:
        """Play a named haptic pattern on the active controller.

        Patterns are defined in ``_HAPTIC_PATTERNS`` and scaled by both
        ``intensity_scale`` and the global ``vibration_intensity`` setting.
        Ursina has no built-in rumble API, so this is a documented stub:
        replace the body with a platform call (e.g. pygame.joystick.rumble)
        when controller support is added.

        Args:
            pattern_name: One of 'fire', 'damage', 'explosion', 'heartbeat',
                          'radial_tick'. Unknown names are silently ignored.
            intensity_scale: Per-call multiplier on top of vibration_intensity.
        """
        if not self.is_controller():
            return
        if pattern_name not in _HAPTIC_PATTERNS:
            return
        _low, _high, _dur = _HAPTIC_PATTERNS[pattern_name]
        _strength = self.vibration_intensity * intensity_scale
        # TODO: call platform rumble API here, e.g.:
        #   joystick.rumble(_low * _strength, _high * _strength, int(_dur * 1000))


# Global singleton
input_manager = _InputManager()
