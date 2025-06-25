"""
Screen Selector with Monitor Support
-----------------------------------
Fixed implementation for selecting screen regions.
"""

import os
import tkinter as tk
from tkinter import messagebox
import logging
from PIL import ImageGrab, ImageTk, Image
import ctypes
from .monitor_detection import MonitorDetector
from .monitor_selection_dialog import MonitorSelectionDialog

logger = logging.getLogger('PristonBot')

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
        self.title = "Selection"
        self.color = "yellow"
        
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
            
            return scale if scale > 0 else 1.0
            
        except Exception as e:
            self.logger.error(f"Error getting DPI scale: {e}")
            return 1.0
    
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
            
            bounds = self.selected_monitor.get_capture_bounds()
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
            
            monitor_screenshot = full_desktop_screenshot.crop((crop_x1, crop_y1, crop_x2, crop_y2))
            actual_width, actual_height = monitor_screenshot.size
            
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
        self.selection_window.geometry(geometry_string)
        
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
        
        monitor_info_text = f"Monitor {self.selected_monitor.index + 1}: {self.selected_monitor.width}x{self.selected_monitor.height}"
        self.canvas.create_text(
            text_x,
            window_height - 50,
            text=monitor_info_text,
            fill="white",
            font=("Arial", 12),
            tags="monitor_info"
        )
        
        self.selection_window.bind("<Escape>", self._on_escape)
        self.selection_window.focus_set()
        
    def _on_escape(self, event):
        self.logger.info(f"Selection canceled by user (ESC key)")
        if self.selection_window:
            self.selection_window.destroy()
            self.selection_window = None
        
    def on_press(self, event):
        self.is_selecting = True
        self.x1 = event.x + self.window_offset_x
        self.y1 = event.y + self.window_offset_y
        
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
            self.canvas.delete(self.selection_rect)
            self.canvas.delete("selection_info")
            self.selection_rect = None
            self.preview_image = None
            
    def get_current_screenshot_region(self):
        if not self.is_configured:
            self.logger.warning("Cannot capture region: not configured yet")
            return None
            
        if not all([self.x1, self.y1, self.x2, self.y2]):
            self.logger.warning("Cannot capture region: coordinates not set")
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