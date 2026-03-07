class_name EnemyDead
extends State

@onready var enemy: BaseEnemy = owner
var _despawn_timer: float = 3.0


func enter(_previous_state: String) -> void:
	_despawn_timer = 3.0
	enemy.velocity = Vector3.ZERO
	# Disable collision so player can walk through
	enemy.collision_layer = 0
	enemy.collision_mask = 0


func physics_process_state(delta: float) -> void:
	# Sink into ground slowly then despawn
	_despawn_timer -= delta
	if _despawn_timer < 1.0:
		enemy.global_position.y -= delta * 0.5
	if _despawn_timer <= 0.0:
		GameManager.unregister_saveable(enemy)
		enemy.queue_free()
