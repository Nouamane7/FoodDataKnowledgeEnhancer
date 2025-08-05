from pydantic import BaseModel
from typing import Dict, List, Optional

class Ingredient(BaseModel):
    id: int
    name: str
    category: str

class Nutrition(BaseModel):
    value: float
    unit: str

class Product(BaseModel):
    ingredientId: int
    brand: str = "unbranded"
    description: str = ""
    unit: str
    nutritions: Dict[str, Nutrition]
    allergens: List[str]
    userGenerated: bool = False

class ProcessingResult(BaseModel):
    success: bool
    product: Optional[Product] = None
    error: Optional[str] = None
    iterations: int = 0

__all__ = ['Ingredient', 'Nutrition', 'Product', 'ProcessingResult']
