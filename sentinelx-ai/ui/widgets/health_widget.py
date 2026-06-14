import streamlit as st
import numpy as np
from data.vision.health_camera_engine import HealthCameraEngine
import cv2
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Private layout helpers — pure UI, zero domain logic
# ---------------------------------------------------------------------------

def _render_header() -> None:
    st.html(
        """
        <div style="background: linear-gradient(135deg, #f0f4ff 0%, #e8f5e9 100%);
                    border-left: 4px solid #2196f3; border-radius: 6px; padding: 1.2rem 1.6rem; margin-bottom: 0.5rem;">
            <h1 style="color:#1a237e; margin:0; font-size:1.8rem; letter-spacing:0.03em;">
                🧑‍⚕️ SentinelX AI Telemetry
            </h1>
            <p style="color:#546e7a; margin:0.3rem 0 0; font-size:0.85rem; letter-spacing:0.07em;">
                CLINICAL OBSERVATION & WELLNESS ENGINE
            </p>
        </div>
        """
    )
    # Prominent disclaimer — always visible
    st.html(
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
        """
    )

def _render_metrics(health_metrics: dict[str, str]) -> None:
    """Display health observation metrics from ViewModel data."""
    st.html(
        "<p style='color:#546e7a; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.5rem;'>📈 LIVE TELEMETRY METRICS</p>"
    )

    st.metric(label="🏃 Activity State", value=health_metrics.get("activity_level", "—"))
    st.metric(label="🧠 Attention State", value=health_metrics.get("attention_level", "—"))
    st.metric(label="🔄 Kinematic Score", value=health_metrics.get("movement_score", "—"))

def _render_detailed_report(report: dict[str, Any]) -> None:
    """Renders a structured final medical-style diagnostic dashboard."""
    color = report.get('color', '#546e7a')

    st.markdown("### 📋 Automated Biomechanical Assessment")

    st.html(
        f"""
        <div style="border: 1px solid #cfd8dc; border-left: 6px solid {color}; border-radius: 8px; padding: 2rem; background-color: #ffffff; font-family: 'Helvetica Neue', Arial, sans-serif;">
            
            <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #eceff1; padding-bottom: 1rem; margin-bottom: 1.5rem;">
                <div>
                    <h3 style="margin: 0; color: #263238; font-size: 1.4rem;">{report.get('status', 'ANALYSIS COMPLETE')}</h3>
                    <p style="margin: 0; color: #78909c; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;">
                        Diagnostic Code: {report.get('sys_code', 'N/A')} | Timestamp: {report.get('timestamp', '--')}
                    </p>
                </div>
                <div style="text-align: right;">
                    <span style="background-color: {color}15; color: {color}; padding: 0.5rem 1.2rem; border-radius: 4px; font-weight: 800; font-size: 0.9rem; letter-spacing: 0.05em;">
                        SEVERITY: {report.get('severity', 'UNKNOWN')}
                    </span>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
                <div style="background: #f5f7fa; padding: 1rem; border-radius: 6px; border: 1px solid #e4e8eb;">
                    <p style="margin: 0; color: #546e7a; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.05em;">OPTICAL RETENTION</p>
                    <h2 style="margin: 0.3rem 0 0 0; color: #263238; font-size: 1.5rem;">{report.get('presence_rate', '0%')}</h2>
                </div>
                <div style="background: #f5f7fa; padding: 1rem; border-radius: 6px; border: 1px solid #e4e8eb;">
                    <p style="margin: 0; color: #546e7a; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.05em;">AXIAL ALIGNMENT</p>
                    <h2 style="margin: 0.3rem 0 0 0; color: #263238; font-size: 1.5rem;">{report.get('centered_rate', '0%')}</h2>
                </div>
                <div style="background: #f5f7fa; padding: 1rem; border-radius: 6px; border: 1px solid #e4e8eb;">
                    <p style="margin: 0; color: #546e7a; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.05em;">KINEMATIC ENTROPY</p>
                    <h2 style="margin: 0.3rem 0 0 0; color: #263238; font-size: 1.5rem;">{report.get('kinematic_entropy', '0')}</h2>
                </div>
                <div style="background: #f5f7fa; padding: 1rem; border-radius: 6px; border: 1px solid #e4e8eb;">
                    <p style="margin: 0; color: #546e7a; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.05em;">PHYSICAL VARIANCE</p>
                    <h2 style="margin: 0.3rem 0 0 0; color: #263238; font-size: 1.5rem;">{report.get('variance', '0')}</h2>
                </div>
            </div>

            <div style="background-color: #fafbfc; border: 1px solid #edf2f7; padding: 1.5rem; border-radius: 6px; margin-bottom: 1.5rem;">
                <h4 style="margin: 0 0 0.8rem 0; color: #2c3e50; font-size: 1.1rem;">🩺 AI Clinical Observations</h4>
                <div style="color: #4a5568; font-size: 0.95rem; line-height: 1.6;">
                    {report.get('clinical_notes', 'Detailed clinical notes are being processed...')}
                </div>
            </div>

            <div style="background: #fff8e1; border-left: 4px solid #ffca28; padding: 1.2rem; border-radius: 4px;">
                <h4 style="margin: 0 0 0.4rem 0; color: #b7791f; font-size: 1rem;">⚡ Actionable Recommendation</h4>
                <p style="margin: 0; color: #744210; font-size: 0.95rem;">{report.get('recommendation', 'Maintain standard ergonomic guidelines.')}</p>
            </div>
            
            <p style="text-align: center; color: #a0aec0; font-size: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px dashed #e2e8f0;">
                <strong>Disclaimer:</strong> This assessment is generated by optical heuristics and machine learning algorithms. It is strictly an observational tool and does not constitute a medical diagnosis, nor does it replace evaluation by a licensed healthcare professional.
            </p>
        </div>
        """
    )

def _render_config(config: dict) -> None:
    """Display current configuration as formatted JSON — mirrors planner screen."""
    st.html(
        "<p style='color:#546e7a; font-size:0.75rem; letter-spacing:0.1em;"
        " margin-bottom:0.4rem;'>⚙️ ACTIVE CONFIGURATION</p>"
    )
    st.json(config, expanded=False)

@st.fragment(run_every=0.1)
def health_widget(view_model):
    # Initialize engine once when the fragment starts/resets
    HealthCameraEngine.init()

    _render_header()

    st.divider()

    col_feed, col_metrics = st.columns([1.5, 1], gap="large")

    with col_feed:
        st.markdown("##### 📹 Live Telemetry Feed")
        frame, signals = HealthCameraEngine.get_frame()
        if frame is not None:
            view_model.on_frame_update(frame, signals)
            
            # 🔥 Convert and Compress before sending to Streamlit
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode(".jpg", rgb, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            st.image(buffer.tobytes(), width="stretch")
        else:
            st.warning("Camera not accessible.")

    with col_metrics:
        st.markdown("##### 📊 Live Metrics")
        _render_metrics(view_model.health_metrics)

    st.divider()

    # Dynamic Analysis UI
    if view_model.is_analyzing:
        st.markdown("##### ⏳ Compiling Biometric Report...")
        prog_pct = int(view_model.analysis_progress * 100)
        st.progress(view_model.analysis_progress, text=f"Analyzing spatial data window... {prog_pct}%")
    else:
        st.success("✅ Analysis Complete!")
        if st.button("🔄 Start New Diagnostic Scan", type="primary"):
            view_model.restart_analysis()
            st.rerun()

        _render_detailed_report(view_model.report_data)

    st.divider()

    with st.expander("⚙️ Configuration", expanded=False):
        _render_config(view_model.current_config)