import time
import logging
import threading
import random
import math

logger = logging.getLogger('PristonBot')

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

try:
    from app.windows_utils.mouse import press_right_mouse
except ImportError:
    try:
        from app.window_utils import press_right_mouse
    except ImportError:
        def press_right_mouse(*args, **kwargs):
            import ctypes
            try:
                MOUSEEVENTF_RIGHTDOWN = 0x0008
                MOUSEEVENTF_RIGHTUP = 0x0010
                
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                time.sleep(0.1)
                ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                
                return True
            except Exception as e:
                return False

from app.bar_selector import BarDetector, HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE

class BotCore:
    def __init__(self, hp_bar, mp_bar, sp_bar, settings_ui, log_callback):
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.settings_ui = settings_ui
        self.log_callback = log_callback
        
        self.hp_detector = BarDetector("Health", HEALTH_COLOR_RANGE)
        self.mp_detector = BarDetector("Mana", MANA_COLOR_RANGE)
        self.sp_detector = BarDetector("Stamina", STAMINA_COLOR_RANGE)
        
        self.running = False
        self.bot_thread = None
        
        self.prev_hp_percent = 100.0
        self.prev_mp_percent = 100.0
        self.prev_sp_percent = 100.0
        
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        self.game_window_rect = None
        
    def start(self):
        if self.running:
            logger.info("Bot already running")
            return False
        
        self.log_callback("Starting bot...")
        self.running = True
        
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        self.bot_thread = threading.Thread(target=self._bot_loop)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
        logger.info("Bot thread started")
        return True
    
    def stop(self):
        if not self.running:
            logger.info("Bot not running")
            return False
        
        self.log_callback("Stopping bot...")
        self.running = False
        
        if self.bot_thread:
            self.bot_thread.join(1.0)
            logger.info("Bot thread joined")
        
        return True
    
    def _find_and_setup_game_window(self):
        try:
            from app.config import load_config
            config = load_config()
            window_config = config.get("bars", {}).get("game_window", {})
            
            if window_config.get("configured", False):
                if all(window_config.get(key) is not None for key in ["x1", "y1", "x2", "y2"]):
                    x1 = window_config["x1"]
                    y1 = window_config["y1"]
                    x2 = window_config["x2"]
                    y2 = window_config["y2"]
                    
                    self.game_window_rect = (x1, y1, x2, y2)
                    self.log_callback(f"Game window found in configuration: ({x1},{y1})-({x2},{y2})")
                    logger.info(f"Game window loaded from config: ({x1},{y1})-({x2},{y2})")
                    return True
        except Exception as e:
            logger.error(f"Error loading game window from config: {e}")
        
        self.log_callback("WARNING: Game window could not be detected")
        logger.warning("Failed to find game window through any method")
        return False
    
    def _has_value_changed(self, prev_val, current_val, threshold=0.5):
        return abs(prev_val - current_val) >= threshold
    
    def _generate_random_target_offsets(self, radius):
        angle = random.uniform(0, 2 * math.pi)
        distance = radius * math.sqrt(random.random())
        
        x_offset = int(distance * math.cos(angle))
        y_offset = int(distance * math.sin(angle))
        
        logger.debug(f"Generated new random offset: ({x_offset}, {y_offset})")
        return x_offset, y_offset
    
    def _bot_loop(self):
        last_hp_potion = 0
        last_mp_potion = 0
        last_sp_potion = 0
        last_spell_cast = 0
        potion_cooldown = 3.0
        loop_count = 0
        
        self.log_callback("Bot started")
        logger.info("Bot loop started")
        
        game_window_found = self._find_and_setup_game_window()
        
        if not game_window_found:
            self.log_callback("WARNING: Game window not detected. Some functionality may not work properly.")
        
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
                
                hp_changed = self._has_value_changed(self.prev_hp_percent, hp_percent)
                mp_changed = self._has_value_changed(self.prev_mp_percent, mp_percent)
                sp_changed = self._has_value_changed(self.prev_sp_percent, sp_percent)
                
                if hp_changed or mp_changed or sp_changed:
                    status_message = (f"Health: {hp_percent:.1f}% | " +
                                    f"Mana: {mp_percent:.1f}% | " +
                                    f"Stamina: {sp_percent:.1f}%")
                    self.log_callback(status_message)
                    logger.debug(status_message)
                    
                    self.prev_hp_percent = hp_percent
                    self.prev_mp_percent = mp_percent
                    self.prev_sp_percent = sp_percent
                
                if hp_percent < hp_threshold and current_time - last_hp_potion > potion_cooldown:
                    hp_key = settings["potion_keys"]["health"]
                    self.log_callback(f"Health low ({hp_percent:.1f}%), using health potion (key {hp_key})")
                    logger.info(f"Using health potion - HP: {hp_percent:.1f}% < {hp_threshold}%")
                    press_key(None, hp_key)
                    last_hp_potion = current_time
                
                if mp_percent < mp_threshold and current_time - last_mp_potion > potion_cooldown:
                    mp_key = settings["potion_keys"]["mana"]
                    self.log_callback(f"Mana low ({mp_percent:.1f}%), using mana potion (key {mp_key})")
                    logger.info(f"Using mana potion - MP: {mp_percent:.1f}% < {mp_threshold}%")
                    press_key(None, mp_key)
                    last_mp_potion = current_time
                
                if sp_percent < sp_threshold and current_time - last_sp_potion > potion_cooldown:
                    sp_key = settings["potion_keys"]["stamina"]
                    self.log_callback(f"Stamina low ({sp_percent:.1f}%), using stamina potion (key {sp_key})")
                    logger.info(f"Using stamina potion - SP: {sp_percent:.1f}% < {sp_threshold}%")
                    press_key(None, sp_key)
                    last_sp_potion = current_time
                
                if settings["spellcasting"]["enabled"]:
                    spell_interval = settings["spellcasting"]["spell_interval"]
                    if current_time - last_spell_cast > spell_interval:
                        spell_key = settings["spellcasting"]["spell_key"]
                        
                        press_key(None, spell_key)
                        time.sleep(0.1)
                        
                        try:
                            press_right_mouse(None)
                        except Exception as e:
                            logger.error(f"Error with right-click: {e}")
                        
                        last_spell_cast = current_time
                
                scan_interval = settings["scan_interval"]
                time.sleep(scan_interval)
                
            except Exception as e:
                self.log_callback(f"Error in bot loop: {e}")
                logger.error(f"Error in bot loop: {e}", exc_info=True)
                time.sleep(1)
        
        self.log_callback("Bot stopped")
        logger.info("Bot loop stopped")