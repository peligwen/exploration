class_name PlayerJump
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	# Coyote time check
	var now := Time.get_ticks_msec() / 1000.0
	var can_jump := player.is_on_floor() or (now - player.last_grounded_time) < player.coyote_time

	if can_jump:
		player.velocity.y = player.jump_force
	else:
		# Buffer the jump for when we land
		player.jump_buffer_timer = player.jump_buffer_time
		transition_to("Fall")
		return


func physics_process_state(delta: float) -> void:
	player.apply_air_control(delta)
	player.move_and_slide()

	if player.velocity.y <= 0.0:
		transition_to("Fall")
		return

	var direction := player.get_camera_relative_input()
	if Input.is_action_just_pressed("dodge") and direction.length() > Player.INPUT_DEADZONE:
		transition_to("Dodge")
