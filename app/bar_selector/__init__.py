"""
Bar Selector Module
------------------
Provides screen selection and bar detection functionality.
"""

from .screen_selector import ScreenSelector
from .bar_detector import BarDetector
from .color_ranges import HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE

__all__ = [
    'ScreenSelector',
    'BarDetector', 
    'HEALTH_COLOR_RANGE',
    'MANA_COLOR_RANGE', 
    'STAMINA_COLOR_RANGE'
]