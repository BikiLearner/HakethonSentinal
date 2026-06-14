import streamlit as st
import warnings
from data.vision.health_camera_engine import HealthCameraEngine
# 🤫 SILENCE DEPRECATION LOGS
warnings.filterwarnings("ignore", message="Please replace `st.components.v1.html` with `st.iframe`.")

# Screens
from ui.screens.config_screen import config_screen
from ui.screens.monitor_screen import monitor_screen
from ui.screens.robot_screen import robot_screen

# ViewModels
from viewmodel.planner_vm import PlannerViewModel
from viewmodel.industrial_vm import make_industrial_view_model
from viewmodel.health_vm import make_health_view_model
import logging

# Core
from core.app_state import AppState

# Navigation
from ui.nav import render_nav
logging.getLogger("streamlit").setLevel(logging.ERROR)

st.set_page_config(layout="wide")

# 🔥 CREATE GLOBAL STATE (IMPORTANT)
if "app_state" not in st.session_state:
    st.session_state.app_state = AppState()
if "page" not in st.session_state:
    st.session_state.page = "Config"

app_state = st.session_state.app_state


# 🔥 CREATE VIEWMODELS
if "viewmodels" not in st.session_state:
    st.session_state.viewmodels = {
        "planner": PlannerViewModel(),
        "industrial": make_industrial_view_model(),
        "health": make_health_view_model(),
    }

viewmodels = st.session_state.viewmodels

# 🔥 SYNC VIEWMODELS WITH GLOBAL CONFIG
for vm in viewmodels.values():
    if hasattr(vm, "load_config"):
        vm.load_config(app_state.config)


HealthCameraEngine.init()

# # 🔥 SHADOW MONITORING (GATHER DATA IN THE DARK)
# if app_state.mode == "health":
#     from data.vision.health_camera_engine import HealthCameraEngine
#     try:
#         frame, signals = HealthCameraEngine.get_frame()
#         if frame is not None:
#             viewmodels["health"].on_frame_update(frame, signals)
#     except:
#         pass

# 🔥 ROUTING
page_map = {"Config": "⚙️ Config", "Monitor": "📊 Monitor", "Robot": "🤖 Robot"}
page = page_map[st.session_state.page]

# ── ROBOT LIFECYCLE MANAGEMENT ──
if page != "🤖 Robot":
    st.session_state.robot_initialized = False
    from robot.stt_engine import stt_engine
    stt_engine.stop()

if page == "⚙️ Config":
    config_screen(app_state)
elif page == "📊 Monitor":
    monitor_screen(app_state, viewmodels)
elif page == "🤖 Robot":
    robot_screen(app_state)

# 🔥 FLOATING NAVIGATION (rendered last so CSS can pin it to bottom)
render_nav(app_state)