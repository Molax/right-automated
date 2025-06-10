"""
Interface definitions for the Priston Tale Potion Bot
---------------------------------------------------
This module defines interfaces (abstract base classes) for bot components
to avoid circular dependencies between UI and bot logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable

class BarManager(ABC):
    """Interface for bar selection and management"""
    
    @abstractmethod
    def is_setup(self) -> bool:
        """Check if the bar is configured"""
        pass
    
    @abstractmethod
    def get_current_screenshot_region(self):
        """Get a screenshot of the selected region"""
        pass

class SettingsProvider(ABC):
    """Interface for settings access"""
    
    @abstractmethod
    def get_settings(self) -> Dict[str, Any]:
        """Get all current settings as a dictionary"""
        pass
    
    @abstractmethod
    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Apply settings from a dictionary"""
        pass

class WindowManager(ABC):
    """Interface for game window management"""
    
    @abstractmethod
    def is_setup(self) -> bool:
        """Check if the window is configured"""
        pass
    
    @property
    @abstractmethod
    def game_window(self):
        """Get the game window selector"""
        pass