"""
Bar Selector Module
------------------
Provides screen selection functionality for the Priston Tale Bot.
"""
from .screen_selector import ScreenSelector
__all__ = ['ScreenSelector']

try:
    from .screen_selector import ScreenSelector
except ImportError as e:
    import logging
    logger = logging.getLogger('PristonBot')
    logger.warning(f"Could not import ScreenSelector from screen_selector: {e}")
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        from PIL import ImageGrab, ImageTk, Image
        import ctypes
        import os
        from ctypes import wintypes, Structure, c_wchar, sizeof, byref
        
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

        class ScreenSelector:
            def __init__(self, root):
                self.root = root
                self.logger = logging.getLogger('PristonBot')
                
                self.x1 = None
                self.y1 = None
                self.x2 = None
                self.y2 = None
                self.is_configured = False
                
                self.selection_window = None
                self.canvas = None
                self.selection_rect = None
                self.start_x = None
                self.start_y = None
                self.preview_image = None
                self.selected_monitor = None
                self.title = "Selection"
                self.color = "yellow"
                
                self.completion_callback = None
                
            def is_setup(self):
                return self.is_configured and all([
                    self.x1 is not None,
                    self.y1 is not None,
                    self.x2 is not None,
                    self.y2 is not None
                ])
            
            def configure_from_saved(self, x1, y1, x2, y2):
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    self.x1 = int(x1)
                    self.y1 = int(y1)
                    self.x2 = int(x2)
                    self.y2 = int(y2)
                    self.is_configured = True
                    
                    title = getattr(self, 'title', 'Selection')
                    self.logger.info(f"{title} configured from saved coordinates: ({self.x1},{self.y1}) to ({self.x2},{self.y2})")
                    return True
                return False
            
            def start_selection(self, title="Select Area", color="yellow", completion_callback=None):
                self.logger.info(f"Starting selection: {title}")
                self.title = title
                self.color = color
                self.completion_callback = completion_callback
                
                try:
                    monitors = self._get_monitors()
                    self.logger.info(f"Detected {len(monitors)} monitor(s)")
                    
                    self.selected_monitor = self._select_monitor(monitors)
                    
                    if not self.selected_monitor:
                        self.logger.info("Monitor selection cancelled")
                        return False
                        
                    self.logger.info(f"Selected: {self.selected_monitor}")
                    return self._create_selection_window()
                    
                except Exception as e:
                    self.logger.error(f"Error starting selection: {e}", exc_info=True)
                    messagebox.showerror("Error", f"Failed to start selection: {e}")
                    return False
            
            def _get_monitors(self):
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
                        
                        self.logger.info(f"Detected monitor {len(monitors)}: {width}x{height} at ({x},{y}) {'(Primary)' if is_primary else ''}")
                        
                    return True
                
                try:
                    MonitorEnumProc = ctypes.WINFUNCTYPE(
                        ctypes.c_bool,
                        ctypes.c_ulong,
                        ctypes.c_ulong,
                        ctypes.POINTER(wintypes.RECT),
                        ctypes.c_ulong
                    )
                    
                    callback = MonitorEnumProc(monitor_enum_proc)
                    ctypes.windll.user32.EnumDisplayMonitors(None, None, callback, 0)
                except Exception as e:
                    self.logger.error(f"Error enumerating monitors: {e}")
                
                if not monitors:
                    try:
                        width = ctypes.windll.user32.GetSystemMetrics(0)
                        height = ctypes.windll.user32.GetSystemMetrics(1)
                        monitors.append(MonitorInfo(0, 0, 0, width, height, True))
                        self.logger.info(f"Fallback to primary monitor: {width}x{height}")
                    except Exception as e:
                        self.logger.error(f"Error getting system metrics: {e}")
                        monitors.append(MonitorInfo(0, 0, 0, 1920, 1080, True))
                
                return monitors
            
            def _select_monitor(self, monitors):
                if len(monitors) == 1:
                    return monitors[0]
                
                dialog = tk.Toplevel(self.root)
                dialog.title("Select Monitor")
                dialog.geometry("400x300")
                dialog.transient(self.root)
                dialog.grab_set()
                
                selected_monitor = [None]
                
                tk.Label(dialog, text="Select monitor for screen capture:", font=("Arial", 12)).pack(pady=10)
                
                listbox = tk.Listbox(dialog, height=8)
                listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                for monitor in monitors:
                    listbox.insert(tk.END, str(monitor))
                
                listbox.selection_set(0)
                
                def on_select():
                    selection = listbox.curselection()
                    if selection:
                        selected_monitor[0] = monitors[selection[0]]
                        dialog.destroy()
                
                def on_cancel():
                    selected_monitor[0] = None
                    dialog.destroy()
                
                button_frame = tk.Frame(dialog)
                button_frame.pack(pady=10)
                
                tk.Button(button_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=5)
                tk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
                
                dialog.protocol("WM_DELETE_WINDOW", on_cancel)
                
                self.root.wait_window(dialog)
                return selected_monitor[0]
            
            def _create_selection_window(self):
                try:
                    if self.selection_window:
                        self.selection_window.destroy()
                        
                    self.selection_window = tk.Toplevel(self.root)
                    self.selection_window.attributes('-fullscreen', True)
                    self.selection_window.attributes('-alpha', 0.3)
                    self.selection_window.attributes('-topmost', True)
                    self.selection_window.configure(bg='black')
                    
                    monitor = self.selected_monitor
                    self.selection_window.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
                    
                    try:
                        screenshot = ImageGrab.grab(bbox=(monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height), all_screens=True)
                    except:
                        screenshot = ImageGrab.grab(bbox=(monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height))
                    
                    self.screenshot_tk = ImageTk.PhotoImage(screenshot)
                    
                    self.canvas = tk.Canvas(
                        self.selection_window, 
                        cursor="cross",
                        highlightthickness=0,
                        width=monitor.width,
                        height=monitor.height,
                        bg='black'
                    )
                    self.canvas.pack(fill=tk.BOTH, expand=True)
                    
                    self.canvas.create_image(0, 0, image=self.screenshot_tk, anchor=tk.NW)
                    
                    self.canvas.create_text(
                        monitor.width // 2,
                        30,
                        text=f"Select {self.title} - Click and drag to select area",
                        fill="yellow",
                        font=("Arial", 14, "bold")
                    )
                    
                    self.canvas.create_text(
                        monitor.width // 2,
                        60,
                        text="ESC to cancel",
                        fill="white",
                        font=("Arial", 12)
                    )
                    
                    self.canvas.bind("<Button-1>", self._on_click)
                    self.canvas.bind("<B1-Motion>", self._on_drag)
                    self.canvas.bind("<ButtonRelease-1>", self._on_release)
                    
                    self.selection_window.bind("<Escape>", self._on_escape)
                    self.selection_window.focus_force()
                    
                    self.start_x = None
                    self.start_y = None
                    
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Error creating selection window: {e}", exc_info=True)
                    return False
            
            def _on_click(self, event):
                self.start_x = event.x + self.selected_monitor.x
                self.start_y = event.y + self.selected_monitor.y
                
                if self.selection_rect:
                    self.canvas.delete(self.selection_rect)
                self.canvas.delete("size_info")
                    
            def _on_drag(self, event):
                if self.start_x is None or self.start_y is None:
                    return
                    
                current_x = event.x + self.selected_monitor.x
                current_y = event.y + self.selected_monitor.y
                
                if self.selection_rect:
                    self.canvas.delete(self.selection_rect)
                self.canvas.delete("size_info")
                
                canvas_x1 = self.start_x - self.selected_monitor.x
                canvas_y1 = self.start_y - self.selected_monitor.y
                canvas_x2 = event.x
                canvas_y2 = event.y
                
                self.selection_rect = self.canvas.create_rectangle(
                    canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                    outline=self.color,
                    width=3,
                    fill="",
                    dash=(8, 4)
                )
                
                width = abs(current_x - self.start_x)
                height = abs(current_y - self.start_y)
                
                if width > 5 and height > 5:
                    self.canvas.create_text(
                        (canvas_x1 + canvas_x2) / 2,
                        (canvas_y1 + canvas_y2) / 2,
                        text=f"{int(width)}×{int(height)}",
                        fill="white",
                        font=("Arial", 12, "bold"),
                        tags="size_info"
                    )
            
            def _on_release(self, event):
                if self.start_x is None or self.start_y is None:
                    return
                    
                end_x = event.x + self.selected_monitor.x
                end_y = event.y + self.selected_monitor.y
                
                self.x1 = min(self.start_x, end_x)
                self.y1 = min(self.start_y, end_y)
                self.x2 = max(self.start_x, end_x)
                self.y2 = max(self.start_y, end_y)
                
                width = abs(self.x2 - self.x1)
                height = abs(self.y2 - self.y1)
                
                if width < 3 or height < 3:
                    self.logger.warning("Selection too small, ignoring")
                    if self.selection_rect:
                        self.canvas.delete(self.selection_rect)
                    self.canvas.delete("size_info")
                    self.start_x = None
                    self.start_y = None
                    return
                
                self._show_confirm_dialog()
            
            def _on_escape(self, event):
                self.logger.info("Selection cancelled by user (ESC key)")
                if self.selection_window:
                    self.selection_window.destroy()
                    self.selection_window = None
            
            def _show_confirm_dialog(self):
                if not all([self.x1, self.y1, self.x2, self.y2]):
                    return
                
                width = abs(self.x2 - self.x1)
                height = abs(self.y2 - self.y1)
                
                try:
                    self.preview_image = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2), all_screens=True)
                    
                    debug_dir = "debug_images"
                    if not os.path.exists(debug_dir):
                        os.makedirs(debug_dir)
                    preview_path = f"{debug_dir}/{self.title.replace(' ', '_').lower()}_preview.png"
                    self.preview_image.save(preview_path)
                    
                except Exception as e:
                    self.logger.error(f"Error creating preview: {e}")
                
                self.selection_window.withdraw()
                
                confirm = messagebox.askyesno(
                    f"Confirm {self.title} Selection",
                    f"Is this the correct area for {self.title}?\n\n"
                    f"Coordinates: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})\n"
                    f"Size: {width}x{height} pixels",
                    parent=self.root
                )
                
                if confirm:
                    self.is_configured = True
                    self.logger.info(f"{self.title} selection confirmed")
                    
                    if self.selection_window:
                        self.selection_window.destroy()
                        self.selection_window = None
                    
                    if self.completion_callback:
                        try:
                            self.completion_callback()
                        except Exception as e:
                            self.logger.error(f"Error in completion callback: {e}")
                else:
                    self.selection_window.deiconify()
                    if self.canvas and self.selection_rect:
                        self.canvas.delete(self.selection_rect)
                    self.canvas.delete("size_info")
                    self.selection_rect = None
                    self.preview_image = None
                    self.start_x = None
                    self.start_y = None
            
            def get_current_screenshot_region(self):
                if not self.is_configured or not all([self.x1, self.y1, self.x2, self.y2]):
                    return None
                    
                try:
                    screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2), all_screens=True)
                    return screenshot
                except Exception as e:
                    self.logger.error(f"Error capturing region: {e}")
                    return None
        
        logger.info("Using fallback ScreenSelector implementation")
        
    except Exception as e:
        logger.error(f"Failed to create fallback ScreenSelector: {e}")
        raise

try:
    from .bar_detector import BarDetector
except ImportError:
    pass