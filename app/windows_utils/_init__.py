"""
Window Utilities Package for Priston Tale Potion Bot
---------------------------------------------------
This package provides utilities for window management and input simulation.
"""

# Import commonly used functions to make them available from the package
from app.window_utils import press_key
from app.window_utils import press_right_mouse
from app.window_utils import find_game_window, focus_game_window, get_window_rect

# Make all modules available for import
__all__ = ['keyboard', 'mouse', 'window_management', 'input_structures']