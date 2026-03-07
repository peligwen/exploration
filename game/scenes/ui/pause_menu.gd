class_name PauseMenu
extends CanvasLayer
## Pause menu overlay. Handles pause/unpause and settings.

@onready var panel: PanelContainer = $CenterContainer/PanelContainer
@onready var resume_button: Button = $CenterContainer/PanelContainer/VBoxContainer/ResumeButton
@onready var sensitivity_slider: HSlider = $CenterContainer/PanelContainer/VBoxContainer/SettingsContainer/SensitivitySlider
@onready var aim_assist_slider: HSlider = $CenterContainer/PanelContainer/VBoxContainer/SettingsContainer/AimAssistSlider
@onready var vibration_slider: HSlider = $CenterContainer/PanelContainer/VBoxContainer/SettingsContainer/VibrationSlider
@onready var invert_y_check: CheckBox = $CenterContainer/PanelContainer/VBoxContainer/SettingsContainer/InvertYCheck
@onready var quit_button: Button = $CenterContainer/PanelContainer/VBoxContainer/QuitButton

var _is_open: bool = false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false

	resume_button.pressed.connect(_on_resume)
	quit_button.pressed.connect(_on_quit)
	sensitivity_slider.value_changed.connect(_on_sensitivity_changed)
	aim_assist_slider.value_changed.connect(_on_aim_assist_changed)
	vibration_slider.value_changed.connect(_on_vibration_changed)
	invert_y_check.toggled.connect(_on_invert_y_toggled)

	# Set initial values from InputManager
	sensitivity_slider.value = InputManager.stick_sensitivity
	aim_assist_slider.value = InputManager.aim_assist_strength
	vibration_slider.value = InputManager.vibration_intensity
	invert_y_check.button_pressed = InputManager.invert_y_controller


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		toggle_pause()
		get_viewport().set_input_as_handled()


func toggle_pause() -> void:
	_is_open = not _is_open
	visible = _is_open
	GameManager.set_paused(_is_open)

	if _is_open:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		resume_button.grab_focus() # Controller navigation
	else:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _on_resume() -> void:
	toggle_pause()


func _on_quit() -> void:
	get_tree().quit()


func _on_sensitivity_changed(value: float) -> void:
	InputManager.stick_sensitivity = value
	InputManager.mouse_sensitivity = value * 0.001


func _on_aim_assist_changed(value: float) -> void:
	InputManager.aim_assist_strength = value


func _on_vibration_changed(value: float) -> void:
	InputManager.vibration_intensity = value


func _on_invert_y_toggled(pressed: bool) -> void:
	InputManager.invert_y_controller = pressed
	InputManager.invert_y_mouse = pressed
