# Project Scope: 3D Open World RPG Shooter

## Overview

A third-person 3D RPG shooter with destructible environments, set in a hub-and-zones open world with low-poly/stylized art.

**Engine:** Godot 4 (GDScript)
**Art Style:** Low-poly / stylized (primitives + free asset packs like Kenney)
**World Structure:** Central hub with distinct connected zones
**Perspective:** Third-person camera

---

## Core Pillars

1. **Third-Person Shooter** — Satisfying movement and gunplay with multiple weapon types
2. **RPG Progression** — Stats, leveling, inventory, quests that make the player feel growth
3. **Destructible Environments** — Breakable objects and structures that affect gameplay and exploration
4. **Explorable World** — A hub with connected zones, each with distinct identity and challenges

---

## Technology: Why Godot 4

- **GDScript** is syntactically close to Python (indentation-based, duck-typed, similar keywords)
- **All project files are plain text** — `.gd` scripts, `.tscn` scenes, `.tres` resources — fully AI-readable and AI-writable
- **No GUI dependency** for development — CLI builds, headless exports, text-based everything
- Built-in 3D features: `CharacterBody3D`, `SpringArm3D`, `RayCast3D`, CSG nodes, physics, animation trees
- Open source, free, actively maintained

---

## Milestone 1: Core Loop — "Move, Shoot, Kill"

**Goal:** Validate that the core movement and combat feel good.

| Feature | Godot Approach |
|---|---|
| Player character (3rd person) | `CharacterBody3D` + `SpringArm3D` + `Camera3D` |
| WASD movement, sprint, jump | Input map + `_physics_process()` |
| Mouse-look camera | `SpringArm3D` rotation on input |
| One weapon (rifle) | `RayCast3D` or projectile `RigidBody3D` |
| Aiming / crosshair | Screen-center crosshair + ray from camera |
| Basic enemy | `CharacterBody3D` + simple state machine (idle → chase → attack → dead) |
| Health system | HP variable on player and enemies, damage signals |
| Test arena | Static `MeshInstance3D` geometry, flat ground |
| HUD | `Control` nodes: health bar, crosshair, ammo count |
| Pause menu | `Control` overlay, `get_tree().paused = true` |

**Deliverable:** A playable arena where you run around in third person, shoot a rifle at enemies, and they die.

---

## Milestone 2: RPG Foundation — "Grow Stronger"

**Goal:** Add progression systems that give combat meaning.

| Feature | Godot Approach |
|---|---|
| Stats (HP, stamina, damage, armor) | Custom `Resource` classes (`StatBlock`) |
| XP and leveling | XP counter, level thresholds, stat point allocation |
| Inventory system | `Resource`-based items, `Array` container, UI grid |
| 3-4 weapon types | Rifle, shotgun, pistol, melee — each a scene with unique behavior |
| Weapon equip/swap | Inventory slots, `Node3D` attachment points on player |
| Consumables | Health potions, ammo pickups — `Resource` items with `use()` |
| Simple quests | Accept from NPC → kill N enemies / find item → return for reward |
| NPC dialogue | Text-based branching via `Resource` dialogue trees |
| UI panels | Inventory screen, character stats, quest log |
| Loot drops | Enemies drop `Area3D` pickups on death |

**Deliverable:** Kill enemies to earn XP, level up stats, find loot, equip weapons, complete a simple quest.

---

## Milestone 3: World Building — "Explore and Destroy"

**Goal:** Replace the test arena with an actual explorable world.

| Feature | Godot Approach |
|---|---|
| Hub area (town/camp) | Hand-crafted scene with NPCs, shops, quest givers |
| 3-4 connected zones | Distinct scenes: forest, ruins, cave, wasteland |
| Zone transitions | `Area3D` triggers at zone boundaries, scene loading |
| Destructible objects | Pre-fractured meshes (crates, walls, pillars) that break on impact |
| Destructible structures | CSG subtraction for holes in walls; mesh-swap for larger destruction |
| Environmental hazards | Explosive barrels, collapsing floors, falling debris |
| Minimap | Viewport-based top-down camera rendered to `TextureRect` |
| Save/load system | `ResourceSaver` / `ResourceLoader` for player state + world state |
| Enemy variety | 3-4 enemy types per zone with different behaviors |
| Boss encounters | One per zone, unique attack patterns |

**Deliverable:** A connected world with a hub, 3-4 zones, destructible environments, varied enemies, and persistence.

---

## Milestone 4: Polish — "Make It Feel Good"

**Goal:** Juice, content, and quality-of-life.

| Feature | Notes |
|---|---|
| Skill tree or perks | Unlock abilities (double jump, dash, explosive rounds) |
| Crafting | Combine loot into consumables or weapon upgrades |
| Sound effects | Gunshots, impacts, footsteps, ambient |
| Music | Per-zone ambient tracks |
| Particle effects | Muzzle flash, bullet impacts, explosions, destruction debris |
| Screen effects | Damage vignette, hit markers, low-health warning |
| Enemy AI improvements | Flanking, cover-seeking, group coordination |
| Quest chains | Multi-step narratives across zones |
| Settings menu | Volume, mouse sensitivity, graphics quality |
| Performance profiling | Optimize draw calls, physics, LOD |

---

## Project Structure

```
exploration/
├── game/                          # Godot project root
│   ├── project.godot              # Engine config, input maps, autoloads
│   ├── .gitignore                 # Ignore .godot/ cache directory
│   │
│   ├── scenes/
│   │   ├── player/
│   │   │   ├── player.tscn        # Player scene (character + camera rig)
│   │   │   └── player.gd          # Movement, input, camera, shooting
│   │   ├── enemies/
│   │   │   ├── base_enemy.tscn
│   │   │   ├── base_enemy.gd      # Base enemy state machine
│   │   │   └── enemy_types/       # Specific enemy variations
│   │   ├── weapons/
│   │   │   ├── weapon_base.gd     # Base weapon class
│   │   │   ├── rifle.tscn
│   │   │   ├── shotgun.tscn
│   │   │   └── melee.tscn
│   │   ├── world/
│   │   │   ├── hub.tscn           # Central hub / town
│   │   │   ├── zones/             # Individual zone scenes
│   │   │   └── destructibles/     # Pre-fractured breakable objects
│   │   ├── ui/
│   │   │   ├── hud.tscn           # In-game HUD
│   │   │   ├── hud.gd
│   │   │   ├── inventory_panel.tscn
│   │   │   ├── quest_log.tscn
│   │   │   └── pause_menu.tscn
│   │   └── npcs/
│   │       ├── npc_base.tscn
│   │       └── dialogue_ui.tscn
│   │
│   ├── scripts/
│   │   ├── autoload/
│   │   │   ├── game_manager.gd    # Singleton: game state, scene transitions
│   │   │   └── event_bus.gd       # Singleton: global signal bus
│   │   └── resources/
│   │       ├── item_resource.gd   # Item data definition
│   │       ├── stat_block.gd      # Character stats resource
│   │       ├── quest_resource.gd  # Quest data definition
│   │       └── dialogue_resource.gd
│   │
│   └── assets/
│       ├── models/                # 3D models (.glb / .obj)
│       ├── textures/              # Textures and materials
│       ├── audio/                 # Sound effects and music
│       └── fonts/                 # UI fonts
│
├── GAME_PLAN.md                   # This file
└── README.md
```

---

## Art & Asset Strategy

Since we're going low-poly/stylized:

- **Milestone 1:** Use Godot primitives (boxes, capsules, cylinders) for everything. Player = capsule, enemies = colored boxes, arena = flat plane with walls.
- **Milestone 2:** Same primitives but with basic materials/colors to distinguish items and weapons.
- **Milestone 3:** Introduce free low-poly asset packs (Kenney, Quaternius, Godot Asset Library) for terrain, buildings, props. Replace primitives gradually.
- **Milestone 4:** Custom materials, particle effects, and visual polish.

This approach means we can start building immediately without waiting for art.

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| GDScript learning curve (it's not Python) | Syntax is 90% similar; main differences are Godot-specific APIs. Learn as we go. |
| Destructible env performance | Use pre-fractured meshes (break into pre-defined pieces), not real-time CSG for most objects. Reserve CSG for scripted moments. |
| Scope creep | Milestones are ordered by priority. Each milestone is playable on its own. Cut from the bottom. |
| No 3D art skills | Low-poly style + free assets + primitives. Art is the last priority. |
| Godot 4 bugs / missing features | Godot 4.x is stable and actively patched. GDScript is mature. |

---

## What We're NOT Building (Out of Scope)

- Multiplayer / networking
- Procedural world generation
- Realistic graphics / PBR materials
- Mobile or console ports
- Mod support
- Cutscenes or voice acting
- Physics-based vehicles

---

## Next Step

Set up the Godot 4 project structure and build Milestone 1: player controller, third-person camera, basic weapon, test enemy, test arena.
