#helth_advisor.py
class HealthAdvisor:
    def __init__(self):
        self.risk_conditions = {
            'asthma': {'temp_range': (18, 24), 'humidity_range': (30, 50)},
            'allergies': {'temp_range': (15, 25), 'humidity_range': (40, 60)},
            'heart_condition': {'temp_range': (18, 27), 'humidity_range': (40, 60)}
        }

        self.place_recommendations = {
            'excellent': [
                {
                    'type': 'Outdoor Activities',
                    'places': [
                        'Local Parks and Gardens',
                        'Hiking Trails',
                        'Beach (if available)',
                        'Open-air Markets',
                        'Outdoor Sports Facilities'
                    ]
                },
                {
                    'type': 'Tourist Attractions',
                    'places': [
                        'Historical Monuments',
                        'Botanical Gardens',
                        'Zoo',
                        'Adventure Parks',
                        'Scenic Viewpoints'
                    ]
                }
            ],
            'good': [
                {
                    'type': 'Mixed Activities',
                    'places': [
                        'Shopping Districts',
                        'Outdoor Cafes',
                        'City Tours',
                        'Public Squares',
                        'Cultural Districts'
                    ]
                }
            ],
            'poor': [
                {
                    'type': 'Indoor Activities',
                    'places': [
                        'Museums',
                        'Art Galleries',
                        'Shopping Malls',
                        'Indoor Sports Centers',
                        'Cinema/Theater',
                        'Indoor Markets',
                        'Aquariums'
                    ]
                }
            ]
        }

    def get_health_advice(self, weather_data, health_conditions):
        advice = []
        temp = weather_data['temperature']
        humidity = weather_data['humidity']
        description = weather_data['description'].lower()

        # General weather-based advice
        if 'rain' in description:
            advice.append("🌧️ Carry an umbrella and wear waterproof clothing")
        elif 'snow' in description:
            advice.append("❄️ Wear warm, layered clothing and waterproof boots")
        elif temp > 30:
            advice.append("🌡️ High temperature - stay hydrated and avoid prolonged sun exposure")
        elif temp < 10:
            advice.append("🌡️ Cold weather - wear warm clothing and protect extremities")

        # Health-specific advice
        for condition in health_conditions:
            if condition in self.risk_conditions:
                temp_range = self.risk_conditions[condition]['temp_range']
                humidity_range = self.risk_conditions[condition]['humidity_range']

                if not (temp_range[0] <= temp <= temp_range[1]):
                    if condition == 'asthma':
                        advice.append("😷 Asthma Alert: Consider using an inhaler before outdoor activities")
                    elif condition == 'allergies':
                        advice.append("🤧 Allergy Alert: Consider wearing a mask outdoors")
                    elif condition == 'heart_condition':
                        advice.append("❤️ Heart Condition Alert: Limit strenuous outdoor activities")

        return advice

    def get_place_recommendations(self, weather_data):
        weather_score = self._calculate_weather_score(weather_data)
        description = weather_data['description'].lower()
        temp = weather_data['temperature']

        # Determine weather category
        if weather_score >= 80 and 'rain' not in description and 'storm' not in description:
            category = 'excellent'
            weather_status = "Perfect weather for outdoor activities! 🌟"
        elif weather_score >= 60 and 'heavy rain' not in description:
            category = 'good'
            weather_status = "Good weather for mixed activities! 👍"
        else:
            category = 'poor'
            weather_status = "Better to stick to indoor activities! 🏠"

        recommendations = {
            'weather_status': weather_status,
            'categories': self.place_recommendations[category]
        }

        # Add time-based recommendations
        recommendations['best_time'] = self._get_best_time_recommendation(temp, description)

        return recommendations

    def _calculate_weather_score(self, weather_data):
        score = 100
        temp = weather_data['temperature']
        description = weather_data['description'].lower()

        # Temperature adjustments
        if temp < 10 or temp > 35:
            score -= 40
        elif temp < 15 or temp > 30:
            score -= 20
        elif temp < 20 or temp > 25:
            score -= 10

        # Weather condition adjustments
        if 'rain' in description or 'storm' in description:
            score -= 40
        elif 'cloud' in description:
            score -= 10
        elif 'snow' in description:
            score -= 30

        return max(0, min(100, score))

    def _get_best_time_recommendation(self, temperature, description):
        if temperature > 30:
            return "Best to visit places early morning (6-9 AM) or evening (after 5 PM) to avoid peak heat"
        elif temperature < 10:
            return "Best to visit during midday (11 AM-3 PM) when temperatures are warmest"
        elif 'rain' in description:
            return "Check hourly forecast for rain-free periods"
        else:
            return "Weather is pleasant throughout the day"
