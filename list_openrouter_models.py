import os
import requests
import json

def list_openrouter_models():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY environment variable not set")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers=headers
    )
    
    print(f"Status code: {response.status_code}")
    models = response.json()
    
    # Print just the model IDs for clarity
    print("Available models:")
    for model in models.get("data", []):
        print(f"- {model.get('id')}")

if __name__ == "__main__":
    list_openrouter_models()
