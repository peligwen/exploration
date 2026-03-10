"""Singleton that wraps all input handling.
Tracks device type, manages settings, provides glyph lookup.
Uses Ursina's held_keys and input system.
"""
from ursina import held_keys, Vec2
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

# KB+M keys held for each logical action.
_KB_ACTION_MAP: dict[str, str] = {
    "fire":    "left mouse",
    "aim":     "right mouse",
    "jump":    "space",
    "dodge":   "left control",
    "sprint":  "left shift",
    "interact": "e",
    "reload":  "r",
    "melee":   "v",
    "pause":   "escape",
}

# Gamepad button names as reported by Ursina/Panda3D held_keys.
# Triggers (fire/aim) are checked via pygame axes in is_action_held()
# because Panda3D treats them as analog axes, not digital buttons.
_PAD_ACTION_MAP: dict[str, str] = {
    "jump":    "gamepad face a",
    "dodge":   "gamepad face b",
    "reload":  "gamepad face x",
    "interact": "gamepad face x",
    "melee":   "gamepad face y",
    "sprint":  "gamepad left thumb",
    "pause":   "gamepad start",
}

# Maps Ursina gamepad key-press strings to their KB equivalent so that
# player.input() can forward them to state handle_input() unchanged.
CONTROLLER_KEY_MAP: dict[str, str] = {
    "gamepad face a":     "space",
    "gamepad face b":     "left control",
    "gamepad face x":     "e",
    "gamepad face y":     "v",
    "gamepad left thumb": "left shift",
    "gamepad start":      "escape",
    # Triggers handled via analog axis, mapped to mouse button strings
    # when they cross the press threshold (see player.py _controller_trigger).
}


class _InputManager:
    """Singleton input manager."""

    def __init__(self):
        self.current_device = DeviceType.KB_MOUSE
        self._device_changed_callbacks: list[Callable[[DeviceType], None]] = []

        # Input settings
        # GDScript sensitivity = 0.002 rad/px ≈ 0.1146 deg/px.
        # Ursina mouse.velocity is normalised screen space.
        # Empirically calibrated; adjust via pause menu.
        self.mouse_sensitivity = 40.0
        self.stick_sensitivity = 3.0
        self.stick_deadzone = 0.2
        # Axis value at which a trigger counts as "held"
        self.trigger_threshold = 0.5
        self.invert_y_mouse = False
        self.invert_y_controller = False
        self.aim_assist_strength = 0.5
        self.vibration_intensity = 0.7
        self.sprint_is_toggle = False
        self.auto_center_camera = True

        # Initialise pygame joystick subsystem for analog stick / trigger
        # reading.  Only the joystick module is needed — avoid full
        # pygame.init() to prevent conflicts with Ursina's window.
        self._joystick = None
        try:
            import pygame
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self._joystick = pygame.joystick.Joystick(0)
                self._joystick.init()
        except Exception:
            pass

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

    def on_device_changed(
            self, callback: Callable[[DeviceType], None],
    ) -> None:
        """Register a device-changed callback."""
        self._device_changed_callbacks.append(callback)

    def notify_input(self, source: DeviceType) -> None:
        """Switch current_device and fire callbacks if needed."""
        if source != self.current_device:
            self.current_device = source
            for cb in self._device_changed_callbacks:
                cb(self.current_device)

    # ------------------------------------------------------------------
    # Glyph lookup
    # ------------------------------------------------------------------

    def get_action_glyph(self, action_name: str) -> str:
        """Return display label for an action."""
        if self.is_controller():
            return self._controller_glyphs.get(action_name, action_name)
        return self._kb_glyphs.get(action_name, action_name)

    # ------------------------------------------------------------------
    # Joystick helper
    # ------------------------------------------------------------------

    def _get_joystick(self):
        """Return the cached pygame Joystick, or None.

        Pumps pygame events so axis values stay fresh.  Re-checks for
        newly connected controllers when no joystick is cached.
        """
        try:
            import pygame
            pygame.event.pump()
            if self._joystick is not None:
                return self._joystick
            # Check for hot-plugged controller
            if pygame.joystick.get_count() > 0:
                self._joystick = pygame.joystick.Joystick(0)
                self._joystick.init()
                return self._joystick
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Action queries — use instead of held_keys directly
    # ------------------------------------------------------------------

    def is_action_held(self, action_name: str) -> bool:
        """True if KB+M or controller binding is held.

        Checks held_keys for buttons and pygame axes
        for triggers (fire=RT axis 5, aim=LT axis 2).
        """
        kb_key = _KB_ACTION_MAP.get(action_name)
        if kb_key and held_keys.get(kb_key, 0):
            return True

        pad_key = _PAD_ACTION_MAP.get(action_name)
        if pad_key and held_keys.get(pad_key, 0):
            return True

        # Analog triggers must be read as axes
        if action_name in ("fire", "aim"):
            js = self._get_joystick()
            if js is not None:
                # Xbox layout: LT = axis 2, RT = axis 5
                axis = 5 if action_name == "fire" else 2
                return js.get_axis(axis) > self.trigger_threshold

        return False

    # ------------------------------------------------------------------
    # Movement / look vectors
    # ------------------------------------------------------------------

    def get_move_vector(self) -> Vec2:
        """Returns movement input as Vec2 (x=right, y=forward).

        Prefers KB input; falls back to controller left stick (axes 0/1).
        Calls notify_input() to keep device tracking up to date.
        """
        x = float(held_keys['d']) - float(held_keys['a'])
        y = float(held_keys['w']) - float(held_keys['s'])
        if x != 0.0 or y != 0.0:
            self.notify_input(DeviceType.KB_MOUSE)
            return Vec2(x, y)

        js = self._get_joystick()
        if js is not None:
            sx = js.get_axis(0)           # left stick X
            sy = -js.get_axis(1)          # left stick Y (up = negative)
            if abs(sx) < self.stick_deadzone:
                sx = 0.0
            if abs(sy) < self.stick_deadzone:
                sy = 0.0
            if sx != 0.0 or sy != 0.0:
                self.notify_input(DeviceType.CONTROLLER)
                return Vec2(sx, sy)

        return Vec2(0.0, 0.0)

    def get_look_vector(self) -> Vec2:
        """Returns camera look input from controller right stick (axes 2/3).

        Applies deadzone, stick_sensitivity, and invert_y_controller.
        Returns Vec2(0,0) on KB+M or when no joystick is connected.
        Calls notify_input() when non-zero input is detected.
        """
        js = self._get_joystick()
        if js is not None:
            raw_x = js.get_axis(2)   # right stick X
            raw_y = js.get_axis(3)   # right stick Y
            if abs(raw_x) < self.stick_deadzone:
                raw_x = 0.0
            if abs(raw_y) < self.stick_deadzone:
                raw_y = 0.0
            if raw_x != 0.0 or raw_y != 0.0:
                self.notify_input(DeviceType.CONTROLLER)
                if self.invert_y_controller:
                    raw_y *= -1
                return Vec2(raw_x * self.stick_sensitivity,
                            raw_y * self.stick_sensitivity)
        return Vec2(0, 0)

    # ------------------------------------------------------------------
    # Haptic feedback
    # ------------------------------------------------------------------

    def request_haptic(self, pattern_name: str,
                       intensity_scale: float = 1.0
                       ) -> None:
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
        _strength = self.vibration_intensity * intensity_scale  # noqa: F841
        # Platform rumble call goes here, e.g.:
        #   joystick.rumble(
        #       _low * _strength, _high * _strength,
        #       int(_dur * 1000)
        #   )


# Global singleton
input_manager = _InputManager()
