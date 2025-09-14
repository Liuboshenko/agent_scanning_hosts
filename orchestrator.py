import logging
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from autogen import UserProxyAgent, AssistantAgent, register_function
from autogen.coding import LocalCommandLineCodeExecutor
from config import SystemConfig
from agents import create_dominant_agent, create_scanner_agent, create_analyzer_agent
from state import SystemState
from tools import ping_host, port_scan

logger = logging.getLogger(__name__)

class CoopetitionSystem:
    """Manages a cooperative-competitive system for processing queries with multiple agents."""
    
    DEFAULT_IP = "10.27.192.116"
    STEPS = ["ping", "scan", "analyze", "select"]

    def __init__(self, config: SystemConfig):
        """Initializes the system with configuration, state, and agents.

        Args:
            config (SystemConfig): Configuration object containing system settings.
        """
        self.config = config
        self.state = SystemState()
        self.code_executor = self._setup_code_executor()
        self.config.code_execution_config = {"executor": self.code_executor}
        self.dominant: AssistantAgent = None
        self.scanner: AssistantAgent = None
        self.analyzer1: AssistantAgent = None
        self.analyzer2: AssistantAgent = None
        self._setup_agents()

    def _setup_code_executor(self) -> LocalCommandLineCodeExecutor:
        """Sets up the code executor with a workspace directory.

        Returns:
            LocalCommandLineCodeExecutor: Configured code executor.
        """
        work_dir = Path("workspace")
        work_dir.mkdir(exist_ok=True)
        return LocalCommandLineCodeExecutor(work_dir=str(work_dir), timeout=60)

    def _setup_agents(self) -> None:
        """Initializes all agents using the provided configuration and state."""
        self.dominant = create_dominant_agent(self.config, self.state)
        self.scanner = create_scanner_agent(self.config, self.state)
        self.analyzer1 = create_analyzer_agent(1, self.config, self.state)
        self.analyzer2 = create_analyzer_agent(2, self.config, self.state)

    def _create_user_proxy(self) -> UserProxyAgent:
        """Creates a UserProxyAgent with the configured settings.

        Returns:
            UserProxyAgent: Configured user proxy agent.
        """
        return UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            code_execution_config=self.config.code_execution_config,
            is_termination_msg=lambda x: isinstance(x, dict) and "content" in x and isinstance(x["content"], str) and x["content"].rstrip().endswith(self.config.termination_msg),
        )

    def _register_tools(self, user_proxy: UserProxyAgent) -> None:
        """Registers tool functions for the ScannerAgent.

        Args:
            user_proxy (UserProxyAgent): The user proxy agent to execute tool calls.
        """
        for func, desc in [(ping_host, ping_host.__doc__), (port_scan, port_scan.__doc__)]:
            register_function(
                func,
                caller=self.scanner,
                executor=user_proxy,
                name=func.__name__,
                description=desc
            )

    def _parse_json_response(self, response: Dict, step: str, key: str) -> Dict:
        """Parses JSON from the agent's response content.

        Args:
            response (Dict): The agent's response dictionary.
            step (str): The current processing step.
            key (str): The key to extract from the parsed JSON.

        Returns:
            Dict: The parsed JSON data.

        Raises:
            ValueError: If JSON parsing fails or the response is invalid.
        """
        try:
            content = response["content"].split("TERMINATE")[0].strip()
            return json.loads(content)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse JSON from Scanner in step {step}: {response}")
            raise ValueError(f"Invalid JSON from Scanner in step {step}: {str(e)}")

    def _process_ping(self, user_proxy: UserProxyAgent, ip: str) -> None:
        """Processes the ping step.

        Args:
            user_proxy (UserProxyAgent): The user proxy agent.
            ip (str): The IP address to ping.
        """
        user_proxy.initiate_chat(self.scanner, message=f"Perform ping on IP {ip}. Update state.")
        last_message = self.scanner.last_message()
        if isinstance(last_message, dict) and "tool_calls" in last_message:
            tool_response = user_proxy.last_message()["content"]
            result_json = self._parse_json_response({"content": tool_response}, "ping", "ping_result")
        else:
            result_json = self._parse_json_response(last_message, "ping", "ping_result")
        self.state.update("ping_result", result_json.get("ping_result", "No result"))

    def _process_scan(self, user_proxy: UserProxyAgent, ip: str) -> None:
        """Processes the scan step.

        Args:
            user_proxy (UserProxyAgent): The user proxy agent.
            ip (str): The IP address to scan.
        """
        user_proxy.initiate_chat(self.scanner, message=f"Perform scan on IP {ip}. Update state.")
        last_message = self.scanner.last_message()
        if isinstance(last_message, dict) and "tool_calls" in last_message:
            tool_response = user_proxy.last_message()["content"]
            result_json = self._parse_json_response({"content": tool_response}, "scan", "scan_result")
        else:
            result_json = self._parse_json_response(last_message, "scan", "scan_result")
        self.state.update("scan_result", result_json.get("scan_result", "No result"))

    def _process_analyze(self, user_proxy: UserProxyAgent) -> None:
        """Processes the analyze step.

        Args:
            user_proxy (UserProxyAgent): The user proxy agent.

        Raises:
            ValueError: If scan result is missing.
        """
        if not self.state.get("scan_result"):
            raise ValueError("Scan result is missing. Cannot analyze.")
        self.state.data["analyses"] = []
        for analyzer in [self.analyzer1, self.analyzer2]:
            user_proxy.initiate_chat(analyzer, message=f"Analyze data from state: {self.state.get('scan_result')}")
            analysis_content = analyzer.last_message()["content"]
            analysis = analysis_content.split("TERMINATE")[0].strip()
            self.state.data["analyses"].append(analysis)

    def _process_select(self, user_proxy: UserProxyAgent) -> None:
        """Processes the select step.

        Args:
            user_proxy (UserProxyAgent): The user proxy agent.
        """
        user_proxy.initiate_chat(self.dominant, message=f"Select best analysis from state.analyses: {self.state.data['analyses']}")
        select_content = self.dominant.last_message()["content"]
        best_analysis = select_content.split("TERMINATE")[0].strip()
        self.state.update("best_analysis", best_analysis)

    def process_query(self, user_query: str) -> str:
        """Processes a user query through multiple steps (ping, scan, analyze, select).

        Args:
            user_query (str): The user query containing an IP address or other instructions.

        Returns:
            str: The best analysis result or an error message.
        """
        try:
            self.state.update("query", user_query)
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', user_query)
            ip = ip_match.group(1) if ip_match else self.DEFAULT_IP
            self.state.update("ip", ip)

            user_proxy = self._create_user_proxy()
            self._register_tools(user_proxy)

            for step in self.STEPS:
                self.state.advance_step(step)
                logger.info(f"Current step: {step}, State: {self.state.data}")

                if step == "ping":
                    self._process_ping(user_proxy, ip)
                elif step == "scan":
                    self._process_scan(user_proxy, ip)
                elif step == "analyze":
                    self._process_analyze(user_proxy)
                elif step == "select":
                    self._process_select(user_proxy)

                last_message = self.state.get("best_analysis") or self.state.get("analyses") or self.state.get("scan_result") or self.state.get("ping_result")
                if last_message and isinstance(last_message, str) and "error" in last_message.lower():
                    raise ValueError(f"Error in step {step}: {last_message}")

            return self.state.get("best_analysis") or "No result"
        except Exception as e:
            logger.error(f"Error: {e}")
            return str(e)