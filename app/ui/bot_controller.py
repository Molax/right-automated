"""
Fixed Bot Controller UI with proper bot functionality
--------------------------------------------------
Includes proper potion management and spellcasting.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import time
import random
import math
from PIL import Image

try:
    from app.windows_utils.mouse import move_mouse_direct, press_right_mouse
except ImportError:
    try:
        from app.window_utils import press_right_mouse, get_window_rect
    except ImportError:
        def press_right_mouse(*args, **kwargs):
            return False
        def get_window_rect(*args, **kwargs):
            return None
    
    def move_mouse_direct(x, y):
        import ctypes
        try:
            ctypes.windll.user32.SetCursorPos(int(x), int(y))
            return True
        except:
            return False

try:
    from app.windows_utils.keyboard import press_key
except ImportError:
    try:
        from app.window_utils import press_key
    except ImportError:
        def press_key(hwnd, key):
            import ctypes
            key_map = {
                '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
                '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
                'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
                'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
                'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
                'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
                'x': 0x58, 'space': 0x20, 'enter': 0x0D
            }
            
            if isinstance(key, str):
                key = key.lower()
                vk_code = key_map.get(key)
                if vk_code is None:
                    try:
                        vk_code = ord(key.upper()[0])
                    except:
                        return False
            else:
                vk_code = key
                
            try:
                KEYEVENTF_KEYDOWN = 0x0000
                KEYEVENTF_KEYUP = 0x0002
                
                ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYDOWN, 0)
                time.sleep(0.05)
                ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
                
                return True
            except Exception as e:
                return False

LARGATO_AVAILABLE = True
try:
    from app.largato_hunt import LargatoHunter
except:
    class LargatoHunter:
        def __init__(self, log_callback):
            self.log_callback = log_callback
            self.running = False
            self.wood_stacks_destroyed = 0
            self.current_round = 1
        
        def start_hunt(self):
            self.log_callback("ERROR: Largato Hunt module not available!")
            return False
        
        def stop_hunt(self):
            return True
            
        def set_skill_bar_selector(self, selector):
            pass
        
        def get_skill_percentage(self):
            return 0

from app.bar_selector import BarDetector, HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE
from app.config import load_config

logger = logging.getLogger('PristonBot')

class BotControllerUI:
    def __init__(self, parent, root, hp_bar, mp_bar, sp_bar, largato_skill_bar, settings_ui, log_callback):
        self.parent = parent
        self.root = root
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.largato_skill_bar = largato_skill_bar
        self.settings_ui = settings_ui
        self.log_callback = log_callback
        
        self.hp_detector = BarDetector("Health", HEALTH_COLOR_RANGE)
        self.mp_detector = BarDetector("Mana", MANA_COLOR_RANGE)
        self.sp_detector = BarDetector("Stamina", STAMINA_COLOR_RANGE)
        
        self.running = False
        self.bot_thread = None
        
        self.largato_running = False
        self.largato_hunter = LargatoHunter(self.log_callback)
        
        self.prev_hp_percent = 100.0
        self.prev_mp_percent = 100.0
        self.prev_sp_percent = 100.0
        
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        self.start_time = None
        
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        self.game_window = None
        self.game_window_rect = None
        self.game_hwnd = None
        
        self.target_zone_selector = None
        
        self._create_ui()
        self._setup_keyboard_shortcuts()
    
    def _create_ui(self):
        status_frame = ttk.Frame(self.parent)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Ready to configure")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        status_label.pack(side=tk.LEFT, padx=5)
        
        values_frame = ttk.Frame(self.parent)
        values_frame.pack(fill=tk.X, padx=5, pady=5)
        
        values_left = ttk.Frame(values_frame)
        values_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        values_right = ttk.Frame(values_frame)
        values_right.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        hp_frame = ttk.Frame(values_left)
        hp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_frame, text="Health:", foreground="#e74c3c", width=10).pack(side=tk.LEFT)
        self.hp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(hp_frame, textvariable=self.hp_value_var).pack(side=tk.LEFT)
        
        mp_frame = ttk.Frame(values_left)
        mp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_frame, text="Mana:", foreground="#3498db", width=10).pack(side=tk.LEFT)
        self.mp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(mp_frame, textvariable=self.mp_value_var).pack(side=tk.LEFT)
        
        hp_pot_frame = ttk.Frame(values_right)
        hp_pot_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(hp_pot_frame, text="HP Potions:", width=12).pack(side=tk.LEFT)
        self.hp_potions_var = tk.StringVar(value="0")
        ttk.Label(hp_pot_frame, textvariable=self.hp_potions_var).pack(side=tk.LEFT)
        
        mp_pot_frame = ttk.Frame(values_right)
        mp_pot_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(mp_pot_frame, text="MP Potions:", width=12).pack(side=tk.LEFT)
        self.mp_potions_var = tk.StringVar(value="0")
        ttk.Label(mp_pot_frame, textvariable=self.mp_potions_var).pack(side=tk.LEFT)
        
        sp_frame = ttk.Frame(values_left)
        sp_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_frame, text="Stamina:", foreground="#2ecc71", width=10).pack(side=tk.LEFT)
        self.sp_value_var = tk.StringVar(value="100.0%")
        ttk.Label(sp_frame, textvariable=self.sp_value_var).pack(side=tk.LEFT)
        
        runtime_frame = ttk.Frame(values_left)
        runtime_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(runtime_frame, text="Runtime:", width=10).pack(side=tk.LEFT)
        self.runtime_var = tk.StringVar(value="00:00:00")
        ttk.Label(runtime_frame, textvariable=self.runtime_var).pack(side=tk.LEFT)
        
        sp_pot_frame = ttk.Frame(values_right)
        sp_pot_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sp_pot_frame, text="SP Potions:", width=12).pack(side=tk.LEFT)
        self.sp_potions_var = tk.StringVar(value="0")
        ttk.Label(sp_pot_frame, textvariable=self.sp_potions_var).pack(side=tk.LEFT)
        
        spell_frame = ttk.Frame(values_right)
        spell_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(spell_frame, text="Spells Cast:", width=12).pack(side=tk.LEFT)
        self.spells_var = tk.StringVar(value="0")
        ttk.Label(spell_frame, textvariable=self.spells_var).pack(side=tk.LEFT)

        target_frame = ttk.Frame(values_right)
        target_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(target_frame, text="Target Offset:", width=12).pack(side=tk.LEFT)
        self.target_var = tk.StringVar(value="(0, 0)")
        ttk.Label(target_frame, textvariable=self.target_var).pack(side=tk.LEFT)
        
        largato_status_frame = ttk.Frame(values_right)
        largato_status_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(largato_status_frame, text="Largato Round:", width=12).pack(side=tk.LEFT)
        self.largato_round_var = tk.StringVar(value="0/4")
        ttk.Label(largato_status_frame, textvariable=self.largato_round_var).pack(side=tk.LEFT)
        
        skill_status_frame = ttk.Frame(values_left)
        skill_status_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(skill_status_frame, text="Skill Bar:", width=10).pack(side=tk.LEFT)
        self.skill_value_var = tk.StringVar(value="0.0%")
        ttk.Label(skill_status_frame, textvariable=self.skill_value_var).pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = tk.Button(
            button_frame, 
            text="START BOT\n(Ctrl+Shift+A)",
            command=self.start_bot, 
            bg="#4CAF50",
            fg="black",
            font=("Arial", 10, "bold"),
            height=2,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        largato_state = tk.NORMAL if LARGATO_AVAILABLE else tk.DISABLED
        largato_bg = "#FF9800" if LARGATO_AVAILABLE else "#a0a0a0"
        largato_text = "LARGATO HUNT\n(Ctrl+Shift+L)" if LARGATO_AVAILABLE else "LARGATO HUNT\n(Not Available)"
        
        self.largato_button = tk.Button(
            button_frame, 
            text=largato_text,
            command=self.start_largato_hunt, 
            bg=largato_bg,
            fg="black",
            font=("Arial", 10, "bold"),
            height=2,
            state=largato_state
        )
        self.largato_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.stop_button = tk.Button(
            button_frame, 
            text="STOP BOT\n(Ctrl+Shift+B)",
            command=self.stop_bot, 
            bg="#F44336",
            fg="black",
            font=("Arial", 10, "bold"),
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        shortcut_frame = ttk.Frame(self.parent)
        shortcut_frame.pack(fill=tk.X, pady=5)
        
        shortcut_text = "Shortcuts: Ctrl+Shift+A (Start), Ctrl+Shift+L (Largato Hunt), Ctrl+Shift+B (Stop)"
        if not LARGATO_AVAILABLE:
            shortcut_text += " - Largato Hunt requires proper module installation"
            
        shortcut_label = ttk.Label(
            shortcut_frame, 
            text=shortcut_text,
            font=("Arial", 8),
            foreground="#555555"
        )
        shortcut_label.pack(anchor=tk.CENTER)
    
    def _setup_keyboard_shortcuts(self):
        self.root.bind("<Control-Shift-a>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-A>", lambda event: self._handle_start_shortcut())
        self.root.bind("<Control-Shift-b>", lambda event: self._handle_stop_shortcut())
        self.root.bind("<Control-Shift-B>", lambda event: self._handle_stop_shortcut())
        
        if LARGATO_AVAILABLE:
            self.root.bind("<Control-Shift-l>", lambda event: self._handle_largato_shortcut())
            self.root.bind("<Control-Shift-L>", lambda event: self._handle_largato_shortcut())
        
        logger.info("Keyboard shortcuts registered")
        
    def _handle_start_shortcut(self):
        if not self.running and not self.largato_running and self.start_button.cget('state') != 'disabled':
            logger.info("Start bot shortcut (Ctrl+Shift+A) triggered")
            self.start_bot()
            
    def _handle_stop_shortcut(self):
        if self.running or self.largato_running:
            logger.info("Stop bot shortcut (Ctrl+Shift+B) triggered")
            self.stop_bot()
    
    def _handle_largato_shortcut(self):
        if not LARGATO_AVAILABLE:
            self.log_callback("Largato Hunt not available - module not properly installed")
            return
            
        if not self.running and not self.largato_running:
            logger.info("Largato hunt shortcut (Ctrl+Shift+L) triggered")
            self.start_largato_hunt()
        elif self.largato_running:
            logger.info("Stop Largato hunt shortcut (Ctrl+Shift+L) triggered")
            self.stop_largato_hunt()
    
    def start_largato_hunt(self):
        if not LARGATO_AVAILABLE:
            messagebox.showerror(
                "Largato Hunt Not Available",
                "Largato Hunt module is not properly installed.\n\n"
                "Please ensure the module is available and try again.",
                parent=self.root
            )
            return
            
        if self.running:
            messagebox.showwarning(
                "Bot Already Running",
                "Please stop the regular bot before starting Largato Hunt.",
                parent=self.root
            )
            return
            
        if self.largato_running:
            logger.info("Largato hunt button clicked, but hunt is already running")
            return
        
        skill_bar_configured = self._is_skill_bar_configured()
        logger.info(f"Skill bar configuration check result: {skill_bar_configured}")
        
        if not skill_bar_configured:
            messagebox.showerror(
                "Largato Skill Bar Not Configured",
                "Please configure the Largato skill bar first.\n\n"
                "Go to the Bar Selection tab and select the Largato skill bar.",
                parent=self.root
            )
            return
        
        self.log_callback("Starting Largato Hunt...")
        self.largato_running = True
        
        self.largato_round_var.set("1/4")
        
        self.largato_hunter.set_skill_bar_selector(self.largato_skill_bar)
        success = self.largato_hunter.start_hunt()
        
        if success:
            self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
            self.largato_button.config(text="STOP LARGATO\n(Ctrl+Shift+L)", bg="#F44336")
            self.stop_button.config(state=tk.NORMAL, bg="#F44336")
            
            self.status_var.set("Largato Hunt is running")
            
            self._update_largato_progress()
        else:
            self.largato_running = False
            self.log_callback("Failed to start Largato Hunt")
    
    def _is_skill_bar_configured(self):
        if not self.largato_skill_bar:
            logger.debug("Largato skill bar is None")
            return False
        
        if hasattr(self.largato_skill_bar, 'is_setup'):
            result = self.largato_skill_bar.is_setup()
            logger.debug(f"Largato skill bar is_setup() returned: {result}")
            if result:
                return True
        
        if hasattr(self.largato_skill_bar, 'x1'):
            has_coords = (self.largato_skill_bar.x1 is not None and 
                        self.largato_skill_bar.y1 is not None and
                        self.largato_skill_bar.x2 is not None and
                        self.largato_skill_bar.y2 is not None)
            logger.debug(f"Largato skill bar coordinate check: {has_coords}")
            return has_coords
        
        logger.debug("Largato skill bar has no recognizable setup method or coordinates")
        return False
    
    def stop_largato_hunt(self):
        if not self.largato_running:
            return
        
        self.log_callback("Stopping Largato Hunt...")
        
        success = self.largato_hunter.stop_hunt()
        
        if success:
            self.largato_running = False
            
            if LARGATO_AVAILABLE:
                self.largato_button.config(text="LARGATO HUNT\n(Ctrl+Shift+L)", bg="#FF9800")
            else:
                self.largato_button.config(text="LARGATO HUNT\n(Not Available)", bg="#a0a0a0")
            self.stop_button.config(state=tk.DISABLED, bg="#a0a0a0")
            
            if self._can_enable_start_button():
                self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
            
            self.status_var.set("Largato Hunt stopped")
    
    def _update_largato_progress(self):
        if self.largato_running and self.largato_hunter:
            round_count = self.largato_hunter.current_round
            self.largato_round_var.set(f"{round_count}/4")
            
            skill_percentage = 0
            if self.largato_skill_bar and self._is_skill_bar_configured():
                skill_percentage = self.largato_hunter.get_skill_percentage()
                self.skill_value_var.set(f"{skill_percentage:.1f}%")
            
            if not self.largato_hunter.running:
                self.largato_running = False
                
                if LARGATO_AVAILABLE:
                    self.largato_button.config(text="LARGATO HUNT\n(Ctrl+Shift+L)", bg="#FF9800")
                else:
                    self.largato_button.config(text="LARGATO HUNT\n(Not Available)", bg="#a0a0a0")
                self.stop_button.config(state=tk.DISABLED, bg="#a0a0a0")
                
                if self._can_enable_start_button():
                    self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
                
                if round_count >= 4:
                    self.status_var.set("Largato Hunt completed!")
                else:
                    self.status_var.set("Largato Hunt stopped")
                
                return
            
            self.root.after(1000, self._update_largato_progress)
    
    def start_bot(self):
        if self.largato_running:
            messagebox.showwarning(
                "Largato Hunt Running",
                "Please stop Largato Hunt before starting the regular bot.",
                parent=self.root
            )
            return
            
        if self.running:
            logger.info("Start button clicked, but bot is already running")
            return
        
        self.log_callback("Starting bot...")
        self.running = True
        
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        self.spells_cast = 0
        
        self.hp_potions_var.set("0")
        self.mp_potions_var.set("0")
        self.sp_potions_var.set("0")
        self.spells_var.set("0")
        
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        self.start_time = time.time()
        
        self._update_runtime()
        
        self.bot_thread = threading.Thread(target=self.bot_loop)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        logger.info("Bot thread started")
        
        self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
        if LARGATO_AVAILABLE:
            self.largato_button.config(state=tk.DISABLED, bg="#a0a0a0")
        self.stop_button.config(state=tk.NORMAL, bg="#F44336")
        
        self.status_var.set("Bot is running")
    
    def stop_bot(self):
        stopped_something = False
        
        if self.running:
            self.log_callback("Stopping bot...")
            self.running = False
            if self.bot_thread:
                self.bot_thread.join(1.0)
                logger.info("Bot thread joined")
            stopped_something = True
        
        if self.largato_running:
            self.stop_largato_hunt()
            stopped_something = True
        
        if not stopped_something:
            logger.info("Stop button clicked, but no bot is running")
            return
        
        self.stop_button.config(state=tk.DISABLED, bg="#a0a0a0")
        
        if LARGATO_AVAILABLE:
            self.largato_button.config(text="LARGATO HUNT\n(Ctrl+Shift+L)", bg="#FF9800", state=tk.NORMAL)
        else:
            self.largato_button.config(text="LARGATO HUNT\n(Not Available)", bg="#a0a0a0", state=tk.DISABLED)
        
        if self._can_enable_start_button():
            self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
        
        self.status_var.set("All bots stopped")
    
    def _can_enable_start_button(self):
        configured = 0
        if hasattr(self, 'hp_bar') and self.hp_bar and hasattr(self.hp_bar, 'is_setup') and self.hp_bar.is_setup():
            configured += 1
        if hasattr(self, 'mp_bar') and self.mp_bar and hasattr(self.mp_bar, 'is_setup') and self.mp_bar.is_setup():
            configured += 1
        if hasattr(self, 'sp_bar') and self.sp_bar and hasattr(self.sp_bar, 'is_setup') and self.sp_bar.is_setup():
            configured += 1
        
        return configured == 3
    
    def _update_runtime(self):
        if self.running and self.start_time:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            self.runtime_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            self.root.after(1000, self._update_runtime)
    
    def enable_start_button(self):
        if not self.largato_running:
            self.start_button.config(state=tk.NORMAL, bg="#4CAF50")
            self.status_var.set("Ready to start")
    
    def disable_start_button(self):
        self.start_button.config(state=tk.DISABLED, bg="#a0a0a0")
    
    def set_status(self, message):
        self.status_var.set(message)
    
    def has_value_changed(self, prev_val, current_val, threshold=0.5):
        return abs(prev_val - current_val) >= threshold
    
    def generate_random_target_offsets(self, radius):
        angle = random.uniform(0, 2 * math.pi)
        distance = radius * math.sqrt(random.random())
        
        x_offset = int(distance * math.cos(angle))
        y_offset = int(distance * math.sin(angle))
        
        logger.debug(f"Generated new random offset: ({x_offset}, {y_offset})")
        return x_offset, y_offset
    
    def bot_loop(self):
        last_hp_potion = 0
        last_mp_potion = 0
        last_sp_potion = 0
        last_spell_cast = 0
        potion_cooldown = 3.0
        loop_count = 0
        
        self.log_callback("Bot started")
        logger.info("Bot loop started")
        
        while self.running:
            try:
                loop_count += 1
                logger.debug(f"Bot loop iteration {loop_count}")
                
                current_time = time.time()
                
                settings = self.settings_ui.get_settings()
                
                hp_percent = 100.0
                mp_percent = 100.0
                sp_percent = 100.0
                hp_threshold = settings["thresholds"]["health"]
                mp_threshold = settings["thresholds"]["mana"]
                sp_threshold = settings["thresholds"]["stamina"]
                
                if self.hp_bar and hasattr(self.hp_bar, 'is_setup') and self.hp_bar.is_setup():
                    hp_image = self.hp_bar.get_current_screenshot_region()
                    if hp_image:
                        hp_percent = self.hp_detector.detect_percentage(hp_image)
                
                if self.mp_bar and hasattr(self.mp_bar, 'is_setup') and self.mp_bar.is_setup():
                    mp_image = self.mp_bar.get_current_screenshot_region()
                    if mp_image:
                        mp_percent = self.mp_detector.detect_percentage(mp_image)
                
                if self.sp_bar and hasattr(self.sp_bar, 'is_setup') and self.sp_bar.is_setup():
                    sp_image = self.sp_bar.get_current_screenshot_region()
                    if sp_image:
                        sp_percent = self.sp_detector.detect_percentage(sp_image)
                
                hp_changed = self.has_value_changed(self.prev_hp_percent, hp_percent)
                mp_changed = self.has_value_changed(self.prev_mp_percent, mp_percent)
                sp_changed = self.has_value_changed(self.prev_sp_percent, sp_percent)
                
                if hp_changed or mp_changed or sp_changed:
                    status_message = (f"Health: {hp_percent:.1f}% | " +
                                    f"Mana: {mp_percent:.1f}% | " +
                                    f"Stamina: {sp_percent:.1f}%")
                    self.log_callback(status_message)
                    logger.debug(status_message)
                    
                    self.prev_hp_percent = hp_percent
                    self.prev_mp_percent = mp_percent
                    self.prev_sp_percent = sp_percent
                    
                    self.hp_value_var.set(f"{hp_percent:.1f}%")
                    self.mp_value_var.set(f"{mp_percent:.1f}%")
                    self.sp_value_var.set(f"{sp_percent:.1f}%")
                
                if hp_percent < hp_threshold and current_time - last_hp_potion > potion_cooldown:
                    hp_key = settings["potion_keys"]["health"]
                    self.log_callback(f"Health low ({hp_percent:.1f}%), using health potion (key {hp_key})")
                    logger.info(f"Using health potion - HP: {hp_percent:.1f}% < {hp_threshold}%")
                    press_key(None, hp_key)
                    last_hp_potion = current_time
                    
                    self.hp_potions_used += 1
                    self.hp_potions_var.set(str(self.hp_potions_used))
                
                if mp_percent < mp_threshold and current_time - last_mp_potion > potion_cooldown:
                    mp_key = settings["potion_keys"]["mana"]
                    self.log_callback(f"Mana low ({mp_percent:.1f}%), using mana potion (key {mp_key})")
                    logger.info(f"Using mana potion - MP: {mp_percent:.1f}% < {mp_threshold}%")
                    press_key(None, mp_key)
                    last_mp_potion = current_time
                    
                    self.mp_potions_used += 1
                    self.mp_potions_var.set(str(self.mp_potions_used))
                
                if sp_percent < sp_threshold and current_time - last_sp_potion > potion_cooldown:
                    sp_key = settings["potion_keys"]["stamina"]
                    self.log_callback(f"Stamina low ({sp_percent:.1f}%), using stamina potion (key {sp_key})")
                    logger.info(f"Using stamina potion - SP: {sp_percent:.1f}% < {sp_threshold}%")
                    press_key(None, sp_key)
                    last_sp_potion = current_time
                    
                    self.sp_potions_used += 1
                    self.sp_potions_var.set(str(self.sp_potions_used))
                
                if settings["spellcasting"]["enabled"]:
                    spell_interval = settings["spellcasting"]["spell_interval"]
                    if current_time - last_spell_cast > spell_interval:
                        spell_key = settings["spellcasting"]["spell_key"]
                        
                        logger.info(f"Casting spell: {spell_key}")
                        press_key(None, spell_key)
                        
                        time.sleep(0.1)
                        
                        try:
                            press_right_mouse(None)
                        except Exception as e:
                            logger.error(f"Error with right-click: {e}")
                        
                        last_spell_cast = current_time
                        self.spells_cast += 1
                        self.spells_var.set(str(self.spells_cast))
                
                scan_interval = settings["scan_interval"]
                time.sleep(scan_interval)
                
            except Exception as e:
                self.log_callback(f"Error in bot loop: {e}")
                logger.error(f"Error in bot loop: {e}", exc_info=True)
                time.sleep(1)
        
        self.log_callback("Bot stopped")
        logger.info("Bot loop stopped")