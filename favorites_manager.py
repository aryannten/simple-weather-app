"""
Favorites Manager for Weather App

Handles CRUD operations for favorite cities with persistent storage.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from config_manager import ConfigManager


class FavoritesManager:
    """Manages user's favorite cities with persistent storage and validation."""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize FavoritesManager with ConfigManager instance.
        
        Args:
            config_manager: ConfigManager instance for persistent storage
        """
        self.config_manager = config_manager
        self._favorites_cache = None
    
    def load_favorites(self) -> List[Dict[str, Any]]:
        """
        Load favorites from configuration.
        
        Returns:
            List of favorite city dictionaries
        """
        favorites = self.config_manager.get_setting("favorites", [])
        
        # Validate and clean favorites data
        validated_favorites = []
        for favorite in favorites:
            if self._validate_favorite_structure(favorite):
                validated_favorites.append(favorite)
        
        # Update cache and save cleaned data if needed
        if len(validated_favorites) != len(favorites):
            self.config_manager.set_setting("favorites", validated_favorites)
        
        self._favorites_cache = validated_favorites
        return validated_favorites
    
    def add_favorite(self, city_name: str, country_code: str = "") -> bool:
        """
        Add city to favorites with validation and duplicate prevention.
        
        Args:
            city_name: Name of the city to add
            country_code: Optional country code (e.g., "US", "GB")
            
        Returns:
            True if successfully added, False if validation failed or duplicate
        """
        # Validate input
        if not self._validate_city_input(city_name, country_code):
            return False
        
        # Normalize city name for comparison
        normalized_city = self._normalize_city_name(city_name)
        normalized_country = country_code.upper().strip() if country_code else ""
        
        # Check for duplicates
        if self.is_favorite(city_name, country_code):
            return False
        
        # Create favorite entry
        favorite_entry = {
            "name": normalized_city,
            "country": normalized_country,
            "added_date": datetime.now().isoformat()
        }
        
        # Add to favorites
        current_favorites = self.load_favorites()
        current_favorites.append(favorite_entry)
        
        # Save to configuration
        success = self.config_manager.set_setting("favorites", current_favorites)
        if success:
            self._favorites_cache = current_favorites
        
        return success
    
    def remove_favorite(self, city_name: str, country_code: str = "") -> bool:
        """
        Remove city from favorites.
        
        Args:
            city_name: Name of the city to remove
            country_code: Optional country code for more precise matching
            
        Returns:
            True if successfully removed, False if not found
        """
        current_favorites = self.load_favorites()
        normalized_city = self._normalize_city_name(city_name)
        normalized_country = country_code.upper().strip() if country_code else ""
        
        # Find and remove matching favorite
        updated_favorites = []
        removed = False
        
        for favorite in current_favorites:
            if self._matches_favorite(favorite, normalized_city, normalized_country):
                removed = True
                continue
            updated_favorites.append(favorite)
        
        if removed:
            success = self.config_manager.set_setting("favorites", updated_favorites)
            if success:
                self._favorites_cache = updated_favorites
            return success
        
        return False
    
    def get_favorites(self) -> List[Dict[str, Any]]:
        """
        Get list of all favorite cities.
        
        Returns:
            List of favorite city dictionaries sorted by name
        """
        favorites = self.load_favorites()
        # Sort by city name for consistent display
        return sorted(favorites, key=lambda x: x.get("name", "").lower())
    
    def is_favorite(self, city_name: str, country_code: str = "") -> bool:
        """
        Check if city is in favorites.
        
        Args:
            city_name: Name of the city to check
            country_code: Optional country code for more precise matching
            
        Returns:
            True if city is in favorites, False otherwise
        """
        current_favorites = self.load_favorites()
        normalized_city = self._normalize_city_name(city_name)
        normalized_country = country_code.upper().strip() if country_code else ""
        
        for favorite in current_favorites:
            if self._matches_favorite(favorite, normalized_city, normalized_country):
                return True
        
        return False
    
    def get_favorites_count(self) -> int:
        """
        Get the number of favorite cities.
        
        Returns:
            Number of favorite cities
        """
        return len(self.load_favorites())
    
    def clear_all_favorites(self) -> bool:
        """
        Remove all favorite cities.
        
        Returns:
            True if successful, False otherwise
        """
        success = self.config_manager.set_setting("favorites", [])
        if success:
            self._favorites_cache = []
        return success
    
    def get_favorite_names(self) -> List[str]:
        """
        Get list of favorite city names for display purposes.
        
        Returns:
            List of city names with country codes if available
        """
        favorites = self.get_favorites()
        names = []
        
        for favorite in favorites:
            name = favorite.get("name", "")
            country = favorite.get("country", "")
            
            if country:
                names.append(f"{name}, {country}")
            else:
                names.append(name)
        
        return names
    
    def _validate_city_input(self, city_name: str, country_code: str) -> bool:
        """
        Validate city name and country code input.
        
        Args:
            city_name: City name to validate
            country_code: Country code to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Validate city name
        if not city_name or not isinstance(city_name, str):
            return False
        
        city_name = city_name.strip()
        if len(city_name) < 1 or len(city_name) > 100:
            return False
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", city_name):
            return False
        
        # Validate country code if provided
        if country_code:
            if not isinstance(country_code, str):
                return False
            
            country_code = country_code.strip().upper()
            if len(country_code) != 2 or not country_code.isalpha():
                return False
        
        return True
    
    def _validate_favorite_structure(self, favorite: Dict[str, Any]) -> bool:
        """
        Validate favorite dictionary structure.
        
        Args:
            favorite: Favorite dictionary to validate
            
        Returns:
            True if structure is valid, False otherwise
        """
        if not isinstance(favorite, dict):
            return False
        
        # Check required fields
        if "name" not in favorite:
            return False
        
        name = favorite.get("name")
        if not isinstance(name, str) or not name.strip():
            return False
        
        # Validate country code if present
        country = favorite.get("country", "")
        if country and (not isinstance(country, str) or len(country) != 2):
            return False
        
        # Validate date if present
        added_date = favorite.get("added_date")
        if added_date:
            try:
                datetime.fromisoformat(added_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False
        
        return True
    
    def _normalize_city_name(self, city_name: str) -> str:
        """
        Normalize city name for consistent storage and comparison.
        
        Args:
            city_name: City name to normalize
            
        Returns:
            Normalized city name
        """
        if not city_name:
            return ""
        
        # Strip whitespace and convert to title case
        normalized = city_name.strip().title()
        
        # Handle common abbreviations and special cases
        normalized = re.sub(r'\bSt\b', 'St.', normalized)
        normalized = re.sub(r'\bMt\b', 'Mt.', normalized)
        normalized = re.sub(r'\bFt\b', 'Ft.', normalized)
        
        return normalized
    
    def _matches_favorite(self, favorite: Dict[str, Any], city_name: str, country_code: str) -> bool:
        """
        Check if favorite matches the given city name and country code.
        
        Args:
            favorite: Favorite dictionary to check
            city_name: Normalized city name to match
            country_code: Normalized country code to match
            
        Returns:
            True if matches, False otherwise
        """
        favorite_name = favorite.get("name", "")
        favorite_country = favorite.get("country", "")
        
        # City name must match
        if favorite_name.lower() != city_name.lower():
            return False
        
        # If country code is provided, it must match
        if country_code and favorite_country:
            return favorite_country.upper() == country_code.upper()
        
        # If no country code provided, match any favorite with same city name
        return True