import requests

def explain_event(event: str):
    prompt = f"""
    You are an industrial safety AI.

    Event detected: {event}

    Explain what is happening and what action should be taken.
    Keep it short and professional.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",  # Ollama
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]