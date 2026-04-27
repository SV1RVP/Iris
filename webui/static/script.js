document.addEventListener('DOMContentLoaded', () => {
    window.appSettings = {};
    window.lastPrimarySource = null;
    window.updateDynamicFrames = async function() {
        const primarySource = document.getElementById('primary_source').value;
        const secondarySource = document.getElementById('secondary_source').value;
        const envSource = document.getElementById('env_source').value;
        const swSource = document.getElementById('sw_source').value;

        const pwsPathGroup = document.getElementById('pws_path_group');
        const weatherModelGroup = document.getElementById('weather_model_group');
        const forecastModelGroup = document.getElementById('forecast_model_group');
        const envPathGroup = document.getElementById('env_path_group');

        const framePrimary = document.getElementById('frame_primary');
        const framePrimaryTitle = document.getElementById('frame_primary_title');
        const frameSecondary = document.getElementById('frame_secondary');
        const frameEnv = document.getElementById('frame_env');
        const frameSW = document.getElementById('frame_sw');
        const frameForecast = document.getElementById('frame_forecast');
        const forecastTarget = document.getElementById('forecast_target').value;

        if (primarySource !== 'off') {
            pwsPathGroup.style.display = 'block';
            framePrimary.style.display = 'block';
            
            const opt = document.querySelector(`#primary_source option[value="${primarySource}"]`);
            const title = opt ? opt.textContent : primarySource.toUpperCase();
            framePrimaryTitle.textContent = `Broadcast Parameters From ${title}`;
            
            // Fetch template variables only if source changed
            if (primarySource !== 'open_meteo' && primarySource !== window.lastPrimarySource) {
                window.lastPrimarySource = primarySource;
                try {
                    const res = await fetch(`/api/pws_template/${primarySource}`);
                    const data = await res.json();
                    const grid = document.querySelector('#frame_primary .sequence-grid');
                    if (data.variables && data.variables.length > 0) {
                        grid.innerHTML = '';
                        data.variables.forEach(v => {
                            const id = `seq_pws_${v.id}`;
                            const val = window.appSettings[id] || 0;
                            grid.innerHTML += `<label class="cb-label"><input type="number" min="0" value="${val}" class="seq-input" id="${id}"> ${v.label}</label>`;
                        });
                    }
                } catch (e) {
                    console.error("Failed to load PWS template:", e);
                }
            }
        } else {
            pwsPathGroup.style.display = 'none';
            framePrimary.style.display = 'none';
        }

        if (secondarySource === 'open_meteo') {
            weatherModelGroup.style.display = 'block';
            frameSecondary.style.display = 'block';
        } else {
            weatherModelGroup.style.display = 'none';
            frameSecondary.style.display = 'none';
        }

        if (envSource === 'on') {
            envPathGroup.style.display = 'block';
            frameEnv.style.display = 'block';
        } else {
            envPathGroup.style.display = 'none';
            frameEnv.style.display = 'none';
        }

        if (swSource === 'on') {
            frameSW.style.display = 'block';
        } else {
            frameSW.style.display = 'none';
        }

        if (forecastTarget !== 'OFF') {
            frameForecast.style.display = 'block';
            forecastModelGroup.style.display = 'block';
        } else {
            frameForecast.style.display = 'none';
            forecastModelGroup.style.display = 'none';
        }

        // Hide Broadcast Message Script if NO current sources are active
        const anyCurrentActive = (primarySource !== 'off' || secondarySource !== 'off' || envSource === 'on' || swSource === 'on');
        const scriptContainer = document.querySelector('.script-container');
        if (scriptContainer) {
            scriptContainer.style.display = anyCurrentActive ? 'block' : 'none';
        }
    };
    
    setTimeout(() => { if (window.updateDynamicFrames) window.updateDynamicFrames(); }, 100);

    // DOM Elements
    const form = document.getElementById('settings-form');
    const triggerBtn = document.getElementById('trigger-btn');
    const apiCountEl = document.getElementById('api-count');
    const terminalWindow = document.getElementById('terminal-window');
    
    const latInput = document.getElementById('latitude');
    const lonInput = document.getElementById('longitude');
    
    // Sliders
    const rateSlider = document.getElementById('tts_rate');
    const rateVal = document.getElementById('rate-val');
    const volSlider = document.getElementById('audio_volume');
    const volVal = document.getElementById('vol-val');
    
    rateSlider.addEventListener('input', (e) => {
        let val = e.target.value;
        rateVal.textContent = (val > 0 ? '+' : '') + val + '%';
    });
    
    volSlider.addEventListener('input', (e) => {
        volVal.textContent = Math.round(e.target.value * 100) + '%';
    });

    // Initialize Leaflet Map
    const map = L.map('map').setView([37.9838, 23.7275], 6); // Default Athens
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);
    
    let marker = L.marker([37.9838, 23.7275], { draggable: true }).addTo(map);
    
    function updateInputsFromMarker() {
        const pos = marker.getLatLng();
        latInput.value = pos.lat.toFixed(6);
        lonInput.value = pos.lng.toFixed(6);
    }
    
    marker.on('dragend', updateInputsFromMarker);
    
    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        updateInputsFromMarker();
    });

    // Fetch Audio Devices
    const audioSelect = document.getElementById('audio_device');
    fetch('/api/audio_devices')
        .then(res => res.json())
        .then(data => {
            data.devices.forEach(dev => {
                const opt = document.createElement('option');
                opt.value = dev;
                opt.textContent = dev;
                audioSelect.appendChild(opt);
            });
        });

    // Fetch COM Ports
    const pttPortSelect = document.getElementById('ptt_port');
    fetch('/api/com_ports')
        .then(res => res.json())
        .then(data => {
            data.ports.forEach(port => {
                const opt = document.createElement('option');
                opt.value = port;
                opt.textContent = port;
                pttPortSelect.appendChild(opt);
            });
        });

    // Locate Me
    document.getElementById('locate-btn').addEventListener('click', () => {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(position => {
                const latlng = new L.LatLng(position.coords.latitude, position.coords.longitude);
                marker.setLatLng(latlng);
                map.setView(latlng, 12);
                updateInputsFromMarker();
            }, error => {
                console.error("Geolocation error:", error);
                alert("Geolocation failed.\n\nNote: Browsers require an HTTPS connection to allow location access when the server is on a different machine. Please use the map to select your location manually.");
            });
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    });

    // Load Settings
    fetch('/api/settings')
        .then(res => res.json())
        .then(data => {
            if (Object.keys(data).length === 0) return;
            window.appSettings = data;
            
            // Map
            if (data.latitude && data.longitude) {
                const latlng = new L.LatLng(data.latitude, data.longitude);
                marker.setLatLng(latlng);
                map.setView(latlng, 10);
                latInput.value = data.latitude;
                lonInput.value = data.longitude;
            }
            
            // Text Inputs & Selects
            document.getElementById('schedule_interval').value = data.schedule_interval || 15;
            document.getElementById('ptt_pin').value = data.ptt_pin || 'RTS High';
            document.getElementById('tts_voice').value = data.tts_voice || 'en-US-AriaNeural';
            
            // Handle select values that might not be loaded yet
            setTimeout(() => {
                if (data.ptt_port) document.getElementById('ptt_port').value = data.ptt_port;
            }, 500);
            
            // New Settings
            if(data.primary_source) document.getElementById('primary_source').value = data.primary_source;
            if(data.secondary_source) document.getElementById('secondary_source').value = data.secondary_source;
            if(data.env_source) document.getElementById('env_source').value = data.env_source;
            if(data.env_path) document.getElementById('env_path').value = data.env_path;
            if(data.sw_source) document.getElementById('sw_source').value = data.sw_source;
            if(data.units) document.getElementById('units').value = data.units;
            if(data.pws_path) document.getElementById('pws_path').value = data.pws_path;
            if(data.weather_model) document.getElementById('weather_model').value = data.weather_model;
            if(data.forecast_target) document.getElementById('forecast_target').value = data.forecast_target;
            if(data.forecast_model) document.getElementById('forecast_model').value = data.forecast_model;
            if(data.forecast_prologue) document.getElementById('forecast_prologue').value = data.forecast_prologue;
            if(data.forecast_epilogue) document.getElementById('forecast_epilogue').value = data.forecast_epilogue;
            if(data.prologue) document.getElementById('prologue').value = data.prologue;
            if(data.epilogue) document.getElementById('epilogue').value = data.epilogue;
            
            // Need a slight delay to allow devices to load before setting value
            setTimeout(() => {
                if (data.audio_device) {
                    audioSelect.value = data.audio_device;
                }
            }, 500);
            
            // Sliders
            rateSlider.value = data.tts_rate || 0;
            rateVal.textContent = (data.tts_rate > 0 ? '+' : '') + (data.tts_rate || 0) + '%';
            
            volSlider.value = data.audio_volume !== undefined ? data.audio_volume : 1.0;
            volVal.textContent = Math.round((data.audio_volume !== undefined ? data.audio_volume : 1.0) * 100) + '%';
            
            // Checkboxes (only enable_beacon remains boolean)
            if (data.enable_beacon !== undefined) document.getElementById('enable_beacon').checked = data.enable_beacon;
            
            // Sequences
            const sequences = [
                'seq_secondary_weather_code', 'seq_secondary_temp', 'seq_secondary_apparent_temp', 'seq_secondary_humidity', 
                'seq_secondary_precipitation', 'seq_secondary_wind_speed', 'seq_secondary_wind_dir', 'seq_secondary_wind_gusts', 
                'seq_secondary_cloud_cover', 'seq_secondary_air_quality',
                
                'seq_env_temp', 'seq_env_humidity', 'seq_env_pressure',
                
                'seq_sw_noaa_g', 'seq_sw_noaa_s', 'seq_sw_noaa_r',

                'seq_forecast_weather_code', 'seq_forecast_temp', 'seq_forecast_apparent_temp', 'seq_forecast_precipitation', 
                'seq_forecast_precipitation_sum', 'seq_forecast_wind_speed', 'seq_forecast_wind_dir', 'seq_forecast_uv_index', 
                'seq_forecast_sunrise', 'seq_forecast_sunset'
            ];
            
            sequences.forEach(seq => {
                const el = document.getElementById(seq);
                if (el && data[seq] !== undefined) {
                    el.value = data[seq];
                }
            });
            
            if (window.updateDynamicFrames) window.updateDynamicFrames();
        });

    // Sync appSettings with live inputs
    form.addEventListener('input', (e) => {
        if (e.target.classList.contains('seq-input')) {
            window.appSettings[e.target.id] = parseInt(e.target.value) || 0;
        } else if (e.target.type === 'checkbox') {
            window.appSettings[e.target.id] = e.target.checked;
        } else {
            window.appSettings[e.target.id] = e.target.value;
        }
    });
        
    // Fetch Autostart Status
    fetch('/api/autostart')
        .then(res => res.json())
        .then(data => {
            if (data.enabled !== undefined) {
                document.getElementById('autostart').checked = data.enabled;
            }
        });

    // Save Settings
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const btn = form.querySelector('.btn-save');
        const originalText = btn.textContent;
        btn.textContent = "Saving...";
        
        const data = {
            latitude: parseFloat(latInput.value),
            longitude: parseFloat(lonInput.value),
            schedule_interval: parseInt(document.getElementById('schedule_interval').value),
            ptt_port: document.getElementById('ptt_port').value,
            ptt_pin: document.getElementById('ptt_pin').value,
            tts_voice: document.getElementById('tts_voice').value,
            audio_device: audioSelect.value,
            primary_source: document.getElementById('primary_source').value,
            secondary_source: document.getElementById('secondary_source').value,
            env_source: document.getElementById('env_source').value,
            env_path: document.getElementById('env_path').value,
            sw_source: document.getElementById('sw_source').value,
            units: document.getElementById('units').value,
            pws_path: document.getElementById('pws_path').value,
            weather_model: document.getElementById('weather_model').value,
            forecast_target: document.getElementById('forecast_target').value,
            forecast_model: document.getElementById('forecast_model').value,
            forecast_prologue: document.getElementById('forecast_prologue').value,
            forecast_epilogue: document.getElementById('forecast_epilogue').value,
            prologue: document.getElementById('prologue').value,
            epilogue: document.getElementById('epilogue').value,
            tts_rate: parseInt(rateSlider.value),
            audio_volume: parseFloat(volSlider.value),
            enable_beacon: document.getElementById('enable_beacon').checked
        };
        
        // Dynamically save all sequence inputs
        document.querySelectorAll('.seq-input').forEach(input => {
            data[input.id] = parseInt(input.value) || 0;
        });
        
        fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(() => {
            // Also save autostart
            const autostartEnabled = document.getElementById('autostart').checked;
            return fetch('/api/autostart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enable: autostartEnabled })
            });
        })
        .then(res => res.json())
        .then((autostartData) => {
            // Update window.appSettings with saved data
            window.appSettings = { ...window.appSettings, ...data };
            
            btn.textContent = "Saved!";
            btn.style.backgroundColor = "var(--success)";
            
            // Revert back after a bit
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.backgroundColor = "var(--accent)";
            }, 2000);
            
            if (autostartData && autostartData.success === false) {
                alert("Settings saved, but Autostart update failed:\n" + autostartData.message);
            }
        });
    });

    // Trigger Manual
    triggerBtn.addEventListener('click', () => {
        triggerBtn.disabled = true;
        fetch('/api/trigger', { method: 'POST' })
            .then(() => {
                setTimeout(() => triggerBtn.disabled = false, 5000);
            });
    });

    // Fetch Stats
    function updateStats() {
        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                apiCountEl.textContent = data.requests;
            });
    }
    
    updateStats();
    setInterval(updateStats, 60000); // every minute

    // Log Streaming via Server Sent Events equivalent (Fetch stream API)
    async function tailLogs() {
        while (true) {
            try {
                const response = await fetch('/api/logs');
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const text = decoder.decode(value);
                    const lines = text.split('\n');
                    
                    lines.forEach(line => {
                        if (line.trim() === '') return;
                        const div = document.createElement('div');
                        div.style.marginBottom = '2px';
                        div.style.paddingLeft = '5px';
                        
                        // Enhanced color coding and icons
                        if (line.includes('ERROR')) {
                            div.style.color = 'var(--danger)';
                            div.textContent = '❌ ' + line;
                        } else if (line.includes('WARNING')) {
                            div.style.color = '#fbbf24'; // Amber
                            div.textContent = '⚠️ ' + line;
                        } else if (line.includes('INFO')) {
                            div.style.color = 'var(--text-main)';
                            div.textContent = '🔹 ' + line;
                        } else {
                            div.textContent = line;
                        }
                        
                        terminalWindow.appendChild(div);

                        // Add a visual separator after broadcast completes
                        if (line.includes('--- Broadcast Complete ---')) {
                            const hr = document.createElement('div');
                            hr.style.height = '1px';
                            hr.style.background = 'linear-gradient(to right, transparent, var(--accent), transparent)';
                            hr.style.margin = '15px 0';
                            hr.style.opacity = '0.5';
                            terminalWindow.appendChild(hr);
                        }
                    });
                    
                    // Auto scroll
                    terminalWindow.scrollTop = terminalWindow.scrollHeight;
                }
            } catch (e) {
                console.warn("Log stream connection lost. Retrying in 5s...", e.message);
            }
            
            // Wait 5 seconds before retrying, regardless of success or failure
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
    
    tailLogs();

    // --- Update System Logic ---
    const updateBtn = document.getElementById('update-btn');
    const versionTag = document.getElementById('version-tag');
    const updateInfo = document.getElementById('update-info');
    let updateAvailable = false;

    async function checkUpdates(isManual = false) {
        if (isManual) {
            updateBtn.textContent = "...";
            updateBtn.disabled = true;
        }

        try {
            const res = await fetch('/api/update/status');
            const data = await res.json();

            if (data.status === 'success') {
                versionTag.textContent = 'v' + data.local_version;
                if (data.update_available) {
                    updateAvailable = true;
                    updateInfo.textContent = "update available";
                    updateInfo.style.color = "#f59e0b";
                    updateBtn.textContent = "Update";
                    updateBtn.classList.add('available');
                } else {
                    updateAvailable = false;
                    updateInfo.textContent = "up to date";
                    updateInfo.style.color = "var(--text-muted)";
                    updateBtn.textContent = "Check";
                    updateBtn.classList.remove('available');
                }
            }
        } catch (e) {
            console.error("Update check failed:", e);
        } finally {
            updateBtn.disabled = false;
        }
    }

    updateBtn.addEventListener('click', async () => {
        if (updateAvailable) {
            if (confirm("New updates are available. Apply now?\n\nThe dashboard will restart and reload.")) {
                console.log("Update initiated by user...");
                updateBtn.textContent = "Wait";
                updateBtn.classList.add('updating');
                updateBtn.disabled = true;
                
                try {
                    const res = await fetch('/api/update/perform', { method: 'POST' });
                    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                    
                    const data = await res.json();
                    if (data.success) {
                        alert(data.message);
                        console.log("Update success response:", data.message);
                        // Hard reload after 5s
                        setTimeout(() => window.location.reload(true), 5000);
                    } else {
                        throw new Error(data.message);
                    }
                } catch (e) {
                    console.error("Update process failed:", e);
                    alert("Update Error: " + e.message + "\n\nChecking Live Terminal for details...");
                    updateBtn.textContent = "Update";
                    updateBtn.disabled = false;
                    updateBtn.classList.remove('updating');
                }
            }
        } else {
            console.log("Manual update check triggered...");
            checkUpdates(true);
        }
    });

    // Check once on load
    setTimeout(checkUpdates, 1000);
});
