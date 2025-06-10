"""
DirectInput Mouse Control for Games
-----------------------------------
This module provides specialized input functions for games that might
use DirectInput or similar technologies for handling mouse and keyboard input.
"""

import ctypes
import logging
import time
import win32gui
import win32con
from ctypes import wintypes

logger = logging.getLogger('PristonBot')

# DirectInput constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

def game_mouse_move(x, y):
    """
    Move the mouse cursor using DirectInput compatible methods
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert to integers
        x, y = int(x), int(y)
        logger.debug(f"Moving mouse to ({x}, {y}) using DirectInput method")
        
        # Get current mouse position
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        logger.debug(f"Current mouse position: ({point.x}, {point.y})")
        
        # First method: SetCursorPos (works for most applications)
        ctypes.windll.user32.SetCursorPos(x, y)
        time.sleep(0.05)  # Small delay to allow the cursor to move
        
        # Check if we need to use the more forceful approach
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        if abs(point.x - x) > 5 or abs(point.y - y) > 5:
            logger.debug(f"SetCursorPos didn't work well enough, position: ({point.x}, {point.y})")
            
            # Second method: Use MOUSEEVENTF_ABSOLUTE (DirectInput compatible)
            # Convert to normalized coordinates (0..65535)
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            
            # Apply special scaling for absolute mouse coordinates
            norm_x = int(65535 * x / screen_width)
            norm_y = int(65535 * y / screen_height)
            
            # Use the absolute positioning method
            ctypes.windll.user32.mouse_event(
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 
                norm_x, 
                norm_y, 
                0, 
                0
            )
            time.sleep(0.05)  # Give time for the mouse to move
        
        # Verify the final position
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        logger.debug(f"Final mouse position: ({point.x}, {point.y})")
        
        # Check if we're close enough to the target
        if abs(point.x - x) <= 5 and abs(point.y - y) <= 5:
            return True
        else:
            logger.warning(f"Mouse didn't move to exact position. Target: ({x}, {y}), Actual: ({point.x}, {point.y})")
            return False
            
    except Exception as e:
        logger.error(f"Error in game_mouse_move: {e}")
        return False

def game_right_click(x=None, y=None):
    """
    Perform a right-click at the current or specified position using DirectInput
    
    Args:
        x: Optional X coordinate for click
        y: Optional Y coordinate for click
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Move mouse if coordinates are provided
        if x is not None and y is not None:
            game_mouse_move(x, y)
            time.sleep(0.05)  # Small delay after moving
        
        logger.debug(f"Performing right-click with DirectInput at current position")
        
        # Send right mouse down event
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)  # Slightly longer delay between down and up for games
        
        # Send right mouse up event
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        
        return True
    except Exception as e:
        logger.error(f"Error in game_right_click: {e}")
        return False

def game_left_click(x=None, y=None):
    """
    Perform a left-click at the current or specified position using DirectInput
    
    Args:
        x: Optional X coordinate for click
        y: Optional Y coordinate for click
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Move mouse if coordinates are provided
        if x is not None and y is not None:
            game_mouse_move(x, y)
            time.sleep(0.05)  # Small delay after moving
        
        logger.debug(f"Performing left-click with DirectInput at current position")
        
        # Send left mouse down event
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)  # Slightly longer delay between down and up for games
        
        # Send left mouse up event
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        return True
    except Exception as e:
        logger.error(f"Error in game_left_click: {e}")
        return False

def focus_game_window(hwnd):
    """
    Ensure a game window is in focus
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot focus game window: Invalid handle")
        return False
        
    try:
        # First check if window is already in foreground
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd == hwnd:
            logger.debug("Game window is already in focus")
            return True
            
        # Get window title for logging
        window_title = win32gui.GetWindowText(hwnd)
        logger.debug(f"Focusing game window: {window_title}")
        
        # Check if window is minimized and restore if needed
        if win32gui.IsIconic(hwnd):
            logger.debug("Window is minimized, restoring")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)  # Give it time to restore
        
        # Try to bring window to foreground
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)  # Short delay
        
        # Verify that window is now foreground
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd == hwnd:
            logger.debug("Successfully focused game window")
            return True
        else:
            logger.warning(f"Failed to focus game window: {window_title}")
            
            # Try more aggressive approach
            try:
                # Get thread IDs
                foreground_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(
                    foreground_hwnd, None)
                current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
                
                # Attach input processing
                ctypes.windll.user32.AttachThreadInput(
                    foreground_thread_id, current_thread_id, True)
                
                # Try to set foreground window again
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                
                # Detach thread input
                ctypes.windll.user32.AttachThreadInput(
                    foreground_thread_id, current_thread_id, False)
                
                # Check if successful
                foreground_hwnd = win32gui.GetForegroundWindow()
                if foreground_hwnd == hwnd:
                    logger.debug("Successfully focused game window using thread attachment")
                    return True
            except Exception as e:
                logger.error(f"Error in alternative focus method: {e}")
                
            return False
    except Exception as e:
        logger.error(f"Error focusing game window: {e}")
        return False

def press_game_key(key):
    """
    Press a key using DirectInput compatible methods
    
    Args:
        key: Key to press (string or virtual key code)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # If key is a string, convert to virtual key code
        if isinstance(key, str):
            from app.window_utils import get_virtual_key_code
            vk_code = get_virtual_key_code(key)
        else:
            vk_code = key
            
        logger.debug(f"Pressing key {key} (VK: {vk_code}) using DirectInput method")
        
        # Define key event flags
        KEYEVENTF_KEYDOWN = 0x0000
        KEYEVENTF_KEYUP = 0x0002
        
        # Send key down
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYDOWN, 0)
        time.sleep(0.05)  # Small delay between down and up
        
        # Send key up
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
        
        return True
    except Exception as e:
        logger.error(f"Error pressing game key: {e}")
        return False