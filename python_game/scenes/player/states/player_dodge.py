"""Player Dodge state — roll with i-frames."""
from ursina import Vec3
from scripts.components.state import State
from scenes.player.player import INPUT_DEADZONE


class PlayerDodge(State):
    def __init__(self):
        super().__init__("Dodge")
        self._timer = 0.0
        self._dodge_direction = Vec3(0, 0, 0)

    def enter(self, previous_state: str, msg: dict = None):
        player = self.owner
        player.is_dodging = True
        # TODO(migration): is_invincible is set here but HealthComponent.take_damage() never
        # checks it. Player still takes full damage during dodge. Add invincibility check in
        # HealthComponent.take_damage():
        #   if hasattr(self.owner, 'is_invincible') and self.owner.is_invincible: return
        player.is_invincible = True
        self._timer = player.dodge_duration

        # Dodge in input direction, or backward if no input
        direction = player.get_camera_relative_input()
        if direction.length() > INPUT_DEADZONE:
            self._dodge_direction = direction.normalized()
        else:
            self._dodge_direction = -player.facing_direction.normalized()

        player.rotate_model_to_direction(self._dodge_direction, 1.0)

    def exit(self):
        self.owner.is_dodging = False
        self.owner.is_invincible = False

    def process_state(self, delta: float):
        player = self.owner

        player.velocity.x = self._dodge_direction.x * player.dodge_speed
        player.velocity.z = self._dodge_direction.z * player.dodge_speed

        self._timer -= delta
        if self._timer <= 0.0:
            direction = player.get_camera_relative_input()
            if direction.length() > INPUT_DEADZONE:
                self.transition_to("Run")
            else:
                self.transition_to("Idle")
