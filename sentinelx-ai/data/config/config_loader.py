import logging

logger = logging.getLogger(__name__)

def load_config(content: str) -> dict:
    """
    Parses a plain text configuration string into a structured dictionary.
    Expects 'key: value' format per line.
    """
    config_dict = {}
    if not content:
        return config_dict

    for line_number, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        
        # Ignore empty lines and comments (supports # or //)
        if not line or line.startswith(('#', '//')):
            continue
            
        if ':' not in line:
            logger.warning(f"Skipping invalid config line {line_number}: '{line}'")
            continue
            
        # Split only on the first colon to allow colons in the values
        key, value = line.split(':', 1)
        key = key.strip().lower()
        value = value.strip()
        
        # Apply basic type inference for ViewModel compatibility
        config_dict[key] = _infer_type(value)
        
    return config_dict

def _infer_type(value: str):
    """Helper to cast string values to appropriate Python types."""
    val_lower = value.lower()
    
    if val_lower in ('true', 'yes', 'enabled', 'on'):
        return True
    if val_lower in ('false', 'no', 'disabled', 'off'):
        return False
        
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value  # Return as standard string if it's not a number