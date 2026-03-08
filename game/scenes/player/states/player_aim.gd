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
	player.apply_aim_physics(delta)

	# Fire while aiming
	if Input.is_action_just_pressed("fire"):
		transition_to("Shoot")
		return

	if not Input.is_action_pressed("aim"):
		if player.get_camera_relative_input().length() > Player.INPUT_DEADZONE:
			transition_to("Run")
		else:
			transition_to("Idle")
		return

	if Input.is_action_just_pressed("dodge"):
		transition_to("Dodge")
		return

	if not player.is_on_floor():
		transition_to("Fall")
