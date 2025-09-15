from dataclasses import dataclass, field
from typing import Optional, Dict, Any

# Default configuration values
DEFAULT_LLM_BASE_URL = "http://10.27.192.116:8080/v1"
DEFAULT_LLM_MODEL = "Qwen3-14B-Q5_0"
DEFAULT_LLM_API_KEY = "sk-no-key-required"
DEFAULT_MAX_TOKENS = 8192  # 2^13
DEFAULT_TEMPERATURE = 0.7
DEFAULT_CACHE_SEED = None
DEFAULT_CODE_EXECUTION_CONFIG = {"use_docker": False}
TERMINATION_MSG = "TERMINATE"

# Prompt templates
DOMINANT_PROMPT = """
Вы - DominantAgent. Планируйте по шагам: [REASON] рассуждение, [ACT] действие.
Используйте state для хранения данных. Всегда проверяйте доступность хоста перед сканированием.
Делегируйте: Scanner для ping/scan, Analyzers для анализа. Выберите лучший анализ.
После завершения задачи верните результат на русском языке и завершите ответ словом TERMINATE.
"""

SCANNER_PROMPT = """
Вы - ScannerAgent. [REASON] о задаче, [ACT] вызов инструментов (ping_host, port_scan).
Выполните инструмент, дождитесь результата, затем верните JSON в формате {"ping_result": "результат"} или {"scan_result": "результат"}.
Завершите ответ словом TERMINATE.
"""

ANALYZER_PROMPT_TEMPLATE = """
Вы - Analyzer-{id}. Анализируйте данные из state. [REASON] о рисках, [ACT] генерируйте JSON анализ.
Конкурируйте: будьте глубже и профессиональнее других.
После генерации JSON завершите ответ словом TERMINATE.
"""

@dataclass
class SystemConfig:
    """Configuration class for the CoopetitionSystem, holding LLM and agent settings."""
    
    llm_base_url: str = field(default=DEFAULT_LLM_BASE_URL)
    llm_model: str = field(default=DEFAULT_LLM_MODEL)
    llm_api_key: str = field(default=DEFAULT_LLM_API_KEY)
    max_tokens: int = field(default=DEFAULT_MAX_TOKENS)
    temperature: float = field(default=DEFAULT_TEMPERATURE)
    cache_seed: Optional[int] = field(default=DEFAULT_CACHE_SEED)
    code_execution_config: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CODE_EXECUTION_CONFIG)
    dominant_prompt: str = field(default=DOMINANT_PROMPT)
    scanner_prompt: str = field(default=SCANNER_PROMPT)
    analyzer_prompt_template: str = field(default=ANALYZER_PROMPT_TEMPLATE)
    termination_msg: str = field(default=TERMINATION_MSG)

    def __post_init__(self):
        """Validates configuration fields after initialization.

        Raises:
            ValueError: If max_tokens or temperature are out of valid ranges.
        """
        if not (0 < self.max_tokens <= 16384):
            raise ValueError(f"max_tokens must be between 1 and 16384, got {self.max_tokens}")
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError(f"temperature must be between 0.0 and 2.0, got {self.temperature}")
        if not self.llm_base_url.startswith("http"):
            raise ValueError(f"llm_base_url must be a valid URL, got {self.llm_base_url}")