import time
import logging
import threading
import os
from PIL import ImageGrab, Image
import numpy as np
import cv2

logger = logging.getLogger('PristonBot')

def get_press_key_function():
    try:
        from app.windows_utils.keyboard import press_key
        return press_key
    except ImportError:
        try:
            from app.window_utils import press_key
            return press_key
        except ImportError:
            import ctypes
            def press_key(hwnd, key):
                key_map = {
                    'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
                    'x': 0x58, 'space': 0x20, 'enter': 0x0D, 'f1': 0x70,
                    'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75
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
                    logger.error(f"Error pressing key '{key}': {e}")
                    return False
            return press_key

press_key = get_press_key_function()

def get_press_right_mouse_function():
    try:
        from app.windows_utils.mouse import press_right_mouse
        return press_right_mouse
    except ImportError:
        try:
            from app.window_utils import press_right_mouse
            return press_right_mouse
        except ImportError:
            import ctypes
            def press_right_mouse(hwnd=None, target_x=None, target_y=None):
                try:
                    MOUSEEVENTF_RIGHTDOWN = 0x0008
                    MOUSEEVENTF_RIGHTUP = 0x0010
                    
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                    time.sleep(0.1)
                    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
                    
                    return True
                except Exception as e:
                    logger.error(f"Error with right click: {e}")
                    return False
            return press_right_mouse

press_right_mouse = get_press_right_mouse_function()

class AdvancedSkillDetector:
    def __init__(self):
        self.logger = logging.getLogger('PristonBot')
        self.title = "Advanced Skill Detector"
        self.previous_images = []
        self.max_history = 10
        self.stable_start_time = None
        self.required_stable_seconds = 1.0
        self.change_threshold = 0.02
        self.samples_since_change = 0
        self.min_samples_for_stability = 8
        
        self.debug_dir = "debug_images"
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
    
    def save_debug_image(self, image, filename):
        try:
            if isinstance(image, np.ndarray):
                cv2.imwrite(os.path.join(self.debug_dir, filename), image)
            else:
                image.save(os.path.join(self.debug_dir, filename))
            self.logger.debug(f"Saved debug image: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving debug image: {e}")
    
    def extract_skill_core(self, image):
        if hasattr(image, 'size'):
            image = np.array(image)
        
        height, width = image.shape[:2]
        
        center_y = height // 2
        center_x = width // 2
        
        core_height = max(4, height // 3)
        core_width = max(4, width // 2)
        
        y1 = max(0, center_y - core_height // 2)
        y2 = min(height, center_y + core_height // 2)
        x1 = max(0, center_x - core_width // 2)
        x2 = min(width, center_x + core_width // 2)
        
        core_region = image[y1:y2, x1:x2]
        
        if len(core_region.shape) == 3:
            core_region = cv2.cvtColor(core_region, cv2.COLOR_RGB2GRAY)
        
        return core_region
    
    def calculate_image_variance(self, image):
        try:
            core = self.extract_skill_core(image)
            
            mean_value = np.mean(core)
            variance = np.var(core)
            
            histogram = cv2.calcHist([core], [0], None, [16], [0, 256])
            hist_variance = np.var(histogram)
            
            combined_variance = variance + (hist_variance * 0.1)
            
            return combined_variance, mean_value
        except Exception as e:
            self.logger.error(f"Error calculating variance: {e}")
            return 0.0, 0.0
    
    def detect_skill_change(self, current_image):
        try:
            current_time = time.time()
            timestamp = int(current_time)
            
            self.save_debug_image(current_image, f"skill_advanced_{timestamp}_{len(self.previous_images)}.png")
            
            current_variance, current_mean = self.calculate_image_variance(current_image)
            
            if len(self.previous_images) == 0:
                self.previous_images.append((current_variance, current_mean, current_time))
                self.logger.debug(f"First sample: variance={current_variance:.3f}, mean={current_mean:.1f}")
                return False
            
            if len(self.previous_images) < 3:
                self.previous_images.append((current_variance, current_mean, current_time))
                self.logger.debug(f"Collecting samples: {len(self.previous_images)}/3")
                return False
            
            recent_variances = [v for v, m, t in self.previous_images[-3:]]
            recent_means = [m for v, m, t in self.previous_images[-3:]]
            
            variance_change = abs(current_variance - np.mean(recent_variances)) / (np.mean(recent_variances) + 1)
            mean_change = abs(current_mean - np.mean(recent_means)) / (np.mean(recent_means) + 1)
            
            total_change = variance_change + mean_change
            
            self.logger.debug(f"Variance: {current_variance:.3f}, Mean: {current_mean:.1f}, Change: {total_change:.4f}")
            
            if total_change > self.change_threshold:
                self.samples_since_change = 0
                self.stable_start_time = None
                self.logger.debug(f"Significant change detected (change={total_change:.4f} > {self.change_threshold})")
                change_detected = True
            else:
                self.samples_since_change += 1
                
                if self.stable_start_time is None and self.samples_since_change >= 3:
                    self.stable_start_time = current_time
                    self.logger.info("Skill appears stable, starting stability timer")
                
                change_detected = False
            
            self.previous_images.append((current_variance, current_mean, current_time))
            
            if len(self.previous_images) > self.max_history:
                self.previous_images.pop(0)
            
            if self.stable_start_time is not None:
                stable_duration = current_time - self.stable_start_time
                self.logger.info(f"Skill stable for {stable_duration:.1f}s / {self.required_stable_seconds}s (samples: {self.samples_since_change})")
                
                if stable_duration >= self.required_stable_seconds and self.samples_since_change >= self.min_samples_for_stability:
                    self.logger.info(f"ROUND COMPLETE! Stable for {stable_duration:.1f}s with {self.samples_since_change} stable samples")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in skill change detection: {e}")
            return False
    
    def reset_for_new_round(self):
        self.previous_images = []
        self.stable_start_time = None
        self.samples_since_change = 0
        self.logger.info("Reset advanced skill detector for new round")

class LargatoHunter:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.logger = logging.getLogger('PristonBot')
        
        self.running = False
        self.hunt_thread = None
        
        self.wood_stacks_destroyed = 0
        self.current_round = 1
        self.hunt_start_time = None
        
        self.skill_detector = AdvancedSkillDetector()
        self.skill_bar_selector = None
        
        self.hunt_phase = "initial"
        self.phase_start_time = 0
        
        self.game_window_rect = None
        
        self.hp_bar_selector = None
        self.mp_bar_selector = None
        self.sp_bar_selector = None
        self.settings_provider = None
        
        self.hp_detector = None
        self.mp_detector = None
        self.sp_detector = None
        
        self.last_hp_potion = 0
        self.last_mp_potion = 0
        self.last_sp_potion = 0
        
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        
        self.movement_config = {
            "round_1": {
                "right_duration": 0.0,
                "left_duration": 0.4,
                "forward_presses": 0
            },
            "round_2": {
                "right_duration": 22.0,
                "left_duration": 0.4,
                "forward_presses": 15
            },
            "round_3": {
                "right_duration": 8.5,
                "left_duration": 0.4,
                "forward_presses": 8
            },
            "round_4": {
                "right_duration": 16.0,
                "left_duration": 0.4,
                "forward_presses": 12
            }
        }
    
    def set_potion_system(self, hp_bar, mp_bar, sp_bar, settings_provider):
        self.hp_bar_selector = hp_bar
        self.mp_bar_selector = mp_bar
        self.sp_bar_selector = sp_bar
        self.settings_provider = settings_provider
        
        try:
            from app.bar_selector import BarDetector, HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE
            self.hp_detector = BarDetector("Health", HEALTH_COLOR_RANGE)
            self.mp_detector = BarDetector("Mana", MANA_COLOR_RANGE)
            self.sp_detector = BarDetector("Stamina", STAMINA_COLOR_RANGE)
            self.logger.info("Potion system configured for Largato Hunt")
        except Exception as e:
            self.logger.error(f"Error setting up potion system: {e}")
        
    def set_skill_bar_selector(self, skill_bar_selector):
        self.skill_bar_selector = skill_bar_selector
        self.logger.info("Largato skill bar selector configured")
        
    def find_game_window(self):
        try:
            from app.config import load_config
            config = load_config()
            window_config = config.get("bars", {}).get("game_window", {})
            
            if window_config.get("configured", False):
                x1 = window_config["x1"]
                y1 = window_config["y1"]
                x2 = window_config["x2"]
                y2 = window_config["y2"]
                
                self.game_window_rect = (x1, y1, x2, y2)
                self.logger.info(f"Game window found: ({x1},{y1})-({x2},{y2})")
                return True
                
        except Exception as e:
            self.logger.error(f"Error finding game window: {e}")
        
        self.game_window_rect = None
        self.logger.warning("Using full screen as fallback")
        return False
    
    def get_skill_percentage(self):
        if not self.skill_bar_selector or not self.skill_bar_selector.is_setup():
            return 0
            
        try:
            skill_image = self.skill_bar_selector.get_current_screenshot_region()
            if skill_image:
                np_image = np.array(skill_image)
                if np_image.size == 0:
                    return 0
                
                gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
                active_pixels = np.sum(gray > 100)
                total_pixels = gray.size
                
                return (active_pixels / total_pixels) * 100 if total_pixels > 0 else 0
            return 0
        except Exception as e:
            self.logger.error(f"Error getting skill percentage: {e}")
            return 0
    
    def check_and_use_potions(self):
        if not all([self.hp_bar_selector, self.mp_bar_selector, self.sp_bar_selector, 
                   self.settings_provider, self.hp_detector, self.mp_detector, self.sp_detector]):
            return
            
        try:
            current_time = time.time()
            settings = self.settings_provider.get_settings()
            potion_cooldown = settings.get("potion_cooldown", 3.0)
            
            hp_threshold = settings["thresholds"]["health"]
            mp_threshold = settings["thresholds"]["mana"]
            sp_threshold = settings["thresholds"]["stamina"]
            
            if self.hp_bar_selector.is_setup():
                hp_image = self.hp_bar_selector.get_current_screenshot_region()
                if hp_image:
                    hp_percent = self.hp_detector.detect_percentage(hp_image)
                    if hp_percent < hp_threshold and current_time - self.last_hp_potion > potion_cooldown:
                        hp_key = settings["potion_keys"]["health"]
                        press_key(None, hp_key)
                        self.last_hp_potion = current_time
                        self.hp_potions_used += 1
                        self.log_callback(f"Used health potion ({hp_percent:.1f}%)")
            
            if self.mp_bar_selector.is_setup():
                mp_image = self.mp_bar_selector.get_current_screenshot_region()
                if mp_image:
                    mp_percent = self.mp_detector.detect_percentage(mp_image)
                    if mp_percent < mp_threshold and current_time - self.last_mp_potion > potion_cooldown:
                        mp_key = settings["potion_keys"]["mana"]
                        press_key(None, mp_key)
                        self.last_mp_potion = current_time
                        self.mp_potions_used += 1
                        self.log_callback(f"Used mana potion ({mp_percent:.1f}%)")
            
            if self.sp_bar_selector.is_setup():
                sp_image = self.sp_bar_selector.get_current_screenshot_region()
                if sp_image:
                    sp_percent = self.sp_detector.detect_percentage(sp_image)
                    if sp_percent < sp_threshold and current_time - self.last_sp_potion > potion_cooldown:
                        sp_key = settings["potion_keys"]["stamina"]
                        press_key(None, sp_key)
                        self.last_sp_potion = current_time
                        self.sp_potions_used += 1
                        self.log_callback(f"Used stamina potion ({sp_percent:.1f}%)")
                        
        except Exception as e:
            self.logger.error(f"Error checking potions: {e}")
    
    def enhanced_movement_right(self, phase_elapsed, movement_duration, forward_presses):
        """Enhanced right movement with proper forward movement and varied patterns"""
        total_cycles = int(movement_duration / 0.08)
        current_cycle = int(phase_elapsed / 0.08) % max(1, total_cycles)
        
        # More aggressive movement patterns
        if current_cycle % 15 == 0:
            # Every 15 cycles, do multiple forward presses
            for _ in range(3):
                press_key(None, 'up')
                time.sleep(0.02)
        elif current_cycle % 12 == 0:
            # Occasional down movement for positioning
            for _ in range(2):
                press_key(None, 'down')
                time.sleep(0.02)
        elif current_cycle % 8 == 0:
            # Regular forward movement
            press_key(None, 'up')
            time.sleep(0.02)
        elif current_cycle % 10 == 0:
            # Slight down adjustment
            press_key(None, 'down')
            time.sleep(0.02)
        
        # Continuous right movement
        press_key(None, 'right')
        time.sleep(0.03)
        
        # Add extra forward presses based on round requirements
        if current_cycle % 20 == 0 and forward_presses > 0:
            additional_forward = min(forward_presses // 4, 5)
            for _ in range(additional_forward):
                press_key(None, 'up')
                time.sleep(0.02)
    
    def perform_movement_sequence(self, round_num, phase_elapsed):
        """Perform movement based on round-specific configuration"""
        config = self.movement_config.get(f"round_{round_num}", self.movement_config["round_4"])
        
        right_duration = config["right_duration"]
        left_duration = config["left_duration"]
        forward_presses = config["forward_presses"]
        
        self.logger.debug(f"Round {round_num} movement: right={right_duration}s, left={left_duration}s, forward={forward_presses}")
        
        if phase_elapsed < right_duration:
            self.enhanced_movement_right(phase_elapsed, right_duration, forward_presses)
            return False  # Still moving right
        else:
            return True  # Right movement complete
    
    def perform_left_positioning(self, phase_elapsed, left_duration=0.4):
        """Perform left positioning movement"""
        if phase_elapsed < left_duration:
            # More aggressive left movement
            for _ in range(2):
                press_key(None, 'left')
                time.sleep(0.02)
            return False
        else:
            return True
    
    def start_hunt(self):
        if self.running:
            self.logger.info("Hunt already running")
            return False
        
        if not self.skill_bar_selector or not self.skill_bar_selector.is_setup():
            self.log_callback("ERROR: Largato skill bar not configured! Please configure it first.")
            return False
        
        self.running = True
        self.wood_stacks_destroyed = 0
        self.current_round = 1
        self.hunt_start_time = time.time()
        self.hunt_phase = "initial"
        self.phase_start_time = time.time()
        self.skill_detector.reset_for_new_round()
        
        self.last_hp_potion = 0
        self.last_mp_potion = 0
        self.last_sp_potion = 0
        self.hp_potions_used = 0
        self.mp_potions_used = 0
        self.sp_potions_used = 0
        
        self.hunt_thread = threading.Thread(target=self.hunt_loop)
        self.hunt_thread.daemon = True
        self.hunt_thread.start()
        
        self.log_callback("Enhanced Largato Hunt started with improved movement!")
        self.logger.info("Enhanced Largato hunt thread started")
        return True
    
    def stop_hunt(self):
        if not self.running:
            self.logger.info("Hunt not running")
            return False
        
        self.running = False
        if self.hunt_thread:
            self.hunt_thread.join(1.0)
            self.logger.info("Hunt thread joined")
        
        if self.hunt_start_time:
            duration = time.time() - self.hunt_start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.log_callback(f"Hunt stopped. Duration: {minutes}m {seconds}s, Round: {self.current_round}")
            self.log_callback(f"Potions used: HP({self.hp_potions_used}) MP({self.mp_potions_used}) SP({self.sp_potions_used})")
        
        self.log_callback("Enhanced Largato Hunt stopped!")
        self.logger.info("Enhanced Largato hunt stopped")
        return True
    
    def hunt_loop(self):
        self.log_callback(f"Starting Enhanced Largato Hunt Round {self.current_round} with improved movement...")
        self.logger.info("Enhanced Largato hunt loop started")
        
        self.find_game_window()
        
        while self.running:
            try:
                current_time = time.time()
                phase_elapsed = current_time - self.phase_start_time
                
                self.check_and_use_potions()
                
                if self.hunt_phase == "initial":
                    if phase_elapsed >= 3.0:
                        if self.current_round == 1:
                            self.log_callback("Round 1 preparation: casting F5 skills...")
                            self.hunt_phase = "round1_f5_cast1"
                        else:
                            self.log_callback("Initial preparation complete, selecting main skill...")
                            press_key(None, 'f1')
                            time.sleep(0.3)
                            self.log_callback(f"Round {self.current_round}: Moving right with enhanced movement...")
                            self.hunt_phase = "moving_right"
                        self.phase_start_time = current_time
                    else:
                        time.sleep(0.1)
                
                elif self.hunt_phase == "round1_f5_cast1":
                    press_key(None, 'f5')
                    time.sleep(0.1)
                    press_right_mouse()
                    time.sleep(0.1)
                    press_right_mouse()
                    self.log_callback("First F5 cast complete, waiting...")
                    self.hunt_phase = "round1_wait1"
                    self.phase_start_time = current_time
                
                elif self.hunt_phase == "round1_wait1":
                    if phase_elapsed >= 1.5:
                        self.log_callback("Casting F6 skills...")
                        self.hunt_phase = "round1_f6_cast1"
                        self.phase_start_time = current_time
                
                elif self.hunt_phase == "round1_f6_cast1":
                    press_key(None, 'f6')
                    time.sleep(0.1)
                    press_right_mouse()
                    time.sleep(0.1)
                    press_right_mouse()
                    self.log_callback("First F6 cast complete, waiting...")
                    self.hunt_phase = "round1_wait2"
                    self.phase_start_time = current_time
                
                elif self.hunt_phase == "round1_wait2":
                    if phase_elapsed >= 1.5:
                        self.log_callback("Casting second F6 skills...")
                        self.hunt_phase = "round1_f6_cast2"
                        self.phase_start_time = current_time
                
                elif self.hunt_phase == "round1_f6_cast2":
                    press_key(None, 'f6')
                    time.sleep(0.1)
                    press_right_mouse()
                    time.sleep(0.1)
                    press_right_mouse()
                    self.log_callback("Second F6 cast complete, waiting...")
                    self.hunt_phase = "round1_wait3"
                    self.phase_start_time = current_time
                
                elif self.hunt_phase == "round1_wait3":
                    if phase_elapsed >= 1.5:
                        self.log_callback("Selecting main skill for Round 1...")
                        press_key(None, 'f1')
                        time.sleep(0.3)
                        self.log_callback("Round 1: Moving left to position for attack...")
                        self.hunt_phase = "round1_moving_left"
                        self.phase_start_time = current_time
                
                elif self.hunt_phase == "round1_moving_left":
                    if self.perform_left_positioning(phase_elapsed, 0.4):
                        self.log_callback("Round 1 positioning complete, beginning attack sequence...")
                        self.hunt_phase = "attacking"
                        self.phase_start_time = current_time
                        self.skill_detector.reset_for_new_round()
                
                elif self.hunt_phase == "moving_right":
                    if self.perform_movement_sequence(self.current_round, phase_elapsed):
                        self.log_callback(f"Round {self.current_round}: Right movement complete, positioning for attack...")
                        self.hunt_phase = "moving_left"
                        self.phase_start_time = current_time
                
                elif self.hunt_phase == "moving_left":
                    if self.perform_left_positioning(phase_elapsed, 0.4):
                        self.log_callback(f"Round {self.current_round}: Positioning complete, beginning attack sequence...")
                        self.hunt_phase = "attacking"
                        self.phase_start_time = current_time
                        self.skill_detector.reset_for_new_round()
                
                elif self.hunt_phase == "attacking":
                    press_key(None, 'x')
                    time.sleep(0.5)
                    
                    if phase_elapsed >= 10.0:
                        self.log_callback(f"Round {self.current_round}: Attack phase established, monitoring for completion...")
                        self.hunt_phase = "monitoring_skill"
                        self.phase_start_time = current_time
                        self.skill_detector.reset_for_new_round()
                
                elif self.hunt_phase == "monitoring_skill":
                    press_key(None, 'x')
                    time.sleep(0.5)
                    
                    skill_image = self.skill_bar_selector.get_current_screenshot_region()
                    if skill_image:
                        if self.skill_detector.detect_skill_change(skill_image):
                            self.log_callback(f"Round {self.current_round} COMPLETED! Skill activity ceased. Advancing...")
                            self.hunt_phase = "round_complete"
                            self.phase_start_time = current_time
                            self.wood_stacks_destroyed += 1
                    else:
                        self.logger.warning("Could not capture skill bar image during monitoring")
                
                elif self.hunt_phase == "round_complete":
                    forward_movement_duration = 6.0
                    
                    if phase_elapsed < forward_movement_duration:
                        # Enhanced forward movement between rounds
                        if phase_elapsed < 2.0:
                            # First 2 seconds: aggressive forward movement
                            for _ in range(3):
                                press_key(None, 'up')
                                time.sleep(0.02)
                            time.sleep(0.1)
                        elif phase_elapsed < 4.0:
                            # Next 2 seconds: mixed forward/right movement
                            press_key(None, 'up')
                            time.sleep(0.02)
                            press_key(None, 'right')
                            time.sleep(0.02)
                        else:
                            # Final 2 seconds: prepare for next round
                            press_key(None, 'up')
                            time.sleep(0.05)
                    else:
                        self.current_round += 1
                        self.log_callback(f"Advancing to Round {self.current_round} with enhanced movement...")
                        
                        if self.current_round > 4:
                            self.log_callback("All 4 rounds completed successfully! Hunt finished.")
                            break
                        
                        self.hunt_phase = "moving_right"
                        self.phase_start_time = current_time
                        self.skill_detector.reset_for_new_round()
                
            except Exception as e:
                self.log_callback(f"Error in enhanced hunt loop: {e}")
                self.logger.error(f"Error in enhanced hunt loop: {e}", exc_info=True)
                time.sleep(1.0)
        
        if self.current_round > 4:
            duration = time.time() - self.hunt_start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.log_callback(f"Enhanced Largato Hunt completed successfully! Duration: {minutes}m {seconds}s")
            self.log_callback(f"Total potions used: HP({self.hp_potions_used}) MP({self.mp_potions_used}) SP({self.sp_potions_used})")
            self.logger.info("Enhanced Largato hunt completed successfully")
        else:
            self.log_callback("Enhanced Largato Hunt stopped before completion.")
            self.logger.info("Enhanced Largato hunt stopped by user")
        
        self.running = False