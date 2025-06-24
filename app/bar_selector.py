"""
Fixed Screen and Bar Selector for Priston Tale Potion Bot
----------------------------------------------------------
This module fixes high-DPI display issues and coordinate scaling problems.
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
from ctypes import wintypes

class ScreenSelector:
    """Class for selecting areas on the screen with proper DPI handling"""
    
    def __init__(self, root):
        """
        Initialize the screen selector
        
        Args:
            root: The tkinter root window
        """
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
        
        # Get DPI scaling factor
        self.dpi_scale = self._get_dpi_scale()
        self.logger.info(f"DPI scaling factor: {self.dpi_scale}")
    
    def _get_dpi_scale(self):
        """Get the DPI scaling factor for the current display"""
        try:
            # Get DPI awareness
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            
            # Get actual screen dimensions
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # Get tkinter's reported screen dimensions
            tk_width = self.root.winfo_screenwidth()
            tk_height = self.root.winfo_screenheight()
            
            # Calculate scaling factor
            scale_x = screen_width / tk_width if tk_width > 0 else 1.0
            scale_y = screen_height / tk_height if tk_height > 0 else 1.0
            
            # Use the average or the maximum scale
            scale = max(scale_x, scale_y)
            
            self.logger.debug(f"Screen dimensions - Real: {screen_width}x{screen_height}, Tkinter: {tk_width}x{tk_height}")
            self.logger.debug(f"Scale factors - X: {scale_x}, Y: {scale_y}, Using: {scale}")
            
            return scale if scale > 0 else 1.0
            
        except Exception as e:
            self.logger.error(f"Error getting DPI scale: {e}")
            return 1.0
    
    def is_setup(self):
        """Check if the selection is configured"""
        return self.is_configured
    
    def configure_from_saved(self, x1, y1, x2, y2):
        """Configure selection from saved coordinates without UI interaction
        
        Args:
            x1, y1: Top-left coordinates
            x2, y2: Bottom-right coordinates
            
        Returns:
            True if successful
        """
        # Validate coordinates are reasonable
        max_reasonable_coord = 10000  # Reasonable maximum coordinate
        
        if any(coord > max_reasonable_coord for coord in [x1, y1, x2, y2]):
            self.logger.warning(f"Coordinates seem too large (DPI scaling issue?): ({x1},{y1}) to ({x2},{y2})")
            # Try to correct by dividing by common DPI scales
            for scale in [1.25, 1.5, 2.0, 2.5, 3.0]:
                corrected_coords = [int(coord / scale) for coord in [x1, y1, x2, y2]]
                if all(coord <= max_reasonable_coord for coord in corrected_coords):
                    x1, y1, x2, y2 = corrected_coords
                    self.logger.info(f"Corrected coordinates by scale {scale}: ({x1},{y1}) to ({x2},{y2})")
                    break
            else:
                self.logger.error("Could not correct coordinates - they remain too large")
                return False
        
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.is_configured = True
        
        title = getattr(self, 'title', 'Selection')
        self.logger.info(f"{title} configured from saved coordinates: ({x1},{y1}) to ({x2},{y2})")
        return True
        
    def start_selection(self, title="Select Area", color="yellow"):
        """Start the screen selection process"""
        self.logger.info(f"Starting selection: {title}")
        self.title = title
        self.color = color
        
        # Take a screenshot first to get actual dimensions
        try:
            screenshot = ImageGrab.grab()
            actual_width, actual_height = screenshot.size
            self.logger.debug(f"Screenshot captured: {actual_width}x{actual_height}")
            
            # Validate screenshot size is reasonable
            if actual_width > 10000 or actual_height > 10000:
                self.logger.warning(f"Screenshot dimensions seem too large: {actual_width}x{actual_height}")
                # Try taking a smaller screenshot
                try:
                    # Get screen metrics directly from Windows API
                    user32 = ctypes.windll.user32
                    screen_width = user32.GetSystemMetrics(0)
                    screen_height = user32.GetSystemMetrics(1)
                    self.logger.info(f"Windows API screen size: {screen_width}x{screen_height}")
                    
                    if screen_width <= 8000 and screen_height <= 8000:  # Reasonable limits
                        screenshot = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))
                        actual_width, actual_height = screenshot.size
                        self.logger.info(f"Corrected screenshot size: {actual_width}x{actual_height}")
                except Exception as e:
                    self.logger.error(f"Error getting corrected screenshot: {e}")
                    return
                    
        except Exception as e:
            self.logger.error(f"Error taking initial screenshot: {e}")
            return
        
        # Create selection window that covers the entire screen
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title(title)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.8)  # Semi-transparent
        self.selection_window.attributes('-topmost', True)  # Keep on top
        self.selection_window.configure(bg='black')
        
        # Store the screenshot for later use
        self.full_screenshot = screenshot
        
        # Resize screenshot for display if needed
        display_width = min(actual_width, 3840)  # Max 4K width for display
        display_height = min(actual_height, 2160)  # Max 4K height for display
        
        if actual_width > display_width or actual_height > display_height:
            display_screenshot = screenshot.resize((display_width, display_height), Image.Resampling.LANCZOS)
            self.logger.debug(f"Resized screenshot for display: {display_width}x{display_height}")
        else:
            display_screenshot = screenshot
            
        self.screenshot_tk = ImageTk.PhotoImage(display_screenshot)
        
        # Calculate scale factor for coordinate conversion
        self.coord_scale_x = actual_width / display_width
        self.coord_scale_y = actual_height / display_height
        self.logger.debug(f"Coordinate scale factors: X={self.coord_scale_x}, Y={self.coord_scale_y}")
        
        # Create a canvas to display the screenshot and allow selection
        self.canvas = tk.Canvas(self.selection_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.screenshot_tk, anchor=tk.NW)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Add instructions
        instruction_text = f"Click and drag to select the {title}. Press ESC to cancel."
        text_y = 50
        self.canvas.create_text(
            display_width // 2,
            text_y,
            text=instruction_text,
            fill="white",
            font=("Arial", 18),
            tags="instruction"
        )
        
        # Bind escape key to cancel
        self.selection_window.bind("<Escape>", self._on_escape)
        self.selection_window.focus_set()  # Ensure window can receive key events
        
    def _on_escape(self, event):
        """Handle escape key press"""
        self.logger.info(f"Selection canceled by user (ESC key)")
        self.selection_window.destroy()
        
    def on_press(self, event):
        """Handle mouse button press"""
        self.is_selecting = True
        self.x1 = int(event.x * self.coord_scale_x)
        self.y1 = int(event.y * self.coord_scale_y)
        self.logger.debug(f"Started selection at canvas({event.x}, {event.y}) -> screen({self.x1}, {self.y1})")
        
        # Create the selection rectangle on canvas coordinates
        self.selection_rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, 
            outline=self.color, width=2
        )
        
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.is_selecting:
            # Update canvas rectangle
            canvas_x1 = self.x1 / self.coord_scale_x
            canvas_y1 = self.y1 / self.coord_scale_y
            self.canvas.coords(self.selection_rect, canvas_x1, canvas_y1, event.x, event.y)
            
    def on_release(self, event):
        """Handle mouse button release"""
        if not self.is_selecting:
            return
            
        self.is_selecting = False
        self.x2 = int(event.x * self.coord_scale_x)
        self.y2 = int(event.y * self.coord_scale_y)
        self.logger.debug(f"Completed selection to canvas({event.x}, {event.y}) -> screen({self.x2}, {self.y2})")
        
        # Ensure coordinates are ordered correctly (top-left to bottom-right)
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
            
        # Display selected area details
        canvas_center_x = (self.x1 + self.x2) / 2 / self.coord_scale_x
        canvas_center_y = (self.y2 / self.coord_scale_y) + 20
        
        self.canvas.create_text(
            canvas_center_x,
            canvas_center_y,
            text=f"Selected: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})",
            fill="white",
            font=("Arial", 12),
            tags="selection_info"
        )
        
        # Check for valid selection size
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        
        if width < 5 or height < 5:
            messagebox.showwarning(
                "Warning: Small Selection",
                f"The selected area is very small ({width}x{height} pixels). " +
                "This might make detection difficult. Consider selecting a larger area."
            )
            self.logger.warning(f"User made a small selection: {width}x{height} pixels")
        
        # Validate coordinates are reasonable
        max_coord = 5000  # Reasonable maximum for modern displays
        if any(coord > max_coord for coord in [self.x1, self.y1, self.x2, self.y2]):
            self.logger.warning(f"Selection coordinates seem large: ({self.x1},{self.y1}) to ({self.x2},{self.y2})")
        
        # Capture preview image of selected area
        try:
            # Use the original full screenshot to create the preview
            preview = self.full_screenshot.crop((self.x1, self.y1, self.x2, self.y2))
            self.preview_image = preview
            self.logger.debug(f"Captured preview image: {preview.width}x{preview.height}")
            
            # Save the preview image for debugging
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            preview.save(f"{debug_dir}/{self.title.replace(' ', '_').lower()}_preview.png")
            
            # Special processing for vertical bars
            if preview.height > preview.width * 2:  # Likely a vertical bar
                self.logger.info(f"Detected vertical bar")
                self.preview_image_rotated = preview.rotate(90, expand=True)
                self.preview_image_rotated.save(f"{debug_dir}/{self.title.replace(' ', '_').lower()}_preview_rotated.png")
            else:
                self.preview_image_rotated = None
                
        except Exception as e:
            self.logger.error(f"Error creating preview image: {e}", exc_info=True)
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            f"Confirm {self.title} Selection",
            f"Is this the correct area for {self.title}?\nCoordinates: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})\nSize: {width}x{height} pixels"
        )
        
        if confirm:
            self.is_configured = True
            self.logger.info(f"{self.title} selection confirmed: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
            self.selection_window.destroy()
        else:
            self.logger.info(f"{self.title} selection canceled, retrying")
            self.canvas.delete(self.selection_rect)
            self.canvas.delete("selection_info")
            self.preview_image = None
            
    def get_current_screenshot_region(self):
        """
        Capture a new screenshot of the selected region
        
        Returns:
            PIL.Image of the region
        """
        if not self.is_configured:
            self.logger.warning("Cannot capture region: not configured yet")
            return None
            
        try:
            # Validate coordinates before capture
            if any(coord < 0 for coord in [self.x1, self.y1, self.x2, self.y2]):
                self.logger.error(f"Invalid negative coordinates: ({self.x1},{self.y1}) to ({self.x2},{self.y2})")
                return None
                
            if self.x2 <= self.x1 or self.y2 <= self.y1:
                self.logger.error(f"Invalid coordinate order: ({self.x1},{self.y1}) to ({self.x2},{self.y2})")
                return None
            
            screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
            
            # Validate screenshot
            if screenshot.size[0] == 0 or screenshot.size[1] == 0:
                self.logger.error(f"Screenshot has zero dimensions: {screenshot.size}")
                return None
                
            return screenshot
        except Exception as e:
            self.logger.error(f"Error capturing region: {e}", exc_info=True)
            return None


class BarDetector:
    """Class for detecting and analyzing bars in Priston Tale"""
    
    def __init__(self, title, color_range):
        """
        Initialize a bar detector
        
        Args:
            title: The name of the bar (Health, Mana, Stamina)
            color_range: The HSV color range for detection
        """
        self.title = title
        self.color_range = color_range
        self.logger = logging.getLogger('PristonBot')
        
    def detect_percentage(self, image):
        """
        Detect the percentage of a bar that is filled
        
        Args:
            image: PIL.Image of the bar
            
        Returns:
            Percentage filled (0-100)
        """
        try:
            if image is None:
                self.logger.warning(f"Cannot detect {self.title} percentage: image is None")
                return 100
                
            # Convert PIL image to numpy array
            np_image = np.array(image)
            
            if np_image.size == 0:
                self.logger.warning(f"Cannot detect {self.title} percentage: image is empty")
                return 100
            
            # Convert to HSV for better color detection
            hsv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
            
            # Create mask based on bar color
            if self.title == "Health":  # Red
                # Red can wrap around in HSV, so use two ranges
                lower1 = np.array([0, 50, 50])
                upper1 = np.array([10, 255, 255])
                mask1 = cv2.inRange(hsv_image, lower1, upper1)
                
                lower2 = np.array([160, 50, 50])
                upper2 = np.array([180, 255, 255])
                mask2 = cv2.inRange(hsv_image, lower2, upper2)
                
                mask = mask1 | mask2  # Combine both masks
                
            elif self.title == "Mana":  # Blue
                lower = np.array([100, 50, 50])
                upper = np.array([140, 255, 255])
                mask = cv2.inRange(hsv_image, lower, upper)
                
            else:  # Stamina (Green)
                lower = np.array([40, 50, 50])
                upper = np.array([80, 255, 255])
                mask = cv2.inRange(hsv_image, lower, upper)
            
            # Save the mask for debugging
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            mask_filename = f"{debug_dir}/{self.title.lower()}_mask_{time.strftime('%H%M%S')}.png"
            cv2.imwrite(mask_filename, mask)
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Count non-zero pixels to determine percentage
            total_pixels = mask.shape[0] * mask.shape[1]
            if total_pixels == 0:
                return 100
                
            filled_pixels = cv2.countNonZero(mask)
            percentage = (filled_pixels / total_pixels) * 100
            
            self.logger.debug(f"{self.title} bar percentage: {percentage:.1f}%")
            return max(0, min(100, percentage))  # Clamp to 0-100 range
            
        except Exception as e:
            self.logger.error(f"Error detecting {self.title} bar percentage: {e}", exc_info=True)
            return 100  # Default to 100% (full) to avoid unnecessary potion use


# Define color ranges for Priston Tale bars
# HSV color ranges [hue, saturation, value]
HEALTH_COLOR_RANGE = (
    np.array([0, 50, 50]),       # Lower bound for red
    np.array([10, 255, 255])     # Upper bound for red
)

MANA_COLOR_RANGE = (
    np.array([100, 50, 50]),     # Lower bound for blue
    np.array([140, 255, 255])    # Upper bound for blue
)

STAMINA_COLOR_RANGE = (
    np.array([40, 50, 50]),      # Lower bound for green
    np.array([80, 255, 255])     # Upper bound for green
)