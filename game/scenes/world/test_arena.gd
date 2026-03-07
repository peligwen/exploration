class_name TestArena
extends Node3D
## Test arena for Milestone 1. Spawns player, enemies, and a weapon.

@onready var player: Player = $Player


func _ready() -> void:
	# Give the player a rifle
	var rifle_scene := preload("res://scenes/weapons/rifle.tscn")
	var rifle := rifle_scene.instantiate()
	player.weapon_mount.add_child(rifle)
	player.current_weapon = rifle

	# Connect state machine debug output
	player.state_machine.state_changed.connect(_on_player_state_changed)

	# Initial ammo display
	EventBus.player_ammo_changed.emit(rifle.current_ammo, rifle.max_ammo)


func _on_player_state_changed(_old: String, new_state: String) -> void:
	var hud := get_node_or_null("HUD")
	if hud and hud.has_method("update_state_debug"):
		hud.update_state_debug(new_state)
