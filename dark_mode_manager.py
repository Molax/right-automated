import tkinter as tk
from tkinter import ttk
import json
import os

class DarkModeManager:
    def __init__(self, root):
        self.root = root
        self.is_dark = False
        self.config_file = "dark_mode_config.json"
        
        self.light_theme = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'select_bg': '#0078d4',
            'select_fg': '#ffffff',
            'frame_bg': '#ffffff',
            'entry_bg': '#ffffff',
            'entry_fg': '#000000',
            'button_bg': '#e1e1e1',
            'button_fg': '#000000',
            'text_bg': '#ffffff',
            'text_fg': '#000000'
        }
        
        self.dark_theme = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'select_bg': '#404040',
            'select_fg': '#ffffff',
            'frame_bg': '#3c3c3c',
            'entry_bg': '#404040',
            'entry_fg': '#ffffff',
            'button_bg': '#404040',
            'button_fg': '#ffffff',
            'text_bg': '#2b2b2b',
            'text_fg': '#ffffff'
        }
        
        self.load_theme_preference()
        self.setup_styles()
        
    def load_theme_preference(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.is_dark = config.get('dark_mode', False)
        except Exception:
            pass
    
    def save_theme_preference(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'dark_mode': self.is_dark}, f)
        except Exception:
            pass
    
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.apply_theme()
    
    def get_current_theme(self):
        return self.dark_theme if self.is_dark else self.light_theme
    
    def apply_theme(self):
        theme = self.get_current_theme()
        
        self.root.configure(bg=theme['bg'])
        
        self.style.configure('TFrame', 
                           background=theme['frame_bg'],
                           relief='flat')
        
        self.style.configure('TLabel',
                           background=theme['frame_bg'],
                           foreground=theme['fg'])
        
        self.style.configure('TButton',
                           background=theme['button_bg'],
                           foreground=theme['button_fg'],
                           borderwidth=1,
                           focuscolor='none')
        
        self.style.map('TButton',
                      background=[('active', theme['select_bg']),
                                ('pressed', theme['select_bg'])])
        
        self.style.configure('TEntry',
                           background=theme['entry_bg'],
                           foreground=theme['entry_fg'],
                           fieldbackground=theme['entry_bg'],
                           borderwidth=1)
        
        self.style.configure('TLabelFrame',
                           background=theme['frame_bg'],
                           foreground=theme['fg'],
                           borderwidth=1)
        
        self.style.configure('TLabelFrame.Label',
                           background=theme['frame_bg'],
                           foreground=theme['fg'])
        
        self.style.configure('TNotebook',
                           background=theme['frame_bg'],
                           borderwidth=1)
        
        self.style.configure('TNotebook.Tab',
                           background=theme['button_bg'],
                           foreground=theme['button_fg'],
                           padding=[8, 4])
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', theme['select_bg']),
                                ('active', theme['button_bg'])])
        
        self.style.configure('Vertical.TScrollbar',
                           background=theme['button_bg'],
                           troughcolor=theme['frame_bg'],
                           borderwidth=1)
        
        self.style.configure('Horizontal.TScrollbar',
                           background=theme['button_bg'],
                           troughcolor=theme['frame_bg'],
                           borderwidth=1)
        
        self.update_text_widgets()
    
    def update_text_widgets(self):
        theme = self.get_current_theme()
        
        def update_widget(widget):
            try:
                if isinstance(widget, tk.Text) or hasattr(widget, 'configure'):
                    if 'background' in widget.configure():
                        widget.configure(bg=theme['text_bg'], fg=theme['text_fg'])
                    if hasattr(widget, 'configure') and 'insertbackground' in str(widget.configure()):
                        widget.configure(insertbackground=theme['text_fg'])
                
                if isinstance(widget, tk.Label):
                    widget.configure(bg=theme['frame_bg'], fg=theme['fg'])
                
                if isinstance(widget, tk.Frame):
                    widget.configure(bg=theme['frame_bg'])
                
                for child in widget.winfo_children():
                    update_widget(child)
                    
            except Exception:
                pass
        
        update_widget(self.root)
    
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()
        self.save_theme_preference()
    
    def create_toggle_button(self, parent):
        button_text = "🌙" if not self.is_dark else "☀️"
        toggle_btn = ttk.Button(
            parent,
            text=button_text,
            width=3,
            command=self.toggle_theme
        )
        
        def update_button_text():
            new_text = "🌙" if not self.is_dark else "☀️"
            toggle_btn.configure(text=new_text)
        
        original_toggle = self.toggle_theme
        def enhanced_toggle():
            original_toggle()
            update_button_text()
        
        toggle_btn.configure(command=enhanced_toggle)
        return toggle_btn


def enhance_priston_gui(gui_class):
    original_init = gui_class.__init__
    
    def enhanced_init(self, root):
        self.dark_mode_manager = DarkModeManager(root)
        
        original_init(self, root)
        
        if hasattr(self, 'header_frame') or hasattr(self, 'title_frame'):
            header = getattr(self, 'header_frame', getattr(self, 'title_frame', None))
            if header:
                toggle_btn = self.dark_mode_manager.create_toggle_button(header)
                toggle_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    gui_class.__init__ = enhanced_init
    return gui_class


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Priston Tale Bot - Dark Mode Demo")
    root.geometry("800x600")
    
    dark_manager = DarkModeManager(root)
    
    main_container = ttk.Frame(root, padding="10")
    main_container.pack(fill=tk.BOTH, expand=True)
    
    header_frame = ttk.Frame(main_container)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    
    title_label = ttk.Label(header_frame, text="Priston Tale Potion Bot", 
                           font=("Arial", 16, "bold"))
    title_label.pack(side=tk.LEFT)
    
    toggle_btn = dark_manager.create_toggle_button(header_frame)
    toggle_btn.pack(side=tk.RIGHT)
    
    left_frame = ttk.LabelFrame(main_container, text="Settings", padding="5")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    right_frame = ttk.LabelFrame(main_container, text="Log", padding="5")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
    
    sample_label = ttk.Label(left_frame, text="Sample setting:")
    sample_label.pack(anchor=tk.W, pady=2)
    
    sample_entry = ttk.Entry(left_frame)
    sample_entry.pack(fill=tk.X, pady=2)
    
    sample_button = ttk.Button(left_frame, text="Apply Settings")
    sample_button.pack(pady=5)
    
    import tkinter.scrolledtext as scrolledtext
    log_text = scrolledtext.ScrolledText(right_frame, height=20, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True)
    log_text.insert(tk.END, "Bot initialized...\nDark mode ready!\n")
    
    root.mainloop()