"""
ui/nav.py — Floating pill navigation bar
"""

import streamlit as st
import streamlit.components.v1 as components

_PAGES = ["Config", "Monitor", "Robot"]

_NAV_META = {
    "Config":  {"icon": "⚙",  "label": "Config",  "accent": "#58a6ff"},
    "Monitor": {"icon": "◈",  "label": "Monitor", "accent": "#3fb950"},
    "Robot":   {"icon": "⬡",  "label": "Robot",   "accent": "#bc8cff"},
}

_MODE_COLOURS = {
    "industrial": "#58a6ff",
    "health":     "#3fb950",
    "planner":    "#d29922",
}


def render_nav(app_state) -> None:
    active = st.session_state.get("page", "Config")
    mode   = getattr(app_state, "mode", "") or ""
    ring   = _MODE_COLOURS.get(mode, "#bc8cff")

    # ── Trigger buttons (hidden, used by JS to fire st.rerun) ──
    st.markdown('<div class="nav-hidden">', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, p in enumerate(_PAGES):
        with cols[i]:
            if st.button(p, key=f"_nav_trigger_{p}"):
                st.session_state.page = p
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Visual nav ──
    buttons_html = ""
    for p in _PAGES:
        m       = _NAV_META[p]
        is_act  = p == active
        accent  = m["accent"]
        act_cls = "active" if is_act else ""
        buttons_html += f"""
        <button class="nav-btn {act_cls}"
                data-accent="{accent}"
                onclick="triggerPage('{p}')"
                title="{m['label']}">
          <span class="nav-icon">{m['icon']}</span>
          <span class="nav-label">{m['label']}</span>
          {"<span class='active-dot'></span>" if is_act else ""}
        </button>
        """

    rr = int(ring[1:3], 16)
    rg = int(ring[3:5], 16)
    rb = int(ring[5:7], 16)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{
  background:transparent;
  height:80px;overflow:hidden;
  display:flex;align-items:center;justify-content:center;
  font-family:'Segoe UI',system-ui,sans-serif;
}}
.nav-pill{{
  display:flex;align-items:center;gap:6px;padding:8px 10px;
  background:rgba(13,17,23,0.82);
  border:1px solid rgba({rr},{rg},{rb},0.22);border-radius:28px;
  backdrop-filter:blur(24px);
  box-shadow:0 8px 32px rgba(0,0,0,0.55),0 0 0 1px rgba({rr},{rg},{rb},0.06) inset,0 0 30px rgba({rr},{rg},{rb},0.07);
  animation:float 4s ease-in-out infinite;position:relative;
}}
@keyframes float{{0%,100%{{transform:translateY(0px)}}50%{{transform:translateY(-4px)}}}}
.nav-btn{{
  position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:3px;width:76px;height:56px;border:none;border-radius:18px;
  background:transparent;cursor:pointer;
  transition:all 0.28s cubic-bezier(0.34,1.56,0.64,1);outline:none;overflow:visible;
}}
.nav-btn:hover{{background:rgba(255,255,255,0.05);transform:translateY(-3px) scale(1.04);}}
.nav-btn:active{{transform:translateY(1px) scale(0.95);transition:all 0.08s ease;}}
.nav-icon{{font-size:20px;color:#6b7280;transition:all 0.28s ease;line-height:1;}}
.nav-label{{font-size:10px;letter-spacing:0.08em;color:#484f58;text-transform:uppercase;transition:all 0.28s ease;font-weight:500;}}
.nav-btn.active{{transform:translateY(-6px);}}
.nav-btn.active .nav-icon{{font-size:22px;}}
.nav-btn.active .nav-label{{font-weight:600;}}
.nav-btn.active[data-accent="#58a6ff"]{{background:rgba(88,166,255,0.13);box-shadow:0 6px 22px rgba(88,166,255,0.28),0 0 0 1px rgba(88,166,255,0.18) inset;}}
.nav-btn.active[data-accent="#58a6ff"] .nav-icon,.nav-btn.active[data-accent="#58a6ff"] .nav-label{{color:#58a6ff;}}
.nav-btn.active[data-accent="#3fb950"]{{background:rgba(63,185,80,0.13);box-shadow:0 6px 22px rgba(63,185,80,0.28),0 0 0 1px rgba(63,185,80,0.18) inset;}}
.nav-btn.active[data-accent="#3fb950"] .nav-icon,.nav-btn.active[data-accent="#3fb950"] .nav-label{{color:#3fb950;}}
.nav-btn.active[data-accent="#bc8cff"]{{background:rgba(188,140,255,0.13);box-shadow:0 6px 22px rgba(188,140,255,0.28),0 0 0 1px rgba(188,140,255,0.18) inset;}}
.nav-btn.active[data-accent="#bc8cff"] .nav-icon,.nav-btn.active[data-accent="#bc8cff"] .nav-label{{color:#bc8cff;}}
.active-dot{{position:absolute;bottom:-8px;left:50%;transform:translateX(-50%);width:5px;height:5px;border-radius:50%;background:currentColor;animation:dot-pulse 2s ease-in-out infinite;}}
@keyframes dot-pulse{{0%,100%{{opacity:1;transform:translateX(-50%) scale(1)}}50%{{opacity:0.5;transform:translateX(-50%) scale(0.6)}}}}
.nav-divider{{width:1px;height:28px;background:rgba(255,255,255,0.07);border-radius:1px;flex-shrink:0;}}
.ripple{{position:absolute;border-radius:50%;background:rgba(255,255,255,0.18);transform:scale(0);animation:ripple-out 0.45s ease-out forwards;pointer-events:none;}}
@keyframes ripple-out{{to{{transform:scale(3.5);opacity:0;}}}}
</style>
</head>
<body>
<div class="nav-pill">
  {_insert_dividers(buttons_html)}
</div>
<script>
function triggerPage(page) {{
  var all = window.parent.document.querySelectorAll('button');
  for (var i = 0; i < all.length; i++) {{
    if (all[i].textContent.trim() === page) {{
      all[i].click();
      return;
    }}
  }}
}}

/* 🔥 HIDE STREAMLIT BUTTONS */
window.addEventListener("load", function() {{
  const buttons = window.parent.document.querySelectorAll("button");

  buttons.forEach(btn => {{
    if (
      btn.innerText.trim() === "Config" ||
      btn.innerText.trim() === "Monitor" ||
      btn.innerText.trim() === "Robot"
    ) {{
      btn.style.display = "none";
    }}
  }});
}});
</script>
</body>
</html>"""

    st.markdown('<div class="nav-wrapper">', unsafe_allow_html=True)
    components.html(html, height=80, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
<style>

/* 🔥 ONLY TARGET NAV IFRAME */
.nav-wrapper iframe {
    position: fixed !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;

    z-index: 999999 !important;

    width: auto !important;
    height: 80px !important;

    border: none !important;
    background: transparent !important;
}

/* Prevent overlap */
.main .block-container {
    padding-bottom: 120px !important;
}

</style>
""", unsafe_allow_html=True)


def _insert_dividers(buttons_html: str) -> str:
    parts = buttons_html.strip().split('<button class="nav-btn')
    parts = [p for p in parts if p.strip()]
    rebuilt = []
    for i, part in enumerate(parts):
        rebuilt.append('<button class="nav-btn' + part)
        if i < len(parts) - 1:
            rebuilt.append('<div class="nav-divider"></div>')
    return "\n".join(rebuilt)
