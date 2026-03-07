class_name EnemyChase
extends State

@onready var enemy: BaseEnemy = owner


func enter(_previous_state: String) -> void:
	pass


func physics_process_state(delta: float) -> void:
	if not enemy.target:
		transition_to("Idle")
		return

	if enemy.is_in_attack_range():
		transition_to("Attack")
		return

	if not enemy.can_see_target():
		transition_to("Idle")
		return

	enemy.navigate_to(enemy.target.global_position, enemy.chase_speed, delta)
