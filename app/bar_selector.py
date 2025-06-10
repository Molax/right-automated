"""
Simplified Screen and Bar Selector for Priston Tale Potion Bot
--------------------------------------------------
This module uses a direct full-screen selection approach to avoid window misalignment issues.
"""

import os
import tkinter as tk
from tkinter import messagebox
import logging
from PIL import ImageGrab, ImageTk, Image
import numpy as np
import cv2
import time

class ScreenSelector:
    """Class for selecting areas on the screen without relying on window detection"""
    
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
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.is_configured = True
        self.logger.info(f"{self.title if hasattr(self, 'title') else 'Selection'} configured from saved coordinates: ({x1},{y1}) to ({x2},{y2})")
        return True
        
    def start_selection(self, title="Select Area", color="yellow"):
        """Start the screen selection process"""
        self.logger.info(f"Starting selection: {title}")
        self.title = title
        self.color = color
        
        # Create selection window that covers the entire screen
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title(title)
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-alpha', 0.8)  # Semi-transparent
        self.selection_window.configure(bg='black')
        
        # Take a screenshot of the entire screen
        self.logger.debug("Taking screenshot for selection")
        screenshot = ImageGrab.grab()
        self.screenshot_tk = ImageTk.PhotoImage(screenshot)
        self.full_screenshot = screenshot  # Save the full screenshot for later use
        
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
        self.canvas.create_text(
            self.selection_window.winfo_screenwidth() // 2,
            50,
            text=instruction_text,
            fill="white",
            font=("Arial", 18),
        )
        
        # Bind escape key to cancel
        self.selection_window.bind("<Escape>", self._on_escape)
        
    def _on_escape(self, event):
        """Handle escape key press"""
        self.logger.info(f"Selection canceled by user (ESC key)")
        self.selection_window.destroy()
        
    def on_press(self, event):
        """Handle mouse button press"""
        self.is_selecting = True
        self.x1 = event.x
        self.y1 = event.y
        self.logger.debug(f"Started selection at ({self.x1}, {self.y1})")
        
        # Create the selection rectangle
        self.selection_rect = self.canvas.create_rectangle(
            self.x1, self.y1, self.x1, self.y1, 
            outline=self.color, width=2
        )
        
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.is_selecting:
            self.x2 = event.x
            self.y2 = event.y
            self.canvas.coords(self.selection_rect, self.x1, self.y1, self.x2, self.y2)
            
    def on_release(self, event):
        """Handle mouse button release"""
        if not self.is_selecting:
            return
            
        self.is_selecting = False
        self.x2 = event.x
        self.y2 = event.y
        self.logger.debug(f"Completed selection to ({self.x2}, {self.y2})")
        
        # Ensure coordinates are ordered correctly (top-left to bottom-right)
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
            
        # Display selected area details
        self.canvas.create_text(
            (self.x1 + self.x2) // 2,
            self.y2 + 20,
            text=f"Selected: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})",
            fill="white",
            font=("Arial", 12),
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
        
        # Capture preview image of selected area
        try:
            # Use the saved full screenshot to create the preview
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
                # Rotate preview for display in UI
                self.preview_image_rotated = preview.rotate(90, expand=True)
                self.preview_image_rotated.save(f"{debug_dir}/{self.title.replace(' ', '_').lower()}_preview_rotated.png")
            else:
                self.preview_image_rotated = None
                
        except Exception as e:
            self.logger.error(f"Error creating preview image: {e}", exc_info=True)
        
        # Ask for confirmation
        confirm = messagebox.askyesno(
            f"Confirm {self.title} Selection",
            f"Is this the correct area for {self.title}?\nCoordinates: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})"
        )
        
        if confirm:
            self.is_configured = True
            self.logger.info(f"{self.title} selection confirmed: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
            self.selection_window.destroy()
        else:
            self.logger.info(f"{self.title} selection canceled, retrying")
            self.canvas.delete(self.selection_rect)
            self.preview_image = None
            
    def is_setup(self):
        """Check if the selection is configured"""
        return self.is_configured
        
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
            screenshot = ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
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
            # Convert PIL image to numpy array
            np_image = np.array(image)
            
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
                return 0
                
            filled_pixels = cv2.countNonZero(mask)
            percentage = (filled_pixels / total_pixels) * 100
            
            self.logger.debug(f"{self.title} bar percentage: {percentage:.1f}%")
            return percentage
            
        except Exception as e:
            self.logger.error(f"Error detecting {self.title} bar percentage: {e}", exc_info=True)
            return 100  # Default to 100% (full) to avoid unnecessary potion use
        



# Define color ranges for Priston Tale Potion Botbars
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