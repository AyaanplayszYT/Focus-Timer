"""
Weather service for fetching current weather data.
Uses wttr.in free API (no API key required).
"""

import urllib.request
import json
from typing import Optional, Dict
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QThread


@dataclass
class WeatherData:
    """Weather data structure."""
    temp_c: int
    temp_f: int
    condition: str
    icon: str
    location: str
    humidity: int
    wind_kph: float
    
    @property
    def display_temp(self) -> str:
        return f"{self.temp_c}°C"
    
    @property
    def display_condition(self) -> str:
        return self.condition


class WeatherWorker(QThread):
    """Background worker for fetching weather."""
    
    finished = Signal(object)  # WeatherData or None
    error = Signal(str)
    
    def __init__(self, location: str = ""):
        super().__init__()
        self.location = location
    
    def run(self):
        try:
            # Use wttr.in API - free, no key needed
            url = f"https://wttr.in/{self.location}?format=j1"
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            current = data['current_condition'][0]
            area = data['nearest_area'][0]
            
            # Map weather codes to simple icons
            code = int(current.get('weatherCode', 113))
            icon = self._get_weather_icon(code)
            
            weather = WeatherData(
                temp_c=int(current['temp_C']),
                temp_f=int(current['temp_F']),
                condition=current['weatherDesc'][0]['value'],
                icon=icon,
                location=area['areaName'][0]['value'],
                humidity=int(current['humidity']),
                wind_kph=float(current['windspeedKmph'])
            )
            
            self.finished.emit(weather)
            
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(None)
    
    def _get_weather_icon(self, code: int) -> str:
        """Map weather code to emoji icon."""
        # wttr.in weather codes
        if code == 113:  # Clear/Sunny
            return "☀️"
        elif code in [116, 119]:  # Partly cloudy, Cloudy
            return "⛅"
        elif code == 122:  # Overcast
            return "☁️"
        elif code in [143, 248, 260]:  # Fog/Mist
            return "🌫️"
        elif code in [176, 263, 266, 293, 296, 299, 302, 305, 308, 311, 314, 353, 356, 359]:  # Rain
            return "🌧️"
        elif code in [179, 182, 185, 281, 284, 317, 320, 350, 362, 365, 374, 377]:  # Sleet/Ice
            return "🌨️"
        elif code in [200, 386, 389, 392, 395]:  # Thunder
            return "⛈️"
        elif code in [227, 230, 323, 326, 329, 332, 335, 338, 368, 371]:  # Snow
            return "❄️"
        else:
            return "🌤️"


class WeatherService(QObject):
    """Service for managing weather data fetching."""
    
    weather_updated = Signal(object)  # WeatherData
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: Optional[WeatherWorker] = None
        self._last_weather: Optional[WeatherData] = None
    
    def fetch_weather(self, location: str = ""):
        """Start fetching weather data."""
        if self._worker and self._worker.isRunning():
            return
        
        self._worker = WeatherWorker(location)
        self._worker.finished.connect(self._on_weather_fetched)
        self._worker.start()
    
    def _on_weather_fetched(self, weather: Optional[WeatherData]):
        if weather:
            self._last_weather = weather
            self.weather_updated.emit(weather)
    
    @property
    def last_weather(self) -> Optional[WeatherData]:
        return self._last_weather
