class_name EnemyHurt
extends State

@onready var enemy: BaseEnemy = owner
var _timer: float = 0.0
const HURT_DURATION: float = 0.3


func enter(_previous_state: String) -> void:
	_timer = HURT_DURATION
	enemy.velocity.x = 0.0
	enemy.velocity.z = 0.0


func physics_process_state(delta: float) -> void:
	enemy.move_and_slide()

	_timer -= delta
	if _timer <= 0.0:
		if enemy.health.is_dead:
			transition_to("Dead")
		elif enemy.can_see_target():
			transition_to("Chase")
		else:
			transition_to("Idle")
