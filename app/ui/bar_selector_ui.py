import tkinter as tk
from tkinter import ttk
import logging
from PIL import ImageTk, Image
from app.bar_selector import ScreenSelector

logger = logging.getLogger('PristonBot')

class BarSelectorUI:
    def __init__(self, parent, root, log_callback):
        self.parent = parent
        self.root = root
        self.log_callback = log_callback
        self.logger = logging.getLogger('PristonBot')
        
        self.hp_bar_selector = ScreenSelector(root)
        self.mp_bar_selector = ScreenSelector(root)
        self.sp_bar_selector = ScreenSelector(root)
        self.largato_skill_selector = ScreenSelector(root)
        
        self._create_ui()
        
    def _create_ui(self):
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        bars_frame = ttk.LabelFrame(main_container, text="Bar Selection", padding=5)
        bars_frame.pack(fill=tk.BOTH, expand=True)
        
        bars_container = ttk.Frame(bars_frame)
        bars_container.pack(fill=tk.BOTH, expand=True)
        
        hp_frame = ttk.LabelFrame(bars_container, text="Health Bar")
        hp_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        self.hp_preview_label = ttk.Label(hp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.hp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        ttk.Button(hp_frame, text="Select Health Bar", 
                  command=lambda: self.start_bar_selection("Health", "red")).pack(
                      fill=tk.X, padx=5, pady=5)
        
        mp_frame = ttk.LabelFrame(bars_container, text="Mana Bar")
        mp_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        self.mp_preview_label = ttk.Label(mp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.mp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        ttk.Button(mp_frame, text="Select Mana Bar", 
                  command=lambda: self.start_bar_selection("Mana", "blue")).pack(
                      fill=tk.X, padx=5, pady=5)
        
        sp_frame = ttk.LabelFrame(bars_container, text="Stamina Bar")
        sp_frame.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
        
        self.sp_preview_label = ttk.Label(sp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.sp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        ttk.Button(sp_frame, text="Select Stamina Bar", 
                  command=lambda: self.start_bar_selection("Stamina", "green")).pack(
                      fill=tk.X, padx=5, pady=5)
        
        largato_frame = ttk.LabelFrame(bars_container, text="Largato Skill")
        largato_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        
        largato_content = ttk.Frame(largato_frame)
        largato_content.pack(fill=tk.X, padx=5, pady=5)
        
        self.largato_preview_label = ttk.Label(largato_content, text="Not Selected", 
                                              borderwidth=1, relief="solid", width=30)
        self.largato_preview_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(largato_content, text="Select Largato Skill Bar", 
                  command=lambda: self.start_bar_selection("Largato Skill", "orange")).pack(
                      side=tk.LEFT, padx=5)
        
        ttk.Label(largato_content, text="(Required for Largato Hunt)", 
                 font=("Arial", 8), foreground="#666666").pack(side=tk.LEFT, padx=10)
        
        status_frame = ttk.Frame(bars_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Bars Configured: 0/4")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        for i in range(3):
            bars_container.grid_columnconfigure(i, weight=1)
        bars_container.grid_rowconfigure(0, weight=1)
        bars_container.grid_rowconfigure(1, weight=0)
    
    def start_bar_selection(self, bar_type, color):
        if bar_type == "Health":
            self.hp_bar_selector = ScreenSelector(self.root)
            self.hp_bar_selector.start_selection(title=f"{bar_type} Bar", color=color)
            self.root.after(1000, lambda: self.update_preview_image(self.hp_bar_selector, self.hp_preview_label))
        elif bar_type == "Mana":
            self.mp_bar_selector = ScreenSelector(self.root)
            self.mp_bar_selector.start_selection(title=f"{bar_type} Bar", color=color)
            self.root.after(1000, lambda: self.update_preview_image(self.mp_bar_selector, self.mp_preview_label))
        elif bar_type == "Stamina":
            self.sp_bar_selector = ScreenSelector(self.root)
            self.sp_bar_selector.start_selection(title=f"{bar_type} Bar", color=color)
            self.root.after(1000, lambda: self.update_preview_image(self.sp_bar_selector, self.sp_preview_label))
        elif bar_type == "Largato Skill":
            self.largato_skill_selector = ScreenSelector(self.root)
            self.largato_skill_selector.start_selection(title=f"{bar_type} Bar", color=color)
            self.root.after(1000, lambda: self.update_preview_image(self.largato_skill_selector, self.largato_preview_label))
        
        self.root.after(1500, self.update_status)
    
    def update_preview_image(self, selector, label):
        if selector.is_setup():
            if hasattr(selector, 'preview_image') and selector.preview_image is not None:
                try:
                    preview_img = selector.preview_image
                    
                    preview_size = (100, 60)
                    resized_img = preview_img.resize(preview_size, Image.LANCZOS)
                    preview_photo = ImageTk.PhotoImage(resized_img)
                    label.config(image=preview_photo, text="")
                    label.image = preview_photo
                    
                    self.log_callback(f"{selector.title} selected: ({selector.x1},{selector.y1}) to ({selector.x2},{selector.y2})")
                    self.update_status()
                    
                except Exception as e:
                    logger.error(f"Error displaying preview image: {e}")
                    label.config(text=f"Selected: ({selector.x1},{selector.y1}) to ({selector.x2},{selector.y2})")
            else:
                label.config(text=f"Selected: ({selector.x1},{selector.y1}) to ({selector.x2},{selector.y2})")
        else:
            label.config(text="Not Selected")
            self.root.after(1000, lambda: self.update_preview_image(selector, label))
    
    def update_status(self):
        count = self.get_configured_count()
        total_count = self.get_total_count()
        self.status_var.set(f"Bars Configured: {count}/{total_count}")
    
    def is_bars_configured(self):
        return (self.hp_bar_selector.is_setup() and 
                self.mp_bar_selector.is_setup() and 
                self.sp_bar_selector.is_setup())
                
    def is_all_bars_configured(self):
        return (self.hp_bar_selector.is_setup() and 
                self.mp_bar_selector.is_setup() and 
                self.sp_bar_selector.is_setup() and
                self.largato_skill_selector.is_setup())
                
    def get_configured_count(self):
        return sum([
            self.hp_bar_selector.is_setup(),
            self.mp_bar_selector.is_setup(),
            self.sp_bar_selector.is_setup(),
            self.largato_skill_selector.is_setup()
        ])
    
    def get_total_count(self):
        return 4