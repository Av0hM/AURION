import pyttsx3
from memory.voice_logger import log_voice

engine = pyttsx3.init()

def speak(text, tone="neutral"):
    if not text:
        return

    # 🔊 LOG FIRST (backend truth)
    log_voice(text, tone)

    # 🎙 Voice parameters
    if tone in ["calm", "extra_calm", "gentle"]:
        engine.setProperty("rate", 120)
        engine.setProperty("volume", 0.6)
    elif tone in ["strict", "very_strict"]:
        engine.setProperty("rate", 190)
        engine.setProperty("volume", 1.0)
    elif tone == "hype":
        engine.setProperty("rate", 210)
        engine.setProperty("volume", 1.0)
    elif tone == "de_escalate":
        engine.setProperty("rate", 140)
        engine.setProperty("volume", 0.8)
    else:
        engine.setProperty("rate", 160)
        engine.setProperty("volume", 0.8)

    engine.say(text)
    engine.runAndWait()