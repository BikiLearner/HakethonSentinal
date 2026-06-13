import cv2
import numpy as np
import streamlit as st
import os
import urllib.request
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode


class HealthCameraEngine:

    @staticmethod
    def init():

        model_path = r"D:\TCS Works\HakethonSentinal\sentinelx-ai\models\blaze_face_short_range.tflite"
        if not os.path.exists(model_path):
            st.warning("Model not found. Downloading it now...")
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
            urllib.request.urlretrieve(url, model_path)
            st.success("Download complete!")
        # 🎥 Webcam
        if "health_cap" not in st.session_state:
            st.session_state.health_cap = cv2.VideoCapture(0)

        # 🧠 Face Detector (NEW API)
        if "face_detector" not in st.session_state:

            options = FaceDetectorOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=RunningMode.IMAGE,
                min_detection_confidence=0.5
            )

            st.session_state.face_detector = FaceDetector.create_from_options(options)

        # 🔄 Movement tracking
        if "prev_frame" not in st.session_state:
            st.session_state.prev_frame = None

    @staticmethod
    def get_frame():

        HealthCameraEngine.init()

        cap = st.session_state.health_cap
        detector = st.session_state.face_detector

        ret, frame = cap.read()
        if not ret:
            return None, {}

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 360))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 🔍 Convert to MediaPipe Image
        mp_image = vision.Image(
            image_format=vision.ImageFormat.SRGB,
            data=rgb
        )

        # 🔍 Face Detection (NEW API)
        detection_result = detector.detect(mp_image)

        face_present = False
        face_centered = False

        h, w, _ = frame.shape

        if detection_result.detections:
            face_present = True

            for det in detection_result.detections:
                bbox = det.bounding_box

                x = int(bbox.origin_x)
                y = int(bbox.origin_y)
                bw = int(bbox.width)
                bh = int(bbox.height)

                cx = x + bw // 2

                # 🎯 Center check
                if w * 0.3 < cx < w * 0.7:
                    face_centered = True

                cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

        # 🔄 Movement Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        prev = st.session_state.prev_frame
        movement_score = 0

        if prev is not None:
            diff = cv2.absdiff(prev, gray)
            movement_score = int(np.mean(diff))

        st.session_state.prev_frame = gray

        signals = {
            "face_present": face_present,
            "face_centered": face_centered,
            "movement_score": movement_score
        }

        return frame, signals