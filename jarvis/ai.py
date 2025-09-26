"""
AI Assistant Module
Integrates with local AI API (Ollama)
"""

import requests
import re

class AIAssistant:
    def __init__(self, api_url="http://localhost:11434/api/generate"):
        self.api_url = api_url
        self.model = "llama3.2:3b"  # Besseres Modell für Konversationen
        self._test_connection()
    
    def _test_connection(self):
        """Testet die Verbindung zu Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                print(f"Ollama verbunden. Verfügbare Modelle: {model_names}")
                
                if self.model in model_names:
                    print(f"✅ Modell '{self.model}' gefunden und bereit!")
                else:
                    print(f"⚠️ Modell '{self.model}' nicht gefunden.")
                    if model_names:
                        self.model = model_names[0]
                        print(f"Verwende stattdessen: {self.model}")
            else:
                print(f"❌ Ollama API nicht erreichbar")
        except requests.exceptions.ConnectionError:
            print("❌ Ollama ist nicht gestartet. Starten Sie 'ollama serve'")
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    def process_command(self, command):
        """Verarbeitet einen Befehl mit dem lokalen AI-Modell"""
        try:
            # Nur für sehr einfache Grüße eine schnelle Antwort
            if command.lower().strip() in ['hallo', 'hi', 'hey']:
                return 'Hallo! Wie kann ich helfen?'
            if command.lower().strip() in ['danke', 'dankeschön']:
                return 'Gerne!'
            if command.lower().strip() in ['tschüss', 'auf wiedersehen', 'bye']:
                return 'Auf Wiedersehen!'
            
            # Sehr einfacher, direkter Prompt
            payload = {
                "model": self.model,
                "prompt": f"Antworte auf Deutsch in 1-2 Sätzen: {command}",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 150,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                
                # Sehr minimale Bereinigung - nur offensichtliche Probleme
                if answer.startswith('"') and answer.endswith('"'):
                    answer = answer[1:-1]
                
                # Entferne nur die allergrößten Probleme
                answer = re.sub(r'Antworte auf Deutsch.*?:', '', answer, flags=re.IGNORECASE)
                answer = answer.strip()
                
                if answer and len(answer) > 3:
                    return answer
                else:
                    return "Entschuldigung, ich konnte keine Antwort finden."
                    
            else:
                return "AI-Service nicht verfügbar."
                
        except requests.exceptions.ConnectionError:
            return "Ollama ist nicht erreichbar."
        except Exception as e:
            return f"Fehler: {str(e)}"
    
    def set_model(self, model_name):
        """Ändert das verwendete AI-Modell"""
        self.model = model_name
        print(f"AI-Modell geändert zu: {model_name}")
        self._test_connection()
    
    def get_available_models(self):
        """Ruft verfügbare Ollama-Modelle ab"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            else:
                return ["Fehler beim Abrufen der Modelle"]
        except Exception as e:
            return [f"Verbindungsfehler: {str(e)}"]