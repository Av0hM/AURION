import time
from datetime import datetime

from system.vision.frame_provider import get_combined_frame
from ai.ai_analyzer import analyze_frame
from memory.state_logger import log_state
from ai.learner import Learner

from utils.control import read_control
from utils.timebase import now_unix

import sys
print("BACKEND PYTHON:", sys.executable)

try:
    from voice.voice_engine import speak
    from voice.voice_generator import generate_voice_line, can_speak
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

print("🧠 AURION backend starting... Press Ctrl+C to stop.")

learner = Learner()
LOOP_DELAY = 2

while True:
    try:
        # =====================================================
        # 🔐 READ CONTROL FILE (Option B)
        # =====================================================
        control = read_control()

        aurion_mode = control.get("aurion_mode", "OFF")
        backend_enabled = control.get("backend_enabled", False)
        logging_enabled = control.get("logging_enabled", False)

        # =====================================================
        # 🛑 OFF MODE → backend fully paused
        # =====================================================
        if not backend_enabled:
            print("🛑 AURION backend paused (OFF mode)")
            time.sleep(2)
            continue

        # =====================================================
        # 🧠 SENSE + ANALYZE
        # =====================================================
        frame = get_combined_frame()
        brain = analyze_frame(frame)

        if not isinstance(brain, dict):
            time.sleep(LOOP_DELAY)
            continue

        # =====================================================
        # ⏱️ FORCE SYSTEM TIME (single source of truth)
        # =====================================================
        brain["timestamp"] = now_unix()
        brain["aurion_mode"] = aurion_mode

        # =====================================================
        # 📝 LOGGING (OBSERVE + ACTIVE)
        # =====================================================
        if logging_enabled:
            log_state(brain)

        # =====================================================
        # 🖨️ DEBUG OUTPUT
        # =====================================================
        print("\n🧠 GEMINI 3 OUTPUT @", now_unix())
        for k, v in brain.items():
            print(f"{k}: {v}")

        # =====================================================
        # 🔊 VOICE + SIDE‑EFFECTS (ACTIVE ONLY)
        # =====================================================
        if aurion_mode == "ACTIVE" and VOICE_ENABLED and can_speak():
            result = generate_voice_line(
                state=brain.get("state"),
                intent=brain.get("intent"),
                decision=brain.get("decision"),
                persona=brain.get("persona"),
                user_traits=learner.traits,
                prediction=brain.get("prediction")
            )

            if result:
                line, tone = result
                print("🔊 SPEAKING:", line, "| tone:", tone)
                speak(line, tone=tone)

        # =====================================================
        # 🕒 LOOP DELAY
        # =====================================================
        time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\n🛑 AURION backend stopped.")
        break

    except Exception as e:
        print("❌ Backend error:", e)
        time.sleep(45)