import google.generativeai as genai
import json
from typing import Dict, Any

def get_system_prompt(file_type: str) -> str:
    """Generates a tailored system prompt based on the file type."""

    common_instructions = """
    You are an expert software architect and AI engineer. Your task is to analyze the provided content and return a structured JSON object.
    The JSON object must have the following structure:
    {
      "summary": "A short, concise explanation of the content's purpose and functionality.",
      "complexity": "For code, provide the estimated time and space complexity (e.g., 'O(n)', 'O(n log n)'). For text, describe the conceptual complexity.",
      "improvements": ["Suggest 2-3 concrete, actionable improvements. For code, focus on performance, readability, or best practices. For text, suggest improvements in clarity, structure, or content."],
      "use_case": "Describe a real-world use case or application for this content.",
      "step_by_step": ["Provide a step-by-step breakdown of the logic, algorithm, or main points of the text. Keep it high-level."]
    }

    Do NOT include any markdown formatting (e.g., ```json) or any other text outside of the JSON object itself.
    """

    if file_type in ['.py']:
        return common_instructions + "\nThe content is a Python code file. Analyze its structure, logic, and potential for optimization."
    elif file_type in ['.txt', '.md']:
        return common_instructions + "\nThe content is a text or markdown file. Summarize its key points, identify the main theme, and suggest improvements."
    elif file_type in ['.doc', '.docx']:
        return common_instructions + "\nThe content is a document. Extract the core message, analyze its structure, and provide insights."
    else:
        return common_instructions + "\nThe content is a generic file. Provide a general analysis based on the text provided."


def explain_algorithm(content: str, file_type: str) -> Dict[str, Any]:
    """
    Analyzes content using the Gemini API and returns a structured JSON explanation.

    Args:
        content: The content of the file to analyze.
        file_type: The extension of the file (e.g., '.py', '.txt').

    Returns:
        A dictionary containing the structured analysis from the AI.
    
    Raises:
        ValueError: If the API response is not valid JSON.
        Exception: For any other API or processing errors.
    """
    try:
        api_key = get_gemini_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
            
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = get_system_prompt(file_type)
        
        full_prompt = f"{system_prompt}\n\n--- CONTENT ---\n{content}"

        response = model.generate_content(full_prompt)

        # Clean the response to ensure it's valid JSON
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        # Parse the JSON response
        return json.loads(cleaned_response)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from API response: {e}")
        print(f"Raw response was: {response.text}")
        raise ValueError(f"The AI returned an invalid response. Please try again. Raw output: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred in explain_algorithm: {e}")
        # Re-raise the exception to be handled by the ViewModel
        raise e

# Helper function to get the API key - assumed to be in a helper file
# This is here for completeness if you run this file standalone
def get_gemini_api_key():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")

