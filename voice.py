

# Only use _import_or_exit for simple imports
def _import_or_exit(module, pip_name=None):
    try:
        return __import__(module)
    except ImportError:
        pkg = pip_name if pip_name else module
        print(f"\n[ERROR] Required package '{pkg}' is not installed.\nPlease install it with: pip install {pkg}\n")
        exit(1)

try:
    from gtts import gTTS
except ImportError:
    print("\n[ERROR] Required package 'gTTS' is not installed.\nPlease install it with: pip install gTTS\n")
    exit(1)
try:
    from playsound import playsound
except ImportError:
    print("\n[ERROR] Required package 'playsound' is not installed.\nPlease install it with: pip install playsound\n")
    exit(1)
tempfile = _import_or_exit('tempfile')
threading = _import_or_exit('threading')
os = _import_or_exit('os')
time = _import_or_exit('time')

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

# Global voice lock to prevent overlapping
_voice_lock = threading.Lock()
_currently_speaking = False

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
    """Play in background without blocking, but ensure no overlap."""
    def _play():
        global _currently_speaking
        
        # Wait if another voice is playing
        with _voice_lock:
            if _currently_speaking:
                print(f"[Voice] Skipping - already speaking: {text}")
                return
            _currently_speaking = True
            
        try:
            path = _save_tts(text)
            playsound(path)
        except Exception as e:
            print(f"[Voice] Async error: {e}")
        finally:
            # Always release the lock
            with _voice_lock:
                _currently_speaking = False
                
    threading.Thread(target=_play, daemon=True).start()

def speak_sync(text):
    """Play and wait (blocking), with overlap protection."""
    global _currently_speaking
    
    with _voice_lock:
        if _currently_speaking:
            print(f"[Voice] Skipping sync - already speaking: {text}")
            return
        _currently_speaking = True
        
    try:
        path = _save_tts(text)
        playsound(path)
    except Exception as e:
        print(f"[Voice] Sync error: {e}")
    finally:
        with _voice_lock:
            _currently_speaking = False

def speak_event(key, text, sync=False):
    """Speak only if cooldown passed for this event AND no other voice is playing."""
    now = time.time()
    
    # Check cooldown first
    if now - last_prompt_time.get(key, 0) <= PROMPT_COOLDOWN.get(key, 0):
        return
        
    # Check if already speaking (additional protection)
    with _voice_lock:
        if _currently_speaking:
            print(f"[Voice] Skipping event - already speaking: {text}")
            return
    
    if sync:
        speak_sync(text)
    else:
        speak_async(text)
    last_prompt_time[key] = now