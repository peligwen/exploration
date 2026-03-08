class_name PlayerFall
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	pass


func physics_process_state(delta: float) -> void:
	player.apply_air_control(delta)
	player.move_and_slide()

	# Jump buffering — pressed jump while falling, execute on landing
	if Input.is_action_just_pressed("jump"):
		player.jump_buffer_timer = player.jump_buffer_time

	player.jump_buffer_timer -= delta

	if player.is_on_floor():
		if player.jump_buffer_timer > 0.0:
			player.jump_buffer_timer = 0.0
			transition_to("Jump")
		elif player.get_camera_relative_input().length() > Player.INPUT_DEADZONE:
			transition_to("Run")
		else:
			transition_to("Idle")
