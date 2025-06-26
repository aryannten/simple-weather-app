import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import json
import webbrowser
from PIL import Image, ImageTk
import io

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast")
        self.root.geometry("500x650")
        self.root.configure(bg='#f0f2f5')
        self.root.resizable(False, False)
        
        # Try to load configuration
        try:
            with open('config.json') as config_file:
                config = json.load(config_file)
                self.api_key = config.get('api_key', '')
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.api_key = "d14c849037a06d959de30fedf4759bcd"  # Fallback to hardcoded key
            
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        
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
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="Weather Forecast",
            font=("Helvetica", 24, "bold"),
            bg='#f0f2f5',
            fg='#2c3e50'
        ).pack(side='left')
        
        # Add a refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="🔄",
            font=("Arial", 12),
            bg='#3498db',
            fg='white',
            bd=0,
            command=self.refresh_weather,
            cursor='hand2'
        )
        refresh_btn.pack(side='right', padx=5)
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='#f0f2f5')
        search_frame.pack(fill='x', pady=(0, 20))
        
        # City input with placeholder
        self.city_entry = tk.Entry(
            search_frame,
            font=("Helvetica", 14),
            width=25,
            justify='center',
            bd=2,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground='#bdc3c7',
            highlightcolor='#3498db'
        )
        self.city_entry.pack(pady=5, ipady=5)
        self.city_entry.insert(0, "Enter city name...")
        self.city_entry.bind('<FocusIn>', self.clear_placeholder)
        self.city_entry.bind('<FocusOut>', self.restore_placeholder)
        self.city_entry.bind('<Return>', lambda event: self.get_weather())
        
        # Search button with better styling
        search_btn = tk.Button(
            search_frame,
            text="Get Weather",
            font=("Helvetica", 12, "bold"),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            command=self.get_weather,
            cursor='hand2',
            padx=20,
            pady=8,
            bd=0,
            relief=tk.FLAT
        )
        search_btn.pack(pady=5)
        
        # Weather display card
        self.weather_card = tk.Frame(
            main_frame,
            bg='white',
            relief=tk.RAISED,
            bd=1,
            highlightbackground='#dfe6e9',
            highlightthickness=1
        )
        self.weather_card.pack(fill='both', expand=True)
        
        # Current weather frame
        self.current_weather_frame = tk.Frame(self.weather_card, bg='white')
        self.current_weather_frame.pack(fill='x', pady=10, padx=10)
        
        # Weather icon and city
        self.weather_icon_label = tk.Label(
            self.current_weather_frame,
            text="",
            font=("Arial", 48),
            bg='white'
        )
        self.weather_icon_label.pack(side='left', padx=10)
        
        city_temp_frame = tk.Frame(self.current_weather_frame, bg='white')
        city_temp_frame.pack(side='left', fill='both', expand=True)
        
        self.city_label = tk.Label(
            city_temp_frame,
            text="",
            font=("Helvetica", 18, "bold"),
            bg='white',
            fg='#2c3e50',
            anchor='w'
        )
        self.city_label.pack(fill='x')
        
        self.temp_label = tk.Label(
            city_temp_frame,
            text="",
            font=("Helvetica", 36, "bold"),
            bg='white',
            anchor='w'
        )
        self.temp_label.pack(fill='x')
        
        # Weather description
        self.desc_label = tk.Label(
            self.current_weather_frame,
            text="",
            font=("Helvetica", 14),
            bg='white',
            fg='#7f8c8d'
        )
        self.desc_label.pack(side='right', padx=10)
        
        # Feels like label
        self.feels_like_label = tk.Label(
            self.weather_card,
            text="",
            font=("Helvetica", 12),
            bg='white',
            fg='#95a5a6'
        )
        self.feels_like_label.pack(anchor='w', padx=20)
        
        # Separator
        ttk.Separator(self.weather_card, orient='horizontal').pack(fill='x', pady=10)
        
        # Additional info grid
        info_frame = tk.Frame(self.weather_card, bg='white')
        info_frame.pack(fill='x', padx=20, pady=10)
        
        # Row 1
        self.humidity_label = self.create_info_label(info_frame, "💧 Humidity:", "")
        self.pressure_label = self.create_info_label(info_frame, "📊 Pressure:", "")
        
        # Row 2
        self.wind_label = self.create_info_label(info_frame, "💨 Wind:", "")
        self.visibility_label = self.create_info_label(info_frame, "👁️ Visibility:", "")
        
        # Last updated and credit
        bottom_frame = tk.Frame(self.weather_card, bg='white')
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        self.updated_label = tk.Label(
            bottom_frame,
            text="",
            font=("Helvetica", 9),
            bg='white',
            fg='#bdc3c7'
        )
        self.updated_label.pack(side='left', padx=20)
        
        credit_label = tk.Label(
            bottom_frame,
            text="Powered by OpenWeather",
            font=("Helvetica", 9, "underline"),
            bg='white',
            fg='#3498db',
            cursor='hand2'
        )
        credit_label.pack(side='right', padx=20)
        credit_label.bind("<Button-1>", lambda e: webbrowser.open("https://openweathermap.org"))
        
        # Initially hide weather card
        self.weather_card.pack_forget()
        
        # Add error label (hidden by default)
        self.error_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 12),
            bg='#f0f2f5',
            fg='#e74c3c'
        )
        
    def create_info_label(self, parent, title, value):
        """Helper function to create consistent info labels"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        tk.Label(
            frame,
            text=title,
            font=("Helvetica", 11),
            bg='white',
            fg='#7f8c8d',
            anchor='w'
        ).pack(fill='x')
        
        value_label = tk.Label(
            frame,
            text=value,
            font=("Helvetica", 12, "bold"),
            bg='white',
            fg='#2c3e50',
            anchor='w'
        )
        value_label.pack(fill='x')
        
        return value_label
        
    def clear_placeholder(self, event):
        """Clear placeholder text when entry gets focus"""
        if self.city_entry.get() == "Enter city name...":
            self.city_entry.delete(0, tk.END)
            self.city_entry.config(fg='black')
            
    def restore_placeholder(self, event):
        """Restore placeholder text if entry is empty"""
        if not self.city_entry.get():
            self.city_entry.insert(0, "Enter city name...")
            self.city_entry.config(fg='grey')
            
    def refresh_weather(self):
        """Refresh the current weather"""
        current_city = self.city_label.cget("text")
        if current_city and current_city != "Enter city name...":
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, current_city)
            self.get_weather()
            
    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city or city == "Enter city name...":
            self.show_error("Please enter a city name!")
            return
            
        # Hide any previous error
        self.error_label.pack_forget()
        
        # Show loading state
        self.show_loading()
        
        try:
            # Make API request
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                weather_data = response.json()
                self.display_weather(weather_data)
            elif response.status_code == 404:
                self.show_error(f"City '{city}' not found!")
            else:
                error_msg = response.json().get('message', 'Unknown error')
                self.show_error(f"API Error: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            self.show_error(f"Network error: {str(e)}")
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
    
    def show_loading(self):
        """Show loading state"""
        self.weather_card.pack(fill='both', expand=True)
        self.city_label.config(text="Loading...")
        self.temp_label.config(text="")
        self.desc_label.config(text="")
        self.feels_like_label.config(text="")
        self.humidity_label.config(text="")
        self.pressure_label.config(text="")
        self.wind_label.config(text="")
        self.visibility_label.config(text="")
        self.updated_label.config(text="")
        self.weather_icon_label.config(text="⏳")
        self.root.update()
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.config(text=message)
        self.error_label.pack(fill='x', pady=10)
        self.weather_card.pack_forget()
        
    def display_weather(self, data):
        """Display weather information"""
        try:
            # Extract weather data
            city_name = data['name']
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
            
            # Change temperature color based on value
            if temp <= 0:
                temp_color = '#3498db'  # Blue for cold
            elif temp <= 10:
                temp_color = '#2ecc71'  # Green for cool
            elif temp <= 25:
                temp_color = '#f39c12'  # Orange for mild
            else:
                temp_color = '#e74c3c'  # Red for hot
                
            self.temp_label.config(fg=temp_color)
            
            # Show the weather card if hidden
            self.weather_card.pack(fill='both', expand=True)
            
        except KeyError as e:
            self.show_error(f"Invalid weather data received: Missing {str(e)}")
        except Exception as e:
            self.show_error(f"Error displaying weather: {str(e)}")

def main():
    root = tk.Tk()
    
    # Set window icon if possible
    try:
        root.iconbitmap('weather_icon.ico')  # You can provide an icon file
    except:
        pass
        
    app = WeatherApp(root)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()

if __name__ == "__main__":
    main()