# SentinelX AI: Multi-Modal Monitoring and Conversational AI System

## Project Overview

SentinelX AI is a sophisticated Streamlit-based application designed for multi-modal monitoring and intelligent conversational assistance. It leverages advanced AI models, including Google Gemini, to process diverse data streams (vision, text, audio) and provide contextual insights across various operational modes: Health, Industrial, Planner, and a fully interactive Robot assistant.

The project is built with a clean Model-View-ViewModel (MVVM) architecture, ensuring modularity, scalability, and maintainability. Its primary goal is to demonstrate a robust AI integration in a real-time monitoring and interaction system.

## Features

*   **Multi-Modal AI**: Seamlessly integrates vision, text, and audio processing capabilities.
*   **Modular Design**: Adheres strictly to an MVVM architecture with clear separation of concerns, making it easy to extend and maintain.
*   **Health Mode**: Provides real-time human kinematic and physiological analysis using webcam input and MediaPipe for pose estimation.
*   **Industrial Mode**: Simulates an industrial environment, detecting safety events from video feeds and offering AI-driven explanations.
*   **Planner Mode**: Offers AI-powered analysis of various file types (.py, .txt, .md, .docx), providing structured insights and algorithmic explanations.
*   **Robot Assistant Mode**: Features an interactive conversational AI, now powered by Gemini for highly accurate Speech-to-Text (STT) and intelligent text generation, complemented by fast Text-to-Speech (TTS).
*   **Google Gemini API Integration**: Extensively utilizes the Google Gemini API for complex language understanding, generation, and now, audio transcription.

## Architecture: A Deep Dive

The SentinelX AI application rigorously follows the Model-View-ViewModel (MVVM) pattern, structured across distinct, purpose-driven directories. This structure enhances maintainability, testability, and clarity.

```
sentinelx-ai/
├── core/             # Application lifecycle management and global state
├── data/             # External data interfaces, sensors, and raw processing
├── domain/           # Business logic, use cases, and AI model interactions
├── robot/            # Core components for voice interaction (STT/TTS)
├── ui/               # Streamlit user interface elements (screens, widgets)
├── viewmodel/        # UI state management and data orchestration
└── utils/            # Shared helper functions and configurations
```

### Core Architectural Principles

*   **`core/app_state.py`**: This file defines the `AppState` class, a singleton that acts as the single source of truth for the entire application's global state. It manages the current operational mode (e.g., "health", "industrial"), configuration settings, and ensures state consistency across Streamlit reruns via `st.session_state`.
*   **View Models (`viewmodel/` directory)**: Each operational mode (Health, Industrial, Planner) and the overall `main_viewmodel.py` has a dedicated ViewModel. These classes:
    *   Expose data and commands to the UI layer.
    *   Encapsulate UI-specific logic and state, abstracting complex business rules from the View.
    *   Maintain state across Streamlit reruns by being stored within `st.session_state`.
    *   Interact with `domain/` use cases and `data/` sources to fetch and process data.
*   **Streamlit UI (`ui/` directory)**: The entire user interface is rendered by Streamlit. It directly consumes presentation-ready data from ViewModels and dispatches user actions (e.g., button clicks, text input) back to them. `st.session_state` is fundamental to Streamlit's reactive model, allowing UI elements to trigger reruns and persist state.

## Detailed Data Flow & Operational Mechanics

### 1. Health Mode: Real-time Biomechanical Analysis

*   **Input Acquisition (`data/` layer)**:
    *   The `ui/screens/monitor_screen.py` renders the health monitoring interface.
    *   `data/vision/health_camera_engine.py` (initialized and managed by `core/app_state.py`) continuously captures live video frames from the webcam. It internally uses MediaPipe for robust real-time human pose estimation and facial landmark detection.
*   **Data Processing (`viewmodel/` & `domain/` layers)**:
    *   Raw video frames and the extracted MediaPipe signals (pose, landmarks) are passed to `viewmodel/health_vm.py` via its `on_frame_update()` method.
    *   `health_vm.py` processes these signals to compute biomechanical metrics (e.g., Kinematic Entropy, Physical Variance) and generates comprehensive clinical reports (`_compile_clinical_report()` within `health_vm.py`).
*   **Output Visualization (`ui/` layer)**:
    *   `ui/widgets/health_widget.py` (rendered within `monitor_screen.py`) dynamically displays the live video feed with overlayed pose landmarks, the calculated biomechanical data, and the AI-generated clinical report.

### 2. Industrial Mode: Event Monitoring & AI Explanation

*   **Input Acquisition (`ui/` & `data/` layers)**:
    *   The `ui/screens/monitor_screen.py` presents the industrial monitoring interface.
    *   `ui/components/video_engine.py` simulates a continuous industrial video stream. This component is also responsible for detecting pre-defined safety events (e.g., unauthorized access, equipment malfunction) within the simulated feed.
*   **Data Processing (`viewmodel/` & `domain/` layers)**:
    *   Detected safety events and associated telemetry data are funneled into `viewmodel/industrial_vm.py` via its `on_frame_update()` method.
    *   Upon detecting a critical event, `industrial_vm.py` triggers `domain/usecases/industrial_explainer.py` (specifically its `explain_event()` function).
    *   `industrial_explainer.py` queries the **Gemini API** (`gemini-pro` model) with the event details to generate a concise, actionable explanation and recommended next steps.
*   **Output Visualization (`ui/` layer)**:
    *   `ui/widgets/industrial_widget.py` (rendered within `monitor_screen.py`) displays the simulated video, real-time telemetry, and prominently features the Gemini-generated safety explanations.

### 3. Planner Mode: AI-Powered Document & Code Analysis

*   **Input Acquisition (`ui/` & `utils/` layers)**:
    *   `ui/widgets/planner_widget.py` (part of `ui/screens/config_screen.py`) provides a file uploader component.
    *   Users upload various file types: `.py` (Python code), `.txt` (plain text), `.md` (Markdown), or `.docx` (Microsoft Word document).
*   **Data Processing (`viewmodel/` & `domain/` layers)**:
    *   The uploaded file's content is read by `viewmodel/planner_vm.py`'s `on_file_uploaded()` method. For `.docx` files, `utils/helpers.py`'s `extract_text_from_docx()` handles the text extraction.
    *   `planner_vm.py` then invokes `domain/usecases/explain_algorithm.py` (specifically its `explain_algorithm()` function).
    *   `explain_algorithm.py` sends the extracted file content and its detected type to the **Gemini API** (`gemini-2.5-flash` model). It prompts Gemini to return a structured JSON analysis comprising a summary, complexity, suggested improvements, use cases, and a step-by-step plan.
*   **Output Visualization (`ui/` layer)**:
    *   `ui/widgets/planner_widget.py` intelligently parses and displays the structured JSON analysis received from Gemini, breaking it down into distinct, readable sections within the Streamlit interface.

### 4. Robot Assistant Mode: Hybrid Gemini-Powered Conversational AI (Newly Upgraded)

This mode has undergone a significant upgrade, integrating Google Gemini for highly accurate Speech-to-Text (STT) and intelligent text response generation. It combines this with a fast Text-to-Speech (TTS) engine for a seamless and interactive voice assistant experience.

*   **Core Components & Responsibilities**:
    *   **`robot/gemini_audio_engine.py` (NEW)**:
        *   **Purpose**: Dedicated engine for audio recording and Gemini-powered Speech-to-Text (STT).
        *   **Mechanism**:
            *   `record_audio(duration: int = 5, sample_rate: int = 16000)`: Uses `sounddevice` to capture raw audio from the microphone for a fixed duration. The recorded audio is saved as a temporary WAV file (`gemini_voice_input.wav`) in the system's temporary directory.
            *   `transcribe_audio(audio_path: str)`: Takes the path to the recorded WAV file, securely uploads it to the **Gemini File API**, and then sends it to the `gemini-2.5-flash` model with a specific prompt to generate an accurate transcription. Remote and local temporary audio files are automatically cleaned up after transcription. Robust error handling is included for API key issues, empty audio, and API connection failures.
    *   **`domain/usecases/generate_response.py` (UPDATED)**:
        *   **Purpose**: Functions as the robot's central "brain" for generating intelligent text responses.
        *   **Mechanism**: The `generate_response()` function receives the user's query (which can be transcribed audio or typed text), the active operational `mode` (e.g., "industrial", "health"), relevant `telemetry_context` from the current ViewModel, and crucially, the **conversation history** (`history: list`). It dynamically constructs a sophisticated prompt, incorporating previous turns to maintain contextual continuity. This prompt is then sent to the **Gemini API** (`gemini-2.5-flash` model) to generate the robot's textual reply.
    *   **`robot/tts_engine.py`**:
        *   **Purpose**: Converts the Gemini-generated text responses into natural-sounding spoken audio.
        *   **Mechanism**: Utilizes `edge_tts` (Microsoft Edge's high-quality text-to-speech service) to synthesize audio, selecting a voice based on the active mode. It saves temporary MP3 files and plays them using `playsound`. A vital feature is its ability to `mute()` the `gemini_audio_engine` (from `robot/gemini_audio_engine.py`) during speech and `unmute()` it afterwards, effectively preventing the robot from "hearing itself" and avoiding feedback loops.
    *   **`ui/screens/robot_screen.py` (UPDATED)**:
        *   **Purpose**: Orchestrates the entire robot interaction experience, managing both visual and auditory cues.
        *   **Mechanism**:
            *   **Input**: Provides a prominent "🎤 RECORD (5s)" button (triggering `st.session_state.is_recording = True` upon click) and a manual text input area (`st.text_area`).
            *   **Processing Flow**: When a voice recording is initiated (e.g., via button click):
                1.  A `st.spinner("🎤 Recording for 5 seconds... Speak now.")` is displayed.
                2.  `record_audio()` from `robot/gemini_audio_engine.py` is executed, capturing user speech.
                3.  A `st.spinner("🧠 Gemini is transcribing...")` is displayed.
                4.  `transcribe_audio()` from `robot/gemini_audio_engine.py` is executed, converting speech to text via Gemini.
                5.  The transcribed text (or direct text input from `st.text_area`) is then passed to the `_process_query()` function (also within `robot_screen.py`).
                6.  `_process_query()` updates the animated robot face (`_robot_face_html`) to a "thinking" state.
                7.  `generate_response()` (from `domain/usecases/generate_response.py`) is called, integrating relevant `telemetry_context` and the updated `robot_history`.
                8.  The robot face transitions back to "idle".
                9.  The Gemini-generated textual response is streamed to the UI character-by-character (`_stream_response()` in `robot_screen.py`) for a dynamic display and simultaneously spoken aloud via `tts_engine.speak()` (from `robot/tts_engine.py`).
                10. The interaction (user query and AI response) is saved to `st.session_state.robot_history` for future contextual continuity and displayed by `_render_history()` in `robot_screen.py`.
            *   **Feedback**: Features a dynamically animated robot face (`_robot_face_html`), visual microphone button status (`_mic_button_html` - indicating READY, RECORDING, SPEAKING states), loading spinners for recording/transcription/generation, and a real-time debug log (`st.session_state.robot_debug`) for comprehensive troubleshooting and visibility into the robot's operations.

## Setup & Installation

### Prerequisites

*   **Python 3.14.2**: This project is developed and tested specifically with Python version 3.14.2. Ensure you have this version installed for optimal compatibility.
*   **Google Gemini API Key**: A valid API key is absolutely essential to interact with the Google Gemini models. Obtain yours from the official [Google AI Studio](https://aistudio.google.com/app/apikey).
*   **System Audio Configuration**: A working microphone and speaker setup. The `sounddevice` library relies on correctly configured system audio drivers (e.g., PortAudio on Linux) to function properly.

### Steps

1.  **Clone the Repository**:
    Begin by cloning the project repository to your local machine:
    ```bash
    git clone https://github.com/your-repo/sentinelx-ai.git
    cd sentinelx-ai
    ```
2.  **Create a Virtual Environment** (Highly Recommended):
    Isolating project dependencies within a virtual environment is a critical best practice to prevent conflicts with other Python projects.
    ```bash
    python -m venv venv
    # On Windows (Command Prompt):
    .\venv\Scripts\activate
    # On Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install Dependencies**:
    Once your virtual environment is active, install all required Python libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```
    *   **Note on `sounddevice`**: The `sounddevice` library requires system-level audio development libraries. If `pip install` encounters issues with `sounddevice`, you may need to install these first:
        *   **Debian/Ubuntu**: `sudo apt-get update && sudo apt-get install libportaudio2-dev`
        *   **macOS**: `brew install portaudio` (using Homebrew, `brew install portaudio` then `pip install sounddevice --user`)
4.  **Set Up Google Gemini API Key**:
    *   Create a file named `.env` in the **root directory** of your project (`sentinelx-ai/.env`).
    *   Add your Gemini API key to this file in the following format:
        ```ini
        GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
        **Crucial**: Replace `"YOUR_API_KEY_HERE"` with the actual API key you obtained from Google AI Studio. The `.env` file is explicitly listed in `.gitignore` and **must never** be committed to your version control system to prevent exposing sensitive credentials.

## How to Run the Application

Once all setup steps are successfully completed and your virtual environment is active, execute the Streamlit application from your project's root directory:

```bash
streamlit run ui/app.py
```

This command will launch the SentinelX AI application, opening it automatically in your default web browser.

## Troubleshooting & Common Issues

*   **`SyntaxError: unterminated f-string literal`**: This class of errors, encountered during initial development, was due to incorrect newline characters within f-strings. These issues have been meticulously addressed in the codebase. If similar syntax errors arise, double-check your Python environment compatibility and ensure your project files are synchronized with the latest version.
*   **`404 models/gemini-1.5-flash is not found`**: This error indicated a mismatch between the requested model name and those available via the Gemini API. The project has been updated to use the currently available and stable `gemini-2.5-flash` (for planner and STT) and `gemini-pro` (for industrial explainer) models where appropriate.
*   **Microphone Input Not Working**:
    *   **Browser Permissions**: The application attempts to request microphone access via `navigator.mediaDevices.getUserMedia()`. You *must* grant this permission when prompted by your web browser.
    *   **Operating System Permissions**: Verify your OS (Windows, macOS, Linux) privacy and security settings. Ensure that Python or the terminal application running Streamlit has explicit permission to access your microphone.
    *   **Default Audio Device**: Confirm that your operating system has a functional and correctly configured default input audio device.
    *   **`sounddevice` Backend**: As noted in Step 3, `sounddevice` often requires a backend like `PortAudio`. Follow the specific installation instructions for your OS.
*   **Gemini API Key Issues / "Error connecting to AI audio core."**:
    *   **`.env` File Check**: Double-check that `GEMINI_API_KEY` is precisely set in your `.env` file (no leading/trailing spaces, correct key format).
    *   **Internet Connectivity**: A stable internet connection is required for all Gemini API interactions.
    *   **API Key Validity**: Verify your API key is active and has not expired or reached its quota limits. Consult your Google AI Studio dashboard.
    *   **Debug Logs**: Utilize the "🛠️ LIVE SYSTEM TELEMETRY (DEBUG)" expander in the Robot mode UI to view real-time logs from the Gemini API calls for more specific error messages.

## Component Versions (Approximate)

This project is developed and tested with the following key dependency versions. Minor version updates are generally compatible, but significant version changes might require adjustments.

*   **Python**: `3.14.2`
*   **Streamlit**: `^1.x` (e.g., `1.34.0`) - Please use a recent stable version.
*   **`google-generativeai`**: `^0.x` (e.g., `0.11.0`) - Latest compatible with the current codebase.
*   **`sounddevice`**: `^0.4.x` (e.g., `0.4.7`)
*   **`scipy`**: `^1.x` (e.g., `1.13.0`)
*   **`python-dotenv`**: `^1.x` (e.g., `1.0.1`)
*   **`python-docx`**: `^0.8.x` (e.g., `0.8.11`)
*   **`edge_tts`**: `^6.x` (e.g., `6.1.10`)
*   **AI Models Used**: `gemini-2.5-flash`, `gemini-pro`

## Future Enhancements & Critical Considerations

*   **Critical: Gemini Library Migration**: The `google.generativeai` library currently used in this project is officially **deprecated**. A critical future task for long-term stability and access to new features is to migrate the entire codebase to the newer, actively maintained `google.genai` package. This will ensure compatibility with future Gemini API versions and benefit from ongoing support.
*   **Advanced STT/TTS with Multimodal Live API**: Explore Google's cutting-edge Multimodal Live API for truly real-time, end-to-end conversational experiences with ultra-low latency and advanced features like "barge-in" capabilities. This would represent another significant upgrade to the robot's voice interaction.
*   **Externalized Configuration**: Centralize more configurable parameters (e.g., Gemini model names, API endpoints, recording durations, voice preferences) into a dedicated configuration file (e.g., `config.json` or YAML) for easier management and deployment across different environments.
*   **Robust Error Handling & Fallbacks**: Implement more sophisticated error recovery mechanisms, including graceful degradation or user-friendly prompts when AI services are temporarily unavailable.
*   **Local LLM Integration**: As a complementary feature, investigate the integration of local LLMs (like Llama 3 via Ollama) for scenarios requiring offline capabilities or specific privacy constraints, offering a hybrid deployment option.