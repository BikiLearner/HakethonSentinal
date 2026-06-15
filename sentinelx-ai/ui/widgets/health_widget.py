import streamlit as st
import numpy as np
from data.vision.health_camera_engine import HealthCameraEngine
import cv2
from datetime import datetime
from typing import Any

_ACCENT     = "#39ff14"
_ACCENT_RGB = "57,255,20"
_BG_DARK    = "#0d1117"
_BG_MID     = "#161b22"
_BG_PANEL   = "#0f1520"


def _css() -> None:
    st.markdown(f"""
    <style>
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, {_BG_PANEL} 0%, {_BG_MID} 100%);
        border: 1px solid rgba({_ACCENT_RGB}, 0.18);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        box-shadow: 0 0 18px rgba({_ACCENT_RGB}, 0.05);
        margin-bottom: 0.4rem;
    }}
    div[data-testid="stMetricLabel"] p {{
        color: rgba({_ACCENT_RGB}, 0.7) !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.14em !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: #e6edf3 !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
    }}
    div[data-testid="stExpander"] {{
        background: {_BG_PANEL} !important;
        border: 1px solid rgba({_ACCENT_RGB}, 0.15) !important;
        border-radius: 8px !important;
    }}
    details summary {{
        color: rgba({_ACCENT_RGB}, 0.8) !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.1em !important;
        font-weight: 700 !important;
    }}
    hr {{ border-color: rgba({_ACCENT_RGB}, 0.12) !important; }}
    div[data-testid="stProgress"] > div {{
        background: rgba({_ACCENT_RGB}, 0.12) !important;
        border-radius: 4px !important;
    }}
    div[data-testid="stProgress"] > div > div {{
        background: linear-gradient(90deg, {_ACCENT}, #00f0ff) !important;
        border-radius: 4px !important;
        box-shadow: 0 0 10px rgba({_ACCENT_RGB}, 0.5) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def _divider() -> None:
    st.markdown(
        f"<div style='height:1px;background:linear-gradient(90deg,transparent,"
        f"rgba({_ACCENT_RGB},0.2),transparent);margin:0.75rem 0;'></div>",
        unsafe_allow_html=True,
    )


def _section(icon: str, label: str) -> None:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin:0.8rem 0 0.4rem;">
        <span style="font-size:0.95rem;">{icon}</span>
        <span style="color:rgba({_ACCENT_RGB},0.75);font-size:0.7rem;font-weight:700;
            letter-spacing:0.2em;font-family:'Segoe UI',monospace;">{label}</span>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,
            rgba({_ACCENT_RGB},0.25),transparent);margin-left:6px;"></div>
    </div>
    """, unsafe_allow_html=True)


def _render_header() -> None:
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,#080c14 0%,#0d1520 100%);
        border-left:3px solid {_ACCENT};
        border-bottom:1px solid rgba({_ACCENT_RGB},0.12);
        border-radius:8px;padding:1rem 1.5rem;margin-bottom:0.75rem;
        display:flex;align-items:center;justify-content:space-between;
    ">
        <div>
            <h1 style="color:#e6edf3;margin:0;font-size:1.5rem;font-weight:800;letter-spacing:0.06em;">
                ⚡ SENTINEL · HEALTH
                <span style="font-weight:300;font-size:0.85rem;color:#484f58;"> v3.7</span>
            </h1>
            <p style="color:#8b949e;margin:0.2rem 0 0;font-size:0.72rem;letter-spacing:0.2em;">
                CLINICAL OBSERVATION &amp; WELLNESS ENGINE
                <span style="color:#484f58;margin:0 8px;">|</span>
                STATUS <span style="color:{_ACCENT};font-weight:700;">ONLINE</span>
            </p>
        </div>
        <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.2em;
            color:{_ACCENT};background:rgba({_ACCENT_RGB},0.06);
            border:1px solid rgba({_ACCENT_RGB},0.2);border-radius:20px;
            padding:5px 14px;text-shadow:0 0 12px {_ACCENT}88;">
            PROTOCOL HEALTH
        </div>
    </div>
    <div style="
        background:#0c1a0c;border:1px solid rgba({_ACCENT_RGB},0.2);
        border-left:3px solid #f4a261;
        border-radius:6px;padding:0.55rem 1rem;margin-bottom:0.5rem;
        font-size:0.78rem;color:#c9a96e;letter-spacing:0.03em;
    ">
        ⚠️&nbsp;&nbsp;<strong>Disclaimer:</strong> Observational insight only.
        Does <u>not</u> constitute medical diagnosis or treatment.
        Consult a qualified healthcare professional for clinical concerns.
    </div>
    """, unsafe_allow_html=True)


def _render_metrics(health_metrics: dict[str, str]) -> None:
    _section("📈", "LIVE TELEMETRY METRICS")
    st.metric(label="🏃  ACTIVITY STATE",   value=health_metrics.get("activity_level", "—"))
    st.metric(label="🧠  ATTENTION STATE",  value=health_metrics.get("attention_level", "—"))
    st.metric(label="🔄  KINEMATIC SCORE",  value=health_metrics.get("movement_score", "—"))

    # HUD data strip
    st.markdown(f"""
    <div style="
        background:{_BG_PANEL};border:1px solid rgba({_ACCENT_RGB},0.1);
        border-radius:8px;padding:0.6rem 0.9rem;margin-top:0.6rem;
        font-family:monospace;font-size:0.68rem;
        color:rgba({_ACCENT_RGB},0.45);letter-spacing:0.08em;
    ">
        <div style="margin-bottom:3px;">
            <span style="color:rgba({_ACCENT_RGB},0.28);">PROTOCOL</span>&nbsp;&nbsp;
            <span style="color:{_ACCENT};">HEALTH-MODE</span>
        </div>
        <div style="margin-bottom:3px;">
            <span style="color:rgba({_ACCENT_RGB},0.28);">ENGINE&nbsp;&nbsp;</span>&nbsp;&nbsp;
            <span style="color:{_ACCENT};">BIOMECHANICAL v3.7</span>
        </div>
        <div>
            <span style="color:rgba({_ACCENT_RGB},0.28);">SENSOR&nbsp;&nbsp;</span>&nbsp;&nbsp;
            <span style="color:#39ff14;">CAM-OPTICAL ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _stat_card(label: str, value: str, color: str) -> str:
    return f"""
    <div style="
        background:{_BG_PANEL};padding:0.9rem 1rem;border-radius:8px;
        border:1px solid rgba({_ACCENT_RGB},0.1);
        border-top:2px solid {color};
        text-align:center;
    ">
        <p style="margin:0;color:rgba({_ACCENT_RGB},0.5);font-size:0.62rem;
            font-weight:700;letter-spacing:0.12em;font-family:monospace;">{label}</p>
        <h2 style="margin:0.3rem 0 0;color:#e6edf3;font-size:1.4rem;
            font-weight:800;text-shadow:0 0 12px {color}88;">{value}</h2>
    </div>
    """


def _render_detailed_report(report: dict[str, Any]) -> None:
    color    = report.get('color', _ACCENT)
    severity = report.get('severity', 'UNKNOWN')

    sev_colors = {
        "LOW":      "#39ff14",
        "MODERATE": "#f4a261",
        "HIGH":     "#e63946",
        "CRITICAL": "#e63946",
    }
    sev_color = sev_colors.get(severity.upper(), color)

    _section("📋", "AUTOMATED BIOMECHANICAL ASSESSMENT")

    # Status banner
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});
        border:1px solid rgba({_ACCENT_RGB},0.15);
        border-left:4px solid {sev_color};
        border-radius:10px;padding:1rem 1.4rem;margin-bottom:0.75rem;
        display:flex;justify-content:space-between;align-items:center;
        box-shadow:0 0 20px {sev_color}12;
    ">
        <div>
            <div style="color:#e6edf3;font-size:1rem;font-weight:800;
                letter-spacing:0.06em;">{report.get('status','ANALYSIS COMPLETE')}</div>
            <div style="color:#484f58;font-size:0.65rem;letter-spacing:0.12em;
                margin-top:3px;font-family:monospace;">
                CODE: {report.get('sys_code','N/A')}&nbsp;&nbsp;|&nbsp;&nbsp;
                TS: {report.get('timestamp','--')}
            </div>
        </div>
        <div style="
            background:rgba({_ACCENT_RGB},0.06);color:{sev_color};
            border:1px solid {sev_color}55;border-radius:20px;
            padding:5px 16px;font-size:0.68rem;font-weight:800;
            letter-spacing:0.18em;text-shadow:0 0 10px {sev_color}88;
        ">SEVERITY: {severity}</div>
    </div>
    """, unsafe_allow_html=True)

    # 4-stat grid
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.75rem;">
        {_stat_card("OPTICAL RETENTION",  report.get('presence_rate','0%'),  "#00f0ff")}
        {_stat_card("AXIAL ALIGNMENT",    report.get('centered_rate','0%'),  _ACCENT)}
        {_stat_card("KINEMATIC ENTROPY",  report.get('kinematic_entropy','0'), "#f4a261")}
        {_stat_card("PHYSICAL VARIANCE",  report.get('variance','0'),          "#bc8cff")}
    </div>
    """, unsafe_allow_html=True)

    # Clinical notes
    st.markdown(f"""
    <div style="
        background:{_BG_PANEL};border:1px solid rgba({_ACCENT_RGB},0.12);
        border-radius:10px;padding:1.2rem 1.4rem;margin-bottom:0.6rem;
    ">
        <div style="color:rgba({_ACCENT_RGB},0.7);font-size:0.68rem;font-weight:700;
            letter-spacing:0.18em;margin-bottom:0.7rem;font-family:monospace;">
            🩺&nbsp; AI CLINICAL OBSERVATIONS
        </div>
        <div style="color:#c9d1d9;font-size:0.88rem;line-height:1.75;">
            {report.get('clinical_notes','Detailed clinical notes are being processed...')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recommendation
    st.markdown(f"""
    <div style="
        background:#0c1400;border:1px solid rgba(244,162,97,0.25);
        border-left:3px solid #f4a261;
        border-radius:8px;padding:0.9rem 1.2rem;
    ">
        <div style="color:#f4a261;font-size:0.68rem;font-weight:700;
            letter-spacing:0.18em;margin-bottom:0.5rem;font-family:monospace;">
            ⚡&nbsp; ACTIONABLE RECOMMENDATION
        </div>
        <p style="margin:0;color:#c9a96e;font-size:0.88rem;line-height:1.6;">
            {report.get('recommendation','Maintain standard ergonomic guidelines.')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <p style="text-align:center;color:#484f58;font-size:0.65rem;
        margin-top:1rem;padding-top:0.75rem;
        border-top:1px dashed rgba({_ACCENT_RGB},0.1);letter-spacing:0.05em;">
        Generated by optical heuristics &amp; ML algorithms.
        Strictly observational — not a medical diagnosis.
        Consult a licensed healthcare professional.
    </p>
    """, unsafe_allow_html=True)


def _render_config(config: dict) -> None:
    st.markdown(
        f"<p style='color:rgba({_ACCENT_RGB},0.6);font-size:0.7rem;"
        f"font-weight:700;letter-spacing:0.14em;margin-bottom:0.4rem;'>"
        f"⚙️  ACTIVE CONFIGURATION</p>",
        unsafe_allow_html=True,
    )
    st.json(config, expanded=False)


@st.fragment(run_every=0.5)
def health_widget(view_model):
    
    _css()
    _render_header()
    _divider()

    col_feed, col_metrics = st.columns([1.5, 1], gap="medium")

    with col_feed:
        st.markdown(
            f"<p style='color:rgba({_ACCENT_RGB},0.7);font-size:0.7rem;"
            f"font-weight:700;letter-spacing:0.18em;margin-bottom:0.4rem;'>"
            f"📹  LIVE TELEMETRY FEED</p>",
            unsafe_allow_html=True,
        )
        # ── CAMERA — UNTOUCHED ────────────────────────────────────────────────
        frame, signals = HealthCameraEngine.get_frame()
        if frame is not None:
            view_model.on_frame_update(frame, signals)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode(".jpg", rgb, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

            st.markdown(f"""
            <div style="border:1px solid rgba({_ACCENT_RGB},0.22);border-radius:10px;
                overflow:hidden;box-shadow:0 0 28px rgba({_ACCENT_RGB},0.07),
                inset 0 0 20px rgba(0,0,0,0.4);margin-bottom:0.25rem;">
            """, unsafe_allow_html=True)
            st.image(buffer.tobytes(), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Feed footer strip
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;
                font-size:0.63rem;color:rgba({_ACCENT_RGB},0.38);
                letter-spacing:0.1em;font-family:monospace;margin-top:4px;">
                <span>FEED: CAM-HEALTH-01</span>
                <span>QUALITY: 70%</span>
                <span>AI: ACTIVE</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:{_BG_PANEL};border:1px solid rgba({_ACCENT_RGB},0.15);
                border-radius:10px;padding:2rem;text-align:center;">
                <div style="color:#484f58;font-size:0.75rem;letter-spacing:0.15em;">
                    ⚠️&nbsp; CAMERA NOT ACCESSIBLE
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_metrics:
        _render_metrics(view_model.health_metrics)

    _divider()

    # ── Analysis state ────────────────────────────────────────────────────────
    if view_model.is_analyzing:
        _section("⏳", "COMPILING BIOMETRIC REPORT")
        prog_pct = int(view_model.analysis_progress * 100)
        st.markdown(f"""
        <div style="font-size:0.7rem;color:rgba({_ACCENT_RGB},0.6);
            letter-spacing:0.1em;margin-bottom:0.4rem;font-family:monospace;">
            ANALYZING SPATIAL DATA WINDOW — {prog_pct}%
        </div>
        """, unsafe_allow_html=True)
        st.progress(view_model.analysis_progress)
    else:
        st.markdown(f"""
        <div style="background:#0d2010;border:1px solid rgba({_ACCENT_RGB},0.25);
            border-left:3px solid {_ACCENT};border-radius:8px;
            padding:0.65rem 1rem;margin-bottom:0.75rem;
            color:{_ACCENT};font-size:0.8rem;letter-spacing:0.06em;">
            ✅&nbsp;&nbsp;Analysis complete — all biometric streams nominal.
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            if st.button("🔄  START NEW DIAGNOSTIC SCAN",
                         type="primary", use_container_width=True):
                view_model.restart_analysis()
                st.rerun()

        _render_detailed_report(view_model.report_data)

    _divider()

    with st.expander("⚙️  ACTIVE CONFIGURATION", expanded=False):
        _render_config(view_model.current_config)