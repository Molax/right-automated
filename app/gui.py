"""
Main GUI for the Priston Tale Potion Bot
---------------------------------------
Clean implementation without game window selection.
"""

import os
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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
        
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.title("Priston Tale Potion Bot")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        main_container = ttk.Frame(root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        
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
        
        left_column = ttk.Frame(main_container)
        left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        left_column.grid_rowconfigure(0, weight=1)
        left_column.grid_rowconfigure(1, weight=1)
        left_column.grid_columnconfigure(0, weight=1)
        
        right_column = ttk.Frame(main_container)
        right_column.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        right_column.grid_rowconfigure(0, weight=1)
        right_column.grid_columnconfigure(0, weight=1)
        
        self._create_bar_selection_frame(left_column)
        self._create_log_frame(left_column)
        self._create_settings_and_control_frame(right_column)
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
    
    def _create_settings_and_control_frame(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        self.settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.settings_frame, text="Settings")
        
        self.control_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.control_frame, text="Bot Control")
        
        control_container = ttk.Frame(self.control_frame)
        control_container.pack(fill=tk.BOTH, expand=True)
        
        status_frame = ttk.LabelFrame(control_container, text="Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        values_frame = ttk.LabelFrame(control_container, text="Current Values", padding="5")
        values_frame.pack(fill=tk.X, pady=(0, 10))
        
        buttons_frame = ttk.LabelFrame(control_container, text="Controls", padding="5")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_frame = ttk.LabelFrame(control_container, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_container = status_frame
        self.values_container = values_frame
        self.buttons_container = buttons_frame
        self.stats_container = stats_frame
    
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
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        logger.info(message)
        
        lines = self.log_text.get(1.0, tk.END).count('\n')
        if lines > 1000:
            self.log_text.delete(1.0, "201.0")
    
    def check_bar_config(self):
        try:
            configured = 0
            
            if hasattr(self.bar_selector_ui, 'get_configured_count'):
                configured = self.bar_selector_ui.get_configured_count()
            else:
                if hasattr(self.bar_selector_ui, 'hp_bar_selector') and self.bar_selector_ui.hp_bar_selector.is_setup():
                    configured += 1
                if hasattr(self.bar_selector_ui, 'mp_bar_selector') and self.bar_selector_ui.mp_bar_selector.is_setup():
                    configured += 1
                if hasattr(self.bar_selector_ui, 'sp_bar_selector') and self.bar_selector_ui.sp_bar_selector.is_setup():
                    configured += 1
            
            if configured >= 3:
                if hasattr(self.bot_controller, 'enable_start_button'):
                    self.bot_controller.enable_start_button()
                if hasattr(self.bot_controller, 'set_status'):
                    if configured == 4:
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
                    self.bot_controller.set_status(f"Configure remaining bars ({configured}/3)")
                
            if configured < 3:
                self.root.after(2000, self.check_bar_config)
                
        except Exception as e:
            logger.error(f"Error checking bar configuration: {e}", exc_info=True)
            self.root.after(5000, self.check_bar_config)
    
    def save_config(self):
        try:
            if hasattr(self, 'config_manager') and self.config_manager.save_bar_config():
                self.log("Configuration saved successfully")
            else:
                self.log("Failed to save configuration")
        except Exception as e:
            self.log(f"Error saving configuration: {e}")
            logger.error(f"Error saving configuration: {e}", exc_info=True)
    
    def on_closing(self):
        try:
            if hasattr(self, 'bot_controller'):
                if hasattr(self.bot_controller, 'running') and self.bot_controller.running:
                    self.bot_controller.stop_bot()
                if hasattr(self.bot_controller, 'largato_running') and self.bot_controller.largato_running:
                    self.bot_controller.stop_largato_hunt()
                    
            self.save_config()
            logger.info("Configuration saved on exit")
            
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error on closing: {e}", exc_info=True)
            try:
                self.root.destroy()
            except:
                pass


def main():
    try:
        from app.config import setup_logging
        setup_logging()
        
        root = tk.Tk()
        
        try:
            icon_path = "resources/potion_icon.ico"
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except Exception as e:
            logger.debug(f"Could not set application icon: {e}")
        
        app = PristonTaleBot(root)
        
        root.update_idletasks()
        root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
        
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Fatal error during initialization: {e}", exc_info=True)
        
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
            print(f"FATAL ERROR: {e}")


if __name__ == "__main__":
    main()