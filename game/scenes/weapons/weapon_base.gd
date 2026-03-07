class_name WeaponBase
extends Node3D
## Base class for all weapons. Extend for specific weapon types.

signal ammo_changed(current: int, max_ammo: int)
signal fired()
signal reloaded()

@export_group("Weapon Stats")
@export var weapon_name: String = "Weapon"
@export var damage: float = 10.0
@export var fire_rate: float = 0.15 ## Seconds between shots
@export var max_ammo: int = 30
@export var reload_time: float = 1.5
@export var spread: float = 0.0 ## Degrees of spread
@export var range_distance: float = 100.0

var current_ammo: int
var is_reloading: bool = false
var _fire_cooldown: float = 0.0
var _reload_timer: float = 0.0

@onready var raycast: RayCast3D = $RayCast3D
@onready var muzzle: Marker3D = $Muzzle


func _ready() -> void:
	current_ammo = max_ammo
	if raycast:
		raycast.target_position = Vector3(0, 0, -range_distance)
		# Hit enemies, destructibles, environment (layers 1, 3, 8)
		raycast.collision_mask = 1 | 4 | 128


func _process(delta: float) -> void:
	if _fire_cooldown > 0.0:
		_fire_cooldown -= delta

	if is_reloading:
		_reload_timer -= delta
		if _reload_timer <= 0.0:
			_finish_reload()


func fire() -> void:
	if is_reloading or _fire_cooldown > 0.0:
		return
	if current_ammo <= 0:
		start_reload()
		return

	current_ammo -= 1
	_fire_cooldown = fire_rate

	# Apply spread
	if spread > 0.0 and raycast:
		var spread_rad := deg_to_rad(spread)
		raycast.rotation.x = randf_range(-spread_rad, spread_rad)
		raycast.rotation.y = randf_range(-spread_rad, spread_rad)

	# Force raycast update this frame
	if raycast:
		raycast.force_raycast_update()
		if raycast.is_colliding():
			_on_hit(raycast.get_collider(), raycast.get_collision_point(), raycast.get_collision_normal())

	fired.emit()
	ammo_changed.emit(current_ammo, max_ammo)
	EventBus.player_ammo_changed.emit(current_ammo, max_ammo)


func start_reload() -> void:
	if is_reloading or current_ammo == max_ammo:
		return
	is_reloading = true
	_reload_timer = reload_time


func _finish_reload() -> void:
	current_ammo = max_ammo
	is_reloading = false
	reloaded.emit()
	ammo_changed.emit(current_ammo, max_ammo)
	EventBus.player_ammo_changed.emit(current_ammo, max_ammo)


func _on_hit(collider: Object, point: Vector3, normal: Vector3) -> void:
	if collider is Node and collider.has_node("HealthComponent"):
		var health_comp: HealthComponent = collider.get_node("HealthComponent")
		var info := DamageInfo.create(
			damage,
			owner, # The player
			DamageInfo.DamageType.PHYSICAL,
			point,
			-normal * 2.0 # Knockback away from hit surface
		)
		health_comp.take_damage(info)
