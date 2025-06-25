import tkinter as tk
from tkinter import messagebox
import math

class MonitorSelectionDialog:
    def __init__(self, parent, monitors):
        self.parent = parent
        self.monitors = monitors
        self.selected_monitor = None
        self.dialog = None
        
    def show(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Monitor")
        
        dialog_width = 800
        dialog_height = 600
        
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.dialog.resizable(True, True)
        self.dialog.minsize(600, 400)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self._create_ui()
        
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        self.dialog.after(100, lambda: self.dialog.attributes('-topmost', False))
        
        self.dialog.focus_force()
        
        self.parent.wait_window(self.dialog)
        
        return self.selected_monitor
        
    def _create_ui(self):
        main_frame = tk.Frame(self.dialog, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            main_frame,
            text="Select Monitor for Screen Capture",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        title_label.pack(pady=(0, 15))
        
        content_frame = tk.Frame(main_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(content_frame, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(content_frame, bg="white", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        canvas_label = tk.Label(
            left_frame,
            text="Monitor Layout (Click to Select):",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        canvas_label.pack(anchor="w", pady=(0, 5))
        
        canvas_frame = tk.Frame(left_frame, relief=tk.SOLID, borderwidth=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_canvas = tk.Canvas(
            canvas_frame,
            bg="#F5F5F5",
            highlightthickness=0
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        list_label = tk.Label(
            right_frame,
            text="Available Monitors:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        list_label.pack(anchor="w", pady=(0, 5))
        
        listbox_frame = tk.Frame(right_frame, relief=tk.SOLID, borderwidth=1)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.monitor_listbox = tk.Listbox(
            listbox_frame,
            font=("Consolas", 9),
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            activestyle='dotbox'
        )
        self.monitor_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.monitor_listbox.yview)
        
        for i, monitor in enumerate(self.monitors):
            primary_text = " (Primary)" if monitor.is_primary else ""
            text = f"Monitor {i+1}: {monitor.width}x{monitor.height}{primary_text}"
            self.monitor_listbox.insert(tk.END, text)
            
        for i, monitor in enumerate(self.monitors):
            if monitor.is_primary:
                self.monitor_listbox.selection_set(i)
                self.monitor_listbox.activate(i)
                break
        else:
            if self.monitors:
                self.monitor_listbox.selection_set(0)
                self.monitor_listbox.activate(0)
        
        button_frame = tk.Frame(right_frame, bg="white")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=12,
            height=2,
            font=("Arial", 10)
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        select_btn = tk.Button(
            button_frame,
            text="Select",
            command=self._on_select,
            width=12,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.monitor_listbox.bind('<<ListboxSelect>>', self._on_selection_change)
        self.monitor_listbox.bind('<Double-Button-1>', lambda e: self._on_select())
        self.preview_canvas.bind('<Button-1>', self._on_canvas_click)
        self.preview_canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.dialog.after(100, self._draw_monitor_layout)
        
    def _on_canvas_configure(self, event):
        self.dialog.after_idle(self._draw_monitor_layout)
        
    def _draw_monitor_layout(self):
        self.preview_canvas.delete("all")
        
        if not self.monitors:
            return
            
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
            
        min_x = min(m.x for m in self.monitors)
        min_y = min(m.y for m in self.monitors)
        max_x = max(m.x + m.width for m in self.monitors)
        max_y = max(m.y + m.height for m in self.monitors)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        margin = 20
        available_width = canvas_width - 2 * margin
        available_height = canvas_height - 2 * margin
        
        if total_width == 0 or total_height == 0:
            return
            
        scale_x = available_width / total_width
        scale_y = available_height / total_height
        scale = min(scale_x, scale_y) * 0.9
        
        scaled_width = total_width * scale
        scaled_height = total_height * scale
        
        offset_x = (canvas_width - scaled_width) // 2
        offset_y = (canvas_height - scaled_height) // 2
        
        selection = self.monitor_listbox.curselection()
        selected_index = selection[0] if selection else 0
        
        self.canvas_rects = []
        
        for i, monitor in enumerate(self.monitors):
            x1 = (monitor.x - min_x) * scale + offset_x
            y1 = (monitor.y - min_y) * scale + offset_y
            x2 = x1 + monitor.width * scale
            y2 = y1 + monitor.height * scale
            
            is_selected = i == selected_index
            
            if is_selected:
                shadow_offset = 3
                self.preview_canvas.create_rectangle(
                    x1 + shadow_offset, y1 + shadow_offset, 
                    x2 + shadow_offset, y2 + shadow_offset,
                    fill="#CCCCCC", outline="", width=0
                )
            
            color = "#4CAF50" if is_selected else "#E3F2FD"
            outline = "#2E7D32" if is_selected else "#1976D2"
            width = 3 if is_selected else 2
            
            rect_id = self.preview_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=outline,
                width=width,
                tags=f"monitor_{i}"
            )
            
            self.canvas_rects.append((rect_id, i, x1, y1, x2, y2))
            
            primary_text = " (Primary)" if monitor.is_primary else ""
            label_text = f"Monitor {i+1}{primary_text}"
            
            self.preview_canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2 - 8,
                text=label_text,
                font=("Arial", int(10 * min(scale, 1.0)), "bold"),
                fill="white" if is_selected else "#1976D2"
            )
            
            resolution_text = f"{monitor.width}x{monitor.height}"
            self.preview_canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2 + 8,
                text=resolution_text,
                font=("Arial", int(8 * min(scale, 1.0))),
                fill="white" if is_selected else "#424242"
            )
            
    def _on_canvas_click(self, event):
        x, y = event.x, event.y
        
        for rect_id, monitor_index, x1, y1, x2, y2 in self.canvas_rects:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.monitor_listbox.selection_clear(0, tk.END)
                self.monitor_listbox.selection_set(monitor_index)
                self.monitor_listbox.activate(monitor_index)
                self._draw_monitor_layout()
                break
                
    def _on_selection_change(self, event):
        self._draw_monitor_layout()
        
    def _on_select(self):
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
        self.selected_monitor = None
        self.dialog.destroy()