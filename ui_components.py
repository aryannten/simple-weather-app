"""
Theme-aware UI Components for Weather App

Provides reusable UI components that automatically apply theme styling
and respond to theme changes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Any, Dict, List
from datetime import datetime
from theme_manager import ThemeManager
from config_manager import ConfigManager


class ThemedFrame(tk.Frame):
    """Frame widget that automatically applies theme styling."""
    
    def __init__(self, parent, theme_manager: ThemeManager, frame_type: str = "default", **kwargs):
        """
        Initialize themed frame.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            frame_type: Type of frame styling ('default', 'card', 'weather_card', 'forecast_card')
            **kwargs: Additional tkinter Frame arguments
        """
        self.theme_manager = theme_manager
        self.frame_type = frame_type
        
        # Remove theme-specific kwargs before passing to Frame
        theme_kwargs = kwargs.copy()
        
        super().__init__(parent, **kwargs)
        
        # Apply initial theme
        self.apply_theme()
        
        # Register for theme change notifications
        self.theme_manager.register_theme_change_callback(self._on_theme_change)
    
    def apply_theme(self):
        """Apply current theme to this frame."""
        colors = self.theme_manager.get_colors()
        
        if self.frame_type == "card":
            self.configure(
                bg=colors["bg_secondary"],
                highlightbackground=colors["border_light"],
                highlightthickness=1,
                relief="solid"
            )
        elif self.frame_type == "weather_card":
            self.configure(
                bg=colors["weather_card_bg"],
                highlightbackground=colors["weather_card_border"],
                highlightthickness=1,
                relief="solid"
            )
        elif self.frame_type == "forecast_card":
            self.configure(
                bg=colors["forecast_card_bg"],
                highlightbackground=colors["border_light"],
                highlightthickness=1,
                relief="solid"
            )
        else:  # default
            self.configure(
                bg=colors["bg_primary"],
                highlightbackground=colors["border_light"]
            )
    
    def _on_theme_change(self, old_theme: str, new_theme: str):
        """Handle theme change notification."""
        self.apply_theme()
    
    def destroy(self):
        """Clean up theme callback when widget is destroyed."""
        self.theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class ThemedLabel(tk.Label):
    """Label widget that automatically applies theme styling."""
    
    def __init__(self, parent, theme_manager: ThemeManager, label_type: str = "primary", **kwargs):
        """
        Initialize themed label.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            label_type: Type of label styling ('primary', 'secondary', 'muted', 'title', 'error', 'success')
            **kwargs: Additional tkinter Label arguments
        """
        self.theme_manager = theme_manager
        self.label_type = label_type
        
        super().__init__(parent, **kwargs)
        
        # Apply initial theme
        self.apply_theme()
        
        # Register for theme change notifications
        self.theme_manager.register_theme_change_callback(self._on_theme_change)
    
    def apply_theme(self):
        """Apply current theme to this label."""
        colors = self.theme_manager.get_colors()
        
        # Set background based on parent or default
        bg_color = colors["bg_secondary"]
        try:
            parent_bg = self.master.cget("bg")
            if parent_bg in colors.values():
                bg_color = parent_bg
        except:
            pass
        
        if self.label_type == "primary":
            self.configure(
                bg=bg_color,
                fg=colors["text_primary"]
            )
        elif self.label_type == "secondary":
            self.configure(
                bg=bg_color,
                fg=colors["text_secondary"]
            )
        elif self.label_type == "muted":
            self.configure(
                bg=bg_color,
                fg=colors["text_muted"]
            )
        elif self.label_type == "title":
            self.configure(
                bg=bg_color,
                fg=colors["text_primary"]
            )
        elif self.label_type == "error":
            self.configure(
                bg=bg_color,
                fg=colors["error"]
            )
        elif self.label_type == "success":
            self.configure(
                bg=bg_color,
                fg=colors["success"]
            )
        elif self.label_type == "warning":
            self.configure(
                bg=bg_color,
                fg=colors["warning"]
            )
        elif self.label_type == "info":
            self.configure(
                bg=bg_color,
                fg=colors["info"]
            )
    
    def _on_theme_change(self, old_theme: str, new_theme: str):
        """Handle theme change notification."""
        self.apply_theme()
    
    def destroy(self):
        """Clean up theme callback when widget is destroyed."""
        self.theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class ThemedButton(tk.Button):
    """Button widget that automatically applies theme styling with hover effects."""
    
    def __init__(self, parent, theme_manager: ThemeManager, button_type: str = "primary", **kwargs):
        """
        Initialize themed button.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            button_type: Type of button styling ('primary', 'secondary', 'success', 'warning', 'error')
            **kwargs: Additional tkinter Button arguments
        """
        self.theme_manager = theme_manager
        self.button_type = button_type
        
        super().__init__(parent, **kwargs)
        
        # Apply initial theme
        self.apply_theme()
        
        # Bind hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        # Register for theme change notifications
        self.theme_manager.register_theme_change_callback(self._on_theme_change)
    
    def apply_theme(self):
        """Apply current theme to this button."""
        colors = self.theme_manager.get_colors()
        
        if self.button_type == "primary":
            self.configure(
                bg=colors["accent"],
                fg="#ffffff",
                activebackground=colors["accent_hover"],
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                cursor="hand2"
            )
        elif self.button_type == "secondary":
            self.configure(
                bg=colors["bg_tertiary"],
                fg=colors["text_primary"],
                activebackground=colors["border_medium"],
                activeforeground=colors["text_primary"],
                relief="flat",
                borderwidth=1,
                highlightbackground=colors["border_medium"],
                cursor="hand2"
            )
        elif self.button_type == "success":
            self.configure(
                bg=colors["success"],
                fg="#ffffff",
                activebackground=self._darken_color(colors["success"]),
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                cursor="hand2"
            )
        elif self.button_type == "warning":
            self.configure(
                bg=colors["warning"],
                fg="#ffffff",
                activebackground=self._darken_color(colors["warning"]),
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                cursor="hand2"
            )
        elif self.button_type == "error":
            self.configure(
                bg=colors["error"],
                fg="#ffffff",
                activebackground=self._darken_color(colors["error"]),
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                cursor="hand2"
            )
    
    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        """Darken a hex color by a factor."""
        # Simple color darkening - remove # and convert to int
        if color.startswith('#'):
            color = color[1:]
        
        # Convert hex to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Darken by factor
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _on_enter(self, event):
        """Handle mouse enter (hover)."""
        colors = self.theme_manager.get_colors()
        
        if self.button_type == "primary":
            self.configure(bg=colors["accent_hover"])
        elif self.button_type == "secondary":
            self.configure(bg=colors["border_medium"])
        elif self.button_type in ["success", "warning", "error"]:
            current_bg = self.cget("bg")
            self.configure(bg=self._darken_color(current_bg, 0.9))
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.apply_theme()  # Reset to normal colors
    
    def _on_press(self, event):
        """Handle button press."""
        colors = self.theme_manager.get_colors()
        
        if self.button_type == "primary":
            self.configure(bg=colors["accent_pressed"])
        elif self.button_type == "secondary":
            self.configure(bg=colors["border_dark"])
        elif self.button_type in ["success", "warning", "error"]:
            current_bg = self.cget("bg")
            self.configure(bg=self._darken_color(current_bg, 0.7))
    
    def _on_release(self, event):
        """Handle button release."""
        # Check if mouse is still over button
        x, y = event.x, event.y
        if 0 <= x <= self.winfo_width() and 0 <= y <= self.winfo_height():
            self._on_enter(event)  # Apply hover state
        else:
            self.apply_theme()  # Reset to normal
    
    def _on_theme_change(self, old_theme: str, new_theme: str):
        """Handle theme change notification."""
        self.apply_theme()
    
    def destroy(self):
        """Clean up theme callback when widget is destroyed."""
        self.theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class ThemedEntry(tk.Entry):
    """Entry widget that automatically applies theme styling."""
    
    def __init__(self, parent, theme_manager: ThemeManager, **kwargs):
        """
        Initialize themed entry.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            **kwargs: Additional tkinter Entry arguments
        """
        self.theme_manager = theme_manager
        
        super().__init__(parent, **kwargs)
        
        # Apply initial theme
        self.apply_theme()
        
        # Register for theme change notifications
        self.theme_manager.register_theme_change_callback(self._on_theme_change)
    
    def apply_theme(self):
        """Apply current theme to this entry."""
        colors = self.theme_manager.get_colors()
        
        self.configure(
            bg=colors["bg_tertiary"],
            fg=colors["text_primary"],
            insertbackground=colors["text_primary"],
            selectbackground=colors["accent"],
            selectforeground="#ffffff" if self.theme_manager.get_current_theme() == "light" else colors["text_primary"],
            highlightbackground=colors["border_medium"],
            highlightcolor=colors["accent"],
            relief="solid",
            borderwidth=1
        )
    
    def _on_theme_change(self, old_theme: str, new_theme: str):
        """Handle theme change notification."""
        self.apply_theme()
    
    def destroy(self):
        """Clean up theme callback when widget is destroyed."""
        self.theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class ThemeToggleButton(ThemedButton):
    """Special button for toggling between light and dark themes."""
    
    def __init__(self, parent, theme_manager: ThemeManager, **kwargs):
        """
        Initialize theme toggle button.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            **kwargs: Additional tkinter Button arguments
        """
        # Store theme manager first
        self.theme_manager = theme_manager
        
        # Set default command to toggle theme
        if 'command' not in kwargs:
            kwargs['command'] = self._toggle_theme
        
        # Set default text based on current theme
        if 'text' not in kwargs:
            kwargs['text'] = self._get_toggle_text()
        
        super().__init__(parent, theme_manager, button_type="secondary", **kwargs)
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme_manager.toggle_theme()
        self.configure(text=self._get_toggle_text())
    
    def _get_toggle_text(self) -> str:
        """Get appropriate text for current theme."""
        current_theme = self.theme_manager.get_current_theme()
        if current_theme == "light":
            return "🌙"  # Moon icon for switching to dark
        else:
            return "☀️"  # Sun icon for switching to light
    
    def _on_theme_change(self, old_theme: str, new_theme: str):
        """Handle theme change notification."""
        super()._on_theme_change(old_theme, new_theme)
        self.configure(text=self._get_toggle_text())


class ThemedScrollableFrame(ThemedFrame):
    """Scrollable frame that maintains theme styling."""
    
    def __init__(self, parent, theme_manager: ThemeManager, **kwargs):
        """
        Initialize themed scrollable frame.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            **kwargs: Additional arguments
        """
        super().__init__(parent, theme_manager, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ThemedFrame(self.canvas, theme_manager)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Apply theme to canvas
        self.apply_canvas_theme()
    
    def apply_canvas_theme(self):
        """Apply theme to canvas."""
        colors = self.theme_manager.get_colors()
        self.canvas.configure(bg=colors["bg_primary"])
    
    def apply_theme(self):
        """Apply theme to frame and canvas."""
        super().apply_theme()
        if hasattr(self, 'canvas'):
            self.apply_canvas_theme()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# Utility functions for creating themed widgets

def create_themed_separator(parent, theme_manager: ThemeManager, orient: str = "horizontal") -> ttk.Separator:
    """
    Create a themed separator.
    
    Args:
        parent: Parent widget
        theme_manager: ThemeManager instance
        orient: Orientation ('horizontal' or 'vertical')
        
    Returns:
        Configured ttk.Separator
    """
    separator = ttk.Separator(parent, orient=orient)
    
    # Configure separator style based on theme
    colors = theme_manager.get_colors()
    style = ttk.Style()
    
    if orient == "horizontal":
        style.configure("Themed.TSeparator", background=colors["border_light"])
    else:
        style.configure("Themed.TSeparator", background=colors["border_light"])
    
    separator.configure(style="Themed.TSeparator")
    return separator


class FavoritesList(ThemedFrame):
    """Scrollable list component for displaying favorite cities."""
    
    def __init__(self, parent, theme_manager: ThemeManager, favorites_manager, on_city_click: Optional[Callable] = None, **kwargs):
        """
        Initialize favorites list.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            favorites_manager: FavoritesManager instance
            on_city_click: Callback function when city is clicked (city_name, country_code)
            **kwargs: Additional arguments
        """
        super().__init__(parent, theme_manager, **kwargs)
        
        self.favorites_manager = favorites_manager
        self.on_city_click = on_city_click
        self.favorite_buttons = []
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ThemedFrame(self.canvas, theme_manager)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Apply theme to canvas
        self._apply_canvas_theme()
        
        # Create header
        self.header_frame = ThemedFrame(self.scrollable_frame, theme_manager)
        self.header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        self.title_label = ThemedLabel(
            self.header_frame,
            theme_manager,
            label_type="title",
            text="Favorite Cities",
            font=("Helvetica", 14, "bold")
        )
        self.title_label.pack(side='left')
        
        # Create content frame for favorites
        self.content_frame = ThemedFrame(self.scrollable_frame, theme_manager)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create empty state message
        self.empty_state_label = ThemedLabel(
            self.content_frame,
            theme_manager,
            label_type="muted",
            text="No favorite cities yet.\nClick the ⭐ button to add cities to your favorites!",
            font=("Helvetica", 11),
            justify='center'
        )
        
        # Load initial favorites
        self.refresh_favorites()
    
    def _apply_canvas_theme(self):
        """Apply theme to canvas."""
        colors = self.theme_manager.get_colors()
        self.canvas.configure(bg=colors["bg_primary"])
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def apply_theme(self):
        """Apply theme to frame and canvas."""
        super().apply_theme()
        if hasattr(self, 'canvas'):
            self._apply_canvas_theme()
    
    def refresh_favorites(self):
        """Refresh the favorites list display."""
        # Clear existing buttons
        for button in self.favorite_buttons:
            button.destroy()
        self.favorite_buttons.clear()
        
        # Get current favorites
        favorites = self.favorites_manager.get_favorites()
        
        if not favorites:
            # Show empty state
            self.empty_state_label.pack(expand=True, pady=20)
        else:
            # Hide empty state
            self.empty_state_label.pack_forget()
            
            # Create buttons for each favorite
            for favorite in favorites:
                self._create_favorite_button(favorite)
    
    def _create_favorite_button(self, favorite: Dict[str, Any]):
        """Create a button for a favorite city."""
        city_name = favorite.get("name", "")
        country_code = favorite.get("country", "")
        
        # Create container frame for the favorite item
        item_frame = ThemedFrame(self.content_frame, self.theme_manager, frame_type="card")
        item_frame.pack(fill='x', pady=2)
        
        # Create city button
        display_text = f"{city_name}, {country_code}" if country_code else city_name
        
        city_button = ThemedButton(
            item_frame,
            self.theme_manager,
            button_type="secondary",
            text=display_text,
            font=("Helvetica", 11),
            anchor='w',
            command=lambda c=city_name, cc=country_code: self._on_city_selected(c, cc)
        )
        city_button.pack(side='left', fill='x', expand=True, padx=(5, 2), pady=5)
        
        # Create remove button
        remove_button = ThemedButton(
            item_frame,
            self.theme_manager,
            button_type="error",
            text="✕",
            font=("Arial", 10),
            width=3,
            command=lambda c=city_name, cc=country_code: self._on_remove_favorite(c, cc)
        )
        remove_button.pack(side='right', padx=(2, 5), pady=5)
        
        # Store references
        self.favorite_buttons.extend([item_frame, city_button, remove_button])
    
    def _on_city_selected(self, city_name: str, country_code: str):
        """Handle city selection."""
        if self.on_city_click:
            self.on_city_click(city_name, country_code)
    
    def _on_remove_favorite(self, city_name: str, country_code: str):
        """Handle favorite removal."""
        success = self.favorites_manager.remove_favorite(city_name, country_code)
        if success:
            self.refresh_favorites()
    
    def add_favorite(self, city_name: str, country_code: str = ""):
        """Add a favorite and refresh the display."""
        success = self.favorites_manager.add_favorite(city_name, country_code)
        if success:
            self.refresh_favorites()
        return success


class FavoriteStarButton(ThemedButton):
    """Star button that toggles favorite status for current city."""
    
    def __init__(self, parent, theme_manager: ThemeManager, favorites_manager, **kwargs):
        """
        Initialize favorite star button.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            favorites_manager: FavoritesManager instance
            **kwargs: Additional tkinter Button arguments
        """
        self.favorites_manager = favorites_manager
        self.current_city = ""
        self.current_country = ""
        self._on_favorite_changed = None
        
        # Set default properties
        kwargs.setdefault('button_type', 'secondary')
        kwargs.setdefault('text', '☆')
        kwargs.setdefault('font', ('Arial', 16))
        kwargs.setdefault('width', 3)
        kwargs.setdefault('command', self._toggle_favorite)
        
        super().__init__(parent, theme_manager, **kwargs)
    
    def set_city(self, city_name: str, country_code: str = ""):
        """
        Set the current city for the star button.
        
        Args:
            city_name: Name of the current city
            country_code: Country code of the current city
        """
        self.current_city = city_name
        self.current_country = country_code
        self._update_star_state()
    
    def set_favorite_changed_callback(self, callback: Callable[[str, str, bool], None]):
        """
        Set callback for when favorite status changes.
        
        Args:
            callback: Function to call with (city_name, country_code, is_favorite)
        """
        self._on_favorite_changed = callback
    
    def _toggle_favorite(self):
        """Toggle favorite status for current city."""
        if not self.current_city:
            return
        
        is_currently_favorite = self.favorites_manager.is_favorite(self.current_city, self.current_country)
        
        if is_currently_favorite:
            success = self.favorites_manager.remove_favorite(self.current_city, self.current_country)
        else:
            success = self.favorites_manager.add_favorite(self.current_city, self.current_country)
        
        if success:
            self._update_star_state()
            
            # Notify callback if set
            if self._on_favorite_changed:
                new_state = not is_currently_favorite
                self._on_favorite_changed(self.current_city, self.current_country, new_state)
    
    def _update_star_state(self):
        """Update star button appearance based on favorite status."""
        if not self.current_city:
            self.configure(text='☆', state='disabled')
            return
        
        is_favorite = self.favorites_manager.is_favorite(self.current_city, self.current_country)
        
        if is_favorite:
            self.configure(text='⭐', state='normal')
        else:
            self.configure(text='☆', state='normal')


class SettingsDialog:
    """Settings dialog window for API key and preference management."""
    
    def __init__(self, parent, config_manager: ConfigManager, theme_manager: ThemeManager):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent window
            config_manager: ConfigManager instance
            theme_manager: ThemeManager instance
        """
        self.parent = parent
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.dialog = None
        self.validation_labels = {}
        self.entry_widgets = {}
        
    def show(self):
        """Show the settings dialog."""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            self.dialog.focus()
            return
            
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Apply theme to dialog
        colors = self.theme_manager.get_colors()
        self.dialog.configure(bg=colors["bg_primary"])
        
        # Center dialog on parent
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        self._create_widgets()
        self._load_current_settings()
        
        # Register for theme changes
        self.theme_manager.register_theme_change_callback(self._on_theme_change)
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """Create all dialog widgets."""
        # Main container
        self.main_frame = ThemedFrame(self.dialog, self.theme_manager)
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ThemedLabel(
            self.main_frame,
            self.theme_manager,
            label_type="title",
            text="Application Settings",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create scrollable frame for settings
        self.scroll_frame = ThemedScrollableFrame(self.main_frame, self.theme_manager)
        self.scroll_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Settings container
        settings_frame = self.scroll_frame.scrollable_frame
        
        # API Key Section
        self._create_api_key_section(settings_frame)
        
        # Theme Section
        self._create_theme_section(settings_frame)
        
        # Units Section
        self._create_units_section(settings_frame)
        
        # Auto Refresh Section
        self._create_auto_refresh_section(settings_frame)
        
        # Button frame
        button_frame = ThemedFrame(self.main_frame, self.theme_manager)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Buttons
        self.save_btn = ThemedButton(
            button_frame,
            self.theme_manager,
            button_type="primary",
            text="Save Settings",
            font=("Helvetica", 12, "bold"),
            command=self._save_settings,
            padx=20,
            pady=8
        )
        self.save_btn.pack(side='right', padx=(10, 0))
        
        self.cancel_btn = ThemedButton(
            button_frame,
            self.theme_manager,
            button_type="secondary",
            text="Cancel",
            font=("Helvetica", 12),
            command=self._on_close,
            padx=20,
            pady=8
        )
        self.cancel_btn.pack(side='right')
        
        self.reset_btn = ThemedButton(
            button_frame,
            self.theme_manager,
            button_type="warning",
            text="Reset to Defaults",
            font=("Helvetica", 12),
            command=self._reset_to_defaults,
            padx=20,
            pady=8
        )
        self.reset_btn.pack(side='left')
    
    def _create_api_key_section(self, parent):
        """Create API key configuration section."""
        section_frame = ThemedFrame(parent, self.theme_manager, frame_type="card")
        section_frame.pack(fill='x', pady=(0, 15), padx=5)
        section_frame.configure(padx=15, pady=15)
        
        # Section title
        title_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="title",
            text="🔑 API Configuration",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # API Key field
        api_key_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="primary",
            text="OpenWeather API Key:",
            font=("Helvetica", 11)
        )
        api_key_label.pack(anchor='w', pady=(0, 5))
        
        self.api_key_entry = ThemedEntry(
            section_frame,
            self.theme_manager,
            font=("Helvetica", 11),
            show="*",
            width=50
        )
        self.api_key_entry.pack(fill='x', pady=(0, 5))
        self.api_key_entry.bind('<KeyRelease>', lambda e: self._validate_field('api_key'))
        self.entry_widgets['api_key'] = self.api_key_entry
        
        # Show/Hide API key button
        show_hide_frame = ThemedFrame(section_frame, self.theme_manager)
        show_hide_frame.pack(fill='x', pady=(0, 5))
        
        self.show_api_key_var = tk.BooleanVar()
        self.show_api_key_btn = ThemedButton(
            show_hide_frame,
            self.theme_manager,
            button_type="secondary",
            text="👁️ Show",
            font=("Helvetica", 9),
            command=self._toggle_api_key_visibility,
            width=8
        )
        self.show_api_key_btn.pack(side='left')
        
        # API key validation label
        self.validation_labels['api_key'] = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="error",
            text="",
            font=("Helvetica", 10)
        )
        self.validation_labels['api_key'].pack(anchor='w', pady=(0, 5))
        
        # Help text
        help_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="muted",
            text="Get your free API key from openweathermap.org/api",
            font=("Helvetica", 9)
        )
        help_label.pack(anchor='w')
    
    def _create_theme_section(self, parent):
        """Create theme configuration section."""
        section_frame = ThemedFrame(parent, self.theme_manager, frame_type="card")
        section_frame.pack(fill='x', pady=(0, 15), padx=5)
        section_frame.configure(padx=15, pady=15)
        
        # Section title
        title_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="title",
            text="🎨 Appearance",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Theme selection
        theme_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="primary",
            text="Theme:",
            font=("Helvetica", 11)
        )
        theme_label.pack(anchor='w', pady=(0, 5))
        
        self.theme_var = tk.StringVar()
        theme_frame = ThemedFrame(section_frame, self.theme_manager)
        theme_frame.pack(fill='x', pady=(0, 5))
        
        # Light theme radio button
        self.light_radio = tk.Radiobutton(
            theme_frame,
            text="☀️ Light Theme",
            variable=self.theme_var,
            value="light",
            font=("Helvetica", 11),
            command=self._on_theme_preview
        )
        self.light_radio.pack(side='left', padx=(0, 20))
        
        # Dark theme radio button
        self.dark_radio = tk.Radiobutton(
            theme_frame,
            text="🌙 Dark Theme",
            variable=self.theme_var,
            value="dark",
            font=("Helvetica", 11),
            command=self._on_theme_preview
        )
        self.dark_radio.pack(side='left')
        
        # Apply theme to radio buttons
        self._apply_theme_to_radio_buttons()
    
    def _create_units_section(self, parent):
        """Create units configuration section."""
        section_frame = ThemedFrame(parent, self.theme_manager, frame_type="card")
        section_frame.pack(fill='x', pady=(0, 15), padx=5)
        section_frame.configure(padx=15, pady=15)
        
        # Section title
        title_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="title",
            text="🌡️ Units",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Units selection
        units_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="primary",
            text="Temperature Units:",
            font=("Helvetica", 11)
        )
        units_label.pack(anchor='w', pady=(0, 5))
        
        self.units_var = tk.StringVar()
        units_frame = ThemedFrame(section_frame, self.theme_manager)
        units_frame.pack(fill='x', pady=(0, 5))
        
        # Metric radio button
        self.metric_radio = tk.Radiobutton(
            units_frame,
            text="🌡️ Celsius (°C)",
            variable=self.units_var,
            value="metric",
            font=("Helvetica", 11)
        )
        self.metric_radio.pack(anchor='w', pady=2)
        
        # Imperial radio button
        self.imperial_radio = tk.Radiobutton(
            units_frame,
            text="🌡️ Fahrenheit (°F)",
            variable=self.units_var,
            value="imperial",
            font=("Helvetica", 11)
        )
        self.imperial_radio.pack(anchor='w', pady=2)
        
        # Apply theme to radio buttons
        self._apply_theme_to_units_radio_buttons()
    
    def _create_auto_refresh_section(self, parent):
        """Create auto refresh configuration section."""
        section_frame = ThemedFrame(parent, self.theme_manager, frame_type="card")
        section_frame.pack(fill='x', pady=(0, 15), padx=5)
        section_frame.configure(padx=15, pady=15)
        
        # Section title
        title_label = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="title",
            text="🔄 Auto Refresh",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Auto refresh checkbox
        self.auto_refresh_var = tk.BooleanVar()
        self.auto_refresh_check = tk.Checkbutton(
            section_frame,
            text="Enable automatic weather refresh",
            variable=self.auto_refresh_var,
            font=("Helvetica", 11),
            command=self._on_auto_refresh_toggle
        )
        self.auto_refresh_check.pack(anchor='w', pady=(0, 10))
        
        # Refresh interval
        interval_frame = ThemedFrame(section_frame, self.theme_manager)
        interval_frame.pack(fill='x', pady=(0, 5))
        
        interval_label = ThemedLabel(
            interval_frame,
            self.theme_manager,
            label_type="primary",
            text="Refresh interval (seconds):",
            font=("Helvetica", 11)
        )
        interval_label.pack(side='left')
        
        self.refresh_interval_entry = ThemedEntry(
            interval_frame,
            self.theme_manager,
            font=("Helvetica", 11),
            width=10
        )
        self.refresh_interval_entry.pack(side='right')
        self.refresh_interval_entry.bind('<KeyRelease>', lambda e: self._validate_field('refresh_interval'))
        self.entry_widgets['refresh_interval'] = self.refresh_interval_entry
        
        # Validation label for refresh interval
        self.validation_labels['refresh_interval'] = ThemedLabel(
            section_frame,
            self.theme_manager,
            label_type="error",
            text="",
            font=("Helvetica", 10)
        )
        self.validation_labels['refresh_interval'].pack(anchor='w')
        
        # Apply theme to checkbox
        self._apply_theme_to_checkbox()
    
    def _apply_theme_to_radio_buttons(self):
        """Apply theme to radio buttons."""
        colors = self.theme_manager.get_colors()
        
        for radio in [self.light_radio, self.dark_radio]:
            radio.configure(
                bg=colors["bg_secondary"],
                fg=colors["text_primary"],
                activebackground=colors["bg_tertiary"],
                activeforeground=colors["text_primary"],
                selectcolor=colors["bg_tertiary"],
                highlightbackground=colors["border_light"]
            )
    
    def _apply_theme_to_units_radio_buttons(self):
        """Apply theme to units radio buttons."""
        colors = self.theme_manager.get_colors()
        
        for radio in [self.metric_radio, self.imperial_radio]:
            radio.configure(
                bg=colors["bg_secondary"],
                fg=colors["text_primary"],
                activebackground=colors["bg_tertiary"],
                activeforeground=colors["text_primary"],
                selectcolor=colors["bg_tertiary"],
                highlightbackground=colors["border_light"]
            )
    
    def _apply_theme_to_checkbox(self):
        """Apply theme to checkbox."""
        colors = self.theme_manager.get_colors()
        
        self.auto_refresh_check.configure(
            bg=colors["bg_secondary"],
            fg=colors["text_primary"],
            activebackground=colors["bg_tertiary"],
            activeforeground=colors["text_primary"],
            selectcolor=colors["bg_tertiary"],
            highlightbackground=colors["border_light"]
        )
    
    def _toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.show_api_key_var.get():
            self.api_key_entry.configure(show="")
            self.show_api_key_btn.configure(text="🙈 Hide")
            self.show_api_key_var.set(False)
        else:
            self.api_key_entry.configure(show="*")
            self.show_api_key_btn.configure(text="👁️ Show")
            self.show_api_key_var.set(True)
    
    def _on_theme_preview(self):
        """Handle theme preview selection."""
        # Optionally implement live preview
        pass
    
    def _on_auto_refresh_toggle(self):
        """Handle auto refresh toggle."""
        if self.auto_refresh_var.get():
            self.refresh_interval_entry.configure(state='normal')
        else:
            self.refresh_interval_entry.configure(state='disabled')
    
    def _validate_field(self, field_name: str) -> bool:
        """
        Validate a specific field and show error message if invalid.
        
        Args:
            field_name: Name of the field to validate
            
        Returns:
            True if valid, False otherwise
        """
        validation_label = self.validation_labels.get(field_name)
        if not validation_label:
            return True
        
        # Clear previous error
        validation_label.configure(text="")
        
        if field_name == 'api_key':
            api_key = self.api_key_entry.get().strip()
            if not api_key:
                validation_label.configure(text="⚠️ API key is required")
                return False
            elif len(api_key) < 10:
                validation_label.configure(text="⚠️ API key appears to be too short")
                return False
            else:
                validation_label.configure(text="✅ API key format looks valid", fg=self.theme_manager.get_color("success"))
                return True
        
        elif field_name == 'refresh_interval':
            try:
                interval = int(self.refresh_interval_entry.get())
                if interval < 60:
                    validation_label.configure(text="⚠️ Minimum interval is 60 seconds")
                    return False
                elif interval > 3600:
                    validation_label.configure(text="⚠️ Maximum interval is 3600 seconds (1 hour)")
                    return False
                else:
                    validation_label.configure(text="✅ Valid interval", fg=self.theme_manager.get_color("success"))
                    return True
            except ValueError:
                validation_label.configure(text="⚠️ Please enter a valid number")
                return False
        
        return True
    
    def _validate_all_fields(self) -> bool:
        """
        Validate all fields in the form.
        
        Returns:
            True if all fields are valid, False otherwise
        """
        all_valid = True
        
        for field_name in self.entry_widgets.keys():
            if not self._validate_field(field_name):
                all_valid = False
        
        return all_valid
    
    def _load_current_settings(self):
        """Load current settings into the form."""
        # Load API key
        api_key = self.config_manager.get_setting('api_key', '')
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, api_key)
        
        # Load theme
        current_theme = self.config_manager.get_setting('theme', 'light')
        self.theme_var.set(current_theme)
        
        # Load units
        current_units = self.config_manager.get_setting('units', 'metric')
        self.units_var.set(current_units)
        
        # Load auto refresh settings
        auto_refresh = self.config_manager.get_setting('auto_refresh', False)
        self.auto_refresh_var.set(auto_refresh)
        
        refresh_interval = self.config_manager.get_setting('refresh_interval', 300)
        self.refresh_interval_entry.delete(0, tk.END)
        self.refresh_interval_entry.insert(0, str(refresh_interval))
        
        # Update auto refresh state
        self._on_auto_refresh_toggle()
        
        # Validate loaded fields
        for field_name in self.entry_widgets.keys():
            self._validate_field(field_name)
    
    def _save_settings(self):
        """Save settings and close dialog."""
        if not self._validate_all_fields():
            # Show error message
            tk.messagebox.showerror(
                "Validation Error",
                "Please fix the validation errors before saving.",
                parent=self.dialog
            )
            return
        
        try:
            # Collect settings
            settings = {
                'api_key': self.api_key_entry.get().strip(),
                'theme': self.theme_var.get(),
                'units': self.units_var.get(),
                'auto_refresh': self.auto_refresh_var.get(),
                'refresh_interval': int(self.refresh_interval_entry.get())
            }
            
            # Save settings
            success = self.config_manager.update_settings(settings)
            
            if success:
                # Apply theme change if needed
                if settings['theme'] != self.theme_manager.get_current_theme():
                    self.theme_manager.set_theme(settings['theme'])
                
                # Show success message
                tk.messagebox.showinfo(
                    "Settings Saved",
                    "Settings have been saved successfully!",
                    parent=self.dialog
                )
                
                self._on_close()
            else:
                tk.messagebox.showerror(
                    "Save Error",
                    "Failed to save settings. Please try again.",
                    parent=self.dialog
                )
                
        except Exception as e:
            tk.messagebox.showerror(
                "Error",
                f"An error occurred while saving settings: {str(e)}",
                parent=self.dialog
            )
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        result = tk.messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults? This cannot be undone.",
            parent=self.dialog
        )
        
        if result:
            try:
                # Reset to defaults
                self.config_manager.reset_to_defaults()
                
                # Reload form with defaults
                self._load_current_settings()
                
                # Apply default theme
                self.theme_manager.set_theme("light")
                
                tk.messagebox.showinfo(
                    "Settings Reset",
                    "All settings have been reset to defaults.",
                    parent=self.dialog
                )
                
            except Exception as e:
                tk.messagebox.showerror(
                    "Reset Error",
                    f"An error occurred while resetting settings: {str(e)}",
                    parent=self.dialog
                )
    
    def _on_theme_change(self, old_theme: str, new_theme: str):
        """Handle theme change notification."""
        if self.dialog and self.dialog.winfo_exists():
            # Update dialog background
            colors = self.theme_manager.get_colors()
            self.dialog.configure(bg=colors["bg_primary"])
            
            # Update radio button themes
            self._apply_theme_to_radio_buttons()
            self._apply_theme_to_units_radio_buttons()
            self._apply_theme_to_checkbox()
    
    def _on_close(self):
        """Handle dialog close."""
        if self.dialog:
            # Unregister theme callback
            self.theme_manager.unregister_theme_change_callback(self._on_theme_change)
            
            # Destroy dialog
            self.dialog.destroy()
            self.dialog = None


class ForecastCard(ThemedFrame):
    """Individual forecast card component for daily weather display."""
    
    def __init__(self, parent, theme_manager: ThemeManager, **kwargs):
        """
        Initialize forecast card.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            **kwargs: Additional arguments
        """
        super().__init__(parent, theme_manager, frame_type="forecast_card", **kwargs)
        
        # Configure card styling - make more compact
        self.configure(relief="solid", borderwidth=1, padx=5, pady=5, width=95, height=150)
        
        # Day label - more compact
        self.day_label = ThemedLabel(
            self,
            theme_manager,
            label_type="primary",
            text="",
            font=("Helvetica", 10, "bold"),
            anchor='center'
        )
        self.day_label.pack(fill='x', pady=(0, 2))
        
        # Date label - smaller
        self.date_label = ThemedLabel(
            self,
            theme_manager,
            label_type="secondary",
            text="",
            font=("Helvetica", 8),
            anchor='center'
        )
        self.date_label.pack(fill='x', pady=(0, 4))
        
        # Weather icon - smaller
        self.icon_label = ThemedLabel(
            self,
            theme_manager,
            label_type="primary",
            text="",
            font=("Arial", 20),
            anchor='center'
        )
        self.icon_label.pack(fill='x', pady=(0, 3))
        
        # Temperature range - compact
        self.temp_label = ThemedLabel(
            self,
            theme_manager,
            label_type="primary",
            text="",
            font=("Helvetica", 9, "bold"),
            anchor='center'
        )
        self.temp_label.pack(fill='x', pady=(0, 2))
        
        # Weather description - smaller and wrapped
        self.desc_label = ThemedLabel(
            self,
            theme_manager,
            label_type="secondary",
            text="",
            font=("Helvetica", 7),
            anchor='center',
            wraplength=90,
            justify='center'
        )
        self.desc_label.pack(fill='x', pady=(0, 2))
        
        # Additional info (humidity, wind) - very compact
        self.info_label = ThemedLabel(
            self,
            theme_manager,
            label_type="muted",
            text="",
            font=("Helvetica", 7),
            anchor='center'
        )
        self.info_label.pack(fill='x')
    
    def update_forecast_data(self, forecast_data: Dict[str, Any], weather_icons: Dict[str, str]):
        """
        Update the forecast card with weather data.
        
        Args:
            forecast_data: Dictionary containing forecast information
            weather_icons: Dictionary mapping icon codes to emoji
        """
        try:
            # Update day and date
            self.day_label.config(text=forecast_data.get('day_name', ''))
            self.date_label.config(text=forecast_data.get('date_str', ''))
            
            # Update weather icon
            icon_code = forecast_data.get('icon_code', '01d')
            weather_icon = weather_icons.get(icon_code, '☁️')
            self.icon_label.config(text=weather_icon)
            
            # Update temperature range
            high_temp = forecast_data.get('high_temp', 0)
            low_temp = forecast_data.get('low_temp', 0)
            self.temp_label.config(text=f"{int(high_temp)}° / {int(low_temp)}°")
            
            # Update description - truncate if too long
            description = forecast_data.get('description', '').title()
            if len(description) > 12:
                description = description[:12] + "..."
            self.desc_label.config(text=description)
            
            # Update additional info - more compact
            humidity = forecast_data.get('humidity', 0)
            wind_speed = forecast_data.get('wind_speed', 0)
            self.info_label.config(text=f"💧{humidity}% 💨{wind_speed:.0f}")
            
        except Exception as e:
            print(f"Error updating forecast card: {e}")
            # Set error state
            self.day_label.config(text="Error")
            self.date_label.config(text="")
            self.icon_label.config(text="❌")
            self.temp_label.config(text="--° / --°")
            self.desc_label.config(text="Data unavailable")
            self.info_label.config(text="")


class ForecastContainer(ThemedFrame):
    """Scrollable container for displaying multiple forecast cards."""
    
    def __init__(self, parent, theme_manager: ThemeManager, **kwargs):
        """
        Initialize forecast container.
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance
            **kwargs: Additional arguments
        """
        super().__init__(parent, theme_manager, **kwargs)
        
        # Container title
        self.title_frame = ThemedFrame(self, theme_manager)
        self.title_frame.pack(fill='x', pady=(0, 10))
        
        self.title_label = ThemedLabel(
            self.title_frame,
            theme_manager,
            label_type="title",
            text="5-Day Forecast",
            font=("Helvetica", 16, "bold")
        )
        self.title_label.pack(side='left')
        
        # Add scroll hint label
        self.scroll_hint_label = ThemedLabel(
            self.title_frame,
            theme_manager,
            label_type="muted",
            text="← → Scroll",
            font=("Helvetica", 8)
        )
        self.scroll_hint_label.pack(side='right')
        
        # Create scrollable frame for forecast cards - reduced height
        self.canvas = tk.Canvas(self, highlightthickness=0, height=170)
        self.scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ThemedFrame(self.canvas, theme_manager)
        
        # Configure horizontal scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self._on_scroll)
        
        # Create container for canvas with scroll indicators
        self.canvas_container = ThemedFrame(self, theme_manager)
        self.canvas_container.pack(side="top", fill="both", expand=True)
        
        # Left scroll indicator
        self.left_indicator = ThemedLabel(
            self.canvas_container,
            theme_manager,
            label_type="muted",
            text="◀",
            font=("Arial", 12),
            cursor="hand2"
        )
        self.left_indicator.bind("<Button-1>", lambda e: self._smooth_scroll(-3))
        
        # Right scroll indicator  
        self.right_indicator = ThemedLabel(
            self.canvas_container,
            theme_manager,
            label_type="muted",
            text="▶",
            font=("Arial", 12),
            cursor="hand2"
        )
        self.right_indicator.bind("<Button-1>", lambda e: self._smooth_scroll(3))
        
        # Pack elements
        self.left_indicator.pack(side="left", padx=5)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.right_indicator.pack(side="right", padx=5)
        self.scrollbar.pack(side="bottom", fill="x")
        
        # Bind mousewheel for horizontal scrolling to canvas and all child widgets
        self._bind_mousewheel_recursive(self.canvas)
        self._bind_mousewheel_recursive(self.scrollable_frame)
        
        # Bind keyboard navigation
        self.canvas.bind("<Left>", self._on_key_left)
        self.canvas.bind("<Right>", self._on_key_right)
        self.canvas.bind("<Home>", self._on_key_home)
        self.canvas.bind("<End>", self._on_key_end)
        
        # Make canvas focusable for keyboard navigation
        self.canvas.configure(takefocus=True)
        
        # Add drag scrolling support
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)
        
        # Variables for drag scrolling
        self._drag_start_x = 0
        self._drag_last_x = 0
        
        # Apply theme to canvas
        self._apply_canvas_theme()
        
        # Store forecast cards
        self.forecast_cards = []
        
        # Error label for forecast-specific errors
        self.error_label = ThemedLabel(
            self,
            theme_manager,
            label_type="error",
            text="",
            font=("Helvetica", 11),
            anchor='center'
        )
    
    def _apply_canvas_theme(self):
        """Apply theme to canvas and scrollbar."""
        colors = self.theme_manager.get_colors()
        self.canvas.configure(
            bg=colors["weather_card_bg"],
            highlightbackground=colors["border_light"],
            highlightcolor=colors["border_medium"]
        )
        
        # Configure scrollbar style
        style = ttk.Style()
        style.configure(
            "Horizontal.TScrollbar",
            background=colors["bg_tertiary"],
            troughcolor=colors["bg_secondary"],
            bordercolor=colors["border_light"],
            arrowcolor=colors["text_secondary"],
            darkcolor=colors["border_medium"],
            lightcolor=colors["bg_primary"]
        )
    
    def _bind_mousewheel_recursive(self, widget):
        """Recursively bind mousewheel to widget and all its children."""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        
        # Also bind to children
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for horizontal movement."""
        # Only scroll if there's content to scroll
        if self.canvas.winfo_exists():
            bbox = self.canvas.bbox("all")
            if bbox and bbox[2] > self.canvas.winfo_width():
                # Handle different platforms
                if event.delta:
                    # Windows - convert vertical scroll to horizontal
                    delta = int(-1 * (event.delta / 120))
                    self.canvas.xview_scroll(delta, "units")
                elif event.num == 4:
                    # Linux scroll up - scroll left
                    self.canvas.xview_scroll(-1, "units")
                elif event.num == 5:
                    # Linux scroll down - scroll right
                    self.canvas.xview_scroll(1, "units")
                
                # Prevent event from bubbling up
                return "break"
    
    def _on_key_left(self, event):
        """Handle left arrow key - scroll left."""
        self._smooth_scroll(-3)
        return "break"
    
    def _on_key_right(self, event):
        """Handle right arrow key - scroll right."""
        self._smooth_scroll(3)
        return "break"
    
    def _on_key_home(self, event):
        """Handle Home key - scroll to beginning."""
        self.canvas.xview_moveto(0)
        return "break"
    
    def _on_key_end(self, event):
        """Handle End key - scroll to end."""
        self.canvas.xview_moveto(1)
        return "break"
    
    def _update_scroll_indicators(self):
        """Update scroll indicator visibility based on scroll position."""
        try:
            # Get current scroll position
            left_pos, right_pos = self.canvas.xview()
            
            # Update left indicator (visible if we can scroll left)
            if left_pos > 0:
                self.left_indicator.configure(fg=self.theme_manager.get_color("text_primary"))
            else:
                self.left_indicator.configure(fg=self.theme_manager.get_color("text_muted"))
            
            # Update right indicator (visible if we can scroll right)  
            if right_pos < 1:
                self.right_indicator.configure(fg=self.theme_manager.get_color("text_primary"))
            else:
                self.right_indicator.configure(fg=self.theme_manager.get_color("text_muted"))
                
        except Exception as e:
            print(f"Error updating scroll indicators: {e}")
    
    def _on_scroll(self, *args):
        """Handle scroll events to update scrollbar and indicators."""
        # Update scrollbar
        self.scrollbar.set(*args)
        
        # Update scroll indicators
        self._update_scroll_indicators()
    
    def _on_drag_start(self, event):
        """Handle start of drag scrolling."""
        self._drag_start_x = event.x
        self._drag_last_x = event.x
        self.canvas.configure(cursor="hand2")
    
    def _on_drag_motion(self, event):
        """Handle drag motion for scrolling."""
        # Calculate drag distance
        delta_x = self._drag_last_x - event.x
        self._drag_last_x = event.x
        
        # Convert to scroll units (adjust sensitivity)
        scroll_units = delta_x // 10
        if scroll_units != 0:
            self.canvas.xview_scroll(scroll_units, "units")
    
    def _on_drag_end(self, event):
        """Handle end of drag scrolling."""
        self.canvas.configure(cursor="")
    
    def _smooth_scroll(self, units):
        """Perform smooth scrolling animation."""
        def animate_scroll(remaining_units, step=1):
            if remaining_units == 0:
                return
            
            # Scroll one unit
            direction = 1 if remaining_units > 0 else -1
            self.canvas.xview_scroll(direction * step, "units")
            
            # Continue animation
            new_remaining = remaining_units - (direction * step)
            if abs(new_remaining) > 0:
                self.canvas.after(20, lambda: animate_scroll(new_remaining, step))
        
        animate_scroll(units)
    
    def apply_theme(self):
        """Apply theme to container and canvas."""
        super().apply_theme()
        if hasattr(self, 'canvas'):
            self._apply_canvas_theme()
    
    def clear_forecast(self):
        """Clear all forecast cards."""
        for card in self.forecast_cards:
            card.destroy()
        self.forecast_cards.clear()
        self.error_label.pack_forget()
    
    def show_forecast_error(self, message: str):
        """Show forecast-specific error message."""
        self.clear_forecast()
        self.error_label.config(text=message)
        self.error_label.pack(fill='x', pady=20)
    
    def hide_forecast_error(self):
        """Hide forecast error message."""
        self.error_label.pack_forget()
    
    def update_forecast(self, forecast_data_list: List[Dict[str, Any]], weather_icons: Dict[str, str]):
        """
        Update the forecast container with forecast data.
        
        Args:
            forecast_data_list: List of forecast data dictionaries
            weather_icons: Dictionary mapping icon codes to emoji
        """
        try:
            # Clear existing cards and errors
            self.clear_forecast()
            self.hide_forecast_error()
            
            if not forecast_data_list:
                self.show_forecast_error("No forecast data available")
                return
            
            # Create forecast cards
            for i, forecast_data in enumerate(forecast_data_list[:5]):  # Limit to 5 days
                card = ForecastCard(self.scrollable_frame, self.theme_manager)
                card.pack(side='left', padx=3, pady=3)  # Reduced padding
                card.pack_propagate(False)  # Maintain fixed size
                card.update_forecast_data(forecast_data, weather_icons)
                self.forecast_cards.append(card)
                
                # Bind mousewheel to new cards
                self._bind_mousewheel_recursive(card)
            
            # Force update and configure scroll region
            self.scrollable_frame.update_idletasks()
            self.canvas.update_idletasks()
            
            # Set scroll region to encompass all content
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
                
                # If content is wider than canvas, show scrollbar
                canvas_width = self.canvas.winfo_width()
                content_width = bbox[2] - bbox[0]
                
                if content_width > canvas_width:
                    self.scrollbar.pack(side="bottom", fill="x")
                else:
                    self.scrollbar.pack_forget()
            
            # Reset scroll position to start
            self.canvas.xview_moveto(0)
            
            # Update scroll indicators
            self._update_scroll_indicators()
            
        except Exception as e:
            print(f"Error updating forecast container: {e}")
            self.show_forecast_error("Error displaying forecast data")
    
    def show_loading(self):
        """Show loading state for forecast."""
        self.clear_forecast()
        self.hide_forecast_error()
        
        # Create loading cards
        for i in range(5):
            card = ForecastCard(self.scrollable_frame, self.theme_manager)
            card.pack(side='left', padx=3, pady=3)  # Reduced padding
            card.pack_propagate(False)  # Maintain fixed size
            
            # Set loading state
            loading_data = {
                'day_name': 'Loading...',
                'date_str': '',
                'icon_code': '01d',
                'high_temp': 0,
                'low_temp': 0,
                'description': 'Loading...',
                'humidity': 0,
                'wind_speed': 0
            }
            card.update_forecast_data(loading_data, {'01d': '⏳'})
            self.forecast_cards.append(card)
            
            # Bind mousewheel to loading cards
            self._bind_mousewheel_recursive(card)
        
        # Update scroll region for loading cards
        self.scrollable_frame.update_idletasks()
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)


def parse_forecast_data(forecast_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse 5-day forecast API response into daily forecast data.
    
    Args:
        forecast_response: Raw API response from OpenWeatherMap 5-day forecast
        
    Returns:
        List of daily forecast dictionaries
    """
    try:
        forecast_list = forecast_response.get('list', [])
        if not forecast_list:
            return []
        
        # Group forecasts by date
        daily_forecasts = {}
        
        for item in forecast_list:
            # Parse datetime
            dt_txt = item.get('dt_txt', '')
            if not dt_txt:
                continue
                
            try:
                dt = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
                date_key = dt.date()
                
                # Skip today's remaining hours, start from tomorrow
                today = datetime.now().date()
                if date_key <= today:
                    continue
                
                # Initialize daily data if not exists
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = {
                        'date': date_key,
                        'temps': [],
                        'conditions': [],
                        'humidity_values': [],
                        'wind_speeds': [],
                        'icons': []
                    }
                
                # Collect data for this day
                main_data = item.get('main', {})
                weather_data = item.get('weather', [{}])[0]
                wind_data = item.get('wind', {})
                
                daily_forecasts[date_key]['temps'].append(main_data.get('temp', 0))
                daily_forecasts[date_key]['conditions'].append(weather_data.get('description', ''))
                daily_forecasts[date_key]['humidity_values'].append(main_data.get('humidity', 0))
                daily_forecasts[date_key]['wind_speeds'].append(wind_data.get('speed', 0))
                daily_forecasts[date_key]['icons'].append(weather_data.get('icon', '01d'))
                
            except ValueError:
                continue
        
        # Process daily forecasts
        processed_forecasts = []
        
        for date_key in sorted(daily_forecasts.keys())[:5]:  # Limit to 5 days
            day_data = daily_forecasts[date_key]
            
            # Calculate daily values
            temps = day_data['temps']
            high_temp = max(temps) if temps else 0
            low_temp = min(temps) if temps else 0
            
            # Get most common condition and icon (midday preference)
            conditions = day_data['conditions']
            icons = day_data['icons']
            
            # Prefer midday conditions (around index len//2)
            mid_index = len(conditions) // 2 if conditions else 0
            description = conditions[mid_index] if conditions else 'Unknown'
            icon_code = icons[mid_index] if icons else '01d'
            
            # Average humidity and wind
            humidity = sum(day_data['humidity_values']) // len(day_data['humidity_values']) if day_data['humidity_values'] else 0
            wind_speed = sum(day_data['wind_speeds']) / len(day_data['wind_speeds']) if day_data['wind_speeds'] else 0
            
            # Format date strings
            day_name = date_key.strftime('%a')  # Mon, Tue, etc.
            date_str = date_key.strftime('%m/%d')  # MM/DD
            
            processed_forecasts.append({
                'date': date_key,
                'day_name': day_name,
                'date_str': date_str,
                'high_temp': high_temp,
                'low_temp': low_temp,
                'description': description,
                'icon_code': icon_code,
                'humidity': humidity,
                'wind_speed': wind_speed
            })
        
        return processed_forecasts
        
    except Exception as e:
        print(f"Error parsing forecast data: {e}")
        return []


def apply_theme_to_existing_widget(widget: tk.Widget, theme_manager: ThemeManager, widget_type: str = "default"):
    """
    Apply theme to an existing widget that wasn't created with themed components.
    
    Args:
        widget: Existing tkinter widget
        theme_manager: ThemeManager instance
        widget_type: Type of widget for styling
    """
    theme_manager.apply_theme_to_widget(widget, widget_type)