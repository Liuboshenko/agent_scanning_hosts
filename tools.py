import logging
import subprocess
from typing import List, Optional

logger = logging.getLogger(__name__)

# Constants for subprocess commands
PING_COMMAND = ['ping', '-c', '1', '-W', '2']
NMAP_COMMAND = ['nmap', '-sT', '-p', '1-1000']
TIMEOUT_SECONDS = 30

def _run_subprocess(command: List[str], host: str) -> subprocess.CompletedProcess:
    """Runs a subprocess command with the specified host.

    Args:
        command (List[str]): The command and its arguments to execute.
        host (str): The target host for the command.

    Returns:
        subprocess.CompletedProcess: The result of the subprocess execution.

    Raises:
        subprocess.SubprocessError: If the subprocess execution fails.
    """
    try:
        return subprocess.run(
            command + [host],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )
    except subprocess.SubprocessError as e:
        logger.error(f"Subprocess error for command {command} on host {host}: {str(e)}")
        raise

def ping_host(host: str) -> str:
    """Checks the availability of a host using the ping command.

    Args:
        host (str): The IP address or hostname to ping.

    Returns:
        str: A message indicating whether the host is reachable or not, or an error message.
    """
    try:
        result = _run_subprocess(PING_COMMAND, host)
        if result.returncode == 0:
            logger.info(f"Host {host} is reachable.")
            return f"Host {host} is reachable."
        logger.warning(f"Host {host} is unreachable.")
        return f"Host {host} is unreachable: {result.stderr}"
    except subprocess.SubprocessError as e:
        logger.error(f"Ping error for host {host}: {str(e)}")
        return f"Ping error: {str(e)}"

def port_scan(host: str) -> str:
    """Scans ports on a host using nmap.

    Args:
        host (str): The IP address or hostname to scan.

    Returns:
        str: The nmap scan output or an error message if the host is unreachable or scanning fails.
    """
    ping_result = ping_host(host)
    if "unreachable" in ping_result.lower():
        logger.warning(f"Port scan canceled for {host}: host is unreachable.")
        return "Host unreachable, scan canceled."
    
    try:
        result = _run_subprocess(NMAP_COMMAND, host)
        logger.info(f"Port scan result for {host}: {result.stdout}")
        return result.stdout
    except subprocess.SubprocessError as e:
        logger.error(f"Port scan error for {host}: {str(e)}")
        return f"Scan error: {str(e)}"

def simulate_port_scan(host: str) -> str:
    """Simulates a port scan by returning a predefined JSON response.

    Args:
        host (str): The IP address or hostname to simulate scanning.

    Returns:
        str: A JSON string with simulated scan results.
    """
    logger.info(f"Simulating port scan for {host}")
    return f'{{"host": "{host}", "open_ports": [22, 80, 443], "scan_time": "2025-09-11T12:00:00Z"}}'