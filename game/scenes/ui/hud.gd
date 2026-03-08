class_name HUD
extends CanvasLayer
## In-game HUD. Shows health bar, ammo, crosshair, and input-aware prompts.

@onready var health_bar: ProgressBar = $MarginContainer/VBoxContainer/HealthBar
@onready var health_label: Label = $MarginContainer/VBoxContainer/HealthBar/HealthLabel
@onready var ammo_label: Label = $MarginContainer/VBoxContainer/AmmoContainer/AmmoLabel
@onready var crosshair: TextureRect = $Crosshair
@onready var interact_prompt: Label = $InteractPrompt
@onready var state_label: Label = $StateLabel


func _ready() -> void:
	EventBus.player_health_changed.connect(_on_health_changed)
	EventBus.player_ammo_changed.connect(_on_ammo_changed)
	InputManager.device_changed.connect(_on_device_changed)

	# Initialize
	health_bar.value = 100
	_update_ammo_display(30, 30)


func _on_health_changed(current: float, maximum: float) -> void:
	health_bar.max_value = maximum
	health_bar.value = current
	health_label.text = "%d / %d" % [ceili(current), ceili(maximum)]

	# Color shift at low health
	if current / maximum < 0.25:
		health_bar.modulate = Color(1.0, 0.3, 0.3)
	elif current / maximum < 0.5:
		health_bar.modulate = Color(1.0, 0.8, 0.3)
	else:
		health_bar.modulate = Color(1.0, 1.0, 1.0)


func _on_ammo_changed(current: int, max_ammo: int) -> void:
	_update_ammo_display(current, max_ammo)


func _update_ammo_display(current: int, max_ammo: int) -> void:
	if current == 0:
		var reload_glyph := InputManager.get_action_glyph("reload")
		ammo_label.text = "0 / %d [%s]" % [max_ammo, reload_glyph]
		ammo_label.modulate = Color(1.0, 0.3, 0.3)
	elif current <= max_ammo * 0.25:
		ammo_label.text = "%d / %d" % [current, max_ammo]
		ammo_label.modulate = Color(1.0, 0.8, 0.3)
	else:
		ammo_label.text = "%d / %d" % [current, max_ammo]
		ammo_label.modulate = Color(1.0, 1.0, 1.0)


func _on_device_changed(_device: InputManagerClass.DeviceType) -> void:
	_refresh_prompts()


func _refresh_prompts() -> void:
	# Update any visible prompts to match current input device
	var reload_glyph := InputManager.get_action_glyph("reload")
	if ammo_label and ammo_label.text.ends_with("]"):
		# If showing reload prompt, replace the stale glyph with the current device's glyph
		var bracket_start := ammo_label.text.rfind("[")
		if bracket_start != -1:
			ammo_label.text = ammo_label.text.substr(0, bracket_start) + "[%s]" % reload_glyph

	if interact_prompt and interact_prompt.visible:
		var interact_glyph := InputManager.get_action_glyph("interact")
		# Re-format: replace the leading "[...] " glyph prefix
		var space_idx := interact_prompt.text.find("] ")
		if space_idx != -1:
			var prompt_text := interact_prompt.text.substr(space_idx + 2)
			interact_prompt.text = "[%s] %s" % [interact_glyph, prompt_text]


func show_interact_prompt(text: String) -> void:
	var glyph := InputManager.get_action_glyph("interact")
	interact_prompt.text = "[%s] %s" % [glyph, text]
	interact_prompt.visible = true


func hide_interact_prompt() -> void:
	interact_prompt.visible = false


func update_state_debug(state_name: String) -> void:
	if state_label:
		state_label.text = state_name
