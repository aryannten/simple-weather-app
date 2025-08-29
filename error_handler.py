"""
Comprehensive Error Handler for Weather App

Provides centralized error handling, user notifications, and graceful degradation
for various error scenarios including API failures, configuration issues, and network problems.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Dict, Any
import requests
import json
from enum import Enum
from theme_manager import ThemeManager


class ErrorType(Enum):
    """Enumeration of different error types for categorized handling."""
    NETWORK_ERROR = "network"
    API_ERROR = "api"
    CONFIG_ERROR = "config"
    VALIDATION_ERROR = "validation"
    FORECAST_ERROR = "forecast"
    GENERAL_ERROR = "general"


class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class UserNotification:
    """Represents a user notification with message, type, and display options."""
    
    def __init__(self, message: str, error_type: ErrorType, severity: ErrorSeverity, 
                 dismissible: bool = True, auto_dismiss_ms: Optional[int] = None):
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.dismissible = dismissible
        self.auto_dismiss_ms = auto_dismiss_ms


class ErrorHandler:
    """Centralized error handling and user notification system."""
    
    def __init__(self, theme_manager: ThemeManager):
        """
        Initialize ErrorHandler with theme support.
        
        Args:
            theme_manager: ThemeManager instance for themed notifications
        """
        self.theme_manager = theme_manager
        self.notification_callbacks = []
        self.error_log = []
        
        # Error message templates
        self.error_messages = {
            # Network errors
            "network_timeout": "Connection timed out. Please check your internet connection and try again.",
            "network_connection": "Unable to connect to weather service. Please check your internet connection.",
            "network_dns": "Cannot resolve weather service address. Please check your internet connection.",
            
            # API errors
            "api_key_invalid": "Invalid API key. Please check your API key in settings.",
            "api_key_missing": "API key is required. Please configure your API key in settings.",
            "api_rate_limit": "Too many requests. Please wait a moment before trying again.",
            "api_city_not_found": "City not found. Please check the spelling and try again.",
            "api_service_unavailable": "Weather service is temporarily unavailable. Please try again later.",
            
            # Configuration errors
            "config_file_corrupt": "Configuration file is corrupted. Using default settings.",
            "config_save_failed": "Failed to save configuration. Changes may not persist.",
            "config_load_failed": "Failed to load configuration. Using default settings.",
            
            # Forecast specific errors
            "forecast_unavailable": "5-day forecast is temporarily unavailable, but current weather is still available.",
            "forecast_partial": "Some forecast data is missing. Showing available information.",
            
            # Validation errors
            "city_name_empty": "Please enter a city name.",
            "city_name_invalid": "Invalid city name. Please use only letters, spaces, and common punctuation.",
            
            # General errors
            "unexpected_error": "An unexpected error occurred. Please try again.",
            "data_parsing_error": "Unable to process weather data. Please try again."
        }
    
    def handle_network_error(self, exception: Exception, context: str = "") -> UserNotification:
        """
        Handle network-related errors with specific messaging.
        
        Args:
            exception: The network exception that occurred
            context: Additional context about when the error occurred
            
        Returns:
            UserNotification object for display
        """
        error_key = "network_connection"
        
        if isinstance(exception, requests.exceptions.Timeout):
            error_key = "network_timeout"
        elif isinstance(exception, requests.exceptions.ConnectionError):
            if "Name or service not known" in str(exception) or "getaddrinfo failed" in str(exception):
                error_key = "network_dns"
            else:
                error_key = "network_connection"
        
        message = self.error_messages.get(error_key, self.error_messages["network_connection"])
        if context:
            message = f"{message} (Context: {context})"
        
        notification = UserNotification(
            message=message,
            error_type=ErrorType.NETWORK_ERROR,
            severity=ErrorSeverity.ERROR,
            dismissible=True,
            auto_dismiss_ms=8000
        )
        
        self._log_error(notification, exception)
        return notification
    
    def handle_api_error(self, response: requests.Response, context: str = "") -> UserNotification:
        """
        Handle API-specific errors based on response status and content.
        
        Args:
            response: The HTTP response object
            context: Additional context about the API call
            
        Returns:
            UserNotification object for display
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
            api_message = error_data.get('message', '')
        except (json.JSONDecodeError, ValueError):
            api_message = response.text
        
        if status_code == 401:
            error_key = "api_key_invalid"
            severity = ErrorSeverity.CRITICAL
        elif status_code == 404:
            error_key = "api_city_not_found"
            severity = ErrorSeverity.WARNING
        elif status_code == 429:
            error_key = "api_rate_limit"
            severity = ErrorSeverity.WARNING
        elif status_code >= 500:
            error_key = "api_service_unavailable"
            severity = ErrorSeverity.ERROR
        else:
            error_key = "api_service_unavailable"
            severity = ErrorSeverity.ERROR
        
        base_message = self.error_messages.get(error_key, self.error_messages["api_service_unavailable"])
        
        # Add API message if helpful and different from our message
        if api_message and api_message.lower() not in base_message.lower():
            message = f"{base_message} (API: {api_message})"
        else:
            message = base_message
        
        if context:
            message = f"{message} (Context: {context})"
        
        notification = UserNotification(
            message=message,
            error_type=ErrorType.API_ERROR,
            severity=severity,
            dismissible=True,
            auto_dismiss_ms=10000 if severity == ErrorSeverity.CRITICAL else 8000
        )
        
        self._log_error(notification, f"HTTP {status_code}: {api_message}")
        return notification
    
    def handle_config_error(self, error_type: str, details: str = "") -> UserNotification:
        """
        Handle configuration-related errors.
        
        Args:
            error_type: Type of configuration error
            details: Additional error details
            
        Returns:
            UserNotification object for display
        """
        error_key = f"config_{error_type}"
        message = self.error_messages.get(error_key, self.error_messages["config_load_failed"])
        
        if details:
            message = f"{message} Details: {details}"
        
        severity = ErrorSeverity.CRITICAL if error_type == "api_key_missing" else ErrorSeverity.WARNING
        
        notification = UserNotification(
            message=message,
            error_type=ErrorType.CONFIG_ERROR,
            severity=severity,
            dismissible=True,
            auto_dismiss_ms=None if severity == ErrorSeverity.CRITICAL else 8000
        )
        
        self._log_error(notification, details)
        return notification
    
    def handle_forecast_error(self, error_context: str, current_weather_available: bool = True) -> UserNotification:
        """
        Handle forecast-specific errors with graceful degradation.
        
        Args:
            error_context: Context about the forecast error
            current_weather_available: Whether current weather is still available
            
        Returns:
            UserNotification object for display
        """
        if current_weather_available:
            message = self.error_messages["forecast_unavailable"]
            severity = ErrorSeverity.INFO
        else:
            message = f"Weather service error: {error_context}"
            severity = ErrorSeverity.ERROR
        
        notification = UserNotification(
            message=message,
            error_type=ErrorType.FORECAST_ERROR,
            severity=severity,
            dismissible=True,
            auto_dismiss_ms=6000 if severity == ErrorSeverity.INFO else 8000
        )
        
        self._log_error(notification, error_context)
        return notification
    
    def handle_validation_error(self, field: str, value: str, reason: str = "") -> UserNotification:
        """
        Handle input validation errors.
        
        Args:
            field: The field that failed validation
            value: The invalid value
            reason: Reason for validation failure
            
        Returns:
            UserNotification object for display
        """
        if field == "city_name":
            if not value or value.strip() == "":
                error_key = "city_name_empty"
            else:
                error_key = "city_name_invalid"
        else:
            error_key = "validation_error"
        
        message = self.error_messages.get(error_key, f"Invalid {field}: {reason}")
        
        notification = UserNotification(
            message=message,
            error_type=ErrorType.VALIDATION_ERROR,
            severity=ErrorSeverity.WARNING,
            dismissible=True,
            auto_dismiss_ms=5000
        )
        
        self._log_error(notification, f"Field: {field}, Value: {value}, Reason: {reason}")
        return notification
    
    def handle_general_error(self, exception: Exception, context: str = "") -> UserNotification:
        """
        Handle general/unexpected errors.
        
        Args:
            exception: The exception that occurred
            context: Additional context about when the error occurred
            
        Returns:
            UserNotification object for display
        """
        error_message = str(exception)
        
        if "json" in error_message.lower() or "parsing" in error_message.lower():
            base_message = self.error_messages["data_parsing_error"]
        else:
            base_message = self.error_messages["unexpected_error"]
        
        if context:
            message = f"{base_message} (Context: {context})"
        else:
            message = base_message
        
        notification = UserNotification(
            message=message,
            error_type=ErrorType.GENERAL_ERROR,
            severity=ErrorSeverity.ERROR,
            dismissible=True,
            auto_dismiss_ms=8000
        )
        
        self._log_error(notification, exception)
        return notification
    
    def create_api_key_missing_notification(self) -> UserNotification:
        """
        Create notification for missing API key with action guidance.
        
        Returns:
            UserNotification object for display
        """
        message = "API key is required to fetch weather data. Please configure your API key in the settings."
        
        notification = UserNotification(
            message=message,
            error_type=ErrorType.CONFIG_ERROR,
            severity=ErrorSeverity.CRITICAL,
            dismissible=False,  # Force user to address this
            auto_dismiss_ms=None
        )
        
        self._log_error(notification, "API key not configured")
        return notification
    
    def register_notification_callback(self, callback: Callable[[UserNotification], None]):
        """
        Register a callback to be called when notifications are created.
        
        Args:
            callback: Function to call with UserNotification objects
        """
        if callback not in self.notification_callbacks:
            self.notification_callbacks.append(callback)
    
    def unregister_notification_callback(self, callback: Callable[[UserNotification], None]):
        """
        Unregister a notification callback.
        
        Args:
            callback: Function to remove from callbacks
        """
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
    
    def _log_error(self, notification: UserNotification, details: Any):
        """
        Log error details for debugging and monitoring.
        
        Args:
            notification: The notification object
            details: Additional error details
        """
        import datetime
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": notification.error_type.value,
            "severity": notification.severity.value,
            "message": notification.message,
            "details": str(details)
        }
        
        self.error_log.append(log_entry)
        
        # Keep only last 100 errors to prevent memory issues
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]
        
        # Print to console for debugging
        print(f"[{log_entry['timestamp']}] {log_entry['severity'].upper()}: {log_entry['message']}")
        if details:
            print(f"  Details: {details}")
    
    def _notify_callbacks(self, notification: UserNotification):
        """
        Notify all registered callbacks about a new notification.
        
        Args:
            notification: The notification to send to callbacks
        """
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                print(f"Error in notification callback: {e}")
    
    def get_error_log(self) -> list:
        """
        Get the current error log.
        
        Returns:
            List of error log entries
        """
        return self.error_log.copy()
    
    def clear_error_log(self):
        """Clear the error log."""
        self.error_log.clear()


class LoadingIndicator:
    """Loading indicator component for async operations."""
    
    def __init__(self, parent_widget: tk.Widget, theme_manager: ThemeManager):
        """
        Initialize loading indicator.
        
        Args:
            parent_widget: Parent widget to show loading indicator in
            theme_manager: ThemeManager for themed styling
        """
        self.parent = parent_widget
        self.theme_manager = theme_manager
        self.loading_frame = None
        self.loading_label = None
        self.is_showing = False
        self.animation_job = None
        self.animation_state = 0
    
    def show(self, message: str = "Loading..."):
        """
        Show loading indicator with message.
        
        Args:
            message: Loading message to display
        """
        if self.is_showing:
            return
        
        self.is_showing = True
        colors = self.theme_manager.get_colors()
        
        # Create loading frame
        self.loading_frame = tk.Frame(
            self.parent,
            bg=colors["bg_secondary"],
            relief="solid",
            borderwidth=1,
            highlightbackground=colors["border_light"]
        )
        
        # Create loading label with animation
        self.loading_label = tk.Label(
            self.loading_frame,
            text=f"⏳ {message}",
            bg=colors["bg_secondary"],
            fg=colors["text_primary"],
            font=("Helvetica", 12)
        )
        self.loading_label.pack(padx=20, pady=15)
        
        # Position loading frame
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Start animation
        self._animate_loading()
    
    def hide(self):
        """Hide loading indicator."""
        if not self.is_showing:
            return
        
        self.is_showing = False
        
        # Cancel animation
        if self.animation_job:
            self.parent.after_cancel(self.animation_job)
            self.animation_job = None
        
        # Remove loading frame
        if self.loading_frame:
            self.loading_frame.destroy()
            self.loading_frame = None
            self.loading_label = None
    
    def update_message(self, message: str):
        """
        Update loading message.
        
        Args:
            message: New loading message
        """
        if self.is_showing and self.loading_label:
            animation_chars = ["⏳", "⌛"]
            char = animation_chars[self.animation_state % len(animation_chars)]
            self.loading_label.config(text=f"{char} {message}")
    
    def _animate_loading(self):
        """Animate the loading indicator."""
        if not self.is_showing or not self.loading_label:
            return
        
        animation_chars = ["⏳", "⌛"]
        char = animation_chars[self.animation_state % len(animation_chars)]
        
        current_text = self.loading_label.cget("text")
        if " " in current_text:
            message = current_text.split(" ", 1)[1]
            self.loading_label.config(text=f"{char} {message}")
        
        self.animation_state += 1
        self.animation_job = self.parent.after(500, self._animate_loading)