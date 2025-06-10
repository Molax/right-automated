"""
Configuration Manager UI for the Priston Tale Potion Bot
---------------------------------------------------
This module handles loading and saving configurations.
"""

import logging
from PIL import ImageGrab
from app.config import load_config, save_config

logger = logging.getLogger('PristonBot')

class ConfigManagerUI:
    """Class that handles configuration management UI functions"""
    
    def __init__(self, bar_selector_ui, settings_ui, log_callback):
        """
        Initialize the configuration manager
        
        Args:
            bar_selector_ui: Bar selector UI instance
            settings_ui: Settings UI instance
            log_callback: Function to call for logging
        """
        self.bar_selector_ui = bar_selector_ui
        self.settings_ui = settings_ui
        self.log_callback = log_callback
    
    def save_bar_config(self):
        """Save bar configuration to config file"""
        try:
            # Load current config
            config = load_config()
            
            # Save game window coordinates
            game_window = self.bar_selector_ui.game_window
            if game_window.is_setup():
                config["bars"]["game_window"]["x1"] = game_window.x1
                config["bars"]["game_window"]["y1"] = game_window.y1
                config["bars"]["game_window"]["x2"] = game_window.x2
                config["bars"]["game_window"]["y2"] = game_window.y2
                config["bars"]["game_window"]["configured"] = True
                logger.info("Saved game window configuration")
            
            # Save health bar coordinates
            hp_bar = self.bar_selector_ui.hp_bar_selector
            if hp_bar.is_setup():
                config["bars"]["health_bar"]["x1"] = hp_bar.x1
                config["bars"]["health_bar"]["y1"] = hp_bar.y1
                config["bars"]["health_bar"]["x2"] = hp_bar.x2
                config["bars"]["health_bar"]["y2"] = hp_bar.y2
                config["bars"]["health_bar"]["configured"] = True
                logger.info("Saved health bar configuration")
            
            # Save mana bar coordinates
            mp_bar = self.bar_selector_ui.mp_bar_selector
            if mp_bar.is_setup():
                config["bars"]["mana_bar"]["x1"] = mp_bar.x1
                config["bars"]["mana_bar"]["y1"] = mp_bar.y1
                config["bars"]["mana_bar"]["x2"] = mp_bar.x2
                config["bars"]["mana_bar"]["y2"] = mp_bar.y2
                config["bars"]["mana_bar"]["configured"] = True
                logger.info("Saved mana bar configuration")
            
            # Save stamina bar coordinates
            sp_bar = self.bar_selector_ui.sp_bar_selector
            if sp_bar.is_setup():
                config["bars"]["stamina_bar"]["x1"] = sp_bar.x1
                config["bars"]["stamina_bar"]["y1"] = sp_bar.y1
                config["bars"]["stamina_bar"]["x2"] = sp_bar.x2
                config["bars"]["stamina_bar"]["y2"] = sp_bar.y2
                config["bars"]["stamina_bar"]["configured"] = True
                logger.info("Saved stamina bar configuration")
            
            # Get settings from settings UI
            settings = self.settings_ui.get_settings()
            
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
    
    def load_bar_config(self):
        """Load bar configuration from config file"""
        try:
            # Load config
            config = load_config()
            bars_config = config.get("bars", {})
            
            # Check if there's a saved configuration
            if not bars_config:
                logger.info("No saved bar configuration found")
                return False
            
            bars_configured = 0
            
            # Load game window
            game_window = self.bar_selector_ui.game_window
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
                                game_window.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for game window")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for game window: {e}")
                
                # Update the preview
                self.bar_selector_ui.update_window_preview()
            
            # Load health bar
            hp_bar = self.bar_selector_ui.hp_bar_selector
            hp_config = bars_config.get("health_bar", {})
            if hp_config.get("configured", False) and hasattr(hp_bar, 'configure_from_saved'):
                # Check if we have all needed coordinates
                x1 = hp_config.get("x1")
                y1 = hp_config.get("y1")
                x2 = hp_config.get("x2")
                y2 = hp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if hp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded health bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        # Create a placeholder preview image if one doesn't exist
                        if not hasattr(hp_bar, 'preview_image') or hp_bar.preview_image is None:
                            # Attempt to capture a screenshot of the region for preview
                            try:
                                hp_bar.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for health bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for health bar: {e}")
                                
                # Update the preview
                self.bar_selector_ui.update_preview_image(hp_bar, self.bar_selector_ui.hp_preview_label)
            
            # Load mana bar
            mp_bar = self.bar_selector_ui.mp_bar_selector
            mp_config = bars_config.get("mana_bar", {})
            if mp_config.get("configured", False) and hasattr(mp_bar, 'configure_from_saved'):
                # Check if we have all needed coordinates
                x1 = mp_config.get("x1")
                y1 = mp_config.get("y1")
                x2 = mp_config.get("x2")
                y2 = mp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if mp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded mana bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        # Create a placeholder preview image if one doesn't exist
                        if not hasattr(mp_bar, 'preview_image') or mp_bar.preview_image is None:
                            # Attempt to capture a screenshot of the region for preview
                            try:
                                mp_bar.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for mana bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for mana bar: {e}")
                                
                # Update the preview
                self.bar_selector_ui.update_preview_image(mp_bar, self.bar_selector_ui.mp_preview_label)
            
            # Load stamina bar
            sp_bar = self.bar_selector_ui.sp_bar_selector
            sp_config = bars_config.get("stamina_bar", {})
            if sp_config.get("configured", False) and hasattr(sp_bar, 'configure_from_saved'):
                # Check if we have all needed coordinates
                x1 = sp_config.get("x1")
                y1 = sp_config.get("y1")
                x2 = sp_config.get("x2")
                y2 = sp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if sp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded stamina bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        # Create a placeholder preview image if one doesn't exist
                        if not hasattr(sp_bar, 'preview_image') or sp_bar.preview_image is None:
                            # Attempt to capture a screenshot of the region for preview
                            try:
                                sp_bar.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for stamina bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for stamina bar: {e}")
                                
                # Update the preview
                self.bar_selector_ui.update_preview_image(sp_bar, self.bar_selector_ui.sp_preview_label)
            
            # Load settings to the settings UI
            self.settings_ui.set_settings(config)
            
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