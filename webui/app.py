from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import logging
import serial.tools.list_ports
from core.scheduler import scheduler_instance
from core.ptt_controller import ptt_instance
from core.weather_engine import get_api_stats

app = Flask(__name__)
SETTINGS_FILE = 'settings.json'
LOG_FILE = 'app.log'

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify(load_settings())

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    save_settings(data)
    
    # Apply changes to instances
    scheduler_instance.update_schedule()
    ptt_instance.setup(data.get('ptt_port'), data.get('ptt_pin', 'RTS'))
    
    return jsonify({"status": "success"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({"requests": get_api_stats(), "limit": 10000})

@app.route('/api/trigger', methods=['POST'])
def trigger_manual():
    scheduler_instance.trigger_manual()
    return jsonify({"status": "triggered"})

@app.route('/api/audio_devices', methods=['GET'])
def get_audio_devices():
    import pygame
    try:
        import pygame._sdl2.audio as sdl2_audio
        pygame.init()
        devices = sdl2_audio.get_audio_device_names(False)
        return jsonify({"devices": devices})
    except Exception as e:
        logging.error(f"Failed to list audio devices: {e}")
        return jsonify({"devices": []})

@app.route('/api/com_ports', methods=['GET'])
def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return jsonify({"ports": [p.device for p in ports]})

from core import autostart, updater

@app.route('/api/autostart', methods=['GET'])
def get_autostart():
    status = autostart.check_status()
    return jsonify({"enabled": status})

@app.route('/api/autostart', methods=['POST'])
def set_autostart():
    data = request.json
    enable = data.get('enable', False)
    if enable:
        success, msg = autostart.enable_autostart()
    else:
        success, msg = autostart.disable_autostart()
    return jsonify({"success": success, "message": msg, "enabled": autostart.check_status()})

@app.route('/api/update/status', methods=['GET'])
def get_update_status():
    return jsonify(updater.check_for_updates())

@app.route('/api/update/perform', methods=['POST'])
def perform_update():
    logging.info("WebUI: Received update request.")
    try:
        success, msg = updater.run_update()
        return jsonify({"success": success, "message": msg})
    except Exception as e:
        logging.error(f"WebUI: Update request failed unexpectedly: {e}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/api/pws_template/<source>', methods=['GET'])
def get_pws_template(source):
    import re
    # sanitize source to avoid path traversal
    source = "".join(c for c in source if c.isalnum() or c in ('_', '-'))
    
    # Check multiple extensions
    found_path = None
    for ext in ['.htx', '.json', '.txt']:
        p = os.path.join('core', 'pws_templates', f'{source}{ext}')
        if os.path.exists(p):
            found_path = p
            break
            
    if not found_path:
        return jsonify({"variables": []})
        
    variables = []
    
    # Try to load translations
    translations = {}
    trans_path = os.path.join('core', 'pws_templates', 'translations.json')
    if os.path.exists(trans_path):
        try:
            with open(trans_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
        except: pass
        
    with open(found_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    if found_path.endswith('.htx') or found_path.endswith('.txt'):
        # Match weatherlink style: key="value";
        matches = re.findall(r'(\w+)="[^"]*";', content)
        for m in matches:
            if m not in variables:
                # Filter out units
                if 'unit' not in m.lower():
                    variables.append(m)
    elif found_path.endswith('.json'):
        try:
            data = json.loads(content)
            for m in data.keys():
                if 'unit' not in m.lower():
                    variables.append(m)
        except: pass
        
    res = []
    for v in variables:
        # Create a nice label if no translation exists
        label = translations.get(v)
        if not label:
            # Add spaces before capital letters
            spaced = re.sub(r"([A-Z])", r" \1", v)
            label = spaced.capitalize().replace("  ", " ").strip()
            
        res.append({"id": v, "label": label})
        
    return jsonify({"variables": res})

@app.route('/api/logs')
def stream_logs():
    def generate():
        if not os.path.exists(LOG_FILE):
            yield "Log file not found.\n"
            return
            
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            # Send the last 50 lines first
            lines = f.readlines()
            for line in lines[-50:]:
                yield line
                
            # Tail the file
            while True:
                where = f.tell()
                line = f.readline()
                if not line:
                    import time
                    time.sleep(1)
                    f.seek(where)
                else:
                    yield line
                    
    return app.response_class(generate(), mimetype='text/plain')
