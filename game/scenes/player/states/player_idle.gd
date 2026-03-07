class_name PlayerIdle
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	player.is_sprinting = false
	player.current_speed = 0.0


func physics_process_state(delta: float) -> void:
	player.apply_gravity(delta)
	player.velocity.x = move_toward(player.velocity.x, 0.0, player.move_speed * delta * 10.0)
	player.velocity.z = move_toward(player.velocity.z, 0.0, player.move_speed * delta * 10.0)
	player.move_and_slide()

	# Track grounded for coyote time
	if player.is_on_floor():
		player.last_grounded_time = Time.get_ticks_msec() / 1000.0

	# Transitions
	var input := player.get_camera_relative_input()
	if input.length() > 0.1:
		transition_to("Run")
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
