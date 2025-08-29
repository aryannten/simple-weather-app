# Weather Forecast Application

A modern, theme-aware weather application built with Python and Tkinter, featuring comprehensive error handling, favorites management, and accessibility compliance.

## Features

- **Real-time Weather Data**: Get current weather and 5-day forecasts using OpenWeatherMap API
- **Dual Theme Support**: Light and dark themes with accessibility-compliant color contrast
- **Favorites Management**: Save and quickly access your favorite cities
- **Comprehensive Error Handling**: Graceful error recovery and user-friendly notifications
- **Keyboard Shortcuts**: Enhanced user experience with keyboard navigation
- **Accessibility**: WCAG-compliant design with proper contrast ratios

## Project Structure

```
weather-app/
├── weather.py              # Main application entry point
├── config_manager.py       # Configuration management system
├── theme_manager.py        # Theme switching and color management
├── favorites_manager.py    # Favorites CRUD operations
├── error_handler.py        # Centralized error handling
├── notification_system.py  # User notification system
├── ui_components.py        # Reusable themed UI components
├── config.json            # User configuration file
├── .kiro/                 # Kiro IDE specifications
└── README.md              # This file
```

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install requests tkinter
   ```

2. **Get API Key**:
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key

3. **Configure Application**:
   - Copy `config.example.json` to `config.json`
   - Edit `config.json` and add your OpenWeatherMap API key
   - Or run the application: `python weather.py` and click settings (⚙️) to configure

## Usage

### Basic Operations
- **Search Weather**: Enter city name and press Enter or click "Get Weather"
- **Add to Favorites**: Click the star (⭐) button next to city name
- **Switch Themes**: Click the theme toggle button (🌙/☀️)
- **Refresh Data**: Click refresh button (🔄) or press F5

### Keyboard Shortcuts
- **Enter**: Search for weather (when in search field)
- **F5**: Refresh current weather data
- **Ctrl+T**: Toggle between light and dark themes
- **Escape**: Clear search field

### Favorites Management
- Click the star button to add/remove cities from favorites
- Access favorites from the right panel
- Click any favorite city to load its weather data

## Configuration

The application stores settings in `config.json`:

```json
{
    "api_key": "your_openweather_api_key",
    "theme": "light",
    "units": "metric",
    "favorites": [],
    "auto_refresh": false,
    "refresh_interval": 300
}
```

## Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- Invalid API keys
- City not found errors
- Configuration file corruption
- Forecast service unavailability

## Accessibility

- **Color Contrast**: Both themes meet WCAG AA standards
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper labeling and structure
- **Visual Indicators**: Clear status and error messaging

## Development

### Core Components

- **WeatherApp**: Main application class managing UI and interactions
- **ConfigManager**: Handles configuration persistence and validation
- **ThemeManager**: Manages theme switching and color schemes
- **FavoritesManager**: Handles favorite cities CRUD operations
- **ErrorHandler**: Centralized error handling and user notifications
- **NotificationManager**: User notification display system

### Architecture

The application follows a modular architecture with clear separation of concerns:
- UI components are theme-aware and self-updating
- Configuration is centrally managed with validation
- Error handling provides graceful degradation
- All components support both light and dark themes

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions, please check the error messages in the application or review the configuration settings.