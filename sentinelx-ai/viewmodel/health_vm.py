from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np


@dataclass
class HealthViewModel:
    """
    ViewModel for Healthcare AI Monitoring.
    """

    # UI State
    insight_message: str | None = None

    health_metrics: dict = field(default_factory=lambda: {
        "activity_level":  "Moderate",
        "movement_score":  "62 / 100",
        "attention_level": "High",
        "posture_score":   "78 / 100",
        "overall_wellness": "MODERATE",
    })

    current_config: dict = field(default_factory=lambda: {
        "model":                 "health-observer-v1.3",
        "observation_mode":      "passive",
        "fps_target":            10,
        "insight_threshold":     0.65,
        "privacy_blur":          True,
        "logging":               False,
    })

    # Injected services
    _observation_engine: Any = field(default=None, repr=False)
    _insight_service: Any = field(default=None, repr=False)
    _metrics_aggregator: Any = field(default=None, repr=False)

    def load_config(self, config_data: dict) -> None:
        """
        Updates the internal config from the global app state.
        """
        self.current_config.update(config_data)

    def on_frame_update(self, frame: np.ndarray, signals: dict) -> None:
        """
        Called by UI every frame with real signals.
        """

        if frame is None:
            return

        # 🔥 Extract signals from MediaPipe engine
        movement = signals.get("movement_score", 0)
        face_present = signals.get("face_present", False)
        face_centered = signals.get("face_centered", False)

        # 🔥 Config thresholds (dynamic)
        low_activity_threshold = self.current_config.get("low_activity_threshold", 15)
        attention_threshold = self.current_config.get("attention_threshold", 0.5)

        # 🔥 Convert to UI-friendly metrics
        self.health_metrics["movement_score"] = f"{movement} / 100"

        self.health_metrics["activity_level"] = (
            "Active" if movement > low_activity_threshold else "Low"
        )

        self.health_metrics["attention_level"] = (
            "High" if face_centered else "Low"
        )

        # (optional placeholder until posture is implemented)
        self.health_metrics["posture_score"] = "—"

        # 🔥 REAL DECISION LOGIC

        if not face_present:
            self.insight_message = "⚠️ No person detected"
            self.health_metrics["overall_wellness"] = "CONCERN"

        elif movement < low_activity_threshold:
            self.insight_message = "⚠️ Low activity detected"
            self.health_metrics["overall_wellness"] = "LOW"

        elif not face_centered:
            self.insight_message = "⚠️ Reduced attention"
            self.health_metrics["overall_wellness"] = "MODERATE"

        else:
            self.insight_message = "✅ Normal condition"
            self.health_metrics["overall_wellness"] = "HIGH"


def make_health_view_model(
    observation_engine=None,
    insight_service=None,
    metrics_aggregator=None,
) -> HealthViewModel:
    return HealthViewModel(
        _observation_engine=observation_engine,
        _insight_service=insight_service,
        _metrics_aggregator=metrics_aggregator,
    )
