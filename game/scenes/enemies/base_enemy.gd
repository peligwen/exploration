class_name BaseEnemy
extends CharacterBody3D
## Base enemy controller. Uses state machine for behavior.
## Extend for specific enemy types.

@export_group("Stats")
@export var move_speed: float = 3.5
@export var chase_speed: float = 5.0
@export var attack_damage: float = 10.0
@export var attack_range: float = 2.0
@export var detection_range: float = 15.0
@export var attack_cooldown: float = 1.0

@export_group("Patrol")
@export var patrol_points: Array[Vector3] = []
@export var patrol_wait_time: float = 2.0

var target: Node3D = null ## Usually the player
var gravity: float = 20.0
var unique_id: String = ""

@onready var state_machine: StateMachine = $StateMachine
@onready var health: HealthComponent = $HealthComponent
@onready var nav_agent: NavigationAgent3D = $NavigationAgent3D
@onready var model: Node3D = $Model


func _ready() -> void:
	unique_id = str(get_instance_id())
	add_to_group("saveable")
	add_to_group("enemies")
	GameManager.register_saveable(self)

	health.died.connect(_on_died)
	health.damage_taken.connect(_on_damage_taken)

	# Find player as target
	await get_tree().process_frame
	var players := get_tree().get_nodes_in_group("saveable")
	for node in players:
		if node is Player:
			target = node
			break


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta


func get_distance_to_target() -> float:
	if target:
		return global_position.distance_to(target.global_position)
	return INF


func can_see_target() -> bool:
	if not target:
		return false
	return get_distance_to_target() <= detection_range


func is_in_attack_range() -> bool:
	return get_distance_to_target() <= attack_range


func face_target(delta: float) -> void:
	if not target:
		return
	var direction := (target.global_position - global_position).normalized()
	direction.y = 0.0
	if direction.length() > 0.01:
		var target_angle := atan2(direction.x, direction.z)
		model.rotation.y = lerp_angle(model.rotation.y, target_angle, delta * 8.0)


func navigate_to(target_pos: Vector3, speed: float, delta: float) -> void:
	nav_agent.target_position = target_pos
	if nav_agent.is_navigation_finished():
		return

	var next_pos := nav_agent.get_next_path_position()
	var direction := (next_pos - global_position).normalized()
	direction.y = 0.0
	velocity.x = direction.x * speed
	velocity.z = direction.z * speed

	if direction.length() > 0.01:
		var target_angle := atan2(direction.x, direction.z)
		model.rotation.y = lerp_angle(model.rotation.y, target_angle, delta * 8.0)

	move_and_slide()


func deal_damage_to_target() -> void:
	if target and target.has_node("HealthComponent"):
		var health_comp: HealthComponent = target.get_node("HealthComponent")
		var direction := (target.global_position - global_position).normalized()
		var info := DamageInfo.create(
			attack_damage,
			self,
			DamageInfo.DamageType.PHYSICAL,
			target.global_position,
			direction * 3.0
		)
		health_comp.take_damage(info)


func _on_died() -> void:
	state_machine.transition_to("Dead")


func _on_damage_taken(damage_info: DamageInfo) -> void:
	if not health.is_dead:
		state_machine.transition_to("Hurt")


# Saveable interface
func get_save_data() -> Dictionary:
	return {
		"id": unique_id,
		"scene_path": scene_file_path,
		"position": [global_position.x, global_position.y, global_position.z],
		"health": health.get_save_data(),
	}


func load_save_data(data: Dictionary) -> void:
	var pos: Array = data.get("position", [0, 0, 0])
	global_position = Vector3(pos[0], pos[1], pos[2])
	if data.has("health"):
		health.load_save_data(data["health"])
