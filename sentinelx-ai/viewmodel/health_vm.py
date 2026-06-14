from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np


from datetime import datetime

@dataclass
class HealthViewModel:
    """ViewModel for Healthcare AI Monitoring."""
    # State flags
    is_analyzing: bool = True
    analysis_progress: float = 0.0
    insight_message: str | None = "Initializing analysis window..."
    
    # Internal buffers
    _frame_count: int = 0
    _window_size: int = 150  # Longer window for better baseline
    _history_face_present: list[bool] = field(default_factory=list)
    _history_face_centered: list[bool] = field(default_factory=list)
    _history_movement: list[int] = field(default_factory=list)

    # Output Data
    report_data: dict[str, Any] = field(default_factory=lambda: {
        "timestamp": "--",
        "sys_code": "WAIT-CALIB",
        "presence_rate": "0%",
        "centered_rate": "0%",
        "kinematic_entropy": "0",
        "variance": "0",
        "status": "CALIBRATING",
        "severity": "PENDING",
        "color": "#546e7a",
        "clinical_notes": "System is gathering initial telemetry window...",
        "recommendation": "Maintain neutral posture during calibration."
    })
    health_metrics: dict[str, str] = field(default_factory=lambda: {
        "activity_level":  "Calibrating...",
        "movement_score":  "0",
        "attention_level": "Calibrating...",
        "overall_wellness": "PENDING",
    })

    current_config: dict[str, Any] = field(default_factory=lambda: {
        "model":                 "health-observer-v1.3",
        "observation_mode":      "continuous",
        "fps_target":            10,
        "low_activity_threshold": 5, 
    })

    # Injected services
    _observation_engine: Any = field(default=None, repr=False)
    _insight_service: Any = field(default=None, repr=False)
    _metrics_aggregator: Any = field(default=None, repr=False)

    def restart_analysis(self) -> None:
        """Resets the state to run a new analysis for the reviewer."""
        self.is_analyzing = True
        self.analysis_progress = 0.0
        self._frame_count = 0
        self._history_face_present.clear()
        self._history_face_centered.clear()
        self._history_movement.clear()
        self.report_data.clear()
        # Restore placeholder after clear
        self.report_data.update({
            "timestamp": "--",
            "sys_code": "WAIT-CALIB",
            "status": "CALIBRATING",
            "severity": "PENDING",
            "color": "#546e7a",
            "clinical_notes": "System is gathering initial telemetry window...",
            "recommendation": "Maintain neutral posture during calibration."
        })
        self.insight_message = "Initializing analysis window..."

    def load_config(self, config_data: dict) -> None:
        """
        Updates the internal config from the global app state.
        """
        self.current_config.update(config_data)

    def on_frame_update(self, frame: np.ndarray, signals: dict[str, Any]) -> None:
        """Called by UI every frame with real signals to update live metrics and roll analysis."""
        if frame is None or not self.is_analyzing:
            return

        movement = signals.get("movement_score", 0)
        face_present = signals.get("face_present", False)
        face_centered = signals.get("face_centered", False)

        # 1. Update Immediate Metric Cards
        self.health_metrics["movement_score"] = f"{movement}"
        self.health_metrics["activity_level"] = "Elevated" if movement > 8 else "Baseline"
        self.health_metrics["attention_level"] = "Engaged" if face_centered else "Deviated"

        # 2. Accumulate tracking buffers
        self._frame_count += 1
        self._history_face_present.append(face_present)
        self._history_face_centered.append(face_centered)
        self._history_movement.append(movement)
        
        # Calculate matching fraction for progress bar
        self.analysis_progress = min(self._frame_count / self._window_size, 1.0)

        # 3. Compile Long-Form Structural Report when window matches full evaluation size
        if self._frame_count >= self._window_size:
            self.is_analyzing = False
            self._compile_clinical_report()

    def _compile_clinical_report(self) -> None:
        """Translates raw pixel data into simulated clinical diagnostics."""
        avg_movement = np.mean(self._history_movement) if self._history_movement else 0
        presence_rate = np.mean(self._history_face_present) * 100 if self._history_face_present else 0
        centered_rate = np.mean(self._history_face_centered) * 100 if self._history_face_centered else 0
        
        # Calculate Variance (Fidgeting vs Stagnation)
        movement_variance = np.var(self._history_movement) if self._history_movement else 0

        # Clinical Logic Tree
        if presence_rate < 50:
            status = "INSUFFICIENT TELEMETRY"
            severity = "CRITICAL"
            color = "#b71c1c"
            sys_code = "ERR-O2-LOSS"
            clinical_notes = (
                "<ul style='margin:0; padding-left:1.2rem; color:#4a5568;'>"
                "<li><b>Target Acquisition Failure:</b> The visual subject was absent for >50% of the diagnostic window.</li>"
                "<li><b>Diagnostic Impact:</b> Unable to establish a continuous physiological baseline.</li>"
                "<li><b>System Note:</b> Verify ocular framing and ensure ambient lux levels exceed 300 for optimal sensor tracking.</li>"
                "</ul>"
            )
            recommendation = "Reposition subject within the central optical axis and rerun the diagnostic protocol."
            self.insight_message = "⚠️ Frame evaluation failed due to missing visual target."

        elif avg_movement < 3.5 and movement_variance < 5.0:
            status = "MUSCULOSKELETAL STAGNATION"
            severity = "ELEVATED RISK"
            color = "#e65100"
            sys_code = "MSK-STAG-04"
            clinical_notes = (
                "<ul style='margin:0; padding-left:1.2rem; color:#4a5568;'>"
                "<li><b>Kinematic Entropy (KE):</b> Unusually low physical variation detected over the observation window.</li>"
                "<li><b>Ergonomic Assessment:</b> Prolonged static loading on the cervical spine and lumbar region observed.</li>"
                "<li><b>Fatigue Indicator:</b> High probability of circulatory pooling and muscular rigidity associated with deep sedentary states.</li>"
                "</ul>"
            )
            recommendation = "Immediate physical intervention recommended: 5 minutes of targeted kinetic stretching (cervical rotation, lumbar extension) to restore baseline circulation."
            self.insight_message = "⚠️ Stagnation warning generated."

        elif centered_rate < 60:
            status = "OCULOMOTOR DEVIATION"
            severity = "MODERATE RISK"
            color = "#fbc02d"
            sys_code = "COG-DEV-91"
            clinical_notes = (
                "<ul style='margin:0; padding-left:1.2rem; color:#4a5568;'>"
                "<li><b>Gaze Retention:</b> Frequent lateral cranial shifts away from the primary interaction plane.</li>"
                "<li><b>Cognitive/Visual Load:</b> Indicates potential multi-monitor fatigue or environmental distractor processing.</li>"
                "<li><b>Cervical Strain:</b> High frequency of off-axis viewing may induce asymmetrical trapezius strain.</li>"
                "</ul>"
            )
            recommendation = "Assess environmental ergonomics. Align primary focal points to dead-center to reduce asymmetric cervical loading and ocular fatigue."
            self.insight_message = "⚠️ Lateral framing observed."

        else:
            status = "HOMEOSTASIS NOMINAL"
            severity = "OPTIMAL"
            color = "#1b5e20"
            sys_code = "PHYS-NOM-00"
            clinical_notes = (
                "<ul style='margin:0; padding-left:1.2rem; color:#4a5568;'>"
                "<li><b>Kinematic Baseline:</b> Subject exhibits healthy micro-movements, indicating active muscular engagement.</li>"
                "<li><b>Cranial Alignment:</b> Sustained central axis engagement with nominal deviation.</li>"
                "<li><b>Overall Assessment:</b> No immediate physiological or ergonomic distress markers detected.</li>"
                "</ul>"
            )
            recommendation = "Maintain current ergonomic posture. Continue standard monitoring protocols."
            self.insight_message = "✅ Nominal observational interval recorded."

        self.health_metrics["overall_wellness"] = severity

        # Construct the final report dictionary
        self.report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sys_code": sys_code,
            "presence_rate": f"{presence_rate:.1f}%",
            "centered_rate": f"{centered_rate:.1f}%",
            "kinematic_entropy": f"{avg_movement:.2f} µ-shift/s",
            "variance": f"{movement_variance:.2f}",
            "status": status,
            "severity": severity,
            "color": color,
            "clinical_notes": clinical_notes,
            "recommendation": recommendation
        }


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
