"""Base state class. Extend this for each specific state.
The StateMachine routes lifecycle calls to the active state.
"""


class State:
    """Base state class."""

    def __init__(self, name: str):
        self.name = name
        self.state_machine = None
        self.owner = None  # The entity this state belongs to

    def enter(self, previous_state: str):
        """Called when this state becomes active."""
        pass

    def exit(self):
        """Called when leaving this state."""
        pass

    def process_state(self, delta: float):
        """Called every frame while this state is active."""
        pass

    def physics_process_state(self, delta: float):
        """Called every physics tick while this state is active."""
        pass

    def handle_input(self, key, is_press: bool):
        """Called for input while this state is active."""
        pass

    def transition_to(self, state_name: str):
        """Request a transition to another state by name."""
        if self.state_machine:
            self.state_machine.transition_to(state_name)
