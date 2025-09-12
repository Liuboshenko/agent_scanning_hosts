from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class SystemConfig:
    llm_base_url: str = "http://some_ip_api_llm:8080/v1"
    llm_model: str = "Qwen3-14B-Q5_0"
    llm_api_key: str = "sk-no-key-required"
    max_tokens: int = 8192 #2^13
    temperature: float = 0.7
    cache_seed: Optional[int] = None
    code_execution_config: Dict[str, Any] = field(default_factory=lambda: {"use_docker": False})  # Default; обновляется в orchestrator

    dominant_prompt: str = """
    Вы - DominantAgent. Планируйте по шагам: [REASON] рассуждение, [ACT] действие.
    Используйте state для хранения данных. Всегда проверяйте доступность хоста перед сканированием.
    Делегируйте: Scanner для ping/scan, Analyzers для анализа. Выберите лучший анализ.
    После завершения задачи верните результат на русском языке и завершите ответ словом TERMINATE.
    """

    scanner_prompt: str = """
    Вы - ScannerAgent. [REASON] о задаче, [ACT] вызов инструментов (ping_host, port_scan).
    Выполните инструмент, дождитесь результата, затем верните JSON в формате {"ping_result": "результат"} или {"scan_result": "результат"}.
    Завершите ответ словом TERMINATE.
    """

    analyzer_prompt_template: str = """
    Вы - Analyzer-{id}. Анализируйте данные из state. [REASON] о рисках, [ACT] генерируйте JSON анализ.
    Конкурируйте: будьте глубже и профессиональнее других.
    После генерации JSON завершите ответ словом TERMINATE.
    """

    termination_msg: str = "TERMINATE"