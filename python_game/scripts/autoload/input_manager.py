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
        # GDScript mouse_sensitivity = 0.002 rad/px ≈ 0.1146 deg/px.
        # Ursina mouse.velocity is in normalised screen space (delta / window_width).
        # At 1920 px wide: 1 px → 0.000521 velocity units, so the equivalent
        # Ursina sensitivity would be ≈ 220.  The value below is empirically
        # calibrated for feel; adjust via the pause menu sensitivity slider.
        self.mouse_sensitivity = 40.0
        self.stick_sensitivity = 3.0
        self.stick_deadzone = 0.2
        self.invert_y_mouse = False
        self.invert_y_controller = False
        self.aim_assist_strength = 0.5
        self.vibration_intensity = 0.7
        self.sprint_is_toggle = False
        self.auto_center_camera = True

        # Glyph mappings for UI prompts (KB+M)
        self._kb_glyphs: dict[str, str] = {
            "jump":         "Space",
            "dodge":        "Ctrl",
            "interact":     "E",
            "reload":       "R",
            "melee":        "V",
            "fire":         "LMB",
            "aim":          "RMB",
            "weapon_wheel": "Q",
            "item_wheel":   "Tab",
            "sprint":       "Shift",
            "pause":        "Esc",
        }

        # Glyph mappings for UI prompts (Xbox-style controller)
        self._controller_glyphs: dict[str, str] = {
            "jump":         "A",
            "dodge":        "B",
            "interact":     "X",
            "reload":       "X",
            "melee":        "Y",
            "fire":         "RT",
            "aim":          "LT",
            "weapon_wheel": "LB",
            "item_wheel":   "RB",
            "sprint":       "L3",
            "pause":        "Start",
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

    def get_action_glyph(self, action_name: str) -> str:
        """Return the display label for an action based on the active device."""
        if self.is_controller():
            return self._controller_glyphs.get(action_name, action_name)
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
        """Returns camera look input from controller right stick.

        Reads joy axes 2/3 (right stick X/Y) via pygame, applies deadzone
        and stick_sensitivity.  Returns Vec2(0,0) on KB+M or if no joystick
        is connected.
        """
        try:
            import pygame
            if pygame.joystick.get_count() > 0:
                js = pygame.joystick.Joystick(0)
                raw_x = js.get_axis(2)   # right stick X
                raw_y = js.get_axis(3)   # right stick Y
                if abs(raw_x) < self.stick_deadzone:
                    raw_x = 0.0
                if abs(raw_y) < self.stick_deadzone:
                    raw_y = 0.0
                if self.invert_y_controller:
                    raw_y *= -1
                return Vec2(raw_x * self.stick_sensitivity,
                            raw_y * self.stick_sensitivity)
        except Exception:
            pass
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
        # Platform rumble call goes here, e.g.:
        #   joystick.rumble(_low * _strength, _high * _strength, int(_dur * 1000))


# Global singleton
input_manager = _InputManager()
