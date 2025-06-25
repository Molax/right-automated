"""
Configuration module for the Priston Tale Potion Bot
---------------------------------------------------
This module handles configuration settings and logging setup.
"""

import os
import time
import logging
from logging.handlers import RotatingFileHandler
import json

DEFAULT_CONFIG = {
    "potion_keys": {
        "health": "1",
        "mana": "3",
        "stamina": "2"
    },
    "thresholds": {
        "health": 50,
        "mana": 30,
        "stamina": 40
    },
    "scan_interval": 0.5,
    "potion_cooldown": 3.0,
    "window_name": "Priston Tale",
    "debug_enabled": True,
    "spellcasting": {
        "enabled": False,
        "spell_key": "F5",
        "spell_interval": 3.0,
        "random_targeting": False,
        "target_radius": 100,
        "target_change_interval": 5,
        "target_method": "Ring Around Character",
        "target_points_count": 8,
        "target_zone": {
            "x1": None,
            "y1": None,
            "x2": None,
            "y2": None,
            "points": []
        }
    },
    "bars": {
        "health_bar": {
            "x1": None,
            "y1": None,
            "x2": None,
            "y2": None,
            "configured": False
        },
        "mana_bar": {
            "x1": None,
            "y1": None,
            "x2": None,
            "y2": None,
            "configured": False
        },
        "stamina_bar": {
            "x1": None,
            "y1": None,
            "x2": None,
            "y2": None,
            "configured": False
        },
        "largato_skill_bar": {
            "x1": None,
            "y1": None,
            "x2": None,
            "y2": None,
            "configured": False
        }
    }
}

def setup_logging():
    """Set up logging configuration"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger('PristonBot')
    logger.setLevel(logging.INFO)
    
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    log_file = os.path.join('logs', f'priston_bot_{time.strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    
    if DEFAULT_CONFIG["debug_enabled"]:
        debug_handler = logging.FileHandler(os.path.join('logs', f'debug_{time.strftime("%Y%m%d_%H%M%S")}.log'))
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(file_formatter)
        logger.addHandler(debug_handler)
        logger.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
    
    logger.info("Logging initialized")
    return logger

def load_config():
    """Load configuration from file or create default if not exists"""
    config_path = 'config.json'
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logging.getLogger('PristonBot').info("Configuration loaded from file")
                
                if "spellcasting" not in config:
                    config["spellcasting"] = DEFAULT_CONFIG["spellcasting"]
                    logging.getLogger('PristonBot').info("Added missing spellcasting configuration")
                    save_config(config)
                elif "random_targeting" not in config["spellcasting"]:
                    config["spellcasting"]["random_targeting"] = DEFAULT_CONFIG["spellcasting"]["random_targeting"]
                    config["spellcasting"]["target_radius"] = DEFAULT_CONFIG["spellcasting"]["target_radius"]
                    config["spellcasting"]["target_change_interval"] = DEFAULT_CONFIG["spellcasting"]["target_change_interval"]
                    logging.getLogger('PristonBot').info("Added missing random targeting configuration")
                    save_config(config)
                
                if "target_zone" not in config["spellcasting"]:
                    config["spellcasting"]["target_zone"] = DEFAULT_CONFIG["spellcasting"]["target_zone"]
                    config["spellcasting"]["target_method"] = DEFAULT_CONFIG["spellcasting"]["target_method"]
                    config["spellcasting"]["target_points_count"] = DEFAULT_CONFIG["spellcasting"]["target_points_count"]
                    logging.getLogger('PristonBot').info("Added missing target zone configuration")
                    save_config(config)
                
                if "bars" not in config:
                    config["bars"] = DEFAULT_CONFIG["bars"]
                    logging.getLogger('PristonBot').info("Added missing bars configuration")
                    save_config(config)
                
                if "largato_skill_bar" not in config["bars"]:
                    config["bars"]["largato_skill_bar"] = {
                        "x1": None,
                        "y1": None,
                        "x2": None,
                        "y2": None,
                        "configured": False
                    }
                    logging.getLogger('PristonBot').info("Added missing largato_skill_bar configuration")
                    save_config(config)
                
                if "game_window" in config["bars"]:
                    del config["bars"]["game_window"]
                    logging.getLogger('PristonBot').info("Removed deprecated game_window configuration")
                    save_config(config)
                
                return config
        except Exception as e:
            logging.getLogger('PristonBot').error(f"Error loading configuration: {e}")
            
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file"""
    config_path = 'config.json'
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        logging.getLogger('PristonBot').info("Configuration saved to file")
    except Exception as e:
        logging.getLogger('PristonBot').error(f"Error saving configuration: {e}")