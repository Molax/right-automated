"""
Improved Settings UI for the Priston Tale Potion Bot with simplified targeting
------------------------------------------------
This module contains the settings UI components with better use of space
and simplified targeting options focused on the target zone.
"""

import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger('PristonBot')

class SettingsUI:
    """Class that handles the settings UI with horizontal layout and slider controls"""
    
    def __init__(self, parent, save_callback):
        """
        Initialize the settings UI
        
        Args:
            parent: Parent frame to place UI elements
            save_callback: Function to call to save settings
        """
        self.parent = parent
        self.save_callback = save_callback
        
        # Create the UI
        self._create_ui()
        
    def _create_ui(self):
        """Create the UI components with horizontal layout"""
        # Create notebook (tabs) for settings categories
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Potion settings tab
        potion_tab = ttk.Frame(self.notebook)
        self.notebook.add(potion_tab, text="Potion Settings")
        
        # Spell settings tab
        spell_tab = ttk.Frame(self.notebook)
        self.notebook.add(spell_tab, text="Spell Settings")
        
        # Advanced settings tab
        adv_tab = ttk.Frame(self.notebook)
        self.notebook.add(adv_tab, text="Advanced")
        
        # Create potion settings
        self._create_potion_settings(potion_tab)
        
        # Create spell settings
        self._create_spell_settings(spell_tab)
        
        # Create advanced settings
        self._create_advanced_settings(adv_tab)
        
        # Save button at the bottom
        save_frame = ttk.Frame(self.parent)
        save_frame.pack(fill=tk.X, pady=5)
        
        self.save_button = tk.Button(
            save_frame,
            text="Save Configuration",
            command=self.save_callback,
            bg="#4CAF50",  # Green background
            fg="black",    # Black text for visibility
            font=("Arial", 10, "bold"),
            height=1
        )
        self.save_button.pack(fill=tk.X, pady=5)
    
    def _create_potion_settings(self, parent):
        """Create the potion settings UI with slider controls"""
        # Thresholds frame
        thresholds_frame = ttk.LabelFrame(parent, text="Potion Thresholds", padding=5)
        thresholds_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Brief help text
        ttk.Label(thresholds_frame, 
                 text="Set when potions should be used (percentage of bar remaining)").pack(
                     anchor=tk.W, pady=(0, 5))
        
        # Health threshold with slider
        hp_frame = ttk.Frame(thresholds_frame)
        hp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_frame, text="Health %:", width=12).pack(side=tk.LEFT)
        
        # Create a frame for the slider and value display
        hp_slider_frame = ttk.Frame(hp_frame)
        hp_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a variable to hold the slider value
        self.hp_threshold_var = tk.IntVar(value=50)
        
        # Create the slider
        self.hp_threshold = ttk.Scale(
            hp_slider_frame, 
            from_=1, 
            to=99, 
            orient=tk.HORIZONTAL, 
            variable=self.hp_threshold_var,
            command=self._update_hp_label
        )
        self.hp_threshold.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create a label to display the current value
        self.hp_value_label = ttk.Label(hp_slider_frame, text="50%", width=4)
        self.hp_value_label.pack(side=tk.LEFT)
        
        # Mana threshold with slider
        mp_frame = ttk.Frame(thresholds_frame)
        mp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_frame, text="Mana %:", width=12).pack(side=tk.LEFT)
        
        # Create a frame for the slider and value display
        mp_slider_frame = ttk.Frame(mp_frame)
        mp_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a variable to hold the slider value
        self.mp_threshold_var = tk.IntVar(value=30)
        
        # Create the slider
        self.mp_threshold = ttk.Scale(
            mp_slider_frame, 
            from_=1, 
            to=99, 
            orient=tk.HORIZONTAL, 
            variable=self.mp_threshold_var,
            command=self._update_mp_label
        )
        self.mp_threshold.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create a label to display the current value
        self.mp_value_label = ttk.Label(mp_slider_frame, text="30%", width=4)
        self.mp_value_label.pack(side=tk.LEFT)
        
        # Stamina threshold with slider
        sp_frame = ttk.Frame(thresholds_frame)
        sp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_frame, text="Stamina %:", width=12).pack(side=tk.LEFT)
        
        # Create a frame for the slider and value display
        sp_slider_frame = ttk.Frame(sp_frame)
        sp_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a variable to hold the slider value
        self.sp_threshold_var = tk.IntVar(value=40)
        
        # Create the slider
        self.sp_threshold = ttk.Scale(
            sp_slider_frame, 
            from_=1, 
            to=99, 
            orient=tk.HORIZONTAL, 
            variable=self.sp_threshold_var,
            command=self._update_sp_label
        )
        self.sp_threshold.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create a label to display the current value
        self.sp_value_label = ttk.Label(sp_slider_frame, text="40%", width=4)
        self.sp_value_label.pack(side=tk.LEFT)
        
        # Potion keys frame
        keys_frame = ttk.LabelFrame(parent, text="Potion Keys", padding=5)
        keys_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Brief help text
        ttk.Label(keys_frame, 
                 text="Set which keyboard keys are used for each potion type").pack(
                     anchor=tk.W, pady=(0, 5))
        
        # Two columns for keys
        key_frame = ttk.Frame(keys_frame)
        key_frame.pack(fill=tk.X, pady=5)
        
        # Health key
        hp_key_frame = ttk.Frame(key_frame)
        hp_key_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_key_frame, text="Health Key:", width=12).pack(side=tk.LEFT)
        self.hp_key = ttk.Combobox(hp_key_frame, values=list("123456789"), width=3)
        self.hp_key.set("1")
        self.hp_key.pack(side=tk.LEFT)
        
        # Mana key
        mp_key_frame = ttk.Frame(key_frame)
        mp_key_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_key_frame, text="Mana Key:", width=12).pack(side=tk.LEFT)
        self.mp_key = ttk.Combobox(mp_key_frame, values=list("123456789"), width=3)
        self.mp_key.set("3")
        self.mp_key.pack(side=tk.LEFT)
        
        # Stamina key
        sp_key_frame = ttk.Frame(key_frame)
        sp_key_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_key_frame, text="Stamina Key:", width=12).pack(side=tk.LEFT)
        self.sp_key = ttk.Combobox(sp_key_frame, values=list("123456789"), width=3)
        self.sp_key.set("2")
        self.sp_key.pack(side=tk.LEFT)
    
    def _update_hp_label(self, value):
        """Update the health threshold label when the slider is moved"""
        # Round to integer
        value = int(float(value))
        self.hp_value_label.config(text=f"{value}%")
    
    def _update_mp_label(self, value):
        """Update the mana threshold label when the slider is moved"""
        # Round to integer
        value = int(float(value))
        self.mp_value_label.config(text=f"{value}%")
    
    def _update_sp_label(self, value):
        """Update the stamina threshold label when the slider is moved"""
        # Round to integer
        value = int(float(value))
        self.sp_value_label.config(text=f"{value}%")
    
    def _create_spell_settings(self, parent):
        """Create the spell settings UI"""
        # Spellcasting frame
        spell_frame = ttk.LabelFrame(parent, text="Auto Spellcasting", padding=5)
        spell_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Brief help text
        ttk.Label(spell_frame, 
                 text="Configure automatic spell casting at regular intervals").pack(
                     anchor=tk.W, pady=(0, 5))
        
        # Enable spellcasting
        enable_frame = ttk.Frame(spell_frame)
        enable_frame.pack(fill=tk.X, pady=5)
        
        self.spellcast_enabled = tk.BooleanVar(value=False)
        enable_check = ttk.Checkbutton(
            enable_frame, 
            text="Enable Auto Spellcasting", 
            variable=self.spellcast_enabled
        )
        enable_check.pack(anchor=tk.W)
        
        # Spell key
        key_frame = ttk.Frame(spell_frame)
        key_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(key_frame, text="Spell Key:", width=12).pack(side=tk.LEFT)
        self.spell_key = ttk.Combobox(
            key_frame, 
            values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"], 
            width=5
        )
        self.spell_key.set("F1")
        self.spell_key.pack(side=tk.LEFT)
        
        # Spell interval with slider
        interval_frame = ttk.Frame(spell_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(interval_frame, text="Cast Interval:", width=12).pack(side=tk.LEFT)
        
        # Create a frame for the slider and value display
        interval_slider_frame = ttk.Frame(interval_frame)
        interval_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a variable to hold the slider value
        self.spell_interval_var = tk.DoubleVar(value=1.2)
        
        # Create the slider
        self.spell_interval = ttk.Scale(
            interval_slider_frame, 
            from_=0.5, 
            to=10.0, 
            orient=tk.HORIZONTAL, 
            variable=self.spell_interval_var,
            command=self._update_interval_label
        )
        self.spell_interval.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create a label to display the current value
        self.interval_value_label = ttk.Label(interval_slider_frame, text="1.2s", width=5)
        self.interval_value_label.pack(side=tk.LEFT)
        
        # Monster Target Zone frame
        target_frame = ttk.LabelFrame(parent, text="Monster Target Zone", padding=5)
        target_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(target_frame, 
                 text="Define an area where monsters typically appear for better targeting").pack(
                     anchor=tk.W, pady=(0, 5))
                     
        # Use target zone checkbox
        use_zone_frame = ttk.Frame(target_frame)
        use_zone_frame.pack(fill=tk.X, pady=2)
        
        self.use_target_zone_var = tk.BooleanVar(value=True)
        use_zone_check = ttk.Checkbutton(
            use_zone_frame,
            text="Use target zone for spell targeting",
            variable=self.use_target_zone_var
        )
        use_zone_check.pack(anchor=tk.W)
        
        # Target zone status
        status_frame = ttk.Frame(target_frame)
        status_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(status_frame, text="Status:", width=12).pack(side=tk.LEFT)
        self.target_zone_var = tk.StringVar(value="Not Configured")
        ttk.Label(status_frame, textvariable=self.target_zone_var).pack(side=tk.LEFT)
        
        # Select button
        select_button = ttk.Button(
            target_frame, 
            text="Select Monster Target Zone", 
            command=self._select_target_zone
        )
        select_button.pack(fill=tk.X, pady=5)
        
        # Target points count slider
        points_frame = ttk.Frame(target_frame)
        points_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(points_frame, text="Target Points:", width=12).pack(side=tk.LEFT)
        
        # Create a frame for the slider and value display
        points_slider_frame = ttk.Frame(points_frame)
        points_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a variable to hold the slider value
        self.target_points_var = tk.IntVar(value=8)
        
        # Create the slider
        self.target_points = ttk.Scale(
            points_slider_frame, 
            from_=4, 
            to=16, 
            orient=tk.HORIZONTAL, 
            variable=self.target_points_var,
            command=self._update_points_label
        )
        self.target_points.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create a label to display the current value
        self.points_value_label = ttk.Label(points_slider_frame, text="8 points", width=8)
        self.points_value_label.pack(side=tk.LEFT)
        
        # Additional info
        ttk.Label(target_frame, 
                 text="Character is assumed to be in the center of game window").pack(
                     anchor=tk.W, pady=(5, 0))
    
    def _update_interval_label(self, value):
        """Update the spell interval label when the slider is moved"""
        # Round to 1 decimal place
        value = round(float(value), 1)
        self.interval_value_label.config(text=f"{value}s")
    
    def _update_points_label(self, value):
        """Update the target points label when the slider is moved"""
        # Round to integer
        value = int(float(value))
        self.points_value_label.config(text=f"{value} points")

    def _select_target_zone(self):
        """Launch the target zone selector"""
        from app.target_zone_selector import TargetZoneSelector
        target_selector = TargetZoneSelector(self.parent.winfo_toplevel())
        target_selector.num_target_points = self.target_points_var.get()
        target_selector.start_selection()
        
        # Check if selection was completed
        if target_selector.is_configured:
            self.target_zone_var.set(f"Configured ({len(target_selector.target_points)} points)")
            self.target_zone_selector = target_selector
            
            # Store the target zone data in settings
            settings = self.get_settings()
            if "target_zone" not in settings["spellcasting"]:
                settings["spellcasting"]["target_zone"] = {}
                
            settings["spellcasting"]["target_zone"]["x1"] = target_selector.x1
            settings["spellcasting"]["target_zone"]["y1"] = target_selector.y1
            settings["spellcasting"]["target_zone"]["x2"] = target_selector.x2
            settings["spellcasting"]["target_zone"]["y2"] = target_selector.y2
            settings["spellcasting"]["target_zone"]["points"] = target_selector.get_serializable_points()
            
            # Save configuration
            if callable(self.save_callback):
                self.save_callback()
    
    def _create_advanced_settings(self, parent):
        """Create the advanced settings UI with sliders"""
        # Scanning parameters
        scan_frame = ttk.LabelFrame(parent, text="Scanning Parameters", padding=5)
        scan_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Brief help text
        ttk.Label(scan_frame, 
                 text="Configure how frequently the bot checks bar values").pack(
                     anchor=tk.W, pady=(0, 5))
        
        # Scan interval with slider
        interval_frame = ttk.Frame(scan_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(interval_frame, text="Scan Interval:", width=12).pack(side=tk.LEFT)
        
        # Create a frame for the slider and value display
        scan_slider_frame = ttk.Frame(interval_frame)
        scan_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a variable to hold the slider value
        self.scan_interval_var = tk.DoubleVar(value=0.5)
        
        # Create the slider
        self.scan_interval = ttk.Scale(
            scan_slider_frame, 
            from_=0.1, 
            to=2.0, 
            orient=tk.HORIZONTAL, 
            variable=self.scan_interval_var,
            command=self._update_scan_label
        )
        self.scan_interval.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create a label to display the current value
        self.scan_value_label = ttk.Label(scan_slider_frame, text="0.5s", width=5)
        self.scan_value_label.pack(side=tk.LEFT)
        
        # Potion cooldown with slider
        cooldown_frame = ttk.Frame(scan_frame)
        cooldown_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(cooldown_frame, text="Potion Cooldown:", width=12).pack(side=tk.LEFT)
        
        # Create a frame for the slider and value display
        cooldown_slider_frame = ttk.Frame(cooldown_frame)
        cooldown_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create a variable to hold the slider value
        self.potion_cooldown_var = tk.DoubleVar(value=3.0)
        
        # Create the slider
        self.potion_cooldown = ttk.Scale(
            cooldown_slider_frame, 
            from_=1.0, 
            to=10.0, 
            orient=tk.HORIZONTAL, 
            variable=self.potion_cooldown_var,
            command=self._update_cooldown_label
        )
        self.potion_cooldown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create a label to display the current value
        self.cooldown_value_label = ttk.Label(cooldown_slider_frame, text="3.0s", width=5)
        self.cooldown_value_label.pack(side=tk.LEFT)
        
        # Debug options
        debug_frame = ttk.LabelFrame(parent, text="Debug Options", padding=5)
        debug_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Debug mode
        self.debug_var = tk.BooleanVar(value=True)
        debug_check = ttk.Checkbutton(
            debug_frame, 
            text="Enable Debug Mode (saves screenshots and logs extra information)", 
            variable=self.debug_var
        )
        debug_check.pack(anchor=tk.W, pady=5)
    
    def _update_scan_label(self, value):
        """Update the scan interval label when the slider is moved"""
        # Round to 1 decimal place
        value = round(float(value), 1)
        self.scan_value_label.config(text=f"{value}s")
    
    def _update_cooldown_label(self, value):
        """Update the potion cooldown label when the slider is moved"""
        # Round to 1 decimal place
        value = round(float(value), 1)
        self.cooldown_value_label.config(text=f"{value}s")
    
    def get_settings(self):
        """Get current settings as a dictionary"""
        settings = {
            "thresholds": {
                "health": float(self.hp_threshold_var.get()),
                "mana": float(self.mp_threshold_var.get()),
                "stamina": float(self.sp_threshold_var.get())
            },
            "potion_keys": {
                "health": self.hp_key.get(),
                "mana": self.mp_key.get(),
                "stamina": self.sp_key.get()
            },
            "spellcasting": {
                "enabled": self.spellcast_enabled.get(),
                "spell_key": self.spell_key.get(),
                "spell_interval": float(self.spell_interval_var.get()),
                "use_target_zone": self.use_target_zone_var.get(),
                "target_points_count": int(self.target_points_var.get()),
                "target_zone": {}
            },
            "scan_interval": float(self.scan_interval_var.get()),
            "potion_cooldown": float(self.potion_cooldown_var.get()),
            "debug_enabled": self.debug_var.get()
        }
        
        # Add target zone if available
        if hasattr(self, 'target_zone_selector') and self.target_zone_selector and self.target_zone_selector.is_setup():
            settings["spellcasting"]["target_zone"] = {
                "x1": self.target_zone_selector.x1,
                "y1": self.target_zone_selector.y1,
                "x2": self.target_zone_selector.x2,
                "y2": self.target_zone_selector.y2,
                "points": self.target_zone_selector.get_serializable_points()
            }
        
        return settings
    
    def set_settings(self, settings):
        """Set settings from a dictionary"""
        # Thresholds
        thresholds = settings.get("thresholds", {})
        self.hp_threshold_var.set(thresholds.get("health", 50))
        self.mp_threshold_var.set(thresholds.get("mana", 30))
        self.sp_threshold_var.set(thresholds.get("stamina", 40))
        
        # Update labels
        self._update_hp_label(self.hp_threshold_var.get())
        self._update_mp_label(self.mp_threshold_var.get())
        self._update_sp_label(self.sp_threshold_var.get())
        
        # Potion keys
        potion_keys = settings.get("potion_keys", {})
        self.hp_key.set(potion_keys.get("health", "1"))
        self.mp_key.set(potion_keys.get("mana", "3"))
        self.sp_key.set(potion_keys.get("stamina", "2"))
        
        # Spellcasting
        spellcasting = settings.get("spellcasting", {})
        self.spellcast_enabled.set(spellcasting.get("enabled", False))
        self.spell_key.set(spellcasting.get("spell_key", "F1"))
        self.spell_interval_var.set(spellcasting.get("spell_interval", 1.2))
        self._update_interval_label(self.spell_interval_var.get())
        
        # Target zone
        self.use_target_zone_var.set(spellcasting.get("use_target_zone", True))
        self.target_points_var.set(spellcasting.get("target_points_count", 8))
        self._update_points_label(self.target_points_var.get())
        
        # Target zone settings
        if "target_zone" in spellcasting and spellcasting["target_zone"]:
            target_zone = spellcasting["target_zone"]
            
            # Check if we have all needed coordinates
            if all(k in target_zone for k in ["x1", "y1", "x2", "y2"]):
                # Create a target zone selector and configure it
                from app.target_zone_selector import TargetZoneSelector
                self.target_zone_selector = TargetZoneSelector(self.parent.winfo_toplevel())
                
                # Configure with points if they're available
                if "points" in target_zone and target_zone["points"]:
                    self.target_zone_selector.configure_from_saved(
                        target_zone["x1"],
                        target_zone["y1"],
                        target_zone["x2"],
                        target_zone["y2"],
                        target_zone["points"]
                    )
                else:
                    self.target_zone_selector.configure_from_saved(
                        target_zone["x1"],
                        target_zone["y1"],
                        target_zone["x2"],
                        target_zone["y2"]
                    )
                
                # Update status
                self.target_zone_var.set(f"Configured ({len(self.target_zone_selector.target_points)} points)")
            else:
                self.target_zone_var.set("Not Configured")
        else:
            self.target_zone_var.set("Not Configured")
        
        # Other settings
        self.scan_interval_var.set(settings.get("scan_interval", 0.5))
        self._update_scan_label(self.scan_interval_var.get())
        
        self.potion_cooldown_var.set(settings.get("potion_cooldown", 3.0))
        self._update_cooldown_label(self.potion_cooldown_var.get())
        
        self.debug_var.set(settings.get("debug_enabled", True))