class_name HealthComponent
extends Node
## Reusable health component. Attach to any damageable node.
## Handles HP tracking, damage application, death, and i-frames.

signal health_changed(current: float, maximum: float)
signal died()
signal damage_taken(damage_info: DamageInfo)

@export var max_hp: float = 100.0
@export var iframe_duration: float = 0.0 ## Seconds of invulnerability after taking damage

var current_hp: float
var is_dead: bool = false
var _iframe_timer: float = 0.0


func _ready() -> void:
	current_hp = max_hp


func _process(delta: float) -> void:
	if _iframe_timer > 0.0:
		_iframe_timer -= delta


func take_damage(damage_info: DamageInfo) -> void:
	if is_dead:
		return
	if _iframe_timer > 0.0:
		return

	current_hp -= damage_info.amount
	current_hp = maxf(current_hp, 0.0)

	if iframe_duration > 0.0:
		_iframe_timer = iframe_duration

	health_changed.emit(current_hp, max_hp)
	damage_taken.emit(damage_info)
	EventBus.damage_dealt.emit(damage_info)

	if current_hp <= 0.0:
		is_dead = true
		died.emit()
		EventBus.entity_died.emit(get_parent(), damage_info.source)


func heal(amount: float) -> void:
	if is_dead:
		return
	current_hp = minf(current_hp + amount, max_hp)
	health_changed.emit(current_hp, max_hp)


func reset() -> void:
	current_hp = max_hp
	is_dead = false
	_iframe_timer = 0.0
	health_changed.emit(current_hp, max_hp)


func get_hp_percent() -> float:
	return current_hp / max_hp if max_hp > 0.0 else 0.0


# Saveable interface
func get_save_data() -> Dictionary:
	return {
		"current_hp": current_hp,
		"max_hp": max_hp,
		"is_dead": is_dead,
	}


func load_save_data(data: Dictionary) -> void:
	current_hp = data.get("current_hp", max_hp)
	max_hp = data.get("max_hp", max_hp)
	is_dead = data.get("is_dead", false)
	health_changed.emit(current_hp, max_hp)
