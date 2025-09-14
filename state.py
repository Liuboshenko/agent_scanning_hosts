from typing import Dict, Any, Optional
from enum import Enum, auto

class StateStep(Enum):
    """Enum for valid system state steps."""
    INIT = auto()
    PING = auto()
    SCAN = auto()
    ANALYZE = auto()
    SELECT = auto()
    DONE = auto()

class SystemState:
    """Manages shared state for data exchange between agents."""
    
    # Valid state keys
    VALID_KEYS = {"query", "ip", "ping_result", "scan_result", "analyses", "best_analysis"}

    def __init__(self):
        """Initializes the system state with default values and initial step."""
        self.data: Dict[str, Any] = {
            "query": None,
            "ip": None,
            "ping_result": None,
            "scan_result": None,
            "analyses": [],  # List of analyses from analyzer agents
            "best_analysis": None
        }
        self.current_step: StateStep = StateStep.INIT

    def update(self, key: str, value: Any) -> None:
        """Updates the state with a key-value pair.

        Args:
            key (str): The key to update in the state data.
            value (Any): The value to associate with the key.

        Raises:
            ValueError: If the key is not a valid state key.
        """
        if key not in self.VALID_KEYS:
            raise ValueError(f"Invalid state key: {key}. Must be one of {self.VALID_KEYS}")
        self.data[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Retrieves a value from the state by key.

        Args:
            key (str): The key to retrieve from the state data.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key does not exist.
        
        Raises:
            ValueError: If the key is not a valid state key.
        """
        if key not in self.VALID_KEYS:
            raise ValueError(f"Invalid state key: {key}. Must be one of {self.VALID_KEYS}")
        return self.data.get(key)

    def advance_step(self, next_step: str) -> None:
        """Advances the current step to the specified step.

        Args:
            next_step (str): The name of the next step (e.g., 'ping', 'scan', 'analyze', 'select', 'done').

        Raises:
            ValueError: If the specified step is invalid.
        """
        try:
            self.current_step = StateStep[next_step.upper()]
        except KeyError:
            raise ValueError(f"Invalid step: {next_step}. Must be one of {[s.name.lower() for s in StateStep]}")