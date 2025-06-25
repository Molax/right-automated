"""
Monitor Detection and Management
-------------------------------
Handles detection and management of multiple monitors.
"""

import ctypes
import logging
from ctypes import wintypes, Structure, c_wchar, sizeof, byref

logger = logging.getLogger('PristonBot')

class MONITORINFOEX(Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint32),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", ctypes.c_uint32),
        ("szDevice", c_wchar * 32)
    ]

class MonitorInfo:
    def __init__(self, index, x, y, width, height, is_primary=False):
        self.index = index
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_primary = is_primary
        
    def __str__(self):
        primary_text = " (Primary)" if self.is_primary else ""
        return f"Monitor {self.index + 1}{primary_text}: {self.width}x{self.height} at ({self.x}, {self.y})"
    
    def get_capture_bounds(self):
        """Get bounds for screen capture that ensures full coverage"""
        try:
            virtual_screen_left = ctypes.windll.user32.GetSystemMetrics(76)
            virtual_screen_top = ctypes.windll.user32.GetSystemMetrics(77)
            virtual_screen_width = ctypes.windll.user32.GetSystemMetrics(78)
            virtual_screen_height = ctypes.windll.user32.GetSystemMetrics(79)
            
            virtual_screen_right = virtual_screen_left + virtual_screen_width
            virtual_screen_bottom = virtual_screen_top + virtual_screen_height
            
            buffer_size = 800
            
            extended_left = min(self.x - buffer_size, virtual_screen_left - buffer_size)
            extended_top = min(self.y - buffer_size, virtual_screen_top - buffer_size)
            extended_right = max(self.x + self.width + buffer_size, virtual_screen_right + buffer_size)
            extended_bottom = max(self.y + self.height + buffer_size, virtual_screen_bottom + buffer_size)
            
            return (extended_left, extended_top, extended_right, extended_bottom)
        except Exception as e:
            logger.error(f"Error getting capture bounds: {e}")
            buffer_size = 1000
            return (
                self.x - buffer_size,
                self.y - buffer_size,
                self.x + self.width + buffer_size,
                self.y + self.height + buffer_size
            )

class MonitorDetector:
    @staticmethod
    def get_monitors():
        """Detect all available monitors"""
        monitors = []
        
        def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            info = MONITORINFOEX()
            info.cbSize = sizeof(MONITORINFOEX)
            
            if ctypes.windll.user32.GetMonitorInfoW(hMonitor, byref(info)):
                rect = info.rcMonitor
                x = rect.left
                y = rect.top
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                is_primary = bool(info.dwFlags & 1)
                
                monitor = MonitorInfo(len(monitors), x, y, width, height, is_primary)
                monitors.append(monitor)
                
                logger.info(f"Detected monitor {len(monitors)}: {width}x{height} at ({x},{y}) {'(Primary)' if is_primary else ''}")
                
            return True
        
        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.POINTER(wintypes.RECT),
            ctypes.c_ulong
        )
        
        callback = MonitorEnumProc(monitor_enum_proc)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, callback, 0)
        
        if not monitors:
            width = ctypes.windll.user32.GetSystemMetrics(0)
            height = ctypes.windll.user32.GetSystemMetrics(1)
            monitors.append(MonitorInfo(0, 0, 0, width, height, True))
        
        monitors.sort(key=lambda m: m.x)
        
        for i, monitor in enumerate(monitors):
            monitor.index = i
        
        return monitors
    
    @staticmethod
    def get_virtual_screen_info():
        """Get virtual screen information"""
        try:
            left = ctypes.windll.user32.GetSystemMetrics(76)
            top = ctypes.windll.user32.GetSystemMetrics(77)
            width = ctypes.windll.user32.GetSystemMetrics(78)
            height = ctypes.windll.user32.GetSystemMetrics(79)
            
            return {
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'right': left + width,
                'bottom': top + height
            }
        except Exception as e:
            logger.error(f"Error getting virtual screen info: {e}")
            return {
                'left': 0,
                'top': 0,
                'width': 1920,
                'height': 1080,
                'right': 1920,
                'bottom': 1080
            }