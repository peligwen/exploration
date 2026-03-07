class_name StateMachine
extends Node
## Generic state machine. Add State nodes as children.
## Automatically finds and manages child State nodes.

signal state_changed(old_state: String, new_state: String)

@export var initial_state: NodePath

var current_state: State = null
var states: Dictionary = {} # name -> State


func _ready() -> void:
	# Register all child State nodes
	for child in get_children():
		if child is State:
			states[child.name] = child
			child.state_machine = self

	# Enter initial state
	if initial_state:
		var state_node := get_node_or_null(initial_state)
		if state_node and state_node is State:
			current_state = state_node
			current_state.enter("")
	elif not states.is_empty():
		current_state = states.values()[0]
		current_state.enter("")


func _process(delta: float) -> void:
	if current_state:
		current_state.process_state(delta)


func _physics_process(delta: float) -> void:
	if current_state:
		current_state.physics_process_state(delta)


func _unhandled_input(event: InputEvent) -> void:
	if current_state:
		current_state.handle_input(event)


func transition_to(state_name: String) -> void:
	if not states.has(state_name):
		push_warning("StateMachine: No state named '%s'" % state_name)
		return

	var old_state_name := current_state.name if current_state else ""
	if old_state_name == state_name:
		return

	if current_state:
		current_state.exit()

	current_state = states[state_name]
	current_state.enter(old_state_name)
	state_changed.emit(old_state_name, state_name)


func get_current_state_name() -> String:
	return current_state.name if current_state else ""
