import cv2
import time
import streamlit as st


class VideoEngine:

    @staticmethod
    def get_frame(video_path="assets/videos/13814831_3840_2160_100fps.mp4"):
        if "cap" not in st.session_state or not st.session_state.cap.isOpened():
            st.session_state.cap = cv2.VideoCapture(video_path)
            st.session_state.start_time = time.time()

        cap = st.session_state.cap
        ret, frame = cap.read()

        # Loop the video when it ends
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        # GUARD: never resize a None frame (this is what silently kills the feed)
        if not ret or frame is None:
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "NO SIGNAL — CHECK VIDEO PATH", (60, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 255), 2)
            elapsed = int(time.time() - st.session_state.start_time)
            return frame, "critical", elapsed

        frame = cv2.resize(frame, (640, 360))
        elapsed = int(time.time() - st.session_state.start_time)
        frame, event = VideoEngine._process(frame, elapsed)
        return frame, event, elapsed


    @staticmethod
    def _process(frame, elapsed):
        h, w, _ = frame.shape
        event = "normal"

        # ── Determine situation ──────────────────────────────────────────────
        if elapsed < 3:
            event = "normal"
            border_color  = (0, 255, 120)      # green
            overlay_alpha = 0.0
            status_text   = "ALL ZONES NOMINAL"
            status_color  = (0, 255, 120)

        elif elapsed < 6:
            event = "person_detected"
            border_color  = (0, 200, 255)      # cyan
            overlay_alpha = 0.08
            status_text   = "PERSON DETECTED — VERIFY CLEARANCE"
            status_color  = (0, 200, 255)

            # Bounding box around detected person
            px, py = w // 2, h // 2
            cv2.rectangle(frame, (px - 40, py - 80), (px + 40, py + 80),
                          (0, 200, 255), 2)
            # Corner ticks on bounding box
            for dx, dy in [(-40, -80), (40, -80), (-40, 80), (40, 80)]:
                sx, sy = px + dx, py + dy
                ex = sx + (8 if dx > 0 else -8)
                ey = sy + (8 if dy > 0 else -8)
                cv2.line(frame, (sx, sy), (ex, sy), (0, 200, 255), 2)
                cv2.line(frame, (sx, sy), (sx, ey), (0, 200, 255), 2)

            cv2.putText(frame, "ID:UNKNOWN", (px - 36, py + 95),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 200, 255), 1)

        elif elapsed < 8:
            event = "high_temperature"
            border_color  = (0, 140, 255)      # orange
            overlay_alpha = 0.12
            status_text   = "THERMAL ANOMALY DETECTED"
            status_color  = (0, 140, 255)

            # Thermal heat shimmer rectangle
            cv2.rectangle(frame, (w // 3 + 20, h // 4), (2 * w // 3 - 20, 3 * h // 4),
                          (0, 140, 255), 1)
            cv2.putText(frame, "TEMP RISING", (w // 3 + 30, h // 4 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 1)

        else:
            event = "critical"
            border_color  = (30, 30, 255)      # red
            overlay_alpha = 0.22 if elapsed % 2 == 0 else 0.08
            status_text   = "CRITICAL RISK — UNSAFE INTERACTION"
            status_color  = (30, 30, 255)

        # ── Full-frame colored overlay (tint) ───────────────────────────────
        if overlay_alpha > 0:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), border_color, -1)
            frame = cv2.addWeighted(overlay, overlay_alpha, frame, 1 - overlay_alpha, 0)

        # ── Single perimeter border — color matches situation ────────────────
        cv2.rectangle(frame, (2, 2), (w - 2, h - 2), border_color, 2)

        # ── Corner HUD brackets ──────────────────────────────────────────────
        tick = 18
        for (cx, cy) in [(2, 2), (w - 2, 2), (2, h - 2), (w - 2, h - 2)]:
            hx = cx + (tick if cx == 2 else -tick)
            vy = cy + (tick if cy == 2 else -tick)
            cv2.line(frame, (cx, cy), (hx, cy), border_color, 2)
            cv2.line(frame, (cx, cy), (cx, vy), border_color, 2)

        # ── Top-left: AI badge ───────────────────────────────────────────────
        cv2.putText(frame, "SENTINEL AI v3.7",
                    (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.42, border_color, 1)

        # ── Top-right: elapsed timer ─────────────────────────────────────────
        timer_str = f"T+{elapsed:04d}s"
        (tw, _), _ = cv2.getTextSize(timer_str, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(frame, timer_str,
                    (w - tw - 12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.42, border_color, 1)

        # ── Bottom status bar ────────────────────────────────────────────────
        cv2.rectangle(frame, (0, h - 28), (w, h), (8, 10, 16), -1)
        cv2.putText(frame, f"◈ {status_text}",
                    (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.46, status_color, 1)

        # ── Scan-line effect (subtle horizontal lines) ───────────────────────
        scan = frame.copy()
        for y in range(0, h, 4):
            cv2.line(scan, (0, y), (w, y), (0, 0, 0), 1)
        frame = cv2.addWeighted(scan, 0.15, frame, 0.85, 0)

        return frame, event