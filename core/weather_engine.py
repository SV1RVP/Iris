import requests
import json
import logging
import time
from datetime import datetime

def update_api_stats():
    try:
        with open('stats.json', 'r') as f:
            stats = json.load(f)
    except:
        stats = {"requests": 0}
    
    stats["requests"] += 1
    with open('stats.json', 'w') as f:
        json.dump(stats, f)

def get_api_stats():
    try:
        with open('stats.json', 'r') as f:
            return json.load(f).get("requests", 0)
    except:
        return 0

def fetch_weather_data(settings):
    """
    Fetches weather data from multiple sources.
    Returns a dictionary with all collected data.
    """
    data = {}
    
    lat = settings.get('latitude', 37.9838)
    lon = settings.get('longitude', 23.7275)
    
    # --- Primary Source (PWS) ---
    p_src = settings.get('primary_source', 'off')
    if p_src != 'off':
        if p_src == 'open_meteo':
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
                "timezone": "auto"
            }
            if settings.get('units') == 'imperial':
                params['temperature_unit'] = 'fahrenheit'
                params['wind_speed_unit'] = 'mph'
                params['precipitation_unit'] = 'inch'

            try:
                resp = requests.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    data["primary"] = resp.json()
                    update_api_stats()
            except Exception as e:
                logging.error(f"Error fetching Primary (Open-Meteo): {e}")
        else:
            # PWS File/URL Logic
            pws_path = settings.get('pws_path', '')
            if pws_path:
                try:
                    if pws_path.startswith('http'):
                        import urllib3
                        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                        resp = requests.get(pws_path, timeout=15, verify=False)
                        try:
                            raw_data = resp.json()
                        except:
                            # Fallback: Parse as text (WeatherLink/Davis style)
                            import re
                            text = resp.text
                            raw_data = {}
                            # Matches key="value" or key=value
                            matches = re.findall(r'(\w+)\s*=\s*["\']?([^"\'\s;]+)["\']?', text)
                            for k, v in matches:
                                raw_data[k] = v
                    else:
                        with open(pws_path, 'r') as f:
                            raw_data = json.load(f)
                    
                    # Store raw data for dynamic extraction
                    data["primary"] = {"raw_pws": raw_data}
                    
                    # Try to extract common fields for standard logic
                    # This is a fallback in case specific sequence logic isn't used
                    data["primary"]["current"] = {
                        "temperature_2m": raw_data.get('temp') or raw_data.get('temperature'),
                        "relative_humidity_2m": raw_data.get('hum') or raw_data.get('humidity'),
                        "wind_speed_10m": raw_data.get('windspeed') or raw_data.get('wind_speed'),
                        "wind_direction_10m": raw_data.get('winddir') or raw_data.get('wind_direction'),
                        "pressure_msl": raw_data.get('barometer') or raw_data.get('pressure')
                    }
                except Exception as e:
                    logging.error(f"Error fetching PWS data ({p_src}): {e}")

    # --- Secondary & Forecast Source ---
    sec_src = settings.get('secondary_source', 'off')
    forecast_target = settings.get('forecast_target', 'OFF')
    
    # Determine model
    if forecast_target != 'OFF':
        model = settings.get('forecast_model', 'auto') or 'auto'
    else:
        model = settings.get('weather_model', 'auto') or 'auto'
        
    logging.info(f"Weather Fetching Triggered for Lat: {lat}, Lon: {lon}")
    
    units = settings.get('units', 'metric')
    
    if sec_src == 'open_meteo' or forecast_target != 'OFF':
        url = "https://api.open-meteo.com/v1/forecast"
        
        current_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
            "timezone": "auto"
        }
        
        daily_params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant",
            "timezone": "auto"
        }
        
        # ECMWF-specific parameter adjustments
        if model == "ecmwf_ifs025":
            # 0.25 IFS support
            daily_params["forecast_days"] = 3

        if units == 'imperial':
            current_params['temperature_unit'] = 'fahrenheit'
            current_params['wind_speed_unit'] = 'mph'
            current_params['precipitation_unit'] = 'inch'
            daily_params['temperature_unit'] = 'fahrenheit'
            daily_params['wind_speed_unit'] = 'mph'
            daily_params['precipitation_unit'] = 'inch'
            
        if model and model != "auto":
            daily_params["models"] = model
        else:
            current_params["daily"] = daily_params["daily"]
        
        sec_data = {"current": {}, "daily": {}}
        
        # Call Current API
        for attempt in range(3):
            try:
                resp = requests.get(url, params=current_params, timeout=15)
                resp.raise_for_status()
                j = resp.json()
                if "current" in j:
                    sec_data["current"] = j["current"]
                if model == "auto" and "daily" in j:
                    sec_data["daily"] = j["daily"]
                update_api_stats()
                break
            except Exception as e:
                logging.error(f"Error fetching current weather: {e} (Attempt {attempt+1}/3)")
                if attempt < 2:
                    time.sleep(2)
                
        # Call Daily API separately if model is specific
        if model and model != "auto":
            for attempt in range(3):
                try:
                    resp = requests.get(url, params=daily_params, timeout=15)
                    resp.raise_for_status()
                    j = resp.json()
                    if "daily" in j:
                        # Normalize keys: remove model suffixes
                        normalized_daily = {}
                        for k, v in j["daily"].items():
                            clean_k = k.replace(f"_{model}", "")
                            normalized_daily[clean_k] = v
                        sec_data["daily"] = normalized_daily
                    update_api_stats()
                    break
                except Exception as e:
                    logging.error(f"Error fetching daily forecast: {e} (Attempt {attempt+1}/3)")
                    if attempt < 2:
                        time.sleep(2)

        if sec_data["current"] or sec_data["daily"]:
            data["secondary"] = sec_data
            
            # Fetch Air Quality
            if settings.get('seq_secondary_air_quality', 0) > 0:
                aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
                aq_params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current": "european_aqi",
                    "timezone": "auto"
                }
                try:
                    aq_resp = requests.get(aq_url, params=aq_params, timeout=15)
                    if aq_resp.status_code == 200:
                        aq_data = aq_resp.json()
                        if 'current' in aq_data and 'european_aqi' in aq_data['current']:
                            data['secondary']['current']['air_quality'] = aq_data['current']['european_aqi']
                except Exception as e:
                    logging.error(f"Failed to fetch Air Quality API: {e}")

    # Fetch Space Weather
    sw_src = settings.get('sw_source', 'off')
    if sw_src == 'on' and (settings.get('seq_sw_noaa_g', 0) > 0 or settings.get('seq_sw_noaa_s', 0) > 0 or settings.get('seq_sw_noaa_r', 0) > 0):
        noaa_url = "https://services.swpc.noaa.gov/products/noaa-scales.json"
        try:
            noaa_resp = requests.get(noaa_url, timeout=15)
            if noaa_resp.status_code == 200:
                noaa_data = noaa_resp.json()
                if "0" in noaa_data:
                    current_sw = noaa_data["0"]
                    data['sw'] = {
                        'G': int(current_sw.get('G', {}).get('Scale', 0) or 0),
                        'S': int(current_sw.get('S', {}).get('Scale', 0) or 0),
                        'R': int(current_sw.get('R', {}).get('Scale', 0) or 0)
                    }
        except Exception as e:
            logging.error(f"Error fetching Space Weather (NOAA): {e}")

    return data
