# Project Scope: 3D Open World RPG Shooter

## Overview

A third-person 3D RPG shooter with destructible environments, set in a hub-and-zones open world with low-poly/stylized art.

**Engine:** Godot 4 (GDScript)
**Art Style:** Low-poly / stylized (primitives + free asset packs like Kenney)
**World Structure:** Central hub with distinct connected zones
**Perspective:** Third-person camera
**Input:** Controller-first design, with keyboard+mouse as a full alternative

---

## Core Pillars

1. **Third-Person Shooter** — Satisfying movement and gunplay with multiple weapon types
2. **RPG Progression** — Stats, leveling, inventory, quests that make the player feel growth
3. **Destructible Environments** — Breakable objects and structures that affect gameplay and exploration
4. **Explorable World** — A hub with connected zones, each with distinct identity and challenges
5. **Comfy Controls** — Controller-first design with radial menus, aim assist, and seamless input switching

---

## Technology: Why Godot 4

- **GDScript** is syntactically close to Python (indentation-based, duck-typed, similar keywords)
- **All project files are plain text** — `.gd` scripts, `.tscn` scenes, `.tres` resources — fully AI-readable and AI-writable
- **No GUI dependency** for development — CLI builds, headless exports, text-based everything
- Built-in 3D features: `CharacterBody3D`, `SpringArm3D`, `RayCast3D`, CSG nodes, physics, animation trees
- Open source, free, actively maintained

---

## Input & UX Design — "Controller-First, Comfy Always"

### Design Philosophy

The game is designed **controller-first** — every interaction must feel natural on a gamepad. Keyboard+mouse is a fully supported alternative, not an afterthought. The game detects input device automatically and swaps button prompts in real time (no restart, no menu toggle).

Think: *Breath of the Wild* comfort, *Ratchet & Clank* weapon switching, *Mass Effect* power wheel pacing.

### Controller Layout (Gamepad)

```
┌─────────────────────────────────────────────────────┐
│                  GAMEPAD LAYOUT                     │
│                                                     │
│   [LB] Radial: Weapons      [RB] Radial: Items     │
│   [LT] Aim / Zoom           [RT] Fire / Attack      │
│                                                     │
│   [L Stick] Move / Sprint(click)                    │
│   [R Stick] Camera / Look                           │
│                                                     │
│   [A] Jump / Confirm        [B] Dodge Roll / Back   │
│   [X] Interact / Reload     [Y] Melee / Alt-fire    │
│                                                     │
│   [D-pad Up] Quest Log      [D-pad Down] Map        │
│   [D-pad L/R] Quick swap last 2 weapons             │
│                                                     │
│   [Start] Pause Menu        [Select] Character Sheet│
└─────────────────────────────────────────────────────┘
```

### Keyboard + Mouse Layout

| Action | Key | Notes |
|---|---|---|
| Move | WASD | |
| Sprint | Left Shift (hold) | |
| Jump | Space | |
| Dodge Roll | Left Ctrl / Double-tap direction | |
| Look / Aim | Mouse movement | |
| Fire | Left Mouse Button | |
| Aim / Zoom | Right Mouse Button | |
| Melee / Alt-fire | V | |
| Interact / Reload | E / R | Context-sensitive |
| Weapon Radial | Q (hold) | Mouse selects from wheel |
| Item Radial | Tab (hold) | Mouse selects from wheel |
| Quick swap weapons | Mouse Scroll / 1-4 keys | |
| Quest Log | J | |
| Map | M | |
| Character Sheet | C | |
| Inventory | I | |
| Pause | Escape | |

### Radial Menus

Radial menus are the core UI interaction — they replace traditional grid inventories during gameplay.

**How they work:**
- **Controller:** Hold LB/RB → right stick selects a wedge → release to confirm. Time slows (bullet-time at ~20% speed) while radial is open so you can think without pausing.
- **KB+Mouse:** Hold Q/Tab → mouse cursor appears and selects a wedge → release to confirm. Same bullet-time effect.
- Wedges are large and forgiving — 4 to 8 items max per wheel. No fiddly small targets.
- Each wedge shows an icon + name + brief stat (e.g., "Rifle — 24/60" or "Health Potion — x3").
- Selected wedge highlights with a smooth scale-up animation. Subtle haptic pulse on controller when crossing wedge boundaries.

**Radial types:**
| Radial | Trigger | Content | Slots |
|---|---|---|---|
| Weapon Wheel | LB / Q | Equipped weapons | 4-6 wedges |
| Item Wheel | RB / Tab | Quick-use items (potions, grenades, buffs) | 4-8 wedges |
| Emote/Interact Wheel | Hold X / Hold E (near NPC) | Context actions, dialogue choices | 3-6 wedges |

**Radial UX details:**
- Center of radial = "cancel" (don't switch). Release stick/mouse in the center deadzone to dismiss without selecting.
- Recently used item/weapon gets a subtle glow so you can re-select it fast.
- When an item runs out (0 potions), wedge grays out but stays visible so muscle memory isn't disrupted.
- Customizable: players can assign items/weapons to specific wedge positions.

### Aim Assist (Controller)

Controller aiming needs help. Three layers, all tunable:

1. **Sticky aim** — When crosshair is near an enemy, camera rotation slows down slightly (friction). Makes tracking easier without feeling "magnetic."
2. **Snap assist** — When entering aim mode (LT), crosshair nudges toward nearest enemy if one is close to center screen. Subtle, not aggressive.
3. **Bullet magnetism** — Projectiles curve very slightly toward enemies near the aim line. Invisible to the player, just makes shots feel more satisfying.

All three can be individually toggled/scaled in settings. KB+Mouse gets none of these by default.

### Input Detection & Prompt Switching

- Godot's `Input` system detects the last-used input device automatically.
- On any gamepad input → all UI prompts switch to controller glyphs (Xbox style by default, PlayStation glyphs if DualSense detected).
- On any KB+Mouse input → prompts switch to key labels.
- Transition is instant and seamless — no "switch input mode" setting.
- Controller glyphs use simple, clean icons (filled shapes: ●/■/▲/✕ for PlayStation, A/B/X/Y colored for Xbox).

### Camera & Movement Feel

These details make controller play feel "comfy":

- **Camera smoothing** — `SpringArm3D` with slight lerp on rotation. Not laggy, just smooth. Adjustable sensitivity.
- **Sprint is hold, not toggle** — L-stick click to sprint, release to stop. Less cognitive load.
- **Auto-run option** — Double-click L-stick to toggle auto-run for long traversal.
- **Gentle auto-camera** — Camera slowly re-centers behind player during movement (not during combat). Can be disabled.
- **Aim mode camera** — LT shifts camera to over-the-shoulder (slight offset right). Zooms in slightly. Movement slows to strafe-walk.
- **Dodge roll has i-frames** — Brief invincibility during the roll animation. Forgiving window.
- **Coyote time on jumps** — ~100ms window to jump after walking off an edge. Prevents frustrating missed jumps.
- **Input buffering** — If you press jump/dodge during another animation, it queues and fires when possible. No eaten inputs.

### Controller Haptics & Feedback

- Weapon fire → short, sharp rumble scaled to weapon power
- Taking damage → distinct rumble pattern (different from firing)
- Radial wedge crossing → light pulse
- Low health → rhythmic subtle pulse (heartbeat)
- Explosion/destruction nearby → heavy rumble
- All haptics are optional with intensity slider in settings

### Accessibility & Settings

| Setting | Options |
|---|---|
| Stick sensitivity | Slider (camera X and Y separate) |
| Stick deadzone | Slider per stick |
| Aim assist strength | Off / Low / Medium / High |
| Invert Y axis | Toggle (separate for each input method) |
| Vibration intensity | Off → Max slider |
| Sprint toggle vs hold | Toggle |
| Auto-center camera | Toggle |
| Button remapping | Full remap for controller and KB+M |
| Radial slow-mo speed | Slider (0% = full pause, 100% = no slowdown) |
| Colorblind mode | Protanopia / Deuteranopia / Tritanopia filters |
| HUD scale | Slider |
| Subtitle size | Small / Medium / Large |

---

## Milestone 1: Core Loop — "Move, Shoot, Kill"

**Goal:** Validate that the core movement and combat feel good.

| Feature | Godot Approach |
|---|---|
| Player character (3rd person) | `CharacterBody3D` + `SpringArm3D` + `Camera3D` |
| Controller movement + camera | Dual-stick input via Input map, lerped camera smoothing |
| KB+Mouse movement + camera | WASD + mouse look, same Input actions with dual bindings |
| Sprint, jump, dodge roll | L-stick click / Shift, A / Space, B / Ctrl — with coyote time + input buffering |
| Aim mode (over-shoulder) | LT / RMB shifts camera offset, zooms slightly, slows movement |
| One weapon (rifle) | `RayCast3D` or projectile `RigidBody3D` |
| Aim assist (controller) | Sticky aim + snap-to-target on LT. Tunable in settings |
| Crosshair | Screen-center, adapts to weapon spread |
| Auto input detection | Detect last device, swap UI prompts (glyphs ↔ key labels) instantly |
| Basic enemy | `CharacterBody3D` + simple state machine (idle → chase → attack → dead) |
| Health system | HP variable on player and enemies, damage signals |
| Controller haptics | Rumble on fire, damage, low health pulse |
| Test arena | Static `MeshInstance3D` geometry, flat ground |
| HUD | `Control` nodes: health bar, crosshair, ammo — button prompts swap with input device |
| Pause menu | `Control` overlay, `get_tree().paused = true`, navigable with controller |
| Settings (input) | Stick sensitivity, deadzone, invert Y, aim assist toggle, vibration slider |

**Deliverable:** A playable arena that feels great on a controller — smooth camera, aim assist, rumble feedback. Equally playable on KB+Mouse.

---

## Milestone 2: RPG Foundation — "Grow Stronger"

**Goal:** Add progression systems that give combat meaning.

| Feature | Godot Approach |
|---|---|
| Stats (HP, stamina, damage, armor) | Custom `Resource` classes (`StatBlock`) |
| XP and leveling | XP counter, level thresholds, stat point allocation |
| Inventory system | `Resource`-based items, `Array` container, UI grid |
| 3-4 weapon types | Rifle, shotgun, pistol, melee — each a scene with unique behavior |
| Weapon Radial (LB / Q) | Hold to open wheel, right stick / mouse to select, release to equip. Bullet-time while open |
| Item Radial (RB / Tab) | Same UX for quick-use consumables (potions, grenades, buffs) |
| Weapon equip/swap | Radial wheel + D-pad L/R quick swap between last 2 weapons |
| Consumables | Health potions, ammo pickups — `Resource` items with `use()` |
| Simple quests | Accept from NPC → kill N enemies / find item → return for reward |
| NPC dialogue | Branching via `Resource` dialogue trees, selectable with stick/D-pad or mouse |
| UI panels | Inventory screen, character stats, quest log — all fully controller-navigable |
| Loot drops | Enemies drop `Area3D` pickups on death, contextual interact prompt (X / E) |

**Deliverable:** Kill enemies to earn XP, level up stats, use radial menus to swap weapons and items mid-combat, complete a simple quest. All menus navigable by controller.

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
| Settings menu | Volume, sensitivity, graphics, full controller + KB+M remap |
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
│   │   │   ├── player.gd          # Movement, input, camera, shooting
│   │   │   └── aim_assist.gd      # Sticky aim, snap, bullet magnetism
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
│   │   │   ├── radial_menu.tscn   # Reusable radial wheel component
│   │   │   ├── radial_menu.gd     # Wedge selection, bullet-time, animations
│   │   │   ├── input_prompts.gd   # Swap glyphs/key labels based on device
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
│   │   │   ├── event_bus.gd       # Singleton: global signal bus
│   │   │   └── input_manager.gd   # Singleton: device detection, prompt type, settings
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
