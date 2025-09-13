import autogen
from config import SystemConfig
from tools import ping_host, port_scan
from state import SystemState
from typing import Dict

def get_llm_config(config: SystemConfig) -> Dict:
    """Returns the LLM configuration dictionary based on the provided SystemConfig.

    Args:
        config (SystemConfig): Configuration object containing LLM settings.

    Returns:
        Dict: Configuration dictionary for the LLM.
    """
    return {
        "config_list": [{
            "model": config.llm_model,
            "base_url": config.llm_base_url,
            "api_key": config.llm_api_key,
            "api_type": "openai",
            "price": [0, 0]  # Suppress warning
        }],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "cache_seed": config.cache_seed,
    }

def create_agent(
    name: str,
    system_message: str,
    config: SystemConfig,
    state: SystemState
) -> autogen.AssistantAgent:
    """Creates an AssistantAgent with the specified name and system message.

    Args:
        name (str): Name of the agent.
        system_message (str): System message or prompt for the agent.
        config (SystemConfig): Configuration object containing LLM and execution settings.
        state (SystemState): System state object (currently unused but kept for compatibility).

    Returns:
        autogen.AssistantAgent: Configured AssistantAgent instance.
    """
    return autogen.AssistantAgent(
        name=name,
        system_message=system_message,
        llm_config=get_llm_config(config),
        code_execution_config=config.code_execution_config,
    )

def create_dominant_agent(config: SystemConfig, state: SystemState) -> autogen.AssistantAgent:
    """Creates the DominantAgent.

    Args:
        config (SystemConfig): Configuration object.
        state (SystemState): System state object.

    Returns:
        autogen.AssistantAgent: Configured DominantAgent instance.
    """
    return create_agent("DominantAgent", config.dominant_prompt, config, state)

def create_scanner_agent(config: SystemConfig, state: SystemState) -> autogen.AssistantAgent:
    """Creates the ScannerAgent.

    Args:
        config (SystemConfig): Configuration object.
        state (SystemState): System state object.

    Returns:
        autogen.AssistantAgent: Configured ScannerAgent instance.
    """
    return create_agent("ScannerAgent", config.scanner_prompt, config, state)

def create_analyzer_agent(analyzer_id: int, config: SystemConfig, state: SystemState) -> autogen.AssistantAgent:
    """Creates an AnalyzerAgent with a formatted prompt based on the analyzer ID.

    Args:
        analyzer_id (int): Unique identifier for the analyzer agent.
        config (SystemConfig): Configuration object.
        state (SystemState): System state object.

    Returns:
        autogen.AssistantAgent: Configured AnalyzerAgent instance.
    """
    prompt = config.analyzer_prompt_template.format(id=analyzer_id)
    return create_agent(f"Analyzer{analyzer_id}Agent", prompt, config, state)