import sys
import os
import json
import time
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

# ================= PATH FIX =================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(ROOT_DIR)
sys.path.append(ROOT_DIR)

# ================= IMPORTS =================
from cognition.predictor import stress_risk
from cognition.intervention import recommend_intervention
from cognition.learning import best_focus_window, cognitive_entropy
from cognition.automation import emit_actions
from utils.control import read_control

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except Exception:
    AUTOREFRESH_AVAILABLE = False

# ================= CONFIG =================
st.set_page_config(
    page_title="AURION | Neural Command Center",
    page_icon="🧠",
    layout="wide"
)

# ================= FILE PATHS =================
STATE_LOG = "memory/logs/states.json"
VOICE_LOG = "memory/logs/voice_log.json"
CONTROL_FILE = "memory/control.json"

# ================= CONTROL IO =================
def write_control_file(mode):
    if mode == "OFF":
        backend_enabled = False
        logging_enabled = False
    else:
        backend_enabled = True
        logging_enabled = True

    data = {
        "aurion_mode": mode,
        "backend_enabled": backend_enabled,
        "logging_enabled": logging_enabled,
        "last_updated": int(time.time())
    }

    os.makedirs("memory", exist_ok=True)
    with open(CONTROL_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ================= RESET =================
def reset_aurion():
    try:
        os.makedirs("memory/logs", exist_ok=True)
        with open(STATE_LOG, "w") as f:
            json.dump([], f)
        with open(VOICE_LOG, "w") as f:
            json.dump([], f)
    except Exception:
        pass

    try:
        write_control_file("OFF")
    except Exception:
        pass

    st.session_state["aurion_mode"] = "OFF"
    st.session_state["last_mode"] = None

    st.toast("AURION reset. Waiting for backend cognition data…", icon="🔄")

# ================= CONSTANTS =================
STALE_THRESHOLD_SECONDS = 240

SCORE_MAP = {
    "DEEP_WORK": 95,
    "NORMAL_WORK": 75,
    "VICTORY": 85,
    "STRESSED": 40,
    "PROCRASTINATING": 25,
    "TIRED": 45
}

# ================= SESSION INIT =================
if "aurion_mode" not in st.session_state:
    st.session_state.aurion_mode = "OFF"
if "last_mode" not in st.session_state:
    st.session_state.last_mode = None

# ================= LOAD DATA SAFELY =================
if not os.path.exists(STATE_LOG):
    st.info("🧠 Waiting for backend cognition data…")
    st.stop()

with open(STATE_LOG, "r") as f:
    raw = json.load(f)

if not raw:
    st.info("🧠 AURION is idle. Waiting for cognition data…")
    st.stop()

df = pd.DataFrame(raw)

if "timestamp" not in df.columns:
    st.info("🧠 No timestamps yet. Waiting for backend…")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

if "state" not in df.columns:
    st.info("🧠 No state data yet.")
    st.stop()

# ================= FALLBACK COLUMNS =================
if "intensity" not in df.columns:
    df["intensity"] = df["state"].map({
        "DEEP_WORK": 0.9,
        "NORMAL_WORK": 0.7,
        "VICTORY": 0.85,
        "STRESSED": 0.3,
        "PROCRASTINATING": 0.2,
        "TIRED": 0.4
    })

if "confidence" not in df.columns:
    df["confidence"] = df["state"].map({
        "DEEP_WORK": 0.8,
        "NORMAL_WORK": 0.7,
        "VICTORY": 0.85,
        "STRESSED": 0.4,
        "PROCRASTINATING": 0.3,
        "TIRED": 0.45
    })

df["intensity"] = pd.to_numeric(df["intensity"], errors="coerce").fillna(0)
df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0)
df["reason"] = df.get("reason", "").fillna("")

# ================= TABS =================
tab_live, tab_summary = st.tabs(["🧠 Live Command Center", "🗓 Daily Summary"])

# =====================================================
# ================= LIVE TAB ==========================
# =====================================================
with tab_live:

    st.markdown("### ⚠️ System Controls")

    if st.button("🔄 Reset AURION (Clear All Data)", type="primary"):
        reset_aurion()
        st.success("AURION reset. System OFF.")
        st.rerun()

    st.session_state.aurion_mode = st.radio(
        "🧠 AURION Mode",
        ["OFF", "OBSERVE", "ACTIVE"],
        horizontal=True
    )

    if st.session_state.aurion_mode != st.session_state.last_mode:
        write_control_file(st.session_state.aurion_mode)
        st.session_state.last_mode = st.session_state.aurion_mode

    control = read_control()

    st.caption(
        f"🧭 Mode: **{control['aurion_mode']}** | "
        f"Backend: {'🟢 Running' if control['backend_enabled'] else '🔴 Paused'}"
    )

    if st.session_state.aurion_mode == "OFF":
        st.markdown("## 💤 AURION is Resting")
        st.stop()

    # ---------- WINDOW ----------
    minutes = st.slider("⏱ Time Window (minutes)", 5, 120, 15)

    now = datetime.now()
    latest = df["timestamp"].max()
    seconds_old = (now - latest).total_seconds()

    if seconds_old <= STALE_THRESHOLD_SECONDS:
        cutoff = now - timedelta(minutes=minutes)
    else:
        cutoff = latest - timedelta(minutes=minutes)

    recent = df[df["timestamp"] >= cutoff]

    if recent.empty:
        st.info("No usable data.")
        st.stop()

    current = recent.iloc[-1]
    focus = SCORE_MAP.get(current["state"], 50)

    # ---------- AUTO REFRESH ----------
    if (
        st.session_state.aurion_mode == "ACTIVE"
        and AUTOREFRESH_AVAILABLE
        and control["backend_enabled"]
    ):
        st_autorefresh(interval=2000, key="live")

    # ---------- DISPLAY ----------
    st.metric("Current State", current["state"])
    st.progress(focus / 100)

    st.info(current.get("reason", "AURION observing."))

    # ---------- VOICE ----------
    st.markdown("## 🔊 Voice Transcript")

    if os.path.exists(VOICE_LOG):
        vdf = pd.DataFrame(json.load(open(VOICE_LOG)))
        if not vdf.empty:
            if "timestamp" in vdf.columns:
                vdf["timestamp"] = pd.to_datetime(
                    vdf["timestamp"], unit="s", errors="coerce"
                )
            st.table(vdf.tail(10))
        else:
            st.caption("Voice log empty.")
    else:
        st.caption("No voice output yet.")

    # ---------- PREDICTION ----------
    risk = stress_risk(recent.tail(10))
    st.info(f"🧠 Stress risk: {int(risk * 100)}%")

    if st.session_state.aurion_mode == "ACTIVE":
        action = recommend_intervention(current["state"], risk, focus)
        if action:
            st.warning(action)

# =====================================================
# ================= SUMMARY TAB ========================
# =====================================================
with tab_summary:
    st.title("🗓 Daily Summary")

    log_day = df["timestamp"].max().date()
    today = df[df["timestamp"].dt.date == log_day]

    if today.empty:
        st.info("No data today.")
        st.stop()

    deep = (today["state"] == "DEEP_WORK").sum()
    stress = (today["state"] == "STRESSED").sum()
    avg_focus = today["state"].map(SCORE_MAP).mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("Deep Work", deep)
    c2.metric("Stress Events", stress)
    c3.metric("Avg Focus", f"{avg_focus:.1f}")

    st.bar_chart(today["state"].value_counts())

    best = best_focus_window(df)
    entropy = cognitive_entropy(df)

    st.success(f"Best focus hour: {best}:00–{best+1}:00")
    st.metric("Cognitive Stability", f"{entropy:.2f}")

    st.success(f"🧠 Best deep‑work window: {best_hour}:00–{best_hour+1}:00")
    st.metric("Cognitive Stability", f"{entropy:.2f}")
