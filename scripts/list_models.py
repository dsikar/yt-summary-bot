import os
from openai import OpenAI

def list_available_models():
    """List all available OpenAI models with their properties"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        models = client.models.list()
        print("\nAvailable OpenAI Models:")
        print("=" * 50)
        
        # Sort models by ID for better readability
        sorted_models = sorted(models.data, key=lambda x: x.id)
        
        for model in sorted_models:
            print(f"\nModel ID: {model.id}")
            print(f"Created: {model.created}")
            print(f"Owned By: {model.owned_by}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error fetching models: {e}")

if __name__ == "__main__":
    list_available_models()
