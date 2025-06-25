"""
Monitor Selection Dialog
-----------------------
UI dialog for selecting which monitor to use for screen capture.
"""

import tkinter as tk
from tkinter import messagebox

class MonitorSelectionDialog:
    def __init__(self, parent, monitors):
        self.parent = parent
        self.monitors = monitors
        self.selected_monitor = None
        self.dialog = None
        
    def show(self):
        """Show dialog and return selected monitor"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Monitor")
        
        dialog_width = 600
        dialog_height = 500
        
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.dialog.resizable(True, True)
        self.dialog.minsize(500, 400)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self._create_ui()
        
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        self.dialog.after_idle(self.dialog.attributes, '-topmost', False)
        
        self.dialog.focus_force()
        
        self.parent.wait_window(self.dialog)
        
        return self.selected_monitor
        
    def _create_ui(self):
        """Create the dialog UI"""
        main_frame = tk.Frame(self.dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        title_label = tk.Label(
            main_frame,
            text="Multiple Monitors Detected",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        instructions = tk.Label(
            main_frame,
            text="Please select which monitor to use for bar selection:",
            font=("Arial", 11),
            bg="white"
        )
        instructions.grid(row=1, column=0, pady=(0, 15))
        
        list_frame = tk.Frame(main_frame, relief=tk.SOLID, borderwidth=1)
        list_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.monitor_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 11),
            selectmode=tk.SINGLE,
            activestyle='none',
            height=8
        )
        self.monitor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.monitor_listbox.yview)
        
        for monitor in self.monitors:
            display_text = str(monitor)
            self.monitor_listbox.insert(tk.END, display_text)
            
        for i, monitor in enumerate(self.monitors):
            if monitor.is_primary:
                self.monitor_listbox.selection_set(i)
                self.monitor_listbox.see(i)
                break
        else:
            if self.monitors:
                self.monitor_listbox.selection_set(0)
        
        preview_frame = tk.LabelFrame(
            main_frame, 
            text="Monitor Layout Preview",
            bg="white",
            font=("Arial", 10)
        )
        preview_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=560,
            height=120,
            bg="#f0f0f0",
            highlightthickness=0
        )
        self.preview_canvas.pack(padx=10, pady=10)
        
        self._draw_monitor_layout()
        
        self.monitor_listbox.bind('<<ListboxSelect>>', self._on_selection_change)
        
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.grid(row=4, column=0, sticky="ew")
        
        button_frame.grid_columnconfigure(0, weight=1)
        
        button_container = tk.Frame(button_frame, bg="white")
        button_container.grid(row=0, column=0, sticky="e")
        
        select_btn = tk.Button(
            button_container,
            text="Select Monitor",
            command=self._on_select,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        select_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = tk.Button(
            button_container,
            text="Cancel",
            command=self._on_cancel,
            width=12,
            height=2,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        cancel_btn.pack(side=tk.RIGHT)
        
        self.monitor_listbox.bind('<Double-Button-1>', lambda e: self._on_select())
        
    def _draw_monitor_layout(self):
        """Draw a visual representation of monitor layout"""
        self.preview_canvas.delete("all")
        
        if not self.monitors:
            return
            
        all_bounds = [m.get_capture_bounds() for m in self.monitors]
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        canvas_width = 540
        canvas_height = 100
        
        if total_width > 0 and total_height > 0:
            scale_x = canvas_width / total_width
            scale_y = canvas_height / total_height
            scale = min(scale_x, scale_y) * 0.8
        else:
            scale = 1.0
        
        scaled_width = total_width * scale
        scaled_height = total_height * scale
        offset_x = (560 - scaled_width) / 2
        offset_y = (120 - scaled_height) / 2
        
        selection = self.monitor_listbox.curselection()
        selected_index = selection[0] if selection else 0
        
        for i, monitor in enumerate(self.monitors):
            x1 = (monitor.x - min_x) * scale + offset_x
            y1 = (monitor.y - min_y) * scale + offset_y
            x2 = x1 + monitor.width * scale
            y2 = y1 + monitor.height * scale
            
            is_selected = i == selected_index
            
            color = "#4CAF50" if is_selected else "#E0E0E0"
            outline = "#2E7D32" if is_selected else "#9E9E9E"
            width = 3 if is_selected else 2
            
            self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=outline,
                width=width
            )
            
            self.preview_canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=str(i + 1),
                font=("Arial", 12, "bold"),
                fill="white" if is_selected else "black"
            )
            
    def _on_selection_change(self, event):
        """Handle selection change in listbox"""
        self._draw_monitor_layout()
        
    def _on_select(self):
        """Handle select button"""
        selection = self.monitor_listbox.curselection()
        if selection:
            self.selected_monitor = self.monitors[selection[0]]
            self.dialog.destroy()
        else:
            messagebox.showwarning(
                "No Selection",
                "Please select a monitor from the list.",
                parent=self.dialog
            )
            
    def _on_cancel(self):
        """Handle cancel button"""
        self.selected_monitor = None
        self.dialog.destroy()