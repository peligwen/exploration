"""Generic state machine. Register State instances with add_state()."""
from scripts.components.state import State


class StateMachine:
    """Generic state machine that manages State instances."""

    def __init__(self, owner=None):
        self.owner = owner
        self.current_state: State = None
        self.states: dict[str, State] = {}
        self._on_state_changed = None  # Optional callback(old_name, new_name)

    def add_state(self, state: State):
        """Register a state."""
        state.state_machine = self
        state.owner = self.owner
        self.states[state.name] = state

    def start(self, initial_state_name: str):
        """Enter the initial state."""
        if initial_state_name in self.states:
            self.current_state = self.states[initial_state_name]
            self.current_state.enter("")

    def transition_to(self, state_name: str, msg: dict = None):
        """Switch to a named state, forwarding an optional context dict to enter()."""
        if state_name not in self.states:
            print(f"StateMachine: No state named '{state_name}'")
            return

        old_name = self.current_state.name if self.current_state else ""
        if old_name == state_name:
            return

        if self.current_state:
            self.current_state.exit()

        self.current_state = self.states[state_name]
        self.current_state.enter(old_name, msg or {})

        if self._on_state_changed:
            self._on_state_changed(old_name, state_name)

    def get_current_state_name(self) -> str:
        return self.current_state.name if self.current_state else ""

    def update(self, delta: float):
        """Call every frame."""
        if self.current_state:
            self.current_state.process_state(delta)

    def physics_update(self, delta: float):
        """Call every physics tick (same as update in Ursina)."""
        if self.current_state:
            self.current_state.physics_process_state(delta)

    def handle_input(self, key, is_press: bool):
        """Route input to current state."""
        if self.current_state:
            self.current_state.handle_input(key, is_press)
