"""
Improved Bar selector UI for the Priston Tale Potion Bot
------------------------------------------------------
This module handles the UI components for bar selection with better horizontal layout.
"""

import tkinter as tk
from tkinter import ttk
import logging
from PIL import ImageTk, Image, ImageGrab

# Import ScreenSelector differently to avoid circular imports
import app.bar_selector
ScreenSelector = app.bar_selector.ScreenSelector

logger = logging.getLogger('PristonBot')

class BarSelectorUI:
    """Class that handles the UI for bar selection with improved layout"""
    
    def __init__(self, parent, root, log_callback):
        """
        Initialize the bar selector UI
        
        Args:
            parent: Parent frame to place UI elements
            root: Tkinter root window
            log_callback: Function to call for logging
        """
        self.parent = parent
        self.root = root
        self.log_callback = log_callback
        self.logger = logging.getLogger('PristonBot')
        
        # Create bar selectors
        self.hp_bar_selector = ScreenSelector(root)
        self.mp_bar_selector = ScreenSelector(root)
        self.sp_bar_selector = ScreenSelector(root)
        self.game_window = ScreenSelector(root)
        
        # Create the UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the UI components with horizontal layout"""
        # Health bar
        hp_frame = ttk.LabelFrame(self.parent, text="Health Bar")
        hp_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Preview
        self.hp_preview_label = ttk.Label(hp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.hp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Select button
        ttk.Button(hp_frame, text="Select Health Bar", 
                  command=lambda: self.start_bar_selection("Health", "red")).pack(
                      fill=tk.X, padx=5, pady=5)
        
        # Mana bar
        mp_frame = ttk.LabelFrame(self.parent, text="Mana Bar")
        mp_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        # Preview
        self.mp_preview_label = ttk.Label(mp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.mp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Select button
        ttk.Button(mp_frame, text="Select Mana Bar", 
                  command=lambda: self.start_bar_selection("Mana", "blue")).pack(
                      fill=tk.X, padx=5, pady=5)
        
        # Stamina bar
        sp_frame = ttk.LabelFrame(self.parent, text="Stamina Bar")
        sp_frame.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
        
        # Preview
        self.sp_preview_label = ttk.Label(sp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.sp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Select button
        ttk.Button(sp_frame, text="Select Stamina Bar", 
                  command=lambda: self.start_bar_selection("Stamina", "green")).pack(
                      fill=tk.X, padx=5, pady=5)
        
        # Setup status display
        status_frame = ttk.Frame(self.parent)
        status_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)
        
        # Status indicators
        self.status_var = tk.StringVar(value="Bars Configured: 0/3")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Configure grid weights
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
    
    def start_window_selection(self):
        """Start the game window selection process"""
        self.game_window = ScreenSelector(self.root)  # Recreate for fresh selection
        self.game_window.start_selection(title="Game Window", color="yellow")
        # Schedule an update to check if the selection was completed
        self.root.after(1000, self.update_window_preview)
    
    def update_window_preview(self):
        """Update the preview of the game window"""
        if self.game_window.is_setup():
            if hasattr(self.game_window, 'preview_image') and self.game_window.preview_image is not None:
                try:
                    # Resize the image to fit in the label
                    preview_size = (200, 150)  # Width, height
                    resized_img = self.game_window.preview_image.resize(preview_size, Image.LANCZOS)
                    preview_photo = ImageTk.PhotoImage(resized_img)
                    
                    # Update the window preview in main app
                    try:
                        from app.gui import main_app
                        if hasattr(main_app, 'window_preview_label'):
                            main_app.window_preview_label.config(image=preview_photo, text="")
                            main_app.window_preview_label.image = preview_photo  # Keep a reference
                    except (ImportError, AttributeError):
                        # If can't update main app directly, try direct reference
                        try:
                            if hasattr(self.root, 'window_preview_label'):
                                self.root.window_preview_label.config(image=preview_photo, text="")
                                self.root.window_preview_label.image = preview_photo
                        except:
                            pass
                    
                    self.log_callback(f"Game window selected: ({self.game_window.x1},{self.game_window.y1}) to ({self.game_window.x2},{self.game_window.y2})")
                except Exception as e:
                    logger.error(f"Error displaying window preview: {e}")
            else:
                # Try again later
                self.root.after(500, self.update_window_preview)
        else:
            # Check again later
            self.root.after(1000, self.update_window_preview)
    
    def start_bar_selection(self, bar_type, color):
        """Start the selection process for a specific bar"""
        if bar_type == "Health":
            # Re-initialize the bar selector to ensure fresh selection
            self.hp_bar_selector = ScreenSelector(self.root)
            self.hp_bar_selector.start_selection(title=f"{bar_type} Bar", color=color)
            # Schedule an update to check if the selection was completed
            self.root.after(1000, lambda: self.update_preview_image(self.hp_bar_selector, self.hp_preview_label))
        elif bar_type == "Mana":
            # Re-initialize the bar selector to ensure fresh selection
            self.mp_bar_selector = ScreenSelector(self.root)
            self.mp_bar_selector.start_selection(title=f"{bar_type} Bar", color=color)
            # Schedule an update to check if the selection was completed
            self.root.after(1000, lambda: self.update_preview_image(self.mp_bar_selector, self.mp_preview_label))
        elif bar_type == "Stamina":
            # Re-initialize the bar selector to ensure fresh selection
            self.sp_bar_selector = ScreenSelector(self.root)
            self.sp_bar_selector.start_selection(title=f"{bar_type} Bar", color=color)
            # Schedule an update to check if the selection was completed
            self.root.after(1000, lambda: self.update_preview_image(self.sp_bar_selector, self.sp_preview_label))
        
        # After any selection starts, schedule status update
        self.root.after(1500, self.update_status)
    
    def update_preview_image(self, selector, label):
        """Update the preview image for a bar"""
        if selector.is_setup():
            if hasattr(selector, 'preview_image') and selector.preview_image is not None:
                try:
                    # Check if we have a rotated preview for vertical bars
                    preview_img = selector.preview_image_rotated if hasattr(selector, 'preview_image_rotated') and selector.preview_image_rotated is not None else selector.preview_image
                    
                    # Resize the image to fit in the label
                    preview_size = (100, 60)  # Width, height
                    resized_img = preview_img.resize(preview_size, Image.LANCZOS)
                    preview_photo = ImageTk.PhotoImage(resized_img)
                    label.config(image=preview_photo, text="")
                    label.image = preview_photo  # Keep a reference
                    
                    # Log the selection
                    self.log_callback(f"{selector.title} selected: ({selector.x1},{selector.y1}) to ({selector.x2},{selector.y2})")
                    
                    # Update status display
                    self.update_status()
                    
                except Exception as e:
                    # If resize fails, show coords
                    logger.error(f"Error displaying preview image: {e}")
                    label.config(text=f"Selected: ({selector.x1},{selector.y1}) to ({selector.x2},{selector.y2})")
            else:
                # If no preview image yet, show coords
                label.config(text=f"Selected: ({selector.x1},{selector.y1}) to ({selector.x2},{selector.y2})")
        else:
            label.config(text="Not Selected")
            
            # Check again later
            self.root.after(1000, lambda: self.update_preview_image(selector, label))
    
    def update_status(self):
        """Update the status display with bar configuration count"""
        count = self.get_configured_count()
        self.status_var.set(f"Bars Configured: {count}/3")
    
    def is_bars_configured(self):
        """Check if all bars are configured"""
        return (self.hp_bar_selector.is_setup() and 
                self.mp_bar_selector.is_setup() and 
                self.sp_bar_selector.is_setup())
                
    def get_configured_count(self):
        """Get the number of configured bars"""
        return sum([
            self.hp_bar_selector.is_setup(),
            self.mp_bar_selector.is_setup(),
            self.sp_bar_selector.is_setup()
        ])