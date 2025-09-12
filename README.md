# agent_scanning_hosts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**agent_scanning_hosts** is an advanced multi-agent automation framework built with [AutoGen](https://microsoft.github.io/autogen/) for scanning and analyzing network hosts. It leverages large language models (LLMs) to orchestrate cooperative and competitive agents that perform tasks such as host availability checks (ping), port scanning (using Nmap), and in-depth analysis of scan results. The system is designed for network monitoring, security auditing, and infrastructure visibility, providing structured insights into active devices and potential vulnerabilities.

This project implements a **coopetition** (cooperation + competition) model where agents collaborate on tasks while competing to produce the highest-quality analyses. It stores shared state across agents and supports customizable LLM backends, making it extensible for various environments.

## Features

- **Multi-Agent Orchestration**: DominantAgent plans tasks, ScannerAgent executes network probes, and multiple AnalyzerAgents compete to generate detailed reports.
- **Network Tools Integration**: Built-in support for ping (availability checks) and Nmap-based port scanning (TCP ports 1-1000 by default).
- **State Management**: Centralized shared state for data persistence across agents, including query, IP, ping/scan results, and analyses.
- **LLM-Driven Analysis**: Agents use prompts to reason, act, and generate JSON-formatted outputs for risks, vulnerabilities, and recommendations.
- **Modular Configuration**: Easy customization of LLM endpoints, prompts, and execution settings via a dataclass-based config.
- **Error Handling and Logging**: Comprehensive logging and exception handling for robust operation.
- **Simulation Mode**: Optional simulated port scans for testing without real network access.
- **Termination Protocol**: Agents end responses with "TERMINATE" for clean workflow control.
- **Extensibility**: Add more analyzers or tools via AutoGen's function registration.

## Architecture Overview

The system follows a step-by-step workflow orchestrated by `CoopetitionSystem`:

1. **Initialization**: Set up agents (Dominant, Scanner, Analyzers) and shared state.
2. **Ping Step**: ScannerAgent checks host availability.
3. **Scan Step**: If ping succeeds, perform port scan and store results.
4. **Analyze Step**: AnalyzerAgents (e.g., two instances) independently analyze scan data and append JSON analyses to state.
5. **Select Step**: DominantAgent evaluates analyses and selects the best one.
6. **Output**: Return the selected analysis in natural language (Russian by default).

Key Components:
- **Agents** (`agents.py`): LLM-powered agents with specialized prompts.
- **Tools** (`tools.py`): Subprocess-based ping and Nmap functions.
- **State** (`state.py`): Dictionary-based shared data store with step tracking.
- **Config** (`config.py`): Centralized settings for LLMs and prompts.
- **Orchestrator** (`orchestrator.py`): Manages agent interactions and workflow.
- **Main** (`main.py`): Entry point for running queries.

For a visual representation:

```
User Query → DominantAgent (Plan) → ScannerAgent (Ping/Scan) → AnalyzerAgents (Compete) → DominantAgent (Select) → Final Report
                  ↓
              Shared State (Data Persistence)
```

## Requirements

### Hardware/Software Prerequisites
- **Operating System**: Linux (recommended for Nmap/ping; tested on Ubuntu/Debian), macOS, or Windows (with WSL for best compatibility).
- **Python**: Version 3.8 or higher.
- **Network Tools**:
  - `ping`: Built-in on most systems.
  - `nmap`: Required for real port scanning. Install via package manager:
    - Ubuntu/Debian: `sudo apt update && sudo apt install nmap`
    - macOS: `brew install nmap`
    - Windows: Download from [Nmap.org](https://nmap.org/download.html) and add to PATH.
- **LLM Server**: A local or remote LLM endpoint (e.g., Ollama, vLLM). Default config points to a local Qwen model at `http://10.27.192.116:8080/v1`. No API key required for local setups.
- **Disk Space**: Minimal (~100MB for workspace); ensure write permissions for the `workspace/` directory.

### Python Dependencies
- `pyautogen`: Core framework for multi-agent systems.
- Standard library modules: `dataclasses`, `typing`, `pathlib`, `json`, `re`, `logging`, `subprocess` (all included in Python 3.8+).

No additional ML or heavy libraries are required, keeping the footprint lightweight.

## Installation

Follow these steps to set up and launch the project:

1. **Clone the Repository**:
   ```
   git clone https://github.com/yourusername/agent_scanning_hosts.git  # Replace with actual repo URL
   cd agent_scanning_hosts
   ```

2. **Create a Virtual Environment** (Recommended for isolation):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python Dependencies**:
   ```
   pip install pyautogen
   ```
   - This installs AutoGen and its transitive dependencies (e.g., `openai` for API compatibility).
   - Upgrade if needed: `pip install --upgrade pyautogen`.

4. **Install System Tools**:
   - Ensure `ping` and `nmap` are in your PATH (see Requirements above).
   - Verify installation:
     ```
     ping -c 1 8.8.8.8  # Should succeed
     nmap --version     # Should print version info
     ```

5. **Set Up LLM Server** (If not already running):
   - **Option 1: Local Ollama** (Recommended for development):
     - Install Ollama: Follow [Ollama docs](https://ollama.com/download).
     - Pull the model: `ollama pull qwen2:14b` (or similar; adjust config for exact model).
     - Start server: `ollama serve`.
     - Update `config.py` if the endpoint/port differs (default: `http://localhost:11434/v1` for Ollama).
   - **Option 2: Custom Endpoint**:
     - Edit `config.py`:
       ```python
       @dataclass
       class SystemConfig:
           llm_base_url: str = "http://your-llm-server:port/v1"  # e.g., "http://10.27.192.116:8080/v1"
           llm_model: str = "your-model-name"  # e.g., "Qwen3-14B-Q5_0"
           llm_api_key: str = "your-api-key"   # "sk-no-key-required" for local
           # ... other fields
       ```
     - Ensure the server supports OpenAI-compatible API (e.g., `/v1/chat/completions`).

6. **Optional: Enable Simulation Mode**:
   - In `tools.py`, replace `port_scan` calls with `simulate_port_scan` for testing without Nmap.
   - Useful for environments without network access.

7. **Verify Setup**:
   - Run a dry test: `python main.py` (it will attempt a scan on the default IP; expect logs).

## Usage

### Running the Project

1. **Basic Execution**:
   - The entry point is `main.py`, which processes a hardcoded query. To run:
     ```
     python main.py
     ```
   - Output: A final analysis report printed to console (e.g., risks and recommendations for the scanned host).

2. **Custom Queries**:
   - Edit `main.py` to change the `user_query`:
     ```python
     user_query = "просканируй порты на хосте 8.8.8.8"  # Example: Scan Google's DNS
     result = system.process_query(user_query)
     print(result)
     ```
   - Queries should include an IP address (e.g., "Scan ports on 192.168.1.1"). Defaults to "10.27.192.116" if none found.
   - Language: Prompts are in Russian; outputs will be in Russian. For English, modify prompts in `config.py`.

3. **Step-by-Step Workflow Customization**:
   - In `orchestrator.py`, modify `process_query` to add steps, agents, or custom logic.
   - Add more analyzers: Instantiate additional `create_analyzer_agent` in `_setup_agents`.
   - Register new tools: Use `register_function` in `process_query` for custom functions (e.g., vulnerability checks).

4. **Output Format**:
   - The final result is a natural language summary from the best analysis, including:
     - Host status.
     - Open ports and services.
     - Potential risks (e.g., exposed SSH on port 22).
   - Analyses are stored as JSON in state for programmatic access.

### Example Output
For query: "просканируй порты на хосте 10.27.192.116"

```
=== Финальный ответ ===
Хост 10.27.192.116 доступен. Открытые порты: 22 (SSH), 80 (HTTP). Риски: Возможный доступ к веб-серверу без аутентификации. Рекомендация: Проверить firewall.
```

### Advanced Usage
- **Batch Processing**: Loop over IPs in a script:
  ```python
  ips = ["192.168.1.1", "8.8.8.8"]
  for ip in ips:
      query = f"просканируй порты на хосте {ip}"
      print(system.process_query(query))
  ```
- **Logging**: Outputs to console (INFO level). Customize in `main.py`:
  ```python
  logging.basicConfig(level=logging.DEBUG, filename='scan.log')
  ```
- **Timeout Handling**: Scans timeout at 30s; adjust in `tools.py`.

## Configuration Options

All settings are in `config.py` (SystemConfig dataclass):
- **LLM Settings**: `llm_base_url`, `llm_model`, `llm_api_key`, `max_tokens` (default: 8192), `temperature` (0.7).
- **Prompts**: `dominant_prompt`, `scanner_prompt`, `analyzer_prompt_template` – Customize for domain-specific analysis (e.g., focus on IoT devices).
- **Code Execution**: `code_execution_config` – Set `use_docker: True` for isolated execution (requires Docker).
- **Termination**: `termination_msg` – Change from "TERMINATE" if needed.

Reload config after changes without restarting.

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| "Host недоступен" | Firewall or offline host | Verify IP; test with manual `ping`. |
| "nmap not found" | Missing Nmap | Install via package manager; ensure in PATH. |
| LLM connection error | Server down/offline | Start LLM server; check `llm_base_url`. |
| JSON parse error | Invalid agent output | Increase `max_tokens`; debug prompts. |
| Timeout during scan | Slow network/large range | Reduce port range in `tools.py` (e.g., `-p 1-100`). |
| No analyses generated | Missing scan_result | Ensure ping succeeds; check state logs. |
| ImportError: pyautogen | Dependency missing | Run `pip install pyautogen`. |
| Permission denied (workspace) | No write access | Run as user with permissions or change `work_dir`. |

- **Debug Mode**: Set `logging.basicConfig(level=logging.DEBUG)` in `main.py`.
- **Test Tools Independently**:
  ```python
  from tools import ping_host, port_scan
  print(ping_host("8.8.8.8"))
  print(port_scan("8.8.8.8"))
  ```
- If using Docker for LLM: Ensure port exposure (e.g., `-p 8080:8080`).

## Contributing

Contributions are welcome! To get started:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/amazing-feature`.
3. Commit changes: `git commit -m 'Add amazing feature'`.
4. Push: `git push origin feature/amazing-feature`.
5. Open a Pull Request.

### Guidelines
- Follow PEP 8 for code style (use `black` formatter).
- Add tests for new tools/agents (e.g., unit tests in a `tests/` dir).
- Update README for new features.
- Document prompt changes in `config.py` comments.
- Ensure compatibility with Python 3.8+ and no breaking changes to workflow.

Report issues via GitHub Issues, including logs and reproduction steps.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [AutoGen](https://microsoft.github.io/autogen/) by Microsoft.
- Tools inspired by standard network utilities (ping, Nmap).
- Prompts optimized for Russian-language outputs; credits to initial author Artem Liuboshenko (2025).

For support or questions, open an issue or contact the maintainer. Happy scanning! 🚀