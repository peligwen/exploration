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
	player.apply_gravity(delta)

	# Air control
	var direction := player.get_camera_relative_input()
	var air_speed := player.sprint_speed if player.is_sprinting else player.move_speed
	if direction.length() > 0.1:
		player.velocity.x = direction.x * air_speed * 0.8
		player.velocity.z = direction.z * air_speed * 0.8
		player.rotate_model_to_direction(direction, delta)

	player.move_and_slide()

	if player.velocity.y <= 0.0:
		transition_to("Fall")
		return

	if Input.is_action_just_pressed("dodge") and direction.length() > 0.1:
		transition_to("Dodge")
