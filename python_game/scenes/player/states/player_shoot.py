"""Player Shoot state — fire weapon continuously while held."""
from ursina import held_keys
from scripts.components.state import State
from scenes.player.camera_controller import CameraMode


class PlayerShoot(State):
    def __init__(self):
        super().__init__("Shoot")
        self._shoot_timer = 0.0

    def enter(self, previous_state: str):
        self.owner.is_aiming = True
        self.owner.camera_controller.set_mode(CameraMode.AIM)
        self._fire()

    def process_state(self, delta: float):
        player = self.owner
        player.apply_aim_physics(delta)

        self._shoot_timer -= delta

        # Continuous fire while held
        if held_keys['left mouse'] and self._shoot_timer <= 0.0:
            self._fire()
            return

        # Release fire
        if not held_keys['left mouse']:
            if held_keys['right mouse']:
                self.transition_to("Aim")
            else:
                self.transition_to("Idle")
            return

    def exit(self):
        self.owner.is_aiming = False
        self.owner.camera_controller.set_mode(CameraMode.FOLLOW)

    def handle_input(self, key, is_press):
        if key == 'r' and is_press and self.owner.current_weapon:
            self.owner.current_weapon.start_reload()
        if key == 'left control':
            self.transition_to("Dodge")

    def _fire(self):
        player = self.owner
        if player.current_weapon and hasattr(player.current_weapon, 'fire'):
            player.current_weapon.fire()

        player.camera_controller.add_shake(0.3)
        if player.current_weapon:
            self._shoot_timer = player.current_weapon.fire_rate
        else:
            self._shoot_timer = 0.15
