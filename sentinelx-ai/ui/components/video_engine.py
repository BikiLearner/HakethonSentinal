import cv2
import time
import streamlit as st


class VideoEngine:

    @staticmethod
    def get_frame(video_path="assets/videos/13814831_3840_2160_100fps.mp4"):

        if "cap" not in st.session_state:
            st.session_state.cap = cv2.VideoCapture(video_path)

        if "start_time" not in st.session_state:
            st.session_state.start_time = time.time()

        cap = st.session_state.cap

        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        frame = cv2.resize(frame, (640, 360))
        elapsed = int(time.time() - st.session_state.start_time)


        frame, event = VideoEngine._process(frame,elapsed)

        return frame, event ,elapsed 

    @staticmethod
    def _process(frame, elapsed):
        h, w, _ = frame.shape

        event = "normal"

        # ───────────── ZONES ─────────────
        # Safe (left)
        cv2.rectangle(frame, (0, 0), (w//3, h), (0, 255, 0), 2)
        cv2.putText(frame, "SAFE ZONE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Machine (center)
        cv2.rectangle(frame, (w//3, 0), (2*w//3, h), (255, 255, 0), 2)
        cv2.putText(frame, "MACHINE ZONE", (w//3 + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        # Danger (right)
        cv2.rectangle(frame, (2*w//3, 0), (w, h), (0, 0, 255), 2)
        cv2.putText(frame, "DANGER ZONE", (2*w//3 + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # ───────────── AI HUD ─────────────
        cv2.putText(frame, "AI MONITORING ACTIVE",
                    (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1)

        # ───────────── SCENARIO TIMELINE ─────────────

        # 🔹 0–3s → Normal
        if elapsed < 3:
            event = "normal"

        # 🔹 3–6s → Person enters
        elif elapsed < 6:
            event = "person_detected"

            x, y = w//2, h//2

            cv2.rectangle(frame, (x-40, y-80), (x+40, y+80), (0, 0, 255), 3)
            cv2.putText(frame, "PERSON DETECTED",
                        (x-60, y-90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 255),
                        2)

        # 🔹 6–8s → Temperature rising
        elif elapsed < 8:
            event = "high_temperature"

            cv2.putText(frame, "TEMP RISING",
                        (200, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 165, 255),
                        2)

        # 🔹 8–10s → CRITICAL
        else:
            event = "critical"

            # 🔥 Blinking red overlay
            if elapsed % 2 == 0:
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), -1)
                frame = cv2.addWeighted(overlay, 0.25, frame, 0.75, 0)

            cv2.putText(frame, "CRITICAL RISK",
                        (180, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3)

        return frame, event
