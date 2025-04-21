//static/js/main.js
// Utility function to safely get DOM elements
function getElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        throw new Error(`Element with id "${id}" not found`);
    }
    return element;
}

async function getWeather() {
    const cityInput = getElement('cityInput');
    const city = cityInput.value.trim();
    
    if (!city) {
        alert('Please enter a city name');
        return;
    }

    // Get selected health conditions
    const healthConditions = Array.from(document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked'))
        .map(checkbox => checkbox.value);

    try {
        document.body.classList.add('loading');

        const response = await fetch('/api/weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                city: city,
                health_conditions: healthConditions
            })
        });

        if (!response.ok) {
            throw new Error('City not found');
        }

        const data = await response.json();
        updateUI(data);
    } catch (error) {
        alert(error.message);
    } finally {
        document.body.classList.remove('loading');
    }
}

function updateCurrentWeather(currentWeather) {
    const currentWeatherElement = getElement('currentWeatherData');
    currentWeatherElement.querySelector('.temperature').textContent = `${Math.round(currentWeather.temperature)}°C`;
    currentWeatherElement.querySelector('.description').textContent = currentWeather.description;
    currentWeatherElement.querySelector('.humidity').textContent = `Humidity: ${currentWeather.humidity}%`;
    currentWeatherElement.querySelector('.wind').textContent = `Wind: ${currentWeather.wind_speed} m/s`;
}

function updatePlaceRecommendations(recommendations) {
    const recommendationsDiv = getElement('activityRecommendation');
    let recommendationsHTML = `
        <h3>Place & Activity Recommendations</h3>
        <p class="weather-status">${recommendations.weather_status}</p>
        <p class="best-time">⏰ ${recommendations.best_time}</p>
        <div class="recommendations-container">
    `;

    if (recommendations.categories && Array.isArray(recommendations.categories)) {
        recommendations.categories.forEach(category => {
            recommendationsHTML += `
                <div class="recommendation-category">
                    <ul>
                        ${category.places.map(place => `<li>📍 ${place}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
    }

    recommendationsHTML += '</div>';
    recommendationsDiv.innerHTML = recommendationsHTML;
}

function updateHealthAdvice(healthAdvice) {
    const healthAdviceElement = getElement('healthAdvice');
    healthAdviceElement.innerHTML = `
        <h3>Health Advice</h3>
        ${healthAdvice.length > 0 
            ? `<ul>${healthAdvice.map(advice => `<li>${advice}</li>`).join('')}</ul>`
            : '<p>No specific health concerns for current conditions.</p>'}
    `;
}

function updateActivityRecommendation(recommendation) {
    const activityElement = getElement('activityRecommendation');
    activityElement.innerHTML = `
        <h3>Activity Recommendation</h3>
        <p>${recommendation}</p>
    `;
}
function updateUI(data) {
    updateCurrentWeather(data.current_weather);
    updatePlaceRecommendations(data.place_recommendations);
    updateHealthAdvice(data.health_advice);
    // Add null check
    if (data.activity_recommendation) {
        updateActivityRecommendation(data.activity_recommendation);
    }
    updateForecast(data.forecast);
}

function updateForecast(forecast) {
    const forecastContainer = getElement('forecastContainer');
    forecastContainer.innerHTML = forecast.map(day => `
        <div class="forecast-card">
            <h4>${new Date(day.date).toLocaleDateString()}</h4>
            <p class="temperature">${Math.round(day.temperature)}°C</p>
            <p class="description">${day.description}</p>
        </div>
    `).join('');
}

function updateUI(data) {
    updateCurrentWeather(data.current_weather);
    updatePlaceRecommendations(data.place_recommendations);
    updateHealthAdvice(data.health_advice);
    updateActivityRecommendation(data.activity_recommendation);
    updateForecast(data.forecast);
}

// Event Listeners
function initializeEventListeners() {
    const cityInput = getElement('cityInput');
    cityInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            getWeather();
        }
    });
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    try {
        initializeEventListeners();
        const defaultCity = 'kukudakhandi';
        const cityInput = getElement('cityInput');
        cityInput.value = defaultCity;
        getWeather();
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Failed to initialize the application');
    }
});

// Dark/Light Mode Toggle
function toggleTheme() {
    const body = document.body;
    const themeToggle = getElement('themeToggle');
    const isDarkMode = body.getAttribute('data-theme') === 'light';

    if (isDarkMode) {
        body.setAttribute('data-theme', 'dark');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>'; // Moon icon for dark mode
    } else {
        body.setAttribute('data-theme', 'light');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>'; // Sun icon for light mode
    }
}

// Initialize theme toggle
function initializeThemeToggle() {
    const body = document.body;
    const themeToggle = getElement('themeToggle');

    // Set dark theme as default
    body.setAttribute('data-theme', 'dark');
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>'; // Moon icon for dark mode

    // Add event listener for theme toggle
    themeToggle.addEventListener('click', toggleTheme);
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    try {
        initializeThemeToggle();
        initializeEventListeners();
        const defaultCity = 'kukudakhandi';
        const cityInput = getElement('cityInput');
        cityInput.value = defaultCity;
        getWeather();
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Failed to initialize the application');
    }
});


// Show loading spinner
function showLoadingSpinner() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    loadingSpinner.style.display = 'flex';
}

// Hide loading spinner
function hideLoadingSpinner() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    loadingSpinner.style.display = 'none';
}

// Update weather icon dynamically
function updateWeatherIcon(iconElement, description) {
    const weatherIcons = {
        clear: 'fa-sun',
        clouds: 'fa-cloud',
        rain: 'fa-cloud-rain',
        snow: 'fa-snowflake',
        thunderstorm: 'fa-bolt',
        mist: 'fa-smog',
    };

    const lowerCaseDescription = description.toLowerCase();
    let iconClass = 'fa-sun'; // Default icon

    for (const key in weatherIcons) {
        if (lowerCaseDescription.includes(key)) {
            iconClass = weatherIcons[key];
            break;
        }
    }

    iconElement.className = `fas ${iconClass} weather-icon-animation`;
}

// Modify getWeather function to include loading spinner
async function getWeather() {
    const cityInput = getElement('cityInput');
    const city = cityInput.value.trim();

    if (!city) {
        alert('Please enter a city name');
        return;
    }

    showLoadingSpinner();

    try {
        const response = await fetch('/api/weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                city: city,
                health_conditions: Array.from(document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked'))
                    .map(checkbox => checkbox.value),
            }),
        });

        if (!response.ok) {
            throw new Error('City not found');
        }

        const data = await response.json();
        updateUI(data);
    } catch (error) {
        alert(error.message);
    } finally {
        hideLoadingSpinner();
    }
}

// Modify updateUI to update weather icon
function updateUI(data) {
    updateCurrentWeather(data.current_weather);
    updatePlaceRecommendations(data.place_recommendations);
    updateHealthAdvice(data.health_advice);
    if (data.activity_recommendation) {
        updateActivityRecommendation(data.activity_recommendation);
    }
    updateForecast(data.forecast);

    // Update weather icon
    const weatherIconElement = document.querySelector('.weather-icon i');
    updateWeatherIcon(weatherIconElement, data.current_weather.description);
}
