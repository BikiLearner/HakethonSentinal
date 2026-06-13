
import streamlit as st
import numpy as np
import json
import time
import cv2

from ui.components.video_engine import VideoEngine

# ---------------------------------------------------------------------------
# Private layout helpers — pure UI, zero domain logic
# ---------------------------------------------------------------------------

def _render_header() -> None:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
            border-left: 4px solid #e63946;
            border-radius: 6px;
            padding: 1.2rem 1.6rem;
            margin-bottom: 0.5rem;
        ">
            <h1 style="color:#f1faee; margin:0; font-size:1.8rem; letter-spacing:0.04em;">
                🏭 Industrial AI Monitoring
            </h1>
            <p style="color:#a8dadc; margin:0.3rem 0 0; font-size:0.85rem; letter-spacing:0.08em;">
                REAL-TIME ZONE SURVEILLANCE &amp; TELEMETRY
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
@st.fragment
def _render_video_feed(view_model):

    frame, event ,elapsed  = VideoEngine.get_frame()

    # 🔥 send event to VM
    view_model.on_frame_update(frame, event, elapsed)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    st.image(frame, width='stretch')

def _render_telemetry(telemetry: dict) -> None:
    """Display telemetry metrics from ViewModel data."""
    st.markdown(
        "<p style='color:#a8dadc; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.5rem;'>⚙️ LIVE TELEMETRY</p>",
        unsafe_allow_html=True,
    )

    temperature  = telemetry.get("temperature", "—")
    vibration    = telemetry.get("vibration", "—")
    status       = telemetry.get("status", "UNKNOWN")
    uptime       = telemetry.get("uptime_hrs", "—")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(
            label="🌡️ Temperature",
            value=f"{temperature} °C",
            delta=telemetry.get("temperature_delta", None),
        )
        st.metric(
            label="📡 Uptime",
            value=f"{uptime} hrs",
        )
    with col_b:
        st.metric(
            label="📳 Vibration",
            value=f"{vibration} Hz",
            delta=telemetry.get("vibration_delta", None),
        )
        # Status badge
        _render_status_badge(status)


def _render_status_badge(status: str) -> None:
    palette = {
        "SAFE":     ("#2d6a4f", "#52b788", "✅"),
        "WARNING":  ("#7b4f12", "#f4a261", "⚠️"),
        "CRITICAL": ("#6b0f1a", "#e63946", "🔴"),
    }
    bg, fg, icon = palette.get(status.upper(), ("#333", "#aaa", "❓"))

    st.markdown(
        f"""
        <div style="
            background:{bg};
            border:1px solid {fg};
            border-radius:6px;
            padding:0.6rem 0.8rem;
            margin-top:0.6rem;
            text-align:center;
        ">
            <span style="font-size:1.4rem;">{icon}</span>
            <div style="color:{fg}; font-weight:700; letter-spacing:0.12em;
                        font-size:0.9rem; margin-top:0.15rem;">
                {status}
            </div>
            <div style="color:{fg}88; font-size:0.7rem; letter-spacing:0.08em;">
                SYSTEM STATUS
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_alerts(alert_message: str | None) -> None:
    """Render the Alert Panel driven by ViewModel data."""
    st.markdown(
        "<p style='color:#a8dadc; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.4rem;'>🚨 ALERT PANEL</p>",
        unsafe_allow_html=True,
    )

    if not alert_message:
        st.success("✅ All zones nominal — no active alerts.", icon=None)
        return

    lower = alert_message.lower()

    if "critical" in lower:
        st.error(alert_message)
    elif "warning" in lower or "detected" in lower:
        st.warning(alert_message)
    else:
        st.info(alert_message)

    # Secondary hardcoded contextual alerts shown alongside model output
    st.warning("⚠️ Human detected in restricted zone — verify clearance.")
    st.error("🔴 CRITICAL: Unsafe human–machine interaction flagged.")


def _render_config(config: dict) -> None:
    """Display current configuration as formatted JSON — mirrors planner screen."""
    st.markdown(
        "<p style='color:#a8dadc; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.4rem;'>⚙️ ACTIVE CONFIGURATION</p>",
        unsafe_allow_html=True,
    )
    st.json(config, expanded=False)


# ---------------------------------------------------------------------------
# Public entry point — called by the router / app.py
# ---------------------------------------------------------------------------
@st.fragment(run_every=0.03)  # 🔥 30 FPS loop
def industrial_widget(view_model) -> None:
    """
    Render the Industrial AI Monitoring screen.

    Parameters
    ----------
    view_model : IndustrialViewModel
        Must expose:
            - alert_message   : str | None
            - telemetry_data  : dict
            - current_config  : dict
            - on_frame_update(frame) -> None
    """
    _render_header()
    st.divider()

    # ── Trigger a simulated frame update through ViewModel ──────────────────
    # In production this comes from a real camera capture loop.

    # ── Main layout: left feed | right telemetry ────────────────────────────
    col_feed, col_telem = st.columns([1.6, 1], gap="large")

    with col_feed:
        st.markdown("##### 📹 Zone Camera Feed")
        _render_video_feed(view_model)

    with col_telem:
        st.markdown("##### 📊 Telemetry")
        _render_telemetry(view_model.telemetry_data)

    st.divider()

    # ── Alert panel ─────────────────────────────────────────────────────────
    st.markdown("##### 🚨 Zone Alerts")
    _render_alerts(view_model.alert_message)

    st.divider()

    # ── Configuration display ────────────────────────────────────────────────
    with st.expander("⚙️ Configuration", expanded=False):
        _render_config(view_model.current_config)