import time
import streamlit as st
import streamlit.components.v1 as components
from domain.usecases.generate_response import generate_response
from robot.tts_engine import tts_engine
from robot.gemini_audio_engine import record_audio, transcribe_audio

_MODE_PROMPTS = {
    "industrial": "e.g. 'Explain the current zone alert' or 'What does vibration spike mean?'",
    "health":     "e.g. 'Summarise activity levels' or 'What does low movement score indicate?'",
    "planner":    "e.g. 'Generate a task breakdown' or 'Suggest next planning steps'",
}

_MODE_COLOURS = {
    "industrial": "#00f0ff",
    "health":     "#39ff14",
    "planner":    "#ff8800",
}

_GREETINGS = {
    "industrial": "Hi, I am here to tell you about the status and about the machine. You can ask me anything.",
    "health": "Hi, I'm here to monitor your health. Let me analyze your data and walk you through what I find.",
    "planner": "A.I. Core online. I am ready to assist with project planning and strategy.",
    "default": "System online. Advanced logic core active."
}

_TYPING_SPEED = 0.016


def _robot_face_html(mode: str, is_thinking: bool = False) -> str:
    accent     = _MODE_COLOURS.get(mode, "#bc8cff")
    state      = "thinking" if is_thinking else "idle"
    status_txt = "ANALYZING DATABANKS..." if is_thinking else "A.I. CORE ONLINE"
    visor_glow = f"0 0 60px {accent}aa, 0 0 120px {accent}44" if is_thinking else f"0 0 20px {accent}66, 0 0 40px {accent}22"
    scan_speed = "0.8s" if is_thinking else "3s"

    rgb = ','.join(str(int(accent[i:i+2], 16)) for i in (1, 3, 5))

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 520px;
    font-family: 'Segoe UI', system-ui, sans-serif;
    overflow: hidden;
}}
#particles {{ position:absolute;width:100%;height:100%;z-index:0;pointer-events:none; }}
.grid-overlay {{
    position:absolute;width:500px;height:500px;
    background-image:linear-gradient(rgba({rgb},0.03) 1px,transparent 1px),linear-gradient(90deg,rgba({rgb},0.03) 1px,transparent 1px);
    background-size:30px 30px;
    transform:perspective(400px) rotateX(60deg);
    animation:grid-pulse 4s ease-in-out infinite alternate;z-index:0;
}}
@keyframes grid-pulse {{0%{{opacity:0.3}}100%{{opacity:0.7}}}}
.robot-container {{ position:relative;z-index:10;display:flex;flex-direction:column;align-items:center;animation:float 5s ease-in-out infinite; }}
@keyframes float {{0%,100%{{transform:translateY(0px)}}50%{{transform:translateY(-15px)}}}}
.outer-ring {{
    position:absolute;width:340px;height:340px;
    border:1.5px solid rgba({rgb},0.15);border-radius:50%;
    top:50%;left:50%;
    transform:translate(-50%,-50%) rotateX(75deg) rotateZ(0deg);
    animation:ring-spin 12s linear infinite;
    box-shadow:0 0 30px rgba({rgb},0.05);pointer-events:none;
}}
.outer-ring-2 {{ width:380px;height:380px;border-color:rgba({rgb},0.08);animation:ring-spin-reverse 18s linear infinite;border-style:dashed; }}
@keyframes ring-spin {{0%{{transform:translate(-50%,-50%) rotateX(75deg) rotateZ(0deg)}}100%{{transform:translate(-50%,-50%) rotateX(75deg) rotateZ(360deg)}}}}
@keyframes ring-spin-reverse {{0%{{transform:translate(-50%,-50%) rotateX(75deg) rotateZ(0deg)}}100%{{transform:translate(-50%,-50%) rotateX(75deg) rotateZ(-360deg)}}}}
.mech-head {{
    width:220px;height:290px;
    background:linear-gradient(160deg,#1e2430 0%,#0a0d14 40%,#151b24 100%);
    border-radius:50% 50% 45% 45% / 35% 35% 55% 55%;
    box-shadow:inset -10px -10px 30px rgba(0,0,0,0.9),inset 10px 10px 30px rgba(255,255,255,0.04),0 30px 60px rgba(0,0,0,0.7),0 0 40px rgba({rgb},0.08);
    display:flex;flex-direction:column;align-items:center;
    position:relative;padding-top:50px;
    border:1px solid rgba({rgb},0.06);
}}
.circuit-left,.circuit-right {{position:absolute;width:40px;height:70px;top:60px;border:1px solid rgba({rgb},0.12);border-radius:30%;pointer-events:none;}}
.circuit-left {{left:10px;border-right:none;border-bottom:none;box-shadow:-2px -2px 8px rgba({rgb},0.05);}}
.circuit-right {{right:10px;border-left:none;border-bottom:none;box-shadow:2px -2px 8px rgba({rgb},0.05);}}
.circuit-dot {{position:absolute;width:4px;height:4px;background:{accent};border-radius:50%;box-shadow:0 0 8px {accent};animation:dot-pulse 2s ease-in-out infinite;}}
.circuit-dot-1{{top:75px;left:15px;animation-delay:0s}}.circuit-dot-2{{top:75px;right:15px;animation-delay:0.5s}}
.circuit-dot-3{{top:100px;left:12px;animation-delay:1s}}.circuit-dot-4{{top:100px;right:12px;animation-delay:1.5s}}
@keyframes dot-pulse {{0%,100%{{opacity:0.2;transform:scale(0.5)}}50%{{opacity:1;transform:scale(1.2)}}}}
.visor {{
    width:170px;height:90px;
    background:linear-gradient(180deg,#080b10 0%,#11161e 50%,#0a0d14 100%);
    border-radius:18px 18px 35px 35px;
    box-shadow:inset 0 10px 20px rgba(0,0,0,0.95),inset 0 -3px 15px {accent}44,{visor_glow};
    position:relative;display:flex;justify-content:center;align-items:center;overflow:hidden;
    border:1px solid rgba({rgb},0.2);
}}
.visor::before {{
    content:'';position:absolute;width:200%;height:2px;
    background:linear-gradient(90deg,transparent,{accent},transparent);
    top:0;animation:scan-line {scan_speed} linear infinite;z-index:5;opacity:0.6;
}}
@keyframes scan-line {{0%{{top:0;opacity:0}}10%{{opacity:0.6}}90%{{opacity:0.6}}100%{{top:100%;opacity:0}}}}
.eye-grid {{display:grid;grid-template-columns:repeat(5,1fr);grid-template-rows:repeat(5,1fr);gap:3px;width:100px;height:60px;position:relative;z-index:2;}}
.eye-cell {{background:rgba({rgb},0.08);border-radius:2px;transition:all 0.15s ease;animation:cell-idle 3s ease-in-out infinite;}}
.eye-cell.active {{background:{accent};box-shadow:0 0 6px {accent},0 0 12px {accent}66;}}
@keyframes cell-idle {{0%,100%{{opacity:0.3}}50%{{opacity:0.6}}}}
.eye-pupil {{position:absolute;width:12px;height:12px;background:{accent};border-radius:50%;box-shadow:0 0 15px {accent},0 0 30px {accent}44;animation:pupil-scan 3s ease-in-out infinite;z-index:3;}}
@keyframes pupil-scan {{0%{{transform:translateX(-20px)}}50%{{transform:translateX(20px)}}100%{{transform:translateX(-20px)}}}}
.power-core {{position:absolute;width:18px;height:50px;background:linear-gradient(180deg,transparent 0%,{accent}22 30%,{accent}44 50%,{accent}22 70%,transparent 100%);border-radius:9px;top:120px;border:1px solid rgba({rgb},0.15);overflow:hidden;}}
.power-core-left{{left:28px}}.power-core-right{{right:28px}}
.power-core-inner {{position:absolute;bottom:0;width:100%;height:60%;background:linear-gradient(0deg,{accent}88,transparent);border-radius:0 0 9px 9px;animation:core-fill 2s ease-in-out infinite alternate;}}
.power-core-left .power-core-inner{{animation-delay:0s}}.power-core-right .power-core-inner{{animation-delay:0.5s}}
@keyframes core-fill {{0%{{height:20%;opacity:0.3}}100%{{height:80%;opacity:1}}}}
.jaw {{margin-top:35px;width:110px;height:35px;background:linear-gradient(180deg,#161b22,#0d1117);border-radius:8px 8px 25px 25px;box-shadow:inset 0 5px 15px rgba(0,0,0,0.7);display:flex;justify-content:space-evenly;align-items:center;padding:0 8px;border:1px solid rgba({rgb},0.06);}}
.vent {{width:6px;height:20px;background:linear-gradient(180deg,#1a2028,#0d1117);border-radius:3px;box-shadow:inset 0 2px 4px rgba(0,0,0,0.5);transition:all 0.3s;}}
.jaw.speaking .vent {{animation:vent-breathe 0.4s ease-in-out infinite alternate;}}
.jaw.speaking .vent:nth-child(1){{animation-delay:0s}}.jaw.speaking .vent:nth-child(2){{animation-delay:0.1s}}
.jaw.speaking .vent:nth-child(3){{animation-delay:0.2s}}.jaw.speaking .vent:nth-child(4){{animation-delay:0.3s}}
@keyframes vent-breathe {{0%{{height:14px;background:{accent}33}}100%{{height:26px;background:{accent}77}}}}
.neck {{width:80px;height:35px;margin-top:-12px;background:linear-gradient(90deg,#1a2028 0%,#2d3540 50%,#1a2028 100%);border-radius:0 0 15px 15px;box-shadow:inset 0 10px 20px rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;position:relative;z-index:-1;}}
.neck-ring {{width:50px;height:6px;background:#0d1117;border-radius:3px;overflow:hidden;position:relative;}}
.neck-pulse {{position:absolute;width:20px;height:100%;background:{accent};border-radius:3px;box-shadow:0 0 8px {accent};animation:neck-flow 2s linear infinite;}}
@keyframes neck-flow {{0%{{left:-20px}}100%{{left:60px}}}}
.status-hud {{margin-top:25px;font-size:11px;font-weight:600;letter-spacing:0.35em;color:{accent};text-shadow:0 0 15px {accent}88,0 0 30px {accent}44;background:rgba(0,0,0,0.5);padding:6px 18px;border-radius:20px;border:1px solid rgba({rgb},0.2);backdrop-filter:blur(4px);}}
.hud-corner {{position:absolute;width:25px;height:25px;border-color:rgba({rgb},0.2);border-style:solid;border-width:0;pointer-events:none;}}
.hud-tl{{top:5px;left:5px;border-top-width:1px;border-left-width:1px}}.hud-tr{{top:5px;right:5px;border-top-width:1px;border-right-width:1px}}
.hud-bl{{bottom:5px;left:5px;border-bottom-width:1px;border-left-width:1px}}.hud-br{{bottom:5px;right:5px;border-bottom-width:1px;border-right-width:1px}}
.data-stream {{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:1;overflow:hidden;}}
.data-stream span {{position:absolute;font-family:'Courier New',monospace;font-size:10px;color:rgba({rgb},0.12);animation:data-fall 8s linear infinite;white-space:nowrap;}}
@keyframes data-fall {{0%{{transform:translateY(-100%);opacity:0}}10%{{opacity:0.15}}90%{{opacity:0.15}}100%{{transform:translateY(100vh);opacity:0}}}}
</style>
</head>
<body>
<div class="grid-overlay"></div>
<div id="particles"></div>
<div class="data-stream" id="dataStream"></div>
<div class="outer-ring"></div>
<div class="outer-ring outer-ring-2"></div>
<div class="robot-container {state}">
  <div class="mech-head">
    <div class="hud-corner hud-tl"></div><div class="hud-corner hud-tr"></div>
    <div class="hud-corner hud-bl"></div><div class="hud-corner hud-br"></div>
    <div class="circuit-left"></div><div class="circuit-right"></div>
    <div class="circuit-dot circuit-dot-1"></div><div class="circuit-dot circuit-dot-2"></div>
    <div class="circuit-dot circuit-dot-3"></div><div class="circuit-dot circuit-dot-4"></div>
    <div class="power-core power-core-left"><div class="power-core-inner"></div></div>
    <div class="power-core power-core-right"><div class="power-core-inner"></div></div>
    <div class="visor">
        <div class="eye-grid" id="eyeGrid"></div>
        <div class="eye-pupil" id="eyePupil"></div>
    </div>
    <div class="jaw {'speaking' if is_thinking else ''}" id="jaw">
        <div class="vent"></div><div class="vent"></div><div class="vent"></div><div class="vent"></div>
    </div>
  </div>
  <div class="neck"><div class="neck-ring"><div class="neck-pulse"></div></div></div>
  <div class="status-hud">{status_txt}</div>
</div>
<script>
(function() {{
    const grid = document.getElementById('eyeGrid');
    if (!grid) return;
    const cells = [];
    for (let r = 0; r < 5; r++) for (let c = 0; c < 5; c++) {{
        const cell = document.createElement('div');
        cell.className = 'eye-cell';
        grid.appendChild(cell);
        cells.push(cell);
    }}
    const isThinking = {str(is_thinking).lower()};
    function animateEyes() {{
        if (isThinking) {{
            cells.forEach(c => c.classList.remove('active'));
            const count = 6 + Math.floor(Math.random() * 8);
            for (let i = 0; i < count; i++) cells[Math.floor(Math.random() * cells.length)].classList.add('active');
            setTimeout(animateEyes, 120 + Math.random() * 80);
        }} else {{
            cells.forEach((c, i) => {{
                const row = Math.floor(i / 5), col = i % 5;
                const dist = Math.abs(col - 2) + Math.abs(row - 2);
                const val = Math.sin(Date.now() / 1000 * 2 - dist * 0.15) * 0.5 + 0.5;
                if (val > 0.7) c.classList.add('active'); else c.classList.remove('active');
            }});
            requestAnimationFrame(animateEyes);
        }}
    }}
    animateEyes();
}})();
(function() {{
    const container = document.getElementById('dataStream');
    if (!container) return;
    const chars = '01010101 10101010 11001100 AI SENTINEL v3.7 PROTOCOL ACTIVE';
    function createStream() {{
        const span = document.createElement('span');
        let text = '';
        for (let i = 0; i < 6 + Math.floor(Math.random() * 20); i++) text += chars[Math.floor(Math.random() * chars.length)];
        span.textContent = text;
        span.style.left = Math.random() * 100 + '%';
        span.style.animationDuration = (6 + Math.random() * 8) + 's';
        span.style.fontSize = (8 + Math.random() * 6) + 'px';
        container.appendChild(span);
        setTimeout(() => span.remove(), 14000);
    }}
    setInterval(createStream, 400 + Math.random() * 600);
    for (let i = 0; i < 5; i++) setTimeout(createStream, i * 300);
}})();
(function() {{
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 30; i++) {{
        const dot = document.createElement('div');
        dot.style.cssText = `position:absolute;width:2px;height:2px;background:rgba({rgb},0.3);border-radius:50%;left:${{Math.random()*100}}%;top:${{Math.random()*100}}%;pointer-events:none;animation:pdrift ${{4+Math.random()*6}}s linear infinite;animation-delay:${{Math.random()*4}}s;`;
        container.appendChild(dot);
    }}
    const s = document.createElement('style');
    s.textContent = '@keyframes pdrift{{0%{{transform:translate(0,0) scale(0.5);opacity:0}}20%{{opacity:1}}80%{{opacity:1}}100%{{transform:translate(0,-60px) scale(1.5);opacity:0}}}}';
    document.head.appendChild(s);
}})();
</script>
</body>
</html>"""


def _mic_button_html(accent: str, is_listening: bool, is_speaking: bool) -> str:
    """Render a standalone mic button with correct glow color."""
    if is_speaking:
        mic_color = "#ff3333"
        mic_glow  = "0 0 18px #ff3333aa, 0 0 40px #ff333355"
        mic_label = "SPEAKING"
        ring_anim = "ring-pulse-red"
    elif is_listening:
        mic_color = "#39ff14"
        mic_glow  = "0 0 18px #39ff14aa, 0 0 40px #39ff1455"
        mic_label = "RECORDING"
        ring_anim = "ring-pulse-green"
    else:
        mic_color = "#484f58"
        mic_glow  = "none"
        mic_label = "READY"
        ring_anim = "none"

    rgb = ','.join(str(int(accent[i:i+2], 16)) for i in (1, 3, 5))

    return f"""
<style>
.mic-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    margin: 0 auto;
    padding: 12px 0 4px;
}}
.mic-btn {{
    position: relative;
    width: 68px;
    height: 68px;
    border-radius: 50%;
    background: #0d1117;
    border: 2px solid {mic_color};
    box-shadow: {mic_glow};
    cursor: default;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    outline: none;
}}
.mic-ring {{
    position: absolute;
    width: 84px;
    height: 84px;
    border-radius: 50%;
    border: 1.5px solid {mic_color}55;
    animation: {ring_anim} 1.5s ease-in-out infinite;
}}
@keyframes ring-pulse-green {{
    0%,100% {{ transform: scale(1); opacity: 0.6; }}
    50% {{ transform: scale(1.18); opacity: 0.1; }}
}}
@keyframes ring-pulse-red {{
    0%,100% {{ transform: scale(1); opacity: 0.8; }}
    50% {{ transform: scale(1.22); opacity: 0.15; }}
}}
.mic-icon {{
    fill: {mic_color};
    filter: drop-shadow(0 0 6px {mic_color});
    transition: fill 0.3s ease;
}}
.mic-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.22em;
    color: {mic_color};
    text-shadow: 0 0 10px {mic_color}88;
    font-family: 'Segoe UI', monospace;
}}
</style>

<div class="mic-wrap">
  <div class="mic-btn">
    <div class="mic-ring"></div>
    <svg width="28" height="28" viewBox="0 0 24 24">
      <rect class="mic-icon" x="9" y="2" width="6" height="12" rx="3"/>
      <path class="mic-icon" d="M5 11a7 7 0 0 0 14 0" fill="none" stroke="{mic_color}" stroke-width="2" stroke-linecap="round" filter="url(#glow)"/>
      <line class="mic-icon" x1="12" y1="18" x2="12" y2="22" stroke="{mic_color}" stroke-width="2" stroke-linecap="round"/>
      <line class="mic-icon" x1="9"  y1="22" x2="15" y2="22" stroke="{mic_color}" stroke-width="2" stroke-linecap="round"/>
    </svg>
  </div>
  <span class="mic-label">{mic_label}</span>
</div>
"""


def _render_page_header(mode: str) -> None:
    accent     = _MODE_COLOURS.get(mode, "#bc8cff")
    mode_label = mode.upper() if mode else "STANDBY"
    st.markdown(
        f"""
        <div style="text-align:center;padding:0.5rem 1rem;margin-bottom:0.25rem;">
            <h1 style="color:#e6edf3;margin:0;font-size:1.6rem;font-weight:800;letter-spacing:0.08em;">
                ⚡ SENTINEL · AI  <span style="font-weight:300;font-size:0.9rem;color:#484f58;">v3.7</span>
            </h1>
            <p style="color:#8b949e;margin:0.2rem 0 0;font-size:0.75rem;letter-spacing:0.2em;">
                PROTOCOL <span style="color:{accent};font-weight:700;">{mode_label}</span>
                <span style="color:#484f58;margin:0 10px;">|</span>
                STATUS <span style="color:#39ff14;">ONLINE</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_context_hint(mode: str) -> None:
    if not mode:
        st.warning("⚠️ SYSTEM OFFLINE. Please initialize a configuration profile.")
        return
    hint   = _MODE_PROMPTS.get(mode, "Input command parameters...")
    accent = _MODE_COLOURS.get(mode, "#bc8cff")
    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,#161b22 0%,#0d1117 100%);
            border-left:3px solid {accent};padding:0.5rem 1rem;
            color:#8b949e;font-size:0.78rem;letter-spacing:0.05em;
            margin-bottom:0.5rem;border-radius:4px;">
            <b style="color:{accent}88;">SUGGESTED QUERY:</b>&nbsp;{hint}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _get_telemetry(mode: str) -> dict:
    viewmodels = st.session_state.get("viewmodels", {})
    if mode == "health" and "health" in viewmodels:
        return viewmodels["health"].report_data
    if mode == "industrial" and "industrial" in viewmodels:
        return viewmodels["industrial"].telemetry_data
    if mode == "planner" and "planner" in viewmodels:
        # Return the structured analysis from the planner viewmodel
        return viewmodels["planner"].output_content
    return {}


def _process_query(mode: str, query: str, robot_slot, accent: str) -> None:
    """Central logic: show thinking face → generate → stream response → speak."""
    with robot_slot:
        components.html(_robot_face_html(mode, is_thinking=True), height=520)

    telemetry = _get_telemetry(mode)
    history = st.session_state.get("robot_history", [])
    
    # Generate intelligent response using Gemini with context
    response = generate_response(mode, query, telemetry_context=telemetry, history=history)

    with robot_slot:
        components.html(_robot_face_html(mode, is_thinking=False), height=520)

    _stream_response(response, accent)
    tts_engine.speak(response, mode=mode)
    
    # Save to history for contextual continuity
    st.session_state.robot_history.append({"query": query, "response": response})


def _stream_response(response: str, accent: str) -> None:
    st.markdown(
        f"""<div style="border-top:1px solid #30363d;padding-top:0.8rem;margin-top:0.8rem;">
            <p style="color:{accent};font-size:0.72rem;font-weight:700;letter-spacing:0.15em;">◈ SYSTEM RESPONSE</p>
        </div>""",
        unsafe_allow_html=True,
    )
    box = st.empty()
    rendered = ""
    for ch in response:
        rendered += ch
        box.markdown(rendered)
        time.sleep(_TYPING_SPEED)


def _render_history() -> None:
    history = st.session_state.get("robot_history", [])
    if not history:
        return
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#484f58;font-size:0.7rem;font-weight:700;letter-spacing:0.15em;text-align:center;'>⬇ TERMINAL LOG ⬇</p>",
        unsafe_allow_html=True,
    )
    st.divider()
    for entry in reversed(history):
        label = entry["query"][:72] + ("…" if len(entry["query"]) > 72 else "")
        with st.expander(f"USER: {label}"):
            st.markdown(entry["response"])


@st.fragment(run_every=2)
def _render_interactive_agent(app_state, accent: str):
    mode       = app_state.mode
    robot_slot = st.empty()

    # ── Handle scheduled voice query ──
    if st.session_state.get("current_voice_query"):
        query = st.session_state.current_voice_query
        st.session_state.current_voice_query = None
        _process_query(mode, query, robot_slot, accent)
        # st.rerun() # Refresh to update history immediately

    is_recording = st.session_state.get("is_recording", False)
    is_speaking = tts_engine.is_speaking # Define is_speaking here for wider scope

    @st.fragment(run_every=1)
    def _face_loop():
        # Captures `mode` from outer scope
        # Note: tts_engine.is_speaking is evaluated in the fragment's context
        # We use the outer scope's `is_speaking` for consistency, but `tts_engine.is_speaking` can also be directly used here.
        components.html(_robot_face_html(mode, is_thinking=is_speaking), height=520) 

    # Call the nested fragment to render the robot face
    _face_loop()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visual Indicator for Mic ──
    st.markdown(
        _mic_button_html(accent, is_listening=is_recording, is_speaking=is_speaking),
        unsafe_allow_html=True,
    )

    # ── Interactive Controls ──
    col_l, col_c, col_r = st.columns([2, 1, 2])
    with col_c:
        if st.button("🎤 RECORD (5s)", use_container_width=True, disabled=is_recording or is_speaking):
            st.session_state.is_recording = True
            st.rerun()

    # ── Gemini STT Processing Logic ──
    if is_recording:
        audio_path = None
        with st.spinner("🎤 Recording for 5 seconds... Speak now."):
            audio_path = record_audio(duration=5)
            
        if audio_path:
            with st.spinner("🧠 Thinking..."):
                transcribed_text = transcribe_audio(audio_path)
                
            if transcribed_text and not transcribed_text.startswith("Error"):
                st.session_state.current_voice_query = transcribed_text
            else:
                st.error(f"Transcription failed: {transcribed_text}")
        else:
            st.error("Audio recording failed. Check microphone permissions.")
            
        st.session_state.is_recording = False
        st.rerun() # Trigger the query processing

    st.markdown("<br>", unsafe_allow_html=True)
    _render_context_hint(mode)

    # ── Manual Text Input ──
    st.markdown(
        f"""<div style="
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            border: 1px solid rgba({','.join(str(int(accent[i:i+2],16)) for i in (1,3,5))}, 0.25);
            border-radius: 12px 12px 0 0;
            padding: 8px 14px 4px;
            margin-bottom: -4px;
        ">
            <span style="font-size:10px;font-weight:700;letter-spacing:0.18em;color:{accent}88;
                font-family:'Segoe UI',monospace;">◈ MANUAL QUERY INPUT</span>
        </div>""",
        unsafe_allow_html=True,
    )

    user_input = st.text_area(
        label="query",
        placeholder="Enter your directive... (Shift+Enter for new line, Enter to send)",
        height=88,
        label_visibility="collapsed",
        disabled=not mode,
        key="robot_input",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.button(
            "⚡ EXECUTE",
            disabled=(not mode or not (user_input or "").strip() or is_recording),
            use_container_width=True,
            key="robot_send",
        )

    if submitted and (user_input or "").strip():
        _process_query(mode, user_input.strip(), robot_slot, accent)
        # st.rerun() # Refresh history

    _render_history()

    # ── Debug Log ──
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🛠️ LIVE SYSTEM TELEMETRY (DEBUG)", expanded=True):
        debug_logs = st.session_state.get("robot_debug", ["Waiting for system init..."])
        for log in reversed(debug_logs):
            st.code(log, language="bash")


def robot_screen(app_state) -> None:
    # Request microphone permission on load
    components.html(
        "<script>navigator.mediaDevices.getUserMedia({audio:true}).catch(()=>{});</script>",
        height=0,
    )

    # ── Session state init ──
    for key, default in [
        ("robot_history", []),
        ("robot_initialized", False),
        ("current_voice_query", None),
        ("is_recording", False)
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    mode   = app_state.mode
    accent = _MODE_COLOURS.get(mode, "#bc8cff")

    _render_page_header(mode)

    if not st.session_state.robot_initialized:
        greeting = _GREETINGS.get(mode, _GREETINGS["default"])
        tts_engine.speak(greeting, mode=mode)
        st.session_state.robot_initialized = True

    _render_interactive_agent(app_state, accent)
