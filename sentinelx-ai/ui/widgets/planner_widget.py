import streamlit as st
import os

_ACCENT     = "#ff8800"
_ACCENT_RGB = "255,136,0"
_BG_DARK    = "#0d1117"
_BG_MID     = "#161b22"
_BG_PANEL   = "#0f1520"


def _css() -> None:
    st.markdown(f"""
    <style>
    div[data-testid="stFileUploader"] {{
        background: linear-gradient(135deg, {_BG_PANEL} 0%, {_BG_MID} 100%);
        border: 1px dashed rgba({_ACCENT_RGB}, 0.35);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 0 20px rgba({_ACCENT_RGB}, 0.05);
    }}
    div[data-testid="stFileUploader"] label {{
        color: rgba({_ACCENT_RGB}, 0.8) !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.12em !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stExpander"] {{
        background: {_BG_PANEL} !important;
        border: 1px solid rgba({_ACCENT_RGB}, 0.15) !important;
        border-radius: 8px !important;
    }}
    hr {{ border-color: rgba({_ACCENT_RGB}, 0.12) !important; }}
    div[data-testid="stCodeBlock"] {{
        background: #080c14 !important;
        border: 1px solid rgba({_ACCENT_RGB}, 0.12) !important;
        border-radius: 8px !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def _section(icon: str, label: str) -> None:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin:1.2rem 0 0.5rem;">
        <span style="font-size:1rem;">{icon}</span>
        <span style="color:rgba({_ACCENT_RGB},0.75);font-size:0.7rem;font-weight:700;
            letter-spacing:0.2em;font-family:'Segoe UI',monospace;">{label}</span>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,
            rgba({_ACCENT_RGB},0.25),transparent);margin-left:6px;"></div>
    </div>
    """, unsafe_allow_html=True)


def _card(content_html: str, glow: bool = False) -> None:
    shadow = f"0 0 24px rgba({_ACCENT_RGB},0.08)" if glow else "none"
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,{_BG_PANEL} 0%,{_BG_MID} 100%);
        border:1px solid rgba({_ACCENT_RGB},0.18);
        border-radius:10px;padding:1rem 1.2rem;
        box-shadow:{shadow};margin-bottom:0.5rem;
    ">{content_html}</div>
    """, unsafe_allow_html=True)


def _alert(text: str, kind: str = "info") -> None:
    colors = {
        "info":    ("#081420", _ACCENT,    "ℹ️"),
        "success": ("#0d2010", "#39ff14",  "✅"),
        "error":   ("#1a0508", "#e63946",  "🔴"),
        "warning": ("#1e1200", "#f4a261",  "⚠️"),
    }
    bg, fg, icon = colors.get(kind, colors["info"])
    st.markdown(f"""
    <div style="background:{bg};border:1px solid {fg}44;border-left:3px solid {fg};
        border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;
        color:{fg};font-size:0.82rem;letter-spacing:0.04em;
        box-shadow:0 0 14px {fg}14;">
        {icon}&nbsp;&nbsp;{text}
    </div>
    """, unsafe_allow_html=True)


def planner_widget(view_model):
    _css()

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,#080c14 0%,#0d1520 100%);
        border-left:3px solid {_ACCENT};
        border-bottom:1px solid rgba({_ACCENT_RGB},0.12);
        border-radius:8px;padding:1rem 1.5rem;margin-bottom:1rem;
        display:flex;align-items:center;justify-content:space-between;
    ">
        <div>
            <h1 style="color:#e6edf3;margin:0;font-size:1.5rem;font-weight:800;letter-spacing:0.06em;">
                ⚡ SENTINEL · PLANNER
                <span style="font-weight:300;font-size:0.85rem;color:#484f58;"> v3.7</span>
            </h1>
            <p style="color:#8b949e;margin:0.2rem 0 0;font-size:0.72rem;letter-spacing:0.2em;">
                AI-POWERED FILE ANALYSIS &amp; STRATEGIC BREAKDOWN
                <span style="color:#484f58;margin:0 8px;">|</span>
                STATUS <span style="color:#39ff14;font-weight:700;">ONLINE</span>
            </p>
        </div>
        <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.2em;
            color:{_ACCENT};background:rgba({_ACCENT_RGB},0.06);
            border:1px solid rgba({_ACCENT_RGB},0.2);border-radius:20px;
            padding:5px 14px;text-shadow:0 0 12px {_ACCENT}88;">
            PROTOCOL PLANNER
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload zone ───────────────────────────────────────────────────────────
    _section("📂", "FILE UPLINK")
    uploaded_file = st.file_uploader(
        "Upload a .py, .txt, .md, or .docx file",
        type=["txt", "py", "md", "doc", "docx"],
        on_change=view_model.clear_all,
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        # File chip
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:8px;
            background:rgba({_ACCENT_RGB},0.08);border:1px solid rgba({_ACCENT_RGB},0.25);
            border-radius:20px;padding:4px 14px;margin-top:6px;
            font-size:0.72rem;color:{_ACCENT};letter-spacing:0.1em;font-family:monospace;">
            📄&nbsp;{uploaded_file.name}
            &nbsp;<span style="color:rgba({_ACCENT_RGB},0.45);">
                {round(uploaded_file.size/1024,1)} KB
            </span>
        </div>
        """, unsafe_allow_html=True)

        if not view_model.input_content and not view_model.is_loading:
            view_model.on_file_uploaded(uploaded_file)

    st.markdown(
        f"<div style='height:1px;background:linear-gradient(90deg,transparent,"
        f"rgba({_ACCENT_RGB},0.15),transparent);margin:1rem 0;'></div>",
        unsafe_allow_html=True,
    )

    # ── States ────────────────────────────────────────────────────────────────

    if view_model.is_loading:
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});
            border:1px solid rgba({_ACCENT_RGB},0.2);border-radius:12px;
            padding:2rem;text-align:center;
            box-shadow:0 0 30px rgba({_ACCENT_RGB},0.06);
        ">
            <div style="font-size:2rem;margin-bottom:0.75rem;">🤖</div>
            <div style="color:{_ACCENT};font-size:0.75rem;font-weight:700;
                letter-spacing:0.25em;">MODEL ANALYZING FILE...</div>
            <div style="color:#484f58;font-size:0.68rem;letter-spacing:0.1em;
                margin-top:0.4rem;">PLEASE STAND BY</div>
        </div>
        """, unsafe_allow_html=True)
        with st.spinner(""):
            pass

    elif view_model.error_message:
        _alert(f"<b>Analysis Failed:</b> {view_model.error_message}", "error")
        _alert("Check your API key, file content, or try again later.", "warning")

    elif view_model.output_content:
        _alert("Analysis complete. All systems nominal.", "success")

        output = view_model.output_content

        # ── Summary ──
        _section("📌", "SUMMARY")
        _card(f"<p style='color:#c9d1d9;font-size:0.88rem;line-height:1.7;margin:0;'>"
              f"{output.get('summary','Not available.')}</p>", glow=True)

        # ── Complexity ──
        _section("⚡", "COMPLEXITY ANALYSIS")
        st.code(output.get('complexity', 'Not available.'), language='text')

        # ── Improvements ──
        _section("🚀", "RECOMMENDED IMPROVEMENTS")
        improvements = output.get('improvements', [])
        if improvements:
            items_html = "".join(
                f"""<div style="display:flex;align-items:flex-start;gap:10px;
                    padding:0.5rem 0;border-bottom:1px solid rgba({_ACCENT_RGB},0.07);">
                    <span style="color:{_ACCENT};font-size:0.7rem;margin-top:2px;
                        flex-shrink:0;">◈</span>
                    <span style="color:#c9d1d9;font-size:0.85rem;line-height:1.6;">{item}</span>
                </div>"""
                for item in improvements
            )
            _card(items_html)
        else:
            _alert("No specific improvements suggested.", "info")

        # ── Use Case ──
        _section("🌍", "USE CASE")
        _card(f"<p style='color:#c9d1d9;font-size:0.88rem;line-height:1.7;margin:0;'>"
              f"{output.get('use_case','Not available.')}</p>")

        # ── Step-by-step ──
        _section("🧭", "STEP-BY-STEP EXECUTION PLAN")
        steps = output.get('step_by_step', [])
        if steps:
            steps_html = "".join(
                f"""<div style="display:flex;align-items:flex-start;gap:12px;
                    padding:0.55rem 0;border-bottom:1px solid rgba({_ACCENT_RGB},0.07);">
                    <span style="color:{_ACCENT};font-size:0.7rem;font-weight:800;
                        font-family:monospace;flex-shrink:0;margin-top:2px;">
                        {str(i).zfill(2)}
                    </span>
                    <span style="color:#c9d1d9;font-size:0.85rem;line-height:1.6;">{step}</span>
                </div>"""
                for i, step in enumerate(steps, 1)
            )
            _card(steps_html)
        else:
            _alert("No step-by-step plan provided.", "info")

        st.markdown(
            f"<div style='height:1px;background:linear-gradient(90deg,transparent,"
            f"rgba({_ACCENT_RGB},0.15),transparent);margin:1rem 0;'></div>",
            unsafe_allow_html=True,
        )

        # ── Original file ──
        with st.expander("📄  VIEW ORIGINAL UPLOADED CONTENT"):
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            lang = 'python' if file_extension == '.py' else 'text'
            st.code(view_model.input_content, language=lang)

    else:
        # ── Initial idle state ────────────────────────────────────────────────
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});
            border:1px solid rgba({_ACCENT_RGB},0.15);border-radius:12px;
            padding:2.5rem;text-align:center;
            box-shadow:0 0 24px rgba({_ACCENT_RGB},0.04);
        ">
            <div style="font-size:2.5rem;margin-bottom:1rem;">📡</div>
            <div style="color:{_ACCENT};font-size:0.75rem;font-weight:700;
                letter-spacing:0.25em;margin-bottom:0.5rem;">AWAITING FILE UPLINK</div>
            <div style="color:#484f58;font-size:0.72rem;letter-spacing:0.1em;
                line-height:1.8;">
                Upload a <code style="color:rgba({_ACCENT_RGB},0.7);
                background:rgba({_ACCENT_RGB},0.08);padding:1px 6px;
                border-radius:4px;">.py</code>&nbsp;
                <code style="color:rgba({_ACCENT_RGB},0.7);
                background:rgba({_ACCENT_RGB},0.08);padding:1px 6px;
                border-radius:4px;">.txt</code>&nbsp;
                <code style="color:rgba({_ACCENT_RGB},0.7);
                background:rgba({_ACCENT_RGB},0.08);padding:1px 6px;
                border-radius:4px;">.md</code>&nbsp;or&nbsp;
                <code style="color:rgba({_ACCENT_RGB},0.7);
                background:rgba({_ACCENT_RGB},0.08);padding:1px 6px;
                border-radius:4px;">.docx</code>
                &nbsp;to begin AI analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)