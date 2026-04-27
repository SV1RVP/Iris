# Iris Meteo Beacon 📡🌤️

An advanced, open-source automated radio weather broadcast system designed for Amateur Radio (Ham Radio) and meteorological experimentation. It retrieves live environmental data, processes it into natural-sounding speech, and controls a radio transmitter via a Serial PTT interface.

**Creator:** Alexandros - Ermis Tsourapas (SV1RVP)  
**License:** GNU Affero General Public License v3.0 (AGPL-3.0)

> [!NOTE]
> **Cross-Platform Compatibility:** This application is fully OS-aware. It automatically detects whether it's running on **Windows** or **Linux/Raspberry Pi** and adjusts its behavior accordingly (e.g., paths, PTT handling, and Autostart logic).

---

## 🌟 Key Features

- **Dynamic Audio Sequencer:** Transform your beacon into a fully customizable broadcast. Use numeric ordering (1, 2, 3...) to define exactly which parameters are announced and in what order.
- **Dual-Period Announcement System:** The beacon automatically manages two distinct broadcast periods:
    1. **Current Conditions:** Detailed report from local or global data sources.
    2. **Weather Forecast:** A professional-grade daily forecast (Today or Tomorrow) with independent parameters.
- **Bilingual Speech Engine:** OS-aware and language-intelligent. The system automatically speaks the language matching your selected TTS voice (Greek or English) with optimized acoustics for more natural-sounding announcements.
- **Professional Linguistic Logic:** Instead of robotic sentences, the system uses an advanced text formatter that produces natural, professional weather reports. The Greek implementation has been specifically tuned for acoustic clarity and flow.
- **Multi-Software PWS Support:** Dynamic integration with major weather software including **Cumulus MX, Meteobridge, Weather Display, WeeWX, APRS,** and **Weather Link**. Supports flexible data parsing from both JSON and text-based templates.
- **Autonomous Forecast Module:** Fully decoupled from station data. It features independent model selection (ECMWF, GFS, ICON, etc.) and specific parameters like **UV Index, Wind Direction, Sunrise/Sunset, and Total Precipitation**.
- **Space Weather (NOAA):** Detailed reporting of Geomagnetic Storms (G-Scale), Solar Radiation Storms (S-Scale), and Radio Blackouts (R-Scale).
- **High-Precision Wind Tracking:** Upgraded wind direction reporting to a 16-point compass scale (22.5° intervals) for professional-grade accuracy.
- **Smart Unit Handling & Beaufort Scale:** Automatically appends correct units based on the measurement system (Metric/Imperial). In Metric mode, the system automatically calculates and announces the **Beaufort Scale** (1-12) for all wind measurements.
- **Intelligent Comfort Logic:** Smart filtering for comfort indices. **Heat Index** is only announced when the temperature exceeds 20°C and there is an upward difference, while **Wind Chill** is only announced when the temperature is below 19.9°C and there is a downward difference.
- **Smart Data Filtering:** Automatically suppresses irrelevant announcements, such as zero precipitation, zero cloud cover, or non-applicable comfort indices, to maintain a clean and professional broadcast flow.
- **Modern Dashboard:** A sleek, dark-themed WebUI with glassmorphism aesthetics, interactive Leaflet.js maps, and dedicated frames for each data source.
- **Enhanced State Reliability:** The WebUI features advanced state management to ensure user configurations are preserved during source switching and dynamic grid updates.
- **Precision Linguistic Filtering:** Improved voice logic to correctly handle wind direction units and avoid robotic repetition of units where they don't apply.
- **One-Click Automatic Updates:** Stay current with a single click. The beacon features a hybrid, folder-agnostic update system: uses `git` for seamless pulls on Linux and an intelligent ZIP-based replacement system for Windows (no Git required).
- **Remote Activity Terminal:** A real-time, color-coded Live Terminal integrated into the WebUI, providing full transparency into the beacon's internal processes, broadcast status, and update progress.
- **Fail-Safe Scheduler Resilience:** Enhanced broadcast timing with a 5-minute "grace period." This ensures that scheduled announcements are executed even if the application starts late or is temporarily offline during a trigger point.
- **Unified Autostart Logic:** OS-aware boot activation. The system now supports both `systemd` services (Linux) and Startup shortcuts (Windows), with real-time status detection in the WebUI.
- **Zero-Wear Performance:** Processes TTS audio entirely in-memory (RAM), ensuring zero SD card or disk wear—perfect for Raspberry Pi deployments.
- **Semantic Versioning:** Professional version tracking (vX.Y.Z) to easily monitor feature additions and bug fixes.
- **Default Silent Profile:** The system now ships with a "privacy-first" default configuration. All data sources and sequence parameters are deactivated (set to 0) by default, requiring intentional activation by the operator.
- **Flexible PTT Interface:** Enhanced serial control with automatic COM port detection and support for four trigger modes: **RTS High, RTS Low, DTR High, and DTR Low**. This ensures compatibility with any radio interface hardware.

---

## 🏗️ How it Works

1. **Weather Engine (`core/weather_engine.py`)**: A modular data aggregator. It fetches data from selected APIs or parses local PWS templates. It supports independent fetching for Current Conditions and Forecasts using different models if desired.
2. **Text Formatter (`core/text_formatter.py`)**: The "brain" of the beacon. It collects all active parameters (any sequence > 0), sorts them, and applies linguistic rules to build a cohesive paragraph for both Greek and English.
3. **Audio Engine (`core/audio_engine.py`)**: Streams TTS data from the cloud into a memory buffer and plays it via the system's audio output.
4. **PTT Controller (`core/ptt_controller.py`)**: Manages the hardware interface to the radio transmitter. Supports automatic port detection and four hardware trigger modes (RTS/DTR High/Low) for universal compatibility.
5. **Scheduler (`core/scheduler.py`)**: Manages the timing of broadcasts, alternating between Current Conditions and Forecasts.
6. **Updater (`core/updater.py`)**: A hybrid module that checks for new versions on GitLab and handles the update process (Git pull or ZIP override) across different operating systems.

---

## 🎧 Customizing the Sequencer

The Iris Meteo Beacon uses a numeric sequencing system.
- **Current Conditions:** Each data source (Primary, Secondary, Environment, Space Weather) has its own sequence order.
- **Weather Forecast:** This section has a **completely independent sequence order** and its own dedicated **Prologue (Intro)** and **Epilogue (Outro)** text fields.
- **Logic:** Enter a number greater than **0** to enable a parameter. Parameters are spoken in ascending order. Any parameter set to **0** is excluded.
- **Second Period:** The Forecast is always broadcast during the second announcement period to keep the transmission concise and organized.

---

## 🚀 Installation & Setup

### 🪟 Windows Setup (One-Click)
1. **Install Python:** Download and install [Python 3.10+](https://www.python.org/downloads/windows/). Make sure to check **"Add Python to PATH"** during installation.
2. **Download Code:** Download the repository as a ZIP and extract it into a folder (Recommendation: Name it `Iris-Meteo-Beacon`).
3. **Quick Install:** Double-click **`install-windows.bat`**. This will create the virtual environment and install all dependencies automatically.
4. **Run Application:** Double-click **`start_beacon.bat`**.
5. **Access Dashboard:** Open your browser and go to `http://localhost:1982`.

---

### 🐧 Linux (Universal Setup)
The Iris Meteo Beacon supports a wide variety of Linux distributions, including **Raspberry Pi OS, Debian, Ubuntu, Fedora, Arch Linux, openSUSE, and Alpine**.

1. **Clone & Access Folder:**
   ```bash
   git clone https://gitlab.com/SV1RVP/iris-meteo-beacon.git Iris-Meteo-Beacon
   cd Iris-Meteo-Beacon
   ```
2. **Quick Install:** Run the universal installer:
   ```bash
   chmod +x install-linux.sh
   ./install-linux.sh
   ```
   *The script automatically detects your distribution, installs the necessary dependencies, creates a `.venv`, and sets up the beacon as a background service (systemd).*
3. **Access Dashboard:** Open your browser and go to `http://<your-pi-ip>:1982`.
4. **Logs:** View live activity with: `sudo journalctl -u iris-meteo -f`

## 🗑️ Uninstallation

The Iris Meteo Beacon includes automated uninstaller scripts for a clean removal of all components, services, and configurations.

### 🪟 Windows Cleanup
1. Double-click **`uninstall-windows.bat`**.
2. Confirm with `y`.
*This will stop the process, remove the Startup shortcut, and delete the project folder.*

### 🍓 Linux Cleanup
1. Run the uninstaller:
   ```bash
   bash uninstall-linux.sh
   ```
2. Confirm with `y`.
*This will stop and remove the systemd service and delete the project folder.*

---

## 🤝 Contributing

We welcome contributions from the amateur radio community and developers! 
- **Bug Reports:** Open an issue on GitLab.
- **Feature Requests:** Share your ideas for new sensors or data models.
- **Development:** Feel free to fork the project and submit Merge Requests.

---

## ⚖️ Legal & Attributions

### Application Disclaimer
**This application does not generate or collect weather data; it only retrieves and broadcasts it.** Developed in the framework of amateur radio experimentation and the "Ham Spirit".

### Licensing Note
The source code of Iris Meteo Beacon is licensed under the **GNU AGPL v3**. However, the default Speech Synthesis engine relies on the Microsoft Edge-TTS API, which restricts usage strictly to **non-commercial, personal use**. If you intend to use this software for commercial broadcasting or business purposes, you must replace the TTS engine with a commercially compliant alternative to respect Microsoft's Terms of Service.

### Data & Technology Attributions
- **Weather Data:** Provided by [Open-Meteo.com](https://open-meteo.com/) under CC-BY 4.0.
- **Space Weather Data:** Provided by [NOAA Space Weather Prediction Center (SWPC)](https://www.swpc.noaa.gov/).
- **Map Data:** © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors.
- **Speech Synthesis:** Powered by Microsoft Edge-TTS technology for non-commercial, personal use.

---

*73 de SV1RVP*
