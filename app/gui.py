import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
import logging
from PIL import Image, ImageTk

logger = logging.getLogger('PristonBot')

class PristonTaleBot:
    def __init__(self, root):
        logger.info("Initializing Enhanced Priston Tale Bot")
        self.root = root
        
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass
        
        self.root.geometry("1300x900")
        self.root.minsize(1100, 800)
        self.root.title("Priston Tale Bot - Enhanced")
        self.root.configure(bg="#1a1a1a")
        
        self._initialize_screen_selectors()
        self._initialize_bot_system()
        self._create_interface()
        
        self.log("Enhanced Bot interface initialized")
        self._load_configuration()
        self.check_bar_config()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        logger.info("Enhanced Bot GUI initialized successfully")
    
    def _initialize_screen_selectors(self):
        try:
            from app.bar_selector.screen_selector import EnhancedScreenSelector
            
            self.hp_bar_selector = EnhancedScreenSelector(self.root)
            self.mp_bar_selector = EnhancedScreenSelector(self.root)
            self.sp_bar_selector = EnhancedScreenSelector(self.root)
            self.largato_skill_selector = EnhancedScreenSelector(self.root)
            
            logger.info("Enhanced screen selectors initialized")
            
        except ImportError as e:
            logger.error(f"Failed to import EnhancedScreenSelector: {e}")
            
            from app.bar_selector.screen_selector import ScreenSelector
            
            self.hp_bar_selector = ScreenSelector(self.root)
            self.mp_bar_selector = ScreenSelector(self.root)
            self.sp_bar_selector = ScreenSelector(self.root)
            self.largato_skill_selector = ScreenSelector(self.root)
            
            logger.info("Fallback screen selectors initialized")
    
    def _initialize_bot_system(self):
        try:
            from app.bar_selector.bar_detector import EnhancedBarDetector, HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE
            
            self.hp_detector = EnhancedBarDetector("Health", HEALTH_COLOR_RANGE)
            self.mp_detector = EnhancedBarDetector("Mana", MANA_COLOR_RANGE)
            self.sp_detector = EnhancedBarDetector("Stamina", STAMINA_COLOR_RANGE)
            
        except ImportError:
            logger.warning("Enhanced bar detectors not available, using fallback")
            self.hp_detector = None
            self.mp_detector = None
            self.sp_detector = None
        
        self.running = False
        self.largato_running = False
        self.start_time = None
        
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
    
    def _create_interface(self):
        main_canvas = tk.Canvas(self.root, bg="#1a1a1a", highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_main = tk.Frame(main_canvas, bg="#1a1a1a")
        
        scrollable_main.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_main, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_container = tk.Frame(scrollable_main, bg="#1a1a1a")
        main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self._create_header(main_container)
        self._create_content_area(main_container)
    
    def _create_header(self, parent):
        header_frame = tk.Frame(parent, bg="#1a1a1a", height=70)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        header_frame.pack_propagate(False)
        
        title_section = tk.Frame(header_frame, bg="#1a1a1a")
        title_section.pack(side=tk.LEFT, fill=tk.Y, pady=8)
        
        title_label = tk.Label(title_section, text="Priston Tale Bot", 
                              font=("Segoe UI", 20, "bold"), bg="#1a1a1a", fg="#ffffff")
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_section, text="Enhanced Automation Suite", 
                                 font=("Segoe UI", 12), bg="#1a1a1a", fg="#007acc")
        subtitle_label.pack(anchor=tk.W)
        
        status_section = tk.Frame(header_frame, bg="#1a1a1a")
        status_section.pack(side=tk.RIGHT, fill=tk.Y, pady=8)
        
        status_frame = tk.Frame(status_section, bg="#1a1a1a")
        status_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        status_label = tk.Label(status_frame, text="Status:", 
                               font=("Segoe UI", 10), bg="#1a1a1a", fg="#b3b3b3")
        status_label.pack(side=tk.LEFT)
        
        self.status_indicator = tk.Label(status_frame, text="●", 
                                       font=("Segoe UI", 16), bg="#1a1a1a", fg="#28a745")
        self.status_indicator.pack(side=tk.LEFT, padx=(5, 0))
        
        self.status_text = tk.Label(status_frame, text="Ready", 
                                   font=("Segoe UI", 10, "bold"), bg="#1a1a1a", fg="#28a745")
        self.status_text.pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_content_area(self, parent):
        content_frame = tk.Frame(parent, bg="#1a1a1a")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        
        left_panel = tk.Frame(content_frame, bg="#2d2d2d", relief=tk.FLAT, bd=1)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_panel.grid_rowconfigure(1, weight=1)
        
        right_panel = tk.Frame(content_frame, bg="#2d2d2d", relief=tk.FLAT, bd=1)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=2)
        right_panel.grid_rowconfigure(1, weight=1)
        
        self._create_bar_selection_panel(left_panel)
        self._create_log_panel(left_panel)
        self._create_settings_panel(right_panel)
        self._create_controls_panel(right_panel)
    
    def _create_bar_selection_panel(self, parent):
        bars_frame = tk.Frame(parent, bg="#2d2d2d", padx=12, pady=12)
        bars_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        
        title_label = tk.Label(bars_frame, text="Bar Configuration", 
                              font=("Segoe UI", 14, "bold"), bg="#2d2d2d", fg="#ffffff")
        title_label.pack(anchor=tk.W, pady=(0, 12))
        
        bars_grid = tk.Frame(bars_frame, bg="#2d2d2d")
        bars_grid.pack(fill=tk.X)
        
        main_bars = tk.Frame(bars_grid, bg="#2d2d2d")
        main_bars.pack(fill=tk.X, pady=(0, 8))
        
        for i, (name, color, selector) in enumerate([
            ("Health Bar", "#dc3545", self.hp_bar_selector),
            ("Mana Bar", "#007acc", self.mp_bar_selector),
            ("Stamina Bar", "#28a745", self.sp_bar_selector)
        ]):
            main_bars.grid_columnconfigure(i, weight=1, uniform="bar")
            self._create_bar_card(main_bars, name, color, selector, 0, i)
        
        skill_frame = tk.Frame(bars_grid, bg="#2d2d2d")
        skill_frame.pack(fill=tk.X)
        
        self._create_skill_card(skill_frame)
        
        self.config_status_label = tk.Label(bars_frame, text="Configure bars to continue",
                                           font=("Segoe UI", 11), bg="#2d2d2d", fg="#ffc107")
        self.config_status_label.pack(pady=(12, 0))
    
    def _create_bar_card(self, parent, title, color, selector, row, col):
        card = tk.Frame(parent, bg="#3d3d3d", relief=tk.FLAT, bd=1)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        
        header = tk.Frame(card, bg="#3d3d3d")
        header.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        title_label = tk.Label(header, text=title, font=("Segoe UI", 10, "bold"), 
                              bg="#3d3d3d", fg="#ffffff")
        title_label.pack(side=tk.LEFT)
        
        status_dot = tk.Label(header, text="●", font=("Segoe UI", 12), 
                             bg="#3d3d3d", fg="#dc3545")
        status_dot.pack(side=tk.RIGHT)
        setattr(selector, 'status_dot', status_dot)
        
        preview_frame = tk.Frame(card, bg="#1a1a1a", height=50)
        preview_frame.pack(fill=tk.X, padx=8, pady=4)
        preview_frame.pack_propagate(False)
        
        preview_label = tk.Label(preview_frame, text="Not Configured",
                               bg="#1a1a1a", fg="#666666", font=("Segoe UI", 9))
        preview_label.pack(expand=True)
        setattr(selector, 'preview_label', preview_label)
        
        btn_frame = tk.Frame(card, bg="#3d3d3d")
        btn_frame.pack(fill=tk.X, padx=8, pady=(4, 8))
        
        select_btn = tk.Button(btn_frame, text=f"Select {title}",
                             bg=color, fg="#ffffff", relief=tk.FLAT, borderwidth=0,
                             font=("Segoe UI", 9), activebackground=color,
                             command=lambda: self.start_bar_selection(title, color, selector))
        select_btn.pack(fill=tk.X)
    
    def _create_skill_card(self, parent):
        card = tk.Frame(parent, bg="#3d3d3d", relief=tk.FLAT, bd=1)
        card.pack(fill=tk.X, padx=4, pady=4)
        
        header = tk.Frame(card, bg="#3d3d3d")
        header.pack(fill=tk.X, padx=12, pady=(12, 8))
        
        title_label = tk.Label(header, text="Largato Skill Bar", 
                              font=("Segoe UI", 11, "bold"), bg="#3d3d3d", fg="#ffffff")
        title_label.pack(side=tk.LEFT)
        
        optional_label = tk.Label(header, text="(Optional - for Largato Hunt)", 
                                 font=("Segoe UI", 9), bg="#3d3d3d", fg="#ffc107")
        optional_label.pack(side=tk.LEFT, padx=(8, 0))
        
        status_dot = tk.Label(header, text="●", font=("Segoe UI", 12), 
                             bg="#3d3d3d", fg="#dc3545")
        status_dot.pack(side=tk.RIGHT)
        setattr(self.largato_skill_selector, 'status_dot', status_dot)
        
        content = tk.Frame(card, bg="#3d3d3d")
        content.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        preview_frame = tk.Frame(content, bg="#1a1a1a", width=100, height=40)
        preview_frame.pack(side=tk.LEFT, padx=(0, 12))
        preview_frame.pack_propagate(False)
        
        preview_label = tk.Label(preview_frame, text="Not Configured",
                               bg="#1a1a1a", fg="#666666", font=("Segoe UI", 9))
        preview_label.pack(expand=True)
        setattr(self.largato_skill_selector, 'preview_label', preview_label)
        
        select_btn = tk.Button(content, text="Select Largato Skill Bar",
                             bg="#9c27b0", fg="#ffffff", relief=tk.FLAT, borderwidth=0,
                             font=("Segoe UI", 10), activebackground="#7b1fa2",
                             command=lambda: self.start_bar_selection("Largato Skill Bar", "#9c27b0", self.largato_skill_selector))
        select_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_log_panel(self, parent):
        log_frame = tk.Frame(parent, bg="#2d2d2d", padx=12, pady=12)
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        
        title_label = tk.Label(log_frame, text="Activity Log", 
                              font=("Segoe UI", 14, "bold"), bg="#2d2d2d", fg="#ffffff")
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, bg="#1a1a1a", fg="#ffffff", insertbackground="#ffffff",
            selectbackground="#007acc", selectforeground="#ffffff",
            relief=tk.FLAT, borderwidth=0, font=("Consolas", 10), wrap=tk.WORD
        )
        self.log_text.grid(row=1, column=0, sticky="nsew")
    
    def _create_settings_panel(self, parent):
        settings_frame = tk.Frame(parent, bg="#2d2d2d", padx=12, pady=12)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        settings_frame.grid_rowconfigure(1, weight=1)
        
        title_label = tk.Label(settings_frame, text="Bot Settings", 
                              font=("Segoe UI", 14, "bold"), bg="#2d2d2d", fg="#ffffff")
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        settings_content = tk.Frame(settings_frame, bg="#2d2d2d")
        settings_content.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        
        self._create_potion_settings(settings_content)
        self._create_behavior_settings(settings_content)
        self._create_spellcasting_settings(settings_content)
    
    def _create_potion_settings(self, parent):
        frame = tk.LabelFrame(parent, text="Potion Settings", bg="#2d2d2d", fg="#ffffff", 
                             font=("Segoe UI", 10, "bold"))
        frame.pack(fill=tk.X, padx=4, pady=(0, 8))
        
        keys_frame = tk.Frame(frame, bg="#2d2d2d")
        keys_frame.pack(fill=tk.X, padx=8, pady=8)
        
        for i, (name, color, default) in enumerate([
            ("HP:", "#dc3545", "1"),
            ("MP:", "#007acc", "3"),
            ("SP:", "#28a745", "2")
        ]):
            keys_frame.grid_columnconfigure(i*2+1, weight=1)
            
            tk.Label(keys_frame, text=name, bg="#2d2d2d", fg=color,
                    font=("Segoe UI", 9, "bold")).grid(row=0, column=i*2, sticky="e", padx=(0, 4))
            
            var = tk.StringVar(value=default)
            combo = ttk.Combobox(keys_frame, textvariable=var, 
                               values=["1", "2", "3", "4", "5"], state="readonly", width=4)
            combo.grid(row=0, column=i*2+1, sticky="w", padx=(0, 12))
            setattr(self, f"{name[:-1].lower()}_key_var", var)
        
        thresholds_frame = tk.Frame(frame, bg="#2d2d2d")
        thresholds_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        for i, (name, color, default) in enumerate([
            ("Health:", "#dc3545", 50),
            ("Mana:", "#007acc", 30),
            ("Stamina:", "#28a745", 40)
        ]):
            row_frame = tk.Frame(thresholds_frame, bg="#2d2d2d")
            row_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(row_frame, text=name, bg="#2d2d2d", fg=color,
                    font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            
            scale = tk.Scale(row_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                           bg="#2d2d2d", fg="#ffffff", troughcolor="#1a1a1a",
                           highlightthickness=0, activebackground=color)
            scale.set(default)
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 4))
            
            label = tk.Label(row_frame, text=f"{default}%", bg="#2d2d2d", fg=color,
                           font=("Segoe UI", 9, "bold"), width=5)
            label.pack(side=tk.RIGHT)
            
            scale.bind("<Motion>", lambda e, l=label, s=scale: l.config(text=f"{s.get()}%"))
            setattr(self, f"{name[:-1].lower()}_threshold", scale)
    
    def _create_behavior_settings(self, parent):
        frame = tk.LabelFrame(parent, text="Bot Behavior", bg="#2d2d2d", fg="#ffffff", 
                             font=("Segoe UI", 10, "bold"))
        frame.pack(fill=tk.X, padx=4, pady=(0, 8))
        
        scan_frame = tk.Frame(frame, bg="#2d2d2d")
        scan_frame.pack(fill=tk.X, padx=8, pady=8)
        
        tk.Label(scan_frame, text="Scan Interval:", bg="#2d2d2d", fg="#ffffff",
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        self.scan_interval = tk.Scale(scan_frame, from_=0.1, to=2.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, bg="#2d2d2d", fg="#ffffff",
                                    troughcolor="#1a1a1a", highlightthickness=0)
        self.scan_interval.set(0.5)
        self.scan_interval.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 4))
        
        self.scan_label = tk.Label(scan_frame, text="0.5s", bg="#2d2d2d", fg="#ffffff",
                                 font=("Segoe UI", 9), width=5)
        self.scan_label.pack(side=tk.RIGHT)
        
        self.scan_interval.bind("<Motion>", lambda e: self.scan_label.config(text=f"{self.scan_interval.get()}s"))
        
        debug_frame = tk.Frame(frame, bg="#2d2d2d")
        debug_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.debug_var = tk.BooleanVar()
        debug_check = tk.Checkbutton(debug_frame, text="Enable debug mode",
                                   variable=self.debug_var, bg="#2d2d2d", fg="#ffffff",
                                   selectcolor="#1a1a1a", activebackground="#2d2d2d",
                                   activeforeground="#ffffff", font=("Segoe UI", 9))
        debug_check.pack(side=tk.LEFT)
    
    def _create_spellcasting_settings(self, parent):
        frame = tk.LabelFrame(parent, text="Spellcasting", bg="#2d2d2d", fg="#ffffff", 
                             font=("Segoe UI", 10, "bold"))
        frame.pack(fill=tk.X, padx=4, pady=(0, 8))
        
        enable_frame = tk.Frame(frame, bg="#2d2d2d")
        enable_frame.pack(fill=tk.X, padx=8, pady=8)
        
        self.spellcasting_var = tk.BooleanVar()
        spell_check = tk.Checkbutton(enable_frame, text="Enable spellcasting",
                                   variable=self.spellcasting_var, bg="#2d2d2d", fg="#ffffff",
                                   selectcolor="#1a1a1a", activebackground="#2d2d2d",
                                   activeforeground="#ffffff", font=("Segoe UI", 9, "bold"))
        spell_check.pack(side=tk.LEFT)
        
        controls_frame = tk.Frame(frame, bg="#2d2d2d")
        controls_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        tk.Label(controls_frame, text="Key:", bg="#2d2d2d", fg="#ffffff",
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        self.spell_key_var = tk.StringVar(value="F4")
        spell_combo = ttk.Combobox(controls_frame, textvariable=self.spell_key_var,
                                 values=["F1", "F2", "F3", "F4", "F5", "F6"], 
                                 state="readonly", width=6)
        spell_combo.pack(side=tk.LEFT, padx=(4, 12))
        
        tk.Label(controls_frame, text="Interval:", bg="#2d2d2d", fg="#ffffff",
                font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        self.spell_interval = tk.Scale(controls_frame, from_=1, to=10, resolution=0.1,
                                     orient=tk.HORIZONTAL, bg="#2d2d2d", fg="#ffffff",
                                     troughcolor="#1a1a1a", highlightthickness=0)
        self.spell_interval.set(3.7)
        self.spell_interval.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        
        self.spell_label = tk.Label(controls_frame, text="3.7s", bg="#2d2d2d", fg="#ffffff",
                                   font=("Segoe UI", 9), width=5)
        self.spell_label.pack(side=tk.RIGHT)
        
        self.spell_interval.bind("<Motion>", lambda e: self.spell_label.config(text=f"{self.spell_interval.get()}s"))
    
    def _create_controls_panel(self, parent):
        controls_frame = tk.Frame(parent, bg="#2d2d2d", padx=12, pady=12)
        controls_frame.grid(row=1, column=0, sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=1)
        
        bot_frame = tk.Frame(controls_frame, bg="#2d2d2d")
        bot_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        bot_frame.grid_columnconfigure(0, weight=1)
        bot_frame.grid_columnconfigure(1, weight=1)
        
        self.start_btn = tk.Button(bot_frame, text="START BOT",
                                 bg="#28a745", fg="#ffffff", relief=tk.FLAT, borderwidth=0,
                                 font=("Segoe UI", 12, "bold"), height=2, state=tk.DISABLED,
                                 activebackground="#218838", command=self.start_bot)
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        
        self.stop_btn = tk.Button(bot_frame, text="STOP BOT",
                                bg="#dc3545", fg="#ffffff", relief=tk.FLAT, borderwidth=0,
                                font=("Segoe UI", 12, "bold"), height=2, state=tk.DISABLED,
                                activebackground="#c82333", command=self.stop_bot)
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        
        self.largato_btn = tk.Button(controls_frame, text="LARGATO HUNT",
                                   bg="#9c27b0", fg="#ffffff", relief=tk.FLAT, borderwidth=0,
                                   font=("Segoe UI", 11, "bold"), height=2, state=tk.DISABLED,
                                   activebackground="#7b1fa2", command=self.start_largato_hunt)
        self.largato_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        stats_frame = tk.Frame(controls_frame, bg="#2d2d2d")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        self._create_stats_display(stats_frame)
        
        actions_frame = tk.Frame(controls_frame, bg="#2d2d2d")
        actions_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        reset_btn = tk.Button(actions_frame, text="Reset Stats",
                             bg="#6c757d", fg="#ffffff", relief=tk.FLAT, borderwidth=0,
                             font=("Segoe UI", 10), height=1, activebackground="#5a6268",
                             command=self.reset_stats)
        reset_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        
        save_btn = tk.Button(actions_frame, text="Save Settings",
                           bg="#17a2b8", fg="#ffffff", relief=tk.FLAT, borderwidth=0,
                           font=("Segoe UI", 10), height=1, activebackground="#138496",
                           command=self.save_settings)
        save_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))
    
    def _create_stats_display(self, parent):
        stats_grid = tk.Frame(parent, bg="#2d2d2d")
        stats_grid.pack(fill=tk.X)
        
        for i in range(3):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        labels = [
            ("HP Potions:", "#dc3545", "hp_potions_var"),
            ("MP Potions:", "#007acc", "mp_potions_var"),
            ("SP Potions:", "#28a745", "sp_potions_var"),
            ("Spells Cast:", "#ffffff", "spells_var"),
            ("Uptime:", "#ffffff", "uptime_var"),
            ("Round:", "#9c27b0", "round_var")
        ]
        
        for i, (text, color, var_name) in enumerate(labels):
            row, col = divmod(i, 3)
            
            frame = tk.Frame(stats_grid, bg="#2d2d2d")
            frame.grid(row=row, column=col, sticky="ew", padx=1, pady=1)
            
            tk.Label(frame, text=text, bg="#2d2d2d", fg=color,
                    font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            
            var = tk.StringVar(value="0" if "var" not in var_name.replace("uptime", "time").replace("round", "1") else ("00:00:00" if "uptime" in var_name else "1"))
            label = tk.Label(frame, textvariable=var, bg="#2d2d2d", fg="#ffffff",
                           font=("Segoe UI", 9))
            label.pack(side=tk.RIGHT)
            
            setattr(self, var_name, var)
    
    def start_bar_selection(self, title, color, selector):
        self.log(f"Starting {title} selection...")
        
        def on_completion():
            self.log(f"{title} selection completed")
            self.update_bar_status(selector)
            self.check_bar_config()
        
        try:
            success = selector.start_selection(
                title=title,
                color=color,
                completion_callback=on_completion
            )
            
            if not success:
                self.log(f"Failed to start {title} selection")
                
        except Exception as e:
            logger.error(f"Error starting {title} selection: {e}")
            self.log(f"Error starting {title} selection: {e}")
    
    def update_bar_status(self, selector):
        if hasattr(selector, 'status_dot') and hasattr(selector, 'preview_label'):
            if selector.is_setup():
                selector.status_dot.config(fg="#28a745")
                selector.preview_label.config(text="Configured", fg="#28a745")
                
                if hasattr(selector, 'preview_image') and selector.preview_image:
                    try:
                        img = selector.preview_image.resize((80, 40), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        selector.preview_label.config(image=photo, text="")
                        selector.preview_label.image = photo
                    except Exception as e:
                        logger.debug(f"Could not update preview image: {e}")
            else:
                selector.status_dot.config(fg="#dc3545")
                selector.preview_label.config(text="Not Configured", fg="#666666")
    
    def check_bar_config(self):
        configured_count = sum([
            self.hp_bar_selector.is_setup(),
            self.mp_bar_selector.is_setup(),
            self.sp_bar_selector.is_setup()
        ])
        
        largato_configured = self.largato_skill_selector.is_setup()
        
        if configured_count >= 3:
            self.config_status_label.config(text="Ready to start bot!", fg="#28a745")
            self.start_btn.config(state=tk.NORMAL)
            
            if largato_configured:
                self.largato_btn.config(state=tk.NORMAL)
                self.config_status_label.config(text="All systems ready! Largato Hunt available.")
            else:
                self.config_status_label.config(text="Bot ready! Configure Largato skill bar for hunt mode.")
        else:
            self.config_status_label.config(text=f"Configure {3-configured_count} more bar(s) to continue", fg="#ffc107")
            self.start_btn.config(state=tk.DISABLED)
            self.largato_btn.config(state=tk.DISABLED)
        
        for selector in [self.hp_bar_selector, self.mp_bar_selector, self.sp_bar_selector, self.largato_skill_selector]:
            self.update_bar_status(selector)
    
    def start_bot(self):
        self.log("Starting bot...")
        self.running = True
        self.start_time = time.time()
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.largato_btn.config(state=tk.DISABLED)
        
        self.update_status("Running", "#28a745")
        self._update_display()
    
    def stop_bot(self):
        self.log("Stopping bot...")
        self.running = False
        self.largato_running = False
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if self.largato_skill_selector.is_setup():
            self.largato_btn.config(state=tk.NORMAL)
        
        self.update_status("Ready", "#28a745")
    
    def start_largato_hunt(self):
        self.log("Starting Largato Hunt...")
        self.largato_running = True
        self.start_time = time.time()
        
        self.start_btn.config(state=tk.DISABLED)
        self.largato_btn.config(text="Stop Hunt", state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.update_status("Hunting", "#9c27b0")
        self._update_display()
    
    def reset_stats(self):
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        self.start_time = None
        
        self.hp_potions_var.set("0")
        self.mp_potions_var.set("0")
        self.sp_potions_var.set("0")
        self.spells_var.set("0")
        self.uptime_var.set("00:00:00")
        self.round_var.set("1")
        
        self.log("Statistics reset")
    
    def save_settings(self):
        try:
            self._save_configuration()
            self.log("Settings saved successfully")
        except Exception as e:
            self.log(f"Error saving settings: {e}")
    
    def _update_display(self):
        if not (self.running or self.largato_running):
            return
        
        try:
            if self.start_time:
                uptime = time.time() - self.start_time
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                seconds = int(uptime % 60)
                self.uptime_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            self.hp_potions_var.set(str(self.hp_potions_used))
            self.mp_potions_var.set(str(self.mp_potions_used))
            self.sp_potions_var.set(str(self.sp_potions_used))
            self.spells_var.set(str(self.spells_cast))
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
        
        if self.running or self.largato_running:
            self.root.after(1000, self._update_display)
    
    def update_status(self, text, color):
        self.status_indicator.config(fg=color)
        self.status_text.config(text=text, fg=color)
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        logger.info(message)
    
    def _load_configuration(self):
        try:
            from app.config import load_config
            config = load_config()
            
            bars_config = config.get("bars", {})
            
            for bar_name, selector in [
                ("health_bar", self.hp_bar_selector),
                ("mana_bar", self.mp_bar_selector),
                ("stamina_bar", self.sp_bar_selector),
                ("largato_skill_bar", self.largato_skill_selector)
            ]:
                bar_config = bars_config.get(bar_name, {})
                if bar_config.get("configured", False):
                    x1 = bar_config.get("x1")
                    y1 = bar_config.get("y1")
                    x2 = bar_config.get("x2")
                    y2 = bar_config.get("y2")
                    
                    if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                        selector.configure_from_saved(x1, y1, x2, y2)
                        selector.title = bar_name.replace("_", " ").title()
            
            self._load_settings_from_config(config)
            self.log("Configuration loaded from file")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.log("Using default configuration")
    
    def _load_settings_from_config(self, config):
        try:
            potion_keys = config.get("potion_keys", {})
            self.hp_key_var.set(potion_keys.get("health", "1"))
            self.mp_key_var.set(potion_keys.get("mana", "3"))
            self.sp_key_var.set(potion_keys.get("stamina", "2"))
            
            thresholds = config.get("thresholds", {})
            self.health_threshold.set(thresholds.get("health", 50))
            self.mana_threshold.set(thresholds.get("mana", 30))
            self.stamina_threshold.set(thresholds.get("stamina", 40))
            
            self.scan_interval.set(config.get("scan_interval", 0.5))
            self.debug_var.set(config.get("debug_enabled", False))
            
            spellcasting = config.get("spellcasting", {})
            self.spellcasting_var.set(spellcasting.get("enabled", False))
            self.spell_key_var.set(spellcasting.get("spell_key", "F4"))
            self.spell_interval.set(spellcasting.get("spell_interval", 3.7))
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def _save_configuration(self):
        try:
            from app.config import load_config, save_config
            config = load_config()
            
            for bar_name, selector in [
                ("health_bar", self.hp_bar_selector),
                ("mana_bar", self.mp_bar_selector),
                ("stamina_bar", self.sp_bar_selector),
                ("largato_skill_bar", self.largato_skill_selector)
            ]:
                if selector.is_setup():
                    config["bars"][bar_name] = {
                        "x1": selector.x1,
                        "y1": selector.y1,
                        "x2": selector.x2,
                        "y2": selector.y2,
                        "configured": True
                    }
            
            config["potion_keys"] = {
                "health": self.hp_key_var.get(),
                "mana": self.mp_key_var.get(),
                "stamina": self.sp_key_var.get()
            }
            
            config["thresholds"] = {
                "health": self.health_threshold.get(),
                "mana": self.mana_threshold.get(),
                "stamina": self.stamina_threshold.get()
            }
            
            config["scan_interval"] = self.scan_interval.get()
            config["debug_enabled"] = self.debug_var.get()
            
            config["spellcasting"] = {
                "enabled": self.spellcasting_var.get(),
                "spell_key": self.spell_key_var.get(),
                "spell_interval": self.spell_interval.get()
            }
            
            save_config(config)
            logger.info("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def on_closing(self):
        try:
            if self.running or self.largato_running:
                self.stop_bot()
            
            self._save_configuration()
            logger.info("Application closing gracefully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        finally:
            self.root.destroy()

if __name__ == "__main__":
    import logging
    from app.config import setup_logging
    
    setup_logging()
    
    root = tk.Tk()
    app = PristonTaleBot(root)
    root.mainloop()