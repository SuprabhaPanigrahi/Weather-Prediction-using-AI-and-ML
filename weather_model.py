import numpy as np
import requests
from datetime import datetime, timedelta
from config import OPENWEATHER_API_KEY

class WeatherPredictor:
    def __init__(self):
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather_data(self, city):
        try:
            url = f"{self.base_url}/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon']
                }
            return None
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_forecast(self, city):
        try:
            url = f"{self.base_url}/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                daily_forecasts = {}
                
                # Group forecasts by day
                for item in data['list']:
                    date = datetime.fromtimestamp(item['dt']).date()
                    if date not in daily_forecasts:
                        daily_forecasts[date] = {
                            'temps': [],
                            'descriptions': [],
                            'icons': []
                        }
                    daily_forecasts[date]['temps'].append(item['main']['temp'])
                    daily_forecasts[date]['descriptions'].append(item['weather'][0]['description'])
                    daily_forecasts[date]['icons'].append(item['weather'][0]['icon'])

                # Process daily forecasts
                forecasts = []
                for date, data in daily_forecasts.items():
                    forecasts.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'temperature': np.mean(data['temps']),
                        'description': max(set(data['descriptions']), key=data['descriptions'].count),
                        'icon': max(set(data['icons']), key=data['icons'].count)
                    })
                
                return forecasts[:7]  # Return only next 7 days
            return None
        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            return None

    def get_weather_score(self, weather_data):
        """Calculate a weather score for activity recommendations"""
        score = 100
        
        # Temperature penalties
        temp = weather_data['temperature']
        if temp < 10 or temp > 30:
            score -= 20
        elif temp < 15 or temp > 25:
            score -= 10

        # Wind penalties
        wind_speed = weather_data['wind_speed']
        if wind_speed > 10:
            score -= 20
        elif wind_speed > 5:
            score -= 10

        # Weather condition penalties
        description = weather_data['description'].lower()
        if 'rain' in description or 'storm' in description:
            score -= 30
        elif 'cloud' in description:
            score -= 10

        return max(0, score)
