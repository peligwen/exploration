"""In-game HUD — health bar, ammo, crosshair, kills, damage numbers."""
from ursina import Text, Entity, camera, color, destroy
import math

from scripts.autoload.event_bus import (
    event_bus, PLAYER_HEALTH_CHANGED, PLAYER_AMMO_CHANGED,
    ENTITY_DIED, DAMAGE_DEALT,
)
from scripts.autoload.input_manager import input_manager


class HUD:
    """In-game HUD overlay."""

    def __init__(self):
        # Health bar background
        self.health_bar_bg = Entity(
            parent=camera.ui,
            model='quad',
            color=color.hsv(0, 0, 0.15),
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

        # Crosshair (4 lines + center dot)
        _line_len = 0.012
        _line_w = 0.002
        _gap = 0.005
        self._crosshair_parts = []
        for pos, scale in [
            ((0, _gap + _line_len / 2), (_line_w, _line_len)),       # top
            ((0, -(_gap + _line_len / 2)), (_line_w, _line_len)),    # bottom
            ((-(_gap + _line_len / 2), 0), (_line_len, _line_w)),    # left
            ((_gap + _line_len / 2, 0), (_line_len, _line_w)),       # right
        ]:
            part = Entity(parent=camera.ui, model='quad', color=color.white,
                          scale=scale, position=pos)
            self._crosshair_parts.append(part)
        # Center dot
        self._crosshair_parts.append(
            Entity(parent=camera.ui, model='quad', color=color.white,
                   scale=(_line_w, _line_w), position=(0, 0))
        )

        # Kill counter
        self._kill_count = 0
        self.kill_label = Text(
            text="Kills: 0",
            position=(0.55, 0.40),
            origin=(0, 0),
            scale=1,
            parent=camera.ui,
        )

        # State debug label (top right)
        self.state_label = Text(
            text="Idle",
            position=(0.6, 0.45),
            scale=0.8,
            parent=camera.ui,
        )

        # Cache last known ammo so the glyph can be refreshed on device switch
        self._last_ammo = 30
        self._last_max_ammo = 30

        # Connect signals
        event_bus.connect(PLAYER_HEALTH_CHANGED, self._on_health_changed)
        event_bus.connect(PLAYER_AMMO_CHANGED, self._on_ammo_changed)
        event_bus.connect(ENTITY_DIED, self._on_entity_died)
        event_bus.connect(DAMAGE_DEALT, self._on_damage_dealt)
        input_manager.on_device_changed(self._on_device_changed)

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

    def _on_device_changed(self, _device):
        """Refresh input hint glyphs whenever the active device switches."""
        self._on_ammo_changed(self._last_ammo, self._last_max_ammo)

    def _on_ammo_changed(self, current: int, max_ammo: int):
        self._last_ammo = current
        self._last_max_ammo = max_ammo
        if current == 0:
            reload_glyph = input_manager.get_action_glyph("reload")
            self.ammo_label.text = f"0 / {max_ammo} [{reload_glyph}]"
            self.ammo_label.color = color.red
        elif current <= max_ammo * 0.25:
            self.ammo_label.text = f"{current} / {max_ammo}"
            self.ammo_label.color = color.orange
        else:
            self.ammo_label.text = f"{current} / {max_ammo}"
            self.ammo_label.color = color.white

    def _on_entity_died(self, entity, source):
        from scenes.enemies.base_enemy import BaseEnemy
        if isinstance(entity, BaseEnemy):
            self._kill_count += 1
            self.kill_label.text = f"Kills: {self._kill_count}"

    def _on_damage_dealt(self, damage_info):
        hit_pos = damage_info.hit_position
        if hit_pos is None or hit_pos.length() < 0.01:
            return
        screen_pos = camera.world_to_screen_point(hit_pos)
        if screen_pos.z < 0:
            return
        # Ursina UI coords: x in [-0.5*aspect, 0.5*aspect],
        # y in [-0.5, 0.5]
        ui_x = (screen_pos.x - 0.5) * camera.ui.aspect_ratio
        ui_y = screen_pos.y - 0.5
        dmg_color = color.red if damage_info.is_critical else color.yellow
        dmg_text = Text(
            text=f"{damage_info.amount:.0f}",
            position=(ui_x, ui_y),
            origin=(0, 0),
            scale=2,
            color=dmg_color,
            parent=camera.ui,
        )
        dmg_text.animate_y(ui_y + 0.05, duration=0.6)
        dmg_text.animate('color', color.clear, duration=0.6)
        destroy(dmg_text, delay=0.7)

    def update_state_debug(self, state_name: str):
        self.state_label.text = state_name
