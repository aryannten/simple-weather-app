"""
Configuration Manager for Weather App

Handles loading, saving, and validation of application configuration.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration with JSON file handling and validation."""
    
    DEFAULT_CONFIG = {
        "api_key": "",
        "theme": "light",
        "units": "metric",
        "favorites": [],
        "auto_refresh": False,
        "refresh_interval": 300
    }
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize ConfigManager with specified config file.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default if not exists.
        
        Returns:
            Dictionary containing configuration data
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.config = {**self.DEFAULT_CONFIG, **loaded_config}
            else:
                # Create default config file
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            self.config = self.DEFAULT_CONFIG.copy()
            
        return self.config
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set configuration value and save to file.
        
        Args:
            key: Configuration key
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        self.config[key] = value
        return self.save_config()
    
    def validate_config(self) -> Dict[str, str]:
        """
        Validate configuration and return any errors.
        
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Validate API key
        api_key = self.get_setting("api_key", "")
        if not api_key or api_key.strip() == "":
            errors["api_key"] = "API key is required"
        elif len(api_key) < 10:  # Basic length check
            errors["api_key"] = "API key appears to be invalid (too short)"
        
        # Validate theme
        theme = self.get_setting("theme", "light")
        if theme not in ["light", "dark"]:
            errors["theme"] = "Theme must be 'light' or 'dark'"
        
        # Validate units
        units = self.get_setting("units", "metric")
        if units not in ["metric", "imperial", "kelvin"]:
            errors["units"] = "Units must be 'metric', 'imperial', or 'kelvin'"
        
        # Validate refresh interval
        refresh_interval = self.get_setting("refresh_interval", 300)
        if not isinstance(refresh_interval, int) or refresh_interval < 60:
            errors["refresh_interval"] = "Refresh interval must be at least 60 seconds"
        
        # Validate favorites format
        favorites = self.get_setting("favorites", [])
        if not isinstance(favorites, list):
            errors["favorites"] = "Favorites must be a list"
        
        return errors
    
    def is_valid(self) -> bool:
        """
        Check if current configuration is valid.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return len(self.validate_config()) == 0
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults and save.
        
        Returns:
            True if successful, False otherwise
        """
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save_config()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all configuration settings.
        
        Returns:
            Dictionary containing all settings
        """
        return self.config.copy()
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update multiple settings at once.
        
        Args:
            settings: Dictionary of settings to update
            
        Returns:
            True if successful, False otherwise
        """
        self.config.update(settings)
        return self.save_config()