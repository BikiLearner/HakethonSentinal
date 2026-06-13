from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np
import random
from domain.usecases.industrial_explainer import explain_event

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

    def on_frame_update(self, frame, event=None,elapsed=0) -> None:

        # 🔥 Simulated telemetry
        temp = 70 + (elapsed * 1.5) + random.random()*2
        vibration = 15 + (elapsed * 0.8) + random.random()*2

        self.telemetry_data["temperature"] = temp
        self.telemetry_data["vibration"] = vibration

        # 🔥 Base status
        self.telemetry_data["status"] = "SAFE"
        self.alert_message = None

        # 🔥 If no event → normal
        if not event:
            return

        # 🔥 Map event → system state
        if event == "person_detected":
            self.telemetry_data["status"] = "WARNING"

        elif event == "high_temperature":
            self.telemetry_data["status"] = "WARNING"

        elif event == "critical":
            self.telemetry_data["status"] = "CRITICAL"

        # 🔥 🧠 REAL AI CALL (THIS IS THE CORE)
        try:
            ai_response = explain_event(
                event=event,
                temperature=temp,
                vibration=vibration
            )
            self.alert_message = ai_response

        except Exception as e:
            # 🔥 Fallback (never break demo)
            if event == "person_detected":
                self.alert_message = "⚠️ Human detected in restricted zone"
            elif event == "high_temperature":
                self.alert_message = "⚠️ Rising thermal levels detected"
            elif event == "critical":
                self.alert_message = "🔴 CRITICAL: Unsafe human-machine interaction"

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
