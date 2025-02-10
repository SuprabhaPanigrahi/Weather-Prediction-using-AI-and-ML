import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import datetime

# Step 1: Generate Synthetic Historical Weather Data
def generate_synthetic_weather_data(n_days=365):
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", periods=n_days)
    temperature = 20 + 10 * np.sin(np.linspace(0, 2 * np.pi, n_days)) + np.random.normal(0, 1, n_days)
    humidity = 60 + 10 * np.cos(np.linspace(0, 2 * np.pi, n_days)) + np.random.normal(0, 5, n_days)
    wind_speed = 5 + 2 * np.sin(np.linspace(0, 2 * np.pi, n_days)) + np.random.normal(0, 0.5, n_days)

    data = pd.DataFrame({
        "Date": dates,
        "Temperature": temperature,
        "Humidity": humidity,
        "Wind Speed": wind_speed
    })
    return data

# Step 2: Prepare Data for Training
def prepare_data(data, feature, look_back=10):
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data[[feature]])

    X, y = [], []
    for i in range(len(data_scaled) - look_back):
        X.append(data_scaled[i:i + look_back, 0])
        y.append(data_scaled[i + look_back, 0])

    return np.array(X), np.array(y), scaler

# Step 3: Build Neural Network (LSTM)
def build_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model

# Step 4: Fetch Coordinates for a Given City Using OpenWeatherMap API
def get_city_coordinates(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    if data.get("cod") != 200:
        print(f"Error fetching data for {city_name}.")
        return None, None
    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]
    return lat, lon

# Step 5: Fetch Real-Time Data using OpenWeatherMap API
def fetch_real_time_weather(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    return {"Temperature": temperature, "Humidity": humidity, "Wind Speed": wind_speed}

# Step 6: Predict Future Weather Based on Real-Time Data
def predict_weather(model, scaler, real_time_data, look_back=10):
    # Create a sequence based on the real-time data
    new_data = np.array([real_time_data['Temperature']])
    new_data = new_data.reshape((1, 1, 1))
    
    # Normalize the data before making the prediction
    prediction = model.predict(new_data)
    prediction = scaler.inverse_transform(prediction.reshape(-1, 1))
    return prediction[0][0]

# Main Script
if __name__ == "__main__":
    # User inputs city name
    city_name = input("Enter the city name for weather prediction: ")
    
    # Your OpenWeatherMap API key
    api_key = "5a5d82e881547ef55e4ac2b074b47a46"
    
    # Get coordinates of the city
    lat, lon = get_city_coordinates(city_name, api_key)
    if lat is None or lon is None:
        print("Failed to fetch city coordinates. Exiting...")
        exit()

    # Generate synthetic historical weather data
    historical_data = generate_synthetic_weather_data()
    feature = "Temperature"  # Feature to predict
    look_back = 10  # Number of days to look back

    # Prepare data for training
    X, y, scaler = prepare_data(historical_data, feature, look_back)
    X = X.reshape((X.shape[0], X.shape[1], 1))  # Reshape data for LSTM input

    # Split data into training and testing sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Build and train the model
    model = build_model((X_train.shape[1], 1))
    model.fit(X_train, y_train, batch_size=32, epochs=50, validation_data=(X_test, y_test), verbose=1)

    # Fetch real-time weather data using OpenWeatherMap API
    real_time_data = fetch_real_time_weather(api_key, lat, lon)

    # Predict future temperature using real-time data
    predicted_temperature = predict_weather(model, scaler, real_time_data)
    print(f"\nPredicted Temperature for {city_name}: {predicted_temperature:.2f}°C")

    # Get the last 'look_back' number of days for prediction comparison
    last_real_data = historical_data.iloc[-look_back:]

    # Prepare the data for plotting actual vs predicted
    # Get predicted values for the last `look_back` days
    predicted_values = model.predict(X[-look_back:])
    predicted_values = scaler.inverse_transform(predicted_values)

    # Plot both Actual and Predicted Temperatures
    plt.figure(figsize=(12, 6))
    plt.plot(historical_data['Date'], historical_data['Temperature'], label="Historical Temperature (Actual)", color="blue")
    plt.plot(last_real_data['Date'], predicted_values, label="Predicted Temperature", color="red", linestyle="--")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.title(f"Actual vs Predicted Temperature for {city_name}")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Show actual and predicted temperatures for the last days
    print("\nLast 10 Days - Actual vs Predicted Temperatures:")
    for i in range(len(last_real_data)):
        print(f"Date: {last_real_data['Date'].iloc[i]} | Actual: {last_real_data['Temperature'].iloc[i]:.2f}°C | Predicted: {predicted_values[i][0]:.2f}°C")
