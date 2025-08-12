# voice.py
from gtts import gTTS
from playsound import playsound
import tempfile
import threading
import os
import time

# Cache for repeated phrases
_voice_cache = {}

# Cooldown tracking
last_prompt_time = {
    "face_detected": 0,
    "remove_accessory": 0,
    "scan_complete_threat": 0,
    "scan_complete_safe": 0,
    "camera_start": 0
}

PROMPT_COOLDOWN = {
    "face_detected": 15,
    "remove_accessory": 8,
    "scan_complete_threat": 5,
    "scan_complete_safe": 5,
    "camera_start": 60
}

def _save_tts(text):
    """Generate TTS file once and return its path."""
    if text in _voice_cache:
        return _voice_cache[text]
    tts = gTTS(text=text, lang='en')
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    _voice_cache[text] = tmp_file.name
    return tmp_file.name

def speak_async(text):
    """Play in background without blocking."""
    def _play():
        try:
            path = _save_tts(text)
            playsound(path)
        except Exception as e:
            print(f"[Voice] Async error: {e}")
    threading.Thread(target=_play, daemon=True).start()

def speak_sync(text):
    """Play and wait (blocking)."""
    try:
        path = _save_tts(text)
        playsound(path)
    except Exception as e:
        print(f"[Voice] Sync error: {e}")

def speak_event(key, text, sync=False):
    """Speak only if cooldown passed for this event."""
    now = time.time()
    if now - last_prompt_time.get(key, 0) > PROMPT_COOLDOWN.get(key, 0):
        if sync:
            speak_sync(text)
        else:
            speak_async(text)
        last_prompt_time[key] = now
        