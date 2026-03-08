"""Pause menu overlay with settings."""
from ursina import (Entity, Text, Button, Slider, camera, color, mouse,
                    application, Vec2, destroy)

from scripts.autoload.input_manager import input_manager
from scripts.autoload.game_manager import game_manager


class PauseMenu:
    """Pause menu with settings controls."""

    def __init__(self):
        self.is_open = False
        self._entities = []

        # Build UI elements (initially hidden)
        self._build_ui()
        self.hide()

    def _build_ui(self):
        # Background overlay
        self.background = Entity(
            parent=camera.ui,
            model='quad',
            color=color.hsv(0, 0, 0, 0.7),
            scale=(2, 2),
            z=-0.1,
        )
        self._entities.append(self.background)

        # Title
        self.title = Text(
            text="PAUSED",
            position=(0, 0.35),
            origin=(0, 0),
            scale=3,
            parent=camera.ui,
        )
        self._entities.append(self.title)

        # Resume button
        self.resume_button = Button(
            text="Resume",
            position=(0, 0.2),
            scale=(0.3, 0.06),
            parent=camera.ui,
            on_click=self.toggle_pause,
        )
        self._entities.append(self.resume_button)

        # Sensitivity slider
        self.sens_label = Text(
            text=f"Sensitivity: {input_manager.mouse_sensitivity:.0f}",
            position=(0, 0.1),
            origin=(0, 0),
            scale=1,
            parent=camera.ui,
        )
        self._entities.append(self.sens_label)

        self.sens_slider = Slider(
            min=5, max=100, default=input_manager.mouse_sensitivity,
            position=(-0.15, 0.05),
            scale=(0.6, 0.8),
            parent=camera.ui,
            dynamic=True,
        )
        self.sens_slider.on_value_changed = self._on_sensitivity_changed
        self._entities.append(self.sens_slider)

        # TODO(migration): Missing settings controls that exist in GDScript version:
        # - Aim assist strength slider (input_manager.aim_assist_strength)
        # - Vibration intensity slider (input_manager.vibration_intensity)
        # - Invert Y-axis toggle (input_manager.invert_y_mouse / invert_y_controller)
        # Add these controls matching the GDScript pause_menu.gd implementation.

        # Quit button
        self.quit_button = Button(
            text="Quit",
            position=(0, -0.15),
            scale=(0.3, 0.06),
            color=color.hsv(0, 0.8, 0.5),
            parent=camera.ui,
            on_click=application.quit,
        )
        self._entities.append(self.quit_button)

    def toggle_pause(self):
        if self.is_open:
            self.hide()
            game_manager.set_paused(False)
            mouse.locked = True
            mouse.visible = False
        else:
            self.show()
            game_manager.set_paused(True)
            mouse.locked = False
            mouse.visible = True
        # TODO(migration): is_open is toggled AFTER show()/hide() calls. If show()/hide()
        # trigger callbacks that check self.is_open, they'll see stale state. Toggle first,
        # then call show/hide, or use separate open()/close() methods.
        self.is_open = not self.is_open

    def show(self):
        for e in self._entities:
            e.enabled = True

    def hide(self):
        for e in self._entities:
            e.enabled = False

    def _on_sensitivity_changed(self):
        val = self.sens_slider.value
        input_manager.mouse_sensitivity = val
        self.sens_label.text = f"Sensitivity: {val:.0f}"
