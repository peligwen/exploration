class_name PlayerFall
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	pass


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

	# Jump buffering — pressed jump while falling, execute on landing
	if Input.is_action_just_pressed("jump"):
		player.jump_buffer_timer = player.jump_buffer_time

	player.jump_buffer_timer -= delta

	if player.is_on_floor():
		if player.jump_buffer_timer > 0.0:
			player.jump_buffer_timer = 0.0
			transition_to("Jump")
		elif direction.length() > 0.1:
			transition_to("Run")
		else:
			transition_to("Idle")
