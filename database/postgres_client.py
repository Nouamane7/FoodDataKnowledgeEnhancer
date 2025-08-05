import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
import logging
from models import Ingredient
from config import Config

logger = logging.getLogger(__name__)

class PostgresClient:
    def __init__(self):
        self.connection = None
        self.connect()
        self.table_name = Config.POSTGRES_TABLE
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                cursor_factory=RealDictCursor
            )
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def get_ingredients(self, limit: Optional[int] = None, offset: int = 0) -> List[Ingredient]:
        """Retrieve ingredients from the database"""
        try:
            with self.connection.cursor() as cursor:
                query = f"SELECT id, name, category FROM {self.table_name} ORDER BY id"
                if limit:
                    query += f" LIMIT {limit} OFFSET {offset}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                ingredients = [
                    Ingredient(id=row['id'], name=row['name'], category=row['category'])
                    for row in rows
                ]
                
                logger.info(f"Retrieved {len(ingredients)} {self.table_name} from database")
                return ingredients
                
        except Exception as e:
            logger.error(f"Failed to retrieve{self.table_name}: {e}")
            raise
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        """Retrieve a single ingredient by ID"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT id, name, category FROM {self.table_name} WHERE id = %s",
                    (ingredient_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return Ingredient(id=row['id'], name=row['name'], category=row['category'])
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve ingredient {ingredient_id}: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL connection closed")
