import cv2
import numpy as np
import streamlit as st
import os
import urllib.request
from typing import Any
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode
import mediapipe as mp


class HealthCameraEngine:

    @staticmethod
    def init() -> None:
        """Initializes the model, camera, and state once."""
        model_path = "blaze_face_short_range.tflite"

        if not os.path.exists(model_path):
            with st.spinner("Downloading MediaPipe Face Detection model..."):
                url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
                urllib.request.urlretrieve(url, model_path)

        if "health_cap" not in st.session_state or st.session_state.health_cap is None:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else 0)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                cap.set(cv2.CAP_PROP_FPS, 30)
                # Warm-up: drain corrupt startup frames
                for _ in range(15):
                    cap.read()
                st.session_state.health_cap = cap
            else:
                st.session_state.health_cap = None
                st.error("Failed to connect to Webcam.")

        if "face_detector" not in st.session_state or st.session_state.face_detector is None:
            options = FaceDetectorOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=RunningMode.IMAGE,
                min_detection_confidence=0.5
            )
            st.session_state.face_detector = FaceDetector.create_from_options(options)

        if "prev_frame" not in st.session_state:
            st.session_state.prev_frame = None

        # Last good frame cache — key fix for flash/black glitch
        if "last_good_frame" not in st.session_state:
            st.session_state.last_good_frame = None
        if "last_good_signals" not in st.session_state:
            st.session_state.last_good_signals = {}

    @staticmethod
    def get_frame() -> tuple[np.ndarray | None, dict[str, Any]]:
        """Grabs the current frame and computes AI signals."""
        cap = st.session_state.get("health_cap")
        detector = st.session_state.get("face_detector")

        if cap is None or not cap.isOpened() or detector is None:
            return None, {}

        # Drain stale buffered frames
        for _ in range(4):
            if not cap.grab():
                # grab failed — return last good frame to avoid flash
                return (
                    st.session_state.get("last_good_frame"),
                    st.session_state.get("last_good_signals", {}),
                )

        ret, frame = cap.retrieve()

        # If frame is bad/black, return last known good frame instead of None
        if not ret or frame is None or frame.size == 0:
            return (
                st.session_state.get("last_good_frame"),
                st.session_state.get("last_good_signals", {}),
            )

        # Preprocess
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 360))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe Detection
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = detector.detect(mp_image)

        face_present = False
        face_centered = False
        h, w, _ = frame.shape

        if detection_result.detections:
            face_present = True
            for det in detection_result.detections:
                bbox = det.bounding_box
                x, y, bw, bh = (
                    int(bbox.origin_x), int(bbox.origin_y),
                    int(bbox.width), int(bbox.height),
                )
                cx = x + bw // 2
                if w * 0.3 < cx < w * 0.7:
                    face_centered = True
                cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

        # Movement Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_small = cv2.resize(gray, (160, 90))
        prev = st.session_state.get("prev_frame")
        movement_score = 0

        if prev is not None and prev.shape == gray_small.shape:
            diff = cv2.absdiff(prev, gray_small)
            movement_score = int(np.mean(diff))

        st.session_state.prev_frame = gray_small

        signals = {
            "face_present": face_present,
            "face_centered": face_centered,
            "movement_score": movement_score,
        }

        # Cache this good frame so bad frames fall back to it
        st.session_state.last_good_frame = frame
        st.session_state.last_good_signals = signals

        return frame, signals