import ollama
import json
import logging
from typing import Optional, Tuple, Dict, Any
from models import Ingredient, Product
from config import Config

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.client = ollama.Client(host=Config.OLLAMA_HOST)
        self.food_transform_prompt = """
You are a food knowledge assistant. Your task is to transform an Ingredient into a detailed Product JSON object for a food database.

Each ingredient has:
- id: unique numeric ID
- name: the main name of the ingredient (e.g., "Cheddar Cheese")
- category: the type of ingredient (e.g., "Dairy", "Vegetables")

From this, create a Product JSON with the following fields:

- ingredientId: copy the id from the ingredient
- brand: set to "unbranded"
- description: leave as ""
- unit: choose the most realistic unit for the ingredient.
  Common units include "kg", "g", "l", "ml" — but use any other appropriate unit that matches the ingredient's natural form or packaging.
- nutritions: include accurate nutrition facts per 1 unit chosen above.
  Provide as many as relevant (e.g., "energy", "protein", "fat", "sugar", "carbohydrates", "fiber", "salt", "calcium", etc.).
  Each nutrition is an object with value and unit.
- allergens: realistic list based on the ingredient’s name and category
- userGenerated: always false

Only return valid JSON. Do not include any explanation or extra text.

Example:

Ingredient Input:
{
  "id": 101,
  "name": "Cheddar Cheese",
  "category": "Dairy"
}

Expected Product Output:
{
  "ingredientId": 101,
  "brand": "unbranded",
  "description": "",
  "unit": "g",
  "nutritions": {
    "energy": {
      "value": 402,
      "unit": "kcal"
    },
    "protein": {
      "value": 25,
      "unit": "g"
    },
    "fat": {
      "value": 33,
      "unit": "g"
    },
    "saturated_fat": {
      "value": 21,
      "unit": "g"
    },
    "carbohydrates": {
      "value": 1.3,
      "unit": "g"
    },
    "sugar": {
      "value": 0.5,
      "unit": "g"
    },
    "salt": {
      "value": 1.8,
      "unit": "g"
    },
    "calcium": {
      "value": 721,
      "unit": "mg"
    }
  },
  "allergens": ["lactose"],
  "userGenerated": false
}
.
"""

        self.validator_prompt = """
You are a food data validator reviewing a Product JSON created from an ingredient.

Output ONLY valid JSON with these fields exactly:
- ingredientId: integer
- brand: string
- description: string
- unit: string
- nutritions: object with nutrition values { "value": number, "unit": string }
- allergens: list of strings
- userGenerated: boolean

Do NOT include any explanations or extra text before or after.

Example input ingredient:
{
  "id": 101,
  "name": "Cheddar Cheese",
  "category": "Dairy"
}

Example input product JSON:
{
  "ingredientId": 101,
  "brand": "unbranded",
  "description": "",
  "unit": "g",
  "nutritions": {
    "energy": {"value": 402, "unit": "kcal"},
    "protein": {"value": 25, "unit": "g"},
    "fat": {"value": 33, "unit": "g"},
    "saturated_fat": {"value": 21, "unit": "g"},
    "carbohydrates": {"value": 1.3, "unit": "g"},
    "sugar": {"value": 0.5, "unit": "g"},
    "salt": {"value": 1.8, "unit": "g"},
    "calcium": {"value": 721, "unit": "mg"}
  },
  "allergens": ["lactose"],
  "userGenerated": false
}

Output the validated/corrected product JSON ONLY.
"""


    def _call_model(self, model: str, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Make a call to Ollama model with retry logic"""
        # Log the input prompt
        logger.info(f"\n{'='*50}\n{model} - Input:\n{prompt}\n{'='*50}")
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat(
                    model=model,
                    messages=[
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    options={
                        'temperature': 0.1,  # Low temperature for consistent results
                        'top_p': 0.9,
                        'num_predict': 1000,  # Limit response length
                    }
                )
                
                if response and 'message' in response and 'content' in response['message']:
                    result = response['message']['content'].strip()
                    # Log the output response
                    logger.info(f"\n{'='*50}\n{model} - Output:\n{result}\n{'='*50}")
                    return result
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for model {model}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All attempts failed for model {model}")
                    raise
        
        logger.warning(f"\n{'='*50}\n{model} - No valid response received\n{'='*50}")
        return None

    def transform_ingredient_to_product(self, ingredient: Ingredient) -> Optional[Product]:
        """Transform ingredient to product using LLM1"""
        try:
            ingredient_text = f"Ingredient: id={ingredient.id}, name='{ingredient.name}', category='{ingredient.category}'"
            prompt = f"{self.food_transform_prompt}\n\n{ingredient_text}"
            
            response = self._call_model(Config.LLM1_MODEL, prompt)
            if not response:
                return None
            
            # Clean the response to extract JSON
            json_str = self._extract_json(response)
            if not json_str:
                logger.error(f"No valid JSON found in LLM1 response for ingredient {ingredient.id}")
                return None
            
            # Parse and validate JSON
            product_data = json.loads(json_str)
            product = Product(**product_data)
            
            logger.info(f"Successfully transformed ingredient {ingredient.id} to product")
            return product
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for ingredient {ingredient.id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error transforming ingredient {ingredient.id}: {e}")
            return None

    def validate_and_correct_product(self, ingredient: Ingredient, product: Product) -> Optional[Product]:
        """Validate and potentially correct product using LLM2"""
        try:
            ingredient_text = json.dumps({
                "id": ingredient.id,
                "name": ingredient.name,
                "category": ingredient.category
            }, indent=2)

            product_json = json.dumps(product.model_dump(), indent=2)

            prompt = (
                f"{self.validator_prompt}Original ingredient:\n{ingredient_text}\n"
                f"Product JSON to validate:\n{product_json}\n"
                "Output ONLY the corrected or validated Product JSON with no explanation or extra text."
            )

            response = self._call_model(Config.LLM2_MODEL, prompt)
            if not response:
                return product  # Return original if validation fails
            
            # Clean the response to extract JSON
            json_str = self._extract_json(response)
            if not json_str:
                logger.warning(f"No valid JSON found in LLM2 response for ingredient {ingredient.id}, using original")
                return product
            
            # Parse and validate corrected JSON
            corrected_data = json.loads(json_str)
            corrected_product = Product(**corrected_data)
            
            # Check if there were changes
            if corrected_product.model_dump() != product.model_dump():
                logger.info(f"LLM2 made corrections to product for ingredient {ingredient.id}")
                return corrected_product
            else:
                logger.info(f"LLM2 validated product for ingredient {ingredient.id} - no changes needed")
                return product
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in validation for ingredient {ingredient.id}: {e}")
            return product  # Return original if parsing fails
        except Exception as e:
            logger.error(f"Error validating product for ingredient {ingredient.id}: {e}")
            return product  # Return original if validation fails

#     def iterative_refinement(self, ingredient: Ingredient, max_iterations: int = 3) -> Tuple[Optional[Product], int]:
#         """
#         Iterative refinement process between LLM1 and LLM2 until they converge
#         """
#         logger.info(f"Starting iterative refinement for ingredient {ingredient.id}")
        
#         # Initial transformation
#         current_product = self.transform_ingredient_to_product(ingredient)
#         if not current_product:
#             return None, 0
        
#         for iteration in range(max_iterations):
#             logger.info(f"Refinement iteration {iteration + 1} for ingredient {ingredient.id}")
            
#             # Validate and potentially correct with LLM2
#             validated_product = self.validate_and_correct_product(ingredient, current_product)
            
#             if not validated_product:
#                 logger.warning(f"Validation failed at iteration {iteration + 1}")
#                 break
            
#             # Check if products are identical (convergence)
#             if validated_product.model_dump() == current_product.model_dump():
#                 logger.info(f"Convergence achieved at iteration {iteration + 1} for ingredient {ingredient.id}")
#                 return validated_product, iteration + 1
            
#             # If not converged, let LLM1 process the corrected version
#             if iteration < max_iterations - 1:  # Don't do this on the last iteration
#                 # Create a refined prompt for LLM1 based on LLM2's corrections
#                 refined_prompt = f"""
# {self.food_transform_prompt}

# Please review and refine this existing product data:
# {json.dumps(validated_product.model_dump(), indent=2)}

# Original ingredient: id={ingredient.id}, name='{ingredient.name}', category='{ingredient.category}'

# Output only the final JSON product data.
# """
                
#                 response = self._call_model(Config.LLM1_MODEL, refined_prompt)
#                 if response:
#                     json_str = self._extract_json(response)
#                     if json_str:
#                         try:
#                             refined_data = json.loads(json_str)
#                             current_product = Product(**refined_data)
#                         except (json.JSONDecodeError, Exception) as e:
#                             logger.warning(f"Failed to parse refined response: {e}")
#                             current_product = validated_product
#                     else:
#                         current_product = validated_product
#                 else:
#                     current_product = validated_product
#             else:
#                 current_product = validated_product
        
#         logger.info(f"Refinement completed after {max_iterations} iterations for ingredient {ingredient.id}")
#         return current_product, max_iterations

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from text response"""
        text = text.strip()
        
        # Try to find JSON within the text
        start_chars = ['{', '[']
        end_chars = ['}', ']']
        
        for start_char, end_char in zip(start_chars, end_chars):
            start_idx = text.find(start_char)
            if start_idx != -1:
                # Find the matching closing bracket
                bracket_count = 0
                for i, char in enumerate(text[start_idx:], start_idx):
                    if char == start_char:
                        bracket_count += 1
                    elif char == end_char:
                        bracket_count -= 1
                        if bracket_count == 0:
                            return text[start_idx:i+1]
        
        # If no brackets found, try to parse the entire text as JSON
        try:
            json.loads(text)
            return text
        except:
            pass
        
        return None

    def check_models_available(self) -> Dict[str, bool]:
        """Check if the required models are available in Ollama"""
        try:
            models = self.client.list()
            available_models = [model['name'] for model in models['models']]
            
            return {
                'llm1_available': Config.LLM1_MODEL in available_models,
                'llm2_available': Config.LLM2_MODEL in available_models,
                'available_models': available_models
            }
        except Exception as e:
            logger.error(f"Failed to check available models: {e}")
            return {
                'llm1_available': False,
                'llm2_available': False,
                'available_models': []
            }