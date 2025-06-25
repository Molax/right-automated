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
        
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(parent, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self._create_settings_ui()
        self._load_settings()
        
        logger.info("Settings UI initialized")
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _create_settings_ui(self):
        self._create_potion_keys_section()
        self._create_thresholds_section()
        self._create_behavior_section()
        self._create_spellcasting_section()
        self._create_control_section()
    
    def _create_potion_keys_section(self):
        keys_frame = ttk.LabelFrame(self.scrollable_frame, text="Potion Keys", padding="5")
        keys_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.hp_key_var = tk.StringVar(value="1")
        self.mp_key_var = tk.StringVar(value="3")
        self.sp_key_var = tk.StringVar(value="2")
        
        # Arrange in a more compact 3-column layout
        ttk.Label(keys_frame, text="Health:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        hp_entry = ttk.Entry(keys_frame, textvariable=self.hp_key_var, width=6)
        hp_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(keys_frame, text="Mana:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        mp_entry = ttk.Entry(keys_frame, textvariable=self.mp_key_var, width=6)
        mp_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(keys_frame, text="Stamina:").grid(row=0, column=4, sticky="w", padx=(0, 5))
        sp_entry = ttk.Entry(keys_frame, textvariable=self.sp_key_var, width=6)
        sp_entry.grid(row=0, column=5)
    
    def _create_thresholds_section(self):
        thresholds_frame = ttk.LabelFrame(self.scrollable_frame, text="Potion Thresholds", padding="5")
        thresholds_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.hp_threshold_var = tk.DoubleVar(value=50)
        self.mp_threshold_var = tk.DoubleVar(value=30)
        self.sp_threshold_var = tk.DoubleVar(value=40)
        
        hp_frame = ttk.Frame(thresholds_frame)
        hp_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(hp_frame, text="Health:", width=10, foreground="#e74c3c").pack(side=tk.LEFT)
        hp_scale = ttk.Scale(hp_frame, from_=10, to=90, variable=self.hp_threshold_var, orient=tk.HORIZONTAL)
        hp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.hp_thresh_label = ttk.Label(hp_frame, text="50%", width=5)
        self.hp_thresh_label.pack(side=tk.LEFT)
        hp_scale.configure(command=lambda v: self.hp_thresh_label.config(text=f"{int(float(v))}%"))
        
        mp_frame = ttk.Frame(thresholds_frame)
        mp_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(mp_frame, text="Mana:", width=10, foreground="#3498db").pack(side=tk.LEFT)
        mp_scale = ttk.Scale(mp_frame, from_=10, to=90, variable=self.mp_threshold_var, orient=tk.HORIZONTAL)
        mp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.mp_thresh_label = ttk.Label(mp_frame, text="30%", width=5)
        self.mp_thresh_label.pack(side=tk.LEFT)
        mp_scale.configure(command=lambda v: self.mp_thresh_label.config(text=f"{int(float(v))}%"))
        
        sp_frame = ttk.Frame(thresholds_frame)
        sp_frame.pack(fill=tk.X)
        ttk.Label(sp_frame, text="Stamina:", width=10, foreground="#2ecc71").pack(side=tk.LEFT)
        sp_scale = ttk.Scale(sp_frame, from_=10, to=90, variable=self.sp_threshold_var, orient=tk.HORIZONTAL)
        sp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.sp_thresh_label = ttk.Label(sp_frame, text="40%", width=5)
        self.sp_thresh_label.pack(side=tk.LEFT)
        sp_scale.configure(command=lambda v: self.sp_thresh_label.config(text=f"{int(float(v))}%"))
    
    def _create_behavior_section(self):
        behavior_frame = ttk.LabelFrame(self.scrollable_frame, text="Bot Behavior", padding="5")
        behavior_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.scan_interval_var = tk.DoubleVar(value=0.5)
        self.debug_enabled_var = tk.BooleanVar(value=False)
        
        scan_frame = ttk.Frame(behavior_frame)
        scan_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(scan_frame, text="Scan Interval:", width=12).pack(side=tk.LEFT)
        scan_scale = ttk.Scale(scan_frame, from_=0.1, to=3.0, variable=self.scan_interval_var, orient=tk.HORIZONTAL)
        scan_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.scan_label = ttk.Label(scan_frame, text="0.5s", width=5)
        self.scan_label.pack(side=tk.LEFT)
        scan_scale.configure(command=lambda v: self.scan_label.config(text=f"{float(v):.1f}s"))
        
        debug_frame = ttk.Frame(behavior_frame)
        debug_frame.pack(fill=tk.X)
        ttk.Checkbutton(debug_frame, text="Enable debug mode", variable=self.debug_enabled_var).pack(side=tk.LEFT)
    
    def _create_spellcasting_section(self):
        spell_frame = ttk.LabelFrame(self.scrollable_frame, text="Spellcasting", padding="5")
        spell_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.spell_enabled_var = tk.BooleanVar(value=False)
        self.spell_key_var = tk.StringVar(value="4")
        self.spell_interval_var = tk.DoubleVar(value=3.0)
        
        ttk.Checkbutton(spell_frame, text="Enable spellcasting", variable=self.spell_enabled_var, 
                       command=self._toggle_spell_settings).pack(anchor=tk.W, pady=(0, 5))
        
        self.spell_settings_frame = ttk.Frame(spell_frame)
        self.spell_settings_frame.pack(fill=tk.X)
        
        key_frame = ttk.Frame(self.spell_settings_frame)
        key_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(key_frame, text="Key:").pack(side=tk.LEFT)
        ttk.Entry(key_frame, textvariable=self.spell_key_var, width=6).pack(side=tk.LEFT, padx=(5, 0))
        
        interval_frame = ttk.Frame(self.spell_settings_frame)
        interval_frame.pack(fill=tk.X)
        ttk.Label(interval_frame, text="Interval:").pack(side=tk.LEFT)
        interval_scale = ttk.Scale(interval_frame, from_=0.5, to=10.0, variable=self.spell_interval_var, orient=tk.HORIZONTAL)
        interval_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        self.interval_label = ttk.Label(interval_frame, text="3.0s", width=5)
        self.interval_label.pack(side=tk.LEFT)
        interval_scale.configure(command=lambda v: self.interval_label.config(text=f"{float(v):.1f}s"))
        
        self._toggle_spell_settings()
    
    def _create_control_section(self):
        self.control_container = ttk.LabelFrame(self.scrollable_frame, text="Bot Control", padding="5")
        self.control_container.pack(fill=tk.X, pady=(0, 5))
    
    def _create_save_section(self):
        save_frame = ttk.Frame(self.scrollable_frame)
        save_frame.pack(fill=tk.X, pady=(15, 20))
        
        save_button = ttk.Button(
            save_frame, 
            text="Save Settings", 
            command=self._save_settings
        )
        save_button.pack(side=tk.RIGHT)
        
        ttk.Label(
            save_frame, 
            text="Settings are automatically saved when bot starts",
            foreground="#666666",
            font=("Arial", 9)
        ).pack(side=tk.LEFT)
    
    def _toggle_spell_settings(self):
        state = "normal" if self.spell_enabled_var.get() else "disabled"
        for child in self.spell_settings_frame.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Scale)):
                    widget.configure(state=state)
    
    def _load_settings(self):
        try:
            config = load_config()
            
            potion_keys = config.get("potion_keys", {})
            self.hp_key_var.set(potion_keys.get("health", "1"))
            self.mp_key_var.set(potion_keys.get("mana", "3"))
            self.sp_key_var.set(potion_keys.get("stamina", "2"))
            
            thresholds = config.get("thresholds", {})
            hp_thresh = thresholds.get("health", 50)
            mp_thresh = thresholds.get("mana", 30)
            sp_thresh = thresholds.get("stamina", 40)
            
            self.hp_threshold_var.set(hp_thresh)
            self.mp_threshold_var.set(mp_thresh)
            self.sp_threshold_var.set(sp_thresh)
            
            self.hp_thresh_label.config(text=f"{hp_thresh}%")
            self.mp_thresh_label.config(text=f"{mp_thresh}%")
            self.sp_thresh_label.config(text=f"{sp_thresh}%")
            
            self.scan_interval_var.set(config.get("scan_interval", 0.5))
            self.scan_label.config(text=f"{config.get('scan_interval', 0.5):.1f}s")
            
            self.debug_enabled_var.set(config.get("debug_enabled", False))
            
            spellcasting = config.get("spellcasting", {})
            self.spell_enabled_var.set(spellcasting.get("enabled", False))
            self.spell_key_var.set(spellcasting.get("key", "4"))
            spell_interval = spellcasting.get("interval", 3.0)
            self.spell_interval_var.set(spell_interval)
            self.interval_label.config(text=f"{spell_interval:.1f}s")
            
            self._toggle_spell_settings()
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    def _save_settings(self):
        return self.save_callback()
    
    def get_settings(self):
        settings = {
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
            "scan_interval": self.scan_interval_var.get(),
            "debug_enabled": self.debug_enabled_var.get(),
            "spellcasting": {
                "enabled": self.spell_enabled_var.get(),
                "key": self.spell_key_var.get(),
                "interval": self.spell_interval_var.get()
            }
        }
        
        return settings
    
    def set_settings(self, config):
        """Apply settings from configuration dictionary"""
        try:
            potion_keys = config.get("potion_keys", {})
            self.hp_key_var.set(potion_keys.get("health", "1"))
            self.mp_key_var.set(potion_keys.get("mana", "3"))
            self.sp_key_var.set(potion_keys.get("stamina", "2"))
            
            thresholds = config.get("thresholds", {})
            hp_thresh = thresholds.get("health", 50)
            mp_thresh = thresholds.get("mana", 30)
            sp_thresh = thresholds.get("stamina", 40)
            
            self.hp_threshold_var.set(hp_thresh)
            self.mp_threshold_var.set(mp_thresh)
            self.sp_threshold_var.set(sp_thresh)
            
            self.hp_thresh_label.config(text=f"{hp_thresh}%")
            self.mp_thresh_label.config(text=f"{mp_thresh}%")
            self.sp_thresh_label.config(text=f"{sp_thresh}%")
            
            self.scan_interval_var.set(config.get("scan_interval", 0.5))
            self.scan_label.config(text=f"{config.get('scan_interval', 0.5):.1f}s")
            
            self.debug_enabled_var.set(config.get("debug_enabled", False))
            
            spellcasting = config.get("spellcasting", {})
            self.spell_enabled_var.set(spellcasting.get("enabled", False))
            self.spell_key_var.set(spellcasting.get("key", "4"))
            spell_interval = spellcasting.get("interval", 3.0)
            self.spell_interval_var.set(spell_interval)
            self.interval_label.config(text=f"{spell_interval:.1f}s")
            
            self._toggle_spell_settings()
            
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")