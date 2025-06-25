import tkinter as tk
from tkinter import ttk
import logging
from PIL import ImageTk, Image

logger = logging.getLogger('PristonBot')

class BarSelectorUI:
    def __init__(self, parent, root, log_callback):
        self.parent = parent
        self.root = root
        self.log_callback = log_callback
        self.logger = logging.getLogger('PristonBot')
        
        try:
            from app.bar_selector.screen_selector import ScreenSelector
        except ImportError:
            try:
                from app.bar_selector import ScreenSelector
            except ImportError:
                self.log_callback("ERROR: Could not import ScreenSelector")
                raise ImportError("ScreenSelector not found")
        
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
                  command=self._select_health_bar).pack(
                      fill=tk.X, padx=5, pady=5)
        
        mp_frame = ttk.LabelFrame(bars_container, text="Mana Bar")
        mp_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        self.mp_preview_label = ttk.Label(mp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.mp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        ttk.Button(mp_frame, text="Select Mana Bar", 
                  command=self._select_mana_bar).pack(
                      fill=tk.X, padx=5, pady=5)
        
        sp_frame = ttk.LabelFrame(bars_container, text="Stamina Bar")
        sp_frame.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
        
        self.sp_preview_label = ttk.Label(sp_frame, text="Not Selected", 
                                         borderwidth=1, relief="solid")
        self.sp_preview_label.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        ttk.Button(sp_frame, text="Select Stamina Bar", 
                  command=self._select_stamina_bar).pack(
                      fill=tk.X, padx=5, pady=5)
        
        largato_frame = ttk.LabelFrame(bars_container, text="Largato Skill")
        largato_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)
        
        largato_content = ttk.Frame(largato_frame)
        largato_content.pack(fill=tk.X, padx=5, pady=5)
        
        self.largato_preview_label = ttk.Label(largato_content, text="Not Selected", 
                                              borderwidth=1, relief="solid", width=30)
        self.largato_preview_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(largato_content, text="Select Largato Skill Bar", 
                  command=self._select_largato_skill).pack(
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
    
    def _select_health_bar(self):
        self.log_callback("Starting health_bar selection...")
        self.start_bar_selection("Health", "red", self.hp_bar_selector, self.hp_preview_label)
    
    def _select_mana_bar(self):
        self.log_callback("Starting mana_bar selection...")
        self.start_bar_selection("Mana", "blue", self.mp_bar_selector, self.mp_preview_label)
    
    def _select_stamina_bar(self):
        self.log_callback("Starting stamina_bar selection...")
        self.start_bar_selection("Stamina", "green", self.sp_bar_selector, self.sp_preview_label)
    
    def _select_largato_skill(self):
        self.log_callback("Starting largato_skill selection...")
        self.start_bar_selection("Largato Skill", "purple", self.largato_skill_selector, self.largato_preview_label)
    
    def start_bar_selection(self, bar_type, color, selector, preview_label):
        self.log_callback(f"Starting {bar_type} bar selection with {color} overlay...")
        
        def on_selection_complete():
            try:
                self.update_preview_image(selector, preview_label)
                self.update_status()
                self.log_callback(f"{bar_type} bar selection completed successfully")
            except Exception as e:
                self.logger.error(f"Error in completion callback: {e}")
                self.log_callback(f"Error completing {bar_type} selection: {e}")
        
        try:
            success = selector.start_selection(
                title=f"{bar_type} Bar", 
                color=color, 
                completion_callback=on_selection_complete
            )
            
            if not success:
                self.log_callback(f"Failed to start {bar_type} selection")
                
        except Exception as e:
            self.logger.error(f"Error starting {bar_type} selection: {e}")
            self.log_callback(f"Failed to start {bar_type} selection: {e}")
    
    def update_preview_image(self, selector, label):
        if selector.is_setup():
            if hasattr(selector, 'preview_image') and selector.preview_image is not None:
                try:
                    preview_img = selector.preview_image
                    
                    preview_size = (100, 60)
                    if preview_img.width > preview_size[0] or preview_img.height > preview_size[1]:
                        preview_img = preview_img.resize(preview_size, Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(preview_img)
                    label.configure(image=photo, text="")
                    label.image = photo
                    
                    self.logger.info(f"Updated preview image for {getattr(selector, 'title', 'bar')}")
                    
                except Exception as e:
                    self.logger.error(f"Error updating preview image: {e}")
                    label.configure(text="Preview Error", image="")
            else:
                try:
                    if all([selector.x1, selector.y1, selector.x2, selector.y2]):
                        from PIL import ImageGrab
                        preview_img = ImageGrab.grab(bbox=(selector.x1, selector.y1, selector.x2, selector.y2), all_screens=True)
                        
                        preview_size = (100, 60)
                        if preview_img.width > preview_size[0] or preview_img.height > preview_size[1]:
                            preview_img = preview_img.resize(preview_size, Image.Resampling.LANCZOS)
                        
                        photo = ImageTk.PhotoImage(preview_img)
                        label.configure(image=photo, text="")
                        label.image = photo
                        
                        selector.preview_image = preview_img
                        
                        self.logger.info(f"Created and updated preview image for {getattr(selector, 'title', 'bar')}")
                        
                except Exception as e:
                    self.logger.error(f"Error creating preview image: {e}")
                    label.configure(text="✓ Selected", image="")
        else:
            label.configure(text="Not Selected", image="")
    
    def update_status(self):
        configured = self.get_configured_count()
        total = self.get_total_count()
        self.status_var.set(f"Bars Configured: {configured}/{total}")
        
        self.logger.info(f"Bar configuration status: {configured}/{total}")
    
    def get_configured_count(self):
        count = 0
        if self.hp_bar_selector.is_setup():
            count += 1
        if self.mp_bar_selector.is_setup():
            count += 1
        if self.sp_bar_selector.is_setup():
            count += 1
        if self.largato_skill_selector.is_setup():
            count += 1
        return count
    
    def get_total_count(self):
        return 4
    
    def get_bars_data(self):
        return {
            "health_bar": {
                "x1": self.hp_bar_selector.x1,
                "y1": self.hp_bar_selector.y1,
                "x2": self.hp_bar_selector.x2,
                "y2": self.hp_bar_selector.y2,
                "configured": self.hp_bar_selector.is_setup()
            },
            "mana_bar": {
                "x1": self.mp_bar_selector.x1,
                "y1": self.mp_bar_selector.y1,
                "x2": self.mp_bar_selector.x2,
                "y2": self.mp_bar_selector.y2,
                "configured": self.mp_bar_selector.is_setup()
            },
            "stamina_bar": {
                "x1": self.sp_bar_selector.x1,
                "y1": self.sp_bar_selector.y1,
                "x2": self.sp_bar_selector.x2,
                "y2": self.sp_bar_selector.y2,
                "configured": self.sp_bar_selector.is_setup()
            },
            "largato_skill_bar": {
                "x1": self.largato_skill_selector.x1,
                "y1": self.largato_skill_selector.y1,
                "x2": self.largato_skill_selector.x2,
                "y2": self.largato_skill_selector.y2,
                "configured": self.largato_skill_selector.is_setup()
            }
        }