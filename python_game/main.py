"""Exploration RPG — Python/Ursina port.
Entry point. Run this file to start the game.
"""
import sys
import os

# Add python_game to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ursina import Ursina, window, color, application, DirectionalLight, AmbientLight, Vec3

# Create the app first
app = Ursina(
    title='Exploration RPG',
    borderless=False,
    fullscreen=False,
    development_mode=True,
)

# Window settings
window.size = (1280, 720)
window.fps_counter.enabled = True

# Lighting
DirectionalLight(y=10, rotation=(45, -45, 0))
AmbientLight(color=color.color(0, 0, 0.3))

# Create the test arena
from scenes.world.test_arena import create_test_arena

player, enemies, hud, pause_menu = create_test_arena()


def input(key):
    """Global input handler."""
    if key == 'escape':
        pause_menu.toggle_pause()


# Run
app.run()
