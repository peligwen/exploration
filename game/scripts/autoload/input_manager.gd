class_name InputManagerClass
extends Node
## Singleton that wraps all input handling.
## Tracks device type, manages settings, provides glyph lookup, handles haptics.

signal device_changed(device_type: DeviceType)

enum DeviceType { KB_MOUSE, CONTROLLER }

var current_device: DeviceType = DeviceType.KB_MOUSE

# Input settings
var mouse_sensitivity: float = 0.002
var stick_sensitivity: float = 3.0
var stick_deadzone: float = 0.2
var invert_y_mouse: bool = false
var invert_y_controller: bool = false
var aim_assist_strength: float = 0.5 # 0.0 = off, 1.0 = max
var vibration_intensity: float = 0.7 # 0.0 = off, 1.0 = max
var sprint_is_toggle: bool = false
var auto_center_camera: bool = true

# Controller glyph names for UI prompts
var _controller_glyphs := {
	"jump": "A",
	"dodge": "B",
	"interact": "X",
	"reload": "X",
	"melee": "Y",
	"fire": "RT",
	"aim": "LT",
	"weapon_wheel": "RB",
	"item_wheel": "LB",
	"sprint": "L-Stick",
	"pause": "Start",
	"quick_swap_prev": "D-Left",
	"quick_swap_next": "D-Right",
}

var _kb_glyphs := {
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
	"quick_swap_prev": "Scroll Down",
	"quick_swap_next": "Scroll Up",
}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _input(event: InputEvent) -> void:
	var new_device := current_device
	if event is InputEventKey or event is InputEventMouseButton or event is InputEventMouseMotion:
		new_device = DeviceType.KB_MOUSE
	elif event is InputEventJoypadButton or event is InputEventJoypadMotion:
		if event is InputEventJoypadMotion and abs(event.axis_value) < stick_deadzone:
			return
		new_device = DeviceType.CONTROLLER

	if new_device != current_device:
		current_device = new_device
		device_changed.emit(current_device)


func is_controller() -> bool:
	return current_device == DeviceType.CONTROLLER


func get_action_glyph(action_name: String) -> String:
	if is_controller():
		return str(_controller_glyphs.get(action_name, action_name))
	return str(_kb_glyphs.get(action_name, action_name))


func get_look_vector() -> Vector2:
	## Returns camera look input as a normalized Vector2.
	## For mouse, this is handled separately via _unhandled_input mouse motion.
	## For controller, reads right stick axes.
	if is_controller():
		var look := Vector2(
			Input.get_axis("look_left", "look_right"),
			Input.get_axis("look_up", "look_down")
		)
		if look.length() < stick_deadzone:
			return Vector2.ZERO
		if invert_y_controller:
			look.y *= -1.0
		return look * stick_sensitivity
	return Vector2.ZERO


func get_move_vector() -> Vector2:
	## Returns movement input as a Vector2 (x = right, y = forward).
	return Vector2(
		Input.get_axis("move_left", "move_right"),
		Input.get_axis("move_forward", "move_back")
	)


func request_haptic(type: StringName, intensity: float = 1.0, duration: float = 0.2) -> void:
	## Request controller haptic feedback. Scales by user's vibration setting.
	if vibration_intensity <= 0.0 or not is_controller():
		return

	var scaled := intensity * vibration_intensity
	match type:
		&"fire":
			Input.start_joy_vibration(0, scaled * 0.3, scaled * 0.6, duration)
		&"damage":
			Input.start_joy_vibration(0, scaled * 0.6, scaled * 0.3, duration)
		&"explosion":
			Input.start_joy_vibration(0, scaled, scaled, duration)
		&"heartbeat":
			Input.start_joy_vibration(0, scaled * 0.2, 0.0, duration)
		&"radial_tick":
			Input.start_joy_vibration(0, scaled * 0.1, 0.0, 0.05)
		_:
			Input.start_joy_vibration(0, scaled * 0.5, scaled * 0.5, duration)
