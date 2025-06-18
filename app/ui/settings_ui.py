import tkinter as tk
from tkinter import ttk
import logging
from app.config import load_config

logger = logging.getLogger('PristonBot')

class SettingsUI:
    def __init__(self, parent, save_callback):
        self.parent = parent
        self.save_callback = save_callback
        self.logger = logging.getLogger('PristonBot')
        
        self.create_ui()
        self.load_settings()
    
    def create_ui(self):
        container = ttk.Frame(self.parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        potion_frame = ttk.LabelFrame(container, text="Potion Keys", padding=5)
        potion_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.hp_key_var = tk.StringVar(value="1")
        self.mp_key_var = tk.StringVar(value="3")
        self.sp_key_var = tk.StringVar(value="2")
        
        ttk.Label(potion_frame, text="Health Potion Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(potion_frame, textvariable=self.hp_key_var, width=5).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(potion_frame, text="Mana Potion Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(potion_frame, textvariable=self.mp_key_var, width=5).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(potion_frame, text="Stamina Potion Key:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(potion_frame, textvariable=self.sp_key_var, width=5).grid(row=2, column=1, padx=5, pady=2)
        
        threshold_frame = ttk.LabelFrame(container, text="Thresholds (%)", padding=5)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        self.hp_threshold_var = tk.IntVar(value=50)
        self.mp_threshold_var = tk.IntVar(value=30)
        self.sp_threshold_var = tk.IntVar(value=40)
        
        ttk.Label(threshold_frame, text="Health Threshold:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(threshold_frame, from_=10, to=90, orient=tk.HORIZONTAL, variable=self.hp_threshold_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(threshold_frame, textvariable=self.hp_threshold_var).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(threshold_frame, text="Mana Threshold:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(threshold_frame, from_=10, to=90, orient=tk.HORIZONTAL, variable=self.mp_threshold_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(threshold_frame, textvariable=self.mp_threshold_var).grid(row=1, column=2, padx=5, pady=2)
        
        ttk.Label(threshold_frame, text="Stamina Threshold:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Scale(threshold_frame, from_=10, to=90, orient=tk.HORIZONTAL, variable=self.sp_threshold_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(threshold_frame, textvariable=self.sp_threshold_var).grid(row=2, column=2, padx=5, pady=2)
        
        threshold_frame.columnconfigure(1, weight=1)
        
        spell_frame = ttk.LabelFrame(container, text="Spellcasting", padding=5)
        spell_frame.pack(fill=tk.X, pady=5)
        
        self.spell_enabled_var = tk.BooleanVar(value=False)
        self.spell_key_var = tk.StringVar(value="F5")
        self.spell_interval_var = tk.DoubleVar(value=3.0)
        
        ttk.Checkbutton(spell_frame, text="Enable Spellcasting", variable=self.spell_enabled_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(spell_frame, text="Spell Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(spell_frame, textvariable=self.spell_key_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(spell_frame, text="Spell Interval (s):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(spell_frame, textvariable=self.spell_interval_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        misc_frame = ttk.LabelFrame(container, text="Miscellaneous", padding=5)
        misc_frame.pack(fill=tk.X, pady=5)
        
        self.scan_interval_var = tk.DoubleVar(value=0.5)
        self.debug_enabled_var = tk.BooleanVar(value=True)
        
        ttk.Label(misc_frame, text="Scan Interval (s):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(misc_frame, textvariable=self.scan_interval_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(misc_frame, text="Enable Debug Logging", variable=self.debug_enabled_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.RIGHT, padx=5)
    
    def get_settings(self):
        return {
            "potion_keys": {
                "health": self.hp_key_var.get(),
                "mana": self.mp_key_var.get(),
                "stamina": self.sp_key_var.get()
            },
            "thresholds": {
                "health": self.hp_threshold_var.get(),
                "mana": self.mp_threshold_var.get(),
                "stamina": self.sp_threshold_var.get()
            },
            "spellcasting": {
                "enabled": self.spell_enabled_var.get(),
                "spell_key": self.spell_key_var.get(),
                "spell_interval": self.spell_interval_var.get(),
                "random_targeting": False,
                "target_radius": 100,
                "target_change_interval": 5,
                "target_method": "Ring Around Character",
                "target_points_count": 8,
                "target_zone": {
                    "x1": None,
                    "y1": None,
                    "x2": None,
                    "y2": None,
                    "points": []
                }
            },
            "scan_interval": self.scan_interval_var.get(),
            "debug_enabled": self.debug_enabled_var.get()
        }
    
    def set_settings(self, config):
        try:
            if "potion_keys" in config:
                self.hp_key_var.set(config["potion_keys"].get("health", "1"))
                self.mp_key_var.set(config["potion_keys"].get("mana", "3"))
                self.sp_key_var.set(config["potion_keys"].get("stamina", "2"))
            
            if "thresholds" in config:
                self.hp_threshold_var.set(config["thresholds"].get("health", 50))
                self.mp_threshold_var.set(config["thresholds"].get("mana", 30))
                self.sp_threshold_var.set(config["thresholds"].get("stamina", 40))
            
            if "spellcasting" in config:
                self.spell_enabled_var.set(config["spellcasting"].get("enabled", False))
                self.spell_key_var.set(config["spellcasting"].get("spell_key", "F5"))
                self.spell_interval_var.set(config["spellcasting"].get("spell_interval", 3.0))
            
            self.scan_interval_var.set(config.get("scan_interval", 0.5))
            self.debug_enabled_var.set(config.get("debug_enabled", True))
            
            logger.info("Settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def load_settings(self):
        try:
            config = load_config()
            self.set_settings(config)
        except Exception as e:
            logger.error(f"Error loading settings from config: {e}")
    
    def save_settings(self):
        if self.save_callback:
            self.save_callback()