# Save this as mouse_test.py in the root directory of your project

import tkinter as tk
from tkinter import ttk, messagebox
import time
import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mouse_test_log.txt')
    ]
)

logger = logging.getLogger('MouseTest')

# Add the app directory to path
sys.path.append(os.path.abspath('.'))

# Import the mouse functions
from app.windows_utils.mouse import press_right_mouse, press_left_mouse

class MouseTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Movement Test Tool")
        self.root.geometry("500x400")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Mouse Movement Test Tool", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Coordinates section
        coords_frame = ttk.LabelFrame(main_frame, text="Target Coordinates", padding=10)
        coords_frame.pack(fill=tk.X, pady=10)
        
        # X coordinate
        x_frame = ttk.Frame(coords_frame)
        x_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(x_frame, text="X Coordinate:", width=15).pack(side=tk.LEFT)
        self.x_var = tk.StringVar(value="500")
        ttk.Entry(x_frame, textvariable=self.x_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(x_frame, text="Current", command=self.get_current_x).pack(side=tk.LEFT, padx=5)
        
        # Y coordinate
        y_frame = ttk.Frame(coords_frame)
        y_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(y_frame, text="Y Coordinate:", width=15).pack(side=tk.LEFT)
        self.y_var = tk.StringVar(value="500")
        ttk.Entry(y_frame, textvariable=self.y_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(y_frame, text="Current", command=self.get_current_y).pack(side=tk.LEFT, padx=5)
        
        # Actions section
        actions_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        actions_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        buttons_frame = ttk.Frame(actions_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="Move Mouse", command=self.move_mouse).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Right Click", command=self.right_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Left Click", command=self.left_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Test Sequence", command=self.test_sequence).pack(side=tk.LEFT, padx=5)
        
        # Restore checkbox
        restore_frame = ttk.Frame(actions_frame)
        restore_frame.pack(fill=tk.X, pady=5)
        
        self.restore_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(restore_frame, text="Restore cursor position after action", 
                        variable=self.restore_var).pack(anchor=tk.W)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Log initial message
        self.log("Mouse Movement Test Tool initialized")
    
    def log(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        logger.info(message)
    
    def get_current_x(self):
        """Get current mouse X coordinate"""
        try:
            import win32gui
            cursor_info = win32gui.GetCursorInfo()
            x, y = cursor_info[2]
            self.x_var.set(str(x))
            self.log(f"Current X coordinate: {x}")
        except Exception as e:
            self.log(f"Error getting current X coordinate: {e}")
    
    def get_current_y(self):
        """Get current mouse Y coordinate"""
        try:
            import win32gui
            cursor_info = win32gui.GetCursorInfo()
            x, y = cursor_info[2]
            self.y_var.set(str(y))
            self.log(f"Current Y coordinate: {y}")
        except Exception as e:
            self.log(f"Error getting current Y coordinate: {e}")
    
    def move_mouse(self):
        """Move the mouse to the specified coordinates"""
        try:
            import ctypes
            
            # Get target coordinates
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
            except ValueError:
                self.log("Error: Coordinates must be integers")
                return
            
            # Save original position if restore is checked
            original_pos = None
            if self.restore_var.get():
                import win32gui
                cursor_info = win32gui.GetCursorInfo()
                original_pos = cursor_info[2]
                self.log(f"Saved original position: {original_pos}")
            
            # Move cursor
            self.log(f"Moving cursor to ({x}, {y})")
            ctypes.windll.user32.SetCursorPos(x, y)
            
            # Wait before restoring
            time.sleep(1.0)
            
            # Restore position if needed
            if self.restore_var.get() and original_pos:
                self.log(f"Restoring cursor to {original_pos}")
                ctypes.windll.user32.SetCursorPos(original_pos[0], original_pos[1])
                
        except Exception as e:
            self.log(f"Error moving mouse: {e}")
    
    def right_click(self):
        """Perform a right click at the specified coordinates"""
        try:
            # Get target coordinates
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
            except ValueError:
                self.log("Error: Coordinates must be integers")
                return
            
            # Perform right click
            self.log(f"Right clicking at ({x}, {y})")
            result = press_right_mouse(None, x, y)
            self.log(f"Right click result: {'Success' if result else 'Failed'}")
                
        except Exception as e:
            self.log(f"Error performing right click: {e}")
    
    def left_click(self):
        """Perform a left click at the specified coordinates"""
        try:
            # Get target coordinates
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
            except ValueError:
                self.log("Error: Coordinates must be integers")
                return
            
            # Perform left click
            self.log(f"Left clicking at ({x}, {y})")
            result = press_left_mouse(None, x, y)
            self.log(f"Left click result: {'Success' if result else 'Failed'}")
                
        except Exception as e:
            self.log(f"Error performing left click: {e}")
    
    def test_sequence(self):
        """Run a test sequence of mouse movements"""
        try:
            import win32gui
            import ctypes
            
            # Save original position
            cursor_info = win32gui.GetCursorInfo()
            original_pos = cursor_info[2]
            self.log(f"Starting test sequence. Original position: {original_pos}")
            
            # Get screen dimensions
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            
            # Test positions: center, top-left, top-right, bottom-right, bottom-left
            test_positions = [
                (screen_width // 2, screen_height // 2),  # Center
                (100, 100),                               # Top-left
                (screen_width - 100, 100),                # Top-right
                (screen_width - 100, screen_height - 100),# Bottom-right
                (100, screen_height - 100)                # Bottom-left
            ]
            
            for i, (x, y) in enumerate(test_positions):
                self.log(f"Test {i+1}/5: Moving to ({x}, {y})")
                ctypes.windll.user32.SetCursorPos(x, y)
                time.sleep(0.5)
            
            # Restore original position
            self.log(f"Test sequence complete. Restoring to {original_pos}")
            ctypes.windll.user32.SetCursorPos(original_pos[0], original_pos[1])
            
        except Exception as e:
            self.log(f"Error during test sequence: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTestApp(root)
    root.mainloop()