class_name CameraController
extends Node3D
## Independent camera system. Follows a target node loosely.
## Modes: Follow, Aim, Shake, Death.

enum CameraMode { FOLLOW, AIM, SHAKE, DEATH }

@export var target_path: NodePath
@export var follow_distance: float = 5.0
@export var follow_height: float = 2.0
@export var aim_offset: Vector3 = Vector3(0.8, 1.8, 3.0) ## right, up, back
@export var aim_fov: float = 55.0
@export var default_fov: float = 70.0
@export var lerp_speed: float = 10.0
@export var auto_center_speed: float = 1.5

var mode: CameraMode = CameraMode.FOLLOW
var pitch: float = 0.0 ## Vertical rotation in radians
var yaw: float = 0.0 ## Horizontal rotation in radians

var _shake_amount: float = 0.0
var _shake_decay: float = 5.0
var _death_orbit_speed: float = 0.3
var _target: Node3D = null

@onready var spring_arm: SpringArm3D = $SpringArm3D
@onready var camera: Camera3D = $SpringArm3D/Camera3D


func _ready() -> void:
	if target_path:
		_target = get_node_or_null(target_path)
	# Make sure camera doesn't collide with player (layer 2)
	spring_arm.collision_mask = 1 # Environment only


func _process(delta: float) -> void:
	if not _target:
		return

	# Follow the target
	global_position = _target.global_position

	match mode:
		CameraMode.FOLLOW:
			_process_follow(delta)
		CameraMode.AIM:
			_process_aim(delta)
		CameraMode.DEATH:
			_process_death(delta)

	# Apply shake on top of any mode
	if _shake_amount > 0.01:
		_apply_shake(delta)


func rotate_camera(look_input: Vector2, delta: float) -> void:
	## Call this from the player controller with processed input.
	yaw -= look_input.x * delta
	pitch -= look_input.y * delta
	pitch = clampf(pitch, -1.2, 1.2) # ~70 degrees up/down


func apply_mouse_motion(relative: Vector2) -> void:
	## Direct mouse input (already scaled by sensitivity in player).
	yaw -= relative.x
	pitch -= relative.y
	pitch = clampf(pitch, -1.2, 1.2)


func set_mode(new_mode: CameraMode) -> void:
	mode = new_mode


func add_shake(amount: float) -> void:
	_shake_amount = maxf(_shake_amount, amount)


func get_camera_forward() -> Vector3:
	## Returns the flat (Y=0) forward direction of the camera.
	var forward := -camera.global_transform.basis.z
	forward.y = 0.0
	return forward.normalized()


func get_camera_right() -> Vector3:
	var right := camera.global_transform.basis.x
	right.y = 0.0
	return right.normalized()


func _process_follow(delta: float) -> void:
	rotation.y = yaw
	spring_arm.rotation.x = pitch
	spring_arm.spring_length = follow_distance
	spring_arm.position.y = follow_height
	spring_arm.position.x = 0.0

	camera.fov = lerpf(camera.fov, default_fov, delta * lerp_speed)


func _process_aim(delta: float) -> void:
	rotation.y = yaw
	spring_arm.rotation.x = pitch
	spring_arm.spring_length = aim_offset.z
	spring_arm.position.y = aim_offset.y
	spring_arm.position.x = aim_offset.x

	camera.fov = lerpf(camera.fov, aim_fov, delta * lerp_speed)


func _process_death(delta: float) -> void:
	yaw += _death_orbit_speed * delta
	rotation.y = yaw
	spring_arm.rotation.x = lerpf(spring_arm.rotation.x, -0.3, delta)
	spring_arm.spring_length = lerpf(spring_arm.spring_length, 8.0, delta * 2.0)


func _apply_shake(delta: float) -> void:
	var offset := Vector3(
		randf_range(-_shake_amount, _shake_amount),
		randf_range(-_shake_amount, _shake_amount),
		0.0
	)
	camera.position = offset * 0.1
	_shake_amount = lerpf(_shake_amount, 0.0, delta * _shake_decay)
	if _shake_amount < 0.01:
		_shake_amount = 0.0
		camera.position = Vector3.ZERO
