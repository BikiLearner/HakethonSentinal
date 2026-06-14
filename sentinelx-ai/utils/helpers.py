import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from typing import Dict, Any
import docx

def get_gemini_api_key():
    """
    Loads the Gemini API key from the .env file.
    """
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")

def extract_text_from_docx(file) -> str:
    """
    Extracts text content from a .docx file.
    """
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading docx file: {e}")
        return ""
