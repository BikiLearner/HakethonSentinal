import requests
import json

def generate_response(mode: str, user_input: str, telemetry_context: dict = None) -> str:
    """
    Calls local Ollama instance (Llama 3) with telemetry context.
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
            "If telemetry is calibrating, inform the user. "
            "Speak clinically but empathetically. Provide actionable wellness advice based on the data. "
            "Keep responses under 3 sentences for voice clarity."
        )
    else:
        system_role = "You are a helpful AI assistant. Keep it brief."

    # 2. Add Telemetry Data to prompt
    data_context = ""
    if telemetry_context:
        data_context = f"\nCURRENT TELEMETRY DATA: {json.dumps(telemetry_context)}"

    full_prompt = (
        f"{system_role}\n"
        f"USER SAYS: {user_input}\n"
        f"{data_context}\n"
        f"ASSISTANT RESPONSE:"
    )

    # 3. Call Ollama
    def _add_log(message):
        import streamlit as st
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        if "robot_debug" not in st.session_state:
            st.session_state.robot_debug = []
        st.session_state.robot_debug.append(f"[{ts}] 🧠 {message}")
        st.session_state.robot_debug = st.session_state.robot_debug[-10:]

    try:
        _add_log(f"Querying A.I. Core (Mode: {mode})...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100
                }
            },
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json().get("response", "I am processing the data.")
        else:
            _add_log("A.I. Core returned error status")
            return "A.I. Core connection error. Status: Offline."

    except Exception as e:
        _add_log(f"A.I. Core connection failed: {e}")
        return "I am currently unable to reach my advanced logic core. Please stand by."
