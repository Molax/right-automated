import tkinter as tk

class ModernControls:
    def __init__(self, app):
        self.app = app
        self.create_control_buttons_section()
    
    def create_control_buttons_section(self):
        # Control buttons at bottom of settings card
        control_frame = tk.Frame(self.app.settings_card, bg="#3d3d3d")
        control_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Main bot controls
        bot_frame = tk.Frame(control_frame, bg="#3d3d3d")
        bot_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        bot_frame.grid_columnconfigure(0, weight=1)
        bot_frame.grid_columnconfigure(1, weight=1)
        
        self.start_btn = tk.Button(bot_frame, text="START BOT",
                                 bg="#28a745", fg="#ffffff",
                                 relief=tk.FLAT, borderwidth=0,
                                 font=('Segoe UI', 11, 'bold'),
                                 height=2, state=tk.DISABLED,
                                 activebackground="#218838",
                                 command=self.app.start_bot)
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        self.stop_btn = tk.Button(bot_frame, text="STOP BOT",
                                bg="#dc3545", fg="#ffffff",
                                relief=tk.FLAT, borderwidth=0,
                                font=('Segoe UI', 11, 'bold'),
                                height=2, state=tk.DISABLED,
                                activebackground="#c82333",
                                command=self.app.stop_bot)
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        # Largato hunt button
        self.largato_btn = tk.Button(control_frame, text="LARGATO HUNT",
                                   bg="#9c27b0", fg="#ffffff",
                                   relief=tk.FLAT, borderwidth=0,
                                   font=('Segoe UI', 10, 'bold'),
                                   height=2, state=tk.DISABLED,
                                   activebackground="#7b1fa2",
                                   command=self.app.start_largato_hunt)
        self.largato_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 5))
        
        # Additional control buttons
        extra_frame = tk.Frame(control_frame, bg="#3d3d3d")
        extra_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        extra_frame.grid_columnconfigure(0, weight=1)
        extra_frame.grid_columnconfigure(1, weight=1)
        
        self.reset_btn = tk.Button(extra_frame, text="Reset Stats",
                                 bg="#6c757d", fg="#ffffff",
                                 relief=tk.FLAT, borderwidth=0,
                                 font=('Segoe UI', 9),
                                 height=1,
                                 activebackground="#5a6268",
                                 command=self.app.reset_stats)
        self.reset_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        self.save_btn = tk.Button(extra_frame, text="Save Settings",
                                bg="#17a2b8", fg="#ffffff",
                                relief=tk.FLAT, borderwidth=0,
                                font=('Segoe UI', 9),
                                height=1,
                                activebackground="#138496",
                                command=self.app.save_config)
        self.save_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))