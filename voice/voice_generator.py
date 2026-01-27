import google.generativeai as genai
import os
import time
from memory.memory_summary import get_memory_context

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3-flash-preview")

_last_spoken = 0

def can_speak(cooldown=10):
    global _last_spoken
    now = time.time()
    if now - _last_spoken > cooldown:
        _last_spoken = now
        return True
    return False


# ================== TONE ENGINE ==================

def get_tone(state, user_traits=None):
    discipline = 0.5
    stress_prone = 0.5

    if user_traits:
        discipline = user_traits.get("discipline", 0.5)
        stress_prone = user_traits.get("stress_prone", 0.5)

    if state in ["CRYING", "STRESSED"]:
        tone = "calm"
    elif state == "ANGRY":
        tone = "de_escalate"
    elif state == "PROCRASTINATING":
        tone = "strict"
    elif state == "TIRED":
        tone = "gentle"
    elif state == "VICTORY":
        tone = "hype"
    elif state == "DEEP_WORK":
        tone = "silent"
    else:
        tone = "neutral"

    if tone == "strict":
        if discipline < 0.3:
            tone = "very_strict"
        elif discipline < 0.5:
            tone = "strict"
        else:
            tone = "soft_strict"

    if stress_prone > 0.7:
        tone = "extra_calm"

    # 🔒 safety: only DEEP_WORK can be silent
    if tone == "silent" and state != "DEEP_WORK":
        tone = "calm"

    return tone


# ================== PROMPTS ==================

VOICE_SYSTEM_PROMPT = """
You are Omni, an intelligent AI companion observing a user's behaviour in real time.

You speak like a calm, human presence — never robotic, never scripted.
You are emotionally intelligent, subtle, and natural.

Rules:
- 1–2 sentences max
- Never lecture
- Never sound like a therapist
- Never repeat yourself
- No emojis
- No commands, no pressure
"""

TONE_INSTRUCTIONS = {
    "calm": "Speak softly, reassuring, emotionally grounding.",
    "extra_calm": "Be extremely soothing and steady.",
    "gentle": "Warm, caring, low energy.",
    "strict": "Firm, direct, no nonsense.",
    "very_strict": "Sharp, commanding, decisive.",
    "soft_strict": "Firm but encouraging.",
    "de_escalate": "Slow things down, reduce anger.",
    "hype": "High energy, celebratory.",
    "neutral": "Natural, supportive conversation."
}


# ================== CORE ==================

def generate_voice_line(state, intent, decision, persona, user_traits=None, prediction=None):
    tone = get_tone(state, user_traits)

    if tone == "silent":
        return None

    memory_context = get_memory_context()

    prompt = f"""
Context:
State: {state}
Intent: {intent}
Decision: {decision}
Persona: {persona}
Traits: {user_traits}
Prediction: {prediction}

Recent memory:
{memory_context}

Tone instruction:
{TONE_INSTRUCTIONS.get(tone, "neutral")}

What would Omni say right now?
"""

    response = model.generate_content([VOICE_SYSTEM_PROMPT, prompt])
    text = response.text.strip()

    if not text:
        return None

    return text, tone