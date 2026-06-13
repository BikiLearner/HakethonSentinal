"""
ui/screens/config_screen.py
"""

import streamlit as st
from core.mode_controller import detect_mode_from_config
from data.config.config_loader import load_config


def _render_header() -> None:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            border-left: 4px solid #58a6ff;
            border-radius: 6px;
            padding: 1.2rem 1.6rem;
            margin-bottom: 0.25rem;
        ">
            <h1 style="color:#e6edf3; margin:0; font-size:1.75rem; letter-spacing:0.03em;">
                ⚙️ Configuration Panel
            </h1>
            <p style="color:#8b949e; margin:0.3rem 0 0; font-size:0.82rem; letter-spacing:0.08em;">
                UPLOAD A CONFIG FILE TO INITIALISE SYSTEM MODE
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_upload_zone() -> bytes | None:
    st.markdown("##### 📁 Upload Configuration File")
    uploaded = st.file_uploader(
        label="Accepted formats: .txt, .doc",
        type=["txt", "doc"],
        label_visibility="collapsed",
    )
    return uploaded.read() if uploaded else None


def _render_mode_badge(mode: str) -> None:
    palette = {
        "industrial": ("#0d2137", "#58a6ff", "🏭"),
        "health":     ("#0d2d1f", "#3fb950", "🧑‍⚕️"),
        "planner":    ("#1f1a0d", "#d29922", "📋"),
    }
    bg, fg, icon = palette.get(mode.lower(), ("#161b22", "#8b949e", "❓"))
    st.markdown(
        f"""
        <div style="
            background:{bg};
            border:1px solid {fg};
            border-radius:6px;
            padding:0.75rem 1.2rem;
            display:flex;
            align-items:center;
            gap:0.75rem;
            margin-top:0.5rem;
        ">
            <span style="font-size:1.5rem;">{icon}</span>
            <div>
                <div style="color:{fg}; font-weight:700; font-size:0.95rem;
                            letter-spacing:0.08em;">
                    MODE ACTIVATED: {mode.upper()}
                </div>
                <div style="color:{fg}99; font-size:0.73rem; margin-top:0.1rem;">
                    System behaviour will update across all screens
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_config_preview(content: str) -> None:
    st.markdown("##### 📄 Uploaded Configuration")
    st.code(content, language="text")


def config_screen(app_state) -> None:
    _render_header()
    st.divider()

    raw = _render_upload_zone()

    if raw is None:
        st.info("ℹ️ No configuration loaded. Upload a file to begin.", icon=None)
        return

    content = raw.decode("utf-8", errors="replace")

    config_dict = load_config(content)
    mode = detect_mode_from_config(config_dict)
    
    app_state.update_state(mode, config_dict)

    st.divider()
    st.markdown("##### ✅ Detection Result")
    _render_mode_badge(mode)

    st.divider()
    _render_config_preview(content)
