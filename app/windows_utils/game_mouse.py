"""
Enhanced Mouse Input Utilities for Priston Tale Potion Bot
-------------------------------------------------------
This module provides improved utilities for simulating mouse input in games.
Save this file as app/windows_utils/game_mouse.py
"""

import time
import logging
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32api

logger = logging.getLogger('PristonBot')

# Mouse event flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_WHEEL = 0x0800

def game_move_mouse(x, y, absolute=True):
    """
    Enhanced function to move mouse cursor with multiple methods for game compatibility
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        absolute: Whether coordinates are absolute screen coordinates
        
    Returns:
        True if successful, False otherwise
    """
    logger.debug(f"Moving game mouse to ({x}, {y})")
    
    try:
        # Convert to integers
        x, y = int(x), int(y)
        
        # Save original position
        orig_point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(orig_point))
        logger.debug(f"Original mouse position: ({orig_point.x}, {orig_point.y})")
        
        # Method 1: Direct SetCursorPos
        logger.debug(f"Using SetCursorPos")
        ctypes.windll.user32.SetCursorPos(x, y)
        time.sleep(0.05)
        
        # Verify position
        new_point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(new_point))
        if abs(new_point.x - x) <= 5 and abs(new_point.y - y) <= 5:
            logger.debug(f"SetCursorPos successful: ({new_point.x}, {new_point.y})")
            return True
            
        # Method 2: Use mouse_event with ABSOLUTE coordinates
        if absolute:
            logger.debug(f"Using mouse_event with ABSOLUTE coordinates")
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            
            # Convert to normalized coordinates (0..65535)
            norm_x = int(65535 * x / screen_width)
            norm_y = int(65535 * y / screen_height)
            
            # Move the mouse
            ctypes.windll.user32.mouse_event(
                MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE,
                norm_x,
                norm_y,
                0,
                0
            )
            time.sleep(0.05)
            
            # Verify position again
            ctypes.windll.user32.GetCursorPos(ctypes.byref(new_point))
            logger.debug(f"After mouse_event position: ({new_point.x}, {new_point.y})")
            return True
        
        # Method 3: Use SendInput (final attempt)
        logger.debug(f"Using SendInput for mouse movement")
        # Define structures for SendInput
        class MouseInput(ctypes.Structure):
            _fields_ = [
                ("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
            ]

        class InputI(ctypes.Union):
            _fields_ = [
                ("mi", MouseInput),
                ("ki", ctypes.c_ubyte * 28),  # KeyboardInput size
                ("hi", ctypes.c_ubyte * 16)   # HardwareInput size
            ]

        class Input(ctypes.Structure):
            _fields_ = [
                ("type", ctypes.c_ulong),
                ("ii", InputI)
            ]
        
        # Prepare mouse movement with SendInput
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Convert to normalized coordinates for absolute positioning
        norm_x = int(65535 * x / screen_width)
        norm_y = int(65535 * y / screen_height)
        
        # Create input structure
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(
            norm_x, norm_y, 0, 
            MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, 
            0, ctypes.pointer(extra)
        )
        x_input = Input(0, ii_)  # 0 = INPUT_MOUSE
        
        # Send the input
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x_input), ctypes.sizeof(x_input))
        time.sleep(0.05)
        
        # Final verification
        ctypes.windll.user32.GetCursorPos(ctypes.byref(new_point))
        logger.debug(f"Final position after all methods: ({new_point.x}, {new_point.y})")
        
        # Calculate distance from target
        distance = ((new_point.x - x)**2 + (new_point.y - y)**2)**0.5
        logger.debug(f"Distance from target: {distance:.1f}px")
        
        return True
    except Exception as e:
        logger.error(f"Error moving mouse: {e}", exc_info=True)
        return False

def game_right_click(x=None, y=None):
    """
    Perform a right-click using multiple methods for maximum game compatibility
    
    Args:
        x: Optional target X coordinate (will move mouse there first)
        y: Optional target Y coordinate (will move mouse there first)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Move mouse first if coordinates provided
        if x is not None and y is not None:
            game_move_mouse(x, y)
            # Give the game time to register the new position
            time.sleep(0.1)
        
        logger.debug("Performing right-click")
        
        # Method 1: mouse_event
        try:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)  # Longer delay for game to register
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            logger.debug("Right-click with mouse_event completed")
            return True
        except Exception as e:
            logger.warning(f"mouse_event right-click failed: {e}")
            
            # Method 2: SendInput (more reliable in some cases)
            try:
                # Define structures again for local scope clarity
                class MouseInput(ctypes.Structure):
                    _fields_ = [
                        ("dx", ctypes.c_long),
                        ("dy", ctypes.c_long),
                        ("mouseData", ctypes.c_ulong),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                    ]

                class InputI(ctypes.Union):
                    _fields_ = [
                        ("mi", MouseInput),
                        ("ki", ctypes.c_ubyte * 28),
                        ("hi", ctypes.c_ubyte * 16)
                    ]

                class Input(ctypes.Structure):
                    _fields_ = [
                        ("type", ctypes.c_ulong),
                        ("ii", InputI)
                    ]
                
                # Mouse down
                extra = ctypes.c_ulong(0)
                ii_ = InputI()
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(extra))
                x_input = Input(0, ii_)  # 0 = INPUT_MOUSE
                
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x_input), ctypes.sizeof(x_input))
                time.sleep(0.1)
                
                # Mouse up
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
                x_input = Input(0, ii_)
                
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x_input), ctypes.sizeof(x_input))
                logger.debug("Right-click with SendInput completed")
                return True
            except Exception as e2:
                logger.error(f"SendInput right-click also failed: {e2}", exc_info=True)
                return False
    except Exception as e:
        logger.error(f"Error performing right-click: {e}", exc_info=True)
        return False

def game_left_click(x=None, y=None):
    """
    Perform a left-click using multiple methods for maximum game compatibility
    
    Args:
        x: Optional target X coordinate (will move mouse there first)
        y: Optional target Y coordinate (will move mouse there first)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Move mouse first if coordinates provided
        if x is not None and y is not None:
            game_move_mouse(x, y)
            # Give the game time to register the new position
            time.sleep(0.1)
        
        logger.debug("Performing left-click")
        
        # Method 1: mouse_event
        try:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)  # Longer delay for game to register
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            logger.debug("Left-click with mouse_event completed")
            return True
        except Exception as e:
            logger.warning(f"mouse_event left-click failed: {e}")
            
            # Method 2: SendInput (more reliable in some cases)
            try:
                # Define structures again for local scope clarity
                class MouseInput(ctypes.Structure):
                    _fields_ = [
                        ("dx", ctypes.c_long),
                        ("dy", ctypes.c_long),
                        ("mouseData", ctypes.c_ulong),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                    ]

                class InputI(ctypes.Union):
                    _fields_ = [
                        ("mi", MouseInput),
                        ("ki", ctypes.c_ubyte * 28),
                        ("hi", ctypes.c_ubyte * 16)
                    ]

                class Input(ctypes.Structure):
                    _fields_ = [
                        ("type", ctypes.c_ulong),
                        ("ii", InputI)
                    ]
                
                # Mouse down
                extra = ctypes.c_ulong(0)
                ii_ = InputI()
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
                x_input = Input(0, ii_)  # 0 = INPUT_MOUSE
                
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x_input), ctypes.sizeof(x_input))
                time.sleep(0.1)
                
                # Mouse up
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
                x_input = Input(0, ii_)
                
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x_input), ctypes.sizeof(x_input))
                logger.debug("Left-click with SendInput completed")
                return True
            except Exception as e2:
                logger.error(f"SendInput left-click also failed: {e2}", exc_info=True)
                return False
    except Exception as e:
        logger.error(f"Error performing left-click: {e}", exc_info=True)
        return False