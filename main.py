import logging
import os
import json
from webui.app import app
from core.scheduler import scheduler_instance
from core.ptt_controller import ptt_instance

SETTINGS_FILE = 'settings.json'

def setup_logging():
    import sys
    # Ensure Windows console can print UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def ensure_settings():
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "enable_beacon": True,
            "schedule_interval": 15,
            "latitude": 37.9838,
            "longitude": 23.7275,
            "primary_source": "off",
            "pws_path": "",
            "secondary_source": "off",
            "env_source": "off",
            "env_path": "",
            "sw_source": "off",
            "weather_model": "auto",
            "forecast_target": "OFF",
            "forecast_model": "auto",
            "forecast_prologue": "",
            "forecast_epilogue": "",
            "units": "metric",
            "prologue": "",
            "epilogue": "",
            "tts_voice": "en-US-AriaNeural",
            "tts_rate": 0,
            "audio_volume": 1.0,
            "ptt_port": "None",
            "ptt_pin": "RTS High",
            
            "seq_primary_weather_code": 0,
            "seq_primary_temp": 0,
            "seq_primary_apparent_temp": 0,
            "seq_primary_humidity": 0,
            "seq_primary_precipitation": 0,
            "seq_primary_wind_speed": 0,
            "seq_primary_wind_dir": 0,
            "seq_primary_wind_gusts": 0,
            "seq_primary_cloud_cover": 0,
            "seq_primary_air_quality": 0,
            
            "seq_secondary_weather_code": 0,
            "seq_secondary_temp": 0,
            "seq_secondary_apparent_temp": 0,
            "seq_secondary_humidity": 0,
            "seq_secondary_precipitation": 0,
            "seq_secondary_wind_speed": 0,
            "seq_secondary_wind_dir": 0,
            "seq_secondary_wind_gusts": 0,
            "seq_secondary_cloud_cover": 0,
            "seq_secondary_air_quality": 0,
            
            "seq_env_temp": 0,
            "seq_env_humidity": 0,
            "seq_env_pressure": 0,
            
            "seq_sw_noaa_g": 0,
            "seq_sw_noaa_s": 0,
            "seq_sw_noaa_r": 0,
            
            "seq_forecast_weather_code": 0,
            "seq_forecast_temp": 0,
            "seq_forecast_apparent_temp": 0,
            "seq_forecast_precipitation": 0,
            "seq_forecast_precipitation_sum": 0,
            "seq_forecast_wind_speed": 0,
            "seq_forecast_wind_dir": 0,
            "seq_forecast_uv_index": 0,
            "seq_forecast_sunrise": 0,
            "seq_forecast_sunset": 0
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f, indent=4)
        logging.info("Created default settings.json")

def main():
    setup_logging()
    logging.info("Starting Iris Meteo Beacon...")
    
    ensure_settings()
    
    # Init PTT with current settings
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
        ptt_instance.setup(settings.get('ptt_port'), settings.get('ptt_pin', 'RTS'))
        
    # Start Scheduler
    scheduler_instance.start()
    
    # Suppress Flask development server warning
    import sys
    try:
        from flask import cli
        cli.show_server_banner = lambda *args: None
    except Exception:
        pass
        
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Run WebUI on port 1982
    app.run(host='0.0.0.0', port=1982, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()
