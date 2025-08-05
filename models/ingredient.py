from pydantic import BaseModel

class Ingredient(BaseModel):
    id: int
    name: str
    category: str

    def to_prompt(self) -> str:
        """Format ingredient data for LLM prompts"""
        return f"""Ingredient:
- id: {self.id}
- name: {self.name}
- category: {self.category}
"""

    class Config:
        from_attributes = True  # Allow ORM mode
