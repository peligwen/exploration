class_name GameManagerClass
extends Node
## Singleton managing game state, scene transitions, and saveable object registry.

enum GameState { PLAYING, PAUSED, MENU, DEAD }

var state: GameState = GameState.PLAYING
var _saveables: Dictionary = {} # Node -> true, for O(1) register/unregister


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func register_saveable(node: Node) -> void:
	_saveables[node] = true


func unregister_saveable(node: Node) -> void:
	_saveables.erase(node)


func get_all_save_data() -> Array[Dictionary]:
	var data: Array[Dictionary] = []
	for node: Node in _saveables:
		if is_instance_valid(node) and node.has_method("get_save_data"):
			data.append(node.get_save_data())
	return data


func set_paused(paused: bool) -> void:
	if paused:
		state = GameState.PAUSED
	else:
		state = GameState.PLAYING
	get_tree().paused = paused


func is_playing() -> bool:
	return state == GameState.PLAYING
