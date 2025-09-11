from typing import Dict, Any

class SystemState:
    """Shared state для хранения данных между агентами."""
    def __init__(self):
        self.data: Dict[str, Any] = {
            "query": None,
            "ip": None,
            "ping_result": None,
            "scan_result": None,
            "analyses": [],  # Список анализов от анализаторов
            "best_analysis": None
        }
        self.current_step: str = "init"  # Возможные: init, ping, scan, analyze, select, done

    def update(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str) -> Any:
        return self.data.get(key)

    def advance_step(self, next_step: str):
        self.current_step = next_step