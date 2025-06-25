import tkinter as tk
from tkinter import ttk
import time
import logging
from app.ui.modern_interface import ModernInterface
from app.ui.modern_settings import ModernSettings
from app.ui.modern_controls import ModernControls

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
        
        self._initialize_screen_selectors()
        
        self.interface = ModernInterface(self)
        self.settings = ModernSettings(self)
        self.controls = ModernControls(self)
        
        self._initialize_components()
        
        self.log("Modern bot interface initialized")
        
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
    
    def _initialize_screen_selectors(self):
        """Initialize the actual ScreenSelector instances"""
        try:
            from app.bar_selector.screen_selector import ScreenSelector
            
            self.hp_bar_selector = ScreenSelector(self.root)
            self.mp_bar_selector = ScreenSelector(self.root)
            self.sp_bar_selector = ScreenSelector(self.root)
            self.largato_skill_selector = ScreenSelector(self.root)
            
            logger.info("ScreenSelector instances initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import ScreenSelector: {e}")
            try:
                from app.bar_selector import ScreenSelector
                
                self.hp_bar_selector = ScreenSelector(self.root)
                self.mp_bar_selector = ScreenSelector(self.root)
                self.sp_bar_selector = ScreenSelector(self.root)
                self.largato_skill_selector = ScreenSelector(self.root)
                
                logger.info("ScreenSelector instances initialized from fallback")
                
            except ImportError as e2:
                logger.error(f"Failed to import ScreenSelector from fallback: {e2}")
                self.hp_bar_selector = None
                self.mp_bar_selector = None
                self.sp_bar_selector = None
                self.largato_skill_selector = None
    
    def _initialize_components(self):
        """Initialize compatibility objects"""
        
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
        
        self.config_manager = MockConfigManager(self)
        self.bot_controller = MockBotController(self)
        
        logger.info("Components initialized")
    
    def select_bar(self, bar_type):
        """Main entry point for bar selection from UI buttons"""
        self.log(f"Starting {bar_type} selection...")
        
        selector = None
        color = "yellow"
        title = bar_type.replace("_", " ").title()
        
        if bar_type == "health_bar":
            selector = self.hp_bar_selector
            color = "red"
            title = "Health Bar"
        elif bar_type == "mana_bar":
            selector = self.mp_bar_selector
            color = "blue"
            title = "Mana Bar"
        elif bar_type == "stamina_bar":
            selector = self.sp_bar_selector
            color = "green"
            title = "Stamina Bar"
        elif bar_type == "largato_skill":
            selector = self.largato_skill_selector
            color = "purple"
            title = "Largato Skill Bar"
        else:
            self.log(f"Unknown bar type: {bar_type}")
            return
        
        if selector is None:
            self.log("ERROR: ScreenSelector not available. Check imports.")
            return
        
        def on_selection_complete():
            try:
                self.log(f"{title} selection completed successfully")
                self.check_bar_config()
            except Exception as e:
                self.log(f"Error in completion callback: {e}")
        
        try:
            success = selector.start_selection(
                title=title,
                color=color,
                completion_callback=on_selection_complete
            )
            
            if not success:
                self.log(f"Failed to start {title} selection")
        except Exception as e:
            logger.error(f"Error starting {title} selection: {e}")
            self.log(f"Failed to start {title} selection: {e}")
    
    def start_actual_bar_selection(self, bar_name, color):
        """Legacy method - redirects to select_bar"""
        bar_type_map = {
            "Health": "health_bar",
            "Mana": "mana_bar", 
            "Stamina": "stamina_bar",
            "Largato Skill": "largato_skill"
        }
        
        bar_type = bar_type_map.get(bar_name)
        if bar_type:
            self.select_bar(bar_type)
        else:
            self.log(f"Unknown bar name: {bar_name}")
    
    def check_bar_config(self):
        """Check which bars are configured"""
        configured_count = 0
        total_count = 4
        
        if self.hp_bar_selector and self.hp_bar_selector.is_setup():
            configured_count += 1
        if self.mp_bar_selector and self.mp_bar_selector.is_setup():
            configured_count += 1
        if self.sp_bar_selector and self.sp_bar_selector.is_setup():
            configured_count += 1
        if self.largato_skill_selector and self.largato_skill_selector.is_setup():
            configured_count += 1
        
        self.log(f"Bars configured: {configured_count}/{total_count}")
        
        if configured_count >= 3:
            self.log("Ready to start bot!")
        else:
            self.log("Configure at least Health, Mana, and Stamina bars to start bot")
    
    def log(self, message):
        if hasattr(self, 'interface') and hasattr(self.interface, 'log_text'):
            timestamp = time.strftime("%H:%M:%S")
            self.interface.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.interface.log_text.see(tk.END)
        logger.info(message)
    
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
    
    def on_closing(self):
        logger.info("Application closing")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernPristonTaleBot(root)
    root.mainloop()