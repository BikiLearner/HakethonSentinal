import streamlit as st
import cv2

from ui.components.video_engine import VideoEngine

# ── Palette mirroring robot_screen ──────────────────────────────────────────
_ACCENT     = "#00f0ff"
_ACCENT_RGB = "0,240,255"
_BG_DARK    = "#0d1117"
_BG_MID     = "#161b22"
_BG_PANEL   = "#0f1520"


def _css() -> None:
    st.markdown(f"""
    <style>
    /* ── Page base ── */
    section[data-testid="stMain"] > div {{
        background: {_BG_DARK};
    }}

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, {_BG_PANEL} 0%, {_BG_MID} 100%);
        border: 1px solid rgba({_ACCENT_RGB}, 0.18);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        box-shadow: 0 0 18px rgba({_ACCENT_RGB}, 0.05);
    }}
    div[data-testid="stMetricLabel"] p {{
        color: rgba({_ACCENT_RGB}, 0.7) !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.14em !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: #e6edf3 !important;
        font-size: 1.4rem !important;
        font-weight: 800 !important;
    }}
    div[data-testid="stMetricDelta"] svg {{ display: none; }}

    /* ── Expander ── */
    details summary {{
        color: rgba({_ACCENT_RGB}, 0.8) !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.1em !important;
        font-weight: 700 !important;
    }}
    details {{
        background: {_BG_PANEL} !important;
        border: 1px solid rgba({_ACCENT_RGB}, 0.15) !important;
        border-radius: 8px !important;
    }}

    /* ── Dividers ── */
    hr {{ border-color: rgba({_ACCENT_RGB}, 0.12) !important; }}
    </style>
    """, unsafe_allow_html=True)


def _panel(content_html: str) -> None:
    """Wrap content in a dark bordered panel."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {_BG_PANEL} 0%, {_BG_MID} 100%);
        border: 1px solid rgba({_ACCENT_RGB}, 0.18);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 0 24px rgba({_ACCENT_RGB}, 0.05);
        margin-bottom: 0.5rem;
    ">{content_html}</div>
    """, unsafe_allow_html=True)


def _section_label(text: str) -> None:
    st.markdown(
        f"<p style='color:rgba({_ACCENT_RGB},0.7);font-size:0.7rem;"
        f"font-weight:700;letter-spacing:0.18em;margin:0.75rem 0 0.4rem;'>"
        f"{text}</p>",
        unsafe_allow_html=True,
    )


def _render_header() -> None:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #080c14 0%, #0d1520 100%);
        border-left: 3px solid {_ACCENT};
        border-bottom: 1px solid rgba({_ACCENT_RGB}, 0.12);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div>
            <h1 style="color:#e6edf3;margin:0;font-size:1.5rem;font-weight:800;letter-spacing:0.06em;">
                ⚡ SENTINEL · INDUSTRIAL
                <span style="font-weight:300;font-size:0.85rem;color:#484f58;"> v3.7</span>
            </h1>
            <p style="color:#8b949e;margin:0.2rem 0 0;font-size:0.72rem;letter-spacing:0.2em;">
                REAL-TIME ZONE SURVEILLANCE &amp; TELEMETRY
                <span style="color:#484f58;margin:0 8px;">|</span>
                STATUS <span style="color:#39ff14;font-weight:700;">ONLINE</span>
            </p>
        </div>
        <div style="
            font-size:0.65rem;font-weight:700;letter-spacing:0.2em;
            color:{_ACCENT};background:rgba({_ACCENT_RGB},0.06);
            border:1px solid rgba({_ACCENT_RGB},0.2);
            border-radius:20px;padding:5px 14px;
            text-shadow:0 0 12px {_ACCENT}88;
        ">PROTOCOL INDUSTRIAL</div>
    </div>
    """, unsafe_allow_html=True)


@st.fragment
def _render_video_feed(view_model):
    frame, event, elapsed = VideoEngine.get_frame()
    view_model.on_frame_update(frame, event, elapsed)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Wrap in a styled container
    st.markdown(f"""
    <div style="
        border: 1px solid rgba({_ACCENT_RGB}, 0.22);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 0 30px rgba({_ACCENT_RGB}, 0.08), inset 0 0 20px rgba(0,0,0,0.4);
        margin-bottom: 0.25rem;
    ">
    """, unsafe_allow_html=True)
    st.image(frame, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_telemetry(telemetry: dict) -> None:
    _section_label("⚙️  LIVE TELEMETRY")

    temperature = telemetry.get("temperature", "—")
    vibration   = telemetry.get("vibration", "—")
    status      = telemetry.get("status", "UNKNOWN")
    uptime      = telemetry.get("uptime_hrs", "—")

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("🌡️  TEMPERATURE", f"{temperature} °C",
                  delta=telemetry.get("temperature_delta"))
        st.metric("📡  UPTIME", f"{uptime} hrs")
    with col_b:
        st.metric("📳  VIBRATION", f"{vibration} Hz",
                  delta=telemetry.get("vibration_delta"))
        _render_status_badge(status)


def _render_status_badge(status: str) -> None:
    palette = {
        "SAFE":     ("#0d2818", "#39ff14", "✅"),
        "WARNING":  ("#1e1400", "#f4a261", "⚠️"),
        "CRITICAL": ("#1a0508", "#e63946", "🔴"),
    }
    bg, fg, icon = palette.get(status.upper(), ("#1a1a1a", "#8b949e", "❓"))

    st.markdown(f"""
    <div style="
        background:{bg};
        border:1px solid {fg}55;
        border-radius:8px;
        padding:0.65rem 0.8rem;
        margin-top:0.5rem;
        text-align:center;
        box-shadow: 0 0 16px {fg}22;
    ">
        <span style="font-size:1.3rem;">{icon}</span>
        <div style="color:{fg};font-weight:800;letter-spacing:0.14em;
                    font-size:0.85rem;margin-top:0.1rem;
                    text-shadow:0 0 10px {fg}88;">
            {status}
        </div>
        <div style="color:{fg}66;font-size:0.65rem;letter-spacing:0.1em;margin-top:1px;">
            SYSTEM STATUS
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_alerts(alert_message: str | None) -> None:
    _section_label("🚨  ALERT PANEL")

    if not alert_message:
        st.markdown(f"""
        <div style="
            background:linear-gradient(90deg,#0d2010,#0d1117);
            border:1px solid #39ff1433;
            border-left:3px solid #39ff14;
            border-radius:8px;padding:0.7rem 1rem;
            color:#39ff14;font-size:0.82rem;letter-spacing:0.06em;
        ">✅ &nbsp;All zones nominal — no active alerts.</div>
        """, unsafe_allow_html=True)
        return

    lower = alert_message.lower()

    if "critical" in lower:
        border = "#e63946"; bg = "#1a0508"
        icon = "🔴"
    elif "warning" in lower or "detected" in lower:
        border = "#f4a261"; bg = "#1e1200"
        icon = "⚠️"
    else:
        border = _ACCENT; bg = "#081420"
        icon = "ℹ️"

    st.markdown(f"""
    <div style="
        background:{bg};
        border:1px solid {border}44;
        border-left:3px solid {border};
        border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;
        color:{border};font-size:0.82rem;letter-spacing:0.04em;
        box-shadow:0 0 14px {border}18;
    ">{icon} &nbsp;{alert_message}</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        background:#1e1200;border:1px solid #f4a26144;border-left:3px solid #f4a261;
        border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.5rem;
        color:#f4a261;font-size:0.8rem;letter-spacing:0.04em;
    ">⚠️ &nbsp;Human detected in restricted zone — verify clearance.</div>
    <div style="
        background:#1a0508;border:1px solid #e6394644;border-left:3px solid #e63946;
        border-radius:8px;padding:0.65rem 1rem;
        color:#e63946;font-size:0.8rem;letter-spacing:0.04em;
        box-shadow:0 0 12px #e6394618;
    ">🔴 &nbsp;CRITICAL: Unsafe human–machine interaction flagged.</div>
    """, unsafe_allow_html=True)


def _render_config(config: dict) -> None:
    _section_label("⚙️  ACTIVE CONFIGURATION")
    st.json(config, expanded=False)


@st.fragment(run_every=0.03)
def industrial_widget(view_model) -> None:
    _css()
    _render_header()

    # ── Main layout: video left | telemetry right ────────────────────────────
    col_feed, col_telem = st.columns([1.65, 1], gap="medium")

    with col_feed:
        st.markdown(
            f"<p style='color:rgba({_ACCENT_RGB},0.7);font-size:0.7rem;"
            f"font-weight:700;letter-spacing:0.18em;margin-bottom:0.4rem;'>"
            f"📹  ZONE CAMERA FEED</p>",
            unsafe_allow_html=True,
        )
        _render_video_feed(view_model)

        # ── Scan-line decorative footer under video ──
        st.markdown(f"""
        <div style="
            background:linear-gradient(90deg,transparent,rgba({_ACCENT_RGB},0.06),transparent);
            height:1px;margin:0.3rem 0 0.6rem;
        "></div>
        <div style="display:flex;justify-content:space-between;
                    font-size:0.65rem;color:rgba({_ACCENT_RGB},0.4);
                    letter-spacing:0.12em;font-family:monospace;">
            <span>FEED: CAM-01</span>
            <span>RES: 640×360</span>
            <span>AI: ACTIVE</span>
        </div>
        """, unsafe_allow_html=True)

    with col_telem:
        _render_telemetry(view_model.telemetry_data)

        # ── Divider ──
        st.markdown(
            f"<div style='height:1px;background:linear-gradient(90deg,"
            f"transparent,rgba({_ACCENT_RGB},0.15),transparent);"
            f"margin:0.75rem 0;'></div>",
            unsafe_allow_html=True,
        )

        # ── Compact HUD data rows ──
        st.markdown(f"""
        <div style="
            background:{_BG_PANEL};border:1px solid rgba({_ACCENT_RGB},0.12);
            border-radius:8px;padding:0.6rem 0.9rem;
            font-family:monospace;font-size:0.7rem;
            color:rgba({_ACCENT_RGB},0.5);letter-spacing:0.08em;
        ">
            <div style="margin-bottom:4px;">
                <span style="color:rgba({_ACCENT_RGB},0.3);">PROTOCOL</span>
                &nbsp;&nbsp;
                <span style="color:{_ACCENT};">INDUSTRIAL-MODE</span>
            </div>
            <div style="margin-bottom:4px;">
                <span style="color:rgba({_ACCENT_RGB},0.3);">ZONES</span>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span style="color:#39ff14;">3 ACTIVE</span>
            </div>
            <div>
                <span style="color:rgba({_ACCENT_RGB},0.3);">AI MODEL</span>
                &nbsp;&nbsp;
                <span style="color:{_ACCENT};">SENTINEL v3.7</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Alert panel ──────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='height:1px;background:linear-gradient(90deg,"
        f"transparent,rgba({_ACCENT_RGB},0.12),transparent);"
        f"margin:0.6rem 0;'></div>",
        unsafe_allow_html=True,
    )
    _render_alerts(view_model.alert_message)

    # ── Config expander ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("⚙️  ACTIVE CONFIGURATION", expanded=False):
        _render_config(view_model.current_config)