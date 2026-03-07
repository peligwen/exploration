class_name Rifle
extends WeaponBase
## Standard rifle. Medium damage, moderate fire rate, low spread.


func _ready() -> void:
	weapon_name = "Rifle"
	damage = 15.0
	fire_rate = 0.12
	max_ammo = 30
	reload_time = 1.8
	spread = 0.5
	range_distance = 150.0
	super._ready()
