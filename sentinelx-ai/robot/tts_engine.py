import os
import asyncio
import edge_tts
from playsound import playsound
import threading
import time

class TTSEngine:
    """
    Handles Text-to-Speech using Microsoft Edge's high-quality voices.
    Fixed to avoid asyncio event loop closure errors.
    """
    
    VOICES = {
        "industrial": "en-US-GuyNeural", 
        "health": "en-GB-SoniaNeural",
        "default": "en-US-AriaNeural"
    }

    def __init__(self):
        self.output_dir = "assets/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        self._is_speaking = False

    def _add_log(self, message):
        import streamlit as st
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        if "robot_debug" not in st.session_state:
            st.session_state.robot_debug = []
        st.session_state.robot_debug.append(f"[{ts}] 🔊 {message}")
        st.session_state.robot_debug = st.session_state.robot_debug[-10:]

    def speak(self, text, mode="default"):
        if not text:
            return

        def run_tts():
            from robot.stt_engine import stt_engine
            stt_engine.mute() # 🔥 Stop listening while speaking
            
            self._is_speaking = True
            try:
                self._add_log(f"Synthesizing speech: '{text[:30]}...'")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                voice = self.VOICES.get(mode, self.VOICES["default"])
                filename = f"speech_{os.getpid()}_{int(time.time()*1000)}.mp3"
                file_path = os.path.join(self.output_dir, filename)
                
                communicate = edge_tts.Communicate(text, voice)
                loop.run_until_complete(communicate.save(file_path))
                
                self._add_log("Audio playback started")
                playsound(file_path)
                self._add_log("Audio playback finished")
                
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                self._add_log(f"TTS Error: {e}")
            finally:
                self._is_speaking = False
                stt_engine.unmute() # 🔥 Resume listening

        threading.Thread(target=run_tts, daemon=True).start()

    @property
    def is_speaking(self):
        return self._is_speaking

tts_engine = TTSEngine()
