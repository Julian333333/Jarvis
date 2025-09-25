"""
AI Assistant Module
Integrates with local AI API
"""

import requests
import json

class AIAssistant:
    def __init__(self, api_url="http://localhost:11434/api/generate"):  # Default Ollama API
        self.api_url = api_url
        self.model = "llama2"  # Default model, can be changed
    
    def process_command(self, command):
        try:
            payload = {
                "model": self.model,
                "prompt": command,
                "stream": False
            }
            response = requests.post(self.api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "I couldn't process that command.")
            else:
                return "AI service is not available."
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"
    
    def set_model(self, model):
        self.model = model