#!/usr/bin/env python3
"""
Priston Tale Potion Bot - Main Entry Point
-----------------------------------------
Launch the bot application with proper configuration.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import time

def setup_logging():
    """Set up enhanced logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger('PristonBot')
    logger.setLevel(logging.INFO)
    
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    from logging.handlers import RotatingFileHandler
    log_file = os.path.join('logs', f'priston_bot_{time.strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    
    logger.info("Logging initialized")
    return logger

def check_dependencies():
    """Check for required libraries with detailed error reporting"""
    missing_libs = []
    
    dependencies = [
        ('win32gui', 'pywin32', 'Windows GUI functions'),
        ('cv2', 'opencv-python', 'Image processing'),
        ('numpy', 'numpy', 'Numerical operations'),
        ('PIL', 'pillow', 'Image handling')
    ]
    
    for module_name, package_name, purpose in dependencies:
        try:
            __import__(module_name)
        except ImportError:
            missing_libs.append((package_name, purpose))
    
    return missing_libs

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to log unhandled exceptions"""
    logger = logging.getLogger('PristonBot')
    logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def create_splash_screen():
    """Create a splash screen while loading the application"""
    splash = tk.Tk()
    splash.overrideredirect(True)
    
    width, height = 400, 250
    screen_width = splash.winfo_screenwidth()
    screen_height = splash.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")
    
    frame = ttk.Frame(splash, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    title_label = ttk.Label(frame, text="Priston Tale Bot", font=("Arial", 16, "bold"))
    title_label.pack(pady=(10, 5))
    
    version_label = ttk.Label(frame, text="Version 1.0.0", font=("Arial", 10))
    version_label.pack(pady=5)
    
    loading_label = ttk.Label(frame, text="Loading application...", font=("Arial", 10))
    loading_label.pack(pady=20)
    
    progress = ttk.Progressbar(frame, mode="indeterminate", length=300)
    progress.pack(pady=10)
    progress.start()
    
    copyright_label = ttk.Label(frame, text="© 2023 Priston Tale Bot", font=("Arial", 8))
    copyright_label.pack(pady=10)
    
    splash.update()
    return splash

def main():
    """Main application entry point"""
    splash = create_splash_screen()
    
    logger = setup_logging()
    
    sys.excepthook = handle_exception
    
    logger.info("Starting Priston Tale Potion Bot application")
    
    missing_libs = check_dependencies()
    if missing_libs:
        splash.destroy()
        
        error_message = "The following required libraries are missing:\n\n"
        for lib, purpose in missing_libs:
            error_message += f"• {lib} - {purpose}\n"
        
        error_message += "\nPlease install them using:\n"
        error_message += "pip install " + " ".join([lib for lib, _ in missing_libs])
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Missing Dependencies", error_message)
            root.destroy()
        except:
            print("ERROR: Missing dependencies")
            print(error_message)
            
        sys.exit(1)
    
    for directory in ["logs", "debug_images"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    try:
        time.sleep(1.5)
        
        from app.gui import PristonTaleBot
        
        splash.destroy()
        
        root = tk.Tk()
        root.title("Priston Tale Potion Bot")
        
        try:
            icon_path = "resources/potion_icon.ico"
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
            else:
                logger.info("Icon file not found")
        except Exception as e:
            logger.warning(f"Could not set application icon: {e}")
        
        app = PristonTaleBot(root)
        
        root.update_idletasks()
        root.minsize(root.winfo_width(), root.winfo_height())
        
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Fatal error during initialization: {e}", exc_info=True)
        
        try:
            splash.destroy()
        except:
            pass
            
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error", 
                f"A fatal error occurred while starting the application:\n\n{e}\n\nPlease check the logs for details."
            )
            root.destroy()
        except:
            print(f"FATAL ERROR: {e}")
            
        sys.exit(1)

if __name__ == "__main__":
    main()