class_name DamageInfo
extends Resource
## Structured damage data passed through the EventBus.

enum DamageType { PHYSICAL, FIRE, EXPLOSIVE, FALL }

@export var amount: float = 0.0
@export var damage_type: DamageType = DamageType.PHYSICAL
@export var hit_position: Vector3 = Vector3.ZERO
@export var knockback_force: Vector3 = Vector3.ZERO
@export var is_critical: bool = false

## Set at runtime, not exported (node refs can't be serialized)
var source: Node3D = null


static func create(
	p_amount: float,
	p_source: Node3D = null,
	p_type: DamageType = DamageType.PHYSICAL,
	p_hit_pos: Vector3 = Vector3.ZERO,
	p_knockback: Vector3 = Vector3.ZERO,
	p_crit: bool = false
) -> DamageInfo:
	var info := DamageInfo.new()
	info.amount = p_amount
	info.source = p_source
	info.damage_type = p_type
	info.hit_position = p_hit_pos
	info.knockback_force = p_knockback
	info.is_critical = p_crit
	return info
