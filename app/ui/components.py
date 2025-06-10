"""
UI Components for the Priston Tale Potion Bot
-----------------------------------
This module contains reusable UI components.
"""

import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger('PristonBot')

class ScrollableFrame(ttk.Frame):
    """A scrollable frame container"""
    
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Configure the canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Create a window inside the canvas containing the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to scroll
        self.bind_mousewheel()
        
    def bind_mousewheel(self):
        """Bind mousewheel to scroll canvas"""
        def _on_mousewheel(event):
            # Scroll direction depends on platform
            if event.num == 4 or event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.canvas.yview_scroll(1, "units")
                
        # Bind mousewheel events
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows and macOS
        self.canvas.bind_all("<Button-4>", _on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", _on_mousewheel)    # Linux scroll down