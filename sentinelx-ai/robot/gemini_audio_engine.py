import sounddevice as sd
import scipy.io.wavfile as wav
import google.generativeai as genai
import tempfile
import os
from utils.helpers import get_gemini_api_key

def record_audio(duration: int = 5, sample_rate: int = 16000) -> str:
    """
    Records audio from the microphone for a specific duration and saves it.
    Returns the path to the temporary WAV file.
    """
    try:
        # Record audio
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Wait until the recording is finished
        
        # Save to temp directory
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "gemini_voice_input.wav")
        wav.write(file_path, sample_rate, recording)
        
        return file_path
    except Exception as e:
        print(f"STT Recording Error: {e}")
        return None

def transcribe_audio(audio_path: str) -> str:
    """
    Uploads the audio file to the Gemini API and returns the transcribed text.
    Uses the gemini-2.5-flash model.
    """
    if not audio_path or not os.path.exists(audio_path):
        return "Error: No audio file found."

    try:
        api_key = get_gemini_api_key()
        if not api_key:
            return "Error: GEMINI_API_KEY not found in .env."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Upload the audio file to Gemini
        audio_file = genai.upload_file(path=audio_path)
        
        # Request transcription
        prompt = "Listen to this audio and accurately transcribe what is being said. Only output the text transcript, no other commentary."
        response = model.generate_content([prompt, audio_file])
        
        transcription = response.text.strip()
        
        # Cleanup remote and local files
        genai.delete_file(audio_file.name)
        os.remove(audio_path)
        
        return transcription
    except Exception as e:
        error_msg = f"Gemini Transcription Error: {e}"
        print(error_msg)
        return "Error connecting to AI audio core."
