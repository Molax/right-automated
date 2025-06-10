"""
Window Management Utilities
--------------------------
This module provides utilities for finding, focusing, and getting information about windows.
"""

import time
import logging
import win32gui
import win32con
import ctypes
from ctypes import wintypes

logger = logging.getLogger('PristonBot')

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

def get_client_area(hwnd):
    """
    Get the client area rectangle of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        Tuple of (left, top, right, bottom) or None if failed
    """
    if not hwnd:
        logger.warning("Cannot get client area: Invalid handle")
        return None
    
    try:
        # Get window rect in screen coordinates
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        
        # Get client rect in client coordinates (relative to window)
        client_rect = win32gui.GetClientRect(hwnd)
        client_left, client_top, client_right, client_bottom = client_rect
        
        # Convert the client rect to screen coordinates
        client_left_screen, client_top_screen = win32gui.ClientToScreen(hwnd, (client_left, client_top))
        client_right_screen, client_bottom_screen = win32gui.ClientToScreen(hwnd, (client_right, client_bottom))
        
        return (client_left_screen, client_top_screen, client_right_screen, client_bottom_screen)
    except Exception as e:
        logger.error(f"Error getting client area: {e}")
        return None

def get_window_center(hwnd):
    """
    Get the center point of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        Tuple of (center_x, center_y) or None if failed
    """
    rect = get_window_rect(hwnd)
    if rect:
        left, top, right, bottom = rect
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        return (center_x, center_y)
    return None

def get_client_center(hwnd):
    """
    Get the center point of a window's client area
    
    Args:
        hwnd: Window handle
        
    Returns:
        Tuple of (center_x, center_y) or None if failed
    """
    rect = get_client_area(hwnd)
    if rect:
        left, top, right, bottom = rect
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        return (center_x, center_y)
    return None

def get_all_windows():
    """
    Get a list of all visible windows with titles
    
    Returns:
        List of (hwnd, title) tuples
    """
    windows = []
    
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindow(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Only include windows with titles
                windows.append((hwnd, title))
        return True
    
    win32gui.EnumWindows(callback, windows)
    return windows

def get_window_process_id(hwnd):
    """
    Get the process ID of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        Process ID or None if failed
    """
    if not hwnd:
        logger.warning("Cannot get process ID: Invalid handle")
        return None
        
    try:
        _, pid = win32gui.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception as e:
        logger.error(f"Error getting window process ID: {e}")
        return None

def is_window_fullscreen(hwnd):
    """
    Check if a window is in fullscreen mode
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if window is fullscreen, False otherwise
    """
    if not hwnd:
        return False
        
    try:
        # Get window rect
        window_rect = get_window_rect(hwnd)
        if not window_rect:
            return False
            
        # Get screen dimensions
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        # Check if window covers the entire screen
        left, top, right, bottom = window_rect
        width = right - left
        height = bottom - top
        
        return (width >= screen_width and height >= screen_height)
    except Exception as e:
        logger.error(f"Error checking if window is fullscreen: {e}")
        return False

def get_window_text(hwnd):
    """
    Get the text of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        Window text or empty string if failed
    """
    if not hwnd:
        return ""
        
    try:
        return win32gui.GetWindowText(hwnd)
    except Exception as e:
        logger.error(f"Error getting window text: {e}")
        return ""

def get_window_class(hwnd):
    """
    Get the class name of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        Window class name or empty string if failed
    """
    if not hwnd:
        return ""
        
    try:
        return win32gui.GetClassName(hwnd)
    except Exception as e:
        logger.error(f"Error getting window class: {e}")
        return ""

def is_window_visible(hwnd):
    """
    Check if a window is visible
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if window is visible, False otherwise
    """
    if not hwnd:
        return False
        
    try:
        return win32gui.IsWindowVisible(hwnd)
    except Exception as e:
        logger.error(f"Error checking if window is visible: {e}")
        return False

def is_window_enabled(hwnd):
    """
    Check if a window is enabled
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if window is enabled, False otherwise
    """
    if not hwnd:
        return False
        
    try:
        return win32gui.IsWindowEnabled(hwnd)
    except Exception as e:
        logger.error(f"Error checking if window is enabled: {e}")
        return False

def get_child_windows(hwnd):
    """
    Get all child windows of a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        List of child window handles
    """
    if not hwnd:
        return []
        
    children = []
    try:
        def callback(child_hwnd, children):
            children.append(child_hwnd)
            return True
            
        win32gui.EnumChildWindows(hwnd, callback, children)
        return children
    except Exception as e:
        logger.error(f"Error getting child windows: {e}")
        return []

def move_window(hwnd, x, y, width, height, repaint=True):
    """
    Move and resize a window
    
    Args:
        hwnd: Window handle
        x, y: New position
        width, height: New size
        repaint: Whether to repaint the window after moving
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot move window: Invalid handle")
        return False
        
    try:
        win32gui.MoveWindow(hwnd, x, y, width, height, repaint)
        return True
    except Exception as e:
        logger.error(f"Error moving window: {e}")
        return False

def set_window_position(hwnd, position=win32con.HWND_TOP, x=0, y=0, width=0, height=0, flags=0):
    """
    Set the position of a window
    
    Args:
        hwnd: Window handle
        position: Position code (HWND_TOP, HWND_BOTTOM, HWND_TOPMOST, HWND_NOTOPMOST)
        x, y: New position
        width, height: New size (0 to keep current size)
        flags: Flags (SWP_NOMOVE, SWP_NOSIZE, etc.)
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot set window position: Invalid handle")
        return False
        
    try:
        win32gui.SetWindowPos(hwnd, position, x, y, width, height, flags)
        return True
    except Exception as e:
        logger.error(f"Error setting window position: {e}")
        return False

def maximize_window(hwnd):
    """
    Maximize a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot maximize window: Invalid handle")
        return False
        
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return True
    except Exception as e:
        logger.error(f"Error maximizing window: {e}")
        return False

def minimize_window(hwnd):
    """
    Minimize a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot minimize window: Invalid handle")
        return False
        
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True
    except Exception as e:
        logger.error(f"Error minimizing window: {e}")
        return False

def restore_window(hwnd):
    """
    Restore a window (from maximized or minimized state)
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot restore window: Invalid handle")
        return False
        
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        return True
    except Exception as e:
        logger.error(f"Error restoring window: {e}")
        return False

def hide_window(hwnd):
    """
    Hide a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot hide window: Invalid handle")
        return False
        
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        return True
    except Exception as e:
        logger.error(f"Error hiding window: {e}")
        return False

def show_window(hwnd):
    """
    Show a window
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot show window: Invalid handle")
        return False
        
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        return True
    except Exception as e:
        logger.error(f"Error showing window: {e}")
        return False

def find_window_by_class_and_title(class_name=None, window_name=None):
    """
    Find a window by class name and/or window title
    
    Args:
        class_name: Window class name or None
        window_name: Window title or None
        
    Returns:
        Window handle if found, None otherwise
    """
    try:
        hwnd = win32gui.FindWindow(class_name, window_name)
        if hwnd != 0:
            return hwnd
        return None
    except Exception as e:
        logger.error(f"Error finding window by class and title: {e}")
        return None

def find_window_by_pid(pid):
    """
    Find a window by process ID
    
    Args:
        pid: Process ID
        
    Returns:
        Window handle if found, None otherwise
    """
    result = []
    
    def callback(hwnd, result):
        try:
            _, window_pid = win32gui.GetWindowThreadProcessId(hwnd)
            if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                result.append(hwnd)
        except:
            pass
        return True
    
    try:
        win32gui.EnumWindows(callback, result)
        if result:
            return result[0]  # Return the first window found
        return None
    except Exception as e:
        logger.error(f"Error finding window by PID: {e}")
        return None

def send_message(hwnd, message, wparam=0, lparam=0):
    """
    Send a message to a window
    
    Args:
        hwnd: Window handle
        message: Message ID
        wparam: WPARAM parameter
        lparam: LPARAM parameter
        
    Returns:
        Result of the message or None if failed
    """
    if not hwnd:
        logger.warning("Cannot send message: Invalid handle")
        return None
        
    try:
        return win32gui.SendMessage(hwnd, message, wparam, lparam)
    except Exception as e:
        logger.error(f"Error sending message to window: {e}")
        return None

def post_message(hwnd, message, wparam=0, lparam=0):
    """
    Post a message to a window without waiting for a response
    
    Args:
        hwnd: Window handle
        message: Message ID
        wparam: WPARAM parameter
        lparam: LPARAM parameter
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot post message: Invalid handle")
        return False
        
    try:
        win32gui.PostMessage(hwnd, message, wparam, lparam)
        return True
    except Exception as e:
        logger.error(f"Error posting message to window: {e}")
        return False

def close_window(hwnd):
    """
    Close a window by sending WM_CLOSE message
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
    """
    if not hwnd:
        logger.warning("Cannot close window: Invalid handle")
        return False
        
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return True
    except Exception as e:
        logger.error(f"Error closing window: {e}")
        return False

def wait_for_window(window_name, timeout=10, check_interval=0.5):
    """
    Wait for a window to appear
    
    Args:
        window_name: Window title to wait for
        timeout: Maximum time to wait in seconds
        check_interval: How often to check in seconds
        
    Returns:
        Window handle if found, None if timed out
    """
    logger.info(f"Waiting for window '{window_name}' to appear (timeout: {timeout}s)")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        hwnd = find_game_window(window_name)
        if hwnd:
            logger.info(f"Window '{window_name}' appeared after {time.time() - start_time:.1f}s")
            return hwnd
            
        time.sleep(check_interval)
    
    logger.warning(f"Timed out waiting for window '{window_name}' after {timeout}s")
    return None

def is_window_active(hwnd):
    """
    Check if a window is the active (foreground) window
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if window is active, False otherwise
    """
    if not hwnd:
        return False
        
    try:
        active_hwnd = win32gui.GetForegroundWindow()
        return active_hwnd == hwnd
    except Exception as e:
        logger.error(f"Error checking if window is active: {e}")
        return False

def is_window_valid(hwnd):
    """
    Check if a window handle is valid (window exists)
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if window is valid, False otherwise
    """
    if not hwnd:
        return False
        
    try:
        return win32gui.IsWindow(hwnd)
    except:
        return False

def set_foreground_window_timeout(timeout_ms):
    """
    Set the timeout for the SetForegroundWindow function
    
    Args:
        timeout_ms: Timeout in milliseconds (0 for no timeout)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
        SPIF_SENDCHANGE = 0x2
        
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETFOREGROUNDLOCKTIMEOUT, 
            0, 
            ctypes.c_void_p(timeout_ms), 
            SPIF_SENDCHANGE
        )
        
        return result != 0
    except Exception as e:
        logger.error(f"Error setting foreground window timeout: {e}")
        return False