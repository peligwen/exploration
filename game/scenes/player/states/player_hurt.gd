class_name PlayerHurt
extends State

@onready var player: Player = owner
var _timer: float = 0.0
const HURT_DURATION: float = 0.3
const HURT_DECEL: float = 20.0


func enter(_previous_state: String) -> void:
	_timer = HURT_DURATION
	InputManager.request_haptic(&"damage", 0.8, 0.2)
	player.camera_controller.add_shake(0.5)


func physics_process_state(delta: float) -> void:
	# Slow to a stop during hurt stun
	player.decelerate_horizontal(delta, HURT_DECEL)
	player.move_and_slide()

	_timer -= delta
	if _timer <= 0.0:
		if player.health.is_dead:
			transition_to("Dead")
		elif player.get_camera_relative_input().length() > Player.INPUT_DEADZONE:
			transition_to("Run")
		else:
			transition_to("Idle")
