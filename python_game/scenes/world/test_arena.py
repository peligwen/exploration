"""Test arena for Milestone 1. Spawns player, enemies, weapon, and arena geometry."""
from ursina import Entity, Vec3, color

from scenes.player.player import Player
from scenes.enemies.base_enemy import BaseEnemy
from scenes.weapons.rifle import Rifle
from scenes.ui.hud import HUD
from scenes.ui.pause_menu import PauseMenu

# Import all player states
from scenes.player.states.player_idle import PlayerIdle
from scenes.player.states.player_run import PlayerRun
from scenes.player.states.player_sprint import PlayerSprint
from scenes.player.states.player_jump import PlayerJump
from scenes.player.states.player_fall import PlayerFall
from scenes.player.states.player_dodge import PlayerDodge
from scenes.player.states.player_aim import PlayerAim
from scenes.player.states.player_shoot import PlayerShoot
from scenes.player.states.player_hurt import PlayerHurt
from scenes.player.states.player_dead import PlayerDead

# Import all enemy states
from scenes.enemies.states.enemy_idle import EnemyIdle
from scenes.enemies.states.enemy_patrol import EnemyPatrol
from scenes.enemies.states.enemy_chase import EnemyChase
from scenes.enemies.states.enemy_attack import EnemyAttack
from scenes.enemies.states.enemy_hurt import EnemyHurt
from scenes.enemies.states.enemy_dead import EnemyDead

from scripts.autoload.event_bus import event_bus, PLAYER_AMMO_CHANGED


def _setup_player_states(player: Player):
    """Register all 10 player states."""
    states = [
        PlayerIdle(), PlayerRun(), PlayerSprint(),
        PlayerJump(), PlayerFall(), PlayerDodge(),
        PlayerAim(), PlayerShoot(), PlayerHurt(), PlayerDead(),
    ]
    for state in states:
        player.state_machine.add_state(state)
    player.state_machine.start("Idle")


def _setup_enemy_states(enemy: BaseEnemy):
    """Register all 6 enemy states."""
    states = [
        EnemyIdle(), EnemyPatrol(), EnemyChase(),
        EnemyAttack(), EnemyHurt(), EnemyDead(),
    ]
    for state in states:
        enemy.state_machine.add_state(state)
    enemy.state_machine.start("Idle")


def create_test_arena():
    """Build the test arena with all entities."""

    # --- Arena Geometry ---

    # Floor
    floor = Entity(
        model='plane',
        color=color.color(120, 0.3, 0.4),
        scale=(50, 1, 50),
        position=(0, 0, 0),
        collider='box',
    )

    # Walls
    wall_color = color.color(0, 0, 0.3)
    # North wall
    Entity(model='cube', color=wall_color, scale=(50, 4, 1),
           position=(0, 2, 25), collider='box')
    # South wall
    Entity(model='cube', color=wall_color, scale=(50, 4, 1),
           position=(0, 2, -25), collider='box')
    # East wall
    Entity(model='cube', color=wall_color, scale=(1, 4, 50),
           position=(25, 2, 0), collider='box')
    # West wall
    Entity(model='cube', color=wall_color, scale=(1, 4, 50),
           position=(-25, 2, 0), collider='box')

    # Pillars (cover)
    pillar_color = color.color(30, 0.2, 0.5)
    for pos in [Vec3(5, 1.5, 5), Vec3(-5, 1.5, -5), Vec3(8, 1.5, -3), Vec3(-7, 1.5, 6)]:
        Entity(model='cube', color=pillar_color, scale=(1.5, 3, 1.5),
               position=pos, collider='box')

    # --- Player ---
    player = Player(position=Vec3(0, 0.9, 0))
    _setup_player_states(player)

    # Give player a rifle
    rifle = Rifle(owner_entity=player, parent=player, position=Vec3(0.3, 0.5, -0.5))
    player.current_weapon = rifle
    event_bus.emit(PLAYER_AMMO_CHANGED, rifle.current_ammo, rifle.max_ammo)

    # --- Enemies ---
    enemy_positions = [Vec3(10, 1, 10), Vec3(-10, 1, -10), Vec3(15, 1, -5)]
    enemies = []
    for pos in enemy_positions:
        enemy = BaseEnemy(position=pos)
        enemy.target = player
        _setup_enemy_states(enemy)
        enemies.append(enemy)

    # --- UI ---
    hud = HUD()
    pause_menu = PauseMenu()

    # Connect state machine debug output
    def on_state_changed(old_name, new_name):
        hud.update_state_debug(new_name)
    player.state_machine._on_state_changed = on_state_changed

    # Handle pause input
    def handle_pause(key):
        if key == 'escape':
            pause_menu.toggle_pause()

    # Store pause handler on player for input routing
    player._pause_menu = pause_menu

    return player, enemies, hud, pause_menu
