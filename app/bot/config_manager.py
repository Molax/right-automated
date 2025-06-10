"""
Configuration management for the Priston Tale Potion Bot
-------------------------------------------------------
This module handles saving and loading bot configurations.
"""

import logging
import time
from typing import Callable, Dict, Any
from app.config import load_config, save_config
from app.bot.interfaces import BarManager, SettingsProvider, WindowManager

logger = logging.getLogger('PristonBot')

class ConfigManager:
    """Class for managing bot configuration"""
    
    def __init__(self, settings_provider: SettingsProvider, hp_bar: BarManager, 
                 mp_bar: BarManager, sp_bar: BarManager, window_manager: WindowManager, 
                 log_callback: Callable[[str], None]):
        """
        Initialize the config manager
        
        Args:
            settings_provider: Provider for settings
            hp_bar: Health bar manager
            mp_bar: Mana bar manager
            sp_bar: Stamina bar manager
            window_manager: Window manager
            log_callback: Function to log messages
        """
        self.settings_provider = settings_provider
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.window_manager = window_manager
        self.log_callback = log_callback
    
    def save_bar_config(self) -> bool:
        """
        Save bar configuration to config file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current config
            config = load_config()
            
            # Save game window coordinates
            game_window = self.window_manager.game_window
            if game_window.is_setup():
                config["bars"]["game_window"]["x1"] = game_window.x1
                config["bars"]["game_window"]["y1"] = game_window.y1
                config["bars"]["game_window"]["x2"] = game_window.x2
                config["bars"]["game_window"]["y2"] = game_window.y2
                config["bars"]["game_window"]["configured"] = True
                logger.info("Saved game window configuration")
            
            # Save health bar coordinates
            if hasattr(self.hp_bar, 'x1') and self.hp_bar.is_setup():
                config["bars"]["health_bar"]["x1"] = self.hp_bar.x1
                config["bars"]["health_bar"]["y1"] = self.hp_bar.y1
                config["bars"]["health_bar"]["x2"] = self.hp_bar.x2
                config["bars"]["health_bar"]["y2"] = self.hp_bar.y2
                config["bars"]["health_bar"]["configured"] = True
                logger.info("Saved health bar configuration")
            
            # Save mana bar coordinates
            if hasattr(self.mp_bar, 'x1') and self.mp_bar.is_setup():
                config["bars"]["mana_bar"]["x1"] = self.mp_bar.x1
                config["bars"]["mana_bar"]["y1"] = self.mp_bar.y1
                config["bars"]["mana_bar"]["x2"] = self.mp_bar.x2
                config["bars"]["mana_bar"]["y2"] = self.mp_bar.y2
                config["bars"]["mana_bar"]["configured"] = True
                logger.info("Saved mana bar configuration")
            
            # Save stamina bar coordinates
            if hasattr(self.sp_bar, 'x1') and self.sp_bar.is_setup():
                config["bars"]["stamina_bar"]["x1"] = self.sp_bar.x1
                config["bars"]["stamina_bar"]["y1"] = self.sp_bar.y1
                config["bars"]["stamina_bar"]["x2"] = self.sp_bar.x2
                config["bars"]["stamina_bar"]["y2"] = self.sp_bar.y2
                config["bars"]["stamina_bar"]["configured"] = True
                logger.info("Saved stamina bar configuration")
            
            # Save settings
            settings = self.settings_provider.get_settings()
            
            # Save potion key settings
            config["potion_keys"] = settings["potion_keys"]
            
            # Save threshold settings
            config["thresholds"] = settings["thresholds"]
            
            # Save spellcasting settings
            config["spellcasting"] = settings["spellcasting"]
            
            # Save other settings
            config["scan_interval"] = settings["scan_interval"]
            config["debug_enabled"] = settings["debug_enabled"]
            
            # Save the config
            save_config(config)
            self.log_callback("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True)
            self.log_callback(f"Error saving configuration: {e}")
            return False
    
    def load_bar_config(self) -> bool:
        """
        Load bar configuration from config file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load config
            config = load_config()
            bars_config = config.get("bars", {})
            
            # Check if there's a saved configuration
            if not bars_config:
                logger.info("No saved bar configuration found")
                return False
            
            bars_configured = 0
            
            # Load game window if it has configure_from_saved method
            game_window = self.window_manager.game_window
            game_window_config = bars_config.get("game_window", {})
            if game_window_config.get("configured", False) and hasattr(game_window, 'configure_from_saved'):
                # Check if we have all needed coordinates
                x1 = game_window_config.get("x1")
                y1 = game_window_config.get("y1")
                x2 = game_window_config.get("x2")
                y2 = game_window_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if game_window.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded game window configuration: ({x1},{y1}) to ({x2},{y2})")
                        # Create a placeholder preview image if one doesn't exist
                        if not hasattr(game_window, 'preview_image') or game_window.preview_image is None:
                            # Attempt to capture a screenshot of the region for preview
                            try:
                                from PIL import ImageGrab
                                game_window.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for game window")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for game window: {e}")
                
                # Try to update preview in the UI directly
                if hasattr(self.window_manager, 'update_window_preview'):
                    self.window_manager.update_window_preview()
            
            # Load health bar if it has configure_from_saved method
            hp_config = bars_config.get("health_bar", {})
            if hp_config.get("configured", False) and hasattr(self.hp_bar, 'configure_from_saved'):
                # Check if we have all needed coordinates
                x1 = hp_config.get("x1")
                y1 = hp_config.get("y1")
                x2 = hp_config.get("x2")
                y2 = hp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if self.hp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded health bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        # Set title for proper logging and UI display
                        if hasattr(self.hp_bar, 'screen_selector'):
                            self.hp_bar.screen_selector.title = "Health Bar"
                            
                        # Create a placeholder preview image if one doesn't exist
                        if not hasattr(self.hp_bar.screen_selector, 'preview_image') or self.hp_bar.screen_selector.preview_image is None:
                            # Attempt to capture a screenshot of the region for preview
                            try:
                                from PIL import ImageGrab
                                self.hp_bar.screen_selector.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for health bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for health bar: {e}")
            
            # Load mana bar if it has configure_from_saved method
            mp_config = bars_config.get("mana_bar", {})
            if mp_config.get("configured", False) and hasattr(self.mp_bar, 'configure_from_saved'):
                # Check if we have all needed coordinates
                x1 = mp_config.get("x1")
                y1 = mp_config.get("y1")
                x2 = mp_config.get("x2")
                y2 = mp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if self.mp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded mana bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        # Set title for proper logging and UI display
                        if hasattr(self.mp_bar, 'screen_selector'):
                            self.mp_bar.screen_selector.title = "Mana Bar"
                            
                        # Create a placeholder preview image if one doesn't exist
                        if not hasattr(self.mp_bar.screen_selector, 'preview_image') or self.mp_bar.screen_selector.preview_image is None:
                            # Attempt to capture a screenshot of the region for preview
                            try:
                                from PIL import ImageGrab
                                self.mp_bar.screen_selector.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for mana bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for mana bar: {e}")
            
            # Load stamina bar if it has configure_from_saved method
            sp_config = bars_config.get("stamina_bar", {})
            if sp_config.get("configured", False) and hasattr(self.sp_bar, 'configure_from_saved'):
                # Check if we have all needed coordinates
                x1 = sp_config.get("x1")
                y1 = sp_config.get("y1")
                x2 = sp_config.get("x2")
                y2 = sp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if self.sp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded stamina bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        # Set title for proper logging and UI display
                        if hasattr(self.sp_bar, 'screen_selector'):
                            self.sp_bar.screen_selector.title = "Stamina Bar"
                            
                        # Create a placeholder preview image if one doesn't exist
                        if not hasattr(self.sp_bar.screen_selector, 'preview_image') or self.sp_bar.screen_selector.preview_image is None:
                            # Attempt to capture a screenshot of the region for preview
                            try:
                                from PIL import ImageGrab
                                self.sp_bar.screen_selector.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for stamina bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for stamina bar: {e}")
            
            # Load settings
            self.settings_provider.set_settings(config)
            
            # Update UI previews after a small delay to allow UI elements to initialize
            if hasattr(self.window_manager, 'root'):
                self.window_manager.root.after(500, self._update_ui_previews)
            
            # Return success if any bars were configured
            if bars_configured > 0:
                self.log_callback(f"Loaded {bars_configured}/3 bars from saved configuration")
                logger.info(f"Loaded {bars_configured}/3 bars from saved configuration")
                return True
            else:
                logger.info("No bar configurations loaded")
                return False
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}", exc_info=True)
            self.log_callback(f"Error loading configuration: {e}")
            return False
    
    def _update_ui_previews(self):
        """Helper method to update UI previews after loading configuration"""
        try:
            # Update bar selector UI previews
            if hasattr(self.window_manager, 'root'):
                root = self.window_manager.root
                
                # Find and update the bar selector UI previews
                if hasattr(self.window_manager, 'update_window_preview'):
                    self.window_manager.update_window_preview()
                
                # Try to find the bar selector UI instance
                for widget in root.winfo_children():
                    if hasattr(widget, 'bar_selector_ui'):
                        bar_selector_ui = widget.bar_selector_ui
                        
                        # Update previews if methods exist
                        if hasattr(bar_selector_ui, 'update_preview_image'):
                            if hasattr(bar_selector_ui, 'hp_bar_selector') and hasattr(bar_selector_ui, 'hp_preview_label'):
                                bar_selector_ui.update_preview_image(bar_selector_ui.hp_bar_selector, bar_selector_ui.hp_preview_label)
                            
                            if hasattr(bar_selector_ui, 'mp_bar_selector') and hasattr(bar_selector_ui, 'mp_preview_label'):
                                bar_selector_ui.update_preview_image(bar_selector_ui.mp_bar_selector, bar_selector_ui.mp_preview_label)
                            
                            if hasattr(bar_selector_ui, 'sp_bar_selector') and hasattr(bar_selector_ui, 'sp_preview_label'):
                                bar_selector_ui.update_preview_image(bar_selector_ui.sp_bar_selector, bar_selector_ui.sp_preview_label)
        except Exception as e:
            logger.error(f"Error updating UI previews: {e}", exc_info=True)