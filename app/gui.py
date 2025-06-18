"""
Main GUI for the Priston Tale Potion Bot with improved layout
---------------------------------------------------------
This module contains the main GUI class with practical horizontal layout
that maintains all functionality in a single window.
"""

import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging
from app.ui.components import ScrollableFrame

# Import our improved UI components
from app.ui.bar_selector_ui import BarSelectorUI
from app.ui.bot_controller_ui import SettingsUI
from app.ui.bot_controller import BotControllerUI
from app.ui.config_manager_ui import ConfigManagerUI

logger = logging.getLogger('PristonBot')

# Global reference to the main application instance
main_app = None

class PristonTaleBot:
    """Improved application class for the Priston Tale"""
    
    def __init__(self, root):
        """
        Initialize the application with improved UI
        
        Args:
            root: tkinter root window
        """
        global main_app
        main_app = self
        
        logger.info("Initializing Priston Tale")
        self.root = root
        self.root.geometry("900x700")  # Wider initial size for better horizontal layout
        self.root.minsize(800, 600)    # Minimum size
        
       # NEW CODE
        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create title with version
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        # ... title code stays the same

        # Create scrollable container
        scrollable_container = ScrollableFrame(main_container)
        scrollable_container.pack(fill=tk.BOTH, expand=True)

        # Content goes inside the scrollable frame
        content_frame = scrollable_container.scrollable_frame

        # Create two-column layout
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Left column - Bar selection
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right column - Settings and controls
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create game window selection frame in left column
        window_frame = ttk.LabelFrame(left_column, text="Game Window", padding=5)
        window_frame.pack(fill=tk.X, pady=(0, 5))
        
        window_content = ttk.Frame(window_frame)
        window_content.pack(fill=tk.X, pady=5)
        
        # Window preview
        preview_frame = ttk.Frame(window_content)
        preview_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.window_preview_label = tk.Label(preview_frame, text="Not Selected", 
                                            borderwidth=1, relief="solid",
                                            width=25, height=8)
        self.window_preview_label.pack(padx=5, pady=5)
        
        # Window selection button
        button_frame = ttk.Frame(window_content)
        button_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Button(button_frame, text="Select Game Window", 
                  command=self.start_window_selection).pack(fill=tk.X, pady=5)
        
        # Create bar selection frame in left column
        bars_frame = ttk.LabelFrame(left_column, text="Bar Selection", padding=5)
        bars_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create log frame at the bottom of left column
        log_frame = ttk.LabelFrame(left_column, text="Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Log text area
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_container, height=10, width=40, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create settings frame in right column
        settings_frame = ttk.LabelFrame(right_column, text="Settings", padding=5)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create bot control frame in right column
        control_frame = ttk.LabelFrame(right_column, text="Bot Control", padding=5)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Initialize components
        # Bar selector UI (in bars_frame)
        self.bar_selector_ui = BarSelectorUI(bars_frame, root, self.log)
        
        # Settings UI (in settings_frame)
        self.settings_ui = SettingsUI(settings_frame, self.save_config)
        
        # Config manager
        self.config_manager = ConfigManagerUI(
            self.bar_selector_ui,
            self.settings_ui,
            self.log
        )
        
        # Bot controller (in control_frame)
        self.bot_controller = BotControllerUI(
            control_frame, 
            root,
            self.bar_selector_ui.hp_bar_selector,
            self.bar_selector_ui.mp_bar_selector,
            self.bar_selector_ui.sp_bar_selector,
            self.settings_ui,
            self.log
        )
        
        # Initial log entry
        self.log("Bot GUI initialized successfully")
        
        # Try to load saved configuration
        if self.config_manager.load_bar_config():
            self.log("Loaded saved configuration")
        else:
            self.log("No saved configuration found or loading failed")
            self.log("Please select the Health, Mana, and Stamina bars to continue")
        
        # Check if bars are configured periodically
        self.check_bar_config()
        
        # Set up window close handler to save configuration
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Bot GUI initialized")
    
    def log(self, message):
        """Add a message to the log display"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        # Also log to the logger
        logger.info(message)
    
    def start_window_selection(self):
        """Start the game window selection process"""
        self.bar_selector_ui.start_window_selection()
    
    def check_bar_config(self):
        """Check if all bars are configured and enable the start button if they are"""
        # Count configured bars
        configured = self.bar_selector_ui.get_configured_count()
        
        if configured > 0:
            self.bot_controller.set_status(f"{configured}/3 bars configured")
            
        # Enable start button if all bars are configured
        if configured == 3:
            self.bot_controller.enable_start_button()
            self.bot_controller.set_status("Ready to start")
            self.log("All bars configured! You can now start the bot.")
            logger.info("All bars configured, start button enabled")
        else:
            self.bot_controller.disable_start_button()
            
        # Check again later if not all configured yet
        if configured < 3:
            self.root.after(1000, self.check_bar_config)
    
    def save_config(self):
        """Save the configuration"""
        if self.config_manager.save_bar_config():
            self.log("Configuration saved successfully")
    
    def on_closing(self):
        """Handle window closing event"""
        try:
            # Stop the bot if running
            if self.bot_controller.running:
                self.bot_controller.stop_bot()
                
            # Save configuration before exiting
            self.save_config()
            logger.info("Configuration saved on exit")
            
            # Destroy the window
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error on closing: {e}", exc_info=True)
            self.root.destroy()