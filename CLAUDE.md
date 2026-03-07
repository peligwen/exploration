# CLAUDE.md — AI Assistant Guide for the Exploration RPG

This file provides context for AI assistants working on this codebase. Read it before making any changes.

---

## Project Overview

**Exploration RPG** is a Godot 4 third-person shooter/RPG developed through "vibe coding" — an AI-assisted workflow where intent is described at a high level and the AI handles implementation. The project uses Godot 4.4 with GDScript throughout.

The game is controller-first but fully supports keyboard + mouse. Core pillars: fluid movement, satisfying combat, meaningful exploration, light RPG progression.

---

## Repository Layout

```
exploration/
├── CLAUDE.md          ← this file
├── README.md          ← project overview
├── GAME_PLAN.md       ← full design doc; read before adding features
└── game/              ← Godot project root (open this in the editor)
    ├── project.godot
    ├── scenes/
    │   ├── player/
    │   │   ├── player.tscn / player.gd
    │   │   ├── camera_controller.gd
    │   │   ├── aim_assist.gd
    │   │   └── states/          ← 10 player state files
    │   ├── enemies/
    │   │   ├── base_enemy.tscn / base_enemy.gd
    │   │   └── states/          ← 6 enemy state files
    │   ├── weapons/
    │   │   ├── weapon_base.gd   ← abstract base; extend this for new weapons
    │   │   └── rifle.gd / rifle.tscn
    │   ├── world/
    │   │   └── test_arena.tscn  ← Milestone 1 test level
    │   └── ui/
    │       ├── hud.tscn / hud.gd
    │       └── pause_menu.tscn / pause_menu.gd
    ├── scripts/
    │   ├── autoload/            ← global singletons
    │   │   ├── event_bus.gd
    │   │   ├── input_manager.gd
    │   │   └── game_manager.gd
    │   ├── components/          ← reusable, node-based components
    │   │   ├── state_machine.gd
    │   │   ├── state.gd
    │   │   └── health_component.gd
    │   └── resources/           ← data resources
    │       └── damage_info.gd
    └── assets/
        └── themes/
            └── game_theme.tres  ← master UI theme
```

---

## Running the Project

There are no build scripts. This is a pure Godot project.

```bash
# Run from editor
godot --path game/

# Or open game/ in the Godot 4.4 editor
```

No unit test framework is used. Testing is scene-based: run `test_arena.tscn` and validate behaviour manually. Milestone acceptance criteria are listed in `GAME_PLAN.md`.

---

## Architecture — The 8 Foundations

Every significant system is built on one or more of these eight pillars. Understand them before adding new code.

### 1. EventBus (`scripts/autoload/event_bus.gd`)
Global signal bus for all cross-system communication. Never use direct node references for cross-system events — emit and connect through EventBus instead.

```gdscript
# emit
EventBus.damage_dealt.emit(damage_info)
# connect
EventBus.entity_died.connect(_on_entity_died)
```

Key signals: `damage_dealt`, `entity_died`, `item_picked_up`, `weapon_switched`, `xp_gained`, `quest_updated`.

### 2. InputManager (`scripts/autoload/input_manager.gd`)
Abstracts all input. Detects active device (controller vs KB+M) and exposes unified vectors. Never call `Input.get_axis()` or `Input.is_action_pressed()` directly in gameplay code — use InputManager.

```gdscript
var move := InputManager.get_move_vector()   # returns Vector2, works for both devices
var look := InputManager.get_look_vector()   # returns Vector2
InputManager.request_haptic(0.5, 0.2, 0.3)  # scaled by user vibration setting
```

### 3. GameManager (`scripts/autoload/game_manager.gd`)
Tracks game state, manages scene transitions, and maintains the saveable registry. Use it to change scenes and register objects that need to be saved.

### 4. StateMachine + State (`scripts/components/`)
Generic state machine used by both Player and enemies. States are `Node` children of the state machine node and are auto-discovered. Each state implements:

```gdscript
func enter(msg: Dictionary = {}) -> void: ...
func exit() -> void: ...
func update(delta: float) -> void: ...
func physics_update(delta: float) -> void: ...
func handle_input() -> void: ...
```

Request transitions with `state_machine.transition_to("StateName", {optional_data})`. Never bypass the state machine to set state directly.

### 5. HealthComponent (`scripts/components/health_component.gd`)
Reusable HP node. Attach to any entity. Handles i-frames, damage application, and death signaling. Always use `health_component.take_damage(damage_info)` — never modify HP directly.

### 6. DamageInfo (`scripts/resources/damage_info.gd`)
Structured `Resource` passed with every damage event. Fields: `amount`, `type` (physical/energy/etc.), `source_entity`, `knockback_direction`, `is_crit`. Use the static factory:

```gdscript
var dmg := DamageInfo.create(15.0, "physical", self, direction)
```

### 7. CameraController (`scenes/player/camera_controller.gd`)
Independent camera node with four modes: `Follow`, `Aim`, `Shake`, `Death`. Transitions are requested by player states, not driven externally. Do not parent game cameras to the player node directly.

### 8. Physics Collision Layers (defined in `project.godot`)
Nine layers are pre-defined. Always use layer names, never raw numbers.

| Layer | Name |
|-------|------|
| 1 | Environment |
| 2 | Player |
| 3 | Enemy |
| 4 | PlayerProjectile |
| 5 | EnemyProjectile |
| 6 | Pickup |
| 7 | Trigger |
| 8 | Destructible |
| 9 | NPC |

---

## GDScript Conventions

### Naming
- Classes: `PascalCase` with `class_name` declaration at top of file
- Methods and variables: `snake_case`
- Signals: past-tense snake_case (`damage_dealt`, `entity_died`)
- Constants: `UPPER_SNAKE_CASE`
- Private members: prefix with `_` (`_current_ammo`)

### File structure order
```gdscript
class_name MyClass
extends BaseClass

# signals
signal something_happened

# constants & enums
const MAX_VALUE := 100

# exported vars (tunable in editor)
@export var speed: float = 5.0

# onready vars (node references)
@onready var mesh: MeshInstance3D = $Mesh

# private vars
var _state: String = ""

# lifecycle methods (_ready, _process, _physics_process, _input)
# public methods
# private methods (prefixed with _)
```

### Key patterns
- Use `@export` for any value that might be tuned — avoid magic numbers in logic.
- Use `@onready` for all child node references; avoid `get_node()` calls scattered through methods.
- Input: always camera-relative for movement. `InputManager.get_move_vector()` returns local space; rotate by camera's Y basis before applying to the character.
- Signals: define at the top of the emitting script; connect in `_ready()` of the receiver.
- Type hints everywhere: `var speed: float`, `func shoot(target: Node3D) -> void`.

---

## Adding New Features

### New weapon
1. Extend `WeaponBase` (`scenes/weapons/weapon_base.gd`).
2. Override `_fire()`, set exported stats (`damage`, `fire_rate`, `ammo_capacity`, `reload_time`).
3. Create a `.tscn` scene for it.
4. Register it in the weapon radial menu (M2 feature).

### New player state
1. Create `player_<name>.gd` in `scenes/player/states/`, extending `State`.
2. Implement `enter`, `exit`, `update`, `physics_update`, `handle_input`.
3. Add the scene node as a child of the StateMachine node in `player.tscn`.
4. Add transition calls in adjacent states as needed.

### New enemy type
1. Extend `BaseEnemy` or duplicate `base_enemy.tscn`.
2. Override exported stats and add specialised states if needed.
3. Place in `scenes/enemies/`.

### New UI screen
1. Create `.tscn` + `.gd` in `scenes/ui/`.
2. Apply `game_theme.tres` as the root Control's theme.
3. Connect signals through EventBus rather than direct scene references.
4. Handle `InputManager.device_changed` signal to swap controller/KB+M prompts.

### New autoload
Only add autoloads for truly global, stateful systems. Register in `project.godot` under `[autoload]`. Autoloads initialise in the order listed — place dependencies after their dependents.

---

## Milestone Status

| Milestone | Goal | Status |
|-----------|------|--------|
| M1 | Core loop — Move, Shoot, Kill | **Complete** |
| M2 | RPG Foundation — inventory, XP, weapons | Planned |
| M3 | World Building — hub, zones, NPCs | Planned |
| M4 | Polish — audio, VFX, skill trees | Planned |

Current work happens in `test_arena.tscn`. New zones and the hub world are M3 scope.

See `GAME_PLAN.md` for full feature lists and acceptance criteria per milestone.

---

## What NOT to Do

- **Do not** write `Input.get_action_strength()` in gameplay scripts — use `InputManager`.
- **Do not** emit damage by modifying HP directly — always go through `HealthComponent.take_damage()`.
- **Do not** use hard-coded collision layer numbers — use the named layer constants.
- **Do not** create cross-system dependencies by storing direct node references across scenes — use EventBus signals.
- **Do not** add M2/M3 features to M1 files — keep scope per milestone.
- **Do not** bypass the state machine (e.g., setting a `current_state` variable manually) — call `transition_to()`.
- **Do not** add editor-only debug code to production scripts — use `if OS.is_debug_build():` guards.

---

## Git Workflow

Branches follow the pattern `claude/<description>-<id>`. One branch per task/PR. Commit messages are imperative, present-tense ("Add rifle reload animation"), not past-tense.

```bash
git checkout -b claude/<task-description>-<id>
# make changes
git add <specific files>
git commit -m "Descriptive message"
git push -u origin <branch-name>
```

Do not push directly to `main`. All changes go through pull requests.

---

## Quick Reference

| Need to… | Look at… |
|----------|----------|
| Add a signal | `event_bus.gd` |
| Read controller/KB+M input | `input_manager.gd` |
| Change game state / scene | `game_manager.gd` |
| Add player behaviour | `scenes/player/states/` |
| Add enemy behaviour | `scenes/enemies/states/` |
| Damage an entity | `health_component.gd` + `damage_info.gd` |
| Add a new weapon | extend `weapon_base.gd` |
| Style a UI element | `assets/themes/game_theme.tres` |
| Understand full design | `GAME_PLAN.md` |
