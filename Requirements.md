Software and Libraries
	Gemini API Key (for cognition, reasoning, and prediction)
  StreamLit (dashboard & control interface)
  Computer vision libraries (frame capture & analysis)
	Data libraries (JSON, Pandas)

System utilities
psutil>=5.9.5
Desktop / laptop system
Python 3.9+
Stable Internet connection

Permissions Required
  Screen access (to observe on‑screen activity)
  System time access (for accurate cognitive logging)
  Local file read/write (logs, memory, control states)
  Microphone access (optional) — only if voice feedback is enabled
  pyaudio>=0.2.13
  sounddevice>=0.4.6

Operational Requirements
  User‑controlled mode selection: OFF / OBSERVE / ACTIVE
  Backend explicitly started via dashboard (not auto‑running)
	Logs generated only in OBSERVE and ACTIVE modes

Privacy and Safety 
	All data stored locally
	No background execution without user consent
	No interventions unless ACTIVE mode is enabled
