class_name PlayerAim
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	player.is_aiming = true
	player.camera_controller.set_mode(CameraController.CameraMode.AIM)


func exit() -> void:
	player.is_aiming = false
	player.camera_controller.set_mode(CameraController.CameraMode.FOLLOW)


func physics_process_state(delta: float) -> void:
	player.apply_gravity(delta)

	# Slow strafe movement while aiming
	var direction := player.get_camera_relative_input()
	if direction.length() > 0.1:
		player.velocity.x = direction.x * player.aim_speed
		player.velocity.z = direction.z * player.aim_speed
	else:
		player.velocity.x = move_toward(player.velocity.x, 0.0, player.aim_speed * delta * 10.0)
		player.velocity.z = move_toward(player.velocity.z, 0.0, player.aim_speed * delta * 10.0)

	# Face camera direction while aiming (not movement direction)
	var cam_forward := player.camera_controller.get_camera_forward()
	player.rotate_model_to_direction(cam_forward, delta)

	player.move_and_slide()

	# Controller look input
	var look := InputManager.get_look_vector()
	if look.length() > 0.01:
		player.camera_controller.rotate_camera(look, delta)

	# Fire while aiming
	if Input.is_action_just_pressed("fire"):
		transition_to("Shoot")
		return

	if not Input.is_action_pressed("aim"):
		var input := player.get_camera_relative_input()
		if input.length() > 0.1:
			transition_to("Run")
		else:
			transition_to("Idle")
		return

	if Input.is_action_just_pressed("dodge"):
		transition_to("Dodge")
		return

	if not player.is_on_floor():
		transition_to("Fall")
