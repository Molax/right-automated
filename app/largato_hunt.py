"""
Enhanced Largato Hunt Module for Priston Tale Potion Bot
-------------------------------------------------------
Redesigned for first round logic with skill bar detection integration.
"""

import time
import logging
import threading
import random
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
                    logger.error(f"Error pressing key '{key}': {e}")
                    return False
            return press_key

press_key = get_press_key_function()

class LargatoSkillDetector:
    def __init__(self):
        self.logger = logging.getLogger('PristonBot')
        self.title = "Largato Skill"
        
    def detect_percentage(self, image):
        try:
            np_image = np.array(image)
            hsv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
            
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
            
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
            
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            mask3 = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
            
            combined_mask = mask1 | mask2 | mask3
            
            kernel = np.ones((3, 3), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            
            total_pixels = combined_mask.shape[0] * combined_mask.shape[1]
            if total_pixels == 0:
                return 0
                
            filled_pixels = cv2.countNonZero(combined_mask)
            percentage = (filled_pixels / total_pixels) * 100
            
            gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
            dark_pixels = np.sum(gray < 50)
            dark_ratio = dark_pixels / total_pixels
            
            if dark_ratio > 0.7:
                percentage = 0
                self.logger.debug(f"Largato skill appears greyed out (dark ratio: {dark_ratio:.2f})")
            
            self.logger.debug(f"Largato skill percentage: {percentage:.1f}%")
            return percentage
            
        except Exception as e:
            self.logger.error(f"Error detecting Largato skill percentage: {e}")
            return 0

class LargatoHunter:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.logger = logging.getLogger('PristonBot')
        
        self.running = False
        self.hunt_thread = None
        
        self.wood_stacks_destroyed = 0
        self.current_round = 1
        self.hunt_start_time = None
        
        self.skill_detector = LargatoSkillDetector()
        self.skill_bar_selector = None
        
        self.hunt_phase = "initial"
        self.phase_start_time = 0
        self.skill_full_start_time = 0
        self.skill_was_full = False
        
        self.game_window_rect = None
        
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
            self.logger.warning("Skill bar not configured")
            return 0
            
        try:
            skill_image = self.skill_bar_selector.get_current_screenshot_region()
            if skill_image:
                return self.skill_detector.detect_percentage(skill_image)
            return 0
        except Exception as e:
            self.logger.error(f"Error getting skill percentage: {e}")
            return 0
    
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
        self.skill_full_start_time = 0
        self.skill_was_full = False
        
        self.hunt_thread = threading.Thread(target=self.hunt_loop)
        self.hunt_thread.daemon = True
        self.hunt_thread.start()
        
        self.log_callback("Largato Hunt started! Round 1 beginning...")
        self.logger.info("Largato hunt thread started")
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
        
        self.log_callback("Largato Hunt stopped!")
        self.logger.info("Largato hunt stopped")
        return True
    
    def hunt_loop(self):
        self.log_callback(f"Starting Largato Hunt Round {self.current_round}...")
        self.logger.info("Largato hunt loop started")
        
        self.find_game_window()
        
        while self.running:
            try:
                current_time = time.time()
                phase_elapsed = current_time - self.phase_start_time
                
                if self.hunt_phase == "initial":
                    if phase_elapsed >= 2.0:
                        self.log_callback("Initial wait complete, moving right...")
                        self.hunt_phase = "moving_right"
                        self.phase_start_time = current_time
                    else:
                        time.sleep(0.1)
                
                elif self.hunt_phase == "moving_right":
                    if phase_elapsed < 3.0:
                        press_key(None, 'right')
                        time.sleep(0.1)
                    else:
                        self.log_callback("Movement complete, starting attack phase...")
                        self.hunt_phase = "attacking"
                        self.phase_start_time = current_time
                
                elif self.hunt_phase == "attacking":
                    press_key(None, 'x')
                    time.sleep(0.4)
                    
                    if phase_elapsed >= 5.0:
                        self.log_callback("Attack phase duration reached, checking skill bar...")
                        self.hunt_phase = "monitoring_skill"
                        self.phase_start_time = current_time
                        self.skill_full_start_time = 0
                        self.skill_was_full = False
                
                elif self.hunt_phase == "monitoring_skill":
                    press_key(None, 'x')
                    time.sleep(0.4)
                    
                    skill_percentage = self.get_skill_percentage()
                    
                    if skill_percentage >= 90:
                        if not self.skill_was_full:
                            self.skill_was_full = True
                            self.skill_full_start_time = current_time
                            self.log_callback(f"Skill bar is full! Monitoring for 2.8 seconds...")
                        
                        skill_full_duration = current_time - self.skill_full_start_time
                        
                        if skill_full_duration >= 2.8:
                            self.log_callback(f"Round {self.current_round} completed! Moving forward...")
                            self.hunt_phase = "round_complete"
                            self.phase_start_time = current_time
                            self.wood_stacks_destroyed += 1
                    else:
                        if self.skill_was_full:
                            self.log_callback("Skill bar no longer full, continuing attack...")
                        self.skill_was_full = False
                        self.skill_full_start_time = 0
                
                elif self.hunt_phase == "round_complete":
                    if phase_elapsed < 5.0:
                        press_key(None, 'right')
                        time.sleep(0.1)
                    else:
                        self.current_round += 1
                        self.log_callback(f"Starting Round {self.current_round}...")
                        
                        if self.current_round > 4:
                            self.log_callback("All 4 rounds completed! Hunt finished.")
                            break
                        
                        self.hunt_phase = "moving_right"
                        self.phase_start_time = current_time
                
            except Exception as e:
                self.log_callback(f"Error in hunt loop: {e}")
                self.logger.error(f"Error in hunt loop: {e}", exc_info=True)
                time.sleep(1.0)
        
        if self.current_round > 4:
            self.log_callback("Largato Hunt completed successfully!")
            self.logger.info("Largato hunt completed successfully")
        else:
            self.log_callback("Largato Hunt stopped before completion.")
            self.logger.info("Largato hunt stopped by user")
        
        self.running = False