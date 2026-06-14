import google.generativeai as genai
from utils.helpers import get_gemini_api_key

def explain_event(event: str) -> str:
    """
    Uses Gemini to explain an industrial event.
    """
    prompt = f"""
    You are an industrial safety AI for SentinelX.
    An event has been detected.

    EVENT: "{event}"

    Based on this event, explain what is likely happening and what immediate action should be taken.
    Your response must be concise, professional, and no more than 2 sentences.
    """

    try:
        api_key = get_gemini_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        response = model.generate_content(prompt)
        
        return response.text.strip()

    except Exception as e:
        error_message = f"Error calling Gemini in explain_event: {e}"
        print(error_message)
        return "An alert was triggered, but I am unable to provide analysis at this time."
