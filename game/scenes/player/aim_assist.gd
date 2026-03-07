class_name AimAssist
extends Node
## Aim assist system for controller input.
## Three layers: sticky aim, snap assist, bullet magnetism.
## Only active when InputManager reports controller device.

@export var sticky_radius: float = 100.0 ## Screen-space pixel radius for sticky aim
@export var sticky_friction: float = 0.4 ## How much to slow rotation (0 = none, 1 = full stop)
@export var snap_radius: float = 150.0 ## Screen-space radius for snap assist
@export var snap_strength: float = 0.3 ## How strongly to snap (0-1)
@export var magnetism_angle: float = 3.0 ## Degrees of bullet magnetism cone

var _player: Player
var _camera: Camera3D


func _ready() -> void:
	_player = owner as Player
	# Camera reference found after tree is built
	await get_tree().process_frame
	if _player and _player.camera_controller:
		_camera = _player.camera_controller.camera


func get_sticky_factor(enemies: Array[Node3D]) -> float:
	## Returns 0-1 friction factor. Apply to camera rotation speed.
	## 0 = no assist, 1 = full friction (would freeze).
	if not _should_assist():
		return 0.0

	var closest_screen_dist := sticky_radius + 1.0
	var screen_center := _get_screen_center()

	for enemy in enemies:
		if not is_instance_valid(enemy):
			continue
		if not _camera.is_position_behind(enemy.global_position):
			var screen_pos := _camera.unproject_position(enemy.global_position)
			var dist := screen_pos.distance_to(screen_center)
			closest_screen_dist = minf(closest_screen_dist, dist)

	if closest_screen_dist > sticky_radius:
		return 0.0

	var t := 1.0 - (closest_screen_dist / sticky_radius)
	return t * sticky_friction * InputManager.aim_assist_strength


func get_snap_offset(enemies: Array[Node3D]) -> Vector2:
	## Returns a screen-space offset to nudge crosshair toward nearest enemy.
	## Apply when entering aim mode (LT pressed).
	if not _should_assist():
		return Vector2.ZERO

	var screen_center := _get_screen_center()
	var best_enemy: Node3D = null
	var best_dist := snap_radius + 1.0

	for enemy in enemies:
		if not is_instance_valid(enemy):
			continue
		if not _camera.is_position_behind(enemy.global_position):
			var screen_pos := _camera.unproject_position(enemy.global_position)
			var dist := screen_pos.distance_to(screen_center)
			if dist < best_dist:
				best_dist = dist
				best_enemy = enemy

	if best_enemy == null:
		return Vector2.ZERO

	var target_screen := _camera.unproject_position(best_enemy.global_position)
	var offset := (target_screen - screen_center) * snap_strength * InputManager.aim_assist_strength
	return offset


func get_magnetism_target(origin: Vector3, direction: Vector3, enemies: Array[Node3D]) -> Vector3:
	## Returns adjusted aim direction that curves slightly toward enemies.
	## For bullet magnetism.
	if not _should_assist():
		return direction

	var mag_cos := cos(deg_to_rad(magnetism_angle))
	var best_enemy: Node3D = null
	var best_dot := mag_cos

	for enemy in enemies:
		if not is_instance_valid(enemy):
			continue
		var to_enemy := (enemy.global_position - origin).normalized()
		var dot := direction.dot(to_enemy)
		if dot > best_dot:
			best_dot = dot
			best_enemy = enemy

	if best_enemy == null:
		return direction

	var to_target := (best_enemy.global_position - origin).normalized()
	var blend := InputManager.aim_assist_strength * 0.15
	return direction.lerp(to_target, blend).normalized()


func _should_assist() -> bool:
	return InputManager.is_controller() and InputManager.aim_assist_strength > 0.0 and _camera != null


func _get_screen_center() -> Vector2:
	var viewport := _camera.get_viewport()
	return Vector2(viewport.size) / 2.0
