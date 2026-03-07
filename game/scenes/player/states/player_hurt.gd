class_name PlayerHurt
extends State

@onready var player: Player = owner
var _timer: float = 0.0
const HURT_DURATION: float = 0.3


func enter(_previous_state: String) -> void:
	_timer = HURT_DURATION
	InputManager.request_haptic(&"damage", 0.8, 0.2)
	player.camera_controller.add_shake(0.5)


func physics_process_state(delta: float) -> void:
	player.apply_gravity(delta)

	# Slow to a stop during hurt stun
	player.velocity.x = move_toward(player.velocity.x, 0.0, 20.0 * delta)
	player.velocity.z = move_toward(player.velocity.z, 0.0, 20.0 * delta)
	player.move_and_slide()

	_timer -= delta
	if _timer <= 0.0:
		if player.health.is_dead:
			transition_to("Dead")
		elif player.get_camera_relative_input().length() > 0.1:
			transition_to("Run")
		else:
			transition_to("Idle")
