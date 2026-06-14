import sounddevice as sd
import numpy as np
import speech_recognition as sr
import threading
import queue
import time
import io
import scipy.io.wavfile as wav

class STTEngine:
    """
    Hands-free Speech-to-Text engine using background recording.
    Enhanced with muting to prevent robot hearing itself.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self._is_listening = False
        self._is_muted = False
        self.sample_rate = 16000
        self.silence_threshold = 0.01  # Energy threshold for silence
        self.listen_thread = None

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        if not self._is_muted:
            self.audio_queue.put(indata.copy())

    def mute(self):
        self._is_muted = True

    def unmute(self):
        # Clear queue when unmuting to avoid processing stale audio
        while not self.audio_queue.empty():
            try: self.audio_queue.get_nowait()
            except: break
        self._is_muted = False

    def _add_log(self, message):
        import streamlit as st
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        if "robot_debug" not in st.session_state:
            st.session_state.robot_debug = []
        st.session_state.robot_debug.append(f"[{ts}] 👂 {message}")
        # Keep last 10 logs
        st.session_state.robot_debug = st.session_state.robot_debug[-10:]

    def listen(self, callback):
        """
        Starts listening in a background thread.
        When a sentence is detected, calls 'callback(text)'.
        """
        if self._is_listening:
            return
        
        def run():
            self._is_listening = True
            self._add_log("Mic listening active")
            
            try:
                with sd.InputStream(samplerate=self.sample_rate, channels=1, callback=self._audio_callback):
                    accumulated_audio = []
                    silent_chunks = 0
                    
                    while self._is_listening:
                        try:
                            chunk = self.audio_queue.get(timeout=0.5)
                            accumulated_audio.append(chunk)
                            
                            # Energy-based silence detection
                            energy = np.linalg.norm(chunk) / np.sqrt(len(chunk))
                            
                            if energy > self.silence_threshold:
                                if silent_chunks == 0 and len(accumulated_audio) == 1:
                                     self._add_log("Audio pulse detected...")
                                silent_chunks = 0
                            else:
                                silent_chunks += 1
                            
                            # If we have audio and then ~1.5 seconds of silence, process it
                            if silent_chunks > 30 and len(accumulated_audio) > 20:
                                self._add_log("Processing audio buffer...")
                                self._process_audio(accumulated_audio, callback)
                                accumulated_audio = []
                                silent_chunks = 0
                                
                        except queue.Empty:
                            continue
            except Exception as e:
                print(f"Stream Error: {e}")
                self._is_listening = False

        self.listen_thread = threading.Thread(target=run, daemon=True)
        self.listen_thread.start()

    def stop(self):
        self._is_listening = False
        if self.listen_thread:
            # We don't join to avoid blocking the UI, 
            # the thread will exit naturally on the next loop check
            self.listen_thread = None

    def _process_audio(self, chunks, callback):
        """Converts raw chunks to WAV and transcribes."""
        if not chunks:
            return
            
        audio_data = np.concatenate(chunks, axis=0)
        
        # Save to buffer
        byte_io = io.BytesIO()
        wav.write(byte_io, self.sample_rate, (audio_data * 32767).astype(np.int16))
        byte_io.seek(0)
        
        # Transcribe
        with sr.AudioFile(byte_io) as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio)
                if text:
                    self._add_log(f"Recognized: '{text}'")
                    callback(text)
            except sr.UnknownValueError:
                self._add_log("Audio unintelligible (silence?)")
            except Exception as e:
                print(f"STT Error: {e}")

# Singleton instance
stt_engine = STTEngine()
