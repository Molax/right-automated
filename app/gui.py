"""
Fixed Main GUI for the Priston Tale Potion Bot
---------------------------------------------
This module contains the main GUI class with proper layout handling
and DPI awareness for modern displays.
"""

import os
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging

logger = logging.getLogger('PristonBot')

# Global reference to the main application instance
main_app = None

class PristonTaleBot:
    """Fixed application class for the Priston Tale Bot"""
    
    def __init__(self, root):
        """
        Initialize the application with proper DPI handling
        
        Args:
            root: tkinter root window
        """
        global main_app
        main_app = self
        
        logger.info("Initializing Priston Tale Bot with DPI fixes")
        self.root = root
        
        # Set DPI awareness for Windows
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per monitor DPI aware
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()  # System DPI aware
            except:
                pass  # If DPI functions fail, continue anyway
        
        # Configure root window
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)
        self.root.title("Priston Tale Potion Bot")
        
        # Configure grid weights for proper resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container with padding
        main_container = ttk.Frame(root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        
        # Create title frame
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="Priston Tale Potion Bot", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(
            title_frame, 
            text="v1.0.0", 
            font=("Arial", 10), 
            foreground="#666666"
        )
        version_label.pack(side=tk.RIGHT)
        
        # Create left column - Configuration
        left_column = ttk.Frame(main_container)
        left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        left_column.grid_rowconfigure(1, weight=1)
        left_column.grid_rowconfigure(2, weight=1)
        left_column.grid_columnconfigure(0, weight=1)
        
        # Create right column - Settings and Control
        right_column = ttk.Frame(main_container)
        right_column.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        right_column.grid_rowconfigure(0, weight=1)
        right_column.grid_columnconfigure(0, weight=1)
        
        # Game window frame in left column
        self._create_game_window_frame(left_column)
        
        # Bar selection frame in left column
        self._create_bar_selection_frame(left_column)
        
        # Log frame in left column
        self._create_log_frame(left_column)
        
        # Settings and control frame in right column
        self._create_settings_and_control_frame(right_column)
        
        # Initialize components
        self._initialize_components()
        
        # Initial log entry
        self.log("Bot GUI initialized successfully")
        
        # Try to load saved configuration
        if self.config_manager.load_bar_config():
            self.log("Loaded saved configuration")
        else:
            self.log("No saved configuration found")
            self.log("Please configure the game window and all bars to continue")
        
        # Check if bars are configured periodically
        self.check_bar_config()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Bot GUI initialized successfully")
    
    def _create_game_window_frame(self, parent):
        """Create the game window selection frame"""
        window_frame = ttk.LabelFrame(parent, text="Game Window Selection", padding="5")
        window_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        window_frame.grid_columnconfigure(1, weight=1)
        
        # Preview label
        self.window_preview_label = tk.Label(
            window_frame, 
            text="Not Selected", 
            borderwidth=1, 
            relief="solid",
            width=30, 
            height=6,
            bg="white"
        )
        self.window_preview_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        # Button frame
        button_frame = ttk.Frame(window_frame)
        button_frame.grid(row=0, column=1, sticky="ew", pady=5)
        button_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(
            button_frame, 
            text="Select Game Window", 
            command=self.start_window_selection
        ).grid(row=0, column=0, sticky="ew", pady=2)
        
        ttk.Label(
            button_frame, 
            text="Select the game window area first",
            font=("Arial", 9),
            foreground="#666666"
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))
    
    def _create_bar_selection_frame(self, parent):
        """Create the bar selection frame"""
        self.bars_frame = ttk.LabelFrame(parent, text="Bar Selection", padding="5")
        self.bars_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        
    def _create_log_frame(self, parent):
        """Create the log frame"""
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding="5")
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        # Create log text with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=12, 
            width=50, 
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
    
    def _create_settings_and_control_frame(self, parent):
        """Create the settings and control frame"""
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        # Settings tab
        self.settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.settings_frame, text="Settings")
        
        # Control tab
        self.control_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.control_frame, text="Bot Control")
        
        # Add some spacing and organization to control frame
        control_container = ttk.Frame(self.control_frame)
        control_container.pack(fill=tk.BOTH, expand=True)
        
        # Status frame
        status_frame = ttk.LabelFrame(control_container, text="Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Values frame
        values_frame = ttk.LabelFrame(control_container, text="Current Values", padding="5")
        values_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.LabelFrame(control_container, text="Controls", padding="5")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(control_container, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store references for the bot controller
        self.status_container = status_frame
        self.values_container = values_frame
        self.buttons_container = buttons_frame
        self.stats_container = stats_frame
    
    def _initialize_components(self):
        """Initialize all the UI components"""
        # Import UI components
        from app.ui.bar_selector_ui import BarSelectorUI
        from app.ui.bot_controller_ui import SettingsUI
        from app.ui.bot_controller import BotControllerUI
        from app.ui.config_manager_ui import ConfigManagerUI
        
        # Bar selector UI (in bars_frame)
        self.bar_selector_ui = BarSelectorUI(self.bars_frame, self.root, self.log)
        
        # Settings UI (in settings_frame)
        self.settings_ui = SettingsUI(self.settings_frame, self.save_config)
        
        # Config manager
        self.config_manager = ConfigManagerUI(
            self.bar_selector_ui,
            self.settings_ui,
            self.log
        )
        
        # Bot controller (in control containers)
        self.bot_controller = BotControllerUI(
            self.control_frame,
            self.root,
            self.bar_selector_ui.hp_bar_selector,
            self.bar_selector_ui.mp_bar_selector,
            self.bar_selector_ui.sp_bar_selector,
            getattr(self.bar_selector_ui, 'largato_skill_selector', None),
            self.settings_ui,
            self.log
        )
    
    def log(self, message):
        """Add a message to the log display"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        # Also log to the logger
        logger.info(message)
        
        # Limit log size to prevent memory issues
        lines = self.log_text.get(1.0, tk.END).count('\n')
        if lines > 1000:
            # Remove first 200 lines
            self.log_text.delete(1.0, "201.0")
    
    def start_window_selection(self):
        """Start the game window selection process"""
        try:
            self.bar_selector_ui.start_window_selection()
        except Exception as e:
            self.log(f"Error starting window selection: {e}")
            logger.error(f"Error starting window selection: {e}", exc_info=True)
    
    def check_bar_config(self):
        """Check if all bars are configured and enable the start button if they are"""
        try:
            # Count configured bars
            configured = 0
            
            if hasattr(self.bar_selector_ui, 'get_configured_count'):
                configured = self.bar_selector_ui.get_configured_count()
            else:
                # Fallback counting method
                if hasattr(self.bar_selector_ui, 'hp_bar_selector') and self.bar_selector_ui.hp_bar_selector.is_setup():
                    configured += 1
                if hasattr(self.bar_selector_ui, 'mp_bar_selector') and self.bar_selector_ui.mp_bar_selector.is_setup():
                    configured += 1
                if hasattr(self.bar_selector_ui, 'sp_bar_selector') and self.bar_selector_ui.sp_bar_selector.is_setup():
                    configured += 1
            
            # Check game window
            game_window_configured = False
            if hasattr(self.bar_selector_ui, 'game_window') and self.bar_selector_ui.game_window.is_setup():
                game_window_configured = True
            
            # Update status
            if game_window_configured and configured >= 3:
                if hasattr(self.bot_controller, 'enable_start_button'):
                    self.bot_controller.enable_start_button()
                if hasattr(self.bot_controller, 'set_status'):
                    if configured == 4:  # Including Largato skill bar
                        self.bot_controller.set_status("Ready to start (All features available)")
                        self.log("All bars configured! Regular bot and Largato Hunt are available.")
                    else:
                        self.bot_controller.set_status("Ready to start (Basic features)")
                        self.log("Core bars configured! Basic bot functionality is available.")
                logger.info("Bars configured, start button enabled")
            else:
                if hasattr(self.bot_controller, 'disable_start_button'):
                    self.bot_controller.disable_start_button()
                if hasattr(self.bot_controller, 'set_status'):
                    if not game_window_configured:
                        self.bot_controller.set_status("Please configure game window first")
                    else:
                        self.bot_controller.set_status(f"Configure remaining bars ({configured}/3)")
                
            # Check again later if not fully configured yet
            if not game_window_configured or configured < 3:
                self.root.after(2000, self.check_bar_config)
                
        except Exception as e:
            logger.error(f"Error checking bar configuration: {e}", exc_info=True)
            self.root.after(5000, self.check_bar_config)  # Retry after longer delay
    
    def save_config(self):
        """Save the configuration"""
        try:
            if hasattr(self, 'config_manager') and self.config_manager.save_bar_config():
                self.log("Configuration saved successfully")
            else:
                self.log("Failed to save configuration")
        except Exception as e:
            self.log(f"Error saving configuration: {e}")
            logger.error(f"Error saving configuration: {e}", exc_info=True)
    
    def on_closing(self):
        """Handle window closing event"""
        try:
            # Stop any running bots
            if hasattr(self, 'bot_controller'):
                if hasattr(self.bot_controller, 'running') and self.bot_controller.running:
                    self.bot_controller.stop_bot()
                if hasattr(self.bot_controller, 'largato_running') and self.bot_controller.largato_running:
                    self.bot_controller.stop_largato_hunt()
                    
            # Save configuration before exiting
            self.save_config()
            logger.info("Configuration saved on exit")
            
            # Destroy the window
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error on closing: {e}", exc_info=True)
            # Force close even if there's an error
            try:
                self.root.destroy()
            except:
                pass


def main():
    """Main function to start the application"""
    try:
        # Set up logging first
        from app.config import setup_logging
        setup_logging()
        
        # Create root window
        root = tk.Tk()
        
        # Set window icon if available
        try:
            icon_path = "resources/potion_icon.ico"
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception as e:
            logger.debug(f"Could not set application icon: {e}")
        
        # Create application
        app = PristonTaleBot(root)
        
        # Set minimum size based on content
        root.update_idletasks()
        root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
        
        # Start the main loop
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Fatal error during initialization: {e}", exc_info=True)
        
        # Show error message to user
        try:
            error_root = tk.Tk()
            error_root.withdraw()
            messagebox.showerror(
                "Fatal Error", 
                f"A fatal error occurred while starting the application:\n\n{e}\n\n"
                "Please check the logs for details."
            )
            error_root.destroy()
        except:
            # If GUI error dialog fails, print to console
            print(f"FATAL ERROR: {e}")


if __name__ == "__main__":
    main()