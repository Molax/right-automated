import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import logging
from app.ui.components import ScrollableFrame
from app.ui.bar_selector_ui import BarSelectorUI
from app.ui.settings_ui import SettingsUI
from app.ui.bot_controller_ui import BotControllerUI
from app.ui.config_manager_ui import ConfigManagerUI

logger = logging.getLogger('PristonBot')

main_app = None

class PristonTaleBot:
    def __init__(self, root):
        global main_app
        main_app = self
        
        logger.info("Initializing Priston Tale Bot")
        self.root = root
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(title_frame, text="Priston Tale Bot", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)

        version_label = ttk.Label(title_frame, text="v1.0.0", 
                                 font=("Arial", 10), foreground="#666666")
        version_label.pack(side=tk.RIGHT)

        scrollable_container = ScrollableFrame(main_container)
        scrollable_container.pack(fill=tk.BOTH, expand=True)

        content_frame = scrollable_container.scrollable_frame

        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        window_frame = ttk.LabelFrame(left_column, text="Game Window", padding=5)
        window_frame.pack(fill=tk.X, pady=(0, 5))
        
        window_content = ttk.Frame(window_frame)
        window_content.pack(fill=tk.X, pady=5)
        
        preview_frame = ttk.Frame(window_content)
        preview_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.window_preview_label = tk.Label(preview_frame, text="Not Selected", 
                                            borderwidth=1, relief="solid",
                                            width=25, height=8)
        self.window_preview_label.pack(padx=5, pady=5)
        
        button_frame = ttk.Frame(window_content)
        button_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Button(button_frame, text="Select Game Window", 
                  command=self.start_window_selection).pack(fill=tk.X, pady=5)
        
        bars_frame = ttk.LabelFrame(left_column, text="Bar Selection", padding=5)
        bars_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_frame = ttk.LabelFrame(left_column, text="Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_container, height=10, width=40, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        settings_frame = ttk.LabelFrame(right_column, text="Settings", padding=5)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        control_frame = ttk.LabelFrame(right_column, text="Bot Control", padding=5)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.bar_selector_ui = BarSelectorUI(bars_frame, root, self.log)
        
        self.settings_ui = SettingsUI(settings_frame, self.save_config)
        
        self.config_manager = ConfigManagerUI(
            self.bar_selector_ui,
            self.settings_ui,
            self.log
        )
        
        self.bot_controller = BotControllerUI(
            control_frame, 
            root,
            self.bar_selector_ui.hp_bar_selector,
            self.bar_selector_ui.