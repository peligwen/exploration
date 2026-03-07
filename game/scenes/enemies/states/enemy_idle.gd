class_name EnemyIdle
extends State

@onready var enemy: BaseEnemy = owner
var _idle_timer: float = 0.0


func enter(_previous_state: String) -> void:
	_idle_timer = randf_range(1.0, 3.0)
	enemy.velocity.x = 0.0
	enemy.velocity.z = 0.0


func physics_process_state(delta: float) -> void:
	enemy.move_and_slide()

	if enemy.can_see_target():
		transition_to("Chase")
		return

	_idle_timer -= delta
	if _idle_timer <= 0.0 and not enemy.patrol_points.is_empty():
		transition_to("Patrol")
