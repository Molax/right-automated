import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab
import logging
import ctypes

class ScreenSelector:
    def __init__(self, root):
        self.root = root
        self.logger = logging.getLogger(__name__)
        
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
        
    def start_selection(self, title="Select Area", color="yellow"):
        self.logger.info(f"Starting selection: {title}")
        self.title = title
        self.color = color
        
        from .monitor_detection import MonitorDetector
        from .monitor_selection_dialog import MonitorSelectionDialog
        
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
            
        self._create_selection_window()
        
    def _create_selection_window(self):
        if self.selection_window:
            self.selection_window.destroy()
            
        monitor = self.selected_monitor
        self.logger.info(f"Creating selection window for monitor: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
        
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            
            virtual_left = user32.GetSystemMetrics(76)
            virtual_top = user32.GetSystemMetrics(77)
            virtual_width = user32.GetSystemMetrics(78)
            virtual_height = user32.GetSystemMetrics(79)
            
            self.logger.debug(f"Virtual screen: {virtual_width}x{virtual_height} at ({virtual_left}, {virtual_top})")
            
            full_screenshot = ImageGrab.grab(all_screens=True)
            screenshot_width, screenshot_height = full_screenshot.size
            self.logger.debug(f"Full screenshot: {screenshot_width}x{screenshot_height}")
            
            # Add larger buffer for Monitor 2, smaller for Monitor 1
            buffer_pixels = 400 if getattr(monitor, 'index', 0) > 0 else 80
            
            crop_left = max(0, (monitor.x - virtual_left) - buffer_pixels)
            crop_top = max(0, (monitor.y - virtual_top) - buffer_pixels)
            crop_right = min(screenshot_width, (monitor.x - virtual_left) + monitor.width + buffer_pixels)
            crop_bottom = min(screenshot_height, (monitor.y - virtual_top) + monitor.height + buffer_pixels)
            
            self.logger.debug(f"Monitor bounds: ({monitor.x}, {monitor.y}) {monitor.width}x{monitor.height}")
            self.logger.debug(f"Cropping with {buffer_pixels}px buffer: ({crop_left}, {crop_top}) to ({crop_right}, {crop_bottom})")
            
            monitor_screenshot = full_screenshot.crop((crop_left, crop_top, crop_right, crop_bottom))
            actual_width, actual_height = monitor_screenshot.size
            
            self.logger.info(f"Monitor screenshot: {actual_width}x{actual_height}")
            
            if actual_width <= 0 or actual_height <= 0:
                raise ValueError(f"Invalid screenshot dimensions: {actual_width}x{actual_height}")
            
            # Store the exact offset for accurate coordinate conversion
            self.crop_offset_x = crop_left
            self.crop_offset_y = crop_top
            self.virtual_offset_x = virtual_left
            self.virtual_offset_y = virtual_top
            
            self.logger.debug(f"Crop offset: ({self.crop_offset_x}, {self.crop_offset_y})")
            self.logger.debug(f"Virtual offset: ({self.virtual_offset_x}, {self.virtual_offset_y})")
                
            self.screenshot_tk = ImageTk.PhotoImage(monitor_screenshot)
            
        except Exception as e:
            self.logger.error(f"Error taking monitor screenshot: {e}")
            messagebox.showerror("Error", f"Failed to capture monitor screenshot: {e}")
            return
            
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title(f"Select {getattr(self, 'title', 'Area')} - Monitor {getattr(monitor, 'index', 0) + 1}")
        
        # Use expanded size for the window to show more content
        expanded_width = actual_width
        expanded_height = actual_height
        
        # Position window to cover the screenshot area
        window_x = self.crop_offset_x + self.virtual_offset_x
        window_y = self.crop_offset_y + self.virtual_offset_y
        
        self.selection_window.geometry(f"{expanded_width}x{expanded_height}+{window_x}+{window_y}")
        self.selection_window.attributes('-topmost', True)
        self.selection_window.configure(bg='black')
        self.selection_window.overrideredirect(True)
        
        main_container = tk.Frame(self.selection_window, bg='black')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # No header frame - keep it simple to avoid coordinate issues
        self.canvas = tk.Canvas(
            main_container,
            highlightthickness=0,
            cursor="crosshair",
            bg='gray10'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        if hasattr(self, 'screenshot_tk') and self.screenshot_tk:
            self.canvas.create_image(0, 0, image=self.screenshot_tk, anchor=tk.NW)
        
        # Add instructions directly on canvas
        self.canvas.create_text(
            expanded_width // 2,
            30,
            text=f"Select {getattr(self, 'title', 'Area')} - Monitor {getattr(monitor, 'index', 0) + 1} (Expanded view)",
            fill="yellow",
            font=("Arial", 12, "bold")
        )
        
        self.canvas.create_text(
            expanded_width // 2,
            50,
            text="Click and drag to select • ESC to cancel",
            fill="white",
            font=("Arial", 10)
        )
        
        footer_info = f"Monitor {getattr(monitor, 'index', 0) + 1}: {monitor.width}x{monitor.height}"
        self.canvas.create_text(
            expanded_width // 2,
            expanded_height - 20,
            text=footer_info,
            fill="lime",
            font=("Arial", 10, "bold")
        )
        
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        
        self.selection_window.bind("<Escape>", lambda e: self._cancel_selection())
        self.selection_window.focus_force()
        
        self.start_x = None
        self.start_y = None
        
    def _on_click(self, event):
        if self.start_x is not None or self.start_y is not None:
            return
            
        # Convert canvas coordinates directly to global coordinates
        # Canvas coordinates + crop position + virtual screen offset = global coordinates
        self.start_x = event.x + self.crop_offset_x + self.virtual_offset_x
        self.start_y = event.y + self.crop_offset_y + self.virtual_offset_y
        
        self.logger.debug(f"Click at canvas ({event.x}, {event.y}) -> global ({self.start_x}, {self.start_y})")
        
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.canvas.delete("size_info")
            
    def _on_drag(self, event):
        if self.start_x is None or self.start_y is None:
            return
            
        # Convert canvas coordinates to global coordinates
        current_x = event.x + self.crop_offset_x + self.virtual_offset_x
        current_y = event.y + self.crop_offset_y + self.virtual_offset_y
        
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.canvas.delete("size_info")
            
        # For drawing on canvas, use the raw canvas coordinates
        canvas_x1 = self.start_x - self.crop_offset_x - self.virtual_offset_x
        canvas_y1 = self.start_y - self.crop_offset_y - self.virtual_offset_y
        canvas_x2 = event.x
        canvas_y2 = event.y
        
        self.selection_rect = self.canvas.create_rectangle(
            canvas_x1, canvas_y1, canvas_x2, canvas_y2,
            outline=getattr(self, 'color', 'red'),
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
            self.logger.warning("Mouse release without valid start coordinates")
            return
            
        # Convert canvas coordinates to global coordinates
        end_x = event.x + self.crop_offset_x + self.virtual_offset_x
        end_y = event.y + self.crop_offset_y + self.virtual_offset_y
        
        self.x1 = min(self.start_x, end_x)
        self.y1 = min(self.start_y, end_y)
        self.x2 = max(self.start_x, end_x)
        self.y2 = max(self.start_y, end_y)
        
        width = abs(self.x2 - self.x1)
        height = abs(self.y2 - self.y1)
        
        if width < 10 or height < 10:
            self.logger.warning("Selection too small, ignoring")
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            self.canvas.delete("size_info")
            self.start_x = None
            self.start_y = None
            return
            
        self.logger.info(f"Selection made: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
        self.show_confirm_dialog()
        
    def _cancel_selection(self):
        self.logger.info("Selection cancelled")
        if self.selection_window:
            self.selection_window.destroy()
            self.selection_window = None
            
    def show_confirm_dialog(self):
        if not all([self.x1, self.y1, self.x2, self.y2]):
            self.logger.error("Cannot show confirm dialog: coordinates not set")
            return
            
        width = abs(self.x2 - self.x1)
        height = abs(self.y2 - self.y1)
        
        try:
            preview_screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2), all_screens=True)
            self.preview_image = preview_screenshot
        except Exception as e:
            self.logger.error(f"Error creating preview: {e}")
        
        self.selection_window.withdraw()
        
        confirm_dialog = tk.Toplevel(self.root)
        confirm_dialog.title(f"Confirm {getattr(self, 'title', 'Selection')}")
        
        dialog_width = 500
        dialog_height = 450
        
        screen_width = confirm_dialog.winfo_screenwidth()
        screen_height = confirm_dialog.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        confirm_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        confirm_dialog.resizable(False, False)
        confirm_dialog.transient(self.root)
        confirm_dialog.grab_set()
        
        main_frame = tk.Frame(confirm_dialog, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            main_frame,
            text=f"Confirm {getattr(self, 'title', 'Selection')}",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title_label.pack(pady=(0, 15))
        
        info_frame = tk.Frame(main_frame, bg="white")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        coords_text = f"Coordinates: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})"
        size_text = f"Size: {width} × {height} pixels"
        
        coords_label = tk.Label(
            info_frame,
            text=coords_text,
            font=("Consolas", 10),
            bg="white",
            fg="#666666"
        )
        coords_label.pack()
        
        size_label = tk.Label(
            info_frame,
            text=size_text,
            font=("Arial", 11, "bold"),
            bg="white"
        )
        size_label.pack(pady=(5, 0))
        
        if self.preview_image:
            preview_frame = tk.Frame(main_frame, bg="white")
            preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            try:
                max_preview_width = 400
                max_preview_height = 200
                
                img_width, img_height = self.preview_image.size
                
                scale_x = max_preview_width / img_width
                scale_y = max_preview_height / img_height
                scale = min(scale_x, scale_y, 1.0)
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                preview_resized = self.preview_image.resize((new_width, new_height), Image.LANCZOS)
                preview_tk = ImageTk.PhotoImage(preview_resized)
                
                preview_label = tk.Label(
                    preview_frame, 
                    image=preview_tk, 
                    relief=tk.SOLID, 
                    borderwidth=2,
                    bg="white"
                )
                preview_label.image = preview_tk
                preview_label.pack(expand=True)
                
            except Exception as e:
                self.logger.error(f"Error displaying preview: {e}")
                error_label = tk.Label(
                    preview_frame,
                    text="Preview not available",
                    font=("Arial", 10),
                    fg="#999999",
                    bg="white"
                )
                error_label.pack(expand=True)
        
        question_label = tk.Label(
            main_frame,
            text=f"Is this the correct {getattr(self, 'title', 'area')}?",
            font=("Arial", 12),
            bg="white"
        )
        question_label.pack(pady=(0, 20))
        
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill=tk.X)
        
        def confirm_selection():
            self.is_configured = True
            self.logger.info(f"{getattr(self, 'title', 'Selection')} confirmed: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
            confirm_dialog.destroy()
            if self.selection_window:
                self.selection_window.destroy()
                self.selection_window = None
        
        def retry_selection():
            confirm_dialog.destroy()
            if self.selection_window:
                self.selection_window.deiconify()
                if self.canvas and self.selection_rect:
                    self.canvas.delete(self.selection_rect)
                self.canvas.delete("size_info")
                self.selection_rect = None
                self.preview_image = None
                self.start_x = None
                self.start_y = None
        
        retry_btn = tk.Button(
            button_frame,
            text="Try Again",
            command=retry_selection,
            width=15,
            height=2,
            font=("Arial", 11),
            relief=tk.RAISED,
            borderwidth=2
        )
        retry_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        confirm_btn = tk.Button(
            button_frame,
            text="Confirm Selection",
            command=confirm_selection,
            width=18,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.RAISED,
            borderwidth=2
        )
        confirm_btn.pack(side=tk.RIGHT)
        
        confirm_dialog.protocol("WM_DELETE_WINDOW", retry_selection)
        
        confirm_dialog.lift()
        confirm_dialog.focus_force()
        
    def get_current_screenshot_region(self):
        if not self.is_configured:
            self.logger.warning("Cannot capture region: not configured yet")
            return None
            
        if not all([self.x1, self.y1, self.x2, self.y2]):
            self.logger.warning("Cannot capture region: coordinates not set")
            return None
            
        try:
            if any(coord < -10000 or coord > 10000 for coord in [self.x1, self.y1, self.x2, self.y2]):
                self.logger.error(f"Coordinates out of range: ({self.x1},{self.y1}) to ({self.x2},{self.y2})")
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
            
    def configure_from_saved(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.is_configured = True
        
        title = getattr(self, 'title', 'Selection')
        self.logger.info(f"{title} configured from saved coordinates: ({x1},{y1}) to ({x2},{y2})")
        return True
        
    def is_setup(self):
        return self.is_configured