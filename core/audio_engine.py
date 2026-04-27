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

async def _generate_audio_buffer(text, voice, rate):
    """
    Internal async function to generate audio.
    Rate can be e.g. '+0%' or '+10%'.
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
    return io.BytesIO(audio_data)

def generate_and_play(text, settings, ptt_callback=None):
    """
    Generates TTS in-memory and plays it.
    ptt_callback is a function that takes a boolean (True to open, False to close PTT).
    """
    voice = settings.get('tts_voice', 'en-US-AriaNeural')
    rate = f"{settings.get('tts_rate', 0):+d}%" # format as +10% or -10%
    volume = settings.get('audio_volume', 1.0)
    audio_device = settings.get('audio_device', 'Default')
    
    logging.info(f"Generating audio in memory (Voice: {voice}, Rate: {rate})")
    
    try:
        buffer = asyncio.run(_generate_audio_buffer(text, voice, rate))
    except Exception as e:
        logging.error(f"Failed to generate TTS audio: {e}")
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
