import streamlit as st

from ui.widgets.industrial_widget import industrial_widget
from ui.widgets.health_widget import health_widget
from ui.widgets.planner_widget import planner_widget


def monitor_screen(app_state, viewmodels):
    st.title("📊 Monitoring System")

    mode = app_state.mode

    st.markdown(f"### Active Mode: **{mode.upper()}**")

    st.divider()

    if mode == "industrial":
        industrial_widget(viewmodels["industrial"])

    elif mode == "health":
        health_widget(viewmodels["health"])

    elif mode == "planner":
        planner_widget(viewmodels["planner"])