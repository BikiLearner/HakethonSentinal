from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np
import random
from domain.usecases.industrial_explainer import explain_event
import streamlit as st




@dataclass
class IndustrialViewModel:
    """
    ViewModel for the Industrial AI Monitoring screen.
    """

    # UI State
    alert_message: str | None = None

    telemetry_data: dict = field(default_factory=lambda: {
        "temperature":       72.4,
        "temperature_delta": "+1.2",
        "vibration":         18.7,
        "vibration_delta":   "-0.3",
        "status":            "SAFE",
        "uptime_hrs":        143,
    })

    current_config: dict = field(default_factory=lambda: {
        "model":               "industrial-v2.1",
        "zone_ids":            ["Z1", "Z2", "Z3"],
        "alert_threshold":     0.75,
        "fps_target":          15,
        "telemetry_interval_s": 5,
        "logging":             True,
    })

    # Injected services (optional)
    _frame_processor: Any = field(default=None, repr=False)
    _telemetry_service: Any = field(default=None, repr=False)
    _alert_service: Any = field(default=None, repr=False)

    def load_config(self, config_data: dict) -> None:
        """
        Updates the internal config from the global app state.
        """
        self.current_config.update(config_data)

    def on_frame_update(self, frame, event=None, elapsed=0) -> None:
        if "industrial_ai_called" not in st.session_state:
            st.session_state.industrial_ai_called = False
        # 🔥 Simulated industrial telemetry (more realistic)
        temp = 65 + (elapsed * 0.8) + random.random() * 1.5
        vibration = 12 + (elapsed * 0.5) + random.random() * 1.2
        load = 40 + (elapsed * 1.2) + random.random() * 3

        self.telemetry_data["temperature"] = temp
        self.telemetry_data["vibration"] = vibration
        self.telemetry_data["load"] = load

        # 🔥 Default state
        self.telemetry_data["status"] = "NORMAL"
        self.alert_message = None

        if not event:
            return

        # 🔥 Industrial event mapping
        if event == "vibration_anomaly":
            self.telemetry_data["status"] = "WARNING"

        elif event == "thermal_spike":
            self.telemetry_data["status"] = "WARNING"

        elif event == "joint_overload":
            self.telemetry_data["status"] = "WARNING"

        elif event == "critical_failure":
            self.telemetry_data["status"] = "CRITICAL"

        # 🔥 🧠 AI explanation
        try:
            if not st.session_state.industrial_ai_called:
                ai_response = explain_event(
                    event=event,
                    temperature=temp,
                    vibration=vibration,
                    load=load
                )
                st.session_state.industrial_ai_response = ai_response

                self.alert_message = ai_response
                st.session_state.industrial_ai_called = True
            else:
             self.alert_message = st.session_state.get("industrial_ai_response", self.alert_message)

        except Exception:
            # 🔥 fallback (industrial tone)
            if event == "vibration_anomaly":
                self.alert_message = "⚠️ Abnormal vibration detected in actuator assembly"

            elif event == "thermal_spike":
                self.alert_message = "⚠️ Rapid temperature increase in motor unit"

            elif event == "joint_overload":
                self.alert_message = "⚠️ Excess load detected on robotic joint"

            elif event == "critical_failure":
                self.alert_message = "🔴 CRITICAL: Mechanical instability detected"

def make_industrial_view_model(
    frame_processor=None,
    telemetry_service=None,
    alert_service=None,
) -> IndustrialViewModel:
    return IndustrialViewModel(
        _frame_processor=frame_processor,
        _telemetry_service=telemetry_service,
        _alert_service=alert_service,
    )
