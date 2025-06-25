"""
Fixed Monitor Selection Dialog
----------------------------
Simplified dialog for monitor selection.
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
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Monitor")
        
        dialog_width = 500
        dialog_height = 300
        
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.dialog.resizable(False, False)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self._create_ui()
        
        self.dialog.lift()
        self.dialog.focus_force()
        
        self.parent.wait_window(self.dialog)
        
        return self.selected_monitor
        
    def _create_ui(self):
        main_frame = tk.Frame(self.dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(
            main_frame,
            text="Multiple Monitors Detected",
            font=("Arial", 14, "bold"),
            bg="white"
        )
        title_label.pack(pady=(0, 10))
        
        instructions = tk.Label(
            main_frame,
            text="Please select which monitor to use for bar selection:",
            font=("Arial", 10),
            bg="white"
        )
        instructions.pack(pady=(0, 15))
        
        list_frame = tk.Frame(main_frame, relief=tk.SOLID, borderwidth=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.monitor_listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 10),
            selectmode=tk.SINGLE,
            height=len(self.monitors) + 1
        )
        self.monitor_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        for monitor in self.monitors:
            self.monitor_listbox.insert(tk.END, str(monitor))
            
        for i, monitor in enumerate(self.monitors):
            if monitor.is_primary:
                self.monitor_listbox.selection_set(i)
                break
        else:
            if self.monitors:
                self.monitor_listbox.selection_set(0)
        
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=12,
            height=2
        )
        cancel_btn.pack(side=tk.LEFT)
        
        select_btn = tk.Button(
            button_frame,
            text="Select Monitor",
            command=self._on_select,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        select_btn.pack(side=tk.RIGHT)
        
        self.monitor_listbox.bind('<Double-Button-1>', lambda e: self._on_select())
        
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