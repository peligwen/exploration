"""In-game HUD — health bar, ammo display, crosshair, state debug."""
from ursina import Text, Entity, camera, color, Vec2
import math

from scripts.autoload.event_bus import event_bus, PLAYER_HEALTH_CHANGED, PLAYER_AMMO_CHANGED
from scripts.autoload.input_manager import input_manager


class HUD:
    """In-game HUD overlay."""

    def __init__(self):
        # Health bar background
        self.health_bar_bg = Entity(
            parent=camera.ui,
            model='quad',
            color=color.color(0, 0, 0.15),
            scale=(0.3, 0.03),
            position=(-0.55, 0.45),
        )

        # Health bar fill
        self.health_bar = Entity(
            parent=camera.ui,
            model='quad',
            color=color.green,
            scale=(0.3, 0.03),
            position=(-0.55, 0.45),
            origin=(-0.5, 0),
        )

        # Health text
        self.health_label = Text(
            text="100 / 100",
            position=(-0.55, 0.46),
            scale=0.8,
            parent=camera.ui,
        )

        # Ammo text
        self.ammo_label = Text(
            text="30 / 30",
            position=(-0.65, 0.40),
            scale=0.8,
            parent=camera.ui,
        )
        self.ammo_prefix = Text(
            text="Ammo:",
            position=(-0.7, 0.40),
            scale=0.8,
            parent=camera.ui,
        )

        # Crosshair
        self.crosshair = Text(
            text="+",
            position=(0, 0),
            origin=(0, 0),
            scale=2,
            parent=camera.ui,
        )

        # State debug label (top right)
        self.state_label = Text(
            text="Idle",
            position=(0.6, 0.45),
            scale=0.8,
            parent=camera.ui,
        )

        # TODO(migration): Missing device_changed handler. GDScript HUD listens for
        # InputManager.device_changed signal to swap button prompts between controller
        # glyphs and KB+M labels. Add a callback that updates any input hint text when
        # the active device changes.

        # Connect signals
        event_bus.connect(PLAYER_HEALTH_CHANGED, self._on_health_changed)
        event_bus.connect(PLAYER_AMMO_CHANGED, self._on_ammo_changed)

    def _on_health_changed(self, current: float, maximum: float):
        ratio = current / maximum if maximum > 0 else 0
        self.health_bar.scale_x = 0.3 * ratio
        self.health_label.text = f"{math.ceil(current)} / {math.ceil(maximum)}"

        if ratio < 0.25:
            self.health_bar.color = color.red
        elif ratio < 0.5:
            self.health_bar.color = color.orange
        else:
            self.health_bar.color = color.green

    def _on_ammo_changed(self, current: int, max_ammo: int):
        self.ammo_label.text = f"{current} / {max_ammo}"
        if current == 0:
            self.ammo_label.color = color.red
        elif current <= max_ammo * 0.25:
            self.ammo_label.color = color.orange
        else:
            self.ammo_label.color = color.white

    def update_state_debug(self, state_name: str):
        self.state_label.text = state_name
