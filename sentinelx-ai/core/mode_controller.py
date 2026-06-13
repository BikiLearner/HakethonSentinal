import logging

logger = logging.getLogger(__name__)

# Define allowed system modes to prevent rogue configs from breaking routing
VALID_MODES = {"industrial", "health", "planner"}
DEFAULT_MODE = "planner"

def detect_mode_from_config(config_dict: dict) -> str:
    """
    Determines the system mode from the parsed configuration dictionary.
    Falls back to a default mode if missing or invalid.
    """
    mode = config_dict.get('mode')
    
    if not mode:
        logger.warning(f"No mode specified in config. Defaulting to '{DEFAULT_MODE}'.")
        return DEFAULT_MODE
        
    # Ensure string comparison works cleanly
    mode = str(mode).lower()
    
    if mode not in VALID_MODES:
        logger.error(f"Invalid mode detected: '{mode}'. Defaulting to '{DEFAULT_MODE}'.")
        return DEFAULT_MODE
        
    return mode