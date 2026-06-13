from typing import Any, Dict

class AppState:
    """
    Centralized application state management for SentinelX AI.
    Holds the current operational mode and active configuration parameters.
    """
    def __init__(self):
        self._mode: str = "planner"  # Safe default fallback
        self._config: Dict[str, Any] = {}
        
    @property
    def mode(self) -> str:
        """Returns the current operational mode."""
        return self._mode
        
    @property
    def config(self) -> Dict[str, Any]:
        """Returns a copy of the config to prevent unintended external mutations."""
        return self._config.copy()
        
    def update_state(self, new_mode: str, new_config: Dict[str, Any]) -> None:
        """
        Updates the global state. Called after a document is successfully parsed.
        """
        self._mode = new_mode
        self._config = new_config
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieves a configuration parameter.
        
        Args:
            key: The configuration key to look up (case-insensitive).
            default: The value to return if the key is not found.
            
        Returns:
            The dynamically typed configuration value, or the default.
        """
        return self._config.get(key.lower(), default)

    def is_configured(self) -> bool:
        """Helper to check if a configuration document has been loaded."""
        return bool(self._config)