"""
Mouse Input Utilities
--------------------
This module provides utilities for simulating mouse input.
"""

import time
import logging
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes

# Import structures if available, otherwise define them here
try:
    from app.windows_utils.input_structures import MouseInput, InputI, Input
except ImportError:
    # Define pointers and structures for Windows API input simulation
    PUL = ctypes.POINTER(ctypes.c_ulong)

    class KeyBdInput(ctypes.Structure):
        """Keyboard input structure for SendInput"""
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", PUL)
        ]

    class HardwareInput(ctypes.Structure):
        """Hardware input structure for SendInput"""
        _fields_ = [
            ("uMsg", ctypes.c_ulong),
            ("wParamL", ctypes.c_short),
            ("wParamH", ctypes.c_ushort)
        ]

    class MouseInput(ctypes.Structure):
        """Mouse input structure for SendInput"""
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", PUL)
        ]

    class InputI(ctypes.Union):
        """Input union for SendInput"""
        _fields_ = [
            ("ki", KeyBdInput),
            ("mi", MouseInput),
            ("hi", HardwareInput)
        ]

    class Input(ctypes.Structure):
        """Input structure for SendInput"""
        _fields_ = [
            ("type", ctypes.c_ulong),
            ("ii", InputI)
        ]

# Enhanced move_mouse_direct function for app/windows_utils/mouse.py
def move_mouse_direct(x, y):
    """
    Move the mouse cursor directly to specified coordinates using multiple methods
    
    Args:
        x: X-coordinate
        y: Y-coordinate
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('PristonBot')
    try:
        # Force integer coordinates
        x, y = int(x), int(y)
        
        # Save original position for debugging
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        original_x, original_y = point.x, point.y
        logger.debug(f"Moving cursor from ({original_x}, {original_y}) to ({x}, {y})")
        
        # First method - SetCursorPos
        ctypes.windll.user32.SetCursorPos(x, y)
        time.sleep(0.05)  # Small delay
        
        # Check if the cursor is at the expected position
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        if abs(point.x - x) > 5 or abs(point.y - y) > 5:
            logger.debug(f"SetCursorPos didn't move precisely, actual: ({point.x}, {point.y})")
            
            # Try using absolute positioning with mouse_event
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            
            # Apply special scaling for absolute mouse coordinates
            norm_x = int(65535 * x / screen_width)
            norm_y = int(65535 * y / screen_height)
            
            # Use the absolute positioning method
            MOUSEEVENTF_ABSOLUTE = 0x8000
            MOUSEEVENTF_MOVE = 0x0001
            ctypes.windll.user32.mouse_event(
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 
                norm_x, 
                norm_y, 
                0, 
                0
            )
            time.sleep(0.1)  # Longer delay for absolute movement
        
        # Verify final position
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        distance = ((point.x - x)**2 + (point.y - y)**2)**0.5
        logger.debug(f"Final position: ({point.x}, {point.y}), distance from target: {distance:.1f}px")
        
        return True
    except Exception as e:
        logger.error(f"Error moving cursor: {e}", exc_info=True)
        return False

def press_right_mouse(hwnd=None, target_x=None, target_y=None, method=None):
    """
    Try specific or all mouse click methods to simulate a right-click
    
    Args:
        hwnd: Window handle or None
        target_x: X-coordinate for the click, or None to use current position
        target_y: Y-coordinate for the click, or None to use current position
        method: Specific method to use, or None to try all methods
    
    Returns:
        True if at least one method worked, False otherwise
    """
    # Get logger within the function scope
    logger = logging.getLogger('PristonBot')
    logger.debug(f"Entered press_right_mouse function with target: ({target_x}, {target_y})")
    success = False

    # Store original cursor position if we're moving it
    original_pos = None
    if target_x is not None and target_y is not None:
        try:
            cursor_info = win32gui.GetCursorInfo()
            original_pos = cursor_info[2]  # (x, y) tuple
            logger.debug(f"Saved original cursor position: {original_pos}")
        except Exception as e:
            logger.warning(f"Could not get original cursor position: {e}")
    
    try:
        # Move cursor to target position if specified using the enhanced direct method
        if target_x is not None and target_y is not None:
            logger.debug(f"Moving cursor to position ({target_x}, {target_y})")
            move_mouse_direct(target_x, target_y)
            # Give time for the cursor to move and the game to register it
            time.sleep(0.1)
        
        # If hwnd is provided, try to ensure the window is focused
        if hwnd:
            try:
                if win32gui.GetForegroundWindow() != hwnd:
                    logger.debug(f"Focusing game window before clicking")
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
            except Exception as e:
                logger.warning(f"Could not focus window: {e}")
        
        # Try direct approach for right click
        try:
            logger.debug(f"Right-clicking with mouse_event")
            MOUSEEVENTF_RIGHTDOWN = 0x0008
            MOUSEEVENTF_RIGHTUP = 0x0010
            
            # Mouse down
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)  # Longer delay between down and up for game to register
            
            # Mouse up
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            
            success = True
            
        except Exception as e:
            logger.error(f"Error with mouse_event click: {e}", exc_info=True)
            
            # Try SendInput method
            try:
                logger.debug(f"Trying SendInput for right-click")
                
                # Define constants
                INPUT_MOUSE = 0
                MOUSEEVENTF_RIGHTDOWN = 0x0008
                MOUSEEVENTF_RIGHTUP = 0x0010
                
                # Mouse down
                extra = ctypes.c_ulong(0)
                ii_ = InputI()
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(extra))
                x = Input(INPUT_MOUSE, ii_)
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
                
                # Small delay between down and up
                time.sleep(0.1)
                
                # Mouse up
                extra = ctypes.c_ulong(0)
                ii_ = InputI()
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
                x = Input(INPUT_MOUSE, ii_)
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
                
                success = True
                
            except Exception as e2:
                logger.error(f"Error with SendInput click: {e2}", exc_info=True)
        
        if not success and hwnd:
            # Last resort: Try sending messages directly to the window
            try:
                logger.debug("Trying to send click directly to window")
                
                # Convert screen coordinates to client coordinates
                if target_x is not None and target_y is not None:
                    client_x, client_y = win32gui.ScreenToClient(hwnd, (int(target_x), int(target_y)))
                else:
                    # If no target specified, use center of window
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    center_x = (left + right) // 2
                    center_y = (top + bottom) // 2
                    client_x, client_y = win32gui.ScreenToClient(hwnd, (center_x, center_y))
                
                # Create lParam from coordinates
                lParam = win32api.MAKELONG(client_x, client_y)
                
                # Send messages
                win32gui.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
                time.sleep(0.1)
                win32gui.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
                
                success = True
                logger.debug("Successfully sent click directly to window")
            except Exception as e3:
                logger.error(f"Error sending click to window: {e3}", exc_info=True)
        
        # Log outcome
        if success:
            logger.debug("Right-click successful")
        else:
            logger.error("All click methods failed!")
            
        return success
        
    finally:
        # Restore original cursor position if we moved it and we want to restore it
        if original_pos is not None:
            # Wait slightly longer before restoring position to ensure click is registered
            time.sleep(0.2)
            logger.debug(f"Restoring cursor to original position: {original_pos}")
            ctypes.windll.user32.SetCursorPos(original_pos[0], original_pos[1])

def press_left_mouse(hwnd=None, target_x=None, target_y=None):
    """
    Simulate a left mouse button click
    
    Args:
        hwnd: Window handle or None
        target_x: X-coordinate for the click, or None to use current position
        target_y: Y-coordinate for the click, or None to use current position
        
    Returns:
        True if successful, False otherwise
    """
    # Get logger within the function scope
    logger = logging.getLogger('PristonBot')
    logger.debug(f"Entered press_left_mouse function with target: ({target_x}, {target_y})")
    
    # Store original cursor position if we're moving it
    original_pos = None
    if target_x is not None and target_y is not None:
        try:
            cursor_info = win32gui.GetCursorInfo()
            original_pos = cursor_info[2]  # (x, y) tuple
            logger.debug(f"Saved original cursor position: {original_pos}")
        except Exception as e:
            logger.warning(f"Could not get original cursor position: {e}")
    
    try:
        # Move cursor to target position if specified
        if target_x is not None and target_y is not None:
            logger.debug(f"Moving cursor to position ({target_x}, {target_y})")
            move_mouse_direct(target_x, target_y)
            # Ensure the cursor has moved before continuing
            time.sleep(0.1)
        
        # If hwnd is provided, try to ensure the window is focused
        if hwnd:
            try:
                if win32gui.GetForegroundWindow() != hwnd:
                    logger.debug(f"Focusing game window before clicking")
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
            except Exception as e:
                logger.warning(f"Could not focus window: {e}")
        
        # Try mouse_event method first
        try:
            logger.debug(f"Left-clicking with mouse_event")
            MOUSEEVENTF_LEFTDOWN = 0x0002
            MOUSEEVENTF_LEFTUP = 0x0004
            
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)  # Longer delay between down and up for game to register
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            return True
            
        except Exception as e:
            logger.error(f"Error with mouse_event left-click: {e}", exc_info=True)
            
            # Try SendInput as backup
            try:
                logger.debug(f"Trying SendInput for left-click")
                
                # Define constants
                INPUT_MOUSE = 0
                MOUSEEVENTF_LEFTDOWN = 0x0002
                MOUSEEVENTF_LEFTUP = 0x0004
                
                # Mouse down
                extra = ctypes.c_ulong(0)
                ii_ = InputI()
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
                x = Input(INPUT_MOUSE, ii_)
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
                
                time.sleep(0.1)
                
                # Mouse up
                extra = ctypes.c_ulong(0)
                ii_ = InputI()
                ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
                x = Input(INPUT_MOUSE, ii_)
                ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
                
                return True
                
            except Exception as e2:
                logger.error(f"Error with SendInput left-click: {e2}", exc_info=True)
            
            # Last resort if we have a window handle
            if hwnd:
                try:
                    logger.debug("Trying to send left-click directly to window")
                    
                    # Convert screen coordinates to client coordinates
                    if target_x is not None and target_y is not None:
                        client_x, client_y = win32gui.ScreenToClient(hwnd, (int(target_x), int(target_y)))
                    else:
                        # If no target specified, use center of window
                        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                        center_x = (left + right) // 2
                        center_y = (top + bottom) // 2
                        client_x, client_y = win32gui.ScreenToClient(hwnd, (center_x, center_y))
                    
                    # Create lParam from coordinates
                    lParam = win32api.MAKELONG(client_x, client_y)
                    
                    # Send messages
                    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
                    time.sleep(0.1)
                    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
                    
                    logger.debug("Successfully sent left-click directly to window")
                    return True
                except Exception as e3:
                    logger.error(f"Error sending left-click to window: {e3}", exc_info=True)
                    
            return False
        
    finally:
        # Restore original cursor position if we moved it
        if original_pos is not None:
            # Wait slightly longer before restoring position to ensure click is registered
            time.sleep(0.2)
            logger.debug(f"Restoring cursor to original position: {original_pos}")
            ctypes.windll.user32.SetCursorPos(original_pos[0], original_pos[1])

def test_click_methods(hwnd=None):
    """
    Test multiple mouse click methods and log results to determine which works
    
    Args:
        hwnd: Window handle or None to test global methods
        
    Returns:
        Dictionary with results of each test method
    """
    logger = logging.getLogger('PristonBot')
    logger.info("Starting comprehensive mouse click testing")
    
    results = {}
    window_title = "Unknown"
    
    if hwnd:
        try:
            window_title = win32gui.GetWindowText(hwnd)
            logger.info(f"Testing click methods on window: '{window_title}' (handle: {hwnd})")
        except:
            logger.error("Could not get window title for provided handle")
    else:
        logger.info("Testing global click methods (no window handle)")
    
    # Get screen dimensions
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    
    # Calculate test positions
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    test_positions = [
        (center_x, center_y),               # Center
        (center_x - 100, center_y - 100),   # Top-left of center
        (center_x + 100, center_y - 100),   # Top-right of center
        (center_x + 100, center_y + 100),   # Bottom-right of center
        (center_x - 100, center_y + 100)    # Bottom-left of center
    ]
    
    # Test moving to each position
    logger.info("Testing cursor movement to various positions")
    for i, (x, y) in enumerate(test_positions):
        try:
            logger.info(f"Test {i+1}: Moving cursor to ({x}, {y})")
            move_mouse_direct(x, y)
            time.sleep(0.5)
            
            # Get current position to verify
            point = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
            logger.info(f"  Actual position: ({point.x}, {point.y})")
            
            # Calculate distance from target
            distance = ((point.x - x)**2 + (point.y - y)**2)**0.5
            logger.info(f"  Distance from target: {distance:.1f} pixels")
            
            results[f"Move to ({x}, {y})"] = (
                f"Actual: ({point.x}, {point.y}), "
                f"Error: {distance:.1f}px, "
                f"{'Success' if distance < 5 else 'Failed'}"
            )
        except Exception as e:
            logger.error(f"Error testing cursor movement: {e}")
            results[f"Move to ({x}, {y})"] = f"Error: {str(e)}"
    
    # Test right-click methods
    logger.info("Testing right-click methods")
    click_methods = {
        "mouse_event": lambda: _click_method_mouse_event(),
        "SendInput": lambda: _click_method_send_input(),
        "Combined direct": lambda: press_right_mouse(hwnd, center_x, center_y)
    }
    
    # If hwnd is provided, add window-specific methods
    if hwnd:
        click_methods["SendMessage to window"] = lambda: _click_method_send_message(hwnd)
    
    # Test each method
    for method_name, method_func in click_methods.items():
        try:
            logger.info(f"Testing {method_name}")
            success = method_func()
            results[f"Right-click: {method_name}"] = "Success" if success else "Failed"
        except Exception as e:
            logger.error(f"Error testing {method_name}: {e}")
            results[f"Right-click: {method_name}"] = f"Error: {str(e)}"
    
    # Test left-click methods
    logger.info("Testing left-click methods")
    try:
        logger.info("Testing press_left_mouse")
        success = press_left_mouse(hwnd, center_x, center_y)
        results["Left-click: Combined direct"] = "Success" if success else "Failed"
    except Exception as e:
        logger.error(f"Error testing left-click: {e}")
        results["Left-click: Combined direct"] = f"Error: {str(e)}"
    
    # Log summary
    logger.info("Mouse testing completed. Results:")
    for test, result in results.items():
        logger.info(f"  {test}: {result}")
    
    return results

# Helper functions for different click methods (for testing)
def _click_method_mouse_event():
    """mouse_event method for global clicking"""
    logger = logging.getLogger('PristonBot')
    try:
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        return True
    except Exception as e:
        logger.debug(f"mouse_event click failed: {e}")
        return False

def _click_method_send_input():
    """SendInput method for global clicking"""
    logger = logging.getLogger('PristonBot')
    try:
        INPUT_MOUSE = 0
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        
        # Mouse down
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        time.sleep(0.1)
        
        # Mouse up
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        return True
    except Exception as e:
        logger.debug(f"SendInput click failed: {e}")
        return False

def _click_method_send_message(hwnd):
    """SendMessage method for window-specific clicking"""
    logger = logging.getLogger('PristonBot')
    if not hwnd:
        return False
        
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        center_x = left + width // 2
        center_y = top + height // 2
        client_coords = win32gui.ScreenToClient(hwnd, (center_x, center_y))
        
        lParam = win32api.MAKELONG(client_coords[0], client_coords[1])
        win32api.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        time.sleep(0.1)
        win32api.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
        return True
    except Exception as e:
        logger.debug(f"SendMessage click failed: {e}")
        return False