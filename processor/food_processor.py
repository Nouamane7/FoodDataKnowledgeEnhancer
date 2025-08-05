import logging
from typing import Optional, List
from config import Config
from database.postgres_client import PostgresClient
from database.mongo_client import MongoDBClient
from llm.ollama_client import OllamaClient
from models import Ingredient, Product

logger = logging.getLogger(__name__)

def process_ingredient(ingredient: Ingredient, llm_client: OllamaClient) -> Optional[Product]:
    """Process a single ingredient through the LLM pipeline"""
    try:
        # Generate initial product data
        product_data = llm_client.transform_ingredient_to_product(ingredient)
        if not product_data:
            logger.error(f"Failed to generate product data for ingredient {ingredient.id}")
            return None

        # Validate and refine through iterations
        for i in range(Config.MAX_ITERATIONS):
            validated_data = llm_client.validate_and_correct_product(ingredient, product_data)
            if validated_data == product_data:
                logger.info(f"Product data converged after {i+1} iterations for ingredient {ingredient.id}")
                break
            product_data = validated_data

        return validated_data
    except Exception as e:
        logger.error(f"Error processing ingredient {ingredient.id}: {e}")
        return None

def process_batch(batch_size: int = None):
    """Process a batch of ingredients from PostgreSQL to MongoDB"""
    if not batch_size:
        batch_size = Config.BATCH_SIZE

    logger.info(f"Starting batch processing with size {batch_size}")
    
    try:
        # Initialize clients
        pg_client = PostgresClient()
        mongo_client = MongoDBClient()
        llm_client = OllamaClient()
        
        # Get ingredients from PostgreSQL
        ingredients = pg_client.get_ingredients(limit=batch_size)
        if not ingredients:
            logger.info("No ingredients to process")
            return
        
        logger.info(f"Retrieved {len(ingredients)} ingredients for processing")
        
        # Process each ingredient
        processed_products: List[Product] = []
        for ingredient in ingredients:
            # Skip if already processed
            if mongo_client.product_exists(ingredient.id):
                logger.info(f"Product for ingredient {ingredient.id} already exists, skipping")
                continue
                
            # Process the ingredient
            product = process_ingredient(ingredient, llm_client)
            if product:
                processed_products.append(product)
        
        # Store results in MongoDB
        if processed_products:
            inserted_count = mongo_client.insert_products(processed_products)
            logger.info(f"Successfully inserted {inserted_count} products into MongoDB")
        else:
            logger.info("No new products to insert")
            
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise
    finally:
        # Close MongoDB connection
        mongo_client.close()
