from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class NutritionValue(BaseModel):
    value: float
    unit: str

class Product(BaseModel):
    ingredientId: int
    brand: str = "unbranded"
    description: str = ""
    unit: str
    nutritions: Dict[str, NutritionValue]
    allergens: List[str]
    userGenerated: bool = False

    def to_json(self) -> str:
        """Return the product as a JSON string"""
        return self.model_dump_json(indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Return the product as a dictionary"""
        return self.model_dump()
