import logging
import argparse
from orchestrator import CoopetitionSystem
from config import SystemConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_QUERY = "просканируй порты на хосте 10.27.192.116"

def main() -> None:
    """Main entry point for the application.

    Initializes the system, processes a user query, and logs the result.
    The query can be provided via command-line arguments or defaults to a predefined value.
    """
    parser = argparse.ArgumentParser(description="Run the CoopetitionSystem with a user query.")
    parser.add_argument(
        "--query",
        type=str,
        default=DEFAULT_QUERY,
        help="User query to process (e.g., 'просканируй порты на хосте 10.27.192.116')"
    )
    args = parser.parse_args()

    try:
        logger.info("Initializing SystemConfig")
        config = SystemConfig()
        
        logger.info("Creating CoopetitionSystem")
        system = CoopetitionSystem(config)
        
        logger.info(f"Processing query: {args.query}")
        result = system.process_query(args.query)
        
        logger.info("Query processing completed")
        print("\n=== Финальный ответ ===")
        print(result)
        
    except Exception as e:
        logger.error(f"Failed to process query: {str(e)}")
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()