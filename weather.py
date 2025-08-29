import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser
import requests
from config_manager import ConfigManager
from theme_manager import ThemeManager
from favorites_manager import FavoritesManager
from error_handler import ErrorHandler, LoadingIndicator
from notification_system import NotificationManager
# from weather_service import WeatherService
from ui_components import (
    ThemedFrame, ThemedLabel, ThemedButton, ThemedEntry, 
    ThemeToggleButton, FavoritesList, FavoriteStarButton,
    ForecastContainer, create_themed_separator, apply_theme_to_existing_widget,
    parse_forecast_data, SettingsDialog
)

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast")
        self.root.geometry("800x750")
        self.root.resizable(False, False)
        
        # Initialize managers in proper order
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager(self.config_manager)
        self.favorites_manager = FavoritesManager(self.config_manager)
        self.error_handler = ErrorHandler(self.theme_manager)
        self.notification_manager = NotificationManager(self.root, self.theme_manager)
        # self.weather_service = WeatherService(self.config_manager)
        
        # Load configuration and apply theme on startup
        self._initialize_application()
        
        # Weather icons mapping
        self.weather_icons = {
            '01d': '☀️', '01n': '🌙',
            '02d': '⛅', '02n': '⛅',
            '03d': '☁️', '03n': '☁️',
            '04d': '☁️', '04n': '☁️',
            '09d': '🌧️', '09n': '🌧️',
            '10d': '🌦️', '10n': '🌦️',
            '11d': '⛈️', '11n': '⛈️',
            '13d': '❄️', '13n': '❄️',
            '50d': '🌫️', '50n': '🌫️'
        }
    
    def _initialize_application(self):
        """Initialize application with configuration and theme setup."""
        # Setup UI components first
        self.setup_ui()
        
        # Apply initial theme to root window
        self.apply_root_theme()
        
        # Register for theme changes
        self.theme_manager.register_theme_change_callback(self._on_theme_change)
        
        # Register error handler callback for notifications
        self.error_handler.register_notification_callback(self.notification_manager.show_notification)
        
        # Initialize loading indicators
        self.current_weather_loading = LoadingIndicator(self.weather_card, self.theme_manager)
        self.forecast_loading = LoadingIndicator(self.forecast_container, self.theme_manager)
        
        # Validate configuration on startup and show notifications
        self._validate_startup_configuration()
        
        # Load favorites on startup
        self.favorites_manager.load_favorites()
        
        # Initialize weather service functionality inline
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    
    def _validate_startup_configuration(self):
        """Validate configuration on startup and show appropriate notifications."""
        # Check for configuration file issues
        config_errors = self.config_manager.validate_config()
        if config_errors:
            for error in config_errors:
                notification = self.error_handler.handle_config_error("load_failed", error)
                self.notification_manager.show_notification(notification)
        
        # Check API key configuration
        api_key = self.config_manager.get_setting('api_key', '')
        if not api_key or api_key == 'your_api_key_here':
            notification = self.error_handler.create_api_key_missing_notification()
            self.notification_manager.show_notification(notification, force_type="bar")
        else:
            # Validate API key in background (don't block startup)
            self.root.after(1000, self._validate_api_key_async)
    
    def _validate_api_key_async(self):
        """Validate API key asynchronously and show notification if invalid."""
        try:
            api_key = self.config_manager.get_setting('api_key', '')
            if not api_key:
                return
                
            # Test API key with a simple request
            params = {
                'q': 'London',
                'appid': api_key,
                'units': 'metric'
            }
            
            import requests
            response = requests.get(self.base_url, params=params, timeout=5)
            
            if response.status_code == 401:
                notification = self.error_handler.handle_api_error(response, "API key validation")
                self.notification_manager.show_notification(notification, force_type="bar")
            elif response.status_code != 200:
                # Don't show error for other issues during validation
                pass
                
        except Exception:
            # Don't show errors for validation failures during startup
            pass
        
    def setup_ui(self):
        # Create notification manager first (will be initialized later)
        # This is a placeholder - actual initialization happens in _initialize_application
        
        # Main container with horizontal layout
        self.main_frame = ThemedFrame(self.root, self.theme_manager)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel for weather (main content)
        self.weather_panel = ThemedFrame(self.main_frame, self.theme_manager)
        self.weather_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel for favorites
        self.favorites_panel = ThemedFrame(self.main_frame, self.theme_manager, frame_type="card")
        self.favorites_panel.pack(side='right', fill='y', padx=(10, 0))
        self.favorites_panel.configure(width=250)
        self.favorites_panel.pack_propagate(False)
        
        # Header
        self.header_frame = ThemedFrame(self.weather_panel, self.theme_manager)
        self.header_frame.pack(fill='x', pady=(0, 20))
        
        self.title_label = ThemedLabel(
            self.header_frame,
            self.theme_manager,
            label_type="title",
            text="Weather Forecast",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(side='left')
        
        # Button container for right side
        button_frame = ThemedFrame(self.header_frame, self.theme_manager)
        button_frame.pack(side='right')
        
        # Settings button
        self.settings_btn = ThemedButton(
            button_frame,
            self.theme_manager,
            button_type="secondary",
            text="⚙️",
            font=("Arial", 12),
            command=self.show_settings,
            width=3
        )
        self.settings_btn.pack(side='right', padx=5)
        
        # Theme toggle button
        self.theme_toggle_btn = ThemeToggleButton(
            button_frame,
            self.theme_manager,
            font=("Arial", 14),
            width=3
        )
        self.theme_toggle_btn.pack(side='right', padx=5)
        
        # Refresh button
        self.refresh_btn = ThemedButton(
            button_frame,
            self.theme_manager,
            button_type="secondary",
            text="🔄",
            font=("Arial", 12),
            command=self.refresh_weather,
            width=3
        )
        self.refresh_btn.pack(side='right', padx=5)
        
        # Search frame
        self.search_frame = ThemedFrame(self.weather_panel, self.theme_manager)
        self.search_frame.pack(fill='x', pady=(0, 20))
        
        # City input with placeholder
        self.city_entry = ThemedEntry(
            self.search_frame,
            self.theme_manager,
            font=("Helvetica", 14),
            width=25,
            justify='center'
        )
        self.city_entry.pack(pady=5, ipady=5)
        self.city_entry.insert(0, "Enter city name...")
        self.city_entry.bind('<FocusIn>', self.clear_placeholder)
        self.city_entry.bind('<FocusOut>', self.restore_placeholder)
        self.city_entry.bind('<Return>', lambda event: self.get_weather())
        
        # Search button
        self.search_btn = ThemedButton(
            self.search_frame,
            self.theme_manager,
            button_type="primary",
            text="Get Weather",
            font=("Helvetica", 12, "bold"),
            command=self.get_weather,
            padx=20,
            pady=8
        )
        self.search_btn.pack(pady=5)
        
        # Weather display card
        self.weather_card = ThemedFrame(
            self.weather_panel,
            self.theme_manager,
            frame_type="weather_card"
        )
        self.weather_card.pack(fill='both', expand=True)
        
        # Current weather frame
        self.current_weather_frame = ThemedFrame(self.weather_card, self.theme_manager, frame_type="weather_card")
        self.current_weather_frame.pack(fill='x', pady=10, padx=10)
        
        # Weather icon and city
        self.weather_icon_label = ThemedLabel(
            self.current_weather_frame,
            self.theme_manager,
            label_type="primary",
            text="",
            font=("Arial", 48)
        )
        self.weather_icon_label.pack(side='left', padx=10)
        
        city_temp_frame = ThemedFrame(self.current_weather_frame, self.theme_manager, frame_type="weather_card")
        city_temp_frame.pack(side='left', fill='both', expand=True)
        
        # City name and favorite star container
        city_header_frame = ThemedFrame(city_temp_frame, self.theme_manager, frame_type="weather_card")
        city_header_frame.pack(fill='x')
        
        self.city_label = ThemedLabel(
            city_header_frame,
            self.theme_manager,
            label_type="title",
            text="",
            font=("Helvetica", 18, "bold"),
            anchor='w'
        )
        self.city_label.pack(side='left', fill='x', expand=True)
        
        # Favorite star button
        self.favorite_star = FavoriteStarButton(
            city_header_frame,
            self.theme_manager,
            self.favorites_manager
        )
        self.favorite_star.pack(side='right', padx=(5, 0))
        self.favorite_star.set_favorite_changed_callback(self._on_favorite_changed)
        
        self.temp_label = ThemedLabel(
            city_temp_frame,
            self.theme_manager,
            label_type="primary",
            text="",
            font=("Helvetica", 36, "bold"),
            anchor='w'
        )
        self.temp_label.pack(fill='x')
        
        # Weather description
        self.desc_label = ThemedLabel(
            self.current_weather_frame,
            self.theme_manager,
            label_type="secondary",
            text="",
            font=("Helvetica", 14)
        )
        self.desc_label.pack(side='right', padx=10)
        
        # Feels like label
        self.feels_like_label = ThemedLabel(
            self.weather_card,
            self.theme_manager,
            label_type="muted",
            text="",
            font=("Helvetica", 12)
        )
        self.feels_like_label.pack(anchor='w', padx=20)
        
        # Separator
        self.separator = create_themed_separator(self.weather_card, self.theme_manager, orient='horizontal')
        self.separator.pack(fill='x', pady=10)
        
        # Additional info grid
        self.info_frame = ThemedFrame(self.weather_card, self.theme_manager, frame_type="weather_card")
        self.info_frame.pack(fill='x', padx=20, pady=10)
        
        # Row 1
        self.humidity_label = self.create_info_label(self.info_frame, "💧 Humidity:", "")
        self.pressure_label = self.create_info_label(self.info_frame, "📊 Pressure:", "")
        
        # Row 2
        self.wind_label = self.create_info_label(self.info_frame, "💨 Wind:", "")
        self.visibility_label = self.create_info_label(self.info_frame, "👁️ Visibility:", "")
        
        # Last updated and credit
        self.bottom_frame = ThemedFrame(self.weather_card, self.theme_manager, frame_type="weather_card")
        self.bottom_frame.pack(fill='x', pady=(10, 0))
        
        self.updated_label = ThemedLabel(
            self.bottom_frame,
            self.theme_manager,
            label_type="muted",
            text="",
            font=("Helvetica", 9)
        )
        self.updated_label.pack(side='left', padx=20)
        
        self.credit_label = ThemedLabel(
            self.bottom_frame,
            self.theme_manager,
            label_type="info",
            text="Powered by OpenWeather",
            font=("Helvetica", 9, "underline"),
            cursor='hand2'
        )
        self.credit_label.pack(side='right', padx=20)
        self.credit_label.bind("<Button-1>", lambda e: webbrowser.open("https://openweathermap.org"))
        
        # Forecast separator
        self.forecast_separator = create_themed_separator(self.weather_card, self.theme_manager, orient='horizontal')
        
        # 5-Day Forecast Container
        self.forecast_container = ForecastContainer(self.weather_card, self.theme_manager)
        
        # Initially hide weather card
        self.weather_card.pack_forget()
        
        # Add error label (hidden by default)
        self.error_label = ThemedLabel(
            self.weather_panel,
            self.theme_manager,
            label_type="error",
            text="",
            font=("Helvetica", 12)
        )
        
        # Setup favorites panel
        self.setup_favorites_panel()
        
    def create_info_label(self, parent, title, value):
        """Helper function to create consistent info labels"""
        frame = ThemedFrame(parent, self.theme_manager, frame_type="weather_card")
        frame.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        ThemedLabel(
            frame,
            self.theme_manager,
            label_type="secondary",
            text=title,
            font=("Helvetica", 11),
            anchor='w'
        ).pack(fill='x')
        
        value_label = ThemedLabel(
            frame,
            self.theme_manager,
            label_type="primary",
            text=value,
            font=("Helvetica", 12, "bold"),
            anchor='w'
        )
        value_label.pack(fill='x')
        
        return value_label
    
    def setup_favorites_panel(self):
        """Setup the favorites panel with the favorites list."""
        # Create favorites list
        self.favorites_list = FavoritesList(
            self.favorites_panel,
            self.theme_manager,
            self.favorites_manager,
            on_city_click=self._on_favorite_city_clicked
        )
        self.favorites_list.pack(fill='both', expand=True)
    
    def _on_favorite_city_clicked(self, city_name: str, country_code: str):
        """Handle click on favorite city with error handling."""
        try:
            # Clear any existing notifications
            self.notification_manager.clear_all_notifications()
            
            # Set the city in the search entry
            self.city_entry.delete(0, tk.END)
            display_name = f"{city_name}, {country_code}" if country_code else city_name
            self.city_entry.insert(0, display_name)
            
            # Clear placeholder styling
            colors = self.theme_manager.get_colors()
            self.city_entry.config(fg=colors["text_primary"])
            
            # Get weather for the selected city
            self.get_weather()
        except Exception as e:
            notification = self.error_handler.handle_general_error(e, f"loading favorite city {city_name}")
            self.notification_manager.show_notification(notification)
    
    def _on_favorite_changed(self, city_name: str, country_code: str, is_favorite: bool):
        """Handle favorite status change with error handling and user feedback."""
        try:
            # Refresh the favorites list to show updated state
            self.favorites_list.refresh_favorites()
            
            # Show user-friendly notification
            from error_handler import UserNotification, ErrorType, ErrorSeverity
            if is_favorite:
                message = f"Added {city_name} to favorites"
                notification = UserNotification(
                    message=message,
                    error_type=ErrorType.GENERAL_ERROR,  # Using general for info messages
                    severity=ErrorSeverity.INFO,
                    dismissible=True,
                    auto_dismiss_ms=3000
                )
            else:
                message = f"Removed {city_name} from favorites"
                notification = UserNotification(
                    message=message,
                    error_type=ErrorType.GENERAL_ERROR,
                    severity=ErrorSeverity.INFO,
                    dismissible=True,
                    auto_dismiss_ms=3000
                )
            
            self.notification_manager.show_notification(notification, force_type="toast")
            
        except Exception as e:
            notification = self.error_handler.handle_general_error(e, "updating favorite status")
            self.notification_manager.show_notification(notification)
        
    def clear_placeholder(self, event):
        """Clear placeholder text when entry gets focus"""
        if self.city_entry.get() == "Enter city name...":
            self.city_entry.delete(0, tk.END)
            colors = self.theme_manager.get_colors()
            self.city_entry.config(fg=colors["text_primary"])
            
    def restore_placeholder(self, event):
        """Restore placeholder text if entry is empty"""
        if not self.city_entry.get():
            self.city_entry.insert(0, "Enter city name...")
            colors = self.theme_manager.get_colors()
            self.city_entry.config(fg=colors["text_muted"])
            
    def refresh_weather(self):
        """Refresh the current weather and forecast with error handling"""
        current_city = self.city_label.cget("text")
        if current_city and current_city != "Enter city name..." and current_city != "Loading..." and current_city.strip():
            # Clear any existing notifications
            self.notification_manager.clear_all_notifications()
            
            # Set city in entry and refresh
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, current_city)
            
            # Clear placeholder styling
            colors = self.theme_manager.get_colors()
            self.city_entry.config(fg=colors["text_primary"])
            
            self.get_weather()
        else:
            # No current city to refresh
            notification = self.error_handler.handle_validation_error(
                "refresh", "", "No current weather data to refresh"
            )
            self.notification_manager.show_notification(notification)
            
    def get_weather(self):
        city = self.city_entry.get().strip()
        
        # Validate city input
        if not city or city == "Enter city name...":
            notification = self.error_handler.handle_validation_error("city_name", "", "City name is required")
            self.notification_manager.show_notification(notification)
            return
        
        # Additional validation for city name format
        if len(city) < 2:
            notification = self.error_handler.handle_validation_error(
                "city_name", city, "City name must be at least 2 characters long"
            )
            self.notification_manager.show_notification(notification)
            return
        
        # Check for invalid characters (basic validation)
        import re
        if not re.match(r'^[a-zA-Z\s\-\.,\']+$', city):
            notification = self.error_handler.handle_validation_error(
                "city_name", city, "City name contains invalid characters"
            )
            self.notification_manager.show_notification(notification)
            return
            
        # Clear any previous notifications and errors
        self.notification_manager.clear_all_notifications()
        self.error_label.pack_forget()
        
        # Check API key before making request
        api_key = self.config_manager.get_setting('api_key', '')
        if not api_key or api_key == 'your_api_key_here':
            notification = self.error_handler.create_api_key_missing_notification()
            self.notification_manager.show_notification(notification, force_type="bar")
            return
        
        # Show loading indicators
        self.show_loading_with_indicators()
        
        # Get current weather using integrated service with comprehensive error handling
        try:
            params = {
                'q': city,
                'appid': api_key,
                'units': self.config_manager.get_setting('units', 'metric')
            }
            
            import requests
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                weather_data = response.json()
                self.display_weather(weather_data)
                # Fetch 5-day forecast with graceful degradation
                self.fetch_forecast_with_error_handling(city)
            else:
                # Handle API errors with detailed messaging
                notification = self.error_handler.handle_api_error(response, f"fetching weather for {city}")
                self.notification_manager.show_notification(notification)
                self.hide_loading_indicators()
                
        except requests.exceptions.Timeout:
            notification = self.error_handler.handle_network_error(
                requests.exceptions.Timeout("Request timed out"), 
                f"fetching weather for {city}"
            )
            self.notification_manager.show_notification(notification)
            self.hide_loading_indicators()
        except requests.exceptions.ConnectionError as e:
            notification = self.error_handler.handle_network_error(e, f"fetching weather for {city}")
            self.notification_manager.show_notification(notification)
            self.hide_loading_indicators()
        except requests.exceptions.RequestException as e:
            notification = self.error_handler.handle_network_error(e, f"fetching weather for {city}")
            self.notification_manager.show_notification(notification)
            self.hide_loading_indicators()
        except Exception as e:
            notification = self.error_handler.handle_general_error(e, f"fetching weather for {city}")
            self.notification_manager.show_notification(notification)
            self.hide_loading_indicators()
    
    def fetch_forecast_with_error_handling(self, city: str):
        """
        Fetch 5-day forecast data with graceful degradation.
        Implements graceful degradation when forecast API fails but current weather succeeds.
        """
        try:
            api_key = self.config_manager.get_setting('api_key', '')
            if not api_key:
                # Show informative notification about forecast unavailability
                notification = self.error_handler.handle_forecast_error(
                    "API key not configured for forecast", 
                    current_weather_available=True
                )
                self.notification_manager.show_notification(notification, force_type="toast")
                self.forecast_loading.hide()
                return
                
            params = {
                'q': city,
                'appid': api_key,
                'units': self.config_manager.get_setting('units', 'metric')
            }
            
            import requests
            response = requests.get(self.forecast_url, params=params, timeout=10)
            
            if response.status_code == 200:
                forecast_data = response.json()
                self.display_forecast(forecast_data)
                self.forecast_loading.hide()
            else:
                # Handle forecast API errors with graceful degradation
                if response.status_code == 404:
                    error_context = f"Forecast not available for {city}"
                elif response.status_code == 401:
                    error_context = "Invalid API key for forecast service"
                else:
                    error_data = response.json() if response.content else {}
                    error_context = error_data.get('message', f'Forecast service error (Code: {response.status_code})')
                
                notification = self.error_handler.handle_forecast_error(
                    error_context, 
                    current_weather_available=True
                )
                self.notification_manager.show_notification(notification, force_type="toast")
                self.forecast_container.show_forecast_error("5-day forecast temporarily unavailable")
                self.forecast_loading.hide()
                
        except requests.exceptions.Timeout:
            notification = self.error_handler.handle_forecast_error(
                "Forecast request timed out", 
                current_weather_available=True
            )
            self.notification_manager.show_notification(notification, force_type="toast")
            self.forecast_container.show_forecast_error("Forecast temporarily unavailable")
            self.forecast_loading.hide()
        except requests.exceptions.ConnectionError:
            notification = self.error_handler.handle_forecast_error(
                "Network connection error for forecast", 
                current_weather_available=True
            )
            self.notification_manager.show_notification(notification, force_type="toast")
            self.forecast_container.show_forecast_error("Forecast temporarily unavailable")
            self.forecast_loading.hide()
        except Exception as e:
            notification = self.error_handler.handle_forecast_error(
                f"Unexpected forecast error: {str(e)}", 
                current_weather_available=True
            )
            self.notification_manager.show_notification(notification, force_type="toast")
            self.forecast_container.show_forecast_error("Forecast temporarily unavailable")
            self.forecast_loading.hide()
    
    def display_forecast(self, forecast_data):
        """Display 5-day forecast information"""
        try:
            # Hide forecast loading indicator
            self.forecast_loading.hide()
            
            # Parse forecast data using the utility function
            processed_forecasts = parse_forecast_data(forecast_data)
            
            if processed_forecasts:
                # Update forecast container with processed data
                self.forecast_container.update_forecast(processed_forecasts, self.weather_icons)
                
                # Show forecast separator and container
                self.forecast_separator.pack(fill='x', pady=(15, 10))
                self.forecast_container.pack(fill='x', padx=10, pady=(0, 10))
            else:
                notification = self.error_handler.handle_forecast_error(
                    "No forecast data available in API response", 
                    current_weather_available=True
                )
                self.notification_manager.show_notification(notification, force_type="toast")
                self.forecast_container.show_forecast_error("No forecast data available")
                
        except Exception as e:
            notification = self.error_handler.handle_general_error(e, "parsing forecast data")
            self.notification_manager.show_notification(notification, force_type="toast")
            self.forecast_container.show_forecast_error("Error displaying forecast data")
    
    def show_loading_with_indicators(self):
        """Show loading state with proper loading indicators for async operations."""
        # Clear any existing error displays
        self.error_label.pack_forget()
        
        # Show weather card
        self.weather_card.pack(fill='both', expand=True)
        
        # Show current weather loading indicator
        self.current_weather_loading.show("Loading current weather...")
        
        # Clear existing weather data
        self.city_label.config(text="")
        self.temp_label.config(text="")
        self.desc_label.config(text="")
        self.feels_like_label.config(text="")
        self.humidity_label.config(text="")
        self.pressure_label.config(text="")
        self.wind_label.config(text="")
        self.visibility_label.config(text="")
        self.updated_label.config(text="")
        self.weather_icon_label.config(text="")
        
        # Show forecast loading state
        self.forecast_separator.pack(fill='x', pady=(15, 10))
        self.forecast_container.pack(fill='x', padx=10, pady=(0, 10))
        self.forecast_loading.show("Loading 5-day forecast...")
        
        self.root.update()
    
    def hide_loading_indicators(self):
        """Hide all loading indicators."""
        self.current_weather_loading.hide()
        self.forecast_loading.hide()
    
    def show_loading(self):
        """Legacy method - redirect to new loading system."""
        self.show_loading_with_indicators()
    
    def show_error(self, message):
        """Legacy error display method - now uses notification system"""
        # Hide loading indicators
        self.hide_loading_indicators()
        
        # Create and show error notification
        from error_handler import UserNotification, ErrorType, ErrorSeverity
        notification = UserNotification(
            message=message,
            error_type=ErrorType.GENERAL_ERROR,
            severity=ErrorSeverity.ERROR,
            dismissible=True,
            auto_dismiss_ms=8000
        )
        self.notification_manager.show_notification(notification)
        
        # Hide weather card and forecast components for general errors
        self.weather_card.pack_forget()
        self.forecast_separator.pack_forget()
        self.forecast_container.pack_forget()
        
    def display_weather(self, data):
        """Display weather information"""
        try:
            # Hide current weather loading indicator
            self.current_weather_loading.hide()
            
            # Extract weather data
            city_name = data['name']
            country_code = data['sys'].get('country', '')
            temp = round(data['main']['temp'])
            feels_like = round(data['main']['feels_like'])
            description = data['weather'][0]['description'].title()
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind_speed = data['wind']['speed']
            visibility = data.get('visibility', 0) / 1000  # Convert to km
            icon_code = data['weather'][0]['icon']
            weather_icon = self.weather_icons.get(icon_code, '☁️')
            
            # Update labels
            self.city_label.config(text=f"{city_name}")
            self.temp_label.config(text=f"{temp}°C")
            self.desc_label.config(text=description)
            self.feels_like_label.config(text=f"Feels like {feels_like}°C")
            self.weather_icon_label.config(text=weather_icon)
            
            self.humidity_label.config(text=f"{humidity}%")
            self.pressure_label.config(text=f"{pressure} hPa")
            self.wind_label.config(text=f"{wind_speed} m/s")
            self.visibility_label.config(text=f"{visibility:.1f} km")
            
            # Update timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.updated_label.config(text=f"Last updated: {current_time}")
            
            # Change temperature color based on value using theme colors
            colors = self.theme_manager.get_colors()
            if temp <= 0:
                temp_color = colors["info"]  # Blue for cold
            elif temp <= 10:
                temp_color = colors["success"]  # Green for cool
            elif temp <= 25:
                temp_color = colors["warning"]  # Orange for mild
            else:
                temp_color = colors["error"]  # Red for hot
                
            self.temp_label.config(fg=temp_color)
            
            # Update favorite star button with current city
            self.favorite_star.set_city(city_name, country_code)
            
            # Show the weather card if hidden
            self.weather_card.pack(fill='both', expand=True)
            
        except KeyError as e:
            notification = self.error_handler.handle_general_error(
                KeyError(f"Missing weather data field: {str(e)}"), 
                "parsing weather data"
            )
            self.notification_manager.show_notification(notification)
            self.hide_loading_indicators()
        except Exception as e:
            notification = self.error_handler.handle_general_error(e, "displaying weather data")
            self.notification_manager.show_notification(notification)
            self.hide_loading_indicators()
    
    def apply_root_theme(self):
        """Apply theme to root window."""
        colors = self.theme_manager.get_colors()
        self.root.configure(bg=colors["bg_primary"])
    
    def show_settings(self):
        """Show the settings dialog with error handling."""
        try:
            settings_dialog = SettingsDialog(self.root, self.config_manager, self.theme_manager)
            settings_dialog.show()
            
            # After settings dialog closes, re-validate configuration
            self.root.after(500, self._revalidate_after_settings)
        except Exception as e:
            notification = self.error_handler.handle_general_error(e, "opening settings dialog")
            self.notification_manager.show_notification(notification)
    
    def _revalidate_after_settings(self):
        """Re-validate configuration after settings dialog closes."""
        # Check if API key was updated
        api_key = self.config_manager.get_setting('api_key', '')
        if api_key and api_key != 'your_api_key_here':
            # Clear any existing API key error notifications
            self.notification_manager.clear_all_notifications()
            
            # Validate the new API key
            self.root.after(100, self._validate_api_key_async)
    
    def _on_theme_change(self, old_theme: str, new_theme: str):
        """Handle theme change notification."""
        self.apply_root_theme()
        
        # Update placeholder text color if needed
        if self.city_entry.get() == "Enter city name...":
            colors = self.theme_manager.get_colors()
            self.city_entry.config(fg=colors["text_muted"])
    
    def on_closing(self):
        """Handle application closing with error handling."""
        try:
            # Ensure all configuration is saved
            self.config_manager.save_config()
            
            # Clean up any pending operations
            if hasattr(self, 'current_weather_loading'):
                self.current_weather_loading.hide()
            if hasattr(self, 'forecast_loading'):
                self.forecast_loading.hide()
            
            # Clear all notifications
            if hasattr(self, 'notification_manager'):
                self.notification_manager.clear_all_notifications()
            
        except Exception as e:
            # Don't show notifications during shutdown, just log
            print(f"Error during application shutdown: {e}")
        finally:
            self.root.destroy()

def main():
    """Main application entry point with proper initialization."""
    root = tk.Tk()
    
    # Set window icon if possible
    try:
        root.iconbitmap('weather_icon.ico')  # You can provide an icon file
    except:
        pass
    
    # Initialize the weather application
    app = WeatherApp(root)
    
    # Register closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window
    try:
        root.eval('tk::PlaceWindow . center')
    except:
        # Fallback centering method
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()