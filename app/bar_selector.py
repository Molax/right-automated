"""
Enhanced Screen and Bar Selector with Full Screen Coverage
--------------------------------------------------------
Fixed monitor selection to ensure complete screen coverage.
"""

import os
import tkinter as tk
from tkinter import messagebox
import logging
from PIL import ImageGrab, ImageTk, Image
import numpy as np
import cv2
import time
import ctypes
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
    
    def get_full_bounds(self):
        """Get monitor bounds covering entire virtual screen if needed"""
        try:
            virtual_screen_left = ctypes.windll.user32.GetSystemMetrics(76)
            virtual_screen_top = ctypes.windll.user32.GetSystemMetrics(77)
            virtual_screen_width = ctypes.windll.user32.GetSystemMetrics(78)
            virtual_screen_height = ctypes.windll.user32.GetSystemMetrics(79)
            
            virtual_screen_right = virtual_screen_left + virtual_screen_width
            virtual_screen_bottom = virtual_screen_top + virtual_screen_height
            
            buffer_size = 500
            
            extended_left = min(self.x - buffer_size, virtual_screen_left - buffer_size)
            extended_top = min(self.y - buffer_size, virtual_screen_top - buffer_size)
            extended_right = max(self.x + self.width + buffer_size, virtual_screen_right + buffer_size)
            extended_bottom = max(self.y + self.height + buffer_size, virtual_screen_bottom + buffer_size)
            
            return (extended_left, extended_top, extended_right, extended_bottom)
        except:
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
                
                logger = logging.getLogger('PristonBot')
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

class ScreenSelector:
    def __init__(self, root):
        self.root = root
        self.logger = logging.getLogger('PristonBot')
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.is_selecting = False
        self.is_configured = False
        self.selection_window = None
        self.canvas = None
        self.selection_rect = None
        self.screenshot_tk = None
        self.preview_image = None
        self.selected_monitor = None
        
        self.dpi_scale = self._get_dpi_scale()
        self.logger.info(f"DPI scaling factor: {self.dpi_scale}")
    
    def _get_dpi_scale(self):
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            tk_width = self.root.winfo_screenwidth()
            tk_height = self.root.winfo_screenheight()
            
            scale_x = screen_width / tk_width if tk_width > 0 else 1.0
            scale_y = screen_height / tk_height if tk_height > 0 else 1.0
            
            scale = max(scale_x, scale_y)
            
            self.logger.debug(f"Screen dimensions - Real: {screen_width}x{screen_height}, Tkinter: {tk_width}x{tk_height}")
            self.logger.debug(f"Scale factors - X: {scale_x}, Y: {scale_y}, Using: {scale}")
            
            return scale if scale > 0 else 1.0
            
        except Exception as e:
            self.logger.error(f"Error getting DPI scale: {e}")
            return 1.0
    
    def is_setup(self):
        return self.is_configured
    
    def configure_from_saved(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.is_configured = True
        
        title = getattr(self, 'title', 'Selection')
        self.logger.info(f"{title} configured from saved coordinates: ({x1},{y1}) to ({x2},{y2})")
        return True
        
    def start_selection(self, title="Select Area", color="yellow"):
        self.logger.info(f"Starting selection: {title}")
        self.title = title
        self.color = color
        
        monitors = MonitorDetector.get_monitors()
        self.logger.info(f"Detected {len(monitors)} monitor(s)")
        
        if len(monitors) > 1:
            dialog = MonitorSelectionDialog(self.root, monitors)
            self.selected_monitor = dialog.show()
            
            if not self.selected_monitor:
                self.logger.info("Monitor selection cancelled")
                return
                
            self.logger.info(f"Selected: {self.selected_monitor}")
        else:
            self.selected_monitor = monitors[0] if monitors else None
            
        if not self.selected_monitor:
            self.logger.error("No monitor available")
            messagebox.showerror("Error", "No monitor detected!")
            return
        
        try:
            self.logger.debug(f"Taking screenshot for monitor {self.selected_monitor.index + 1}")
            
            full_desktop_screenshot = ImageGrab.grab(all_screens=True)
            desktop_width, desktop_height = full_desktop_screenshot.size
            self.logger.debug(f"Full desktop screenshot size: {desktop_width}x{desktop_height}")
            
            bounds = self.selected_monitor.get_full_bounds()
            ext_x1, ext_y1, ext_x2, ext_y2 = bounds
            
            virtual_screen_left = ctypes.windll.user32.GetSystemMetrics(76)
            virtual_screen_top = ctypes.windll.user32.GetSystemMetrics(77)
            virtual_screen_width = ctypes.windll.user32.GetSystemMetrics(78)
            virtual_screen_height = ctypes.windll.user32.GetSystemMetrics(79)
            
            actual_left = virtual_screen_left
            actual_top = virtual_screen_top
            actual_right = virtual_screen_left + virtual_screen_width
            actual_bottom = virtual_screen_top + virtual_screen_height
            
            crop_x1 = max(0, ext_x1 - actual_left)
            crop_y1 = max(0, ext_y1 - actual_top)
            crop_x2 = min(desktop_width, ext_x2 - actual_left)
            crop_y2 = min(desktop_height, ext_y2 - actual_top)
            
            self.logger.debug(f"Virtual screen: ({actual_left}, {actual_top}) to ({actual_right}, {actual_bottom})")
            self.logger.debug(f"Extended bounds: ({ext_x1}, {ext_y1}) to ({ext_x2}, {ext_y2})")
            self.logger.debug(f"Crop bounds: ({crop_x1}, {crop_y1}) to ({crop_x2}, {crop_y2})")
            
            monitor_screenshot = full_desktop_screenshot.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            actual_width, actual_height = monitor_screenshot.size
            
            self.logger.debug(f"Monitor screenshot: {actual_width}x{actual_height}")
            
            self.full_screenshot = monitor_screenshot
            self.screenshot_tk = ImageTk.PhotoImage(monitor_screenshot)
            
            self.window_offset_x = ext_x1
            self.window_offset_y = ext_y1
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
            return
        
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title(title)
        
        self.selection_window.overrideredirect(True)
        self.selection_window.attributes('-alpha', 0.85)
        self.selection_window.attributes('-topmost', True)
        self.selection_window.configure(bg='black')
        
        window_x = max(-1000, self.window_offset_x)
        window_y = max(-1000, self.window_offset_y)
        window_width = actual_width
        window_height = actual_height
        
        geometry_string = f"{window_width}x{window_height}+{window_x}+{window_y}"
        self.logger.debug(f"Setting selection window geometry: {geometry_string}")
        self.selection_window.geometry(geometry_string)
        
        self.selection_window.update_idletasks()
        
        self.canvas = tk.Canvas(
            self.selection_window, 
            cursor="cross",
            highlightthickness=0,
            width=window_width,
            height=window_height,
            bg='black'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.create_image(0, 0, image=self.screenshot_tk, anchor=tk.NW)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        instruction_text = f"Click and drag to select the {title}. Press ESC to cancel."
        if len(monitors) > 1:
            instruction_text += f"\nMonitor {self.selected_monitor.index + 1} selected"
            
        text_x = window_width // 2
        text_y = 50
        
        self.canvas.create_text(
            text_x,
            text_y,
            text=instruction_text,
            fill="white",
            font=("Arial", 18),
            tags="instruction"
        )
        
        monitor_info_text = f"Monitor {self.selected_monitor.index + 1}: {self.selected_monitor.width}x{self.selected_monitor.height} at ({self.selected_monitor.x}, {self.selected_monitor.y})"
        self.canvas.create_text(
            text_x,
            window_height - 50,
            text=monitor_info_text,
            fill="white",
            font=("Arial", 12),
            tags="monitor_info"
        )
        
        self.selection_window.bind("<Escape>", self._on_escape)
        self.selection_window.bind_all("<Escape>", self._on_escape)
        
        self.selection_window.focus_set()
        self.selection_window.focus_force()
        
        self.selection_window.lift()
        self.selection_window.attributes('-topmost', True)
        
    def _on_escape(self, event):
        self.logger.info(f"Selection canceled by user (ESC key)")
        if self.selection_window:
            self.selection_window.destroy()
            self.selection_window = None
        
    def on_press(self, event):
        self.is_selecting = True
        self.x1 = event.x + self.window_offset_x
        self.y1 = event.y + self.window_offset_y
        self.logger.debug(f"Started selection at canvas({event.x}, {event.y}) -> screen({self.x1}, {self.y1})")
        
        self.selection_rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, 
            outline=self.color, width=2
        )
        
    def on_drag(self, event):
        if self.is_selecting and self.selection_rect:
            start_x = self.x1 - self.window_offset_x
            start_y = self.y1 - self.window_offset_y
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            end_x = max(0, min(event.x, canvas_width))
            end_y = max(0, min(event.y, canvas_height))
            
            self.canvas.coords(self.selection_rect, start_x, start_y, end_x, end_y)
            
    def on_release(self, event):
        if not self.is_selecting:
            return
            
        self.is_selecting = False
        
        self.x2 = event.x + self.window_offset_x
        self.y2 = event.y + self.window_offset_y
        self.logger.debug(f"Completed selection at canvas({event.x}, {event.y}) -> screen({self.x2}, {self.y2})")
        
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
            
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        
        if width < 5 or height < 5:
            messagebox.showwarning(
                "Invalid Selection",
                f"The selected area is too small ({width}x{height} pixels).\n"
                "Please select a larger area.",
                parent=self.selection_window
            )
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
            return
        
        info_text = f"Selected: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})\nSize: {width}x{height} pixels"
        
        canvas_center_x = ((self.x1 + self.x2) / 2) - self.window_offset_x
        canvas_bottom_y = min((self.y2 - self.window_offset_y) + 20, self.canvas.winfo_height() - 40)
        
        self.canvas.create_text(
            canvas_center_x,
            canvas_bottom_y,
            text=info_text,
            fill="white",
            font=("Arial", 12),
            tags="selection_info"
        )
        
        try:
            crop_x1 = self.x1 - self.window_offset_x
            crop_y1 = self.y1 - self.window_offset_y
            crop_x2 = self.x2 - self.window_offset_x
            crop_y2 = self.y2 - self.window_offset_y
            
            crop_x1 = max(0, crop_x1)
            crop_y1 = max(0, crop_y1)
            crop_x2 = min(self.full_screenshot.width, crop_x2)
            crop_y2 = min(self.full_screenshot.height, crop_y2)
            
            self.preview_image = self.full_screenshot.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            self.logger.debug(f"Captured preview: {self.preview_image.width}x{self.preview_image.height}")
            
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            self.preview_image.save(f"{debug_dir}/{self.title.replace(' ', '_').lower()}_preview.png")
            
        except Exception as e:
            self.logger.error(f"Error creating preview: {e}", exc_info=True)
        
        self.selection_window.withdraw()
        
        confirm = messagebox.askyesno(
            f"Confirm {self.title} Selection",
            f"Is this the correct area for {self.title}?\n\n"
            f"Coordinates: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})\n"
            f"Size: {width}x{height} pixels\n"
            f"Monitor: {self.selected_monitor.index + 1}",
            parent=self.root
        )
        
        if confirm:
            self.is_configured = True
            self.logger.info(f"{self.title} selection confirmed: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
            if self.selection_window:
                self.selection_window.destroy()
                self.selection_window = None
        else:
            self.selection_window.deiconify()
            self.logger.info(f"{self.title} selection canceled, retrying")
            self.canvas.delete(self.selection_rect)
            self.canvas.delete("selection_info")
            self.selection_rect = None
            self.preview_image = None
            
    def get_current_screenshot_region(self):
        if not self.is_configured:
            self.logger.warning("Cannot capture region: not configured yet")
            return None
            
        try:
            if any(coord < -10000 or coord > 10000 for coord in [self.x1, self.y1, self.x2, self.y2]):
                self.logger.error(f"Coordinates out of reasonable range: ({self.x1},{self.y1}) to ({self.x2},{self.y2})")
                return None
                
            if self.x2 <= self.x1 or self.y2 <= self.y1:
                self.logger.error(f"Invalid coordinate order: ({self.x1},{self.y1}) to ({self.x2},{self.y2})")
                return None
            
            try:
                screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2), all_screens=True)
            except TypeError:
                screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
            
            if screenshot.size[0] == 0 or screenshot.size[1] == 0:
                self.logger.error(f"Screenshot has zero dimensions: {screenshot.size}")
                return None
                
            return screenshot
        except Exception as e:
            self.logger.error(f"Error capturing region: {e}", exc_info=True)
            return None


class MonitorSelectionDialog:
    def __init__(self, parent, monitors):
        self.parent = parent
        self.monitors = monitors
        self.selected_monitor = None
        self.dialog = None
        
    def show(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Monitor")
        
        dialog_width = 600
        dialog_height = 500
        
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.dialog.resizable(True, True)
        self.dialog.minsize(500, 400)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self._create_ui()
        
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        self.dialog.after_idle(self.dialog.attributes, '-topmost', False)
        
        self.dialog.focus_force()
        
        self.parent.wait_window(self.dialog)
        
        return self.selected_monitor
        
    def _create_ui(self):
        main_frame = tk.Frame(self.dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(
            main_frame,
            text="Multiple Monitors Detected",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        instructions = tk.Label(
            main_frame,
            text="Please select which monitor to use for screen selection:\n"
                 "(Extended coverage will ensure full screen access)",
            font=("Arial", 11),
            bg="white"
        )
        instructions.grid(row=1, column=0, pady=(0, 15))
        
        list_frame = tk.Frame(main_frame, relief=tk.SOLID, borderwidth=1)
        list_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.monitor_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 11),
            selectmode=tk.SINGLE,
            activestyle='none',
            height=8
        )
        self.monitor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.monitor_listbox.yview)
        
        for monitor in self.monitors:
            display_text = str(monitor) + " (Full Coverage)"
            self.monitor_listbox.insert(tk.END, display_text)
            
        for i, monitor in enumerate(self.monitors):
            if monitor.is_primary:
                self.monitor_listbox.selection_set(i)
                self.monitor_listbox.see(i)
                break
        else:
            if self.monitors:
                self.monitor_listbox.selection_set(0)
        
        preview_frame = tk.LabelFrame(
            main_frame, 
            text="Monitor Layout Preview",
            bg="white",
            font=("Arial", 10)
        )
        preview_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=560,
            height=120,
            bg="#f0f0f0",
            highlightthickness=0
        )
        self.preview_canvas.pack(padx=10, pady=10)
        
        self._draw_monitor_layout()
        
        self.monitor_listbox.bind('<<ListboxSelect>>', self._on_selection_change)
        
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.grid(row=4, column=0, sticky="ew")
        
        button_frame.grid_columnconfigure(0, weight=1)
        
        button_container = tk.Frame(button_frame, bg="white")
        button_container.grid(row=0, column=0, sticky="e")
        
        select_btn = tk.Button(
            button_container,
            text="Select Monitor",
            command=self._on_select,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        select_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = tk.Button(
            button_container,
            text="Cancel",
            command=self._on_cancel,
            width=12,
            height=2,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        cancel_btn.pack(side=tk.RIGHT)
        
        self.monitor_listbox.bind('<Double-Button-1>', lambda e: self._on_select())
        
        info_label = tk.Label(
            main_frame,
            text="Note: Full coverage ensures complete screen access",
            font=("Arial", 9, "italic"),
            bg="white",
            fg="#666666"
        )
        info_label.grid(row=5, column=0, pady=(10, 0))
        
    def _draw_monitor_layout(self):
        self.preview_canvas.delete("all")
        
        if not self.monitors:
            return
            
        all_bounds = [m.get_full_bounds() for m in self.monitors]
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        canvas_width = 540
        canvas_height = 100
        
        if total_width > 0 and total_height > 0:
            scale_x = canvas_width / total_width
            scale_y = canvas_height / total_height
            scale = min(scale_x, scale_y) * 0.8
        else:
            scale = 1.0
        
        scaled_width = total_width * scale
        scaled_height = total_height * scale
        offset_x = (560 - scaled_width) / 2
        offset_y = (120 - scaled_height) / 2
        
        selection = self.monitor_listbox.curselection()
        selected_index = selection[0] if selection else 0
        
        for i, monitor in enumerate(self.monitors):
            ext_x1, ext_y1, ext_x2, ext_y2 = monitor.get_full_bounds()
            
            ext_x1_scaled = (ext_x1 - min_x) * scale + offset_x
            ext_y1_scaled = (ext_y1 - min_y) * scale + offset_y
            ext_x2_scaled = (ext_x2 - min_x) * scale + offset_x
            ext_y2_scaled = (ext_y2 - min_y) * scale + offset_y
            
            x1 = (monitor.x - min_x) * scale + offset_x
            y1 = (monitor.y - min_y) * scale + offset_y
            x2 = x1 + monitor.width * scale
            y2 = y1 + monitor.height * scale
            
            is_selected = i == selected_index
            
            if is_selected:
                self.preview_canvas.create_rectangle(
                    ext_x1_scaled, ext_y1_scaled, ext_x2_scaled, ext_y2_scaled,
                    outline="#4CAF50",
                    width=1,
                    dash=(3, 3)
                )
            
            color = "#4CAF50" if is_selected else "#E0E0E0"
            outline = "#2E7D32" if is_selected else "#9E9E9E"
            width = 3 if is_selected else 2
            
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=outline,
                width=width
            )
            
            self.preview_canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=str(i + 1),
                font=("Arial", 12, "bold"),
                fill="white" if is_selected else "black"
            )
            
    def _on_selection_change(self, event):
        self._draw_monitor_layout()
        
    def _on_select(self):
        selection = self.monitor_listbox.curselection()
        if selection:
            self.selected_monitor = self.monitors[selection[0]]
            self.dialog.destroy()
        else:
            messagebox.showwarning(
                "No Selection",
                "Please select a monitor from the list.",
                parent=self.dialog
            )
            
    def _on_cancel(self):
        self.selected_monitor = None
        self.dialog.destroy()


class BarDetector:
    def __init__(self, title, color_range):
        self.title = title
        self.color_range = color_range
        self.logger = logging.getLogger('PristonBot')
        
    def detect_percentage(self, image):
        try:
            if image is None:
                self.logger.warning(f"Cannot detect {self.title} percentage: image is None")
                return 100
                
            np_image = np.array(image)
            
            if np_image.size == 0:
                self.logger.warning(f"Cannot detect {self.title} percentage: image is empty")
                return 100
            
            hsv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
            
            if self.title == "Health":
                lower1 = np.array([0, 50, 50])
                upper1 = np.array([10, 255, 255])
                mask1 = cv2.inRange(hsv_image, lower1, upper1)
                
                lower2 = np.array([160, 50, 50])
                upper2 = np.array([180, 255, 255])
                mask2 = cv2.inRange(hsv_image, lower2, upper2)
                
                mask = mask1 | mask2
                
            elif self.title == "Mana":
                lower = np.array([100, 50, 50])
                upper = np.array([140, 255, 255])
                mask = cv2.inRange(hsv_image, lower, upper)
                
            else:
                lower = np.array([40, 50, 50])
                upper = np.array([80, 255, 255])
                mask = cv2.inRange(hsv_image, lower, upper)
            
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            mask_filename = f"{debug_dir}/{self.title.lower()}_mask_{time.strftime('%H%M%S')}.png"
            cv2.imwrite(mask_filename, mask)
            
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            total_pixels = mask.shape[0] * mask.shape[1]
            if total_pixels == 0:
                return 100
                
            filled_pixels = cv2.countNonZero(mask)
            percentage = (filled_pixels / total_pixels) * 100
            
            self.logger.debug(f"{self.title} bar percentage: {percentage:.1f}%")
            return max(0, min(100, percentage))
            
        except Exception as e:
            self.logger.error(f"Error detecting {self.title} bar percentage: {e}", exc_info=True)
            return 100


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