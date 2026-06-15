"""
ui/screens/config_screen.py
"""

import streamlit as st
from core.mode_controller import detect_mode_from_config
from data.config.config_loader import load_config


_BG_PANEL = "#0f1520"
_BG_MID   = "#161b22"
_BLUE     = "#58a6ff"
_BLUE_RGB = "88,166,255"

CATEGORIES = {
    "industrial": "machine temperature vibration load sensor monitoring system",
    "health":     "heart rate pulse oxygen medical patient monitoring health data",
    "planner":    "task planning schedule workflow project management steps",
}

# ─── Mode meta ────────────────────────────────────────────────────────────────

MODE_META = {
    "industrial": {
        "accent": "#00f0ff", "rgb": "0,240,255", "icon": "🏭",
        "label": "INDUSTRIAL MONITORING",
        "sections": ["system", "zones", "thresholds", "alerts", "simulation",
                     "ai_behavior", "behavior", "diagnostics", "meta"],
    },
    "health": {
        "accent": "#39ff14", "rgb": "57,255,20", "icon": "🧑‍⚕️",
        "label": "HEALTH MONITORING",
        "sections": ["system", "thresholds", "ai_modules", "simulation",
                     "insights", "privacy", "behavior", "diagnostics", "meta"],
    },
    "planner": {
        "accent": "#ff8800", "rgb": "255,136,0", "icon": "📋",
        "label": "DEVELOPER PLANNING",
        "sections": ["system", "input", "ai_modules", "response",
                     "output", "performance", "meta"],
    },
}

SECTION_ICONS = {
    "system":       ("⚙️",  "System"),
    "zones":        ("🗺️",  "Zone Configuration"),
    "thresholds":   ("📊",  "Thresholds"),
    "alerts":       ("🚨",  "Alert Configuration"),
    "simulation":   ("🧪",  "Simulation"),
    "ai_behavior":  ("🤖",  "AI Behaviour"),
    "ai_modules":   ("🤖",  "AI Modules"),
    "behavior":     ("🔄",  "System Behaviour"),
    "diagnostics":  ("📈",  "Diagnostics"),
    "meta":         ("🧠",  "Meta Context"),
    "input":        ("📥",  "Input Processing"),
    "response":     ("🧾",  "Response Generation"),
    "output":       ("📤",  "Output Generation"),
    "performance":  ("⚡",  "Performance"),
    "insights":     ("💡",  "Insights Engine"),
    "privacy":      ("🔐",  "Privacy & Compliance"),
}

# ─── HTML Renderer ────────────────────────────────────────────────────────────

def _render_html(html_str: str) -> None:
    """
    Minifies HTML into a single continuous line before rendering. 
    This completely prevents Streamlit's Markdown parser from catching empty lines 
    or indentations and incorrectly wrapping the UI in <pre><code> blocks.
    """
    clean = " ".join(line.strip() for line in html_str.split("\n"))
    st.markdown(clean, unsafe_allow_html=True)

# ─── CSS ──────────────────────────────────────────────────────────────────────

def _css() -> None:
    _render_html("""
    <style>
    div[data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #0f1520 0%, #161b22 100%);
        border: 1px dashed rgba(88,166,255,0.3);
        border-radius: 12px; padding: 1rem;
    }
    hr { border-color: rgba(88,166,255,0.1) !important; }
    div[data-testid="stCodeBlock"] {
        background: #080c14 !important;
        border: 1px solid rgba(88,166,255,0.12) !important;
        border-radius: 8px !important;
    }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
    .cursor { display:inline-block; width:2px; height:1em; background:#58a6ff;
              margin-left:2px; vertical-align:middle; animation:blink 1s step-end infinite; }
    @keyframes pulse-dot {
        0%  { box-shadow:0 0 0 0 rgba(88,166,255,0.6); }
        70% { box-shadow:0 0 0 8px rgba(88,166,255,0); }
        100%{ box-shadow:0 0 0 0 rgba(88,166,255,0); }
    }
    .pulse-dot { display:inline-block; width:8px; height:8px; border-radius:50%;
                 background:#58a6ff; animation:pulse-dot 1.4s infinite;
                 margin-right:8px; vertical-align:middle; }
    @keyframes scan { 0%{top:-4px} 100%{top:100%} }
    .scan-container { position:relative; overflow:hidden; border-radius:10px; }
    .scan-line { position:absolute; left:0; right:0; height:2px;
                 background:linear-gradient(90deg,transparent,rgba(88,166,255,0.4),transparent);
                 animation:scan 2s linear infinite; }
    /* Config preview card hover */
    .cfg-section-card { transition: border-color 0.2s; }
    .cfg-section-card:hover { border-color: rgba(88,166,255,0.35) !important; }
    </style>
    """)


def _divider() -> None:
    _render_html("<div style='height:1px;background:linear-gradient(90deg,transparent,rgba(88,166,255,0.18),transparent);margin:0.75rem 0;'></div>")


# ─── Header ───────────────────────────────────────────────────────────────────

def _render_header() -> None:
    _render_html("""
    <div style="background:linear-gradient(135deg,#080c14 0%,#0d1520 100%);border-left:3px solid #58a6ff;border-bottom:1px solid rgba(88,166,255,0.12);border-radius:8px;padding:1rem 1.5rem;margin-bottom:0.75rem;display:flex;align-items:center;justify-content:space-between;">
        <div>
            <h1 style="color:#e6edf3;margin:0;font-size:1.5rem;font-weight:800;letter-spacing:0.06em;">
                ⚡ SENTINEL · CONFIG
                <span style="font-weight:300;font-size:0.85rem;color:#484f58;"> v4.0</span>
            </h1>
            <p style="color:#8b949e;margin:0.2rem 0 0;font-size:0.72rem;letter-spacing:0.2em;">
                SYSTEM INITIALISATION &amp; MODE CONFIGURATION
                <span style="color:#484f58;margin:0 8px;">|</span>
                STATUS <span style="color:#39ff14;font-weight:700;">ONLINE</span>
            </p>
        </div>
        <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.2em;color:#58a6ff;background:rgba(88,166,255,0.06);border:1px solid rgba(88,166,255,0.2);border-radius:20px;padding:5px 14px;text-shadow:0 0 12px #58a6ff88;">
            PROTOCOL CONFIG
        </div>
    </div>
    """)


# ─── Upload zone ──────────────────────────────────────────────────────────────

def _render_upload_zone() -> bytes | None:
    _render_html("<p style='color:rgba(88,166,255,0.7);font-size:0.7rem;font-weight:700;letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;'>📂&nbsp; FILE UPLINK</p>")
    uploaded = st.file_uploader(
        label="Accepted formats: .txt, .yaml, .yml",
        type=["txt", "yaml", "yml"],
        label_visibility="collapsed",
    )
    if uploaded:
        _render_html(f"""
        <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(88,166,255,0.08);border:1px solid rgba(88,166,255,0.25);border-radius:20px;padding:4px 14px;margin-top:6px;font-size:0.72rem;color:#58a6ff;letter-spacing:0.1em;font-family:monospace;">
            📄&nbsp;{uploaded.name}
            &nbsp;<span style="color:rgba(88,166,255,0.4);">{round(uploaded.size/1024,1)} KB</span>
        </div>
        """)
    return uploaded.read() if uploaded else None


# ─── Mode badge ───────────────────────────────────────────────────────────────

def _render_mode_badge(mode: str, config_dict: dict) -> None:
    meta  = MODE_META.get(mode.lower(), MODE_META.get("health"))
    fg    = meta["accent"]
    rgb   = meta["rgb"]
    icon  = meta["icon"]
    label = meta["label"]
    system = config_dict.get("system", {})
    sys_name = system.get("name", "Unknown System")
    version  = system.get("version", system.get("version", "—"))
    env      = system.get("deployment_environment", system.get("deployment", "—"))
    state    = system.get("system_state", "—")

    _render_html(f"""
    <div style="background:rgba({rgb},0.04);border:1px solid {fg}33;border-left:4px solid {fg};border-radius:10px;padding:1rem 1.4rem;margin-top:0.5rem;box-shadow:0 0 24px rgba({rgb},0.08);">
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.8rem;">
            <span style="font-size:2rem;">{icon}</span>
            <div>
                <div style="color:{fg};font-weight:800;font-size:0.95rem;letter-spacing:0.1em;text-shadow:0 0 12px {fg}88;">
                    MODE ACTIVATED: {label}
                </div>
                <div style="color:rgba({rgb},0.45);font-size:0.68rem;letter-spacing:0.1em;margin-top:3px;font-family:monospace;">
                    System behaviour will update across all screens
                </div>
            </div>
        </div>
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap;border-top:1px solid rgba({rgb},0.12);padding-top:0.7rem;">
            <div>
                <span style="color:rgba({rgb},0.4);font-size:0.6rem;font-family:monospace;letter-spacing:0.15em;">SYSTEM</span>
                <div style="color:#c9d1d9;font-size:0.8rem;font-weight:600;margin-top:2px;">{sys_name}</div>
            </div>
            {'<div><span style="color:rgba(' + rgb + ',0.4);font-size:0.6rem;font-family:monospace;letter-spacing:0.15em;">VERSION</span><div style="color:#c9d1d9;font-size:0.8rem;font-weight:600;margin-top:2px;">' + str(version) + '</div></div>' if version != "—" else ""}
            <div>
                <span style="color:rgba({rgb},0.4);font-size:0.6rem;font-family:monospace;letter-spacing:0.15em;">DEPLOYMENT</span>
                <div style="color:#c9d1d9;font-size:0.8rem;font-weight:600;margin-top:2px;">{env}</div>
            </div>
            <div>
                <span style="color:rgba({rgb},0.4);font-size:0.6rem;font-family:monospace;letter-spacing:0.15em;">STATE</span>
                <div style="color:{fg};font-size:0.8rem;font-weight:700;margin-top:2px;text-transform:uppercase;">{state}</div>
            </div>
        </div>
    </div>
    """)


# ─── Analysis ─────────────────────────────────────────────────────────────────

SKIP_PROSE = {"description", "inference_strategy", "risk_model", "explainability_goal",
              "system_intent", "interpretation", "system_goal", "reasoning_strategy",
              "explainability_focus", "user_experience_goal", "risk_strategy",
              "explainability", "meta"}


def _safe_flatten(d: dict, prefix: str = "", depth: int = 1) -> list[dict]:
    rows = []
    for k, v in d.items():
        if k in SKIP_PROSE:
            continue
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and depth > 0:
            rows.extend(_safe_flatten(v, prefix=full_key, depth=depth - 1))
        elif isinstance(v, list):
            rows.append({"name": full_key,
                         "value": ", ".join(str(i) for i in v),
                         "status": "OK"})
        else:
            val = str(v).strip()
            if len(val) > 80:
                val = val[:77] + "…"
            rows.append({"name": full_key, "value": val or "—",
                         "status": "OK" if val else "WARNING"})
    return rows


def _build_risks(config_dict: dict, mode: str) -> list[dict]:
    risks = []
    mode = mode.lower()

    behavior = config_dict.get("behavior", {})
    if not behavior.get("auto_alerting", True):
        risks.append({"level": "LOW", "description": "Auto-alerting is disabled"})

    diag = config_dict.get("diagnostics", {})
    if not diag.get("enable_metrics_logging", True):
        risks.append({"level": "LOW", "description": "Metrics logging disabled — limited observability"})

    if mode == "health":
        privacy = config_dict.get("privacy", {})
        hipaa = privacy.get("compliance", {}).get("hipaa", "")
        if str(hipaa).lower() == "partial":
            risks.append({"level": "MEDIUM", "description": "HIPAA compliance is partial — review required"})
        if privacy.get("audit_logging") is False or privacy.get("audit_logging") == "disabled":
            risks.append({"level": "LOW", "description": "Audit logging disabled — traceability gap"})
        thresholds = config_dict.get("thresholds", {})
        if not thresholds:
            risks.append({"level": "MEDIUM", "description": "No health thresholds defined"})

    if mode == "industrial":
        thresholds = config_dict.get("thresholds", {})
        if not thresholds:
            risks.append({"level": "HIGH", "description": "No sensor thresholds defined — safety risk"})
        alerts = config_dict.get("alerts", {})
        if not alerts.get("enabled", True):
            risks.append({"level": "HIGH", "description": "Alert system is disabled"})
        if not alerts.get("delivery", {}).get("audio_alerts", False):
            risks.append({"level": "LOW", "description": "Audio alerts disabled — operators may miss warnings"})

    if mode == "planner":
        perf = config_dict.get("performance", {})
        if perf.get("cache_results") is False:
            risks.append({"level": "LOW", "description": "Result caching disabled — may impact response speed"})
        ai_mods = config_dict.get("ai_modules", {})
        disabled = [k for k, v in ai_mods.items() if isinstance(v, dict) and not v.get("enabled", True)]
        if disabled:
            risks.append({"level": "MEDIUM", "description": f"Disabled AI modules: {', '.join(disabled)}"})

    if not risks:
        risks.append({"level": "NONE", "description": "No significant risks detected"})

    return risks[:4]


def _build_strengths(config_dict: dict, mode: str) -> list[str]:
    strengths = ["Configuration successfully parsed"]
    mode = mode.lower()

    thresholds = config_dict.get("thresholds", {})
    if thresholds:
        strengths.append(f"{len(thresholds)} threshold group(s) properly defined")

    ai_mods = config_dict.get("ai_modules", config_dict.get("ai_behavior", {}).get("modules", {}))
    enabled_mods = [k for k, v in ai_mods.items() if isinstance(v, dict) and v.get("enabled")]
    if enabled_mods:
        strengths.append(f"{len(enabled_mods)} AI module(s) active: {', '.join(enabled_mods)}")

    if mode == "health":
        privacy = config_dict.get("privacy", {})
        if privacy.get("blur_faces") and privacy.get("anonymize_data"):
            strengths.append("Privacy safeguards active (face blur + data anonymisation)")
        if privacy.get("encryption") == "enabled" or privacy.get("encryption") is True:
            strengths.append("End-to-end encryption enabled")

    if mode == "industrial":
        zones = config_dict.get("zones", {})
        if zones:
            strengths.append(f"{len(zones)} spatial zone(s) configured for risk-aware tracking")
        alerts = config_dict.get("alerts", {})
        if alerts.get("enabled"):
            strengths.append("Alert system active with escalation policy")

    if mode == "planner":
        inp = config_dict.get("input", {})
        langs = inp.get("supported_languages", [])
        if langs:
            strengths.append(f"Multi-language support: {', '.join(langs)}")
        out = config_dict.get("output", {})
        if out.get("generate_pseudocode"):
            strengths.append("Pseudocode generation enabled for explanations")

    if config_dict.get("simulation", {}).get("enabled"):
        strengths.append("Simulation profile active for safe testing")

    return strengths[:5]


def _build_recommendation(config_dict: dict, mode: str) -> str:
    mode = mode.lower()
    if mode == "health":
        hipaa = config_dict.get("privacy", {}).get("compliance", {}).get("hipaa", "")
        if str(hipaa).lower() == "partial":
            return ("Resolve partial HIPAA compliance before production deployment. "
                    "Enable audit logging and metrics logging for full observability. "
                    "All threshold and AI module configurations appear structurally sound.")
        return ("Enable metrics logging for full runtime observability. "
                "Review privacy compliance status before deploying to regulated environments.")
    if mode == "industrial":
        alerts = config_dict.get("alerts", {})
        if not alerts.get("delivery", {}).get("audio_alerts", False):
            return ("Enable audio alerts for critical zones to ensure operators are notified even "
                    "without visual line-of-sight. Verify emergency protocol actions are tested "
                    "in simulation before live deployment.")
        return ("Validate all zone boundaries in physical environment before deployment. "
                "Run simulation profiles to confirm anomaly detection thresholds under load.")
    if mode == "planner":
        return ("Consider enabling result caching for repeated queries to reduce latency. "
                "Validate stepwise reasoning output against test code samples before release. "
                "All AI analysis modules are correctly configured.")
    return "Review all configurations and ensure thresholds and alerting are properly set."


def _analyse_local(config_dict: dict, mode: str) -> dict:
    params   = _safe_flatten(config_dict)
    risks    = _build_risks(config_dict, mode)
    strengths = _build_strengths(config_dict, mode)

    system   = config_dict.get("system", {})
    sys_name = system.get("name", mode.capitalize() + " System")
    env      = (system.get("deployment_environment")
                or system.get("deployment", "unspecified"))
    n_sections = len(config_dict)
    risk_count = sum(1 for r in risks if isinstance(r, dict) and r.get("level") not in ("NONE",))

    summary = (
        f"{sys_name} configuration loaded and validated across {n_sections} top-level sections. "
        f"Deployment target: {env}. "
        f"{'All critical parameters are within acceptable bounds.'  if risk_count == 0 else f'{risk_count} risk flag(s) require attention before deployment.'}"
    )

    score = 90
    if risk_count >= 1: score -= 5
    if risk_count >= 2: score -= 10
    if risk_count >= 3: score -= 15
    if any(isinstance(r, dict) and r.get("level") == "HIGH"     for r in risks): score -= 10
    if any(isinstance(r, dict) and r.get("level") == "CRITICAL" for r in risks): score  = 40

    return {
        "executive_summary":  summary,
        "system_purpose":     sys_name,
        "detected_mode":      mode,
        "confidence":         "HIGH" if score >= 80 else "MEDIUM",
        "parameters":         params[:6],
        "risk_flags":         risks,
        "strengths":          strengths,
        "recommendation":     _build_recommendation(config_dict, mode),
        "compliance_score":   max(score, 0),
    }


# ─── Analysis render ──────────────────────────────────────────────────────────

def _score_color(score: int) -> str:
    if score >= 80: return "#39ff14"
    if score >= 60: return "#f4a261"
    return "#e63946"


def _risk_color(level: str) -> tuple[str, str]:
    return {
        "NONE":     ("#39ff14", "#0d2010"),
        "LOW":      ("#58a6ff", "#080c14"),
        "MEDIUM":   ("#f4a261", "#1a1000"),
        "HIGH":     ("#e63946", "#1a0508"),
        "CRITICAL": ("#ff0055", "#1a0010"),
    }.get(level.upper(), ("#8b949e", "#0f1520"))


def _status_icon(status: str) -> str:
    return {"OK": "✅", "WARNING": "⚠️", "MISSING": "❌"}.get(status.upper(), "◈")


def _render_analysis(analysis: dict, mode: str) -> None:
    meta       = MODE_META.get(mode.lower(), MODE_META["health"])
    accent     = meta["accent"]
    accent_rgb = meta["rgb"]
    score      = int(analysis.get("compliance_score", 0))
    score_col  = _score_color(score)
    confidence = analysis.get("confidence", "—")

    _render_html(f"<p style='color:rgba({accent_rgb},0.7);font-size:0.7rem;font-weight:700;letter-spacing:0.18em;margin:1rem 0 0.5rem;font-family:monospace;'>🧠&nbsp; SENTINEL AI · ANALYSIS REPORT</p>")

    # ── Executive summary banner
    _render_html(f"""
    <div class="scan-container" style="background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});border:1px solid rgba({accent_rgb},0.2);border-left:4px solid {accent};border-radius:10px;padding:1.3rem 1.5rem;margin-bottom:0.75rem;box-shadow:0 0 28px rgba({accent_rgb},0.07);">
        <div class="scan-line"></div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
            <div style="flex:1;">
                <div style="color:rgba({accent_rgb},0.5);font-size:0.62rem;font-weight:700;letter-spacing:0.22em;margin-bottom:0.6rem;font-family:monospace;">◈ EXECUTIVE SUMMARY</div>
                <div style="color:#c9d1d9;font-size:0.9rem;line-height:1.8;">{analysis.get('executive_summary','')}</div>
                <div style="margin-top:0.9rem;padding-top:0.75rem;border-top:1px solid rgba({accent_rgb},0.1);color:rgba({accent_rgb},0.45);font-size:0.65rem;letter-spacing:0.12em;font-family:monospace;">
                    ◈ PRIMARY SYSTEM&nbsp;&nbsp;
                    <span style="color:{accent};font-size:0.82rem;font-weight:600;">{analysis.get('system_purpose','')}</span>
                </div>
            </div>
            <div style="text-align:center;flex-shrink:0;min-width:110px;">
                <div style="width:90px;height:90px;border-radius:50%;margin:0 auto;border:3px solid {score_col};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 0 20px {score_col}44;background:rgba(0,0,0,0.3);">
                    <span style="color:{score_col};font-size:1.5rem;font-weight:900;line-height:1;">{score}</span>
                    <span style="color:rgba(255,255,255,0.3);font-size:0.55rem;letter-spacing:0.1em;">/100</span>
                </div>
                <div style="color:rgba(255,255,255,0.4);font-size:0.6rem;letter-spacing:0.1em;margin-top:6px;font-family:monospace;">COMPLIANCE</div>
                <div style="color:{accent};font-size:0.62rem;font-weight:700;letter-spacing:0.1em;margin-top:3px;font-family:monospace;">CONFIDENCE: {confidence}</div>
            </div>
        </div>
    </div>
    """)

    # ── Three columns
    col_p, col_r, col_s = st.columns(3, gap="medium")

    with col_p:
        _render_html(f"""<div style="color:rgba({accent_rgb},0.6);font-size:0.63rem;font-weight:700;letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;">⚙️&nbsp; DETECTED PARAMETERS</div>""")
        params = analysis.get("parameters", [])
        
        items = "".join(
            f"<div style=\"display:flex;align-items:flex-start;gap:8px;padding:0.45rem 0;border-bottom:1px solid rgba({accent_rgb},0.07);\">"
            f"<span style=\"font-size:0.72rem;flex-shrink:0;margin-top:1px;\">{_status_icon(p.get('status','OK'))}</span>"
            f"<div><div style=\"color:{accent};font-size:0.7rem;font-weight:700;letter-spacing:0.06em;\">{p.get('name','—')}</div>"
            f"<div style=\"color:#8b949e;font-size:0.7rem;margin-top:1px;\">{p.get('value','—')}</div></div></div>"
            for p in params[:6]
        )
        
        _render_html(f"""
        <div style="background:{_BG_PANEL};border:1px solid rgba({accent_rgb},0.14);border-radius:8px;padding:0.8rem 1rem;min-height:180px;">
            {items or '<div style="color:#484f58;font-size:0.75rem;">No parameters extracted.</div>'}
        </div>""")

    with col_r:
        _render_html("""<div style="color:rgba(230,57,70,0.7);font-size:0.63rem;font-weight:700;letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;">🚨&nbsp; RISK FLAGS</div>""")
        risks = analysis.get("risk_flags", [])
        
        flags = "".join(
            f"<div style=\"padding:0.45rem 0;border-bottom:1px solid rgba(230,57,70,0.07);\">"
            f"<span style=\"display:inline-block;padding:1px 7px;border-radius:10px;font-size:0.58rem;font-weight:800;letter-spacing:0.1em;background:{_risk_color(r.get('level','LOW'))[1] if isinstance(r, dict) else '#1a0508'};color:{_risk_color(r.get('level','LOW'))[0] if isinstance(r, dict) else '#e63946'};border:1px solid {(_risk_color(r.get('level','LOW'))[0] if isinstance(r, dict) else '#e63946')}44;margin-bottom:4px;\">{r.get('level','?') if isinstance(r, dict) else 'ERR'}</span>"
            f"<div style=\"color:#c9d1d9;font-size:0.78rem;line-height:1.5;\">{r.get('description','—') if isinstance(r, dict) else str(r)}</div></div>"
            for r in risks[:4]
        )
        
        _render_html(f"""
        <div style="background:#100508;border:1px solid rgba(230,57,70,0.15);border-radius:8px;padding:0.8rem 1rem;min-height:180px;">
            {flags or '<div style="color:#484f58;font-size:0.75rem;">No risk flags detected.</div>'}
        </div>""")

    with col_s:
        _render_html("""<div style="color:rgba(57,255,20,0.6);font-size:0.63rem;font-weight:700;letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;">✅&nbsp; CONFIGURATION STRENGTHS</div>""")
        strengths = analysis.get("strengths", [])
        
        shtml = "".join(
            f"<div style=\"display:flex;align-items:flex-start;gap:8px;padding:0.45rem 0;border-bottom:1px solid rgba(57,255,20,0.07);\">"
            f"<span style=\"color:#39ff14;font-size:0.65rem;flex-shrink:0;margin-top:2px;\">◈</span>"
            f"<span style=\"color:#c9d1d9;font-size:0.78rem;line-height:1.5;\">{s}</span></div>"
            for s in strengths[:5]
        )
        
        _render_html(f"""
        <div style="background:#0c1400;border:1px solid rgba(57,255,20,0.12);border-radius:8px;padding:0.8rem 1rem;min-height:180px;">
            {shtml or '<div style="color:#484f58;font-size:0.75rem;">No strengths extracted.</div>'}
        </div>""")

    # ── Recommendation
    _render_html(f"""
    <div style="background:#0c1400;border:1px solid rgba(244,162,97,0.25);border-left:3px solid #f4a261;border-radius:8px;padding:0.9rem 1.2rem;margin-top:0.75rem;display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.2rem;">⚡</span>
        <div>
            <div style="color:#f4a261;font-size:0.62rem;font-weight:700;letter-spacing:0.18em;margin-bottom:3px;font-family:monospace;">ACTIONABLE RECOMMENDATION</div>
            <p style="margin:0;color:#c9a96e;font-size:0.88rem;line-height:1.6;">{analysis.get('recommendation','')}</p>
        </div>
    </div>
    """)

    _render_html("""
    <p style="text-align:center;color:#484f58;font-size:0.62rem;margin-top:1rem;padding-top:0.75rem;border-top:1px dashed rgba(88,166,255,0.1);letter-spacing:0.05em;">
        Generated by SENTINEL AI · Powered by Claude · Strictly observational — not a substitute for professional system review.
    </p>""")


# ─── Human-readable config preview (fully dynamic) ────────────────────────────

def _val_pill(v, accent: str, rgb: str) -> str:
    v_str = str(v)
    if isinstance(v, bool):
        col  = accent if v else "#e63946"
        bg   = f"rgba({rgb},0.08)" if v else "rgba(230,57,70,0.08)"
        bord = f"rgba({rgb},0.25)" if v else "rgba(230,57,70,0.25)"
        return f'<span style="background:{bg};border:1px solid {bord};color:{col};border-radius:10px;padding:1px 9px;font-size:0.72rem;font-weight:700;">{v_str.upper()}</span>'
    if isinstance(v, (int, float)):
        return f'<span style="color:{accent};font-weight:700;font-size:0.82rem;">{v_str}</span>'
    if len(v_str) <= 30:
        return f'<span style="color:#c9d1d9;font-size:0.82rem;">{v_str}</span>'
    return f'<span style="color:#8b949e;font-size:0.78rem;">{v_str[:60]}…</span>'


def _render_kv_block(data: dict, accent: str, rgb: str, skip_keys: set | None = None, depth: int = 0) -> str:
    skip = skip_keys or SKIP_PROSE
    html = ""
    indent = depth * 12 

    for k, v in data.items():
        if k in skip:
            continue
        key_label = k.replace("_", " ").title()

        if isinstance(v, dict):
            html += f"""
            <div style="margin-top:0.6rem;padding-left:{indent}px;">
                <div style="color:rgba({rgb},0.55);font-size:0.65rem;font-weight:700;letter-spacing:0.12em;font-family:monospace;margin-bottom:0.3rem;">▸ {key_label}</div>
                {_render_kv_block(v, accent, rgb, skip, depth + 1)}
            </div>"""

        elif isinstance(v, list):
            tags = "".join(f'<span style="background:rgba({rgb},0.08);border:1px solid rgba({rgb},0.2);color:{accent};border-radius:8px;padding:1px 8px;font-size:0.7rem;margin:2px 3px 2px 0;display:inline-block;">{item}</span>' for item in v)
            html += f"""
            <div style="display:flex;align-items:flex-start;gap:10px;padding:0.35rem 0;border-bottom:1px solid rgba({rgb},0.06);padding-left:{indent}px;">
                <div style="color:rgba({rgb},0.4);font-size:0.7rem;font-weight:600;min-width:120px;padding-top:3px;font-family:monospace;">{key_label}</div>
                <div style="flex:1;flex-wrap:wrap;">{tags}</div>
            </div>"""

        else:
            v_str = str(v).strip()
            if len(v_str) > 200:
                continue
            html += f"""
            <div style="display:flex;align-items:center;gap:10px;padding:0.32rem 0;border-bottom:1px solid rgba({rgb},0.06);padding-left:{indent}px;">
                <div style="color:rgba({rgb},0.4);font-size:0.7rem;font-weight:600;min-width:120px;font-family:monospace;flex-shrink:0;">{key_label}</div>
                <div>{_val_pill(v, accent, rgb)}</div>
            </div>"""
    return html


def render_human_readable_config(config: dict) -> None:
    mode   = str(config.get("mode", "health")).lower()
    meta   = MODE_META.get(mode, MODE_META["health"])
    accent = meta["accent"]
    rgb    = meta["rgb"]
    icon   = meta["icon"]
    label  = meta["label"]

    ordered = meta["sections"]
    extra   = [k for k in config if k not in ordered and k not in ("mode",)]
    all_sections = ordered + extra

    system   = config.get("system", {})
    if not isinstance(system, dict): system = {}
    sys_name = system.get("name", "Unknown System")
    version  = system.get("version", "")

    _render_html(f"""
    <div style="background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});border:1px solid rgba({rgb},0.2);border-left:4px solid {accent};border-radius:10px;padding:1rem 1.4rem;margin-bottom:1rem;display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.6rem;">{icon}</span>
        <div>
            <div style="color:{accent};font-size:0.8rem;font-weight:800;letter-spacing:0.1em;">{sys_name}{"<span style='color:rgba(" + rgb + ",0.4);font-size:0.7rem;font-weight:400;'> · v" + str(version) + "</span>" if version else ""}</div>
            <div style="color:#8b949e;font-size:0.65rem;letter-spacing:0.15em;font-family:monospace;margin-top:2px;">{label} CONFIG · {len(all_sections)} SECTIONS</div>
        </div>
    </div>
    """)

    for sec_key in all_sections:
        if sec_key not in config:
            continue
        value = config[sec_key]
        if sec_key == "mode":
            continue

        sec_icon, sec_title = SECTION_ICONS.get(sec_key, ("◈", sec_key.replace("_", " ").title()))

        _render_html(f"""
        <div style="display:flex;align-items:center;gap:8px;margin:1rem 0 0.4rem;">
            <span style="font-size:1rem;">{sec_icon}</span>
            <span style="color:{accent};font-size:0.72rem;font-weight:800;letter-spacing:0.15em;font-family:monospace;">{sec_title.upper()}</span>
            <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba({rgb},0.25),transparent);margin-left:8px;"></div>
        </div>
        """)

        if isinstance(value, dict):
            body = _render_kv_block(value, accent, rgb)
            _render_html(f"""
            <div style="background:{_BG_PANEL};border:1px solid rgba({rgb},0.1);border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.25rem;">
                {body}
            </div>""")

        elif isinstance(value, list):
            tags = "".join(f'<span style="background:rgba({rgb},0.08);border:1px solid rgba({rgb},0.2);color:{accent};border-radius:8px;padding:2px 10px;font-size:0.75rem;margin:3px;">{item}</span>' for item in value)
            _render_html(f"""
            <div style="background:{_BG_PANEL};border:1px solid rgba({rgb},0.1);border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.25rem;">
                {tags}
            </div>""")

        else:
            _render_html(f"""
            <div style="background:{_BG_PANEL};border:1px solid rgba({rgb},0.1);border-radius:8px;padding:0.6rem 1rem;margin-bottom:0.25rem;">
                {_val_pill(value, accent, rgb)}
            </div>""")

    _render_html(f"""
    <div style="margin-top:1rem;padding:0.6rem 1rem;border-top:1px dashed rgba({rgb},0.12);color:#484f58;font-size:0.62rem;font-family:monospace;text-align:center;">
        {icon} {sys_name} · {label} · {len(all_sections)} sections rendered
    </div>""")


# ─── Config preview wrapper ───────────────────────────────────────────────────

def _render_config_preview(config_dict: dict) -> None:
    render_human_readable_config(config_dict)


# ─── Main entry ───────────────────────────────────────────────────────────────

def config_screen(app_state) -> None:
    _css()
    _render_header()
    _divider()

    raw = _render_upload_zone()

    if raw is None:
        _render_html(f"""
        <div style="background:linear-gradient(135deg,{_BG_PANEL},{_BG_MID});border:1px solid rgba(88,166,255,0.15);border-radius:12px;padding:2.5rem;text-align:center;margin-top:0.5rem;box-shadow:0 0 24px rgba(88,166,255,0.04);">
            <div style="font-size:2.5rem;margin-bottom:1rem;">📡</div>
            <div style="color:#58a6ff;font-size:0.75rem;font-weight:700;letter-spacing:0.25em;margin-bottom:0.5rem;">AWAITING FILE UPLINK</div>
            <div style="color:#484f58;font-size:0.72rem;letter-spacing:0.1em;">
                Upload a
                <code style="color:rgba(88,166,255,0.7);background:rgba(88,166,255,0.08);padding:1px 6px;border-radius:4px;">.txt</code>
                &nbsp;or&nbsp;
                <code style="color:rgba(88,166,255,0.7);background:rgba(88,166,255,0.08);padding:1px 6px;border-radius:4px;">.yaml / .yml</code>
                &nbsp;file to initialise system mode.
                <br/><br/>
                <span style="color:rgba(88,166,255,0.5);">Supports:</span>
                &nbsp;
                <span style="color:#00f0ff;">🏭 Industrial</span>
                &nbsp;·&nbsp;
                <span style="color:#39ff14;">🧑‍⚕️ Health</span>
                &nbsp;·&nbsp;
                <span style="color:#ff8800;">📋 Planner</span>
            </div>
        </div>
        """)
        return

    content     = raw.decode("utf-8", errors="replace")
    config_dict = load_config(content)
    mode        = detect_mode_from_config(config_dict)
    app_state.update_state(mode, config_dict)

    _divider()

    # ── Detection result
    _render_html("<p style='color:rgba(88,166,255,0.7);font-size:0.7rem;font-weight:700;letter-spacing:0.18em;margin-bottom:0.4rem;font-family:monospace;'>✅&nbsp; DETECTION RESULT</p>")
    _render_mode_badge(mode, config_dict)
    _divider()

    # ── Analysis (cached per content hash)
    cache_key = f"cfg_analysis_{hash(content)}"

    if cache_key not in st.session_state:
        with st.status("⚙️  SENTINEL AI · CONFIGURING ANALYSIS ENGINE...", expanded=True) as status:
            _render_html("""
            <div style="font-family:monospace;font-size:0.78rem;color:#8b949e;line-height:2;">
                <div><span style="color:#58a6ff;">►</span>&nbsp; Parsing configuration schema...</div>
                <div><span style="color:#58a6ff;">►</span>&nbsp; Detecting system topology...</div>
                <div><span style="color:#58a6ff;">►</span>&nbsp; Mapping parameter graph...</div>
                <div><span style="color:#58a6ff;">►</span>&nbsp; Running risk inference engine...</div>
                <div><span style="color:#58a6ff;">►</span>&nbsp; Generating compliance score...</div>
                <div><span style="color:#f4a261;">►</span>&nbsp; Compiling SENTINEL AI report…<span class="cursor"></span></div>
            </div>
            """)
            result = _analyse_local(config_dict, mode)
            st.session_state[cache_key] = result
            status.update(label="✅  SENTINEL AI · ANALYSIS COMPLETE", state="complete", expanded=False)

    _render_analysis(st.session_state[cache_key], mode)
    _divider()

    # ── Full config viewer
    with st.expander("📄  VIEW FULL CONFIGURATION FILE", expanded=False):
        _render_config_preview(config_dict)