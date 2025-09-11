import logging
from pathlib import Path
import json
import re
from config import SystemConfig
from agents import create_dominant_agent, create_scanner_agent, create_analyzer_agent
from state import SystemState
from autogen import UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor

logger = logging.getLogger(__name__)

class CoopetitionSystem:
    def __init__(self, config: SystemConfig):
        self.config = config
        self.state = SystemState()
        self.code_executor = self._setup_code_executor()
        self.config.code_execution_config = {"executor": self.code_executor}
        self._setup_agents()

    def _setup_code_executor(self):
        work_dir = Path("workspace")
        work_dir.mkdir(exist_ok=True)
        return LocalCommandLineCodeExecutor(work_dir=str(work_dir), timeout=60)

    def _setup_agents(self):
        self.dominant = create_dominant_agent(self.config, self.state)
        self.scanner = create_scanner_agent(self.config, self.state)
        self.analyzer1 = create_analyzer_agent(1, self.config, self.state)
        self.analyzer2 = create_analyzer_agent(2, self.config, self.state)

    def process_query(self, user_query: str) -> str:
        try:
            self.state.update("query", user_query)
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', user_query)
            ip = ip_match.group(1) if ip_match else "10.27.192.116"
            self.state.update("ip", ip)

            user_proxy = UserProxyAgent(
                name="UserProxy",
                human_input_mode="NEVER",
                code_execution_config=self.config.code_execution_config,
                is_termination_msg=lambda x: isinstance(x, dict) and "content" in x and isinstance(x["content"], str) and x["content"].rstrip().endswith(self.config.termination_msg),
            )

            # Регистрируем функции только для ScannerAgent
            from autogen import register_function
            from tools import ping_host, port_scan
            for func, desc in [(ping_host, ping_host.__doc__), (port_scan, port_scan.__doc__)]:
                register_function(
                    func,
                    caller=self.scanner,
                    executor=user_proxy,
                    name=func.__name__,
                    description=desc
                )

            steps = ["ping", "scan", "analyze", "select"]
            for step in steps:
                self.state.advance_step(step)
                logger.info(f"Current step: {step}, State: {self.state.data}")

                last_message = None
                if step in ["ping", "scan"]:
                    user_proxy.initiate_chat(self.scanner, message=f"Perform {step} on IP {self.state.get('ip')}. Update state.")
                    last_message = self.scanner.last_message()
                    if isinstance(last_message, dict) and "tool_calls" in last_message:
                        # Tool call initiated; wait for result
                        tool_response = user_proxy.last_message()["content"]
                        try:
                            json_str = tool_response.split("TERMINATE")[0].strip()
                            result_json = json.loads(json_str)
                            if step == "ping":
                                self.state.update("ping_result", result_json.get("ping_result", "No result"))
                            elif step == "scan":
                                self.state.update("scan_result", result_json.get("scan_result", "No result"))
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON from Scanner: {tool_response}")
                            raise ValueError(f"Invalid JSON from Scanner in step {step}")
                    else:
                        try:
                            json_str = last_message["content"].split("TERMINATE")[0].strip()
                            result_json = json.loads(json_str)
                            if step == "ping":
                                self.state.update("ping_result", result_json.get("ping_result", "No result"))
                            elif step == "scan":
                                self.state.update("scan_result", result_json.get("scan_result", "No result"))
                        except (json.JSONDecodeError, KeyError):
                            logger.error(f"Failed to parse JSON from Scanner: {last_message}")
                            raise ValueError(f"Invalid JSON from Scanner in step {step}")
                elif step == "analyze":
                    if not self.state.get("scan_result"):
                        raise ValueError("Scan result is missing. Cannot analyze.")
                    self.state.data["analyses"] = []
                    for analyzer in [self.analyzer1, self.analyzer2]:
                        user_proxy.initiate_chat(analyzer, message=f"Analyze data from state: {self.state.get('scan_result')}")
                        analysis_content = analyzer.last_message()["content"]
                        analysis = analysis_content.split("TERMINATE")[0].strip()
                        self.state.data["analyses"].append(analysis)
                    last_message = "Analyses collected"
                elif step == "select":
                    user_proxy.initiate_chat(self.dominant, message=f"Select best analysis from state.analyses: {self.state.data['analyses']}")
                    select_content = self.dominant.last_message()["content"]
                    last_message = select_content.split("TERMINATE")[0].strip()
                    self.state.update("best_analysis", last_message)

                if last_message and isinstance(last_message, str) and "error" in last_message.lower():
                    raise ValueError(f"Error in step {step}: {last_message}")

            return self.state.get("best_analysis") or "No result"
        except Exception as e:
            logger.error(f"Error: {e}")
            return str(e)