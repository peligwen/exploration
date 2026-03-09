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

        # Aim assist strength slider
        self.aim_label = Text(
            text=f"Aim Assist: {input_manager.aim_assist_strength:.0%}",
            position=(0, -0.02),
            origin=(0, 0),
            scale=1,
            parent=camera.ui,
        )
        self._entities.append(self.aim_label)

        self.aim_slider = Slider(
            min=0, max=1, default=input_manager.aim_assist_strength,
            position=(-0.15, -0.07),
            scale=(0.6, 0.8),
            parent=camera.ui,
            dynamic=True,
        )
        self.aim_slider.on_value_changed = self._on_aim_assist_changed
        self._entities.append(self.aim_slider)

        # Vibration intensity slider
        self.vib_label = Text(
            text=f"Vibration: {input_manager.vibration_intensity:.0%}",
            position=(0, -0.14),
            origin=(0, 0),
            scale=1,
            parent=camera.ui,
        )
        self._entities.append(self.vib_label)

        self.vib_slider = Slider(
            min=0, max=1, default=input_manager.vibration_intensity,
            position=(-0.15, -0.19),
            scale=(0.6, 0.8),
            parent=camera.ui,
            dynamic=True,
        )
        self.vib_slider.on_value_changed = self._on_vibration_changed
        self._entities.append(self.vib_slider)

        # Invert Y-axis toggle
        self._invert_y_text = self._invert_label()
        self.invert_y_button = Button(
            text=self._invert_y_text,
            position=(0, -0.28),
            scale=(0.35, 0.06),
            parent=camera.ui,
            on_click=self._on_invert_y_toggled,
        )
        self._entities.append(self.invert_y_button)

        # Quit button
        self.quit_button = Button(
            text="Quit",
            position=(0, -0.37),
            scale=(0.3, 0.06),
            color=color.hsv(0, 0.8, 0.5),
            parent=camera.ui,
            on_click=application.quit,
        )
        self._entities.append(self.quit_button)

    def toggle_pause(self):
        self.is_open = not self.is_open
        if not self.is_open:
            self.hide()
            game_manager.set_paused(False)
            mouse.locked = True
            mouse.visible = False
        else:
            self.show()
            game_manager.set_paused(True)
            mouse.locked = False
            mouse.visible = True

    def show(self):
        for e in self._entities:
            e.enabled = True

    def hide(self):
        for e in self._entities:
            e.enabled = False

    def _invert_label(self) -> str:
        state = "ON" if input_manager.invert_y_mouse else "OFF"
        return f"Invert Y: {state}"

    def _on_sensitivity_changed(self):
        val = self.sens_slider.value
        input_manager.mouse_sensitivity = val
        self.sens_label.text = f"Sensitivity: {val:.0f}"

    def _on_aim_assist_changed(self):
        val = self.aim_slider.value
        input_manager.aim_assist_strength = val
        self.aim_label.text = f"Aim Assist: {val:.0%}"

    def _on_vibration_changed(self):
        val = self.vib_slider.value
        input_manager.vibration_intensity = val
        self.vib_label.text = f"Vibration: {val:.0%}"

    def _on_invert_y_toggled(self):
        input_manager.invert_y_mouse = not input_manager.invert_y_mouse
        input_manager.invert_y_controller = input_manager.invert_y_mouse
        self.invert_y_button.text = self._invert_label()
