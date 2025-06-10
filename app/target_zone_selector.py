"""
Monster Target Zone Selector for Priston Tale Potion Bot
------------------------------------------------------
This module implements a target zone selector that allows the user
to define an area where monsters typically appear for better spell targeting.
"""

import tkinter as tk
import logging
from PIL import ImageGrab, ImageTk, Image
import os
import random
import numpy as np
import math
from tkinter import messagebox

class TargetZoneSelector:
    """Class for selecting the monster target zone"""
    
    def __init__(self, root):
        """
        Initialize the target zone selector
        
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
        self.title = "Monster Target Zone"
        self.color = "green"
        
        # Store a list of specific target points within the zone
        self.target_points = []
        self.num_target_points = 8  # Number of target points to generate
        
        # Reference to game window (will be populated during selection)
        self.game_window_rect = None
        
    def is_setup(self):
        """Check if the target zone is configured"""
        return self.is_configured
    
    def configure_from_saved(self, x1, y1, x2, y2, target_points=None):
        """Configure target zone from saved coordinates without UI interaction
        
        Args:
            x1, y1: Top-left coordinates
            x2, y2: Bottom-right coordinates
            target_points: Optional list of specific target points
            
        Returns:
            True if successful
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.is_configured = True
        
        # If target points were provided and they're valid, use them
        if target_points and isinstance(target_points, list) and len(target_points) > 0:
            # Verify each point is a valid tuple
            valid_points = []
            for point in target_points:
                if isinstance(point, tuple) and len(point) == 2:
                    valid_points.append(point)
                elif isinstance(point, list) and len(point) == 2:
                    # Convert lists to tuples for consistency
                    valid_points.append((point[0], point[1]))
                    
            if valid_points:
                self.target_points = valid_points
                self.logger.info(f"Loaded {len(valid_points)} target points from saved configuration")
                
                # Log the actual points for debugging
                for i, point in enumerate(self.target_points):
                    self.logger.debug(f"Target point {i}: ({point[0]}, {point[1]})")
        
        # If no valid points were provided or loaded, generate new ones
        if not self.target_points or len(self.target_points) == 0:
            self.generate_target_points()
            self.logger.info(f"Generated {len(self.target_points)} new target points")
            
        return True
    
    def _find_game_window(self):
        """Find the game window configuration to ensure proper coordinate alignment"""
        try:
            # First try to get the game window from the root object
            for attr_name in dir(self.root):
                attr = getattr(self.root, attr_name)
                if hasattr(attr, 'game_window') and hasattr(attr.game_window, 'is_setup') and attr.game_window.is_setup():
                    game_window = attr.game_window
                    return (game_window.x1, game_window.y1, game_window.x2, game_window.y2)
                
                # Try looking for bar_selector_ui
                if hasattr(attr, 'bar_selector_ui') and hasattr(attr.bar_selector_ui, 'game_window'):
                    game_window = attr.bar_selector_ui.game_window
                    if hasattr(game_window, 'is_setup') and game_window.is_setup():
                        return (game_window.x1, game_window.y1, game_window.x2, game_window.y2)
            
            # If we didn't find it through direct attributes, look within modules
            from app.config import load_config
            config = load_config()
            game_window_config = config.get("bars", {}).get("game_window", {})
            if game_window_config.get("configured", False):
                return (
                    game_window_config.get("x1"),
                    game_window_config.get("y1"),
                    game_window_config.get("x2"),
                    game_window_config.get("y2")
                )
                
            # If still not found, return None to indicate we couldn't find it
            return None
        except Exception as e:
            self.logger.error(f"Error finding game window: {e}")
            return None
        
    def start_selection(self):
        """Start the target zone selection process"""
        self.logger.info(f"Starting selection: {self.title}")
        
        # Try to find the game window first to ensure coordinate alignment
        self.game_window_rect = self._find_game_window()
        if self.game_window_rect:
            self.logger.info(f"Found game window at: {self.game_window_rect}")
        else:
            # Warn the user that targeting might not be accurate
            messagebox.showwarning(
                "Game Window Not Found",
                "The game window configuration could not be found. Target coordinates may not align properly. "
                "Please make sure you've configured the game window first.",
                parent=self.root
            )
            self.logger.warning("Game window not found, targeting may be inaccurate")
        
        # Create selection window that covers the entire screen
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title(self.title)
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
        
        # If we have a game window, highlight it
        if self.game_window_rect:
            x1, y1, x2, y2 = self.game_window_rect
            # Draw a rectangle around the game window
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="yellow",
                width=3,
                dash=(5, 5)  # Dashed line
            )
            # Add text label
            self.canvas.create_text(
                x1 + (x2 - x1) // 2,
                y1 - 10,
                text="Game Window",
                fill="yellow",
                font=("Arial", 12, "bold")
            )
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Add instructions
        instruction_text = f"Click and drag to select the Monster Target Zone. Press ESC to cancel."
        self.canvas.create_text(
            self.selection_window.winfo_screenwidth() // 2,
            50,
            text=instruction_text,
            fill="white",
            font=("Arial", 18),
        )
        
        # Add additional instruction if game window is found
        if self.game_window_rect:
            additional_text = "Make your selection within the yellow-outlined game window"
            self.canvas.create_text(
                self.selection_window.winfo_screenwidth() // 2,
                90,
                text=additional_text,
                fill="yellow",
                font=("Arial", 14)
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
        
        # Check if selection is within game window bounds (if we have a game window)
        if self.game_window_rect:
            gx1, gy1, gx2, gy2 = self.game_window_rect
            
            # If selection is completely outside the game window, warn the user
            if (self.x2 < gx1 or self.x1 > gx2 or self.y2 < gy1 or self.y1 > gy2):
                warning_result = messagebox.askquestion(
                    "Warning: Selection Outside Game Window",
                    "Your selection is outside the game window. Targeting may not work correctly.\n\n"
                    "Do you want to proceed with this selection anyway?",
                    icon='warning'
                )
                
                if warning_result != 'yes':
                    # Reset selection and let them try again
                    self.canvas.delete(self.selection_rect)
                    self.is_selecting = False
                    return
            
            # If selection is partially outside, adjust it to fit within game window
            elif (self.x1 < gx1 or self.x2 > gx2 or self.y1 < gy1 or self.y2 > gy2):
                adjust_result = messagebox.askquestion(
                    "Adjust Selection",
                    "Your selection extends beyond the game window bounds. "
                    "Would you like to adjust it to fit within the game window?",
                    icon='question'
                )
                
                if adjust_result == 'yes':
                    # Adjust selection to fit within game window
                    old_x1, old_y1, old_x2, old_y2 = self.x1, self.y1, self.x2, self.y2
                    self.x1 = max(self.x1, gx1)
                    self.y1 = max(self.y1, gy1)
                    self.x2 = min(self.x2, gx2)
                    self.y2 = min(self.y2, gy2)
                    
                    # Update rectangle on canvas
                    self.canvas.coords(self.selection_rect, self.x1, self.y1, self.x2, self.y2)
                    
                    self.logger.info(f"Adjusted selection from ({old_x1},{old_y1})-({old_x2},{old_y2}) to ({self.x1},{self.y1})-({self.x2},{self.y2})")
            
        # Display selected area details
        self.canvas.create_text(
            (self.x1 + self.x2) // 2,
            self.y2 + 20,
            text=f"Selected: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})",
            fill="white",
            font=("Arial", 12),
        )
        
        # Generate target points within the selected area
        self.generate_target_points()
        
        # Draw the target points
        self._draw_target_points()
        
        # Ask for confirmation
        confirmation = messagebox.askyesno(
            f"Confirm {self.title} Selection",
            f"Is this the correct area for monster targeting?\nCoordinates: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})\n\n{len(self.target_points)} target points generated."
        )
        
        if confirmation:
            self.is_configured = True
            self.logger.info(f"{self.title} selection confirmed: ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})")
            
            # Capture preview image of selected area
            try:
                preview = self.full_screenshot.crop((self.x1, self.y1, self.x2, self.y2))
                self.preview_image = preview
                
                # Save the preview image for debugging
                debug_dir = "debug_images"
                if not os.path.exists(debug_dir):
                    os.makedirs(debug_dir)
                    
                # Save the preview with target points
                preview_with_points = preview.copy()
                from PIL import ImageDraw
                draw = ImageDraw.Draw(preview_with_points)
                
                # Draw the target points in the preview
                for point in self.target_points:
                    # Convert to relative coordinates in the preview
                    rel_x = point[0] - self.x1
                    rel_y = point[1] - self.y1
                    draw.ellipse((rel_x-5, rel_y-5, rel_x+5, rel_y+5), outline=(0, 255, 0), width=2)
                    
                preview_with_points.save(f"{debug_dir}/target_zone_preview.png")
                
            except Exception as e:
                self.logger.error(f"Error creating preview image: {e}")
                
            self.selection_window.destroy()
        else:
            self.logger.info(f"{self.title} selection canceled, retrying")
            self.canvas.delete(self.selection_rect)
            self.target_points = []
            
            # Clear target point markers
            for item in self.canvas.find_all():
                if self.canvas.type(item) == "oval":
                    self.canvas.delete(item)
    
    def _draw_target_points(self):
        """Draw the target points on the canvas"""
        # Clear any existing target point markers
        for item in self.canvas.find_all():
            if self.canvas.type(item) == "oval":
                self.canvas.delete(item)
                
        # Draw each target point
        for x, y in self.target_points:
            # Draw a circle for each target point
            self.canvas.create_oval(
                x-5, y-5, x+5, y+5,
                outline=self.color,
                fill=self.color,
                width=2
            )
            
    def generate_target_points(self):
        """Generate target points within the selected area
        
        These points will be used for monster targeting, focusing on areas
        where monsters are likely to appear (forming a semi-circle around
        the character).
        """
        if not all([self.x1, self.y1, self.x2, self.y2]):
            self.logger.warning("Cannot generate target points: coordinates not set")
            return
            
        # Clear existing target points
        self.target_points = []
        
        # Calculate the width and height of the target zone
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        
        # Calculate the center of the target zone (character position)
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        
        # Determine radius based on the smaller dimension, with some margin
        radius = min(width, height) * 0.4
        
        # Method 1: Create points in a circular pattern around the character
        for i in range(self.num_target_points):
            # Calculate angle, focusing more on the lower half
            # Angles range from -135 to 135 degrees (focusing on lower half)
            angle = math.radians(random.uniform(-135, 135))
            
            # Add some randomness to the radius
            rand_radius = radius * random.uniform(0.7, 1.0)
            
            # Calculate point coordinates
            x = center_x + int(rand_radius * math.cos(angle))
            y = center_y + int(rand_radius * math.sin(angle))
            
            # Ensure the point is within the selection bounds
            x = max(self.x1, min(x, self.x2))
            y = max(self.y1, min(y, self.y2))
            
            # Add the exact coordinates of the point to the target points list
            self.target_points.append((x, y))
        
        self.logger.info(f"Generated {len(self.target_points)} target points")
        
        # Additional logging to help with debugging
        for i, point in enumerate(self.target_points):
            self.logger.debug(f"Target point {i}: ({point[0]}, {point[1]})")
    
    def get_random_target(self):
        """Get a random target point within the selection
        
        Returns:
            Tuple of (x, y) coordinates for targeting
        """
        # If we have target points, choose one randomly
        if self.target_points and len(self.target_points) > 0:
            chosen_point = random.choice(self.target_points)
            self.logger.debug(f"Selected target point: {chosen_point}")
            return chosen_point
        
        # Fallback: If no target points available, generate a random point
        if not all([self.x1, self.y1, self.x2, self.y2]):
            self.logger.warning("Cannot get random target: target zone not configured")
            return None
            
        # Random coordinates within the selection
        x = random.randint(self.x1, self.x2)
        y = random.randint(self.y1, self.y2)
        
        self.logger.debug(f"Generated fallback point: ({x}, {y})")
        return (x, y)
        
    def get_serializable_points(self):
        """Get target points in a format that can be serialized to JSON
        
        Returns:
            List of [x, y] pairs
        """
        serializable_points = []
        for point in self.target_points:
            serializable_points.append([point[0], point[1]])
        return serializable_points