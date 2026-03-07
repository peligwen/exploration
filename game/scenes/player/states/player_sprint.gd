class_name PlayerSprint
extends State

@onready var player: Player = owner


func enter(_previous_state: String) -> void:
	player.is_sprinting = true
	player.current_speed = player.sprint_speed


func exit() -> void:
	player.is_sprinting = false


func physics_process_state(delta: float) -> void:
	player.apply_gravity(delta)

	var direction := player.get_camera_relative_input()
	if direction.length() < 0.1:
		transition_to("Idle")
		return

	player.velocity.x = direction.x * player.sprint_speed
	player.velocity.z = direction.z * player.sprint_speed
	player.rotate_model_to_direction(direction, delta)
	player.move_and_slide()

	if player.is_on_floor():
		player.last_grounded_time = Time.get_ticks_msec() / 1000.0

	if not Input.is_action_pressed("sprint"):
		transition_to("Run")
		return

	if Input.is_action_just_pressed("jump"):
		transition_to("Jump")
		return

	if Input.is_action_just_pressed("dodge"):
		transition_to("Dodge")
		return

	if not player.is_on_floor():
		transition_to("Fall")
