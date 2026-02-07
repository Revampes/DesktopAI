import requests

def get_weather(city_name):
    """
    Fetches current weather for a specific city using Open-Meteo.
    """
    try:
        # 1. Geocode the city
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if "results" not in geo_res:
            return f"I couldn't find a location named '{city_name}'."
            
        location = geo_res["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_name = f"{location['name']}, {location.get('country', '')}"
        
        # 2. Get Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        w_res = requests.get(weather_url).json()
        
        if "current" not in w_res:
            return "Could not retrieve weather data."
            
        current = w_res["current"]
        temp = current["temperature_2m"]
        wind = current["wind_speed_10m"]
        unit = w_res["current_units"]["temperature_2m"]
        
        # Interpret weather code (simplified)
        wcode = current["weather_code"]
        condition = "Clear"
        if wcode > 2: condition = "Cloudy"
        if wcode > 50: condition = "Rainy"
        if wcode > 70: condition = "Snowy"
        if wcode > 95: condition = "Thunderstorm"
        
        return f"Weather in {resolved_name}:\nCondition: {condition}\nTemperature: {temp}{unit}\nWind: {wind} km/h"
        
    except Exception as e:
        return f"Error checking weather: {e}"
