import tkinter as tk
from tkinter import ttk, scrolledtext

class ModernInterface:
    def __init__(self, app):
        self.app = app
        self.setup_modern_theme()
        self.create_modern_interface()
    
    def setup_modern_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Modern color palette
        colors = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d', 
            'bg_tertiary': '#3d3d3d',
            'accent': '#007acc',
            'accent_hover': '#1a8cdd',
            'text_primary': '#ffffff',
            'text_secondary': '#b3b3b3',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }
        
        # Configure modern styles
        self.style.configure('Modern.TFrame', 
                           background=colors['bg_secondary'],
                           relief='flat',
                           borderwidth=0)
        
        self.style.configure('Card.TFrame',
                           background=colors['bg_tertiary'],
                           relief='flat',
                           borderwidth=1)
        
        self.style.configure('Modern.TLabel',
                           background=colors['bg_secondary'],
                           foreground=colors['text_primary'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Title.TLabel',
                           background=colors['bg_primary'],
                           foreground=colors['text_primary'],
                           font=('Segoe UI', 18, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background=colors['bg_secondary'],
                           foreground=colors['text_secondary'],
                           font=('Segoe UI', 11, 'bold'))
    
    def create_modern_interface(self):
        # Main container with padding
        main_container = tk.Frame(self.app.root, bg="#1a1a1a")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header section
        self.create_header(main_container)
        
        # Content area with grid layout
        content_frame = tk.Frame(main_container, bg="#1a1a1a")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel - Bar Selection and Activity Log
        left_panel = ttk.Frame(content_frame, style='Modern.TFrame')
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Right panel - Settings and Controls
        right_panel = ttk.Frame(content_frame, style='Modern.TFrame')
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1)
        
        self.create_bar_selection_panel(left_panel)
        self.create_log_panel(left_panel)
        
        # Store right panel for settings
        self.app.settings_frame = right_panel
    
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg="#1a1a1a", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title section
        title_section = tk.Frame(header_frame, bg="#1a1a1a")
        title_section.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        
        title_label = ttk.Label(title_section, text="Priston Tale Bot", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_section, text="Advanced Automation Suite", 
                                 foreground="#007acc", background="#1a1a1a",
                                 font=('Segoe UI', 10))
        subtitle_label.pack(anchor=tk.W)
        
        # Controls section
        controls_section = tk.Frame(header_frame, bg="#1a1a1a")
        controls_section.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Status indicator
        self.status_frame = tk.Frame(controls_section, bg="#1a1a1a")
        self.status_frame.pack(side=tk.RIGHT, padx=(20, 10))
        
        status_label = ttk.Label(self.status_frame, text="Status:", 
                               foreground="#b3b3b3", background="#1a1a1a",
                               font=('Segoe UI', 9))
        status_label.pack(side=tk.LEFT)
        
        self.status_indicator = tk.Label(self.status_frame, text="●", 
                                       foreground="#28a745", background="#1a1a1a",
                                       font=('Segoe UI', 16))
        self.status_indicator.pack(side=tk.LEFT, padx=(5, 0))
        
        self.status_text = ttk.Label(self.status_frame, text="Ready", 
                                   foreground="#28a745", background="#1a1a1a",
                                   font=('Segoe UI', 9, 'bold'))
        self.status_text.pack(side=tk.LEFT, padx=(5, 0))
        
        # Dark mode toggle
        toggle_btn = tk.Button(controls_section, text="🌙", 
                             bg="#2d2d2d", fg="#ffffff", 
                             relief=tk.FLAT, borderwidth=0,
                             font=('Segoe UI', 14),
                             width=3, height=1,
                             activebackground="#3d3d3d",
                             command=self.app.toggle_theme)
        toggle_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_bar_selection_panel(self, parent):
        # Bar selection card
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding=20)
        card_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(card_frame, text="Bar Configuration", style='Subtitle.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Create grid for bars
        bars_grid = tk.Frame(card_frame, bg="#3d3d3d")
        bars_grid.pack(fill=tk.X)
        
        # Health, Mana, Stamina bars in a row
        main_bars_frame = tk.Frame(bars_grid, bg="#3d3d3d")
        main_bars_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_modern_bar_card(main_bars_frame, "Health Bar", "#dc3545", 0, 0)
        self.create_modern_bar_card(main_bars_frame, "Mana Bar", "#007acc", 0, 1)
        self.create_modern_bar_card(main_bars_frame, "Stamina Bar", "#28a745", 0, 2)
        
        # Largato skill bar
        skill_frame = tk.Frame(bars_grid, bg="#3d3d3d")
        skill_frame.pack(fill=tk.X)
        
        self.create_modern_skill_card(skill_frame)
        
        # Configuration status
        self.config_status_frame = tk.Frame(card_frame, bg="#3d3d3d")
        self.config_status_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.config_status_label = ttk.Label(self.config_status_frame, 
                                           text="Configure bars to continue",
                                           foreground="#ffc107", background="#3d3d3d",
                                           font=('Segoe UI', 10))
        self.config_status_label.pack()
        
        self.app.bars_frame = card_frame  # For compatibility
    
    def create_modern_bar_card(self, parent, title, color, row, col):
        parent.grid_columnconfigure(col, weight=1, uniform="bar")
        
        bar_card = tk.Frame(parent, bg="#2d2d2d", relief=tk.FLAT, bd=1)
        bar_card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Header
        header = tk.Frame(bar_card, bg="#2d2d2d", height=30)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title, 
                             bg="#2d2d2d", fg="#ffffff",
                             font=('Segoe UI', 10, 'bold'))
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        status_dot = tk.Label(header, text="●", 
                            bg="#2d2d2d", fg="#dc3545",
                            font=('Segoe UI', 12))
        status_dot.pack(side=tk.RIGHT)
        
        # Preview area
        preview_frame = tk.Frame(bar_card, bg="#1a1a1a", height=80)
        preview_frame.pack(fill=tk.X, padx=10, pady=5)
        preview_frame.pack_propagate(False)
        
        preview_label = tk.Label(preview_frame, text="Not Configured",
                               bg="#1a1a1a", fg="#666666",
                               font=('Segoe UI', 9))
        preview_label.pack(expand=True)
        
        # Button
        btn_frame = tk.Frame(bar_card, bg="#2d2d2d")
        btn_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        select_btn = tk.Button(btn_frame, text=f"Select {title}",
                             bg=color, fg="#ffffff",
                             relief=tk.FLAT, borderwidth=0,
                             font=('Segoe UI', 9),
                             activebackground=color,
                             command=lambda: self.app.select_bar(title.lower().replace(" ", "_")))
        select_btn.pack(fill=tk.X)
    
    def create_modern_skill_card(self, parent):
        skill_card = tk.Frame(parent, bg="#2d2d2d", relief=tk.FLAT, bd=1)
        skill_card.pack(fill=tk.X, padx=5, pady=5)
        
        # Header
        header = tk.Frame(skill_card, bg="#2d2d2d")
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        title_label = tk.Label(header, text="Largato Skill Bar", 
                             bg="#2d2d2d", fg="#ffffff",
                             font=('Segoe UI', 11, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        optional_label = tk.Label(header, text="(Optional - for Largato Hunt)", 
                                bg="#2d2d2d", fg="#ffc107",
                                font=('Segoe UI', 9))
        optional_label.pack(side=tk.LEFT, padx=(10, 0))
        
        status_dot = tk.Label(header, text="●", 
                            bg="#2d2d2d", fg="#dc3545",
                            font=('Segoe UI', 12))
        status_dot.pack(side=tk.RIGHT)
        
        # Content area
        content_frame = tk.Frame(skill_card, bg="#2d2d2d")
        content_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Preview and button side by side
        preview_frame = tk.Frame(content_frame, bg="#1a1a1a", width=150, height=60)
        preview_frame.pack(side=tk.LEFT, padx=(0, 15))
        preview_frame.pack_propagate(False)
        
        preview_label = tk.Label(preview_frame, text="Not Configured",
                               bg="#1a1a1a", fg="#666666",
                               font=('Segoe UI', 9))
        preview_label.pack(expand=True)
        
        select_btn = tk.Button(content_frame, text="Select Largato Skill Bar",
                             bg="#9c27b0", fg="#ffffff",
                             relief=tk.FLAT, borderwidth=0,
                             font=('Segoe UI', 10),
                             activebackground="#7b1fa2",
                             command=lambda: self.app.select_bar("largato_skill"))
        select_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_log_panel(self, parent):
        log_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        log_card.pack(fill=tk.BOTH, expand=True)
        log_card.grid_rowconfigure(1, weight=1)
        
        title_label = ttk.Label(log_card, text="Activity Log", style='Subtitle.TLabel')
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Modern log text widget
        self.log_text = scrolledtext.ScrolledText(
            log_card,
            bg="#1a1a1a",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#007acc",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.log_text.grid(row=1, column=0, sticky="nsew")
    
    def update_status(self, text, color):
        self.status_indicator.configure(foreground=color)
        self.status_text.configure(text=text, foreground=color)
    
    def update_config_status(self, text, color):
        self.config_status_label.configure(text=text, foreground=color)