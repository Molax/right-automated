"""
Core bot logic for Priston Tale Potion Bot
------------------------------------------
This module contains the main bot loop that monitors bars and uses potions.
"""

import time
import logging
import threading
import random
import math
from PIL import Image
from app.window_utils import press_key, press_right_mouse, get_window_rect
from app.bar_selector import BarDetector, HEALTH_COLOR_RANGE, MANA_COLOR_RANGE, STAMINA_COLOR_RANGE
from app.bot.interfaces import BarManager, SettingsProvider, WindowManager

logger = logging.getLogger('PristonBot')

class PotionBot:
    """Main bot class for the Priston Tale Potion Bot"""
    
    def __init__(self, hp_bar: BarManager, mp_bar: BarManager, sp_bar: BarManager, 
                 settings_provider: SettingsProvider, log_callback):
        """
        Initialize the potion bot
        
        Args:
            hp_bar: Health bar manager
            mp_bar: Mana bar manager
            sp_bar: Stamina bar manager
            settings_provider: Settings provider
            log_callback: Function to log messages
        """
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.settings_provider = settings_provider
        self.log_callback = log_callback
        
        # Create detectors
        self.hp_detector = BarDetector("Health", HEALTH_COLOR_RANGE)
        self.mp_detector = BarDetector("Mana", MANA_COLOR_RANGE)
        self.sp_detector = BarDetector("Stamina", STAMINA_COLOR_RANGE)
        
        # Bot state
        self.running = False
        self.bot_thread = None
        
        # Store previous bar values to detect changes
        self.prev_hp_percent = 100.0
        self.prev_mp_percent = 100.0
        self.prev_sp_percent = 100.0
        
        # Random targeting variables
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
    
    def start_bot(self):
        """Start the bot thread"""
        if self.running:
            logger.info("Start button clicked, but bot is already running")
            return False
        
        self.log_callback("Starting bot...")
        self.running = True
        self.bot_thread = threading.Thread(target=self.bot_loop)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        logger.info("Bot thread started")
        
        # Reset previous values when starting
        self.prev_hp_percent = 100.0
        self.prev_mp_percent = 100.0
        self.prev_sp_percent = 100.0
        
        # Reset targeting variables
        self.target_x_offset = 0
        self.target_y_offset = 0
        self.spells_cast_since_target_change = 0
        
        return True
    
    def stop_bot(self):
        """Stop the bot thread"""
        if not self.running:
            logger.info("Stop button clicked, but bot is not running")
            return False
        
        self.log_callback("Stopping bot...")
        self.running = False
        if self.bot_thread:
            self.bot_thread.join(1.0)
            logger.info("Bot thread joined")
        
        return True
    
    def has_value_changed(self, prev_val, current_val, threshold=0.5):
        """
        Check if a value has changed beyond a threshold
        
        Args:
            prev_val: Previous value
            current_val: Current value
            threshold: Change threshold (default 0.5%)
            
        Returns:
            True if the value has changed beyond the threshold
        """
        return abs(prev_val - current_val) >= threshold
    
    def generate_random_target_offsets(self, radius):
        """
        Generate random offsets for spell targeting within specified radius
        
        Args:
            radius: Maximum radius from center in pixels
            
        Returns:
            (x_offset, y_offset) tuple of pixel offsets from center
        """
        # Generate random angle and distance (using square root for more even distribution)
        angle = random.uniform(0, 2 * math.pi)
        distance = radius * math.sqrt(random.random())  # Square root for more even distribution
        
        # Calculate x and y offsets (convert polar to cartesian coordinates)
        x_offset = int(distance * math.cos(angle))
        y_offset = int(distance * math.sin(angle))
        
        return x_offset, y_offset