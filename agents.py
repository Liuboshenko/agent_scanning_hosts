import autogen
from config import SystemConfig
from tools import ping_host, port_scan
from state import SystemState
from typing import Dict

def get_llm_config(config: SystemConfig) -> Dict:
    """Вспомогательная функция для llm_config."""
    return {
        "config_list": [{
            "model": config.llm_model,
            "base_url": config.llm_base_url,
            "api_key": config.llm_api_key,
            "api_type": "openai",
            "price": [0, 0]  # Подавление предупреждения
        }],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "cache_seed": config.cache_seed,
    }

def create_dominant_agent(config: SystemConfig, state: SystemState) -> autogen.AssistantAgent:
    return autogen.AssistantAgent(
        name="DominantAgent",
        system_message=config.dominant_prompt,
        llm_config=get_llm_config(config),
        code_execution_config=config.code_execution_config,
    )

def create_scanner_agent(config: SystemConfig, state: SystemState) -> autogen.AssistantAgent:
    return autogen.AssistantAgent(
        name="ScannerAgent",
        system_message=config.scanner_prompt,
        llm_config=get_llm_config(config),
        code_execution_config=config.code_execution_config,
    )

def create_analyzer_agent(analyzer_id: int, config: SystemConfig, state: SystemState) -> autogen.AssistantAgent:
    prompt = config.analyzer_prompt_template.format(id=analyzer_id)
    return autogen.AssistantAgent(
        name=f"Analyzer{analyzer_id}Agent",
        system_message=prompt,
        llm_config=get_llm_config(config),
        code_execution_config=config.code_execution_config,
    )