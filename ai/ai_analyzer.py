from PIL import Image
import cv2
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3-flash-preview")

ALLOWED_STATES = {
    "DEEP_WORK", "NORMAL_WORK", "DISTRACTED", "PROCRASTINATING",
    "TIRED", "STRESSED", "ANGRY", "CRYING",
    "EATING", "VICTORY", "BORED", "AWAY"
}

SYSTEM_PROMPT = """
You are an AI behavior perception engine.

Input:
Left = user's face (webcam)
Right = user's screen

Classify the user into EXACTLY ONE state from:
[DEEP_WORK, NORMAL_WORK, DISTRACTED, PROCRASTINATING, TIRED,
 STRESSED, ANGRY, CRYING, EATING, VICTORY, BORED, AWAY]

Output STRICTLY in this format.
Do NOT add extra text.

STATE: <STATE>
INTENSITY: <FLOAT 0.0-1.0>
CONFIDENCE: <FLOAT 0.0-1.0>
REASON: <ONE LINE VISUAL REASON>
"""

# ================== HELPERS ==================
def safe_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default

# ================== HELPERS ==================

def safe_float(val, default=0.0):
    try:
        return float(str(val).strip())
    except:
        return default


def normalize_state(state):
    state = state.strip().upper()
    return state if state in ALLOWED_STATES else "NORMAL_WORK"


# ================== CORE ==================

def analyze_state(frame):
    # OpenCV BGR → RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb)

    response = model.generate_content([
        SYSTEM_PROMPT,
        pil_image
    ])

    text = response.text.strip()
    parsed = {}

    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            parsed[k.strip().lower()] = v.strip()

    state = normalize_state(parsed.get("state", "NORMAL_WORK"))
    intensity = safe_float(parsed.get("intensity", 0.5))
    confidence = safe_float(parsed.get("confidence", 0.5))
    reason = parsed.get("reason", "")

    return {
        "state": state,
        "intensity": intensity,
        "confidence": confidence,
        "reason": reason,

        # minimal cognitive fields expected by rest of system
        "intent": "WORK" if state in ["DEEP_WORK", "NORMAL_WORK"] else "OTHER",
        "decision": "CONTINUE" if state not in ["AWAY"] else "IDLE",
        "persona": "SUPPORTIVE",
        "prediction": "ON_TRACK" if intensity > 0.6 else "UNCERTAIN"
    }


def analyze_frame(frame):
    """
    Entry point used by main.py
    """
    return analyze_state(frame)