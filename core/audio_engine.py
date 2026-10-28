import edge_tts
import asyncio
import io
import pygame
import logging
import time

def init_audio(device_name=None):
    """
    Initializes pygame mixer. 
    Can select a specific SDL audio device.
    """
    try:
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        
        if device_name and device_name != "Default":
            pygame.mixer.init(devicename=device_name)
            logging.info(f"Audio engine initialized with device: {device_name}")
        else:
            pygame.mixer.init()
            logging.info("Audio engine initialized with Default device.")
    except Exception as e:
        logging.error(f"Failed to init audio engine: {e}")

_edge_tts_checked = False

def reload_edge_tts():
    """Unloads and reloads edge_tts from disk into sys.modules."""
    import sys
    for mod in list(sys.modules.keys()):
        if mod == 'edge_tts' or mod.startswith('edge_tts.'):
            del sys.modules[mod]
    global edge_tts
    import edge_tts
    return edge_tts

def ensure_edge_tts_compat():
    """Checks if edge-tts is using outdated Sec-MS-GEC v1 tokens and updates if necessary."""
    global _edge_tts_checked
    if _edge_tts_checked:
        return
    _edge_tts_checked = True
    try:
        import edge_tts.constants
        sec_ver = getattr(edge_tts.constants, 'SEC_MS_GEC_VERSION', '')
        if sec_ver.startswith('1-'):
            logging.warning(f"Detected deprecated edge-tts (Sec-MS-GEC version {sec_ver}). Updating edge-tts to >=7.3.1...")
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "edge-tts>=7.3.1"], capture_output=True, timeout=60)
            logging.info("edge-tts update installed. Reloading module in memory...")
            reload_edge_tts()
            import edge_tts.constants
            new_ver = getattr(edge_tts.constants, 'SEC_MS_GEC_VERSION', 'unknown')
            logging.info(f"edge-tts reloaded successfully (Sec-MS-GEC version: {new_ver}).")
    except Exception as e:
        logging.debug(f"edge-tts compatibility check skipped: {e}")

async def _generate_audio_buffer(text, voice, rate):
    """
    Internal async function to generate audio with retries.
    Rate can be e.g. '+0%' or '+10%'.
    """
    last_error = None
    for attempt in range(2):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            audio_data = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
            if audio_data:
                return io.BytesIO(audio_data)
        except Exception as e:
            last_error = e
            logging.warning(f"TTS attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                await asyncio.sleep(1)
                
    raise last_error or Exception("No audio data generated")

def generate_and_play(text, settings, ptt_callback=None):
    """
    Generates TTS in-memory and plays it.
    ptt_callback is a function that takes a boolean (True to open, False to close PTT).
    """
    ensure_edge_tts_compat()
    voice = settings.get('tts_voice', 'en-US-AriaNeural')
    rate = f"{settings.get('tts_rate', 0):+d}%" # format as +10% or -10%
    volume = settings.get('audio_volume', 1.0)
    audio_device = settings.get('audio_device', 'Default')
    
    logging.info(f"Generating audio in memory (Voice: {voice}, Rate: {rate})")
    
    buffer = None
    try:
        buffer = asyncio.run(_generate_audio_buffer(text, voice, rate))
    except Exception as e:
        err_str = str(e)
        if "403" in err_str or "Invalid response status" in err_str:
            logging.error(f"Failed to generate TTS audio: {e}")
            logging.error("Microsoft Edge TTS rejected the request (403 Forbidden). Updating and reloading edge-tts in memory...")
            try:
                import subprocess, sys
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "edge-tts>=7.3.1"], capture_output=True, timeout=60)
                logging.info("Reloading edge-tts module into memory...")
                reload_edge_tts()
                try:
                    logging.info("Retrying audio generation with reloaded edge-tts...")
                    buffer = asyncio.run(_generate_audio_buffer(text, voice, rate))
                except Exception as retry_err:
                    logging.error(f"Retry after reload failed: {retry_err}. Please restart the beacon.")
                    return False
            except Exception as up_err:
                logging.error(f"Could not auto-upgrade edge-tts: {up_err}. Please run: pip install --upgrade edge-tts>=7.3.1")
                return False
        else:
            logging.error(f"Failed to generate TTS audio: {e}")
            return False

    if not buffer:
        logging.error("Failed to generate audio buffer.")
        return False
        
    init_audio(audio_device)
    
    try:
        # Load MP3 buffer
        pygame.mixer.music.load(buffer, 'mp3')
        pygame.mixer.music.set_volume(volume)
        
        # Trigger PTT Open
        if ptt_callback:
            ptt_callback(True)
            
        # Give transmitter a tiny delay to key up before talking
        time.sleep(0.5)
            
        logging.info("Starting audio playback...")
        pygame.mixer.music.play()
        
        # Block until audio finishes
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Trigger PTT Close
        if ptt_callback:
            # Small tail delay
            time.sleep(0.5)
            ptt_callback(False)
            
        logging.info("Audio playback completed.")
        return True
        
    except Exception as e:
        logging.error(f"Failed to play audio: {e}")
        if ptt_callback:
            ptt_callback(False)
        return False
