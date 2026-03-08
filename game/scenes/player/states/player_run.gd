class_name PlayerRun
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	player.is_sprinting = false
	player.current_speed = player.move_speed


func physics_process_state(delta: float) -> void:
	var direction := player.get_camera_relative_input()
	if direction.length() < Player.INPUT_DEADZONE:
		transition_to("Idle")
		return

	player.velocity.x = direction.x * player.move_speed
	player.velocity.z = direction.z * player.move_speed
	player.rotate_model_to_direction(direction, delta)
	player.move_and_slide()

	if player.is_on_floor():
		player.last_grounded_time = Time.get_ticks_msec() / 1000.0

	# Transitions
	if Input.is_action_pressed("sprint"):
		transition_to("Sprint")
		return

	if Input.is_action_just_pressed("jump"):
		transition_to("Jump")
		return

	if Input.is_action_just_pressed("dodge"):
		transition_to("Dodge")
		return

	if Input.is_action_pressed("aim"):
		transition_to("Aim")
		return

	if not player.is_on_floor():
		transition_to("Fall")
