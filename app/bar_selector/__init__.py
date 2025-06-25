"""
Bar Selector Module - Simple Import Structure
------------------------------------------
Provides the main classes needed for bar selection.
"""

try:
    from .screen_selector import ScreenSelector
    from .bar_detector import BarDetector
    from .color_ranges import HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE
except ImportError:
    import os
    import tkinter as tk
    from tkinter import messagebox
    import logging
    from PIL import ImageGrab, ImageTk, Image
    import ctypes
    import numpy as np
    import cv2
    import time
    
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
            self.title = "Selection"
            self.color = "yellow"
            
            self.full_screenshot = None
            self.window_offset_x = 0
            self.window_offset_y = 0
            
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
            
            try:
                screen_width = ctypes.windll.user32.GetSystemMetrics(0)
                screen_height = ctypes.windll.user32.GetSystemMetrics(1)
                
                self.full_screenshot = ImageGrab.grab(all_screens=True)
                
                overlay_width = min(1200, int(screen_width * 0.8))
                overlay_height = min(800, int(screen_height * 0.8))
                
                center_x = screen_width // 2
                center_y = screen_height // 2
                
                window_x = center_x - overlay_width // 2
                window_y = center_y - overlay_height // 2
                
                crop_x = max(0, window_x)
                crop_y = max(0, window_y)
                crop_right = min(self.full_screenshot.width, window_x + overlay_width)
                crop_bottom = min(self.full_screenshot.height, window_y + overlay_height)
                
                display_screenshot = self.full_screenshot.crop((crop_x, crop_y, crop_right, crop_bottom))
                
                self.window_offset_x = crop_x
                self.window_offset_y = crop_y
                
            except Exception as e:
                self.logger.error(f"Error taking screenshot: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
                return
            
            self.selection_window = tk.Toplevel(self.root)
            self.selection_window.title(f"{title} - Click and drag to select")
            
            actual_width, actual_height = display_screenshot.size
            
            self.selection_window.geometry(f"{actual_width}x{actual_height}+{window_x}+{window_y}")
            self.selection_window.resizable(False, False)
            self.selection_window.attributes('-topmost', True)
            self.selection_window.configure(bg='black')
            
            main_frame = tk.Frame(self.selection_window, bg='black')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            info_frame = tk.Frame(main_frame, bg='darkblue', height=40)
            info_frame.pack(fill=tk.X, side=tk.TOP)
            info_frame.pack_propagate(False)
            
            instruction_label = tk.Label(
                info_frame,
                text=f"Select {title} - Click and drag on the image below",
                fg="white",
                bg="darkblue",
                font=("Arial", 12, "bold")
            )
            instruction_label.pack(expand=True)
            
            canvas_frame = tk.Frame(main_frame, bg='black')
            canvas_frame.pack(fill=tk.BOTH, expand=True)
            
            self.canvas = tk.Canvas(
                canvas_frame,
                cursor="cross",
                highlightthickness=1,
                highlightbackground="yellow",
                width=actual_width-4,
                height=actual_height-44,
                bg='black'
            )
            self.canvas.pack(padx=2, pady=2)
            
            self.screenshot_tk = ImageTk.PhotoImage(display_screenshot)
            self.canvas.create_image(0, 0, image=self.screenshot_tk, anchor=tk.NW)
            
            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)
            
            button_frame = tk.Frame(main_frame, bg='darkgray', height=30)
            button_frame.pack(fill=tk.X, side=tk.BOTTOM)
            button_frame.pack_propagate(False)
            
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel (ESC)",
                command=self._cancel_selection,
                bg="#f44336",
                fg="white",
                font=("Arial", 10)
            )
            cancel_btn.pack(side=tk.LEFT, padx=5, pady=3)
            
            help_label = tk.Label(
                button_frame,
                text="Focus on the bottom area where status bars are located",
                fg="black",
                bg="darkgray",
                font=("Arial", 9)
            )
            help_label.pack(side=tk.RIGHT, padx=5, pady=3)
            
            self.selection_window.bind("<Escape>", lambda e: self._cancel_selection())
            self.selection_window.focus_set()
            self.selection_window.grab_set()
            
        def _cancel_selection(self):
            self.logger.info(f"Selection canceled by user")
            if self.selection_window:
                self.selection_window.destroy()
                self.selection_window = None
            
        def on_press(self, event):
            self.is_selecting = True
            
            self.x1 = self.window_offset_x + event.x
            self.y1 = self.window_offset_y + event.y
            
            self.selection_rect = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y, 
                outline=self.color, width=3
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
            
            self.x2 = self.window_offset_x + event.x
            self.y2 = self.window_offset_y + event.y
            
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
            
            try:
                rel_x1 = self.x1
                rel_y1 = self.y1
                rel_x2 = self.x2
                rel_y2 = self.y2
                
                rel_x1 = max(0, rel_x1)
                rel_y1 = max(0, rel_y1)
                rel_x2 = min(self.full_screenshot.width, rel_x2)
                rel_y2 = min(self.full_screenshot.height, rel_y2)
                
                self.preview_image = self.full_screenshot.crop((rel_x1, rel_y1, rel_x2, rel_y2))
                
                debug_dir = "debug_images"
                if not os.path.exists(debug_dir):
                    os.makedirs(debug_dir)
                preview_path = f"{debug_dir}/{self.title.replace(' ', '_').lower()}_preview.png"
                self.preview_image.save(preview_path)
                self.logger.debug(f"Saved preview to {preview_path}")
                
            except Exception as e:
                self.logger.error(f"Error creating preview: {e}", exc_info=True)
            
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
                self.logger.info(f"{self.title} selection confirmed: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
                if self.selection_window:
                    self.selection_window.destroy()
                    self.selection_window = None
            else:
                self.selection_window.deiconify()
                self.canvas.delete(self.selection_rect)
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

    HEALTH_COLOR_RANGE = (np.array([0, 50, 50]), np.array([10, 255, 255]))
    MANA_COLOR_RANGE = (np.array([100, 50, 50]), np.array([140, 255, 255]))
    STAMINA_COLOR_RANGE = (np.array([40, 50, 50]), np.array([80, 255, 255]))

__all__ = [
    'ScreenSelector',
    'BarDetector',
    'HEALTH_COLOR_RANGE',
    'MANA_COLOR_RANGE',
    'STAMINA_COLOR_RANGE'
]