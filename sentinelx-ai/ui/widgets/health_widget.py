
import streamlit as st
import numpy as np
from data.vision.health_camera_engine import HealthCameraEngine
import cv2

# ---------------------------------------------------------------------------
# Private layout helpers — pure UI, zero domain logic
# ---------------------------------------------------------------------------

def _render_header() -> None:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #f0f4ff 0%, #e8f5e9 100%);
            border-left: 4px solid #2196f3;
            border-radius: 6px;
            padding: 1.2rem 1.6rem;
            margin-bottom: 0.5rem;
        ">
            <h1 style="color:#1a237e; margin:0; font-size:1.8rem; letter-spacing:0.03em;">
                🧑‍⚕️ Healthcare AI Monitoring
            </h1>
            <p style="color:#546e7a; margin:0.3rem 0 0; font-size:0.85rem; letter-spacing:0.07em;">
                OBSERVATIONAL ACTIVITY &amp; WELLNESS INSIGHTS
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Prominent disclaimer — always visible
    st.markdown(
        """
        <div style="
            background:#fff8e1;
            border:1px solid #ffca28;
            border-radius:5px;
            padding:0.55rem 1rem;
            margin-top:0.5rem;
            font-size:0.82rem;
            color:#5d4037;
        ">
            ⚠️ <strong>Disclaimer:</strong> This is observational insight only and
            does <u>not</u> constitute medical diagnosis, advice, or treatment.
            Consult a qualified healthcare professional for any clinical concerns.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_observation_feed(view_model):

    frame, signals = HealthCameraEngine.get_frame()

    if frame is None:
        st.warning("Camera not accessible")
        return

    # 🔥 send to ViewModel
    view_model.on_frame_update(frame, signals)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    st.image(frame, use_container_width=True)

def _render_metrics(health_metrics: dict) -> None:
    """Display health observation metrics from ViewModel data."""
    st.markdown(
        "<p style='color:#546e7a; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.5rem;'>📈 OBSERVATION METRICS</p>",
        unsafe_allow_html=True,
    )

    activity   = health_metrics.get("activity_level", "—")
    movement   = health_metrics.get("movement_score", "—")
    attention  = health_metrics.get("attention_level", "—")
    posture    = health_metrics.get("posture_score", "—")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(
            label="🏃 Activity Level",
            value=activity,
            delta=health_metrics.get("activity_delta", None),
        )
        st.metric(
            label="🧠 Attention Level",
            value=attention,
            delta=health_metrics.get("attention_delta", None),
        )
    with col_b:
        st.metric(
            label="🔄 Movement Score",
            value=movement,
            delta=health_metrics.get("movement_delta", None),
        )
        st.metric(
            label="🪑 Posture Score",
            value=posture,
        )


def _render_wellbeing_gauge(health_metrics: dict) -> None:
    """Simple colour-coded wellness indicator."""
    overall = health_metrics.get("overall_wellness", "MODERATE")

    palette = {
        "HIGH":     ("#1b5e20", "#66bb6a", "🟢"),
        "MODERATE": ("#1a237e", "#64b5f6", "🔵"),
        "LOW":      ("#e65100", "#ffa726", "🟡"),
        "CONCERN":  ("#b71c1c", "#ef5350", "🔴"),
    }
    bg, fg, icon = palette.get(overall.upper(), ("#37474f", "#90a4ae", "⚪"))

    st.markdown(
        f"""
        <div style="
            background:{bg}22;
            border:1px solid {fg};
            border-radius:8px;
            padding:0.8rem 1rem;
            margin-top:0.8rem;
            text-align:center;
        ">
            <div style="font-size:1.6rem;">{icon}</div>
            <div style="color:{fg}; font-weight:700; letter-spacing:0.1em;
                        font-size:0.95rem; margin-top:0.2rem;">
                WELLNESS: {overall}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_insights(insight_message: str | None) -> None:
    """Render the Insight Panel driven by ViewModel data."""
    st.markdown(
        "<p style='color:#546e7a; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.4rem;'>💡 AI INSIGHTS</p>",
        unsafe_allow_html=True,
    )

    if not insight_message:
        st.info("ℹ️ No significant observations at this time.")
        return

    lower = insight_message.lower()

    if any(kw in lower for kw in ("concern", "critical", "urgent")):
        st.warning(f"⚠️ {insight_message}")
    elif any(kw in lower for kw in ("fatigue", "low activity", "low")):
        st.warning(f"⚠️ {insight_message}")
    else:
        st.info(f"ℹ️ {insight_message}")

    # Contextual supplemental insights (representative examples)
    st.info("ℹ️ Low activity detected — consider a short movement break.")
    st.warning("⚠️ Possible fatigue pattern observed in recent frames.")
    st.info("ℹ️ High attention state — engagement appears elevated.")


def _render_config(config: dict) -> None:
    """Display current configuration as formatted JSON — mirrors planner screen."""
    st.markdown(
        "<p style='color:#546e7a; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.4rem;'>⚙️ ACTIVE CONFIGURATION</p>",
        unsafe_allow_html=True,
    )
    st.json(config, expanded=False)


# ---------------------------------------------------------------------------
# Public entry point — called by the router / app.py
# ---------------------------------------------------------------------------

@st.fragment(run_every=0.1)
def health_widget(view_model):

    _render_header()
    st.divider()

    col_feed, col_metrics = st.columns([1.6, 1], gap="large")

    with col_feed:
        st.markdown("##### 📹 Observation Feed")
        _render_observation_feed(view_model)

    with col_metrics:
        st.markdown("##### 📊 Metrics")
        _render_metrics(view_model.health_metrics)
        _render_wellbeing_gauge(view_model.health_metrics)

    st.divider()

    st.markdown("##### 💡 Observational Insights")
    _render_insights(view_model.insight_message)

    st.divider()

    with st.expander("⚙️ Configuration", expanded=False):
        _render_config(view_model.current_config)