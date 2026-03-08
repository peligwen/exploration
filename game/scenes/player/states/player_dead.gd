class_name PlayerDead
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	player.camera_controller.set_mode(CameraController.CameraMode.DEATH)
	player.velocity = Vector3.ZERO
	InputManager.request_haptic(&"damage", 1.0, 0.5)


func physics_process_state(_delta: float) -> void:
	# Gravity is applied by Player._physics_process
	player.move_and_slide()
