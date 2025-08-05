"""
# Food Ingredient to Product Processor

A Python application that retrieves ingredient data from PostgreSQL, transforms it into detailed product information using local LLMs via Ollama, and stores the results in MongoDB.

## Features

- **PostgreSQL Integration**: Retrieves ingredients with id, name, and category
- **Local LLM Processing**: Uses Ollama for private, cost-effective AI processing
- **Dual LLM Validation**: Iterative refinement between two models until convergence
- **MongoDB Storage**: Stores enriched product data with nutritional information
- **Batch Processing**: Efficient processing of large ingredient datasets
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Architecture

1. **LLM1 (Primary Transformer)**: Converts ingredients to detailed products
2. **LLM2 (Validator/Corrector)**: Reviews and corrects the product data
3. **Iterative Refinement**: Both LLMs work together until they reach consensus
4. **Data Pipeline**: PostgreSQL → LLM Processing → MongoDB

## Prerequisites

- Python 3.8+
- PostgreSQL with ingredient table
- MongoDB instance
- Ollama running locally
- Required Ollama models (llama3.1:8b, mistral:7b)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd food-processor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Setup Ollama models:
```bash
ollama pull llama3.1:8b
ollama pull mistral:7b
```

## Database Schema

### PostgreSQL (Source)
```sql
CREATE TABLE ingredient (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL
);
```

### MongoDB (Destination)
```json
{
  "ingredientId": 1,
  "brand": "unbranded",
  "description": "",
  "unit": "kg",
  "nutritions": {
    "energy": {"value": 2640, "unit": "kJ"},
    "protein": {"value": 25.0, "unit": "g"},
    "fat": {"value": 33.0, "unit": "g"},
    "carbohydrates": {"value": 1.3, "unit": "g"}
  },
  "allergens": ["lactose"],
  "userGenerated": false
}
```