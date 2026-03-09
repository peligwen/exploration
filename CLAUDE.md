# CLAUDE.md — AI Assistant Guide for the Exploration RPG

This file provides context for AI assistants working on this codebase. Read it before making any changes.

---

## Project Overview

**Exploration RPG** is a Python/Ursina third-person shooter/RPG developed through "vibe coding" — an AI-assisted workflow where intent is described at a high level and the AI handles implementation. The project uses Python 3 with the [Ursina Engine](https://www.ursinaengine.org/).

The game is keyboard + mouse first. Core pillars: fluid movement, satisfying combat, meaningful exploration, light RPG progression.

---

## Repository Layout

```
exploration/
├── CLAUDE.md          ← this file
├── README.md          ← project overview
├── GAME_PLAN.md       ← full design doc; read before adding features
└── python_game/       ← Python/Ursina project root
    ├── main.py        ← entry point; run this to start the game
    ├── requirements.txt
    ├── scenes/
    │   ├── player/
    │   │   ├── player.py
    │   │   ├── camera_controller.py
    │   │   └── states/          ← 10 player state files
    │   ├── enemies/
    │   │   ├── base_enemy.py
    │   │   └── states/          ← 6 enemy state files
    │   ├── weapons/
    │   │   ├── weapon_base.py   ← abstract base; extend this for new weapons
    │   │   └── rifle.py
    │   ├── world/
    │   │   └── test_arena.py    ← Milestone 1 test level
    │   └── ui/
    │       ├── hud.py
    │       └── pause_menu.py
    └── scripts/
        ├── autoload/            ← global singletons
        │   ├── event_bus.py
        │   ├── input_manager.py
        │   └── game_manager.py
        ├── components/          ← reusable components
        │   ├── state_machine.py
        │   ├── state.py
        │   └── health_component.py
        └── resources/           ← data classes
            └── damage_info.py
```

---

## Running the Project

```bash
cd python_game
pip install -r requirements.txt
python main.py
```

No unit test framework is used. Testing is done by running the game directly. Milestone acceptance criteria are listed in `GAME_PLAN.md`.

---

## Architecture — The 8 Foundations

Every significant system is built on one or more of these eight pillars.

### 1. EventBus (`scripts/autoload/event_bus.py`)
Global signal bus for all cross-system communication. Never use direct object references for cross-system events — emit and connect through EventBus instead.

```python
# emit
EventBus.emit('damage_dealt', damage_info)
# connect
EventBus.on('entity_died', self._on_entity_died)
```

Key events: `damage_dealt`, `entity_died`, `item_picked_up`, `weapon_switched`, `xp_gained`, `quest_updated`.

### 2. InputManager (`scripts/autoload/input_manager.py`)
Abstracts all input. Exposes unified movement and look vectors. Never call Ursina's `held_keys` or `mouse` directly in gameplay code — use InputManager.

```python
move = InputManager.get_move_vector()   # returns Vec2
look = InputManager.get_look_vector()   # returns Vec2
```

### 3. GameManager (`scripts/autoload/game_manager.py`)
Tracks game state and manages scene transitions.

### 4. StateMachine + State (`scripts/components/`)
Generic state machine used by both Player and enemies. States are registered by name. Each state implements:

```python
def enter(self, msg: dict = {}) -> None: ...
def exit(self) -> None: ...
def update(self, dt: float) -> None: ...
def handle_input(self) -> None: ...
```

Request transitions with `state_machine.transition_to('StateName', {})`. Never bypass the state machine to set state directly.

### 5. HealthComponent (`scripts/components/health_component.py`)
Reusable HP component. Attach to any entity. Handles i-frames, damage application, and death signaling. Always use `health_component.take_damage(damage_info)` — never modify HP directly.

### 6. DamageInfo (`scripts/resources/damage_info.py`)
Structured dataclass passed with every damage event. Fields: `amount`, `type` (physical/energy/etc.), `source_entity`, `knockback_direction`, `is_crit`. Use the factory:

```python
dmg = DamageInfo.create(15.0, 'physical', self, direction)
```

### 7. CameraController (`scenes/player/camera_controller.py`)
Independent camera with modes: `Follow`, `Aim`, `Shake`, `Death`. Transitions are requested by player states.

### 8. Collision Groups
Named groups are used throughout. Always use the constants, never raw strings.

| Constant | Value |
|----------|-------|
| `LAYER_ENVIRONMENT` | `'environment'` |
| `LAYER_PLAYER` | `'player'` |
| `LAYER_ENEMY` | `'enemy'` |
| `LAYER_PLAYER_PROJECTILE` | `'player_projectile'` |
| `LAYER_ENEMY_PROJECTILE` | `'enemy_projectile'` |
| `LAYER_PICKUP` | `'pickup'` |
| `LAYER_TRIGGER` | `'trigger'` |
| `LAYER_DESTRUCTIBLE` | `'destructible'` |
| `LAYER_NPC` | `'npc'` |

---

## Python/Ursina Conventions

### Naming
- Classes: `PascalCase`
- Methods and variables: `snake_case`
- Events: past-tense snake_case (`damage_dealt`, `entity_died`)
- Constants: `UPPER_SNAKE_CASE`
- Private members: prefix with `_` (`_current_ammo`)

### File structure order
```python
from ursina import *
from scripts.autoload.event_bus import EventBus

class MyClass(Entity):
    # class-level constants
    MAX_VALUE = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # exported/tunable attributes
        self.speed = 5.0
        # component references
        self.health = HealthComponent(self)
        # private state
        self._state = ''

    # lifecycle / Ursina callbacks (update, input, on_destroy)
    # public methods
    # private methods (prefixed with _)
```

### Key patterns
- Use instance attributes for any value that might be tuned — avoid magic numbers in logic.
- Input: always camera-relative for movement.
- Events: connect in `__init__` of the receiver via `EventBus.on(...)`.
- Type hints encouraged throughout.

---

## Adding New Features

### New weapon
1. Extend `WeaponBase` (`scenes/weapons/weapon_base.py`).
2. Override `_fire()`, set stats (`damage`, `fire_rate`, `ammo_capacity`, `reload_time`).
3. Register it in the weapon radial menu (M2 feature).

### New player state
1. Create `player_<name>.py` in `scenes/player/states/`, extending `State`.
2. Implement `enter`, `exit`, `update`, `handle_input`.
3. Register it with the StateMachine in `player.py`.
4. Add transition calls in adjacent states as needed.

### New enemy type
1. Extend `BaseEnemy` (`scenes/enemies/base_enemy.py`).
2. Override stats and add specialised states if needed.
3. Place in `scenes/enemies/`.

### New UI screen
1. Create a `.py` file in `scenes/ui/`.
2. Connect events through EventBus rather than direct object references.

### New global singleton
Only add singletons for truly global, stateful systems. Import them at the top of `main.py` and initialise before the game loop.

---

## Milestone Status

| Milestone | Goal | Status |
|-----------|------|--------|
| M1 | Core loop — Move, Shoot, Kill | **Complete** |
| M2 | RPG Foundation — inventory, XP, weapons | Planned |
| M3 | World Building — hub, zones, NPCs | Planned |
| M4 | Polish — audio, VFX, skill trees | Planned |

Current work runs in `test_arena.py`. New zones and the hub world are M3 scope.

See `GAME_PLAN.md` for full feature lists and acceptance criteria per milestone.

---

## What NOT to Do

- **Do not** read input via `held_keys` or `mouse` directly in gameplay scripts — use `InputManager`.
- **Do not** emit damage by modifying HP directly — always go through `HealthComponent.take_damage()`.
- **Do not** use hard-coded collision group strings — use the named layer constants.
- **Do not** create cross-system dependencies by storing direct object references across modules — use EventBus events.
- **Do not** add M2/M3 features to M1 files — keep scope per milestone.
- **Do not** bypass the state machine — call `transition_to()`.
- **Do not** add debug-only code without guarding it (e.g. `if __debug__:`).

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
| Add an event | `event_bus.py` |
| Read input | `input_manager.py` |
| Change game state / scene | `game_manager.py` |
| Add player behaviour | `scenes/player/states/` |
| Add enemy behaviour | `scenes/enemies/states/` |
| Damage an entity | `health_component.py` + `damage_info.py` |
| Add a new weapon | extend `weapon_base.py` |
| Understand full design | `GAME_PLAN.md` |
