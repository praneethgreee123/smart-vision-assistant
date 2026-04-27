import pyttsx3
import threading

_tts_engine = None
_tts_lock = threading.Lock()

def init_tts(rate=180, volume=1.0, voice=None):
    """
    Initialize the text-to-speech engine.
    """
    global _tts_engine
    _tts_engine = pyttsx3.init()
    _tts_engine.setProperty("rate", rate)
    _tts_engine.setProperty("volume", volume)

    # Optional: choose a female or male voice
    voices = _tts_engine.getProperty("voices")
    if voice == "female" and len(voices) > 1:
        _tts_engine.setProperty("voice", voices[1].id)
    elif voice == "male":
        _tts_engine.setProperty("voice", voices[0].id)

def say(text):
    """
    Speak text using TTS in a background-safe way.
    """
    global _tts_engine
    if not _tts_engine:
        init_tts()

    def _speak():
        with _tts_lock:
            _tts_engine.say(text)
            _tts_engine.runAndWait()

    # Speak in a separate thread (non-blocking)
    t = threading.Thread(target=_speak, daemon=True)
    t.start()