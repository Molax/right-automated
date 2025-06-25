import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
import logging

logger = logging.getLogger('PristonBot')

main_app = None

class PristonTaleBot:
    def __init__(self, root):
        global main_app
        main_app = self
        
        logger.info("Initializing Priston Tale Bot")
        self.root = root
        
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass
        
        self.root.geometry("950x800")
        self.root.minsize(950, 800)
        self.root.title("Priston Tale Potion Bot")
        self.root.configure(bg="#f0f0f0")
        
        main_container = ttk.Frame(root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=2)  # Give more weight to left column
        main_container.grid_columnconfigure(1, weight=1)  # Less weight to right column
        
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Priston Tale Potion Bot", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(
            header_frame, 
            text="v1.0.0", 
            font=("Arial", 10), 
            foreground="#666666"
        )
        version_label.pack(side=tk.RIGHT)
        
        left_column = ttk.Frame(main_container)
        left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        left_column.grid_rowconfigure(1, weight=1)
        left_column.grid_columnconfigure(0, weight=1)
        
        right_column = ttk.Frame(main_container)
        right_column.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        right_column.grid_rowconfigure(0, weight=1)
        right_column.grid_columnconfigure(0, weight=1)
        
        self._create_bar_selection_frame(left_column)
        self._create_log_frame(left_column)
        self._create_settings_frame(right_column)
        self._initialize_components()
        
        self.log("Bot GUI initialized successfully")
        
        if self.config_manager.load_bar_config():
            self.log("Loaded saved configuration")
        else:
            self.log("No saved configuration found")
            self.log("Please configure all bars to continue")
        
        self.check_bar_config()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Bot GUI initialized successfully")
    
    def _create_bar_selection_frame(self, parent):
        self.bars_frame = ttk.LabelFrame(parent, text="Bar Selection", padding="5")
        self.bars_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
    
    def _create_log_frame(self, parent):
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding="5")
        log_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=12, 
            width=50, 
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
    
    def _create_settings_frame(self, parent):
        settings_frame = ttk.LabelFrame(parent, text="Settings & Control", padding="5")
        settings_frame.grid(row=0, column=0, sticky="nsew")
        settings_frame.grid_rowconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(0, weight=1)
        
        # Configure the parent to not expand the settings too much
        parent.grid_columnconfigure(0, weight=0, minsize=400)  # Fixed reasonable width
        
        self.settings_frame = settings_frame
    
    def _initialize_components(self):
        from app.ui.bar_selector_ui import BarSelectorUI
        from app.ui.settings_ui import SettingsUI
        from app.ui.bot_controller import BotControllerUI
        from app.ui.config_manager_ui import ConfigManagerUI
        
        self.bar_selector_ui = BarSelectorUI(self.bars_frame, self.root, self.log)
        
        self.settings_ui = SettingsUI(self.settings_frame, self.save_config)
        
        self.config_manager = ConfigManagerUI(
            self.bar_selector_ui,
            self.settings_ui,
            self.log
        )
        
        self.bot_controller = BotControllerUI(
            self.settings_ui.control_container,
            self.root,
            self.bar_selector_ui.hp_bar_selector,
            self.bar_selector_ui.mp_bar_selector,
            self.bar_selector_ui.sp_bar_selector,
            self.bar_selector_ui.largato_skill_selector,
            self.settings_ui,
            self.log
        )
        
        logger.info("Components initialized")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        logger.info(message)
    
    def save_config(self):
        result = self.config_manager.save_bar_config()
        if result:
            self.log("Settings saved successfully")
            self.check_bar_config()
        else:
            self.log("Failed to save settings")
        return result
    
    def check_bar_config(self):
        if hasattr(self.bar_selector_ui, 'get_configured_count'):
            configured = self.bar_selector_ui.get_configured_count()
            total = self.bar_selector_ui.get_total_count()
            
            if configured > 0:
                self.bot_controller.set_status(f"{configured}/{total} bars configured")
                
            if configured >= 3:
                self.bot_controller.enable_start_button()
                if configured == 4:
                    self.bot_controller.set_status("Ready to start (Largato Hunt available)")
                    self.log("All bars configured! Regular bot and Largato Hunt are available.")
                else:
                    self.bot_controller.set_status("Ready to start (Largato Hunt requires skill bar)")
                    self.log("Core bars configured! Configure Largato skill bar for hunt feature.")
            else:
                self.bot_controller.disable_start_button()
                self.bot_controller.set_status("Please configure all bars")
    
    def on_closing(self):
        try:
            if hasattr(self, 'bot_controller'):
                if hasattr(self.bot_controller, 'running') and self.bot_controller.running:
                    self.bot_controller.stop_bot()
                if hasattr(self.bot_controller, 'largato_running') and self.bot_controller.largato_running:
                    self.bot_controller.stop_largato_hunt()
                    
            self.save_config()
            logger.info("Configuration saved on exit")
            
        except Exception as e:
            logger.error(f"Error on closing: {e}", exc_info=True)
        finally:
            self.root.destroy()