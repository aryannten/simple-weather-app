"""
User Notification System for Weather App

Provides in-app notifications for errors, warnings, and informational messages
with theme support and automatic dismissal options.
"""

import tkinter as tk
from typing import Optional, Callable, List
from error_handler import UserNotification, ErrorSeverity, ErrorType
from theme_manager import ThemeManager
from ui_components import ThemedFrame, ThemedLabel, ThemedButton


class NotificationBar(ThemedFrame):
    """Top-level notification bar for displaying user notifications."""
    
    def __init__(self, parent, theme_manager: ThemeManager, **kwargs):
        """
        Initialize notification bar.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, theme_manager, **kwargs)
        
        self.notifications = []
        self.current_notification = None
        self.auto_dismiss_job = None
        
        # Initially hide the notification bar
        self.pack_forget()
    
    def show_notification(self, notification: UserNotification):
        """
        Show a notification in the bar.
        
        Args:
            notification: UserNotification to display
        """
        # Clear any existing notification
        self.clear_current_notification()
        
        # Add to queue
        self.notifications.append(notification)
        
        # Show the notification
        self._display_notification(notification)
    
    def _display_notification(self, notification: UserNotification):
        """
        Display a specific notification.
        
        Args:
            notification: UserNotification to display
        """
        self.current_notification = notification
        
        # Clear existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Get colors based on severity
        colors = self.theme_manager.get_colors()
        
        if notification.severity == ErrorSeverity.ERROR:
            bg_color = colors["error"]
            text_color = "#ffffff"
        elif notification.severity == ErrorSeverity.WARNING:
            bg_color = colors["warning"]
            text_color = "#ffffff"
        elif notification.severity == ErrorSeverity.CRITICAL:
            bg_color = colors["error"]
            text_color = "#ffffff"
        else:  # INFO
            bg_color = colors["info"]
            text_color = "#ffffff"
        
        # Configure frame colors
        self.configure(
            bg=bg_color,
            highlightbackground=bg_color,
            highlightthickness=0
        )
        
        # Create content frame
        content_frame = tk.Frame(self, bg=bg_color)
        content_frame.pack(fill='both', expand=True, padx=10, pady=8)
        
        # Severity icon
        severity_icons = {
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.CRITICAL: "🚨",
            ErrorSeverity.INFO: "ℹ️"
        }
        
        icon_label = tk.Label(
            content_frame,
            text=severity_icons.get(notification.severity, "ℹ️"),
            bg=bg_color,
            fg=text_color,
            font=("Arial", 14)
        )
        icon_label.pack(side='left', padx=(0, 10))
        
        # Message label
        message_label = tk.Label(
            content_frame,
            text=notification.message,
            bg=bg_color,
            fg=text_color,
            font=("Helvetica", 11),
            wraplength=600,
            justify='left'
        )
        message_label.pack(side='left', fill='both', expand=True)
        
        # Dismiss button (if dismissible)
        if notification.dismissible:
            dismiss_btn = tk.Button(
                content_frame,
                text="✕",
                bg=bg_color,
                fg=text_color,
                font=("Arial", 12, "bold"),
                relief="flat",
                borderwidth=0,
                cursor="hand2",
                command=self.dismiss_current_notification
            )
            dismiss_btn.pack(side='right', padx=(10, 0))
            
            # Hover effects for dismiss button
            def on_enter(e):
                dismiss_btn.configure(bg=self._darken_color(bg_color))
            
            def on_leave(e):
                dismiss_btn.configure(bg=bg_color)
            
            dismiss_btn.bind("<Enter>", on_enter)
            dismiss_btn.bind("<Leave>", on_leave)
        
        # Show the notification bar
        self.pack(fill='x', pady=(0, 5))
        
        # Set up auto-dismiss if specified
        if notification.auto_dismiss_ms:
            self.auto_dismiss_job = self.after(
                notification.auto_dismiss_ms,
                self.dismiss_current_notification
            )
    
    def dismiss_current_notification(self):
        """Dismiss the currently displayed notification."""
        if self.current_notification:
            # Remove from queue if present
            if self.current_notification in self.notifications:
                self.notifications.remove(self.current_notification)
            
            self.current_notification = None
        
        # Cancel auto-dismiss job
        if self.auto_dismiss_job:
            self.after_cancel(self.auto_dismiss_job)
            self.auto_dismiss_job = None
        
        # Hide the notification bar
        self.pack_forget()
        
        # Show next notification if any
        if self.notifications:
            next_notification = self.notifications.pop(0)
            self._display_notification(next_notification)
    
    def clear_current_notification(self):
        """Clear the current notification without showing next."""
        if self.auto_dismiss_job:
            self.after_cancel(self.auto_dismiss_job)
            self.auto_dismiss_job = None
        
        self.current_notification = None
        self.pack_forget()
    
    def clear_all_notifications(self):
        """Clear all notifications including queued ones."""
        self.notifications.clear()
        self.clear_current_notification()
    
    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        """Darken a hex color by a factor."""
        if color.startswith('#'):
            color = color[1:]
        
        # Convert hex to RGB
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # Darken by factor
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color  # Return original if parsing fails


class ToastNotification:
    """Toast-style notification that appears temporarily over content."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        """
        Initialize toast notification system.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
        """
        self.parent = parent
        self.theme_manager = theme_manager
        self.toast_frame = None
        self.auto_dismiss_job = None
    
    def show_toast(self, notification: UserNotification, position: str = "bottom"):
        """
        Show a toast notification.
        
        Args:
            notification: UserNotification to display
            position: Position of toast ("top", "bottom", "center")
        """
        # Clear existing toast
        self.hide_toast()
        
        colors = self.theme_manager.get_colors()
        
        # Determine colors based on severity
        if notification.severity == ErrorSeverity.ERROR:
            bg_color = colors["error"]
            text_color = "#ffffff"
        elif notification.severity == ErrorSeverity.WARNING:
            bg_color = colors["warning"]
            text_color = "#ffffff"
        elif notification.severity == ErrorSeverity.CRITICAL:
            bg_color = colors["error"]
            text_color = "#ffffff"
        else:  # INFO
            bg_color = colors["success"]
            text_color = "#ffffff"
        
        # Create toast frame
        self.toast_frame = tk.Frame(
            self.parent,
            bg=bg_color,
            relief="solid",
            borderwidth=1,
            highlightbackground=colors["border_dark"]
        )
        
        # Content frame
        content_frame = tk.Frame(self.toast_frame, bg=bg_color)
        content_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Severity icon
        severity_icons = {
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.CRITICAL: "🚨",
            ErrorSeverity.INFO: "✅"
        }
        
        icon_label = tk.Label(
            content_frame,
            text=severity_icons.get(notification.severity, "ℹ️"),
            bg=bg_color,
            fg=text_color,
            font=("Arial", 12)
        )
        icon_label.pack(side='left', padx=(0, 8))
        
        # Message label
        message_label = tk.Label(
            content_frame,
            text=notification.message,
            bg=bg_color,
            fg=text_color,
            font=("Helvetica", 10),
            wraplength=300,
            justify='left'
        )
        message_label.pack(side='left', fill='both', expand=True)
        
        # Position the toast
        if position == "top":
            self.toast_frame.place(relx=0.5, y=10, anchor="n")
        elif position == "bottom":
            self.toast_frame.place(relx=0.5, rely=1.0, y=-10, anchor="s")
        else:  # center
            self.toast_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Auto-dismiss
        dismiss_time = notification.auto_dismiss_ms or 4000
        self.auto_dismiss_job = self.parent.after(dismiss_time, self.hide_toast)
        
        # Click to dismiss
        def dismiss_on_click(event):
            self.hide_toast()
        
        self.toast_frame.bind("<Button-1>", dismiss_on_click)
        content_frame.bind("<Button-1>", dismiss_on_click)
        icon_label.bind("<Button-1>", dismiss_on_click)
        message_label.bind("<Button-1>", dismiss_on_click)
    
    def hide_toast(self):
        """Hide the current toast notification."""
        if self.auto_dismiss_job:
            self.parent.after_cancel(self.auto_dismiss_job)
            self.auto_dismiss_job = None
        
        if self.toast_frame:
            self.toast_frame.destroy()
            self.toast_frame = None


class NotificationManager:
    """Central manager for all notification types."""
    
    def __init__(self, parent, theme_manager: ThemeManager):
        """
        Initialize notification manager.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
        """
        self.parent = parent
        self.theme_manager = theme_manager
        
        # Create notification bar
        self.notification_bar = NotificationBar(parent, theme_manager)
        
        # Create toast system
        self.toast_system = ToastNotification(parent, theme_manager)
        
        # Notification preferences
        self.use_toast_for_info = True
        self.use_bar_for_errors = True
    
    def show_notification(self, notification: UserNotification, force_type: Optional[str] = None):
        """
        Show a notification using appropriate display method.
        
        Args:
            notification: UserNotification to display
            force_type: Force specific display type ("bar", "toast", "dialog")
        """
        if force_type == "bar":
            self.notification_bar.show_notification(notification)
        elif force_type == "toast":
            self.toast_system.show_toast(notification)
        elif force_type == "dialog":
            self._show_dialog_notification(notification)
        else:
            # Auto-select based on severity and type
            if notification.severity in [ErrorSeverity.CRITICAL]:
                self._show_dialog_notification(notification)
            elif notification.severity in [ErrorSeverity.ERROR, ErrorSeverity.WARNING]:
                if self.use_bar_for_errors:
                    self.notification_bar.show_notification(notification)
                else:
                    self.toast_system.show_toast(notification)
            else:  # INFO
                if self.use_toast_for_info:
                    self.toast_system.show_toast(notification)
                else:
                    self.notification_bar.show_notification(notification)
    
    def _show_dialog_notification(self, notification: UserNotification):
        """
        Show notification as a dialog box.
        
        Args:
            notification: UserNotification to display
        """
        from tkinter import messagebox
        
        title_map = {
            ErrorSeverity.ERROR: "Error",
            ErrorSeverity.WARNING: "Warning",
            ErrorSeverity.CRITICAL: "Critical Error",
            ErrorSeverity.INFO: "Information"
        }
        
        title = title_map.get(notification.severity, "Notification")
        
        if notification.severity == ErrorSeverity.ERROR:
            messagebox.showerror(title, notification.message)
        elif notification.severity == ErrorSeverity.WARNING:
            messagebox.showwarning(title, notification.message)
        elif notification.severity == ErrorSeverity.CRITICAL:
            messagebox.showerror(title, notification.message)
        else:
            messagebox.showinfo(title, notification.message)
    
    def clear_all_notifications(self):
        """Clear all active notifications."""
        self.notification_bar.clear_all_notifications()
        self.toast_system.hide_toast()
    
    def set_notification_preferences(self, use_toast_for_info: bool = True, use_bar_for_errors: bool = True):
        """
        Set notification display preferences.
        
        Args:
            use_toast_for_info: Use toast notifications for info messages
            use_bar_for_errors: Use notification bar for errors
        """
        self.use_toast_for_info = use_toast_for_info
        self.use_bar_for_errors = use_bar_for_errors