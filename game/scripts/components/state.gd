class_name State
extends Node
## Base state class. Extend this for each specific state.
## The StateMachine parent routes lifecycle calls to the active state.

## Reference to the state machine that owns this state.
var state_machine: StateMachine = null


func enter(_previous_state: String) -> void:
	## Called when this state becomes active.
	pass


func exit() -> void:
	## Called when leaving this state.
	pass


func process_state(_delta: float) -> void:
	## Called every frame while this state is active.
	pass


func physics_process_state(_delta: float) -> void:
	## Called every physics tick while this state is active.
	pass


func handle_input(_event: InputEvent) -> void:
	## Called for unhandled input while this state is active.
	pass


func transition_to(state_name: String) -> void:
	## Request a transition to another state by name.
	if state_machine:
		state_machine.transition_to(state_name)
