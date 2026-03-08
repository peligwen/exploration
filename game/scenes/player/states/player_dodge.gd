class_name PlayerDodge
extends State

@onready var player: Player = owner
var _timer: float = 0.0
var _dodge_direction: Vector3 = Vector3.ZERO


func enter(_previous_state: String) -> void:
	player.is_dodging = true
	player.is_invincible = true
	_timer = player.dodge_duration

	# Dodge in input direction, or backward if no input
	var input := player.get_camera_relative_input()
	if input.length() > Player.INPUT_DEADZONE:
		_dodge_direction = input.normalized()
	else:
		_dodge_direction = -player.facing_direction.normalized()

	player.rotate_model_to_direction(_dodge_direction, 1.0)
	InputManager.request_haptic(&"fire", 0.3, 0.1)


func exit() -> void:
	player.is_dodging = false
	player.is_invincible = false


func physics_process_state(delta: float) -> void:
	player.velocity.x = _dodge_direction.x * player.dodge_speed
	player.velocity.z = _dodge_direction.z * player.dodge_speed
	player.move_and_slide()

	_timer -= delta
	if _timer <= 0.0:
		if player.get_camera_relative_input().length() > Player.INPUT_DEADZONE:
			transition_to("Run")
		else:
			transition_to("Idle")
