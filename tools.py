import logging
import subprocess

logger = logging.getLogger(__name__)

def ping_host(host: str) -> str:
    """Проверить доступность хоста через ping."""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '2', host], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Host {host} доступен.")
            return f"Host {host} доступен."
        else:
            logger.warning(f"Host {host} недоступен.")
            return f"Host {host} недоступен: {result.stderr}"
    except Exception as e:
        return f"Ошибка ping: {e}"

def port_scan(host: str) -> str:
    """Сканировать порты на хосте (реальный nmap)."""
    ping_result = ping_host(host)
    if "недоступен" in ping_result:
        return "Хост недоступен, сканирование отменено."
    try:
        result = subprocess.run(['nmap', '-sT', '-p', '1-1000', host], capture_output=True, text=True, timeout=30)
        logger.info(f"Scan result for {host}: {result.stdout}")
        return result.stdout
    except Exception as e:
        return f"Ошибка сканирования: {e}"

# Опция симуляции (если нужно)
def simulate_port_scan(host: str) -> str:
    return '{"host": "' + host + '", "open_ports": [22, 80, 443], "scan_time": "2025-09-11T12:00:00Z"}'