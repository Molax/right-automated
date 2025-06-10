"""
Improved Window utilities for the Priston Tale Potion Bot
-----------------------------------------------
This module provides utilities for simulating key presses and mouse clicks regardless of window focus.
"""

import time
import logging
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes

logger = logging.getLogger('PristonBot')

# Define key input structures for SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class InputI(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),
        ("mi", MouseInput),
        ("hi", HardwareInput)
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", InputI)
    ]


def get_virtual_key_code(key):
    """
    Convert a key string to virtual key code
    
    Args:
        key: Key string (e.g., "1", "a", "enter")
        
    Returns:
        Virtual key code
    """
    # Map common keys to virtual key codes
    key_map = {
        '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
        '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
        'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
        'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
        'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
        'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
        'space': 0x20, 'enter': 0x0D, 'tab': 0x09, 'esc': 0x1B,
        'backspace': 0x08, 'delete': 0x2E, 'insert': 0x2D,
        'home': 0x24, 'end': 0x23, 'pageup': 0x21, 'pagedown': 0x22,
        'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
        'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
        'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
        'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B
    }
    
    # Convert key to lowercase
    key = key.lower() if isinstance(key, str) else str(key)
    
    # Look up key in map
    if key in key_map:
        return key_map[key]
    
    # Use ASCII value as fallback
    logger.warning(f"Key '{key}' not found in key map, using ASCII value")
    try:
        return ord(key.upper()[0])
    except:
        logger.error(f"Could not determine virtual key code for '{key}'")
        return 0

def press_key(hwnd, key):
    """
    Press a key, either in a specific window or using SendInput globally
    
    Args:
        hwnd: Window handle or None to use SendInput
        key: Key to press
        
    Returns:
        True if successful, False otherwise
    """
    try:
        vk_code = get_virtual_key_code(key)
        
        # If hwnd is provided, send message to that window
        if hwnd:
            window_title = win32gui.GetWindowText(hwnd)
            logger.info(f"Sending key '{key}' (VK: {vk_code}) to window '{window_title}'")
            
            # Send key down message
            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
            time.sleep(0.05)  # Small delay between down and up
            
            # Send key up message
            win32api.SendMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
        else:
            # Use SendInput (works for both focused and background windows)
            logger.info(f"Sending key '{key}' (VK: {vk_code}) using SendInput")
            
            # Define constants
            INPUT_KEYBOARD = 1
            KEYEVENTF_KEYUP = 0x0002
            
            # Key down
            extra = ctypes.c_ulong(0)
            ii_ = InputI()
            ii_.ki = KeyBdInput(vk_code, 0, 0, 0, ctypes.pointer(extra))
            x = Input(INPUT_KEYBOARD, ii_)  # INPUT_KEYBOARD = 1
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            
            # Small delay
            time.sleep(0.05)
            
            # Key up
            extra = ctypes.c_ulong(0)
            ii_ = InputI()
            ii_.ki = KeyBdInput(vk_code, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
            x = Input(INPUT_KEYBOARD, ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            
        return True
    except Exception as e:
        logger.error(f"Error sending key '{key}': {e}", exc_info=True)
        return False

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
    
    # Method 1: SendMessage WM_RBUTTONDOWN/UP (window-specific)
    if hwnd:
        try:
            logger.info("Method 1: SendMessage WM_RBUTTONDOWN/UP")
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            center_x = left + width // 2
            center_y = top + height // 2
            
            # Convert screen coordinates to client coordinates
            client_coords = win32gui.ScreenToClient(hwnd, (center_x, center_y))
            
            # Create lParam from coordinates
            lParam = win32api.MAKELONG(client_coords[0], client_coords[1])
            
            # Send button down message
            win32api.SendMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
            time.sleep(0.05)
            # Send button up message
            win32api.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
            
            logger.info("Method 1 completed without errors")
            results["SendMessage_WM_RBUTTON"] = "Completed"
        except Exception as e:
            logger.error(f"Method 1 failed: {e}", exc_info=True)
            results["SendMessage_WM_RBUTTON"] = f"Failed: {str(e)}"
    else:
        results["SendMessage_WM_RBUTTON"] = "Skipped (no window handle)"
    
    # Method 2: PostMessage WM_RBUTTONDOWN/UP (window-specific)
    if hwnd:
        try:
            logger.info("Method 2: PostMessage WM_RBUTTONDOWN/UP")
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            center_x = left + width // 2
            center_y = top + height // 2
            
            # Convert screen coordinates to client coordinates
            client_coords = win32gui.ScreenToClient(hwnd, (center_x, center_y))
            
            # Create lParam from coordinates
            lParam = win32api.MAKELONG(client_coords[0], client_coords[1])
            
            # Post button down message
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
            time.sleep(0.05)
            # Post button up message
            win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
            
            logger.info("Method 2 completed without errors")
            results["PostMessage_WM_RBUTTON"] = "Completed"
        except Exception as e:
            logger.error(f"Method 2 failed: {e}", exc_info=True)
            results["PostMessage_WM_RBUTTON"] = f"Failed: {str(e)}"
    else:
        results["PostMessage_WM_RBUTTON"] = "Skipped (no window handle)"
    
    # Method 3: mouse_event (global)
    try:
        logger.info("Method 3: mouse_event API")
        
        # Import required constants
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        
        # Mouse down
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        # Mouse up
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        
        logger.info("Method 3 completed without errors")
        results["mouse_event"] = "Completed"
    except Exception as e:
        logger.error(f"Method 3 failed: {e}", exc_info=True)
        results["mouse_event"] = f"Failed: {str(e)}"
    
    # Method 4: SendInput with MOUSEINPUT (global)
    try:
        logger.info("Method 4: SendInput with MOUSEINPUT")
        
        INPUT_MOUSE = 0
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        
        # Mouse down
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        time.sleep(0.05)
        
        # Mouse up
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        logger.info("Method 4 completed without errors")
        results["SendInput_MOUSEINPUT"] = "Completed"
    except Exception as e:
        logger.error(f"Method 4 failed: {e}", exc_info=True)
        results["SendInput_MOUSEINPUT"] = f"Failed: {str(e)}"
    
    # Method 5: SetCursorPos + mouse_event (global with cursor positioning)
    try:
        logger.info("Method 5: SetCursorPos + mouse_event")
        
        # Get current cursor position to restore later
        cursor_info = win32gui.GetCursorInfo()
        original_x, original_y = cursor_info[2]
        
        # Calculate target position
        target_x, target_y = original_x, original_y
        if hwnd:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            target_x = left + (right - left) // 2
            target_y = top + (bottom - top) // 2
        
        # Move cursor
        ctypes.windll.user32.SetCursorPos(target_x, target_y)
        
        # Click
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        
        # Restore cursor position
        ctypes.windll.user32.SetCursorPos(original_x, original_y)
        
        logger.info("Method 5 completed without errors")
        results["SetCursorPos_mouse_event"] = "Completed"
    except Exception as e:
        logger.error(f"Method 5 failed: {e}", exc_info=True)
        results["SetCursorPos_mouse_event"] = f"Failed: {str(e)}"
    
    # Method 6: SendInput with absolute cursor positioning
    try:
        logger.info("Method 6: SendInput with absolute coordinates")
        
        # Get screen dimensions for coordinate conversion
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Calculate position
        target_x, target_y = screen_width // 2, screen_height // 2
        if hwnd:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            target_x = left + (right - left) // 2
            target_y = top + (bottom - top) // 2
        
        # Convert to normalized coordinates (0..65535)
        norm_x = int(65535 * target_x / screen_width)
        norm_y = int(65535 * target_y / screen_height)
        
        INPUT_MOUSE = 0
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        MOUSEEVENTF_ABSOLUTE = 0x8000
        MOUSEEVENTF_MOVE = 0x0001
        
        # Move mouse to position
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(norm_x, norm_y, 0, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        time.sleep(0.05)
        
        # Mouse down
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        time.sleep(0.05)
        
        # Mouse up
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        logger.info("Method 6 completed without errors")
        results["SendInput_Absolute"] = "Completed"
    except Exception as e:
        logger.error(f"Method 6 failed: {e}", exc_info=True)
        results["SendInput_Absolute"] = f"Failed: {str(e)}"
    
    # Method 7: DirectInput simulation (different approach for games)
    try:
        logger.info("Method 7: Direct input simulation via keybd_event (Right Ctrl + Right Alt)")
        
        # Some games interpret key combinations as mouse clicks
        # Try Right Ctrl + Right Alt as an alternative input method
        VK_RCONTROL = 0xA3
        VK_RMENU = 0xA5  # Right Alt key
        KEYEVENTF_KEYUP = 0x0002
        
        # Press Right Control
        ctypes.windll.user32.keybd_event(VK_RCONTROL, 0, 0, 0)
        time.sleep(0.05)
        # Press Right Alt
        ctypes.windll.user32.keybd_event(VK_RMENU, 0, 0, 0)
        time.sleep(0.05)
        # Release Right Alt
        ctypes.windll.user32.keybd_event(VK_RMENU, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        # Release Right Control
        ctypes.windll.user32.keybd_event(VK_RCONTROL, 0, KEYEVENTF_KEYUP, 0)
        
        logger.info("Method 7 completed without errors")
        results["DirectInput_KeyCombination"] = "Completed"
    except Exception as e:
        logger.error(f"Method 7 failed: {e}", exc_info=True)
        results["DirectInput_KeyCombination"] = f"Failed: {str(e)}"
    
    # Log a summary of results
    logger.info("Click method testing completed. Results:")
    for method, result in results.items():
        logger.info(f"  {method}: {result}")
    
    return results

def press_right_mouse(hwnd=None, target_x=None, target_y=None, method=None):
    """
    Try specific or all mouse click methods to simulate a right-click
    
    Args:
        hwnd: Window handle or None
        method: Specific method to use, or None to try all methods
    
    Returns:
        True if at least one method worked, False otherwise
    """
    # Make sure to import the logger at the beginning of the function
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
        # Move cursor to target position if specified
        if target_x is not None and target_y is not None:
            logger.debug(f"Moving cursor to position ({target_x}, {target_y})")
            ctypes.windll.user32.SetCursorPos(int(target_x), int(target_y))
            # Ensure the cursor has moved before continuing
            time.sleep(0.1)
        
        # Try direct approach with SendInput for the right click
        try:
            logger.info(f"Clicking at position ({target_x}, {target_y}) with SendInput")
            
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
            
        except Exception as e:
            logger.error(f"Error with SendInput click: {e}", exc_info=True)
            
            # Try alternative method with mouse_event
            try:
                logger.info("Attempting mouse_event as fallback")
                MOUSEEVENTF_RIGHTDOWN = 0x0008
                MOUSEEVENTF_RIGHTUP = 0x0010
                
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                time.sleep(0.1)
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                
                success = True
            except Exception as e2:
                logger.error(f"Error with mouse_event click: {e2}", exc_info=True)
                success = False
        
        if not success:
            logger.error("All click methods failed!")
        
        return success
        
    finally:
        # Restore original cursor position if we moved it and the setting requires it
        # You can add a setting to control whether to restore the cursor position
        if original_pos is not None:
            # Wait slightly longer before restoring position to ensure click is registered
            time.sleep(0.2)
            logger.debug(f"Restoring cursor to original position: {original_pos}")
            ctypes.windll.user32.SetCursorPos(original_pos[0], original_pos[1])
    """
    Try specific or all mouse click methods to simulate a right-click
    
    Args:
        hwnd: Window handle or None
        method: Specific method to use, or None to try all methods
    
    Returns:
        True if at least one method worked, False otherwise
    """
    logger = logging.getLogger('PristonBot')
    logger.debug("Entered press_right_mouse function")
    success = False

    # Dictionary of available methods
    click_methods = {
        "SendInput": lambda: _click_method_send_input(),
        "SendInputAbsolute": lambda: _click_method_send_input_absolute(hwnd)
    }
    
    # If a specific method is requested
    if method and method in click_methods:
        try:
            logger.info(f"Attempting click method: {method}")
            success = click_methods[method]()
            logger.info(f"Click method {method} " + ("succeeded" if success else "failed"))
            return success
        except Exception as e:
            logger.error(f"Error with click method {method}: {e}", exc_info=True)
            return False
    
    # Try methods in order (most likely to work first)
    methods_to_try = [
        "SendInput"          # Most reliable cross-application
    ]
    
    # Add window-specific methods if we have a window handle
    if hwnd:
        methods_to_try = ["PostMessage", "SendMessage"] + methods_to_try
    
    # Try each method until one succeeds
    for method_name in methods_to_try:
        try:
            logger.info(f"Attempting click method: {method_name}")
            if click_methods[method_name]():
                logger.info(f"Click method {method_name} succeeded")
                success = True
                break
            else:
                logger.warning(f"Click method {method_name} failed")
        except Exception as e:
            logger.warning(f"Error with click method {method_name}: {e}")
    
    # Last resort: try key combination
    if not success:
        try:
            logger.info("Attempting keyboard shortcut as last resort")
            success = click_methods["KeyCombination"]()
            logger.info(f"Key combination method " + ("succeeded" if success else "failed"))
        except Exception as e:
            logger.warning(f"Error with key combination method: {e}")
    
    if not success:
        logger.error("All click methods failed!")
    return success

def find_game_window(window_name="Priston Tale"):
    """
    Find the game window by name
    
    Args:
        window_name: The name of the window to find (default: "Priston Tale")
        
    Returns:
        Window handle if found, None otherwise
    """
    logger.info(f"Searching for game window: {window_name}")
    
    # Try direct match first
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd != 0:
        logger.info(f"Found exact window match with handle {hwnd}")
        return hwnd
    
    # If not found, try partial match
    windows = []
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if window_name.lower() in title.lower():
                windows.append((hwnd, title))
        return True
    
    win32gui.EnumWindows(callback, windows)
    
    if windows:
        logger.info(f"Found similar window: '{windows[0][1]}' with handle {windows[0][0]}")
        return windows[0][0]
    
    logger.warning(f"Game window '{window_name}' not found")
    return None

def focus_game_window(hwnd):
    """
    Bring the game window to the foreground
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot focus window: Invalid handle")
        return False
    
    try:
        # Get window title for logging
        window_title = win32gui.GetWindowText(hwnd)
        logger.info(f"Focusing window: {window_title}")
        
        # Check if window is already in foreground
        current_foreground = win32gui.GetForegroundWindow()
        if current_foreground == hwnd:
            logger.debug("Window already in foreground")
            return True
            
        # Try to bring window to foreground
        logger.debug(f"Current foreground: {win32gui.GetWindowText(current_foreground)}, need to focus {window_title}")
        
        # Check if window is minimized
        if win32gui.IsIconic(hwnd):
            logger.debug("Window is minimized, restoring")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)  # Give it time to restore
        
        # Try multiple methods to focus the window
        try:
            # Standard method
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            logger.warning(f"Standard SetForegroundWindow failed: {e}")
            try:
                # Alternative method using AttachThreadInput
                foreground_thread = ctypes.windll.user32.GetWindowThreadProcessId(
                    win32gui.GetForegroundWindow(), None)
                current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
                
                # Attach threads
                ctypes.windll.user32.AttachThreadInput(foreground_thread, current_thread, True)
                
                # Show and focus window
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                win32gui.SetForegroundWindow(hwnd)
                
                # Detach threads
                ctypes.windll.user32.AttachThreadInput(foreground_thread, current_thread, False)
            except Exception as e2:
                logger.error(f"Alternative focus method failed: {e2}")
                
                try:
                    # Final attempt using ASFW_ANY
                    SPI_GETFOREGROUNDLOCKTIMEOUT = 0x2000
                    SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
                    SPIF_SENDCHANGE = 0x2
                    
                    # Save current timeout
                    timeout_buf = wintypes.DWORD(0)
                    ctypes.windll.user32.SystemParametersInfoW(
                        SPI_GETFOREGROUNDLOCKTIMEOUT, 0, ctypes.byref(timeout_buf), 0)
                    
                    # Set timeout to 0
                    ctypes.windll.user32.SystemParametersInfoW(
                        SPI_SETFOREGROUNDLOCKTIMEOUT, 0, ctypes.c_void_p(0), SPIF_SENDCHANGE)
                    
                    # Try to set foreground window
                    win32gui.SetForegroundWindow(hwnd)
                    
                    # Restore timeout
                    ctypes.windll.user32.SystemParametersInfoW(
                        SPI_SETFOREGROUNDLOCKTIMEOUT, 0, timeout_buf, SPIF_SENDCHANGE)
                except Exception as e3:
                    logger.error(f"Final focus attempt failed: {e3}")
        
        # Give window time to come to foreground
        time.sleep(0.2)
        
        # Verify window is in foreground
        new_foreground = win32gui.GetForegroundWindow()
        if new_foreground != hwnd:
            logger.warning(f"Focus verification failed. Current foreground: {win32gui.GetWindowText(new_foreground)}")
            return False
        
        logger.info("Window focus successful")
        return True
        
    except Exception as e:
        logger.error(f"Error focusing game window: {e}", exc_info=True)
        return False

def get_window_rect(hwnd):
    """
    Get the rectangle coordinates of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        Tuple of (left, top, right, bottom) or None if failed
    """
    if not hwnd:
        logger.warning("Cannot get window rectangle: Invalid handle")
        return None
    
    try:
        return win32gui.GetWindowRect(hwnd)
    except Exception as e:
        logger.error(f"Error getting window rectangle: {e}")
        return None
    
def _click_method_send_message(hwnd):
    """SendMessage method for window-specific clicking"""
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
        time.sleep(0.05)
        win32api.SendMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
        return True
    except Exception as e:
        logging.getLogger('PristonBot').debug(f"SendMessage click failed: {e}")
        return False


def _click_method_post_message(hwnd):
    """PostMessage method for window-specific clicking"""
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
        win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        time.sleep(0.05)
        win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
        return True
    except Exception as e:
        logging.getLogger('PristonBot').debug(f"PostMessage click failed: {e}")
        return False


def _click_method_mouse_event():
    """mouse_event method for global clicking"""
    try:
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        return True
    except Exception as e:
        logging.getLogger('PristonBot').debug(f"mouse_event click failed: {e}")
        return False


def _click_method_send_input():
    """SendInput method for global clicking"""
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
        
        time.sleep(0.05)
        
        # Mouse up
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        return True
    except Exception as e:
        logging.getLogger('PristonBot').debug(f"SendInput click failed: {e}")
        return False


def _click_method_set_cursor_pos(hwnd=None):
    """SetCursorPos + mouse_event method"""
    try:
        # Get current cursor position to restore later
        cursor_info = win32gui.GetCursorInfo()
        original_x, original_y = cursor_info[2]
        
        # Calculate target position
        target_x, target_y = original_x, original_y
        if hwnd:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            target_x = left + (right - left) // 2
            target_y = top + (bottom - top) // 2
        
        # Move cursor
        ctypes.windll.user32.SetCursorPos(target_x, target_y)
        
        # Click
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        
        # Restore cursor position
        ctypes.windll.user32.SetCursorPos(original_x, original_y)
        
        return True
    except Exception as e:
        logging.getLogger('PristonBot').debug(f"SetCursorPos click failed: {e}")
        return False


def _click_method_send_input_absolute(hwnd=None):
    """SendInput with absolute coordinates method"""
    try:
        # Get screen dimensions for coordinate conversion
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Calculate position
        target_x, target_y = screen_width // 2, screen_height // 2
        if hwnd:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            target_x = left + (right - left) // 2
            target_y = top + (bottom - top) // 2
        
        # Convert to normalized coordinates (0..65535)
        norm_x = int(65535 * target_x / screen_width)
        norm_y = int(65535 * target_y / screen_height)
        
        INPUT_MOUSE = 0
        MOUSEEVENTF_RIGHTDOWN = 0x0008
        MOUSEEVENTF_RIGHTUP = 0x0010
        MOUSEEVENTF_ABSOLUTE = 0x8000
        MOUSEEVENTF_MOVE = 0x0001
        
        # Move mouse to position
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(norm_x, norm_y, 0, MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        time.sleep(0.05)
        
        # Mouse down
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        time.sleep(0.05)
        
        # Mouse up
        extra = ctypes.c_ulong(0)
        ii_ = InputI()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        return True
    except Exception as e:
        logging.getLogger('PristonBot').debug(f"SendInput absolute click failed: {e}")
        return False


def _click_method_key_combination():
    """Try keyboard shortcut (Right Ctrl + Right Alt) as alternative"""
    try:
        VK_RCONTROL = 0xA3
        VK_RMENU = 0xA5  # Right Alt key
        KEYEVENTF_KEYUP = 0x0002
        
        # Press Right Control
        ctypes.windll.user32.keybd_event(VK_RCONTROL, 0, 0, 0)
        time.sleep(0.05)
        # Press Right Alt
        ctypes.windll.user32.keybd_event(VK_RMENU, 0, 0, 0)
        time.sleep(0.05)
        # Release Right Alt
        ctypes.windll.user32.keybd_event(VK_RMENU, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        # Release Right Control
        ctypes.windll.user32.keybd_event(VK_RCONTROL, 0, KEYEVENTF_KEYUP, 0)
        
        return True
    except Exception as e:
        logging.getLogger('PristonBot').debug(f"Key combination click failed: {e}")
        return False