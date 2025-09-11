import logging
from orchestrator import CoopetitionSystem
from config import SystemConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    config = SystemConfig()
    system = CoopetitionSystem(config)
    user_query = "просканируй порты на хосте 192.168.192.219"
    result = system.process_query(user_query)
    print("\n=== Финальный ответ ===")
    print(result)

if __name__ == "__main__":
    main()