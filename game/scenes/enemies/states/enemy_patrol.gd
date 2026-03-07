class_name EnemyPatrol
extends State

@onready var enemy: BaseEnemy = owner
var _current_point_index: int = 0
var _wait_timer: float = 0.0
var _waiting: bool = false


func enter(_previous_state: String) -> void:
	_waiting = false
	if enemy.patrol_points.is_empty():
		transition_to("Idle")


func physics_process_state(delta: float) -> void:
	if enemy.can_see_target():
		transition_to("Chase")
		return

	if enemy.patrol_points.is_empty():
		transition_to("Idle")
		return

	if _waiting:
		_wait_timer -= delta
		enemy.velocity.x = 0.0
		enemy.velocity.z = 0.0
		enemy.move_and_slide()
		if _wait_timer <= 0.0:
			_waiting = false
			_current_point_index = (_current_point_index + 1) % enemy.patrol_points.size()
		return

	var target_point := enemy.patrol_points[_current_point_index]
	var dist := enemy.global_position.distance_to(target_point)

	if dist < 1.0:
		_waiting = true
		_wait_timer = enemy.patrol_wait_time
		return

	enemy.navigate_to(target_point, enemy.move_speed, delta)
