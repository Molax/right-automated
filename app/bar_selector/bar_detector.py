"""
Bar Detection and Color Analysis
-------------------------------
Provides percentage detection for health, mana, and stamina bars.
"""

import os
import time
import logging
import cv2
import numpy as np

logger = logging.getLogger('PristonBot')

class BarDetector:
    def __init__(self, title, color_range):
        self.title = title
        self.color_range = color_range
        self.logger = logging.getLogger('PristonBot')
        
    def detect_percentage(self, image):
        try:
            if image is None:
                self.logger.warning(f"Cannot detect {self.title} percentage: image is None")
                return 100
                
            np_image = np.array(image)
            
            if np_image.size == 0:
                self.logger.warning(f"Cannot detect {self.title} percentage: image is empty")
                return 100
            
            hsv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
            
            if self.title == "Health":
                lower1 = np.array([0, 50, 50])
                upper1 = np.array([10, 255, 255])
                mask1 = cv2.inRange(hsv_image, lower1, upper1)
                
                lower2 = np.array([160, 50, 50])
                upper2 = np.array([180, 255, 255])
                mask2 = cv2.inRange(hsv_image, lower2, upper2)
                
                mask = mask1 | mask2
                
            elif self.title == "Mana":
                lower = np.array([100, 50, 50])
                upper = np.array([140, 255, 255])
                mask = cv2.inRange(hsv_image, lower, upper)
                
            else:
                lower = np.array([40, 50, 50])
                upper = np.array([80, 255, 255])
                mask = cv2.inRange(hsv_image, lower, upper)
            
            debug_dir = "debug_images"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            mask_filename = f"{debug_dir}/{self.title.lower()}_mask_{time.strftime('%H%M%S')}.png"
            cv2.imwrite(mask_filename, mask)
            
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            total_pixels = mask.shape[0] * mask.shape[1]
            if total_pixels == 0:
                return 100
                
            filled_pixels = cv2.countNonZero(mask)
            percentage = (filled_pixels / total_pixels) * 100
            
            self.logger.debug(f"{self.title} bar percentage: {percentage:.1f}%")
            return max(0, min(100, percentage))
            
        except Exception as e:
            self.logger.error(f"Error detecting {self.title} bar percentage: {e}", exc_info=True)
            return 100