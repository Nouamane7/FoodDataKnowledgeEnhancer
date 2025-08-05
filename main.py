import logging
import sys
from config import Config
from processor.food_processor import process_batch
from llm.ollama_client import OllamaClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('food_processor.log')
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required services are available"""
    try:
        # Check Ollama models
        ollama_client = OllamaClient()
        model_status = ollama_client.check_models_available()
        
        if not model_status['llm1_available']:
            logger.error(f"Primary model {Config.LLM1_MODEL} not available in Ollama")
            return False
        
        if not model_status['llm2_available']:
            logger.error(f"Validator model {Config.LLM2_MODEL} not available in Ollama")
            return False
            
        logger.info("✓ Ollama models available")
        return True
        
    except Exception as e:
        logger.error(f"Failed to check environment: {e}")
        return False

def main():
    """Main entry point for the food processor"""
    try:
        logger.info("🟢 Food Processor starting...")
        logger.info(f"PostgreSQL: {Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}")
        logger.info(f"MongoDB: {Config.MONGO_URI}")
        logger.info(f"Using models: {Config.LLM1_MODEL} (primary), {Config.LLM2_MODEL} (validator)")
        
        # Check environment
        if not check_environment():
            logger.error("Environment check failed, exiting")
            sys.exit(1)
        
        # Process ingredients
        process_batch()
        
        logger.info("✅ Processing completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
