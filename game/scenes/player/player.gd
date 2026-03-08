class_name Player
extends CharacterBody3D
## Player controller. Delegates behavior to the state machine.
## Provides shared state and utilities that all player states access.

const INPUT_DEADZONE: float = 0.1
const AIR_CONTROL_FACTOR: float = 0.8
const DECEL_FACTOR: float = 10.0

# Movement tuning
@export_group("Movement")
@export var move_speed: float = 6.0
@export var sprint_speed: float = 10.0
@export var aim_speed: float = 3.0
@export var jump_force: float = 8.0
@export var gravity: float = 20.0
@export var dodge_speed: float = 14.0
@export var dodge_duration: float = 0.4
@export var coyote_time: float = 0.1
@export var jump_buffer_time: float = 0.12

# Runtime state (shared between states)
var is_aiming: bool = false
var is_sprinting: bool = false
var is_dodging: bool = false
var is_invincible: bool = false
var current_speed: float = 0.0
var move_direction: Vector3 = Vector3.ZERO
var last_grounded_time: float = 0.0
var jump_buffer_timer: float = 0.0
var facing_direction: Vector3 = Vector3.FORWARD

# Node references
@onready var state_machine: StateMachine = $StateMachine
@onready var camera_controller: CameraController = $CameraController
@onready var health: HealthComponent = $HealthComponent
@onready var weapon_mount: Node3D = $Model/WeaponMount
@onready var model: Node3D = $Model

# Current weapon reference (set by weapon system)
var current_weapon: Node = null


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

	# Connect health signals
	health.health_changed.connect(_on_health_changed)
	health.died.connect(_on_died)

	# Register as saveable
	add_to_group("saveable")
	GameManager.register_saveable(self)


func _unhandled_input(event: InputEvent) -> void:
	# Mouse look (KB+Mouse mode)
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		var mouse_event: InputEventMouseMotion = event as InputEventMouseMotion
		var sensitivity := InputManager.mouse_sensitivity
		var motion: Vector2 = mouse_event.relative * sensitivity
		if InputManager.invert_y_mouse:
			motion.y *= -1.0
		camera_controller.apply_mouse_motion(motion)


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta


func get_camera_relative_input() -> Vector3:
	## Returns movement input relative to camera facing direction.
	var input := InputManager.get_move_vector()
	if input.length() < INPUT_DEADZONE:
		return Vector3.ZERO

	var forward := camera_controller.get_camera_forward()
	var right := camera_controller.get_camera_right()
	return (forward * -input.y + right * input.x).normalized()


func apply_air_control(delta: float) -> void:
	## Shared air movement logic used by Jump and Fall states.
	var direction := get_camera_relative_input()
	var air_speed := sprint_speed if is_sprinting else move_speed
	if direction.length() > INPUT_DEADZONE:
		velocity.x = direction.x * air_speed * AIR_CONTROL_FACTOR
		velocity.z = direction.z * air_speed * AIR_CONTROL_FACTOR
		rotate_model_to_direction(direction, delta)


func decelerate_horizontal(delta: float, rate: float = -1.0) -> void:
	## Smoothly decelerates horizontal velocity toward zero.
	if rate < 0.0:
		rate = move_speed * DECEL_FACTOR
	velocity.x = move_toward(velocity.x, 0.0, rate * delta)
	velocity.z = move_toward(velocity.z, 0.0, rate * delta)


func apply_aim_physics(delta: float) -> void:
	## Shared aim/shoot movement: strafe at aim_speed, face camera direction.
	var direction := get_camera_relative_input()
	if direction.length() > INPUT_DEADZONE:
		velocity.x = direction.x * aim_speed
		velocity.z = direction.z * aim_speed
	else:
		decelerate_horizontal(delta, aim_speed * DECEL_FACTOR)
	var cam_forward := camera_controller.get_camera_forward()
	rotate_model_to_direction(cam_forward, delta)
	move_and_slide()
	# Controller look input
	var look := InputManager.get_look_vector()
	if look.length() > 0.01:
		camera_controller.rotate_camera(look, delta)


func rotate_model_to_direction(direction: Vector3, delta: float) -> void:
	## Smoothly rotates the player model to face movement direction.
	if direction.length() < INPUT_DEADZONE:
		return
	facing_direction = direction
	var target_angle := atan2(direction.x, direction.z)
	model.rotation.y = lerp_angle(model.rotation.y, target_angle, delta * 12.0)


func _on_health_changed(current: float, maximum: float) -> void:
	EventBus.player_health_changed.emit(current, maximum)
	# Low health haptic heartbeat
	if current / maximum < 0.25 and current > 0:
		InputManager.request_haptic(&"heartbeat", 0.5, 0.15)


func _on_died() -> void:
	EventBus.player_died.emit()
	state_machine.transition_to("Dead")


# Saveable interface
func get_save_data() -> Dictionary:
	return {
		"id": "player",
		"position": [global_position.x, global_position.y, global_position.z],
		"health": health.get_save_data(),
	}


func load_save_data(data: Dictionary) -> void:
	var pos: Array = data.get("position", [0, 0, 0])
	global_position = Vector3(pos[0], pos[1], pos[2])
	if data.has("health"):
		health.load_save_data(data["health"])
