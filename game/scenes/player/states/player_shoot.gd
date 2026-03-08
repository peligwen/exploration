class_name PlayerShoot
extends State

@onready var player: Player = owner
var _shoot_timer: float = 0.0


func enter(_previous_state: String) -> void:
	player.is_aiming = true
	player.camera_controller.set_mode(CameraController.CameraMode.AIM)
	_fire()


func exit() -> void:
	pass # Aim state handles resetting camera mode


func physics_process_state(delta: float) -> void:
	player.apply_aim_physics(delta)

	_shoot_timer -= delta

	# Continuous fire while held
	if Input.is_action_pressed("fire") and _shoot_timer <= 0.0:
		_fire()
		return

	# Release fire → back to aim or idle
	if not Input.is_action_pressed("fire"):
		if Input.is_action_pressed("aim"):
			transition_to("Aim")
		else:
			transition_to("Idle")
		return

	if Input.is_action_just_pressed("dodge"):
		transition_to("Dodge")


func _fire() -> void:
	if player.current_weapon and player.current_weapon.has_method("fire"):
		player.current_weapon.fire()

	player.camera_controller.add_shake(0.3)
	InputManager.request_haptic(&"fire", 0.6, 0.1)
	_shoot_timer = 0.15 # Fire rate (will be weapon-specific later)
