import tkinter as tk
from tkinter import ttk

class ModernSettings:
    def __init__(self, app):
        self.app = app
        self.create_settings_panel()
    
    def create_settings_panel(self):
        settings_card = ttk.Frame(self.app.settings_frame, style='Card.TFrame', padding=15)
        settings_card.pack(fill=tk.BOTH, expand=True)
        settings_card.grid_rowconfigure(1, weight=1)
        settings_card.grid_rowconfigure(2, weight=0)
        
        title_label = ttk.Label(settings_card, text="Bot Settings", style='Subtitle.TLabel')
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Scrollable settings content
        canvas = tk.Canvas(settings_card, bg="#3d3d3d", highlightthickness=0)
        scrollbar = ttk.Scrollbar(settings_card, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#3d3d3d")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))
        
        # Create all settings sections
        self.create_potion_keys_section(scrollable_frame)
        self.create_potion_thresholds_section(scrollable_frame)
        self.create_bot_behavior_section(scrollable_frame)
        self.create_spellcasting_section(scrollable_frame)
        
        # Store settings card for controls
        self.app.settings_card = settings_card
    
    def create_potion_keys_section(self, parent):
        section_frame = tk.LabelFrame(parent, text="Potion Keys", 
                                    bg="#3d3d3d", fg="#ffffff", 
                                    font=('Segoe UI', 10, 'bold'))
        section_frame.pack(fill=tk.X, padx=5, pady=(0, 8))
        
        # Compact horizontal layout
        keys_frame = tk.Frame(section_frame, bg="#3d3d3d")
        keys_frame.pack(fill=tk.X, padx=8, pady=8)
        keys_frame.grid_columnconfigure(1, weight=1)
        keys_frame.grid_columnconfigure(3, weight=1)
        keys_frame.grid_columnconfigure(5, weight=1)
        
        # Health key
        tk.Label(keys_frame, text="HP:", bg="#3d3d3d", fg="#dc3545",
                font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky="e", padx=(0, 5))
        
        self.hp_key_var = tk.StringVar(value="1")
        hp_combo = ttk.Combobox(keys_frame, textvariable=self.hp_key_var, 
                               values=["1", "2", "3"], state="readonly", width=3)
        hp_combo.grid(row=0, column=1, sticky="w", padx=(0, 15))
        
        # Mana key
        tk.Label(keys_frame, text="MP:", bg="#3d3d3d", fg="#007acc",
                font=('Segoe UI', 9, 'bold')).grid(row=0, column=2, sticky="e", padx=(0, 5))
        
        self.mp_key_var = tk.StringVar(value="3")
        mp_combo = ttk.Combobox(keys_frame, textvariable=self.mp_key_var,
                               values=["1", "2", "3"], state="readonly", width=3)
        mp_combo.grid(row=0, column=3, sticky="w", padx=(0, 15))
        
        # Stamina key
        tk.Label(keys_frame, text="SP:", bg="#3d3d3d", fg="#28a745",
                font=('Segoe UI', 9, 'bold')).grid(row=0, column=4, sticky="e", padx=(0, 5))
        
        self.sp_key_var = tk.StringVar(value="2")
        sp_combo = ttk.Combobox(keys_frame, textvariable=self.sp_key_var,
                               values=["1", "2", "3"], state="readonly", width=3)
        sp_combo.grid(row=0, column=5, sticky="w")
    
    def create_potion_thresholds_section(self, parent):
        section_frame = tk.LabelFrame(parent, text="Potion Thresholds", 
                                    bg="#3d3d3d", fg="#ffffff", 
                                    font=('Segoe UI', 10, 'bold'))
        section_frame.pack(fill=tk.X, padx=5, pady=(0, 8))
        
        # Health threshold
        hp_frame = tk.Frame(section_frame, bg="#3d3d3d")
        hp_frame.pack(fill=tk.X, padx=8, pady=3)
        
        tk.Label(hp_frame, text="Health:", bg="#3d3d3d", fg="#dc3545",
                font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        
        self.hp_threshold = tk.Scale(hp_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                   bg="#3d3d3d", fg="#ffffff", troughcolor="#2d2d2d",
                                   highlightthickness=0, activebackground="#dc3545")
        self.hp_threshold.set(50)
        self.hp_threshold.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 5))
        
        self.hp_threshold_label = tk.Label(hp_frame, text="50.0%", bg="#3d3d3d", fg="#dc3545",
                                         font=('Segoe UI', 9, 'bold'))
        self.hp_threshold_label.pack(side=tk.RIGHT)
        
        self.hp_threshold.bind("<Motion>", lambda e: self.update_threshold_label(self.hp_threshold, self.hp_threshold_label))
        
        # Mana threshold
        mp_frame = tk.Frame(section_frame, bg="#3d3d3d")
        mp_frame.pack(fill=tk.X, padx=8, pady=3)
        
        tk.Label(mp_frame, text="Mana:", bg="#3d3d3d", fg="#007acc",
                font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        
        self.mp_threshold = tk.Scale(mp_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                   bg="#3d3d3d", fg="#ffffff", troughcolor="#2d2d2d",
                                   highlightthickness=0, activebackground="#007acc")
        self.mp_threshold.set(50)
        self.mp_threshold.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 5))
        
        self.mp_threshold_label = tk.Label(mp_frame, text="50.0%", bg="#3d3d3d", fg="#007acc",
                                         font=('Segoe UI', 9, 'bold'))
        self.mp_threshold_label.pack(side=tk.RIGHT)
        
        self.mp_threshold.bind("<Motion>", lambda e: self.update_threshold_label(self.mp_threshold, self.mp_threshold_label))
        
        # Stamina threshold
        sp_frame = tk.Frame(section_frame, bg="#3d3d3d")
        sp_frame.pack(fill=tk.X, padx=8, pady=3)
        
        tk.Label(sp_frame, text="Stamina:", bg="#3d3d3d", fg="#28a745",
                font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        
        self.sp_threshold = tk.Scale(sp_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                   bg="#3d3d3d", fg="#ffffff", troughcolor="#2d2d2d",
                                   highlightthickness=0, activebackground="#28a745")
        self.sp_threshold.set(50)
        self.sp_threshold.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 5))
        
        self.sp_threshold_label = tk.Label(sp_frame, text="50.0%", bg="#3d3d3d", fg="#28a745",
                                         font=('Segoe UI', 9, 'bold'))
        self.sp_threshold_label.pack(side=tk.RIGHT)
        
        self.sp_threshold.bind("<Motion>", lambda e: self.update_threshold_label(self.sp_threshold, self.sp_threshold_label))
    
    def create_bot_behavior_section(self, parent):
        section_frame = tk.LabelFrame(parent, text="Bot Behavior", 
                                    bg="#3d3d3d", fg="#ffffff", 
                                    font=('Segoe UI', 10, 'bold'))
        section_frame.pack(fill=tk.X, padx=5, pady=(0, 8))
        
        # Scan interval
        scan_frame = tk.Frame(section_frame, bg="#3d3d3d")
        scan_frame.pack(fill=tk.X, padx=8, pady=5)
        
        tk.Label(scan_frame, text="Scan Interval:", bg="#3d3d3d", fg="#ffffff",
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        self.scan_interval = tk.Scale(scan_frame, from_=0.1, to=2.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, bg="#3d3d3d", fg="#ffffff",
                                    troughcolor="#2d2d2d", highlightthickness=0)
        self.scan_interval.set(0.5)
        self.scan_interval.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 5))
        
        self.scan_interval_label = tk.Label(scan_frame, text="0.5s", bg="#3d3d3d", fg="#ffffff",
                                          font=('Segoe UI', 9))
        self.scan_interval_label.pack(side=tk.RIGHT)
        
        self.scan_interval.bind("<Motion>", lambda e: self.update_scan_interval_label())
        
        # Debug mode
        debug_frame = tk.Frame(section_frame, bg="#3d3d3d")
        debug_frame.pack(fill=tk.X, padx=8, pady=3)
        
        self.debug_var = tk.BooleanVar()
        debug_check = tk.Checkbutton(debug_frame, text="Enable debug mode",
                                   variable=self.debug_var, bg="#3d3d3d", fg="#ffffff",
                                   selectcolor="#2d2d2d", activebackground="#3d3d3d",
                                   activeforeground="#ffffff", font=('Segoe UI', 9))
        debug_check.pack(side=tk.LEFT)
    
    def create_spellcasting_section(self, parent):
        section_frame = tk.LabelFrame(parent, text="Spellcasting", 
                                    bg="#3d3d3d", fg="#ffffff", 
                                    font=('Segoe UI', 10, 'bold'))
        section_frame.pack(fill=tk.X, padx=5, pady=(0, 8))
        
        # Enable spellcasting
        spell_enable_frame = tk.Frame(section_frame, bg="#3d3d3d")
        spell_enable_frame.pack(fill=tk.X, padx=8, pady=5)
        
        self.spellcasting_var = tk.BooleanVar()
        spell_check = tk.Checkbutton(spell_enable_frame, text="Enable spellcasting",
                                   variable=self.spellcasting_var, bg="#3d3d3d", fg="#ffffff",
                                   selectcolor="#2d2d2d", activebackground="#3d3d3d",
                                   activeforeground="#ffffff", font=('Segoe UI', 9, 'bold'))
        spell_check.pack(side=tk.LEFT)
        
        # Spell key and interval in same row
        spell_controls_frame = tk.Frame(section_frame, bg="#3d3d3d")
        spell_controls_frame.pack(fill=tk.X, padx=8, pady=3)
        
        tk.Label(spell_controls_frame, text="Key:", bg="#3d3d3d", fg="#ffffff",
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        self.spell_key_var = tk.StringVar(value="F4")
        spell_key_combo = ttk.Combobox(spell_controls_frame, textvariable=self.spell_key_var,
                                     values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"], 
                                     state="readonly", width=5)
        spell_key_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        tk.Label(spell_controls_frame, text="Interval:", bg="#3d3d3d", fg="#ffffff",
                font=('Segoe UI', 9)).pack(side=tk.LEFT)
        
        self.spell_interval = tk.Scale(spell_controls_frame, from_=1, to=10, resolution=0.1,
                                     orient=tk.HORIZONTAL, bg="#3d3d3d", fg="#ffffff",
                                     troughcolor="#2d2d2d", highlightthickness=0)
        self.spell_interval.set(3.7)
        self.spell_interval.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        self.spell_interval_label = tk.Label(spell_controls_frame, text="3.7s", bg="#3d3d3d", fg="#ffffff",
                                           font=('Segoe UI', 9))
        self.spell_interval_label.pack(side=tk.RIGHT)
        
        self.spell_interval.bind("<Motion>", lambda e: self.update_spell_interval_label())
    
    def update_threshold_label(self, scale, label):
        value = scale.get()
        label.config(text=f"{value}.0%")
    
    def update_scan_interval_label(self):
        value = self.scan_interval.get()
        self.scan_interval_label.config(text=f"{value}s")
    
    def update_spell_interval_label(self):
        value = self.spell_interval.get()
        self.spell_interval_label.config(text=f"{value}s")