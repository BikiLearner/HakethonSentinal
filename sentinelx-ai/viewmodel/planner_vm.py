from domain.usecases.explain_algorithm import explain_algorithm
import time

class PlannerViewModel:
    def __init__(self):
        self.input_content = ""
        self.output_content = ""
        self.current_config = {}

    def on_file_uploaded(self, content):
        self.input_content = content

        # 🔥 Fake AI thinking
        time.sleep(1.2)

        # ✅ Call domain logic
        self.output_content = explain_algorithm(content)

    def load_config(self, config_data):
        self.current_config = config_data
