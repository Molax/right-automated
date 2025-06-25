"""
Color Range Definitions
----------------------
Defines HSV color ranges for detecting different bar types.
"""

import numpy as np

HEALTH_COLOR_RANGE = (
    np.array([0, 50, 50]),
    np.array([10, 255, 255])
)

MANA_COLOR_RANGE = (
    np.array([100, 50, 50]),
    np.array([140, 255, 255])
)

STAMINA_COLOR_RANGE = (
    np.array([40, 50, 50]),
    np.array([80, 255, 255])
)