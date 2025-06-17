"""
Enhanced Configuration management with Largato skill bar support
---------------------------------------------------------------
Extended to handle the Largato skill bar configuration alongside existing bars.
"""

import logging
import time
from typing import Callable, Dict, Any
from app.config import load_config, save_config
from app.bot.interfaces import BarManager, SettingsProvider, WindowManager

logger = logging.getLogger('PristonBot')

class ConfigManager:
    def __init__(self, settings_provider: SettingsProvider, hp_bar: BarManager, 
                 mp_bar: BarManager, sp_bar: BarManager, largato_skill_bar: BarManager,
                 window_manager: WindowManager, log_callback: Callable[[str], None]):
        self.settings_provider = settings_provider
        self.hp_bar = hp_bar
        self.mp_bar = mp_bar
        self.sp_bar = sp_bar
        self.largato_skill_bar = largato_skill_bar
        self.window_manager = window_manager
        self.log_callback = log_callback
    
    def save_bar_config(self) -> bool:
        try:
            config = load_config()
            
            game_window = self.window_manager.game_window
            if game_window.is_setup():
                config["bars"]["game_window"]["x1"] = game_window.x1
                config["bars"]["game_window"]["y1"] = game_window.y1
                config["bars"]["game_window"]["x2"] = game_window.x2
                config["bars"]["game_window"]["y2"] = game_window.y2
                config["bars"]["game_window"]["configured"] = True
                logger.info("Saved game window configuration")
            
            if hasattr(self.hp_bar, 'x1') and self.hp_bar.is_setup():
                config["bars"]["health_bar"]["x1"] = self.hp_bar.x1
                config["bars"]["health_bar"]["y1"] = self.hp_bar.y1
                config["bars"]["health_bar"]["x2"] = self.hp_bar.x2
                config["bars"]["health_bar"]["y2"] = self.hp_bar.y2
                config["bars"]["health_bar"]["configured"] = True
                logger.info("Saved health bar configuration")
            
            if hasattr(self.mp_bar, 'x1') and self.mp_bar.is_setup():
                config["bars"]["mana_bar"]["x1"] = self.mp_bar.x1
                config["bars"]["mana_bar"]["y1"] = self.mp_bar.y1
                config["bars"]["mana_bar"]["x2"] = self.mp_bar.x2
                config["bars"]["mana_bar"]["y2"] = self.mp_bar.y2
                config["bars"]["mana_bar"]["configured"] = True
                logger.info("Saved mana bar configuration")
            
            if hasattr(self.sp_bar, 'x1') and self.sp_bar.is_setup():
                config["bars"]["stamina_bar"]["x1"] = self.sp_bar.x1
                config["bars"]["stamina_bar"]["y1"] = self.sp_bar.y1
                config["bars"]["stamina_bar"]["x2"] = self.sp_bar.x2
                config["bars"]["stamina_bar"]["y2"] = self.sp_bar.y2
                config["bars"]["stamina_bar"]["configured"] = True
                logger.info("Saved stamina bar configuration")
            
            if hasattr(self.largato_skill_bar, 'x1') and self.largato_skill_bar.is_setup():
                if "largato_skill_bar" not in config["bars"]:
                    config["bars"]["largato_skill_bar"] = {
                        "x1": None,
                        "y1": None,
                        "x2": None,
                        "y2": None,
                        "configured": False
                    }
                
                config["bars"]["largato_skill_bar"]["x1"] = self.largato_skill_bar.x1
                config["bars"]["largato_skill_bar"]["y1"] = self.largato_skill_bar.y1
                config["bars"]["largato_skill_bar"]["x2"] = self.largato_skill_bar.x2
                config["bars"]["largato_skill_bar"]["y2"] = self.largato_skill_bar.y2
                config["bars"]["largato_skill_bar"]["configured"] = True
                logger.info("Saved Largato skill bar configuration")
            
            settings = self.settings_provider.get_settings()
            
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
    
    def load_bar_config(self) -> bool:
        try:
            config = load_config()
            bars_config = config.get("bars", {})
            
            if not bars_config:
                logger.info("No saved bar configuration found")
                return False
            
            bars_configured = 0
            
            game_window = self.window_manager.game_window
            game_window_config = bars_config.get("game_window", {})
            if game_window_config.get("configured", False) and hasattr(game_window, 'configure_from_saved'):
                x1 = game_window_config.get("x1")
                y1 = game_window_config.get("y1")
                x2 = game_window_config.get("x2")
                y2 = game_window_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if game_window.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded game window configuration: ({x1},{y1}) to ({x2},{y2})")
                        if not hasattr(game_window, 'preview_image') or game_window.preview_image is None:
                            try:
                                from PIL import ImageGrab
                                game_window.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for game window")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for game window: {e}")
                
                if hasattr(self.window_manager, 'update_window_preview'):
                    self.window_manager.update_window_preview()
            
            hp_config = bars_config.get("health_bar", {})
            if hp_config.get("configured", False) and hasattr(self.hp_bar, 'configure_from_saved'):
                x1 = hp_config.get("x1")
                y1 = hp_config.get("y1")
                x2 = hp_config.get("x2")
                y2 = hp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if self.hp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded health bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        if hasattr(self.hp_bar, 'screen_selector'):
                            self.hp_bar.screen_selector.title = "Health Bar"
                            
                        if not hasattr(self.hp_bar.screen_selector, 'preview_image') or self.hp_bar.screen_selector.preview_image is None:
                            try:
                                from PIL import ImageGrab
                                self.hp_bar.screen_selector.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for health bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for health bar: {e}")
            
            mp_config = bars_config.get("mana_bar", {})
            if mp_config.get("configured", False) and hasattr(self.mp_bar, 'configure_from_saved'):
                x1 = mp_config.get("x1")
                y1 = mp_config.get("y1")
                x2 = mp_config.get("x2")
                y2 = mp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if self.mp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded mana bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        if hasattr(self.mp_bar, 'screen_selector'):
                            self.mp_bar.screen_selector.title = "Mana Bar"
                            
                        if not hasattr(self.mp_bar.screen_selector, 'preview_image') or self.mp_bar.screen_selector.preview_image is None:
                            try:
                                from PIL import ImageGrab
                                self.mp_bar.screen_selector.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for mana bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for mana bar: {e}")
            
            sp_config = bars_config.get("stamina_bar", {})
            if sp_config.get("configured", False) and hasattr(self.sp_bar, 'configure_from_saved'):
                x1 = sp_config.get("x1")
                y1 = sp_config.get("y1")
                x2 = sp_config.get("x2")
                y2 = sp_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if self.sp_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded stamina bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        bars_configured += 1
                        
                        if hasattr(self.sp_bar, 'screen_selector'):
                            self.sp_bar.screen_selector.title = "Stamina Bar"
                            
                        if not hasattr(self.sp_bar.screen_selector, 'preview_image') or self.sp_bar.screen_selector.preview_image is None:
                            try:
                                from PIL import ImageGrab
                                self.sp_bar.screen_selector.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for stamina bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for stamina bar: {e}")
            
            largato_config = bars_config.get("largato_skill_bar", {})
            if largato_config.get("configured", False) and hasattr(self.largato_skill_bar, 'configure_from_saved'):
                x1 = largato_config.get("x1")
                y1 = largato_config.get("y1")
                x2 = largato_config.get("x2")
                y2 = largato_config.get("y2")
                
                if all([x1 is not None, y1 is not None, x2 is not None, y2 is not None]):
                    if self.largato_skill_bar.configure_from_saved(x1, y1, x2, y2):
                        logger.info(f"Loaded Largato skill bar configuration: ({x1},{y1}) to ({x2},{y2})")
                        
                        if hasattr(self.largato_skill_bar, 'screen_selector'):
                            self.largato_skill_bar.screen_selector.title = "Largato Skill Bar"
                            
                        if not hasattr(self.largato_skill_bar.screen_selector, 'preview_image') or self.largato_skill_bar.screen_selector.preview_image is None:
                            try:
                                from PIL import ImageGrab
                                self.largato_skill_bar.screen_selector.preview_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                                logger.info("Created preview image for Largato skill bar")
                            except Exception as e:
                                logger.warning(f"Could not create preview image for Largato skill bar: {e}")
            
            self.settings_provider.set_settings(config)
            
            if hasattr(self.window_manager, 'root'):
                self.window_manager.root.after(500, self._update_ui_previews)
            
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
        try:
            if hasattr(self.window_manager, 'root'):
                root = self.window_manager.root
                
                if hasattr(self.window_manager, 'update_window_preview'):
                    self.window_manager.update_window_preview()
                
                for widget in root.winfo_children():
                    if hasattr(widget, 'bar_selector_ui'):
                        bar_selector_ui = widget.bar_selector_ui
                        
                        if hasattr(bar_selector_ui, 'update_preview_image'):
                            if hasattr(bar_selector_ui, 'hp_bar_selector') and hasattr(bar_selector_ui, 'hp_preview_label'):
                                bar_selector_ui.update_preview_image(bar_selector_ui.hp_bar_selector, bar_selector_ui.hp_preview_label)
                            
                            if hasattr(bar_selector_ui, 'mp_bar_selector') and hasattr(bar_selector_ui, 'mp_preview_label'):
                                bar_selector_ui.update_preview_image(bar_selector_ui.mp_bar_selector, bar_selector_ui.mp_preview_label)
                            
                            if hasattr(bar_selector_ui, 'sp_bar_selector') and hasattr(bar_selector_ui, 'sp_preview_label'):
                                bar_selector_ui.update_preview_image(bar_selector_ui.sp_bar_selector, bar_selector_ui.sp_preview_label)
                            
                            if hasattr(bar_selector_ui, 'largato_skill_selector') and hasattr(bar_selector_ui, 'largato_preview_label'):
                                bar_selector_ui.update_preview_image(bar_selector_ui.largato_skill_selector, bar_selector_ui.largato_preview_label)
        except Exception as e:
            logger.error(f"Error updating UI previews: {e}", exc_info=True)