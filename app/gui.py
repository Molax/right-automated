import tkinter as tk
from tkinter import ttk
import time
import logging
from app.ui.modern_interface import ModernInterface
from app.ui.modern_settings import ModernSettings
from app.ui.modern_controls import ModernControls

# Try to import dark mode manager, create fallback if not available
try:
    from dark_mode_manager import DarkModeManager
except ImportError:
    class DarkModeManager:
        def __init__(self, root):
            self.root = root
            self.is_dark = False
        
        def create_toggle_button(self, parent):
            return tk.Button(parent, text="🌙", width=3, height=1)

logger = logging.getLogger('PristonBot')
main_app = None

class ModernPristonTaleBot:
    def __init__(self, root):
        global main_app
        main_app = self
        
        logger.info("Initializing Modern Priston Tale Bot")
        self.root = root
        
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass
        
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.title("Priston Tale Bot")
        self.root.configure(bg="#1a1a1a")
        
        # Initialize components
        self.interface = ModernInterface(self)
        self.settings = ModernSettings(self)
        self.controls = ModernControls(self)
        
        self._initialize_components()
        
        self.log("Modern bot interface initialized")
        
        # Fixed the lambda issue by using proper method calls
        if hasattr(self, 'config_manager'):
            try:
                if self.config_manager.load_bar_config():
                    self.log("Configuration loaded successfully")
                else:
                    self.log("Welcome! Configure your bars to get started")
            except Exception as e:
                self.log(f"Error loading config: {e}")
                self.log("Welcome! Configure your bars to get started")
        else:
            self.log("Welcome! Configure your bars to get started")
        
        self.check_bar_config()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Modern Bot GUI initialized successfully")
    
    def _initialize_components(self):
        """Initialize compatibility objects without lambda issues"""
        
        class MockBar:
            def is_setup(self):
                return False
        
        class MockBarSelector:
            def __init__(self, parent):
                self.parent = parent
                self.hp_bar_selector = MockBar()
                self.mp_bar_selector = MockBar()
                self.sp_bar_selector = MockBar()
                self.largato_skill_selector = MockBar()
            
            def get_configured_count(self):
                return 0
            
            def get_total_count(self):
                return 4
            
            def start_bar_selection(self, name, color):
                return self.parent.start_actual_bar_selection(name, color)
        
        class MockSettings:
            def __init__(self, parent):
                self.parent = parent
                self.control_container = getattr(parent, 'settings_frame', None)
                self.save_callback = parent.save_config
        
        class MockConfigManager:
            def __init__(self, parent):
                self.parent = parent
            
            def load_bar_config(self):
                return False
            
            def save_bar_config(self):
                return True
        
        class MockBotController:
            def __init__(self, parent):
                self.parent = parent
                self.running = False
                self.largato_running = False
            
            def enable_start_button(self):
                if hasattr(self.parent, 'start_btn'):
                    self.parent.start_btn.configure(state=tk.NORMAL)
            
            def disable_start_button(self):
                if hasattr(self.parent, 'start_btn'):
                    self.parent.start_btn.configure(state=tk.DISABLED)
            
            def set_status(self, msg):
                self.parent.update_status(msg, "#28a745")
            
            def stop_bot(self):
                self.parent.stop_bot()
            
            def stop_largato_hunt(self):
                self.parent.log("Largato hunt stopped")
        
        # Initialize all mock objects
        self.bar_selector_ui = MockBarSelector(self)
        self.settings_ui = MockSettings(self)
        self.config_manager = MockConfigManager(self)
        self.bot_controller = MockBotController(self)
        
        logger.info("Modern components initialized")
    
    def start_actual_bar_selection(self, bar_name, color):
        """Implement actual bar selection logic here"""
        self.log(f"Starting {bar_name} bar selection with {color} overlay...")
        # Here you would implement the actual screen selection logic
        # that was working in your original application
    
    def log(self, message):
        if hasattr(self, 'interface') and hasattr(self.interface, 'log_text'):
            timestamp = time.strftime("%H:%M:%S")
            self.interface.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.interface.log_text.see(tk.END)
        logger.info(message)
    
    def select_bar(self, bar_type):
        self.log(f"Starting {bar_type} selection...")
        
        # Call the actual bar selection method
        if bar_type == "health_bar":
            self.start_actual_bar_selection("Health", "red")
        elif bar_type == "mana_bar":
            self.start_actual_bar_selection("Mana", "blue")
        elif bar_type == "stamina_bar":
            self.start_actual_bar_selection("Stamina", "green")
        elif bar_type == "largato_skill":
            self.start_actual_bar_selection("Largato Skill", "purple")
        else:
            self.log(f"Unknown bar type: {bar_type}")
    
    def start_bot(self):
        self.log("Bot started!")
        if hasattr(self, 'controls'):
            self.controls.start_btn.configure(state=tk.DISABLED)
            self.controls.stop_btn.configure(state=tk.NORMAL)
        self.update_status("Running", "#28a745")
    
    def stop_bot(self):
        self.log("Bot stopped!")
        if hasattr(self, 'controls'):
            self.controls.start_btn.configure(state=tk.NORMAL)
            self.controls.stop_btn.configure(state=tk.DISABLED)
        self.update_status("Ready", "#28a745")
    
    def start_largato_hunt(self):
        self.log("Largato Hunt started!")
        self.update_status("Hunting", "#9c27b0")
    
    def reset_stats(self):
        self.log("Statistics reset!")
    
    def update_status(self, text, color):
        if hasattr(self, 'interface'):
            self.interface.update_status(text, color)
    
    def toggle_theme(self):
        self.log("Theme toggled!")
    
    def save_config(self):
        if hasattr(self, 'config_manager'):
            try:
                result = self.config_manager.save_bar_config()
                if result:
                    self.log("Settings saved successfully")
                    self.check_bar_config()
                else:
                    self.log("Failed to save settings")
                return result
            except Exception as e:
                self.log(f"Error saving config: {e}")
                return False
        return False
    
    def check_bar_config(self):
        # Update configuration status
        if hasattr(self, 'bar_selector_ui'):
            try:
                configured = self.bar_selector_ui.get_configured_count()
                total = self.bar_selector_ui.get_total_count()
                
                if hasattr(self, 'interface'):
                    if configured >= 3:
                        if hasattr(self, 'controls'):
                            self.controls.start_btn.configure(state=tk.NORMAL)
                        self.interface.update_config_status("✓ Ready to start", "#28a745")
                        if configured == 4:
                            if hasattr(self, 'controls'):
                                self.controls.largato_btn.configure(state=tk.NORMAL)
                            self.interface.update_config_status("✓ All features available", "#28a745")
                    else:
                        if hasattr(self, 'controls'):
                            self.controls.start_btn.configure(state=tk.DISABLED)
                        self.interface.update_config_status(f"Configure {3-configured} more bars", "#ffc107")
            except Exception as e:
                self.log(f"Error checking bar config: {e}")
    
    def on_closing(self):
        try:
            self.save_config()
            logger.info("Configuration saved on exit")
        except Exception as e:
            logger.error(f"Error on closing: {e}", exc_info=True)
        finally:
            self.root.destroy()

# For backward compatibility, alias the class
PristonTaleBot = ModernPristonTaleBot