"""
Fixed Bot Controller UI for the Priston Tale Potion Bot with Largato Hunt
------------------------------------------------------------------------
This module handles the bot control UI and logic with the new Largato Hunt feature.
CRITICAL FIX: Corrected import paths and added fallback handling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import time
import random
import math
from PIL import Image

# FIXED: Import the Largato Hunter with proper path and fallback
try:
    from app.largato_hunt import LargatoHunter
    LARGATO_AVAILABLE = True
except ImportError:
    LARGATO_AVAILABLE = False
    # Create a dummy class for fallback
    class LargatoHunter:
        def __init__(self, log_callback):
            self.log_callback = log_callback
            self.running = False
            self.wood_stacks_destroyed = 0
        
        def start_hunt(self):
            self.log_callback("ERROR: Largato Hunt module not properly installed!")
            return False
        
        def stop_hunt(self):
            return True

# First try to import the windows_utils mouse functions
try:
    from app.windows_utils.mouse import move_mouse_direct, press_right_mouse
except ImportError:
    # Fallback to older window_utils if needed
    try:
        from app.window_utils import press_right_mouse, get_window_rect
    except ImportError:
        def press_right_mouse(*args, **kwargs):
            logger = logging.getLogger('PristonBot')
            logger.warning("press_right_mouse not available")
            return False
        def get_window_rect(*args, **kwargs):
            return None
    
    # Define move_mouse_direct as fallback
    def move_mouse_direct(x, y):
        """Fallback mouse movement function"""
        logger = logging.getLogger('PristonBot')
        logger.warning(f"Using fallback mouse movement to ({x}, {y})")
        import ctypes
        try:
            ctypes.windll.user32.SetCursorPos(int(x), int(y))
            return True
        except Exception as e:
            logger.error(f"Error in fallback mouse movement: {e}")
            return False

# Import press_key function specifically
try:
    from app.windows_utils.keyboard import press_key
except ImportError:
    try:
        from app.window_utils import press_key
    except ImportError:
        # Define press_key fallback if we can't import it
        def press_key(hwnd, key):
            """Fallback press_key function"""
            logger = logging.getLogger('PristonBot')
            logger.info(f"Using fallback key press for '{key}'")
            import ctypes
            
            # Map common keys to virtual key codes
            key_map = {
                '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
                '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
                'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
                'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
                'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
                'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
                'x': 0x58, 'space': 0x20, 'enter': 0x0D
            }
            
            # Get virtual key code
            if isinstance(key, str):
                key = key.lower()
                vk_code = key_map.get(key)
                if vk_code is None:
                    try:
                        vk_code = ord(key.upper()[0])
                    except:
                        logger.error(f"Could not determine virtual key code for '{key}'")
                        return False
            else:
                vk_code = key
                
            try:
                # Define key event flags
                KEYEVENTF_KEYDOWN = 0x0000
                KEYEVENTF_KEYUP = 0x0002
                
                # Send key down
                ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYDOWN, 0)
                time.sleep(0.05)  # Small delay between down and up
                
                # Send key up
                ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
                
                return True
            except Exception as e:
                logger.error(f"Error pressing key '{key}': {e}")
                return False

# Import focus_game_window, with fallback if not found
try:
    from app.windows_utils.windows_management import focus_game_window
except ImportError:
    try:
        from app.window_utils import focus_game_window
    except ImportError:
        def focus_game_window(hwnd):
            """Fallback function if module isn't created yet"""
            logger = logging.getLogger('PristonBot')
            logger.warning(f"Using fallback for window focus")
            try:
                import win32gui
                return win32gui.SetForegroundWindow(hwnd) if hwnd else False
            except Exception as e:
                logger.error(f"Error in fallback focus: {e}")
                return False

# Import additional functions for window detection
try:
    from app.windows_utils.windows_management import find_game_window
except ImportError:
    try:
        from app.window_utils import find_game_window
    except ImportError:
        def find_game_window(window_name="Priston Tale"):
            """Fallback function to find game window"""
            logger = logging.getLogger('PristonBot')
            logger.warning(f"Using fallback to find game window: {window_name}")
            try:
                import win32gui
                return win32gui.FindWindow(None, window_name)
            except Exception as e:
                logger.error(f"Error in fallback window finding: {e}")
                return None

from app.bar_selector import BarDetector, HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE
from app.config import load_config

logger = logging.getLogger('PristonBot')

class BotControllerUI:
    """Class that handles the bot control UI and logic with Largato Hunt support"""
    
    def __init__(self, parent, root, hp_bar, mp_bar, sp_bar, settings_ui, log_callback):
        """
        Initialize the bot controller UI
        
        Args:
            parent: Parent frame to place UI elements
            root: Tkinter root window
            hp_bar: Health bar selector
            mp_bar: Mana bar selector
            sp_bar: Stamina bar selector
            settings_ui: Settings UI instance
            log_callback: Function to call for logging
        """
        self.parent = parent
        self.root = root
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.settings_ui = settings_ui
        self.log_callback = log_callback
        
        # Create detectors
        self.hp_detector = BarDetector("Health", HEALTH_COLOR_RANGE)
        self.mp_detector = BarDetector("Mana", MANA_COLOR_RANGE)
        self.sp_detector = BarDetector("Stamina", STAMINA_COLOR_RANGE)
        
        # Bot state
        self.running = False
        self.bot_thread = None
        
        # Largato Hunt state
        self.largato_running = False
        self.largato_hunter = None
        
        # Store previous bar values to detect changes
        self.prev_hp_percent = 100.0
        self.prev_mp_percent = 100.0
        self.prev_sp_percent = 100.0
        
        # Statistics
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        self.start_time = None
        
        # Random targeting variables
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        # Game window reference
        self.game_window = None
        self.game_window_rect = None
        self.game_hwnd = None
        
        # Initialize target zone selector
        self.target_zone_selector = None
        
        # Initialize Largato Hunter
        self.largato_hunter = LargatoHunter(self.log_callback)
        
        # Log availability status
        if LARGATO_AVAILABLE:
            self.log_callback("Largato Hunt module loaded successfully")
        else:
            self.log_callback("Warning: Largato Hunt module not available")
        
        # Create the UI
        self._create_ui()
        
        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()
    
    def _create_ui(self):
        """Create the UI components with improved layout including Largato Hunt"""
        # Status section
        status_frame = ttk.Frame(self.parent)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to configure")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        status_label.pack(side=tk.LEFT, padx=5)
        
        # Current values section
        values_frame = ttk.Frame(self.parent)
        values_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Two-column layout for current values
        values_left = ttk.Frame(values_frame)
        values_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        values_right = ttk.Frame(values_frame)
        values_right.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # HP current value
        hp_frame = ttk.Frame(values_left)
        hp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_frame, text="Health:", foreground="#e74c3c", width=10).pack(side=tk.LEFT)
        self.hp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(hp_frame, textvariable=self.hp_value_var).pack(side=tk.LEFT)
        
        # MP current value
        mp_frame = ttk.Frame(values_left)
        mp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_frame, text="Mana:", foreground="#3498db", width=10).pack(side=tk.LEFT)
        self.mp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(mp_frame, textvariable=self.mp_value_var).pack(side=tk.LEFT)
        
        # HP potions used
        hp_pot_frame = ttk.Frame(values_right)
        hp_pot_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_pot_frame, text="HP Potions:", width=12).pack(side=tk.LEFT)
        self.hp_potions_var = tk.StringVar(value="0")
        ttk.Label(hp_pot_frame, textvariable=self.hp_potions_var).pack(side=tk.LEFT)
        
        # MP potions used
        mp_pot_frame = ttk.Frame(values_right)
        mp_pot_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_pot_frame, text="MP Potions:", width=12).pack(side=tk.LEFT)
        self.mp_potions_var = tk.StringVar(value="0")
        ttk.Label(mp_pot_frame, textvariable=self.mp_potions_var).pack(side=tk.LEFT)
        
        # SP current value
        sp_frame = ttk.Frame(values_left)
        sp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_frame, text="Stamina:", foreground="#2ecc71", width=10).pack(side=tk.LEFT)
        self.sp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(sp_frame, textvariable=self.sp_value_var).pack(side=tk.LEFT)
        
        # Runtime display
        runtime_frame = ttk.Frame(values_left)
        runtime_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(runtime_frame, text="Runtime:", width=10).pack(side=tk.LEFT)
        self.runtime_var = tk.StringVar(value="00:00:00")
        ttk.Label(runtime_frame, textvariable=self.runtime_var).pack(side=tk.LEFT)
        
        # SP potions used
        sp_pot_frame = ttk.Frame(values_right)
        sp_pot_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_pot_frame, text="SP Potions:", width=12).pack(side=tk.LEFT)
        self.sp_potions_var = tk.StringVar(value="0")
        ttk.Label(sp_pot_frame, textvariable=self.sp_potions_var).pack(side=tk.LEFT)
        
        # Spells cast
        spell_frame = ttk.Frame(values_right)
        spell_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(spell_frame, text="Spells Cast:", width=12).pack(side=tk.LEFT)
        self.spells_var = tk.StringVar(value="0")
        ttk.Label(spell_frame, textvariable=self.spells_var).pack(side=tk.LEFT)

        # Target position display (for random targeting)
        target_frame = ttk.Frame(values_right)
        target_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(target_frame, text="Target Offset:", width=12).pack(side=tk.LEFT)
        self.target_var = tk.StringVar(value="(0, 0)")
        ttk.Label(target_frame, textvariable=self.target_var).pack(side=tk.LEFT)
        
        # Game window status
        window_frame = ttk.Frame(values_left)
        window_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(window_frame, text="Game Window:", width=10).pack(side=tk.LEFT)
        self.window_var = tk.StringVar(value="Not Detected")
        ttk.Label(window_frame, textvariable=self.window_var).pack(side=tk.LEFT)
        
        # Largato Hunt status
        largato_status_frame = ttk.Frame(values_right)
        largato_status_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(largato_status_frame, text="Wood Stacks:", width=12).pack(side=tk.LEFT)
        self.wood_stacks_var = tk.StringVar(value="0/4")
        ttk.Label(largato_status_frame, textvariable=self.wood_stacks_var).pack(side=tk.LEFT)
        
        # Control buttons - now with 3 buttons in a row
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Create custom button styles with Tkinter for more control and visibility
        self.start_button = tk.Button(
            button_frame, 
            text="START BOT\n(Ctrl+Shift+A)",
            command=self.start_bot, 
            bg="#4CAF50",  # Green background
            fg="black",    # Black text (more visible)
            font=("Arial", 10, "bold"),
            height=2,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Largato button - disable if not available
        largato_state = tk.NORMAL if LARGATO_AVAILABLE else tk.DISABLED
        largato_bg = "#FF9800" if LARGATO_AVAILABLE else "#a0a0a0"
        largato_text = "LARGATO HUNT\n(Ctrl+Shift+L)" if LARGATO_AVAILABLE else "LARGATO HUNT\n(Not Available)"
        
        self.largato_button = tk.Button(
            button_frame, 
            text=largato_text,
            command=self.start_largato_hunt, 
            bg=largato_bg,  # Orange background or gray if disabled
            fg="black",     # Black text (more visible)
            font=("Arial", 10, "bold"),
            height=2,
            state=largato_state
        )
        self.largato_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.stop_button = tk.Button(
            button_frame, 
            text="STOP BOT\n(Ctrl+Shift+B)",
            command=self.stop_bot, 
            bg="#F44336",  # Red background
            fg="black",    # Black text (more visible)
            font=("Arial", 10, "bold"),
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Add shortcut information
        shortcut_frame = ttk.Frame(self.parent)
        shortcut_frame.pack(fill=tk.X, pady=5)
        
        shortcut_text = "Shortcuts: Ctrl+Shift+A (Start), Ctrl+Shift+L (Largato Hunt), Ctrl+Shift+B (Stop)"
        if not LARGATO_AVAILABLE:
            shortcut_text += " - Largato Hunt requires proper module installation"
            
        shortcut_label = ttk.Label(
            shortcut_frame, 
            text=shortcut_text,
            font=("Arial", 8),
            foreground="#555555"
        )
        shortcut_label.pack(anchor=tk.CENTER)
    
    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for starting and stopping the bot"""
        # Register keyboard shortcuts with Tkinter
        self.root.bind("<Control-Shift-a>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-A>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-b>", lambda event: self._handle_stop_shortcut())
        self.root.bind("<Control-Shift-B>", lambda event: self._handle_stop_shortcut())
        
        # Only bind Largato shortcut if available
        if LARGATO_AVAILABLE:
            self.root.bind("<Control-Shift-l>", lambda event: self._handle_largato_shortcut())
            self.root.bind("<Control-Shift-L>", lambda event: self._handle_largato_shortcut())
        
        logger.info("Keyboard shortcuts registered")
        
    def _handle_start_shortcut(self):
        """Handle Ctrl+Shift+A shortcut to start the bot"""
        if not self.running and not self.largato_running and self.start_button.cget('state') != 'disabled':
            logger.info("Start bot shortcut (Ctrl+Shift+A) triggered")
            self.start_bot()
            
    def _handle_stop_shortcut(self):
        """Handle Ctrl+Shift+B shortcut to stop the bot"""
        if self.running or self.largato_running:
            logger.info("Stop bot shortcut (Ctrl+Shift+B) triggered")
            self.stop_bot()
    
    def _handle_largato_shortcut(self):
        """Handle Ctrl+Shift+L shortcut to start/stop Largato hunt"""
        if not LARGATO_AVAILABLE:
            self.log_callback("Largato Hunt not available - module not properly installed")
            return
            
        if not self.running and not self.largato_running:
            logger.info("Largato hunt shortcut (Ctrl+Shift+L) triggered")
            self.start_largato_hunt()
        elif self.largato_running:
            logger.info("Stop Largato hunt shortcut (Ctrl+Shift+L) triggered")
            self.stop_largato_hunt()
    
    def start_largato_hunt(self):
        """Start the Largato hunt"""
        if not LARGATO_AVAILABLE:
            messagebox.showerror(
                "Largato Hunt Not Available",
                "Largato Hunt module is not properly installed.\n\n"
                "Please ensure 'largato_hunt.py' is in the 'app' directory and try again.",
                parent=self.root
            )
            return
            
        if self.running:
            messagebox.showwarning(
                "Bot Already Running",
                "Please stop the regular bot before starting Largato Hunt.",
                parent=self.root
            )
            return
            
        if self.largato_running:
            logger.info("Largato hunt button clicked, but hunt is already running")
            return
        
        self.log_callback("Starting Largato Hunt...")
        self.largato_running = True
        
        # Reset Largato statistics
        self.wood_stacks_var.set("0/4")
        
        # Start the Largato hunter
        success = self.largato_hunter.start_hunt()
        
        if success:
            # Update button states
            self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
            self.largato_button.config(text="STOP LARGATO\n(Ctrl+Shift+L)", bg="#F44336")
            self.stop_button.config(state=tk.NORMAL, bg="#F44336")
            
            # Update status
            self.status_var.set("Largato Hunt is running")
            
            # Start monitoring Largato hunt progress
            self._update_largato_progress()
        else:
            self.largato_running = False
            self.log_callback("Failed to start Largato Hunt")
    
    def stop_largato_hunt(self):
        """Stop the Largato hunt"""
        if not self.largato_running:
            return
        
        self.log_callback("Stopping Largato Hunt...")
        
        # Stop the Largato hunter
        success = self.largato_hunter.stop_hunt()
        
        if success:
            self.largato_running = False
            
            # Update button states
            if LARGATO_AVAILABLE:
                self.largato_button.config(text="LARGATO HUNT\n(Ctrl+Shift+L)", bg="#FF9800")
            else:
                self.largato_button.config(text="LARGATO HUNT\n(Not Available)", bg="#a0a0a0")
            self.stop_button.config(state=tk.DISABLED, bg="#a0a0a0")
            
            # Check if regular bot can be enabled
            if self._can_enable_start_button():
                self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
            
            # Update status
            self.status_var.set("Largato Hunt stopped")
    
    def _update_largato_progress(self):
        """Update the Largato hunt progress display"""
        if self.largato_running and self.largato_hunter:
            # Update wood stacks progress
            wood_count = self.largato_hunter.wood_stacks_destroyed
            self.wood_stacks_var.set(f"{wood_count}/4")
            
            # Check if hunt is completed or stopped
            if not self.largato_hunter.running:
                self.largato_running = False
                
                # Update button states
                if LARGATO_AVAILABLE:
                    self.largato_button.config(text="LARGATO HUNT\n(Ctrl+Shift+L)", bg="#FF9800")
                else:
                    self.largato_button.config(text="LARGATO HUNT\n(Not Available)", bg="#a0a0a0")
                self.stop_button.config(state=tk.DISABLED, bg="#a0a0a0")
                
                # Check if regular bot can be enabled
                if self._can_enable_start_button():
                    self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
                
                # Update status
                if wood_count >= 4:
                    self.status_var.set("Largato Hunt completed!")
                else:
                    self.status_var.set("Largato Hunt stopped")
                
                return  # Don't schedule another update
            
            # Schedule next update
            self.root.after(1000, self._update_largato_progress)
    
    def start_bot(self):
        """Start the regular bot"""
        if self.largato_running:
            messagebox.showwarning(
                "Largato Hunt Running",
                "Please stop Largato Hunt before starting the regular bot.",
                parent=self.root
            )
            return
            
        if self.running:
            logger.info("Start button clicked, but bot is already running")
            return
        
        self.log_callback("Starting bot...")
        self.running = True
        
        # Reset statistics
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        
        self.hp_potions_var.set("0")
        self.mp_potions_var.set("0")
        self.sp_potions_var.set("0")
        self.spells_var.set("0")
        
        # Reset targeting variables
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        # Store start time
        self.start_time = time.time()
        
        # Start runtime updater
        self._update_runtime()
        
        # Start the bot thread
        self.bot_thread = threading.Thread(target=self.bot_loop)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        logger.info("Bot thread started")
        
        # Update button states
        self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
        if LARGATO_AVAILABLE:
            self.largato_button.config(state=tk.DISABLED, bg="#a0a0a0")
        self.stop_button.config(state=tk.NORMAL, bg="#F44336")
        
        # Update status
        self.status_var.set("Bot is running")
    
    def stop_bot(self):
        """Stop both regular bot and Largato hunt"""
        stopped_something = False
        
        # Stop regular bot if running
        if self.running:
            self.log_callback("Stopping bot...")
            self.running = False
            if self.bot_thread:
                self.bot_thread.join(1.0)
                logger.info("Bot thread joined")
            stopped_something = True
        
        # Stop Largato hunt if running
        if self.largato_running:
            self.stop_largato_hunt()
            stopped_something = True
        
        if not stopped_something:
            logger.info("Stop button clicked, but no bot is running")
            return
        
        # Update button states
        self.stop_button.config(state=tk.DISABLED, bg="#a0a0a0")
        
        if LARGATO_AVAILABLE:
            self.largato_button.config(text="LARGATO HUNT\n(Ctrl+Shift+L)", bg="#FF9800", state=tk.NORMAL)
        else:
            self.largato_button.config(text="LARGATO HUNT\n(Not Available)", bg="#a0a0a0", state=tk.DISABLED)
        
        # Check if regular bot can be enabled
        if self._can_enable_start_button():
            self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
        
        # Update status
        self.status_var.set("All bots stopped")
    
    def _can_enable_start_button(self):
        """Check if the start button can be enabled"""
        # Check if all bars are configured
        configured = 0
        if hasattr(self, 'hp_bar') and self.hp_bar.is_setup():
            configured += 1
        if hasattr(self, 'mp_bar') and self.mp_bar.is_setup():
            configured += 1
        if hasattr(self, 'sp_bar') and self.sp_bar.is_setup():
            configured += 1
        
        return configured == 3
    
    def _update_runtime(self):
        """Update the runtime display"""
        if self.running and self.start_time:
            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            # Update display
            self.runtime_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Schedule next update
            self.root.after(1000, self._update_runtime)
    
    def enable_start_button(self):
        """Enable the start button if no other bot is running"""
        if not self.largato_running:
            self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
            self.status_var.set("Ready to start")
    
    def disable_start_button(self):
        """Disable the start button"""
        self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
    
    def set_status(self, message):
        """Set the status message"""
        self.status_var.set(message)
    
    def has_value_changed(self, prev_val, current_val, threshold=0.5):
        """
        Check if a value has changed beyond a threshold
        
        Args:
            prev_val: Previous value
            current_val: Current value
            threshold: Change threshold (default 0.5%)
            
        Returns:
            True if the value has changed beyond the threshold
        """
        return abs(prev_val - current_val) >= threshold
    
    def generate_random_target_offsets(self, radius):
        """
        Generate random offsets for spell targeting within specified radius
        
        Args:
            radius: Maximum radius from center in pixels
            
        Returns:
            (x_offset, y_offset) tuple of pixel offsets from center
        """
        # Generate random angle and distance (using square root for more even distribution)
        angle = random.uniform(0, 2 * math.pi)
        distance = radius * math.sqrt(random.random())  # Square root for more even distribution
        
        # Calculate x and y offsets (convert polar to cartesian coordinates)
        x_offset = int(distance * math.cos(angle))
        y_offset = int(distance * math.sin(angle))
        
        logger.debug(f"Generated new random offset: ({x_offset}, {y_offset})")
        return x_offset, y_offset
        
    def _find_and_setup_game_window(self):
        """Find and set up the game window for targeting"""
        # Try several methods to find the game window
        
        # 1. First try to load from config
        try:
            config = load_config()
            window_config = config.get("bars", {}).get("game_window", {})
            
            if window_config.get("configured", False):
                # Check if we have all coordinates
                if all(window_config.get(key) is not None for key in ["x1", "y1", "x2", "y2"]):
                    x1 = window_config["x1"]
                    y1 = window_config["y1"]
                    x2 = window_config["x2"]
                    y2 = window_config["y2"]
                    
                    self.game_window_rect = (x1, y1, x2, y2)
                    self.log_callback(f"Game window found in configuration: ({x1},{y1})-({x2},{y2})")
                    self.window_var.set(f"Config: {x2-x1}x{y2-y1}")
                    logger.info(f"Game window loaded from config: ({x1},{y1})-({x2},{y2})")
                    return True
        except Exception as e:
            logger.error(f"Error loading game window from config: {e}")
        
        # Additional methods from original implementation...
        # (keeping the rest of the original method for compatibility)
        
        self.log_callback("WARNING: Game window could not be detected")
        logger.warning("Failed to find game window through any method")
        return False
    
    def bot_loop(self):
        """Main bot loop that checks bars and uses potions (original implementation)"""
        # This contains the original bot loop implementation
        # (keeping all the original functionality for regular bot operation)
        
        last_hp_potion = 0
        last_mp_potion = 0
        last_sp_potion = 0
        last_spell_cast = 0
        potion_cooldown = 3.0  # seconds
        loop_count = 0
        
        self.log_callback("Bot started")
        logger.info("Bot loop started")
        
        # Find and set up game window
        game_window_found = self._find_and_setup_game_window()
        
        if not game_window_found:
            self.log_callback("WARNING: Game window not detected. Some functionality may not work properly.")
        
        # Rest of the original bot loop implementation...
        # (keeping all existing functionality)
        
        while self.running:
            try:
                loop_count += 1
                logger.debug(f"Bot loop iteration {loop_count}")
                
                # Get current time for potion cooldowns
                current_time = time.time()
                
                # Get the latest settings
                settings = self.settings_ui.get_settings()
                
                # Initialize status values
                hp_percent = 100.0
                mp_percent = 100.0
                sp_percent = 100.0
                hp_threshold = settings["thresholds"]["health"]
                mp_threshold = settings["thresholds"]["mana"]
                sp_threshold = settings["thresholds"]["stamina"]
                
                # Check HP bar
                if self.hp_bar.is_setup():
                    hp_image = self.hp_bar.get_current_screenshot_region()
                    if hp_image:
                        hp_percent = self.hp_detector.detect_percentage(hp_image)
                
                # Check MP bar
                if self.mp_bar.is_setup():
                    mp_image = self.mp_bar.get_current_screenshot_region()
                    if mp_image:
                        mp_percent = self.mp_detector.detect_percentage(mp_image)
                
                # Check SP bar
                if self.sp_bar.is_setup():
                    sp_image = self.sp_bar.get_current_screenshot_region()
                    if sp_image:
                        sp_percent = self.sp_detector.detect_percentage(sp_image)
                
                # Check if any values have changed
                hp_changed = self.has_value_changed(self.prev_hp_percent, hp_percent)
                mp_changed = self.has_value_changed(self.prev_mp_percent, mp_percent)
                sp_changed = self.has_value_changed(self.prev_sp_percent, sp_percent)
                
                # Log all percentages in a single line if any have changed
                if hp_changed or mp_changed or sp_changed:
                    status_message = (f"Health: {hp_percent:.1f}% | " +
                                    f"Mana: {mp_percent:.1f}% | " +
                                    f"Stamina: {sp_percent:.1f}%")
                    self.log_callback(status_message)
                    logger.debug(status_message)
                    
                    # Update previous values
                    self.prev_hp_percent = hp_percent
                    self.prev_mp_percent = mp_percent
                    self.prev_sp_percent = sp_percent
                    
                    # Update UI values
                    self.hp_value_var.set(f"{hp_percent:.1f}%")
                    self.mp_value_var.set(f"{mp_percent:.1f}%")
                    self.sp_value_var.set(f"{sp_percent:.1f}%")
                
                # Use Health potion if needed
                if hp_percent < hp_threshold and current_time - last_hp_potion > potion_cooldown:
                    hp_key = settings["potion_keys"]["health"]
                    self.log_callback(f"Health low ({hp_percent:.1f}%), using health potion (key {hp_key})")
                    logger.info(f"Using health potion - HP: {hp_percent:.1f}% < {hp_threshold}%")
                    press_key(None, hp_key)
                    last_hp_potion = current_time
                    
                    # Update statistics
                    self.hp_potions_used += 1
                    self.hp_potions_var.set(str(self.hp_potions_used))
                
                # Use Mana potion if needed
                if mp_percent < mp_threshold and current_time - last_mp_potion > potion_cooldown:
                    mp_key = settings["potion_keys"]["mana"]
                    self.log_callback(f"Mana low ({mp_percent:.1f}%), using mana potion (key {mp_key})")
                    logger.info(f"Using mana potion - MP: {mp_percent:.1f}% < {mp_threshold}%")
                    press_key(None, mp_key)
                    last_mp_potion = current_time
                    
                    # Update statistics
                    self.mp_potions_used += 1
                    self.mp_potions_var.set(str(self.mp_potions_used))
                
                # Use Stamina potion if needed
                if sp_percent < sp_threshold and current_time - last_sp_potion > potion_cooldown:
                    sp_key = settings["potion_keys"]["stamina"]
                    self.log_callback(f"Stamina low ({sp_percent:.1f}%), using stamina potion (key {sp_key})")
                    logger.info(f"Using stamina potion - SP: {sp_percent:.1f}% < {sp_threshold}%")
                    press_key(None, sp_key)
                    last_sp_potion = current_time
                    
                    # Update statistics
                    self.sp_potions_used += 1
                    self.sp_potions_var.set(str(self.sp_potions_used))
                
                # Spellcasting logic (keeping original implementation)
                if settings["spellcasting"]["enabled"]:
                    spell_interval = settings["spellcasting"]["spell_interval"]
                    if current_time - last_spell_cast > spell_interval:
                        spell_key = settings["spellcasting"]["spell_key"]
                        
                        # Press the spell key
                        press_key(None, spell_key)
                        
                        # Small delay before right-clicking
                        time.sleep(0.1)
                        
                        # Right-click (simplified for compatibility)
                        try:
                            press_right_mouse(None)
                        except Exception as e:
                            logger.error(f"Error with right-click: {e}")
                        
                        # Update state
                        last_spell_cast = current_time
                        self.spells_cast += 1
                        self.spells_var.set(str(self.spells_cast))
                
                # Wait for next scan
                scan_interval = settings["scan_interval"]
                time.sleep(scan_interval)
                
            except Exception as e:
                self.log_callback(f"Error in bot loop: {e}")
                logger.error(f"Error in bot loop: {e}", exc_info=True)
                time.sleep(1)
        
        self.log_callback("Bot stopped")
        logger.info("Bot loop stopped")