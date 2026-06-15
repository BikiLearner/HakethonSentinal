import logging
import yaml
logger = logging.getLogger(__name__)

def load_config(content: str) -> dict:
    try:
        data = yaml.safe_load(content)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print("YAML Parse Error:", e)
        return {}