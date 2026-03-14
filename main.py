import requests
import datetime
import logging
from geopy.geocoders import Nominatim

# Configuration (Use environment variables for production security)
CONFIG = {
    "WEATHER_KEY": "f8105a60dc3c975f99b181a647370c94",
    "TOMTOM_KEY": "Zs6Yp7O868qgnDGWEGypVLoVhojkdhPT",
    "USER_AGENT": "flow_coffee_adaptive_system"
}

# Logging setup for business logic auditing
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_location(city_name):
    """Convert city name into geolocation coordinates."""
    try:
        geolocator = Nominatim(user_agent=CONFIG["USER_AGENT"])
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude, location.address
        return None, None, None
    except Exception as e:
        logging.error(f"Geocoding error: {e}")
        return None, None, None

def fetch_live_data(lat, lon):
    """Ingest live data from OpenWeather and TomTom APIs."""
    try:
        # 1. Weather Data Ingestion
        w_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={CONFIG['WEATHER_KEY']}&units=metric"
        w_res = requests.get(w_url, timeout=5).json()
        
        temp = w_res['main']['temp']
        hum = w_res['main']['humidity']
        
        # Robust precipitation check
        weather_main = w_res.get('weather', [{}])[0].get('main', '').lower()
        is_raining = any(word in weather_main for word in ['rain', 'drizzle', 'thunderstorm'])

        # 2. Traffic Flow Data Ingestion
        t_url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={CONFIG['TOMTOM_KEY']}&point={lat},{lon}"
        t_res = requests.get(t_url, timeout=5).json()
        
        flow = t_res.get('flowSegmentData', {})
        curr_speed = flow.get('currentSpeed', 1)
        free_speed = flow.get('freeFlowSpeed', 1)
        
        # City Stress Index Calculation: Correlation between traffic congestion and speed
        traffic_idx = round((1 - (curr_speed / free_speed)) * 100)
        traffic_idx = max(0, min(100, traffic_idx)) # Data normalization (0-100 range)
        
        return {
            "temp": temp, 
            "hum": hum, 
            "traffic": traffic_idx, 
            "is_raining": is_raining,
            "condition": weather_main
        }
    except Exception as e:
        logging.error(f"Data ingestion failed: {e}")
        return None

def analyze_city_stress(data):
    """Decision Engine for environmental actuation and business strategy."""
    now = datetime.datetime.now()
    hour = now.hour
    is_rush_hour = (8 <= hour <= 10) or (17 <= hour <= 19)
    
    # 1. Product Strategy (Business Logic)
    if data['is_raining']:
        m_style = "MONSOON COLLECTION (Thermal-Boost Beverages)"
    elif data['temp'] > 33:
        m_style = "OASIS SELECTION (Hydration & Electrolytes)"
    else:
        m_style = "STANDARD SEASONAL"

    # Operational Throughput Optimization
    if data['traffic'] > 70 or is_rush_hour:
        m_layout = "FLASH MODE: Automated Pre-Brew & Grab-and-Go"
    else:
        m_layout = "GOURMET: Hand-Crafted Experience"

    # 2. Atmospheric Response (UX Adaptation)
    # Social Zone: Emotional focus and dwell time optimization
    if data['is_raining'] or data['traffic'] > 80:
        social = {"Mode": "SHELTER", "Lighting": "2000K Amber", "Audio": "Lounge Jazz"}
    elif data['temp'] > 33:
        social = {"Mode": "REFUGE", "Lighting": "5000K Arctic Blue", "Audio": "Chillstep"}
    else:
        social = {"Mode": "VIBRANT", "Lighting": "Natural White", "Audio": "Ambient Indie"}

    # Focus Zone: Cognitive performance and noise masking
    if data['traffic'] > 75 or data['is_raining']:
        focus = {"Acoustics": "Active Pink Noise (Masking)", "Temp": "22°C"}
    else:
        focus = {"Acoustics": "Minimalist Lo-fi", "Temp": "23°C"}

    return m_style, m_layout, social, focus

# --- Execution ---
print("🚀 FLOW COFFEE: ADAPTIVE RETAIL ENGINE v2.1")
print("Initializing system core...")
city = input("Enter city for simulation (e.g.
, Bangkok): ")

lat, lon, address = get_location(city)

if lat:
    stats = fetch_live_data(lat, lon)
    if stats:
        menu_s, menu_l, s_zone, f_zone = analyze_city_stress(stats)
        
        print(f"\n✅ SMART SYSTEM ACTIVE: {address}")
        print(f"Signals: {stats['temp']}°C | Traffic: {stats['traffic']}% | Status: {stats['condition']}")
        print("-" * 60)
        print(f"STRATEGY:  {menu_s}")
        print(f"OPERATION: {menu_l}")
        print("-" * 60)
        print(f"SOCIAL ZONE: {s_zone['Mode']} (Lighting: {s_zone['Lighting']}, Audio: {s_zone['Audio']})")
        print(f"FOCUS ZONE:  Performance Mode (Acoustics: {f_zone['Acoustics']}, Temp: {f_zone['Temp']})")
        print("-" * 60)
    else:
        print("❌ Error: Unable to fetch live data. Verify API keys.")
else:
    print("❌ Error: Location not found.")
