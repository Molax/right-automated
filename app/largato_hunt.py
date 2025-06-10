"""
Improved Largato Hunt Module for Priston Tale Potion Bot
-----------------------------------------------------
Enhanced wood detection accuracy and faster movement system.
"""

import time
import logging
import threading
import random
import os

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from PIL import ImageGrab, Image, ImageDraw

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
                logger = logging.getLogger('PristonBot')
                
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
                            logger.error(f"Could not determine virtual key code for '{key}'")
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
logger = logging.getLogger('PristonBot')

class LargatoHunter:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.logger = logging.getLogger('PristonBot')
        
        self.running = False
        self.hunt_thread = None
        
        self.wood_stacks_destroyed = 0
        self.total_attacks = 0
        self.hunt_start_time = None
        
        self.last_move_direction = 'right'
        self.movement_variation = 0
        
        self.wood_stack_template = None
        self.destroyed_wood_template = None
        self.load_reference_images()
        
        self.game_window_rect = None
        
        self.detection_confidence_threshold = 0.7
        self.false_positive_counter = 0
        self.max_false_positives = 3
        
        self.last_wood_detection_time = 0
        self.wood_detection_cooldown = 5.0
        
    def load_reference_images(self):
        if not OPENCV_AVAILABLE:
            self.logger.warning("OpenCV not available - using fallback detection")
            return
            
        try:
            wood_paths = ["wood_detailed.png", "largato_tronco.png", "wood_found.png"]
            for wood_path in wood_paths:
                if os.path.exists(wood_path):
                    self.wood_stack_template = cv2.imread(wood_path, cv2.IMREAD_COLOR)
                    self.logger.info(f"Loaded wood stack template: {wood_path}")
                    break
            else:
                self.logger.warning("No wood stack template found")
            
            destroyed_path = "largato_tronco_destruido.png"
            if os.path.exists(destroyed_path):
                self.destroyed_wood_template = cv2.imread(destroyed_path, cv2.IMREAD_COLOR)
                self.logger.info("Loaded destroyed wood template")
            else:
                self.logger.warning(f"Destroyed wood template not found: {destroyed_path}")
                
        except Exception as e:
            self.logger.error(f"Error loading reference images: {e}")
    
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
                self.logger.info(f"Game window found in config: ({x1},{y1})-({x2},{y2})")
                return True
                
        except Exception as e:
            self.logger.error(f"Error finding game window: {e}")
        
        self.game_window_rect = None
        self.logger.warning("Using full screen capture as fallback")
        return False
    
    def capture_game_screen(self):
        try:
            if self.game_window_rect:
                screenshot = ImageGrab.grab(bbox=self.game_window_rect)
            else:
                screenshot = ImageGrab.grab()
            
            if OPENCV_AVAILABLE:
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                return screenshot_cv
            else:
                return np.array(screenshot)
            
        except Exception as e:
            self.logger.error(f"Error capturing screen: {e}")
            return None
    
    def find_wood_stack(self, screenshot):
        screen_height, screen_width = screenshot.shape[:2]
        self.logger.debug(f"Analyzing screenshot of size {screen_width}x{screen_height}")
        
        if OPENCV_AVAILABLE:
            try:
                self.logger.debug("Starting template matching...")
                if self.wood_stack_template is not None:
                    try:
                        best_match = 0
                        best_location = None
                        best_scale = 1.0
                        
                        scales = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
                        
                        for scale in scales:
                            if scale != 1.0:
                                h, w = self.wood_stack_template.shape[:2]
                                new_h, new_w = int(h * scale), int(w * scale)
                                if new_h <= 0 or new_w <= 0 or new_h >= screen_height or new_w >= screen_width:
                                    continue
                                scaled_template = cv2.resize(self.wood_stack_template, (new_w, new_h))
                            else:
                                scaled_template = self.wood_stack_template
                            
                            if (scaled_template.shape[0] >= screenshot.shape[0] or 
                                scaled_template.shape[1] >= screenshot.shape[1]):
                                continue
                            
                            result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            
                            if max_val > best_match:
                                best_match = max_val
                                h, w = scaled_template.shape[:2]
                                center_x = max_loc[0] + w // 2
                                center_y = max_loc[1] + h // 2
                                best_location = (center_x, center_y)
                                best_scale = scale
                        
                        if best_match >= 0.25:
                            self.logger.info(f"WOOD DETECTED by template matching at {best_location}")
                            self.logger.info(f"Confidence: {best_match:.3f}, Scale: {best_scale:.1f}")
                            
                            self.save_detection_debug_image(screenshot, best_location, best_match, "wood_template_detected")
                            return True, best_location[0], best_location[1], best_match
                        else:
                            self.logger.debug(f"Template matching failed, best confidence: {best_match:.3f}")
                            
                    except Exception as e:
                        self.logger.error(f"Template matching error: {e}")
                
                self.logger.debug("Starting aggressive wood detection...")
                
                hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
                
                wood_ranges = [
                    ([0, 20, 40], [40, 255, 255]),
                    ([5, 30, 50], [35, 255, 200]),
                    ([8, 40, 60], [25, 200, 180]),
                    ([10, 50, 80], [30, 180, 160]),
                    ([6, 25, 45], [32, 240, 220])
                ]
                
                combined_mask = None
                for i, (lower, upper) in enumerate(wood_ranges):
                    lower_np = np.array(lower)
                    upper_np = np.array(upper)
                    mask = cv2.inRange(hsv, lower_np, upper_np)
                    
                    if combined_mask is None:
                        combined_mask = mask
                    else:
                        combined_mask = cv2.bitwise_or(combined_mask, mask)
                
                kernel = np.ones((2, 2), np.uint8)
                combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
                
                total_wood_pixels = cv2.countNonZero(combined_mask)
                self.logger.debug(f"Total wood-colored pixels found: {total_wood_pixels}")
                
                if total_wood_pixels > 300:
                    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    valid_wood_areas = []
                    for contour in contours:
                        area = cv2.contourArea(contour)
                        if area > 200:
                            x, y, w, h = cv2.boundingRect(contour)
                            
                            if x > screen_width * 0.6:
                                center_x = x + w // 2
                                center_y = y + h // 2
                                
                                roi = screenshot[max(0, y-10):min(screen_height, y+h+10), 
                                                max(0, x-10):min(screen_width, x+w+10)]
                                
                                if roi.size > 0:
                                    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                                    brown_mask_roi = cv2.inRange(hsv_roi, np.array([5, 40, 60]), np.array([25, 200, 180]))
                                    brown_density = cv2.countNonZero(brown_mask_roi) / (roi.shape[0] * roi.shape[1])
                                    
                                    if brown_density > 0.2:
                                        valid_wood_areas.append((center_x, center_y, area, brown_density, w, h))
                    
                    if valid_wood_areas:
                        valid_wood_areas.sort(key=lambda x: x[2], reverse=True)
                        center_x, center_y, area, density, w, h = valid_wood_areas[0]
                        
                        confidence = min(0.9, 0.4 + (area / 1500) + (density * 2))
                        
                        self.logger.info(f"WOOD DETECTED by color analysis at ({center_x}, {center_y})")
                        self.logger.info(f"Area: {area}, Density: {density:.3f}, Size: {w}x{h}, Confidence: {confidence:.3f}")
                        
                        self.save_detection_debug_image(screenshot, (center_x, center_y), confidence, "wood_color_detected")
                        return True, center_x, center_y, confidence
                
                self.logger.debug("Trying circle detection for log ends...")
                gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
                
                circles = cv2.HoughCircles(
                    gray, cv2.HOUGH_GRADIENT, 1, 15,
                    param1=50, param2=35, minRadius=8, maxRadius=25
                )
                
                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    self.logger.debug(f"Found {len(circles)} total circles")
                    
                    if len(circles) > 100:
                        self.logger.debug("Too many circles detected, filtering more strictly")
                        circles = circles[:50]
                    
                    wood_circles = []
                    
                    for (x, y, r) in circles:
                        if x > screen_width * 0.6 and x < screen_width and y < screen_height:
                            roi_margin = 3
                            roi_x1 = max(0, x - r - roi_margin)
                            roi_y1 = max(0, y - r - roi_margin)
                            roi_x2 = min(screen_width, x + r + roi_margin)
                            roi_y2 = min(screen_height, y + r + roi_margin)
                            
                            roi = screenshot[roi_y1:roi_y2, roi_x1:roi_x2]
                            if roi.size > 20:
                                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                                brown_mask = cv2.inRange(hsv_roi, np.array([5, 40, 60]), np.array([25, 200, 180]))
                                brown_ratio = cv2.countNonZero(brown_mask) / (roi.shape[0] * roi.shape[1])
                                
                                if brown_ratio > 0.3:
                                    wood_circles.append((x, y, r, brown_ratio))
                    
                    self.logger.debug(f"Found {len(wood_circles)} valid wood circles")
                    
                    if len(wood_circles) >= 5:
                        wood_circles.sort(key=lambda x: x[3], reverse=True)
                        
                        top_circles = wood_circles[:min(8, len(wood_circles))]
                        avg_x = sum([c[0] for c in top_circles]) // len(top_circles)
                        avg_y = sum([c[1] for c in top_circles]) // len(top_circles)
                        
                        confidence = 0.6 + min(0.3, len(wood_circles) * 0.02)
                        
                        self.logger.info(f"WOOD DETECTED by circle analysis at ({avg_x}, {avg_y})")
                        self.logger.info(f"Found {len(wood_circles)} wood circles, Confidence: {confidence:.3f}")
                        
                        self.save_detection_debug_image(screenshot, (avg_x, avg_y), confidence, "wood_circles_detected")
                        return True, avg_x, avg_y, confidence
                
                self.logger.debug("Trying pixel clustering as final attempt...")
                right_section = screenshot[:, int(screen_width * 0.6):]
                hsv_right = cv2.cvtColor(right_section, cv2.COLOR_BGR2HSV)
                
                brown_mask = cv2.inRange(hsv_right, np.array([5, 40, 60]), np.array([25, 200, 180]))
                brown_pixels = cv2.countNonZero(brown_mask)
                
                self.logger.debug(f"Brown pixels in right section: {brown_pixels}")
                
                if brown_pixels > 800:
                    y_indices, x_indices = np.where(brown_mask > 0)
                    if len(x_indices) > 0 and len(y_indices) > 0:
                        center_x = int(np.mean(x_indices)) + int(screen_width * 0.6)
                        center_y = int(np.mean(y_indices))
                        
                        confidence = min(0.7, 0.4 + (brown_pixels / 5000))
                        
                        self.logger.info(f"WOOD DETECTED by pixel clustering at ({center_x}, {center_y})")
                        self.logger.info(f"Brown pixels: {brown_pixels}, Confidence: {confidence:.3f}")
                        
                        self.save_detection_debug_image(screenshot, (center_x, center_y), confidence, "wood_pixel_cluster")
                        return True, center_x, center_y, confidence
                
            except Exception as e:
                self.logger.error(f"Error in wood detection: {e}", exc_info=True)
        
        self.logger.debug("ALL DETECTION METHODS FAILED - No wood found")
        
        try:
            self.save_detection_debug_image(screenshot, None, 0.0, "no_wood_detected")
        except:
            pass
        
        return False, 0, 0, 0
    
    def is_wood_destroyed(self, screenshot):
        screen_height, screen_width = screenshot.shape[:2]
        right_corner_region = screenshot[:, int(screen_width * 0.65):]
        
        if not OPENCV_AVAILABLE or self.destroyed_wood_template is None:
            return False
        
        try:
            scales = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
            best_match = 0
            
            for scale in scales:
                if scale != 1.0:
                    h, w = self.destroyed_wood_template.shape[:2]
                    new_h, new_w = int(h * scale), int(w * scale)
                    scaled_template = cv2.resize(self.destroyed_wood_template, (new_w, new_h))
                else:
                    scaled_template = self.destroyed_wood_template
                
                if (scaled_template.shape[0] > right_corner_region.shape[0] or 
                    scaled_template.shape[1] > right_corner_region.shape[1]):
                    continue
                
                result = cv2.matchTemplate(right_corner_region, scaled_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_match:
                    best_match = max_val
            
            threshold = 0.5
            
            if best_match >= threshold:
                self.logger.info(f"Destroyed wood detected with confidence {best_match:.3f}")
                self.save_detection_debug_image(screenshot, None, best_match, "wood_destroyed")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in destroyed wood detection: {e}")
            return False
    
    def save_detection_debug_image(self, screenshot, location, confidence, prefix):
        try:
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            timestamp = time.strftime("%H%M%S")
            filename = f"{debug_dir}/{prefix}_{timestamp}_conf{confidence:.2f}.png"
            
            if location:
                debug_img = screenshot.copy()
                cv2.circle(debug_img, location, 20, (0, 255, 0), 3)
                cv2.putText(debug_img, f"{confidence:.2f}", 
                           (location[0] - 30, location[1] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imwrite(filename, debug_img)
            else:
                cv2.imwrite(filename, screenshot)
            
            self.logger.debug(f"Saved debug image: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving debug image: {e}")
        screen_height, screen_width = screenshot.shape[:2]
        right_corner_region = screenshot[:, int(screen_width * 0.65):]
        
        wood_still_there = False
        destroyed_wood_there = False
        
        if OPENCV_AVAILABLE and self.wood_stack_template is not None:
            try:
                scales = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
                best_match = 0
                
                for scale in scales:
                    if scale != 1.0:
                        h, w = self.wood_stack_template.shape[:2]
                        new_h, new_w = int(h * scale), int(w * scale)
                        scaled_template = cv2.resize(self.wood_stack_template, (new_w, new_h))
                    else:
                        scaled_template = self.wood_stack_template
                    
                    if (scaled_template.shape[0] > right_corner_region.shape[0] or 
                        scaled_template.shape[1] > right_corner_region.shape[1]):
                        continue
                    
                    result = cv2.matchTemplate(right_corner_region, scaled_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val > best_match:
                        best_match = max_val
                
                if best_match >= 0.5:
                    wood_still_there = True
                    self.logger.debug(f"Original wood still detected with confidence {best_match:.3f}")
                
            except Exception as e:
                self.logger.error(f"Error checking original wood: {e}")
        
        if OPENCV_AVAILABLE and self.destroyed_wood_template is not None:
            try:
                scales = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
                best_match = 0
                
                for scale in scales:
                    if scale != 1.0:
                        h, w = self.destroyed_wood_template.shape[:2]
                        new_h, new_w = int(h * scale), int(w * scale)
                        scaled_template = cv2.resize(self.destroyed_wood_template, (new_w, new_h))
                    else:
                        scaled_template = self.destroyed_wood_template
                    
                    if (scaled_template.shape[0] > right_corner_region.shape[0] or 
                        scaled_template.shape[1] > right_corner_region.shape[1]):
                        continue
                    
                    result = cv2.matchTemplate(right_corner_region, scaled_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val > best_match:
                        best_match = max_val
                
                if best_match >= 0.5:
                    destroyed_wood_there = True
                    self.logger.debug(f"Destroyed wood detected with confidence {best_match:.3f}")
                
            except Exception as e:
                self.logger.error(f"Error checking destroyed wood: {e}")
        
        if destroyed_wood_there:
            self.logger.info("Wood sprite changed to destroyed state!")
            return True
        elif not wood_still_there:
            hsv = cv2.cvtColor(right_corner_region, cv2.COLOR_BGR2HSV)
            lower_brown = np.array([8, 40, 60])
            upper_brown = np.array([30, 255, 220])
            mask = cv2.inRange(hsv, lower_brown, upper_brown)
            brown_pixels = cv2.countNonZero(mask)
            
            if brown_pixels < 200:
                self.logger.info("Wood sprite disappeared (no brown pixels detected)!")
                return True
            else:
                self.logger.debug(f"Wood template not found but brown pixels still present ({brown_pixels})")
                return False
        else:
            self.logger.debug("Wood sprite unchanged, continue attacking")
            return False
        try:
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            timestamp = time.strftime("%H%M%S")
            filename = f"{debug_dir}/{prefix}_{timestamp}_conf{confidence:.2f}.png"
            
            if location:
                debug_img = screenshot.copy()
                cv2.circle(debug_img, location, 20, (0, 255, 0), 3)
                cv2.putText(debug_img, f"{confidence:.2f}", 
                           (location[0] - 30, location[1] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imwrite(filename, debug_img)
            else:
                cv2.imwrite(filename, screenshot)
            
            self.logger.debug(f"Saved debug image: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving debug image: {e}")
    
    def move_right_fast(self, duration=0.5):
        press_key(None, 'right')
        time.sleep(duration)
        
        self.movement_variation += 1
        if self.movement_variation % 4 == 0:
            variation_key = random.choice(['up', 'down'])
            press_key(None, variation_key)
            time.sleep(0.2)
            self.logger.debug(f"Added movement variation: {variation_key}")
    
    def move_left_fast(self, duration=0.3):
        press_key(None, 'left')
        time.sleep(duration)
    
    def move_up_fast(self, duration=0.3):
        press_key(None, 'up')
        time.sleep(duration)
    
    def move_down_fast(self, duration=0.3):
        press_key(None, 'down')
        time.sleep(duration)
    
    def attack_wood_stack_improved(self):
        attack_count = 0
        max_attacks = 30
        
        self.log_callback("Attacking wood stack...")
        
        while self.running and attack_count < max_attacks:
            press_key(None, 'x')
            attack_count += 1
            self.total_attacks += 1
            
            self.logger.debug(f"Attack #{attack_count}")
            
            time.sleep(0.8)
            
            if attack_count % 3 == 0:
                screenshot = self.capture_game_screen()
                if screenshot is not None:
                    if self.check_wood_sprite_changed(screenshot):
                        self.wood_stacks_destroyed += 1
                        self.log_callback(f"Wood stack destroyed! Total: {self.wood_stacks_destroyed}/4")
                        self.logger.info(f"Wood stack {self.wood_stacks_destroyed} destroyed after {attack_count} attacks")
                        return True
        
        self.wood_stacks_destroyed += 1
        self.log_callback(f"Wood stack destroyed (max attacks reached)! Total: {self.wood_stacks_destroyed}/4")
        return True
    
    def save_detection_debug_image(self, screenshot, location, confidence, prefix):
        try:
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            timestamp = time.strftime("%H%M%S")
            filename = f"{debug_dir}/{prefix}_{timestamp}_conf{confidence:.2f}.png"
            
            if location:
                debug_img = screenshot.copy()
                cv2.circle(debug_img, location, 20, (0, 255, 0), 3)
                cv2.putText(debug_img, f"{confidence:.2f}", 
                           (location[0] - 30, location[1] - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imwrite(filename, debug_img)
            else:
                cv2.imwrite(filename, screenshot)
            
            self.logger.debug(f"Saved debug image: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving debug image: {e}")

    def check_wood_sprite_changed(self, screenshot):
        screen_height, screen_width = screenshot.shape[:2]
        
        wood_still_there = False
        destroyed_wood_there = False
        
        if OPENCV_AVAILABLE and self.wood_stack_template is not None:
            try:
                scales = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
                best_match = 0
                
                for scale in scales:
                    if scale != 1.0:
                        h, w = self.wood_stack_template.shape[:2]
                        new_h, new_w = int(h * scale), int(w * scale)
                        if new_h <= 0 or new_w <= 0:
                            continue
                        scaled_template = cv2.resize(self.wood_stack_template, (new_w, new_h))
                    else:
                        scaled_template = self.wood_stack_template
                    
                    if (scaled_template.shape[0] > screenshot.shape[0] or 
                        scaled_template.shape[1] > screenshot.shape[1]):
                        continue
                    
                    result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val > best_match:
                        best_match = max_val
                
                if best_match >= 0.25:
                    wood_still_there = True
                    self.logger.debug(f"Original wood still detected with confidence {best_match:.3f}")
                
            except Exception as e:
                self.logger.error(f"Error checking original wood: {e}")
        
        if OPENCV_AVAILABLE and self.destroyed_wood_template is not None:
            try:
                scales = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
                best_match = 0
                
                for scale in scales:
                    if scale != 1.0:
                        h, w = self.destroyed_wood_template.shape[:2]
                        new_h, new_w = int(h * scale), int(w * scale)
                        if new_h <= 0 or new_w <= 0:
                            continue
                        scaled_template = cv2.resize(self.destroyed_wood_template, (new_w, new_h))
                    else:
                        scaled_template = self.destroyed_wood_template
                    
                    if (scaled_template.shape[0] > screenshot.shape[0] or 
                        scaled_template.shape[1] > screenshot.shape[1]):
                        continue
                    
                    result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val > best_match:
                        best_match = max_val
                
                if best_match >= 0.25:
                    destroyed_wood_there = True
                    self.logger.debug(f"Destroyed wood detected with confidence {best_match:.3f}")
                
            except Exception as e:
                self.logger.error(f"Error checking destroyed wood: {e}")
        
        if destroyed_wood_there:
            self.logger.info("Wood sprite changed to destroyed state!")
            return True
        elif not wood_still_there:
            right_section = screenshot[:, int(screen_width * 0.6):]
            hsv = cv2.cvtColor(right_section, cv2.COLOR_BGR2HSV)
            lower_brown = np.array([5, 40, 60])
            upper_brown = np.array([25, 200, 180])
            mask = cv2.inRange(hsv, lower_brown, upper_brown)
            brown_pixels = cv2.countNonZero(mask)
            
            if brown_pixels < 500:
                self.logger.info("Wood sprite disappeared (minimal brown pixels detected)!")
                return True
            else:
                self.logger.debug(f"Wood template not found but brown pixels still present ({brown_pixels})")
                return False
        else:
            self.logger.debug("Wood sprite unchanged, continue attacking")
            return False
        if self.running:
            self.logger.info("Hunt already running")
            return False
        
        self.running = True
        self.wood_stacks_destroyed = 0
        self.total_attacks = 0
        self.hunt_start_time = time.time()
        self.movement_variation = 0
        self.false_positive_counter = 0
        self.last_wood_detection_time = 0
        
        self.hunt_thread = threading.Thread(target=self.hunt_loop)
        self.hunt_thread.daemon = True
        self.hunt_thread.start()
        
        self.log_callback("Largato Hunt started!")
        self.logger.info("Largato hunt thread started")
        return True
    
    def start_hunt(self):
        if self.running:
            self.logger.info("Hunt already running")
            return False
        
        self.running = True
        self.wood_stacks_destroyed = 0
        self.total_attacks = 0
        self.hunt_start_time = time.time()
        self.movement_variation = 0
        self.false_positive_counter = 0
        
        self.hunt_thread = threading.Thread(target=self.hunt_loop)
        self.hunt_thread.daemon = True
        self.hunt_thread.start()
        
        self.log_callback("Largato Hunt started!")
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
            self.log_callback(f"Hunt stopped. Duration: {minutes}m {seconds}s, Wood destroyed: {self.wood_stacks_destroyed}/4")
        
        self.log_callback("Largato Hunt stopped!")
        self.logger.info("Largato hunt stopped")
        return True
    
    def hunt_loop(self):
        self.log_callback("Starting Largato dungeon hunt...")
        self.logger.info("Largato hunt loop started")
        
        self.find_game_window()
        
        initial_delay = random.uniform(1.0, 2.0)
        self.log_callback(f"Initial delay: {initial_delay:.1f} seconds...")
        time.sleep(initial_delay)
        
        hunt_phase = "moving"
        last_check_time = 0
        check_interval = 2.0
        wood_found_time = 0
        approach_duration = 3.0
        attacks_count = 0
        movement_duration = 0.8
        
        self.log_callback("Starting movement phase - looking for wood stacks...")
        
        while self.running and self.wood_stacks_destroyed < 4:
            try:
                current_time = time.time()
                
                if hunt_phase == "moving":
                    self.move_right_fast(movement_duration)
                    
                    if current_time - last_check_time >= check_interval:
                        self.log_callback("Scanning for wood stacks...")
                        screenshot = self.capture_game_screen()
                        
                        if screenshot is not None:
                            found, target_x, target_y, confidence = self.find_wood_stack(screenshot)
                            
                            if found and confidence >= self.detection_confidence_threshold:
                                self.log_callback(f"WOOD STACK FOUND! Confidence: {confidence:.2f}, moving forward...")
                                self.logger.info(f"Wood stack detected with confidence {confidence:.3f}")
                                hunt_phase = "approach"
                                wood_found_time = current_time
                            else:
                                self.log_callback("No wood stack detected, continuing search...")
                        
                        last_check_time = current_time
                        check_interval = random.uniform(1.5, 2.5)
                
                elif hunt_phase == "approach":
                    elapsed_since_found = current_time - wood_found_time
                    
                    if elapsed_since_found < approach_duration:
                        self.move_right_fast(0.4)
                        remaining = approach_duration - elapsed_since_found
                        if int(remaining) != int(remaining + 0.4):
                            self.log_callback(f"Approaching wood stack... {remaining:.1f}s remaining")
                    else:
                        hunt_phase = "attacking"
                        attacks_count = 0
                        self.log_callback("Starting attack phase!")
                
                elif hunt_phase == "attacking":
                    if self.attack_wood_stack_improved():
                        hunt_phase = "moving"
                        last_check_time = 0
                        
                        self.log_callback("Continuing search for next wood stack...")
                        time.sleep(1.0)
                
            except Exception as e:
                self.log_callback(f"Error in hunt loop: {e}")
                self.logger.error(f"Error in hunt loop: {e}", exc_info=True)
                time.sleep(1.0)
        
        if self.wood_stacks_destroyed >= 4:
            self.log_callback("Largato Hunt completed! All 4 wood stacks destroyed.")
            self.logger.info("Largato hunt completed successfully")
        else:
            self.log_callback("Largato Hunt stopped before completion.")
            self.logger.info("Largato hunt stopped by user")
        
        self.running = False