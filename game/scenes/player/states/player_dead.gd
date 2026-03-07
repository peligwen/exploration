class_name PlayerDead
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	player.camera_controller.set_mode(CameraController.CameraMode.DEATH)
	player.velocity = Vector3.ZERO
	InputManager.request_haptic(&"damage", 1.0, 0.5)


func physics_process_state(_delta: float) -> void:
	# Just apply gravity and stay put
	player.apply_gravity(_delta)
	player.move_and_slide()
