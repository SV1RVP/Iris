def get_wmo_description(code, is_greek=False):
    wmo_codes_en = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    
    wmo_codes_gr = {
        0: "Καθαρός ουρανός",
        1: "Κυρίως αίθριος καιρός", 2: "Μερική συννεφιά", 3: "Νεφώσεις",
        45: "Ομίχλη", 48: "Πυκνή ομίχλη",
        51: "Ελαφριά ψιχάλα", 53: "Μέτρια ψιχάλα", 55: "Πυκνή ψιχάλα",
        56: "Ελαφριά παγωμένη ψιχάλα", 57: "Πυκνή παγωμένη ψιχάλα",
        61: "Ελαφριά βροχή", 63: "Μέτρια βροχή", 65: "Δυνατή βροχή",
        66: "Ελαφριά παγωμένη βροχή", 67: "Δυνατή παγωμένη βροχή",
        71: "Ελαφριά χιονόπτωση", 73: "Μέτρια χιονόπτωση", 75: "Πυκνή χιονόπτωση",
        77: "Χιονόνερο",
        80: "Ελαφρές μπόρες", 81: "Μέτριες μπόρες", 82: "Δυνατές μπόρες",
        85: "Ελαφρές χιονοπτώσεις", 86: "Δυνατές χιονοπτώσεις",
        95: "Καταιγίδα",
        96: "Καταιγίδα με ψιλό χαλάζι", 99: "Καταιγίδα με χοντρό χαλάζι"
    }
    
    if is_greek:
        return wmo_codes_gr.get(code, "Άγνωστες συνθήκες")
    return wmo_codes_en.get(code, "Unknown conditions")

def format_number(val, is_greek=False):
    try:
        f_val = float(val)
        if f_val == int(f_val):
            return str(int(f_val))
        if is_greek:
            return str(f_val).replace(".", " κόμμα ")
        return str(f_val)
    except:
        return str(val)

def get_beaufort(speed, units='metric'):
    try:
        # Convert mph to kmh if needed
        kmh = float(speed) * 1.60934 if units == 'imperial' else float(speed)
        if kmh < 1: return 0
        elif kmh <= 5: return 1
        elif kmh <= 11: return 2
        elif kmh <= 19: return 3
        elif kmh <= 28: return 4
        elif kmh <= 38: return 5
        elif kmh <= 49: return 6
        elif kmh <= 61: return 7
        elif kmh <= 74: return 8
        elif kmh <= 88: return 9
        elif kmh <= 102: return 10
        elif kmh <= 117: return 11
        else: return 12
    except: return 0

def get_wind_direction(deg, is_greek=False, plural=False):
    try:
        if is_greek:
            if plural:
                dirs = [
                    "βόρειες", "βόρειες βορειοανατολικές", "βορειοανατολικές", "ανατολικές βορειοανατολικές",
                    "ανατολικές", "ανατολικές νοτιοανατολικές", "νοτιοανατολικές", "νότιες νοτιοανατολικές",
                    "νότιες", "νότιες νοτιοδυτικές", "νοτιοδυτικές", "δυτικές νοτιοδυτικές",
                    "δυτικές", "δυτικές βορειοδυτικές", "βορειοδυτικές", "βόρειες βορειοδυτικές"
                ]
            else:
                dirs = [
                    "Βόρειος", "Βόρειος Βορειοανατολικός", "Βορειοανατολικός", "Ανατολικός Βορειοανατολικός",
                    "Ανατολικός", "Ανατολικός Νοτιοανατολικός", "Νοτιοανατολικός", "Νότιος Νοτιοανατολικός",
                    "Νότιος", "Νότιος Νοτιοδυτικός", "Νοτιοδυτικός", "Δυτικός Νοτιοδυτικός",
                    "Δυτικός", "Δυτικός Βορειοδυτικός", "Βορειοδυτικός", "Βόρειος Βορειοδυτικός"
                ]
        else:
            dirs = [
                "North", "North-North-East", "North-East", "East-North-East",
                "East", "East-South-East", "South-East", "South-South-East",
                "South", "South-South-West", "South-West", "West-South-West",
                "West", "West-North-West", "North-West", "North-North-West"
            ]
            
        idx = round(float(deg) / 22.5) % 16
        return dirs[idx]
    except:
        return "άγνωστη" if is_greek else "unknown"

def get_wind_direction_from_str(s, is_greek=False, plural=False):
    compass_map = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
    }
    s_upper = s.upper().strip().replace('"', '').replace("'", "")
    if s_upper in compass_map:
        return get_wind_direction(compass_map[s_upper], is_greek, plural)
    return s

def generate_weather_text(data, settings, is_forecast=False):
    """
    Generates the TTS string based on sequenced inputs.
    is_forecast toggles between Current Weather (False) and Forecast (True).
    """
    voice = settings.get('tts_voice', 'en-US-AriaNeural')
    is_greek = 'el-GR' in voice
    units = settings.get('units', 'metric')
    
    t_unit = "Φαρενάιτ" if units == 'imperial' else "Κελσίου"
    t_unit_en = "Fahrenheit" if units == 'imperial' else "Celsius"
    
    speed_unit = "μίλια" if units == 'imperial' else "χιλιόμετρα"
    speed_unit_en = "miles" if units == 'imperial' else "kilometers"
    
    precip_unit = "ίντσες" if units == 'imperial' else "χιλιοστά"
    precip_unit_en = "inches" if units == 'imperial' else "millimeters"
    
    if not data:
        return "Δεν υπάρχουν διαθέσιμα μετεωρολογικά δεδομένα." if is_greek else "Weather data is currently unavailable."
        
    sequenced_parts = []
    
    def add_part(seq_key, text):
        try:
            seq = int(settings.get(seq_key, 0))
            if seq > 0 and text:
                sequenced_parts.append((seq, text))
        except (ValueError, TypeError):
            pass

    def process_current(source_key, prefix):
        src_data = data.get(source_key)
        if not src_data: return
        current = src_data.get('current', {})
        # Continue if we have current data OR raw_pws data
        if not current and not src_data.get('raw_pws'): return
        
        # Weather Code
        if current.get('weather_code') is not None:
            desc = get_wmo_description(current['weather_code'], is_greek)
            text = f"Αυτή τη στιγμή επικρατεί {desc.lower()}." if is_greek else f"Conditions are {desc}."
            add_part(f'seq_{prefix}_weather_code', text)
            
        # Temperature & Apparent
        if current.get('temperature_2m') is not None:
            raw_t = float(current['temperature_2m'])
            temp = format_number(raw_t, is_greek)
            if prefix == 'env':
                text_temp = f"Η θερμοκρασία περιβάλλοντος είναι {temp} βαθμοί {t_unit}." if is_greek else f"Environment temperature is {temp} degrees {t_unit_en}."
            else:
                text_temp = f"Η θερμοκρασία ανέρχεται στους {temp} βαθμούς {t_unit}." if is_greek else f"Temperature is {temp} degrees {t_unit_en}."
            add_part(f'seq_{prefix}_temp', text_temp)
            
            if current.get('apparent_temperature') is not None:
                raw_app = float(current['apparent_temperature'])
                app_temp = format_number(raw_app, is_greek)
                threshold = 68 if units == 'imperial' else 20
                if raw_t >= threshold:
                    text_app = f"Ο δείκτης δυσφορίας βρίσκεται στους {app_temp} βαθμούς {t_unit}." if is_greek else f"Heat index is {app_temp} degrees {t_unit_en}."
                else:
                    text_app = f"Η αίσθηση ψύχους αγγίζει τους {app_temp} βαθμούς {t_unit}." if is_greek else f"Wind chill is {app_temp} degrees {t_unit_en}."
                add_part(f'seq_{prefix}_apparent_temp', text_app)
            
        # Humidity
        if current.get('relative_humidity_2m') is not None:
            hum = format_number(current['relative_humidity_2m'], is_greek)
            if prefix == 'env':
                text_hum = f"Η υγρασία περιβάλλοντος είναι {hum} τοις εκατό." if is_greek else f"Environment humidity is {hum} percent."
            else:
                text_hum = f"Η υγρασία στην ατμόσφαιρα ανέρχεται στο {hum} τοις εκατό." if is_greek else f"Relative humidity is {hum} percent."
            add_part(f'seq_{prefix}_humidity', text_hum)
            
        # Pressure
        if prefix == 'env' and current.get('surface_pressure') is not None:
            press = format_number(current['surface_pressure'], is_greek)
            text_press = f"Η ατμοσφαιρική πίεση είναι {press}." if is_greek else f"Atmospheric pressure is {press}."
            add_part(f'seq_{prefix}_pressure', text_press)
            
        # Precipitation
        if current.get('precipitation') is not None:
            precip = current['precipitation']
            if float(precip) > 0:
                p_val = format_number(precip, is_greek)
                text = f"Σχετικά με τον υετό, έχει καταγραφεί βροχόπτωση {p_val} {precip_unit}." if is_greek else f"Precipitation is {p_val} {precip_unit_en}."
                add_part(f'seq_{prefix}_precipitation', text)
                
        # Wind Speed
        if current.get('wind_speed_10m') is not None:
            w_speed = current['wind_speed_10m']
            bft = get_beaufort(w_speed, units)
            f_speed = format_number(w_speed, is_greek)
            text_wind = f"Η ένταση του ανέμου είναι στα {bft} Μποφόρ, στα {f_speed} {speed_unit} ανά ώρα." if is_greek else f"Wind speed is force {bft} Beaufort, or {f_speed} {speed_unit_en} per hour."
            add_part(f'seq_{prefix}_wind_speed', text_wind)
            
        # Wind Dir
        if current.get('wind_direction_10m') is not None:
            w_dir = current['wind_direction_10m']
            dir_text = get_wind_direction(w_dir, is_greek)
            deg = format_number(w_dir, is_greek)
            text_dir = f"Ο άνεμος έχει διεύθυνση {dir_text.lower()}, στις {deg} μοίρες." if is_greek else f"Wind direction is {dir_text} at {deg} degrees."
            add_part(f'seq_{prefix}_wind_dir', text_dir)
                
        # Wind Gusts
        if current.get('wind_gusts_10m') is not None and current.get('wind_speed_10m') is not None:
            gusts = current['wind_gusts_10m']
            if float(gusts) > float(current['wind_speed_10m']) + 5:
                gbft = get_beaufort(gusts, units)
                f_gusts = format_number(gusts, is_greek)
                text_gusts = f"Οι ριπές του ανέμου φτάνουν τα {gbft} Μποφόρ, στα {f_gusts} {speed_unit} ανά ώρα." if is_greek else f"Wind gusts reach force {gbft} Beaufort, or {f_gusts} {speed_unit_en} per hour."
                add_part(f'seq_{prefix}_wind_gusts', text_gusts)
            
        # Cloud Cover
        if current.get('cloud_cover') is not None:
            try:
                if float(current['cloud_cover']) > 0:
                    cc = format_number(current['cloud_cover'], is_greek)
                    text = f"Η νεφοκάλυψη είναι στο {cc} τοις εκατό." if is_greek else f"Cloud cover is {cc} percent."
                    add_part(f'seq_{prefix}_cloud_cover', text)
            except: pass
            
        # Air Quality
        if current.get('air_quality') is not None:
            aqi = format_number(current['air_quality'], is_greek)
            text = f"Ο ευρωπαϊκός δείκτης ποιότητας αέρα είναι στο {aqi}." if is_greek else f"European Air Quality Index is {aqi}."
            add_part(f'seq_{prefix}_air_quality', text)

        # Dynamic PWS Variables
        if prefix == 'primary' and 'raw_pws' in src_data:
            import re
            import os, json
            
            # Load translations based on voice language
            translations = {}
            trans_file = 'translations_el.json' if is_greek else 'translations.json'
            trans_path = os.path.join('core', 'pws_templates', trans_file)
            if os.path.exists(trans_path):
                try:
                    with open(trans_path, 'r', encoding='utf-8') as f:
                        translations = json.load(f)
                except: pass
                
            for k, seq_val in settings.items():
                if k.startswith('seq_pws_'):
                    try:
                        seq = int(seq_val)
                        if seq > 0:
                            var_name = k.replace('seq_pws_', '')
                            v_lower = var_name.lower()
                            val = src_data['raw_pws'].get(var_name)
                            if val is not None and str(val).strip():
                                # Strip degree symbol and non-ascii placeholders if present
                                val_clean = str(val).replace('°', '').replace('', '').strip()

                                # Heat Index / Wind Chill Logic
                                if 'heatindex' in v_lower or 'windchill' in v_lower:
                                    curr_temp_val = None
                                    for t_key in ['outsideTemp', 'temp', 'th0temp', 'outTemp']:
                                        if t_key in src_data['raw_pws']:
                                            try:
                                                curr_temp_val = float(str(src_data['raw_pws'][t_key]).replace('°', '').replace('', '').strip())
                                                break
                                            except: continue
                                    
                                    if curr_temp_val is not None:
                                        try:
                                            this_val = float(val_clean)
                                            if 'heatindex' in v_lower:
                                                if not (curr_temp_val > 20 and this_val > curr_temp_val):
                                                    continue
                                            elif 'windchill' in v_lower:
                                                if not (curr_temp_val < 19.9 and this_val < curr_temp_val):
                                                    continue
                                        except: pass

                                # Skip rain/cloud if 0
                                if any(x in var_name.lower() for x in ['rain', 'precip', 'fall', 'cloud']):
                                    try:
                                        if float(val_clean) == 0:
                                            continue
                                    except: pass

                                # Try translation first
                                label = translations.get(var_name)
                                if not label:
                                    spaced = re.sub(r"([A-Z])", r" \1", var_name)
                                    label = spaced.capitalize().replace("  ", " ").strip()
                                val_fmt = format_number(val_clean, is_greek)
                                
                                # Special handling for Wind Direction strings
                                if any(x in var_name.lower() for x in ['dir', 'wdir', 'direction']):
                                    try:
                                        float(val_clean)
                                    except (ValueError, TypeError):
                                        val_fmt = get_wind_direction_from_str(val_clean, is_greek)
                                
                                # Automatic Unit Detection
                                unit_suffix = ""
                                v_lower = var_name.lower()
                                if any(x in v_lower for x in ['temp', 'dewpt', 'heatindex', 'windchill']):
                                    unit_suffix = f" βαθμούς {t_unit}" if is_greek else f" degrees {t_unit_en}"
                                elif 'hum' in v_lower:
                                    unit_suffix = " τοις εκατό" if is_greek else " percent"
                                elif any(x in v_lower for x in ['speed', 'gust', 'avg', 'spd']) or ('wind' in v_lower and not any(y in v_lower for y in ['dir', 'direction'])):
                                    unit_suffix = f" {speed_unit} ανά ώρα" if is_greek else f" {speed_unit_en} per hour"
                                    if units == 'metric':
                                        bft = get_beaufort(val_clean, units)
                                        if bft > 0:
                                            if is_greek:
                                                prep = "Στο" if bft == 1 else "Στα"
                                                unit_suffix += f", {prep} {bft} Μποφόρ"
                                            else:
                                                unit_suffix += f", force {bft} Beaufort"
                                elif any(x in v_lower for x in ['rain', 'precip']):
                                    unit_suffix = f" {precip_unit}" if is_greek else f" {precip_unit_en}"
                                elif any(x in v_lower for x in ['barometer', 'pressure']):
                                    unit_suffix = " hPa" # Standard for weather stations, usually
                                elif any(x in v_lower for x in ['moires', 'degrees']):
                                    unit_suffix = " μοίρες" if is_greek else " degrees"
                                elif 'solarrad' in v_lower:
                                    unit_suffix = " Watt ανά τετραγωνικό μέτρο" if is_greek else " Watts per square meter"
                                
                                punctuation = "," if any(x in var_name.lower() for x in ['dir', 'wdir', 'direction']) and not any(x in var_name.lower() for x in ['degree', 'moires']) else "."
                                separator = ": " if not label.endswith(" ") else ""
                                text = f"{label}{separator}{val_fmt}{unit_suffix}{punctuation}"
                                add_part(k, text)
                    except (ValueError, TypeError):
                        pass

    if not is_forecast:
        if settings.get('primary_source', 'off') != 'off':
            process_current('primary', 'primary')
        if settings.get('secondary_source', 'off') != 'off':
            process_current('secondary', 'secondary')
        if settings.get('env_source', 'off') != 'off':
            process_current('env', 'env')
        
        # Space Weather
        sw = data.get('sw')
        if sw and settings.get('sw_source', 'off') == 'on':
            scale_map_gr = {1: "Χαμηλή", 2: "Μέτρια", 3: "Υψηλή", 4: "Πολύ Υψηλή", 5: "Κατάσταση συναγερμού"}
            scale_map_en = {1: "Minor", 2: "Moderate", 3: "Strong", 4: "Severe", 5: "Extreme"}
            
            g = sw.get('G', 0)
            if 1 <= g <= 5:
                val = scale_map_gr[g] if is_greek else scale_map_en[g]
                text = f"Γεωμαγνητική καταιγίδα G{g}, {val}." if is_greek else f"Geomagnetic storm G{g}, {val}."
                add_part('seq_sw_noaa_g', text)
                
            s = sw.get('S', 0)
            if 1 <= s <= 5:
                val = scale_map_gr[s] if is_greek else scale_map_en[s]
                text = f"Ηλιακή καταιγίδα ακτινοβολίας S{s}, {val}." if is_greek else f"Solar radiation storm S{s}, {val}."
                add_part('seq_sw_noaa_s', text)
                
            r = sw.get('R', 0)
            if 1 <= r <= 5:
                val = scale_map_gr[r] if is_greek else scale_map_en[r]
                text = f"Διακοπές ραδιοεπικοινωνιών R{r}, {val}." if is_greek else f"Radio blackouts R{r}, {val}."
                add_part('seq_sw_noaa_r', text)

    else:
        # --- Forecast Day ---
        forecast_target = settings.get('forecast_target', 'OFF')
        if forecast_target != 'OFF':
            day_idx = 0 if forecast_target == 'today' else 1
            
            sec_data = data.get('secondary')
            if sec_data:
                daily = sec_data.get('daily', {})
                if daily and 'time' in daily and len(daily['time']) > day_idx:
                    # Data Extraction (Rounded to integers for Forecast)
                    cond = get_wmo_description(daily['weather_code'][day_idx], is_greek) if daily.get('weather_code') and daily['weather_code'][day_idx] is not None else None
                    t_max = format_number(int(round(float(daily['temperature_2m_max'][day_idx]))), is_greek) if daily.get('temperature_2m_max') and daily['temperature_2m_max'][day_idx] is not None else None
                    t_min = format_number(int(round(float(daily['temperature_2m_min'][day_idx]))), is_greek) if daily.get('temperature_2m_min') and daily['temperature_2m_min'][day_idx] is not None else None
                    a_max = format_number(int(round(float(daily['apparent_temperature_max'][day_idx]))), is_greek) if daily.get('apparent_temperature_max') and daily['apparent_temperature_max'][day_idx] is not None else None
                    a_min = format_number(int(round(float(daily['apparent_temperature_min'][day_idx]))), is_greek) if daily.get('apparent_temperature_min') and daily['apparent_temperature_min'][day_idx] is not None else None
                    pprob = format_number(int(round(float(daily['precipitation_probability_max'][day_idx]))), is_greek) if daily.get('precipitation_probability_max') and daily['precipitation_probability_max'][day_idx] is not None else None
                    psum = format_number(int(round(float(daily['precipitation_sum'][day_idx]))), is_greek) if daily.get('precipitation_sum') and daily['precipitation_sum'][day_idx] is not None else None
                    wmax = format_number(int(round(float(daily['wind_speed_10m_max'][day_idx]))), is_greek) if daily.get('wind_speed_10m_max') and daily['wind_speed_10m_max'][day_idx] is not None else None
                    wdir = get_wind_direction(daily['wind_direction_10m_dominant'][day_idx], is_greek, plural=True) if daily.get('wind_direction_10m_dominant') and daily['wind_direction_10m_dominant'][day_idx] is not None else None
                    uv = format_number(int(round(float(daily['uv_index_max'][day_idx]))), is_greek) if daily.get('uv_index_max') and daily['uv_index_max'][day_idx] is not None else None
                    stime = daily['sunrise'][day_idx].split('T')[1] if daily.get('sunrise') and daily['sunrise'][day_idx] else None
                    etime = daily['sunset'][day_idx].split('T')[1] if daily.get('sunset') and daily['sunset'][day_idx] else None

                    # Phrase Building (Greek)
                    if is_greek:
                        # Part 1: Intro + Conditions + Precip
                        p1 = f"Για {forecast_target.replace('today','σήμερα').replace('tomorrow','αύριο')} προβλέπονται {cond.lower()}" if cond else f"Για {forecast_target.replace('today','σήμερα').replace('tomorrow','αύριο')} προβλέπεται ότι"
                        if int(settings.get('seq_forecast_precipitation', 0)) > 0 and pprob:
                            p1 += f" με την πιθανότητα βροχής να περιορίζεται στο {pprob}%"
                        
                        # Part 2: Temperature
                        p2 = ""
                        if int(settings.get('seq_forecast_temp', 0)) > 0 and t_max and t_min:
                            p2 = f"Η θερμοκρασία θα κυμανθεί από τους {t_min} έως τους {t_max} βαθμούς {t_unit}"
                            if int(settings.get('seq_forecast_apparent_temp', 0)) > 0 and a_max and a_min:
                                p2 += f", με την πραγματική αίσθηση να διαμορφώνεται μεταξύ {a_min} και {a_max} βαθμών."
                            else:
                                p2 += "."
                        
                        # Part 3: Winds
                        p3 = ""
                        if int(settings.get('seq_forecast_wind_speed', 0)) > 0 and wmax:
                            p3 = f"Οι άνεμοι θα πνέουν"
                            if int(settings.get('seq_forecast_wind_dir', 0)) > 0 and wdir:
                                p3 += f" από {wdir.lower()} διευθύνσεις"
                            p3 += f" με την ταχύτητά τους να αγγίζει τα {wmax} {speed_unit} την ώρα."
                        
                        # Part 4: UV & Sun
                        p4_parts = []
                        if int(settings.get('seq_forecast_uv_index', 0)) > 0 and uv:
                            p4_parts.append(f"ο δείκτης υπεριώδους ακτινοβολίας θα φτάσει το {uv}")
                        if int(settings.get('seq_forecast_sunrise', 0)) > 0 and stime:
                            p4_parts.append(f"η ανατολή του ηλίου θα γίνει στις {stime}")
                        if int(settings.get('seq_forecast_sunset', 0)) > 0 and etime:
                            p4_parts.append(f"η δύση του ηλίου θα γίνει στις {etime}")
                        
                        p4 = ""
                        if p4_parts:
                            p4 = "Παράλληλα, " + ", ενώ ".join(p4_parts) + "."

                        # Combine with proper spacing and punctuation
                        forecast_text = f"{p1}. {p2} {p3} {p4}".replace("  ", " ").replace(" .", ".").replace("..", ".").strip()
                    
                    # Phrase Building (English)
                    else:
                        # Part 1: Intro + Conditions + Precip
                        p1 = f"For {forecast_target}, {cond.lower()} are forecast" if cond else f"For {forecast_target},"
                        if int(settings.get('seq_forecast_precipitation', 0)) > 0 and pprob:
                            p1 += f" with the chance of rain limited to {pprob}%"
                        
                        # Part 2: Temperature
                        p2 = ""
                        if int(settings.get('seq_forecast_temp', 0)) > 0 and t_max and t_min:
                            p2 = f"The temperature will range from {t_min} to {t_max} degrees {t_unit_en}"
                            if int(settings.get('seq_forecast_apparent_temp', 0)) > 0 and a_max and a_min:
                                p2 += f", with the apparent temperature between {a_min} and {a_max} degrees."
                            else:
                                p2 += "."
                        
                        # Part 3: Winds
                        p3 = ""
                        if int(settings.get('seq_forecast_wind_speed', 0)) > 0 and wmax:
                            p3 = f"Winds will blow"
                            if int(settings.get('seq_forecast_wind_dir', 0)) > 0 and wdir:
                                p3 += f" from {wdir.lower()} directions"
                            p3 += f" with speeds reaching {wmax} {speed_unit_en} per hour."

                        # Part 4: UV & Sun
                        p4_parts = []
                        if int(settings.get('seq_forecast_uv_index', 0)) > 0 and uv:
                            p4_parts.append(f"the UV index will reach {uv}")
                        if int(settings.get('seq_forecast_sunrise', 0)) > 0 and stime:
                            p4_parts.append(f"sunrise will be at {stime}")
                        if int(settings.get('seq_forecast_sunset', 0)) > 0 and etime:
                            p4_parts.append(f"sunset will be at {etime}")
                        
                        p4 = ""
                        if p4_parts:
                            p4 = "Additionally, " + ", while ".join(p4_parts) + "."

                        # Combine with proper spacing and punctuation
                        forecast_text = f"{p1}. {p2} {p3} {p4}".replace("  ", " ").replace(" .", ".").replace("..", ".").strip()
                    
                    # Add Forecast Prologue/Epilogue
                    f_prologue = settings.get('forecast_prologue', '').strip()
                    f_epilogue = settings.get('forecast_epilogue', '').strip()
                    
                    full_forecast = ""
                    if f_prologue: full_forecast += f_prologue + " "
                    full_forecast += forecast_text
                    if f_epilogue: full_forecast += " " + f_epilogue
                    
                    sequenced_parts.append((10, full_forecast.strip()))

    # Sort parts by sequence
    sequenced_parts.sort(key=lambda x: x[0])
    
    final_parts = []
    
    # Prologue
    if not is_forecast:
        prologue = settings.get('prologue', '').strip()
        if prologue:
            final_parts.append(prologue)
            
    # Add sequenced text
    for seq, text in sequenced_parts:
        final_parts.append(text)
        
    # Epilogue
    if not is_forecast:
        epilogue = settings.get('epilogue', '').strip()
        if epilogue:
            final_parts.append(epilogue)
            
    return " ".join(final_parts)
