class_name EventBusClass
extends Node
## Global signal bus for cross-system communication.
## Systems connect to these signals instead of calling each other directly.

# Combat
signal damage_dealt(damage_info: Resource)
signal entity_died(entity: Node3D, killer: Node3D)

# Items & Inventory
signal item_picked_up(item: Resource, picker: Node3D)
signal weapon_switched(weapon_index: int)

# Progression
signal quest_updated(quest: Resource, status: int)
signal player_leveled_up(new_level: int)
signal xp_gained(amount: int)

# World
signal zone_entered(zone_name: String)
signal destructible_broken(object: Node3D, damage_info: Resource)

# Player state
signal player_health_changed(current: float, maximum: float)
signal player_ammo_changed(current: int, max_ammo: int)
signal player_died()
signal player_respawned()
