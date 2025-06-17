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
            config = load_config()
            
            game_window = self.bar_selector_ui.game_window
            if game_window.is_setup():
                config["bars"]["game_window"]["x1"] = game_window.x1
                config["bars"]["game_window"]["y1"] = game_window.y1
                config["bars"]["game_window"]["x2"] = game_window.x2
                config["bars"]["game_window"]["y2"] = game_window.y2
                config["bars"]["game_window"]["configured"] = True
                logger.info("Saved game window configuration")
            
            hp_bar = self.bar_selector_ui.hp_bar_selector
            if hp_bar.is_setup():
                config["bars"]["health_bar"]["x1"] = hp_bar.x1
                config["bars"]["health_bar"]["y1"] = hp_bar.y1
                config["bars"]["health_bar"]["x2"] = hp_bar.x2
                config["bars"]["health_bar"]["y2"] = hp_bar.y2
                config["bars"]["health_bar"]["configured"] = True
                logger.info("Saved health bar configuration")
            
            mp_bar = self.bar_selector_ui.mp_bar_selector
            if mp_bar.is_setup():
                config["bars"]["mana_bar"]["x1"] = mp_bar.x1
                config["bars"]["mana_bar"]["y1"] = mp_bar.y1
                config["bars"]["mana_bar"]["x2"] = mp_bar.x2
                config["bars"]["mana_bar"]["y2"] = mp_bar.y2
                config["bars"]["mana_bar"]["configured"] = True
                logger.info("Saved mana bar configuration")
            
            sp_bar = self.bar_selector_ui.sp_bar_selector
            if sp_bar.is_setup():
                config["bars"]["stamina_bar"]["x1"] = sp_bar.x1
                config["bars"]["stamina_bar"]["y1"] = sp_bar.y1
                config["bars"]["stamina_bar"]["x2"] = sp_bar.x2
                config["bars"]["stamina_bar"]["y2"] = sp_bar.y2
                config["bars"]["stamina_bar"]["configured"] = True
                logger.info("Saved stamina bar configuration")
            
            if hasattr(self.bar_selector_ui, 'largato_skill_selector'):
                largato_bar = self.bar_selector_ui.largato_skill_selector
                if largato_bar.is_setup():
                    if "largato_skill_bar" not in config["bars"]:
                        config["bars"]["largato_skill_bar"] = {
                            "x1": None,
                            "y1": None,
                            "x2": None,
                            "y2": None,
                            "configured": False
                        }
                    
                    config["bars"]["largato_skill_bar"]["x1"] = largato_bar.x1
                    config["bars"]["largato_skill_bar"]["y1"] = largato_bar.y1
                    config["bars"]["largato_skill_bar"]["x2"] = largato_bar.x2
                    config["bars"]["largato_skill_bar"]["y2"] = largato_bar.y2
                    config["bars"]["largato_skill_bar"]["configured"] = True
                    logger.info("Saved Largato skill bar configuration")
            
            settings = self.settings_ui.get_settings()
            
            config["potion_keys"] = settings["potion_keys"]
            config["thresholds"] = settings["thresholds"]
            config["spellcasting"] = settings["spellcasting"]
            config["scan_interval"] = settings["scan_interval"]
            config["debug_enabled"] = settings["debug_enabled"]
            
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
            config = load_config()
            bars_config = config.get("bars", {})
            
            if not bars_config:
                logger.info("No saved bar configuration found")
                return False
            
            bars_configured = 0
            
            game_window = self.bar_selector_ui.game_window
            game_window_config = bars_config.get("game_window", {})
            if game_window_config.get("configured", False):
                x1 = game_window_config.get("x1")
                y1 = game_window_config.get("y1")
                x2 = game_window_config.get("x2")
                y2 = game_window_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if game_window.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded game window configuration: ({x1},{y1}) to ({x2},{y2})")
                        if not hasattr(game_window, 'preview_image') or game_window.preview_image is None:
                            try:
                                game_window.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for game window")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for game window: {e}")
                
                self.bar_selector_ui.update_window_preview()
            
            hp_bar = self.bar_selector_ui.hp_bar_selector
            hp_config = bars_config.get("health_bar", {})
            if hp_config.get("configured", False):
                x1 = hp_config.get("x1")
                y1 = hp_config.get("y1")
                x2 = hp_config.get("x2")
                y2 = hp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if hp_bar.configure_from_saved(x1, y1, x2, y2):
                        hp_bar.title = "Health"
                        logger.info(f"Loaded health bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        if not hasattr(hp_bar, 'preview_image') or hp_bar.preview_image is None:
                            try:
                                hp_bar.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for health bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for health bar: {e}")
                                
                self.bar_selector_ui.update_preview_image(hp_bar, self.bar_selector_ui.hp_preview_label)
            
            mp_bar = self.bar_selector_ui.mp_bar_selector
            mp_config = bars_config.get("mana_bar", {})
            if mp_config.get("configured", False):
                x1 = mp_config.get("x1")
                y1 = mp_config.get("y1")
                x2 = mp_config.get("x2")
                y2 = mp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if mp_bar.configure_from_saved(x1, y1, x2, y2):
                        mp_bar.title = "Mana"
                        logger.info(f"Loaded mana bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        if not hasattr(mp_bar, 'preview_image') or mp_bar.preview_image is None:
                            try:
                                mp_bar.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for mana bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for mana bar: {e}")
                                
                self.bar_selector_ui.update_preview_image(mp_bar, self.bar_selector_ui.mp_preview_label)
            
            sp_bar = self.bar_selector_ui.sp_bar_selector
            sp_config = bars_config.get("stamina_bar", {})
            if sp_config.get("configured", False):
                x1 = sp_config.get("x1")
                y1 = sp_config.get("y1")
                x2 = sp_config.get("x2")
                y2 = sp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if sp_bar.configure_from_saved(x1, y1, x2, y2):
                        sp_bar.title = "Stamina"
                        logger.info(f"Loaded stamina bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        if not hasattr(sp_bar, 'preview_image') or sp_bar.preview_image is None:
                            try:
                                sp_bar.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for stamina bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for stamina bar: {e}")
                                
                self.bar_selector_ui.update_preview_image(sp_bar, self.bar_selector_ui.sp_preview_label)
            
            if hasattr(self.bar_selector_ui, 'largato_skill_selector'):
                largato_bar = self.bar_selector_ui.largato_skill_selector
                largato_config = bars_config.get("largato_skill_bar", {})
                if largato_config.get("configured", False):
                    x1 = largato_config.get("x1")
                    y1 = largato_config.get("y1")
                    x2 = largato_config.get("x2")
                    y2 = largato_config.get("y2")
                    
                    if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                        if largato_bar.configure_from_saved(x1, y1, x2, y2):
                            largato_bar.title = "Largato Skill"
                            logger.info(f"Loaded Largato skill bar configuration: ({x1},{y1}) to ({x2},{y2})")
                            
                            if not hasattr(largato_bar, 'preview_image') or largato_bar.preview_image is None:
                                try:
                                    largato_bar.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                    logger.info("Created preview image for Largato skill bar")
                                except Exception as e:
                                    logger.warning(f"Could not create preview image for Largato skill bar: {e}")
                                    
                        self.bar_selector_ui.update_preview_image(largato_bar, self.bar_selector_ui.largato_preview_label)
            
            self.settings_ui.set_settings(config)
            
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