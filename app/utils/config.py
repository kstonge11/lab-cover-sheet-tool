"""
Configuration persistence for Lab Cover Sheet Tool.

Saves and loads user settings to a JSON file in the user's home directory.
Settings include Campaign #, Operator, Firmware, Phase#, and last used paths.

Usage:
    from app.utils.config import Config

    config = Config()
    
    # Load saved settings
    settings = config.load()
    campaign = settings.get("campaign", "")
    
    # Save settings
    config.save({
        "campaign": "12345",
        "operator": "John Doe",
        "firmware": "v1.2.3",
        "phase": "2",
        "last_data_path": "/path/to/data.xlsx",
        "last_cover_path": "/path/to/cover.xlsx",
        "last_save_dir": "/path/to/output"
    })
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import logger, log_exception


class Config:
    """Handles persistent configuration storage."""
    
    DEFAULT_CONFIG_PATH = Path.home() / ".lab_cover_config.json"
    
    # Default values for all settings
    DEFAULTS: Dict[str, Any] = {
        "campaign": "",
        "operator": "",
        "firmware": "",
        "phase": "",
        "last_data_path": "",
        "last_cover_path": "",
        "last_save_dir": "",
        "group_by_printer": False,
        "window_width": 1200,
        "window_height": 700,
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the config manager.
        
        Args:
            config_path: Optional custom path for the config file.
                        Defaults to ~/.lab_cover_config.json
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._cache: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """
        Load settings from the config file.
        
        Returns:
            Dictionary of settings with defaults for missing keys
        """
        settings = dict(self.DEFAULTS)
        
        if not self.config_path.exists():
            logger.debug(f"No config file found at {self.config_path}, using defaults")
            self._cache = settings
            return settings
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                settings.update(saved)
                logger.info(f"Loaded config from {self.config_path}")
                logger.debug(f"Config values: {settings}")
        except json.JSONDecodeError as e:
            log_exception(e, f"Invalid JSON in config file {self.config_path}")
        except Exception as e:
            log_exception(e, f"Error loading config from {self.config_path}")
        
        self._cache = settings
        return settings
    
    def save(self, settings: Dict[str, Any]) -> bool:
        """
        Save settings to the config file.
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Merge with existing settings to preserve keys not being updated
            current = self.load() if self._cache is None else dict(self._cache)
            current.update(settings)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2)
            
            self._cache = current
            logger.info(f"Saved config to {self.config_path}")
            logger.debug(f"Saved values: {current}")
            return True
            
        except Exception as e:
            log_exception(e, f"Error saving config to {self.config_path}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a single config value.
        
        Args:
            key: The setting key to retrieve
            default: Default value if key not found
            
        Returns:
            The setting value or default
        """
        if self._cache is None:
            self.load()
        return self._cache.get(key, default if default is not None else self.DEFAULTS.get(key))
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a single config value and save.
        
        Args:
            key: The setting key to set
            value: The value to save
            
        Returns:
            True if saved successfully
        """
        if self._cache is None:
            self.load()
        self._cache[key] = value
        return self.save(self._cache)
    
    def clear(self) -> bool:
        """
        Clear all settings and delete the config file.
        
        Returns:
            True if cleared successfully
        """
        try:
            if self.config_path.exists():
                self.config_path.unlink()
                logger.info(f"Deleted config file: {self.config_path}")
            self._cache = None
            return True
        except Exception as e:
            log_exception(e, "Error clearing config")
            return False
