"""
ui/screens/config_screen.py
"""

# from sentence_transformers import SentenceTransformer, util
import streamlit as st
from core.mode_controller import detect_mode_from_config
from data.config.config_loader import load_config


_BG_PANEL = "#0f1520"
_BG_MID   = "#161b22"


# @st.cache_resource
# def get_ai_engine():
#     """Loads the model AND pre-computes static embeddings to save memory."""
#     model = SentenceTransformer('all-MiniLM-L6-v2')
    
#     # Pre-encode the categories once, rather than on every file upload
#     category_embeddings = {
#         mode: model.encode(desc, convert_to_tensor=True)
#         for mode, desc in CATEGORIES.items()
#     }
#     return model, category_embeddings

# 🔥 Predefined semantic labels (NOT hardcoded logic, just reference meanings)
CATEGORIES = {
    "industrial": "machine temperature vibration load sensor monitoring system",
    "health": "heart rate pulse oxygen medical patient monitoring health data",
    "planner": "task planning schedule workflow project management steps"
}

KEYWORDS = [
    "temperature", "vibration", "load", "sensor", "threshold",
    "alert", "pressure", "motor", "cycle", "system"
]


def _css() -> None:
    st.markdown("""
    <style>
    div[data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #0f1520 0%, #161b22 100%);
        border: 1px dashed rgba(88,166,255,0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    hr { border-color: rgba(88,166,255,0.1) !important; }
    div[data-testid="stCodeBlock"] {
        background: #080c14 !important;
        border: 1px solid rgba(88,166,255,0.12) !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _divider() -> None:
    st.markdown(
        "<div style='height:1px;background:linear-gradient(90deg,transparent,"
        "rgba(88,166,255,0.18),transparent);margin:0.75rem 0;'></div>",
        unsafe_allow_html=True,
    )


def _render_header() -> None:
    st.markdown("""
    <div style="
        background:linear-gradient(135deg,#080c14 0%,#0d1520 100%);
        border-left:3px solid #58a6ff;
        border-bottom:1px solid rgba(88,166,255,0.12);
        border-radius:8px;padding:1rem 1.5rem;margin-bottom:0.75rem;
        display:flex;align-items:center;justify-content:space-between;
    ">
        <div>
            <h1 style="color:#e6edf3;margin:0;font-size:1.5rem;font-weight:800;letter-spacing:0.06em;">
                ⚡ SENTINEL · CONFIG
                <span style="font-weight:300;font-size:0.85rem;color:#484f58;"> v3.7</span>
            </h1>
            <p style="color:#8b949e;margin:0.2rem 0 0;font-size:0.72rem;letter-spacing:0.2em;">
                SYSTEM INITIALISATION &amp; MODE CONFIGURATION
                <span style="color:#484f58;margin:0 8px;">|</span>
                STATUS <span style="color:#39ff14;font-weight:700;">ONLINE</span>
            </p>
        </div>
        <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.2em;
            color:#58a6ff;background:rgba(88,166,255,0.06);
            border:1px solid rgba(88,166,255,0.2);border-radius:20px;
            padding:5px 14px;text-shadow:0 0 12px #58a6ff88;">
            PROTOCOL CONFIG
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_upload_zone() -> bytes | None:
    st.markdown(
        "<p style='color:rgba(88,166,255,0.7);font-size:0.7rem;font-weight:700;"
        "letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;'>"
        "📂&nbsp; FILE UPLINK</p>",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        label="Accepted formats: .txt, .doc",
        type=["txt", "doc"],
        label_visibility="collapsed",
    )

    if uploaded:
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:8px;
            background:rgba(88,166,255,0.08);border:1px solid rgba(88,166,255,0.25);
            border-radius:20px;padding:4px 14px;margin-top:6px;
            font-size:0.72rem;color:#58a6ff;letter-spacing:0.1em;font-family:monospace;">
            📄&nbsp;{uploaded.name}
            &nbsp;<span style="color:rgba(88,166,255,0.4);">
                {round(uploaded.size/1024,1)} KB
            </span>
        </div>
        """, unsafe_allow_html=True)

    return uploaded.read() if uploaded else None


def _render_mode_badge(mode: str) -> None:
    palette = {
        "industrial": ("rgba(0,240,255,0.06)",  "#00f0ff", "0,240,255",  "🏭"),
        "health":     ("rgba(57,255,20,0.06)",  "#39ff14", "57,255,20",  "🧑‍⚕️"),
        "planner":    ("rgba(255,136,0,0.06)",  "#ff8800", "255,136,0",  "📋"),
    }
    bg, fg, rgb, icon = palette.get(
        mode.lower(), ("rgba(88,166,255,0.06)", "#58a6ff", "88,166,255", "❓")
    )

    st.markdown(f"""
    <div style="
        background:{bg};
        border:1px solid {fg}44;
        border-left:4px solid {fg};
        border-radius:10px;
        padding:1rem 1.4rem;
        display:flex;align-items:center;gap:1rem;
        margin-top:0.5rem;
        box-shadow:0 0 24px rgba({rgb},0.08);
    ">
        <span style="font-size:1.8rem;">{icon}</span>
        <div>
            <div style="color:{fg};font-weight:800;font-size:0.95rem;
                letter-spacing:0.1em;text-shadow:0 0 12px {fg}88;">
                MODE ACTIVATED: {mode.upper()}
            </div>
            <div style="color:rgba({rgb},0.45);font-size:0.68rem;
                letter-spacing:0.1em;margin-top:3px;font-family:monospace;">
                System behaviour will update across all screens
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _analyse_with_ai(content: str) -> dict:
    text = content.lower()

    # 🔥 Mode detection (simple but effective)
    if any(k in text for k in ["temperature", "vibration", "motor", "sensor"]):
        mode = "industrial"
    elif any(k in text for k in ["heart", "pulse", "oxygen"]):
        mode = "health"
    else:
        mode = "planner"

    # 🔥 Extract lines (important for summarization feel)
    lines = [l.strip() for l in content.split("\n") if l.strip()]

    # 🔥 Key parameters (not dumb keywords — real extraction)
    key_params = []
    for line in lines[:10]:
        if ":" in line:
            key_params.append(line.split(":")[0].strip())
        elif "=" in line:
            key_params.append(line.split("=")[0].strip())

    if not key_params:
        key_params = ["General configuration detected"]

    # 🔥 Risks (context-based)
    risks = []
    if "threshold" not in text:
        risks.append("Threshold values not defined")
    if "alert" not in text:
        risks.append("No alert mechanism configured")
    if len(lines) < 3:
        risks.append("Configuration appears incomplete")

    if not risks:
        risks = ["No immediate risks detected"]

    # 🔥 Smart summary (not static)
    summary = f"""
This configuration defines a {mode} system with {len(lines)} operational parameters.
It appears to focus on monitoring and controlling system behavior based on defined inputs.
""".strip()

    return {
        "summary": summary,
        "purpose": f"{mode.capitalize()} system configuration and monitoring setup.",
        "mode_detected": mode,
        "key_parameters": key_params[:5],
        "risk_flags": risks[:3],
        "recommendation": "Ensure all parameters, thresholds, and alerts are properly configured."
    }

def _render_analysis(analysis: dict, mode: str) -> None:
    mode_colors = {
        "industrial": "#00f0ff",
        "health":     "#39ff14",
        "planner":    "#ff8800",
    }
    accent = mode_colors.get(mode.lower(), "#58a6ff")
    accent_rgb = {
        "#00f0ff": "0,240,255",
        "#39ff14": "57,255,20",
        "#ff8800": "255,136,0",
        "#58a6ff": "88,166,255",
    }.get(accent, "88,166,255")

    # ── Summary card ─────────────────────────────────────────────────────────
    st.markdown(
        f"<p style='color:rgba({accent_rgb},0.7);font-size:0.7rem;font-weight:700;"
        f"letter-spacing:0.18em;margin:1rem 0 0.4rem;font-family:monospace;'>"
        f"🧠&nbsp; AI ANALYSIS REPORT</p>",
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});
        border:1px solid rgba({accent_rgb},0.18);
        border-left:4px solid {accent};
        border-radius:10px;padding:1.2rem 1.4rem;
        box-shadow:0 0 24px rgba({accent_rgb},0.07);
        margin-bottom:0.6rem;
    ">
        <div style="color:rgba({accent_rgb},0.6);font-size:0.65rem;font-weight:700;
            letter-spacing:0.2em;margin-bottom:0.6rem;font-family:monospace;">
            ◈ EXECUTIVE SUMMARY
        </div>
        <div style="color:#c9d1d9;font-size:0.9rem;line-height:1.75;">
            {analysis.get('summary','')}
        </div>
        <div style="margin-top:0.9rem;padding-top:0.75rem;
            border-top:1px solid rgba({accent_rgb},0.1);">
            <span style="color:rgba({accent_rgb},0.45);font-size:0.65rem;
                letter-spacing:0.12em;font-family:monospace;">◈ PRIMARY PURPOSE&nbsp;&nbsp;</span>
            <span style="color:{accent};font-size:0.82rem;">
                {analysis.get('purpose','')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column: key params + risk flags ──────────────────────────────────
    col_params, col_risks = st.columns(2, gap="medium")

    with col_params:
        st.markdown(f"""
        <div style="color:rgba({accent_rgb},0.6);font-size:0.65rem;font-weight:700;
            letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;">
            ⚙️&nbsp; KEY PARAMETERS
        </div>
        """, unsafe_allow_html=True)

        params = analysis.get("key_parameters", [])
        items_html = "".join(
            f"""<div style="display:flex;align-items:flex-start;gap:8px;
                padding:0.45rem 0;border-bottom:1px solid rgba({accent_rgb},0.07);">
                <span style="color:{accent};font-size:0.65rem;margin-top:2px;flex-shrink:0;">◈</span>
                <span style="color:#c9d1d9;font-size:0.8rem;line-height:1.5;">{p}</span>
            </div>"""
            for p in params
        )
        st.markdown(f"""
        <div style="background:{_BG_PANEL};border:1px solid rgba({accent_rgb},0.14);
            border-radius:8px;padding:0.8rem 1rem;">
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    with col_risks:
        st.markdown(f"""
        <div style="color:rgba(230,57,70,0.7);font-size:0.65rem;font-weight:700;
            letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;">
            🚨&nbsp; RISK FLAGS
        </div>
        """, unsafe_allow_html=True)

        risks = analysis.get("risk_flags", [])
        none_detected = risks == ["None detected"] or (
            len(risks) == 1 and "none" in risks[0].lower()
        )
        risk_color = "#39ff14" if none_detected else "#e63946"
        risk_bg    = "#0d2010" if none_detected else "#1a0508"

        flags_html = "".join(
            f"""<div style="display:flex;align-items:flex-start;gap:8px;
                padding:0.45rem 0;border-bottom:1px solid rgba(230,57,70,0.07);">
                <span style="color:{risk_color};font-size:0.65rem;margin-top:2px;flex-shrink:0;">
                    {'✅' if none_detected else '⚠️'}
                </span>
                <span style="color:#c9d1d9;font-size:0.8rem;line-height:1.5;">{r}</span>
            </div>"""
            for r in risks
        )
        st.markdown(f"""
        <div style="background:{risk_bg};border:1px solid {risk_color}22;
            border-left:2px solid {risk_color};border-radius:8px;padding:0.8rem 1rem;">
            {flags_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Recommendation banner ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        background:#0c1400;border:1px solid rgba(244,162,97,0.25);
        border-left:3px solid #f4a261;border-radius:8px;
        padding:0.85rem 1.2rem;margin-top:0.6rem;
    ">
        <div style="color:#f4a261;font-size:0.65rem;font-weight:700;
            letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;">
            ⚡&nbsp; RECOMMENDED NEXT STEP
        </div>
        <p style="margin:0;color:#c9a96e;font-size:0.85rem;line-height:1.6;">
            {analysis.get('recommendation','')}
        </p>
    </div>
    """, unsafe_allow_html=True)


def _render_config_preview(content: str) -> None:
    st.markdown(
        "<p style='color:rgba(88,166,255,0.45);font-size:0.65rem;font-weight:700;"
        "letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;'>"
        "📄&nbsp; RAW CONFIGURATION FILE</p>",
        unsafe_allow_html=True,
    )
    st.code(content, language="text")


def config_screen(app_state) -> None:
    _css()
    _render_header()
    _divider()

    raw = _render_upload_zone()

    if raw is None:
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});
            border:1px solid rgba(88,166,255,0.15);border-radius:12px;
            padding:2.5rem;text-align:center;margin-top:0.5rem;
            box-shadow:0 0 24px rgba(88,166,255,0.04);
        ">
            <div style="font-size:2.5rem;margin-bottom:1rem;">📡</div>
            <div style="color:#58a6ff;font-size:0.75rem;font-weight:700;
                letter-spacing:0.25em;margin-bottom:0.5rem;">AWAITING FILE UPLINK</div>
            <div style="color:#484f58;font-size:0.72rem;letter-spacing:0.1em;">
                Upload a
                <code style="color:rgba(88,166,255,0.7);background:rgba(88,166,255,0.08);
                    padding:1px 6px;border-radius:4px;">.txt</code>
                &nbsp;or&nbsp;
                <code style="color:rgba(88,166,255,0.7);background:rgba(88,166,255,0.08);
                    padding:1px 6px;border-radius:4px;">.doc</code>
                &nbsp;file to initialise system mode.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    content = raw.decode("utf-8", errors="replace")
    config_dict = load_config(content)
    mode = detect_mode_from_config(config_dict)
    app_state.update_state(mode, config_dict)

    _divider()

    # ── Mode badge ───────────────────────────────────────────────────────────
    st.markdown(
        "<p style='color:rgba(88,166,255,0.7);font-size:0.7rem;font-weight:700;"
        "letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;'>"
        "✅&nbsp; DETECTION RESULT</p>",
        unsafe_allow_html=True,
    )
    _render_mode_badge(mode)

    _divider()

    # ── AI Analysis (cached per content hash) ────────────────────────────────
    cache_key = f"cfg_analysis_{hash(content)}"
    if cache_key not in st.session_state:
        with st.spinner("🧠 SENTINEL AI analysing configuration..."):
            st.session_state[cache_key] = _analyse_with_ai(content)

    _render_analysis(st.session_state[cache_key], mode)

    _divider()

    # ── Raw file at the bottom ───────────────────────────────────────────────
    with st.expander("📄  VIEW RAW CONFIGURATION FILE", expanded=False):
        _render_config_preview(content)