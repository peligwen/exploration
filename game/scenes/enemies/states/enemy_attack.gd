class_name EnemyAttack
extends State

@onready var enemy: BaseEnemy = owner
var _attack_timer: float = 0.0
var _has_dealt_damage: bool = false


func enter(_previous_state: String) -> void:
	_attack_timer = enemy.attack_cooldown
	_has_dealt_damage = false
	enemy.velocity.x = 0.0
	enemy.velocity.z = 0.0


func physics_process_state(delta: float) -> void:
	enemy.face_target(delta)
	enemy.move_and_slide()

	# Deal damage partway through attack animation
	if not _has_dealt_damage and _attack_timer < enemy.attack_cooldown * 0.5:
		if enemy.is_in_attack_range():
			enemy.deal_damage_to_target()
		_has_dealt_damage = true

	_attack_timer -= delta
	if _attack_timer <= 0.0:
		if enemy.is_in_attack_range():
			# Attack again
			_attack_timer = enemy.attack_cooldown
			_has_dealt_damage = false
		elif enemy.can_see_target():
			transition_to("Chase")
		else:
			transition_to("Idle")
