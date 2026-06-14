import google.generativeai as genai
import json
from utils.helpers import get_gemini_api_key

def generate_response(mode: str, user_input: str, telemetry_context: dict = None, history: list = None) -> str:
    """
    Calls Google Gemini API with telemetry and conversation history context to generate a response.
    """
    mode = mode.lower()

    # 1. Construct System Prompt based on Mode and Data
    if mode == "industrial":
        system_role = (
            "You are an Industrial Safety Assistant for SentinelX AI. "
            "You provide technical status and safety alerts about machinery. "
            "Speak conversationally, professionally, and convincingly. "
            "Keep responses under 3 sentences for voice clarity."
        )
    elif mode == "health":
        system_role = (
            "You are a Clinical Wellness Assistant for SentinelX AI. "
            "You MUST use the provided CURRENT TELEMETRY DATA (e.g. Physical Variance, Kinematic Entropy, status) in your response. "
            "Directly reference the data to explain the user's current physical state. "
            "Keep responses under 3 sentences for voice clarity."
        )
    else:
        system_role = "You are a helpful AI assistant. Keep it brief."

    # 2. Add Telemetry Data to prompt
    data_context = ""
    if telemetry_context:
        data_context = f"\nCURRENT TELEMETRY DATA: {json.dumps(telemetry_context)}"

    # 3. Add History Context
    history_context = ""
    if history:
        history_context = "\nCONVERSATION HISTORY:\n"
        # Keep last 3 turns to maintain recent context without diluting the prompt
        for entry in history[-3:]:
            history_context += f"USER: {entry['query']}\nASSISTANT: {entry['response']}\n"

    full_prompt = (
        f"{system_role}\n\n"
        f"{data_context}\n"
        f"{history_context}\n"
        f"CURRENT USER SAYS: \"{user_input}\"\n\n"
        f"ASSISTANT RESPONSE (must be 3 sentences or less):"
    )

    # 4. Call Gemini API
    def _add_log(message):
        import streamlit as st
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        if "robot_debug" not in st.session_state:
            st.session_state.robot_debug = []
        st.session_state.robot_debug.append(f"[{ts}] 🧠 {message}")
        st.session_state.robot_debug = st.session_state.robot_debug[-10:]

    try:
        _add_log(f"Querying Gemini 2.5 Flash (Mode: {mode})...")

        api_key = get_gemini_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        
        genai.configure(api_key=api_key)
        # Using the requested modern model
        model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(full_prompt)

        _add_log("Gemini response received.")
        return response.text.strip()

    except Exception as e:
        error_message = f"Error calling Gemini API: {e}"
        _add_log(error_message)
        print(error_message)
        return "I'm sorry, I'm having trouble connecting to my AI core right now."
