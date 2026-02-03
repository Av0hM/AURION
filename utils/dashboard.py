import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(ROOT_DIR)
sys.path.append(ROOT_DIR)

import streamlit as st
import json
import time
import pandas as pd
from cognition.predictor import stress_risk
from cognition.intervention import recommend_intervention
from cognition.learning import best_focus_window, cognitive_entropy
from cognition.automation import emit_actions
from datetime import datetime, timedelta
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

def reset_aurion():
    # 1. Safely reset state logs
    try:
        if os.path.exists(STATE_LOG):
            with open(STATE_LOG, "w") as f:
                json.dump([], f)
    except Exception:
        pass

    # 2. Safely reset voice logs
    try:
        if os.path.exists(VOICE_LOG):
            with open(VOICE_LOG, "w") as f:
                json.dump([], f)
    except Exception:
        pass

    # 3. Reset control mode to OFF
    try:
        write_control_file("OFF")
    except Exception:
        pass

    # 4. Reset Streamlit session state (NO crashes)
    st.session_state["omni_mode"] = "OFF"
    st.session_state["last_mode"] = None

    # 5. Optional UX message (no red error)
    st.toast("AURION reset. Waiting for new cognition data…", icon="🔄")


# ================= TIME CONFIG =================
STALE_THRESHOLD_SECONDS = 240

CONTROL_FILE = "memory/control.json"

def write_control_file(aurion_mode):
    if aurion_mode == "OFF":
        backend_enabled = False
        logging_enabled = False
    elif aurion_mode == "OBSERVE":
        backend_enabled = True
        logging_enabled = True
    else:
        backend_enabled = True
        logging_enabled = True

    data = {
        "aurion_mode": aurion_mode,
        "backend_enabled": backend_enabled,
        "logging_enabled": logging_enabled,
        "last_updated": int(time.time())
    }

    os.makedirs("memory", exist_ok=True)
    with open(CONTROL_FILE, "w") as f:
        json.dump(data, f, indent=2)


def read_control_file():
    if not os.path.exists(CONTROL_FILE):
        return {
            "aurion_mode": "OFF",
            "backend_enabled": False,
            "logging_enabled": False
        }

    try:
        with open(CONTROL_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "aurion_mode": "OFF",
            "backend_enabled": False,
            "logging_enabled": False
        }
# ================= BACKGROUND + UI STYLES =================
st.markdown("""
<style>

/* ===== CINEMATIC LOW‑SATURATION BACKGROUND ===== */

:root {
    --bias-hue: 220;
    --energy: 0.55;
    --pulse: 1.05;
}

.stApp {
    background: radial-gradient(circle at center, #020617, #000000 75%);
    overflow: hidden;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: -55%;
    background:
        conic-gradient(
            from 0deg,
            hsla(calc(var(--bias-hue) +   0), 55%, 55%, 0.75),
            hsla(calc(var(--bias-hue) + 120), 55%, 55%, 0.65),
            hsla(calc(var(--bias-hue) + 240), 55%, 55%, 0.75),
            hsla(calc(var(--bias-hue) + 360), 55%, 55%, 0.75)
        );
    filter: blur(70px);
    opacity: var(--energy);
    animation:
        spin 28s linear infinite,
        breathe 10s ease-in-out infinite;
    z-index: 0;
}

@keyframes spin {
    from { transform: rotate(0deg) scale(var(--pulse)); }
    to   { transform: rotate(360deg) scale(var(--pulse)); }
}

@keyframes breathe {
    0%   { transform: scale(1); }
    50%  { transform: scale(1.1); }
    100% { transform: scale(1); }
}

/* ===== GLASS UI ===== */

.card {
    background: rgba(10, 15, 30, 0.82);
    backdrop-filter: blur(18px);
    border-radius: 22px;
    padding: 1.5rem;
    box-shadow: 0 0 40px rgba(0,0,0,0.6);
    margin-bottom: 1.4rem;
}

.chart-canvas {
    background: rgba(6, 10, 25, 0.7);
    backdrop-filter: blur(18px);
    border-radius: 22px;
    padding: 1.4rem;
    margin-top: 1.4rem;
}

.small {
    opacity: 0.75;
    font-size: 0.85rem;
}

section.main,
header,
footer {
    position: relative;
    z-index: 10;
}

</style>
""", unsafe_allow_html=True)

# ================= FILE PATHS =================
STATE_LOG = "memory/logs/states.json"
VOICE_LOG = "memory/logs/voice_log.json"

# ================= LOAD DATA =================
if not os.path.exists(STATE_LOG):
    st.error("No state logs found.")
    st.stop()

raw = json.load(open(STATE_LOG))

if not raw:
    st.info("🧠 AURION is idle. Waiting for cognition data…")
    st.stop()

df = pd.DataFrame(raw)

if "timestamp" not in df.columns:
    st.info("🧠 No timestamps yet. Waiting for backend…")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")


# ================= SANITIZATION & FALLBACKS =================

# Ensure required column
if "state" not in df.columns:
    st.error("State column missing in logs.")
    st.stop()

# Derive intensity if missing
if "intensity" not in df.columns:
    df["intensity"] = df["state"].map({
        "DEEP_WORK": 0.90,
        "NORMAL_WORK": 0.70,
        "VICTORY": 0.85,
        "STRESSED": 0.30,
        "PROCRASTINATING": 0.20,
        "TIRED": 0.40
    })

# Derive confidence if missing
if "confidence" not in df.columns:
    df["confidence"] = df["state"].map({
        "DEEP_WORK": 0.80,
        "NORMAL_WORK": 0.70,
        "VICTORY": 0.85,
        "STRESSED": 0.40,
        "PROCRASTINATING": 0.30,
        "TIRED": 0.45
    })

df["intensity"] = pd.to_numeric(df["intensity"], errors="coerce").fillna(0.0)
df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.0)

if "reason" not in df.columns:
    df["reason"] = ""

df["reason"] = df["reason"].fillna("").astype(str)

# ================= CONSTANTS =================
SCORE_MAP = {
    "DEEP_WORK": 95,
    "NORMAL_WORK": 75,
    "VICTORY": 85,
    "STRESSED": 40,
    "PROCRASTINATING": 25,
    "TIRED": 45
}

# ================= TABS =================
tab_live, tab_summary = st.tabs(
    ["🧠 Live Command Center", "🗓 Daily Summary"]
)

# =====================================================
# ================= LIVE TAB ==========================
# =====================================================
with tab_live:
    # ================= AURION MODE =================
    if "aurion_mode" not in st.session_state:
        st.session_state.aurion_mode = "OFF"
    
    st.markdown("### ⚠️ System Controls")

    if st.button("🔄 Reset AURION (Clear All Data)", type="primary"):
        reset_aurion()
        st.success("AURION has been reset. All logs cleared. System is now OFF.")
    st.rerun()


    st.session_state.aurion_mode = st.radio(
        "🧠 AURION Mode",
        ["OFF", "OBSERVE", "ACTIVE"],
        horizontal=True,
        help="Control whether AURION rests, observes, or actively intervenes"
    )

    AURION_MODE = st.session_state.aurion_mode

    #  WRITE CONTROL FILE ON CHANGE
    if "last_mode" not in st.session_state:
        st.session_state.last_mode = None

    if AURION_MODE != st.session_state.last_mode:
        write_control_file(AURION_MODE)
        st.session_state.last_mode = AURION_MODE

    # 🔹 READ CONTROL FILE BACK (UI TRUTH)
    control = read_control()

    st.caption(
        f"🧭 AURION Mode: **{control['aurion_mode']}** | "
        f"Backend: {'🟢 Running' if control['backend_enabled'] else '🔴 Paused'} | "
        f"Logging: {'📝 On' if control['logging_enabled'] else '⛔ Off'}"
    )

    # ================= OFF MODE =================
    if AURION_MODE == "OFF":
        st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at center, #020617, #000000 90%);
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("## 💤 AURION is Resting")
        st.caption("No cognition is being observed. No predictions, no interventions.")
        st.stop()

    # ---------- CONTROLS ----------
    c1, c2, c3, c4 = st.columns([2,1,1,1])
    minutes = c1.slider("⏱ Time Window (minutes)", 5, 120, 15)
    mode = c2.radio("Mode", ["🟢 Live", "🎬 Replay"], horizontal=True)
    pause = c3.toggle("⏸ Pause")
    dev_mode = c4.toggle("🛠 Dev")

    is_live = mode.startswith("🟢")

    # ---------- DATA WINDOW ----------
    now = datetime.now()

    latest_log_time = df["timestamp"].max()
    seconds_since_last_log = (now - latest_log_time).total_seconds()

    # ---- Decide which data to show ----
    if seconds_since_last_log <= STALE_THRESHOLD_SECONDS:
    #  Fresh data — normal live behavior
        cutoff = now - timedelta(minutes=minutes)
        recent = df[df["timestamp"] >= cutoff]
        data_mode = "LIVE"

    else:
        #  Stale data — fallback to last known window
        cutoff = latest_log_time - timedelta(minutes=minutes)
        recent = df[df["timestamp"] >= cutoff]
        data_mode = "STALE"


    if recent.empty:
        st.error("No historical data available.")
        st.stop()

    current = recent.iloc[-1]

    if is_live:
        current = recent.iloc[-1]
    else:
        idx = st.slider("Scrub Timeline", 0, len(recent)-1, len(recent)-1)
        current = recent.iloc[idx]

    # ---------- AUTO REFRESH ----------
    if AURION_MODE == "ACTIVE" and is_live and not pause and not dev_mode and control["backend_enabled"]:
        if AUTOREFRESH_AVAILABLE:
            st_autorefresh(interval=2000, key="live_refresh")

    # ---------- BACKGROUND REACTIVITY ----------
    if AURION_MODE != "OFF":
        focus = SCORE_MAP.get(current["state"], 50)

    if AURION_MODE == "ACTIVE":
        if current["state"] == "STRESSED":
            bias, energy = 0, 0.65
        elif current["state"] == "DEEP_WORK":
            bias, energy = 135, 0.45
        elif current["state"] == "VICTORY":
            bias, energy = 260, 0.55
        else:
            bias, energy = 220, 0.5
    else:
        # OBSERVE MODE — calm neutral
        bias, energy = 220, 0.35

    pulse = 1 + (focus / 250 if AURION_MODE == "ACTIVE" else 0.02)

    st.markdown(f"""
    <style>
    :root {{
        --bias-hue: {bias};
        --energy: {energy};
        --pulse: {pulse};
    }}
    </style>
    """, unsafe_allow_html=True)

    # ---------- HERO ----------
    st.markdown(f"""
    <div class="card">
        <h1>🧠 AURION Neural Command Center</h1>
        <p class="small">{current["timestamp"]}</p>
        <h2>{current["state"].replace("_"," ").title()}</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"🔒 AURION Mode: **{AURION_MODE}**")

    # ---------- METRICS ----------
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Intent", current.get("intent", "—"))
    m2.metric("Decision", current.get("decision", "—"))
    m3.metric("Persona", current.get("persona", "—"))

    conf = current.get("confidence", 0.0)
    conf = 0.0 if pd.isna(conf) else float(conf)
    m4.metric("Confidence", f"{conf:.2f}")

    start_time = recent["timestamp"].min()
    end_time = recent["timestamp"].max()

    if data_mode == "STALE":
        st.warning(
        f"⏸️ No new data received.\n\n"
        f"Showing last available data from "
        f"**{start_time.strftime('%H:%M:%S')} → {end_time.strftime('%H:%M:%S')}** "
        f"({int(seconds_since_last_log)} seconds old)"
        )
    else:
        st.caption(
        f"🟢 Live data window: "
        f"{start_time.strftime('%H:%M:%S')} → {end_time.strftime('%H:%M:%S')}"
        )


    # ---------- FOCUS ----------
    st.markdown("## 🎯 Focus Integrity")
    st.progress(focus / 100)
    st.caption(f"Estimated focus: **{focus}/100**")

    # ---------- THOUGHTS ----------
    reason = current.get("reason", "")
    if not reason.strip():
        reason = "AURION is silently observing."
    st.info(reason)

    # ---------- VOICE ----------
    st.markdown("## 🔊 Voice Transcript")

    if os.path.exists(VOICE_LOG):
       vdf = pd.DataFrame(json.load(open(VOICE_LOG)))

       if not vdf.empty:
         if "timestamp" in vdf.columns:
            vdf["timestamp"] = pd.to_datetime(vdf["timestamp"], unit="s", errors="coerce")

         st.table(vdf.tail(10))
        else:
           st.caption("Voice log is empty.")
    else:
       st.caption("No voice output yet.")

    # ---------- GRAPHS ----------
    st.markdown("## 📈 Neural Activity")
    st.markdown('<div class="chart-canvas">', unsafe_allow_html=True)

    plot_df = recent.set_index("timestamp").sort_index()

    cL, cR = st.columns(2)
    with cL:
        st.caption("Intensity")
        st.line_chart(
            plot_df["intensity"]
            .rolling(window=5, min_periods=1)
            .mean()
        )

    with cR:
        st.caption("Confidence")
        st.line_chart(
            plot_df["confidence"]
            .rolling(window=5, min_periods=1)
            .mean()
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if dev_mode:
        st.markdown("## 🛠 Developer View")
        st.dataframe(recent.tail(50), use_container_width=True)

    # ================= PREDICTION =================
    risk = None
    if AURION_MODE in ["OBSERVE", "ACTIVE"]:
        risk = stress_risk(recent.tail(10))
        st.info(f"🧠 Predicted stress risk: {int(risk * 100)}%")

    # ================= INTERVENTION =================
    if AURION_MODE == "ACTIVE" and risk is not None:
        action = recommend_intervention(
            current["state"],
            risk,
            focus
        )
        if action:
            st.warning(action)

    # ================= AUTOMATION =================
    if AURION_MODE == "ACTIVE":
        actions = emit_actions(current["state"])
        if actions:
            st.markdown("### 🤖 Automation Signals")
            for a in actions:
                st.code(a)
# =====================================================
# ================= SUMMARY TAB ========================
# =====================================================
with tab_summary:
    st.title("🗓 Daily Session Summary")

    log_day = df["timestamp"].max().date()
    today = df[df["timestamp"].dt.date == log_day]

    if today.empty:
        st.warning("No data for this session.")
        st.stop()

    deep = (today["state"] == "DEEP_WORK").sum()
    stress = (today["state"] == "STRESSED").sum()
    avg_focus = today["state"].map(SCORE_MAP).mean()

    s1, s2, s3 = st.columns(3)
    s1.metric("Deep Work Events", deep)
    s2.metric("Stress Events", stress)
    s3.metric("Avg Focus Score", f"{avg_focus:.1f}")

    st.markdown("### State Breakdown")
    st.bar_chart(today["state"].value_counts())

    best_hour = best_focus_window(df)
    entropy = cognitive_entropy(df)

    st.success(f"🧠 Best deep‑work window: {best_hour}:00–{best_hour+1}:00")
    st.metric("Cognitive Stability", f"{entropy:.2f}")
