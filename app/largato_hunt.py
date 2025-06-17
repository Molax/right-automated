"""
Simple Largato Hunt Module with Image Comparison Logic
-----------------------------------------------------
Uses simple image comparison to detect when skill is stable (round finished).
"""

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
                    'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74
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

class SimpleSkillComparator:
    def __init__(self):
        self.logger = logging.getLogger('PristonBot')
        self.title = "Simple Skill Comparator"
        self.last_image = None
        self.stable_start_time = None
        self.required_stable_seconds = 4.0
        self.similarity_threshold = 0.90
        
        # Create debug directory
        self.debug_dir = "debug_images"
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
    
    def save_debug_image(self, image, filename):
        """Save image for debugging purposes"""
        try:
            if isinstance(image, np.ndarray):
                cv2.imwrite(os.path.join(self.debug_dir, filename), image)
            else:
                image.save(os.path.join(self.debug_dir, filename))
            self.logger.debug(f"Saved debug image: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving debug image: {e}")
    
    def images_are_similar(self, img1, img2):
        """Simple image comparison using mean squared error"""
        try:
            # Convert PIL images to numpy arrays if needed
            if hasattr(img1, 'size'):
                img1 = np.array(img1)
            if hasattr(img2, 'size'):
                img2 = np.array(img2)
            
            # Ensure images are the same size
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to grayscale for comparison
            if len(img1.shape) == 3:
                gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
            else:
                gray1 = img1
                
            if len(img2.shape) == 3:
                gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
            else:
                gray2 = img2
            
            # Calculate mean squared error
            mse = np.mean((gray1.astype(float) - gray2.astype(float)) ** 2)
            
            # Convert to similarity score (0-1, where 1 is identical)
            max_pixel_value = 255.0
            similarity = 1.0 - (mse / (max_pixel_value ** 2))
            similarity = max(0.0, similarity)
            
            self.logger.debug(f"Image similarity: {similarity:.3f} (threshold: {self.similarity_threshold})")
            
            return similarity >= self.similarity_threshold
            
        except Exception as e:
            self.logger.error(f"Error comparing images: {e}")
            return False
    
    def check_skill_stability(self, current_image):
        """Check if the skill has been stable for required time"""
        try:
            current_time = time.time()
            
            # Save current image for debugging
            timestamp = int(current_time)
            self.save_debug_image(current_image, f"skill_current_{timestamp}.png")
            
            # If this is the first image, just store it
            if self.last_image is None:
                self.last_image = np.array(current_image)
                self.stable_start_time = current_time
                self.logger.debug("First skill image captured, starting stability check")
                return False
            
            # Compare with last image
            if self.images_are_similar(current_image, self.last_image):
                # Images are similar
                if self.stable_start_time is None:
                    self.stable_start_time = current_time
                    self.logger.debug("Skill appears stable, starting timer")
                
                stable_duration = current_time - self.stable_start_time
                self.logger.debug(f"Skill stable for {stable_duration:.1f}s / {self.required_stable_seconds}s")
                
                if stable_duration >= self.required_stable_seconds:
                    self.logger.info(f"Skill has been stable for {stable_duration:.1f} seconds - Round complete!")
                    return True
            else:
                # Images are different - skill is changing
                if self.stable_start_time is not None:
                    stable_duration = current_time - self.stable_start_time
                    self.logger.debug(f"Skill changed after {stable_duration:.1f}s of stability")
                
                self.stable_start_time = None
                self.logger.debug("Skill is changing, resetting stability timer")
            
            # Update last image
            self.last_image = np.array(current_image)
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking skill stability: {e}")
            return False
    
    def reset_stability_check(self):
        """Reset the stability check for a new round"""
        self.last_image = None
        self.stable_start_time = None
        self.logger.debug("Reset skill stability check for new round")

class LargatoHunter:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.logger = logging.getLogger('PristonBot')
        
        self.running = False
        self.hunt_thread = None
        
        self.wood_stacks_destroyed = 0
        self.current_round = 1
        self.hunt_start_time = None
        
        self.skill_comparator = SimpleSkillComparator()
        self.skill_bar_selector = None
        
        self.hunt_phase = "initial"
        self.phase_start_time = 0
        
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
        """Get skill percentage for UI display"""
        if not self.skill_bar_selector or not self.skill_bar_selector.is_setup():
            return 0
            
        try:
            skill_image = self.skill_bar_selector.get_current_screenshot_region()
            if skill_image:
                # Simple percentage calculation for UI display
                np_image = np.array(skill_image)
                if np_image.size == 0:
                    return 0
                
                # Convert to grayscale and check how much is "active"
                gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
                active_pixels = np.sum(gray > 100)  # Pixels that aren't dark
                total_pixels = gray.size
                
                return (active_pixels / total_pixels) * 100 if total_pixels > 0 else 0
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
        self.skill_comparator.reset_stability_check()
        
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
                        self.log_callback("Initial wait complete, selecting main skill...")
                        press_key(None, 'f1')
                        time.sleep(0.2)
                        self.log_callback("Moving right...")
                        self.hunt_phase = "moving_right"
                        self.phase_start_time = current_time
                    else:
                        time.sleep(0.1)
                
                elif self.hunt_phase == "moving_right":
                    if phase_elapsed < 3.0:
                        press_key(None, 'right')
                        time.sleep(0.1)
                    else:
                        self.log_callback("Right movement complete, moving left to start position...")
                        self.hunt_phase = "moving_left"
                        self.phase_start_time = current_time
                
                elif self.hunt_phase == "moving_left":
                    if phase_elapsed < 0.4:
                        press_key(None, 'left')
                        time.sleep(0.1)
                    else:
                        self.log_callback("Positioning complete, starting attack phase...")
                        self.hunt_phase = "attacking"
                        self.phase_start_time = current_time
                        # Reset image comparison for this round
                        self.skill_comparator.reset_stability_check()
                
                elif self.hunt_phase == "attacking":
                    press_key(None, 'x')
                    time.sleep(0.4)
                    
                    if phase_elapsed >= 5.0:
                        self.log_callback("Attack phase duration reached, monitoring skill stability...")
                        self.hunt_phase = "monitoring_skill"
                        self.phase_start_time = current_time
                        # Reset for monitoring phase
                        self.skill_comparator.reset_stability_check()
                
                elif self.hunt_phase == "monitoring_skill":
                    press_key(None, 'x')
                    time.sleep(0.4)
                    
                    # Get current skill bar image
                    skill_image = self.skill_bar_selector.get_current_screenshot_region()
                    if skill_image:
                        # Check if skill is stable (round finished)
                        if self.skill_comparator.check_skill_stability(skill_image):
                            self.log_callback(f"Round {self.current_round} completed! Skill has been stable for 4+ seconds. Moving forward...")
                            self.hunt_phase = "round_complete"
                            self.phase_start_time = current_time
                            self.wood_stacks_destroyed += 1
                    else:
                        self.logger.warning("Could not capture skill bar image")
                
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
                        self.skill_comparator.reset_stability_check()
                
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