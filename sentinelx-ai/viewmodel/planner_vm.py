from domain.usecases.explain_algorithm import explain_algorithm
from utils.helpers import extract_text_from_docx
import os

class PlannerViewModel:
    def __init__(self):
        self.input_content = ""
        self.output_content = None  # Will store the structured JSON
        self.is_loading = False
        self.error_message = None
        self.current_config = {}

    def on_file_uploaded(self, uploaded_file):
        """
        Handles the file upload, triggers AI analysis, and manages state.
        """
        self.is_loading = True
        self.error_message = None
        self.output_content = None
        
        try:
            # 1. Get file content and type
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension in ['.doc', '.docx']:
                content = extract_text_from_docx(uploaded_file)
            else:
                content = uploaded_file.read().decode("utf-8")
            
            self.input_content = content
            
            if not content.strip():
                self.error_message = "The uploaded file is empty or could not be read."
                self.is_loading = False
                return

            # 2. Call domain logic (Gemini API)
            ai_response = explain_algorithm(content, file_extension)

            # 3. Process and store the structured response
            self.output_content = {
                "summary": ai_response.get("summary", "No summary provided."),
                "complexity": ai_response.get("complexity", "Not applicable."),
                "improvements": ai_response.get("improvements", []),
                "use_case": ai_response.get("use_case", "No use case provided."),
                "step_by_step": ai_response.get("step_by_step", [])
            }

        except Exception as e:
            # Handle potential errors from the use case (API errors, JSON parsing, etc.)
            self.error_message = f"An error occurred: {str(e)}"
            self.input_content = "" # Clear input on error
        
        finally:
            self.is_loading = False

    def load_config(self, config_data):
        self.current_config = config_data

    def clear_all(self):
        self.input_content = ""
        self.output_content = None
        self.is_loading = False
        self.error_message = None

