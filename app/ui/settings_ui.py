"""
Fixed Settings UI for the Priston Tale Potion Bot
------------------------------------------------
This module provides a clean, organized settings interface.
"""

import tkinter as tk
from tkinter import ttk
import logging
from app.config import load_config

logger = logging.getLogger('PristonBot')

class SettingsUI:
    """Settings UI component with proper layout and validation"""
    
    def __init__(self, parent, save_callback):
        """
        Initialize the settings UI
        
        Args:
            parent: Parent widget
            save_callback: Function to call when settings should be saved
        """
        self.parent = parent
        self.save_callback = save_callback
        self.logger = logging.getLogger('PristonBot')
        
        # Configure parent for scrolling if needed
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Create scrollable canvas
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
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create the settings interface
        self._create_settings_ui()
        
        # Load current settings
        self._load_settings()
        
        logger.info("Settings UI initialized")
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _create_settings_ui(self):
        """Create the settings user interface"""
        # Potion Keys Section
        self._create_potion_keys_section()
        
        # Thresholds Section
        self._create_thresholds_section()
        
        # Bot Behavior Section
        self._create_behavior_section()
        
        # Spellcasting Section
        self._create_spellcasting_section()
        
        # Save Button
        self._create_save_section()
    
    def _create_potion_keys_section(self):
        """Create the potion keys configuration section"""
        keys_frame = ttk.LabelFrame(self.scrollable_frame, text="Potion Hotkeys", padding="10")
        keys_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Health potion key
        hp_frame = ttk.Frame(keys_frame)
        hp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_frame, text="Health Potion Key:", width=20).pack(side=tk.LEFT)
        self.hp_key_var = tk.StringVar(value="1")
        hp_entry = ttk.Entry(hp_frame, textvariable=self.hp_key_var, width=5)
        hp_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(hp_frame, text="(Default: 1)", foreground="#666666").pack(side=tk.LEFT, padx=(5, 0))
        
        # Mana potion key
        mp_frame = ttk.Frame(keys_frame)
        mp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_frame, text="Mana Potion Key:", width=20).pack(side=tk.LEFT)
        self.mp_key_var = tk.StringVar(value="3")
        mp_entry = ttk.Entry(mp_frame, textvariable=self.mp_key_var, width=5)
        mp_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(mp_frame, text="(Default: 3)", foreground="#666666").pack(side=tk.LEFT, padx=(5, 0))
        
        # Stamina potion key
        sp_frame = ttk.Frame(keys_frame)
        sp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_frame, text="Stamina Potion Key:", width=20).pack(side=tk.LEFT)
        self.sp_key_var = tk.StringVar(value="2")
        sp_entry = ttk.Entry(sp_frame, textvariable=self.sp_key_var, width=5)
        sp_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(sp_frame, text="(Default: 2)", foreground="#666666").pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_thresholds_section(self):
        """Create the threshold configuration section"""
        thresholds_frame = ttk.LabelFrame(self.scrollable_frame, text="Usage Thresholds (%)", padding="10")
        thresholds_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Health threshold
        hp_thresh_frame = ttk.Frame(thresholds_frame)
        hp_thresh_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_thresh_frame, text="Health Threshold:", width=20).pack(side=tk.LEFT)
        self.hp_threshold_var = tk.IntVar(value=50)
        hp_thresh_scale = ttk.Scale(
            hp_thresh_frame, 
            from_=10, 
            to=95, 
            variable=self.hp_threshold_var, 
            orient=tk.HORIZONTAL,
            length=150
        )
        hp_thresh_scale.pack(side=tk.LEFT, padx=(5, 5))
        self.hp_thresh_label = ttk.Label(hp_thresh_frame, text="50%", width=5)
        self.hp_thresh_label.pack(side=tk.LEFT)
        hp_thresh_scale.configure(command=lambda v: self.hp_thresh_label.config(text=f"{int(float(v))}%"))
        
        # Mana threshold
        mp_thresh_frame = ttk.Frame(thresholds_frame)
        mp_thresh_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_thresh_frame, text="Mana Threshold:", width=20).pack(side=tk.LEFT)
        self.mp_threshold_var = tk.IntVar(value=30)
        mp_thresh_scale = ttk.Scale(
            mp_thresh_frame, 
            from_=10, 
            to=95, 
            variable=self.mp_threshold_var, 
            orient=tk.HORIZONTAL,
            length=150
        )
        mp_thresh_scale.pack(side=tk.LEFT, padx=(5, 5))
        self.mp_thresh_label = ttk.Label(mp_thresh_frame, text="30%", width=5)
        self.mp_thresh_label.pack(side=tk.LEFT)
        mp_thresh_scale.configure(command=lambda v: self.mp_thresh_label.config(text=f"{int(float(v))}%"))
        
        # Stamina threshold
        sp_thresh_frame = ttk.Frame(thresholds_frame)
        sp_thresh_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_thresh_frame, text="Stamina Threshold:", width=20).pack(side=tk.LEFT)
        self.sp_threshold_var = tk.IntVar(value=40)
        sp_thresh_scale = ttk.Scale(
            sp_thresh_frame, 
            from_=10, 
            to=95, 
            variable=self.sp_threshold_var, 
            orient=tk.HORIZONTAL,
            length=150
        )
        sp_thresh_scale.pack(side=tk.LEFT, padx=(5, 5))
        self.sp_thresh_label = ttk.Label(sp_thresh_frame, text="40%", width=5)
        self.sp_thresh_label.pack(side=tk.LEFT)
        sp_thresh_scale.configure(command=lambda v: self.sp_thresh_label.config(text=f"{int(float(v))}%"))
    
    def _create_behavior_section(self):
        """Create the bot behavior configuration section"""
        behavior_frame = ttk.LabelFrame(self.scrollable_frame, text="Bot Behavior", padding="10")
        behavior_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scan interval
        scan_frame = ttk.Frame(behavior_frame)
        scan_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(scan_frame, text="Scan Interval (seconds):", width=20).pack(side=tk.LEFT)
        self.scan_interval_var = tk.DoubleVar(value=0.5)
        scan_scale = ttk.Scale(
            scan_frame, 
            from_=0.1, 
            to=2.0, 
            variable=self.scan_interval_var, 
            orient=tk.HORIZONTAL,
            length=150
        )
        scan_scale.pack(side=tk.LEFT, padx=(5, 5))
        self.scan_label = ttk.Label(scan_frame, text="0.5s", width=5)
        self.scan_label.pack(side=tk.LEFT)
        scan_scale.configure(command=lambda v: self.scan_label.config(text=f"{float(v):.1f}s"))
        
        # Debug mode
        debug_frame = ttk.Frame(behavior_frame)
        debug_frame.pack(fill=tk.X, pady=5)
        
        self.debug_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            debug_frame, 
            text="Enable debug mode (saves detection images)", 
            variable=self.debug_var
        ).pack(side=tk.LEFT)
    
    def _create_spellcasting_section(self):
        """Create the spellcasting configuration section"""
        spell_frame = ttk.LabelFrame(self.scrollable_frame, text="Spellcasting (Optional)", padding="10")
        spell_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Enable spellcasting
        enable_frame = ttk.Frame(spell_frame)
        enable_frame.pack(fill=tk.X, pady=2)
        
        self.spell_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            enable_frame, 
            text="Enable automatic spellcasting", 
            variable=self.spell_enabled_var,
            command=self._toggle_spell_settings
        ).pack(side=tk.LEFT)
        
        # Spell settings container
        self.spell_settings_frame = ttk.Frame(spell_frame)
        self.spell_settings_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Spell key
        key_frame = ttk.Frame(self.spell_settings_frame)
        key_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(key_frame, text="Spell Key:", width=15).pack(side=tk.LEFT)
        self.spell_key_var = tk.StringVar(value="F5")
        spell_key_entry = ttk.Entry(key_frame, textvariable=self.spell_key_var, width=5)
        spell_key_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(key_frame, text="(Default: F5)", foreground="#666666").pack(side=tk.LEFT, padx=(5, 0))
        
        # Spell interval
        interval_frame = ttk.Frame(self.spell_settings_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(interval_frame, text="Cast Interval:", width=15).pack(side=tk.LEFT)
        self.spell_interval_var = tk.DoubleVar(value=3.0)
        interval_scale = ttk.Scale(
            interval_frame, 
            from_=1.0, 
            to=10.0, 
            variable=self.spell_interval_var, 
            orient=tk.HORIZONTAL,
            length=120
        )
        interval_scale.pack(side=tk.LEFT, padx=(5, 5))
        self.interval_label = ttk.Label(interval_frame, text="3.0s", width=5)
        self.interval_label.pack(side=tk.LEFT)
        interval_scale.configure(command=lambda v: self.interval_label.config(text=f"{float(v):.1f}s"))
        
        # Initially disable spell settings
        self._toggle_spell_settings()
    
    def _create_save_section(self):
        """Create the save button section"""
        save_frame = ttk.Frame(self.scrollable_frame)
        save_frame.pack(fill=tk.X, pady=(10, 0))
        
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
        """Enable or disable spell settings based on checkbox"""
        state = "normal" if self.spell_enabled_var.get() else "disabled"
        for child in self.spell_settings_frame.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Scale)):
                    widget.configure(state=state)
    
    def _load_settings(self):
        """Load settings from configuration file"""
        try:
            config = load_config()
            
            # Load potion keys
            potion_keys = config.get("potion_keys", {})
            self.hp_key_var.set(potion_keys.get("health", "1"))
            self.mp_key_var.set(potion_keys.get("mana", "3"))
            self.sp_key_var.set(potion_keys.get("stamina", "2"))
            
            # Load thresholds
            thresholds = config.get("thresholds", {})
            hp_thresh = thresholds.get("health", 50)
            mp_thresh = thresholds.get("mana", 30)
            sp_thresh = thresholds.get("stamina", 40)
            
            self.hp_threshold_var.set(hp_thresh)
            self.mp_threshold_var.set(mp_thresh)
            self.sp_threshold_var.set(sp_thresh)
            
            # Update labels
            self.hp_thresh_label.config(text=f"{hp_thresh}%")
            self.mp_thresh_label.config(text=f"{mp_thresh}%")
            self.sp_thresh_label.config(text=f"{sp_thresh}%")
            
            # Load behavior settings
            self.scan_interval_var.set(config.get("scan_interval", 0.5))
            self.scan_label.config(text=f"{config.get('scan_interval', 0.5):.1f}s")
            self.debug_var.set(config.get("debug_enabled", True))
            
            # Load spellcasting settings
            spellcasting = config.get("spellcasting", {})
            self.spell_enabled_var.set(spellcasting.get("enabled", False))
            self.spell_key_var.set(spellcasting.get("spell_key", "F5"))
            
            spell_interval = spellcasting.get("spell_interval", 3.0)
            self.spell_interval_var.set(spell_interval)
            self.interval_label.config(text=f"{spell_interval:.1f}s")
            
            # Update spell settings state
            self._toggle_spell_settings()
            
            logger.info("Settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}", exc_info=True)
    
    def _save_settings(self):
        """Save current settings"""
        try:
            self.save_callback()
            logger.info("Settings saved via save button")
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
    
    def get_settings(self):
        """Get current settings as a dictionary"""
        try:
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
                "scan_interval": self.scan_interval_var.get(),
                "debug_enabled": self.debug_var.get(),
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
                }
            }
        except Exception as e:
            logger.error(f"Error getting settings: {e}", exc_info=True)
            return {}
    
    def set_settings(self, config):
        """Set settings from configuration dictionary"""
        try:
            # Set potion keys
            potion_keys = config.get("potion_keys", {})
            if "health" in potion_keys:
                self.hp_key_var.set(potion_keys["health"])
            if "mana" in potion_keys:
                self.mp_key_var.set(potion_keys["mana"])
            if "stamina" in potion_keys:
                self.sp_key_var.set(potion_keys["stamina"])
            
            # Set thresholds
            thresholds = config.get("thresholds", {})
            if "health" in thresholds:
                hp_thresh = thresholds["health"]
                self.hp_threshold_var.set(hp_thresh)
                self.hp_thresh_label.config(text=f"{hp_thresh}%")
            if "mana" in thresholds:
                mp_thresh = thresholds["mana"]
                self.mp_threshold_var.set(mp_thresh)
                self.mp_thresh_label.config(text=f"{mp_thresh}%")
            if "stamina" in thresholds:
                sp_thresh = thresholds["stamina"]
                self.sp_threshold_var.set(sp_thresh)
                self.sp_thresh_label.config(text=f"{sp_thresh}%")
            
            # Set behavior settings
            if "scan_interval" in config:
                scan_interval = config["scan_interval"]
                self.scan_interval_var.set(scan_interval)
                self.scan_label.config(text=f"{scan_interval:.1f}s")
            if "debug_enabled" in config:
                self.debug_var.set(config["debug_enabled"])
            
            # Set spellcasting settings
            spellcasting = config.get("spellcasting", {})
            if "enabled" in spellcasting:
                self.spell_enabled_var.set(spellcasting["enabled"])
            if "spell_key" in spellcasting:
                self.spell_key_var.set(spellcasting["spell_key"])
            if "spell_interval" in spellcasting:
                spell_interval = spellcasting["spell_interval"]
                self.spell_interval_var.set(spell_interval)
                self.interval_label.config(text=f"{spell_interval:.1f}s")
            
            # Update spell settings state
            self._toggle_spell_settings()
            
            logger.info("Settings applied successfully")
            
        except Exception as e:
            logger.error(f"Error setting settings: {e}", exc_info=True)