from pymongo import MongoClient
from typing import List, Dict, Any
import logging
from models import Product
from config import Config

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB]
        self.collection = self.db[Config.MONGO_COLLECTION]
        logger.info("Connected to MongoDB database")
    
    def insert_product(self, product: Product) -> bool:
        """Insert a single product into MongoDB"""
        try:
            result = self.collection.insert_one(product.model_dump())
            logger.info(f"Inserted product with ingredientId {product.ingredientId}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert product {product.ingredientId}: {e}")
            return False
    
    def insert_products(self, products: List[Product]) -> int:
        """Insert multiple products into MongoDB"""
        if not products:
            return 0
        
        try:
            product_dicts = [product.model_dump() for product in products]
            result = self.collection.insert_many(product_dicts)
            inserted_count = len(result.inserted_ids)
            logger.info(f"Inserted {inserted_count} products into MongoDB")
            return inserted_count
        except Exception as e:
            logger.error(f"Failed to insert products: {e}")
            return 0
    
    def product_exists(self, ingredient_id: int) -> bool:
        """Check if a product with given ingredientId already exists"""
        return self.collection.find_one({"ingredientId": ingredient_id}) is not None
    
    def get_product_by_ingredient_id(self, ingredient_id: int) -> Dict[str, Any]:
        """Retrieve a product by ingredientId"""
        return self.collection.find_one({"ingredientId": ingredient_id})
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        logger.info("MongoDB connection closed")