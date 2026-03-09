"""Collision group string constants used throughout the project.

Every entity that participates in raycasts or physics should set
``self.collision_group`` to one of these values. Never use the raw
strings — always import from here.
"""

LAYER_ENVIRONMENT       = 'environment'
LAYER_PLAYER            = 'player'
LAYER_ENEMY             = 'enemy'
LAYER_PLAYER_PROJECTILE = 'player_projectile'
LAYER_ENEMY_PROJECTILE  = 'enemy_projectile'
LAYER_PICKUP            = 'pickup'
LAYER_TRIGGER           = 'trigger'
LAYER_DESTRUCTIBLE      = 'destructible'
LAYER_NPC               = 'npc'

# Groups that a player-fired weapon raycast should register hits on.
# Mirrors GDScript collision_mask layers 1 | 4 | 128.
PLAYER_WEAPON_HITTABLE = frozenset({
    LAYER_ENVIRONMENT,
    LAYER_ENEMY,
    LAYER_DESTRUCTIBLE,
})
