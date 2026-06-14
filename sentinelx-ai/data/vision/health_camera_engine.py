import cv2
import numpy as np
import streamlit as st
import os
import urllib.request
from typing import Any
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode
import mediapipe as mp

class HealthCameraEngine:

    @staticmethod
    def init() -> None:
        """Initializes the model, camera, and state once."""
        model_path = "blaze_face_short_range.tflite"

        # Download the model dynamically to the local working directory
        if not os.path.exists(model_path):
            with st.spinner("Downloading MediaPipe Face Detection model..."):
                url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
                urllib.request.urlretrieve(url, model_path)

        # 🎥 Webcam Initialization (Run Once)
        if "health_cap" not in st.session_state or st.session_state.health_cap is None:
            # We assume camera index 0 (default webcam). 
            # If using multiple, add a Streamlit dropdown to select it.
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else 0)
            if cap.isOpened():
                st.session_state.health_cap = cap
            else:
                st.session_state.health_cap = None
                st.error("Failed to connect to Webcam.")

        # 🧠 Face Detector Initialization (Run Once)
        if "face_detector" not in st.session_state or st.session_state.face_detector is None:
            options = FaceDetectorOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=RunningMode.IMAGE,
                min_detection_confidence=0.5
            )
            st.session_state.face_detector = FaceDetector.create_from_options(options)

        # 🔄 Movement tracking state
        if "prev_frame" not in st.session_state:
            st.session_state.prev_frame = None

    @staticmethod
    def get_frame() -> tuple[np.ndarray | None, dict[str, Any]]:
        """Grabs the current frame and computes AI signals."""
        cap = st.session_state.get("health_cap")
        detector = st.session_state.get("face_detector")

        if cap is None or not cap.isOpened() or detector is None:
            return None, {}

        ret, frame = cap.read()
        if not ret:
            return None, {}

        # Preprocess frame
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 360))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 🔍 MediaPipe Detection
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = detector.detect(mp_image)

        face_present = False
        face_centered = False
        h, w, _ = frame.shape

        if detection_result.detections:
            face_present = True
            for det in detection_result.detections:
                bbox = det.bounding_box
                x, y, bw, bh = int(bbox.origin_x), int(bbox.origin_y), int(bbox.width), int(bbox.height)
                cx = x + bw // 2

                # 🎯 Center check
                if w * 0.3 < cx < w * 0.7:
                    face_centered = True

                # Draw bounding box
                cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

        # 🔄 Movement Detection via Background Subtraction
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 🔥 store lightweight version (downscaled) for motion detection
        gray_small = cv2.resize(gray, (160, 90))
        prev = st.session_state.get("prev_frame")
        movement_score = 0

        if prev is not None:
            # Ensure shapes match by comparing small versions
            diff = cv2.absdiff(prev, gray_small)
            movement_score = int(np.mean(diff))

        st.session_state.prev_frame = gray_small

        signals = {
            "face_present": face_present,
            "face_centered": face_centered,
            "movement_score": movement_score
        }

        return frame, signals