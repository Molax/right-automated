"""
Fixed Monitor Detection
---------------------
Corrected monitor detection for proper coordinate handling.
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

class MonitorDetector:
    @staticmethod
    def get_monitors():
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