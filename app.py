from flask import Flask, render_template, request, jsonify
from weather_model import WeatherPredictor
from health_advisor import HealthAdvisor

app = Flask(__name__)
weather_predictor = WeatherPredictor()
health_advisor = HealthAdvisor()

def get_activity_recommendation(weather):
    """Generate activity recommendations based on weather conditions"""
    if "rain" in weather.lower():
        return "It's rainy. Best to stay indoors with a book or watch a movie."
    elif "clear" in weather.lower():
        return "Great weather! Perfect for a walk, outdoor sports, or cycling."
    elif "cloud" in weather.lower():
        return "Cloudy skies! Consider a relaxing outdoor walk or a visit to a café."
    elif "snow" in weather.lower():
        return "Snowy weather! Try skiing, building a snowman, or enjoy a warm drink inside."
    elif "storm" in weather.lower():
        return "Stormy weather! Stay safe indoors, read a book, or binge-watch a series."
    else:
        return "Enjoy your day with activities you love!"
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.json
    city = data.get('city')

    current_weather = weather_predictor.get_weather_data(city)
    forecast = weather_predictor.get_forecast(city)

    if current_weather and forecast:
        health_conditions = data.get('health_conditions', [])
        health_advice = health_advisor.get_health_advice(current_weather, health_conditions)
        place_recommendations = health_advisor.get_place_recommendations(current_weather)

        # ✅ Get activity recommendation based on weather
        activity_recommendation = get_activity_recommendation(current_weather['description'])

        return jsonify({
            'current_weather': current_weather,
            'forecast': forecast,
            'health_advice': health_advice,
            'place_recommendations': place_recommendations,
            'activity_recommendation': activity_recommendation  # ✅ Added
        })

    return jsonify({'error': 'City not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

