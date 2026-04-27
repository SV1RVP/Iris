from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import json
import os

from .weather_engine import fetch_weather_data
from .text_formatter import generate_weather_text
from .audio_engine import generate_and_play
from .ptt_controller import ptt_instance

SETTINGS_FILE = 'settings.json'

class BeaconScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_forecast_next = False
        
    def _load_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load settings for broadcast: {e}")
            return {}

    def _broadcast_job(self):
        logging.info("--- Broadcast Job Triggered ---")
        settings = self._load_settings()
        
        if not settings.get('enable_beacon', True):
            logging.info("Beacon is disabled in settings. Skipping broadcast.")
            return

        lat = settings.get('latitude', 37.9838)
        lon = settings.get('longitude', 23.7275)
        
        logging.info(f"Fetching weather data for Lat: {lat}, Lon: {lon}")
        data = fetch_weather_data(settings)
        
        if not data:
            logging.error("Failed to retrieve weather data. Aborting broadcast.")
            return
            
        target = settings.get('forecast_target', 'OFF')
        
        # Check if any current conditions source is active
        has_current_sources = any([
            settings.get('primary_source', 'off') != 'off',
            settings.get('secondary_source', 'off') != 'off',
            settings.get('env_source', 'off') != 'off',
            settings.get('sw_source', 'off') != 'off'
        ])
        
        # If ONLY forecast is active, always set is_forecast=True
        is_forecast = self.is_forecast_next
        if not has_current_sources and target != 'OFF':
            is_forecast = True
        
        text = generate_weather_text(data, settings, is_forecast=is_forecast)
        
        # Toggle next broadcast type only if we have both current and forecast sources
        if target != 'OFF' and has_current_sources:
            self.is_forecast_next = not self.is_forecast_next
        elif target == 'OFF':
            self.is_forecast_next = False
        else:
            # Only forecast is active, stay on forecast mode
            self.is_forecast_next = True
        
        logging.info(f"Generated text: {text}")
        
        if not text.strip():
            logging.warning("Generated text is empty. Skipping audio generation.")
            return
        
        success = generate_and_play(text, settings, ptt_callback=ptt_instance.trigger)
        if success:
            logging.info("--- Broadcast Complete ---")
        else:
            logging.error("--- Broadcast Failed during Audio Playback ---")

    def start(self):
        """Starts the scheduler with current settings."""
        settings = self._load_settings()
        interval = settings.get('schedule_interval', 15) # minutes
        
        # Build cron expression
        # E.g., if interval is 15, cron minute is '0,15,30,45'
        # if interval is 30, cron minute is '0,30'
        # if interval is 60, cron minute is '0'
        if interval <= 0 or interval >= 60:
            minute_expr = '0'
        else:
            minutes = list(range(0, 60, interval))
            minute_expr = ','.join(map(str, minutes))
            
        trigger = CronTrigger(minute=minute_expr)
        
        self.scheduler.add_job(
            self._broadcast_job,
            trigger=trigger,
            id='main_broadcast_job',
            replace_existing=True,
            misfire_grace_time=300
        )
        
        self.scheduler.start()
        logging.info(f"Scheduler started. Cron interval minutes: {minute_expr}")

    def update_schedule(self):
        """Called when settings are updated to adjust the timer."""
        settings = self._load_settings()
        interval = settings.get('schedule_interval', 15)
        
        if interval <= 0 or interval >= 60:
            minute_expr = '0'
        else:
            minutes = list(range(0, 60, interval))
            minute_expr = ','.join(map(str, minutes))
            
        trigger = CronTrigger(minute=minute_expr)
        self.scheduler.reschedule_job('main_broadcast_job', trigger=trigger)
        logging.info(f"Schedule updated. New cron interval minutes: {minute_expr}")
        
    def trigger_manual(self):
        """Triggers a broadcast immediately (runs in the background scheduler pool)."""
        self.scheduler.add_job(self._broadcast_job, 'date', id='manual_broadcast')
        logging.info("Manual broadcast triggered.")

scheduler_instance = BeaconScheduler()
