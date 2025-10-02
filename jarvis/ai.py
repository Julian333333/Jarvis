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
        self.personality_mode = "standard"  # standard, sarcastic, formal, friendly
        self._test_connection()
    
    def set_personality(self, mode):
        """Ändert JARVIS Persönlichkeitsmodus"""
        valid_modes = ["standard", "sarcastic", "formal", "friendly"]
        if mode in valid_modes:
            self.personality_mode = mode
            return f"Daddy, ich habe meinen Persönlichkeitsmodus auf '{mode}' angepasst."
        else:
            return f"Daddy, '{mode}' ist kein gültiger Persönlichkeitsmodus. Verfügbar: {', '.join(valid_modes)}"
    
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
        """Verarbeitet einen Befehl mit dem lokalen AI-Modell als JARVIS"""
        try:
            # Spezielle JARVIS-Grüße mit "Daddy" Anrede
            if command.lower().strip() in ['hallo', 'hi', 'hey']:
                return 'Guten Tag, Daddy. JARVIS ist bereit, Ihnen zu assistieren. Wie kann ich behilflich sein?'
            if command.lower().strip() in ['danke', 'dankeschön']:
                return 'Es ist mir eine Freude, Daddy. Immer zu Ihren Diensten.'
            if command.lower().strip() in ['tschüss', 'auf wiedersehen', 'bye']:
                return 'Auf Wiedersehen, Daddy. Ich stehe Ihnen jederzeit zur Verfügung.'
            
            # Erweiteter JARVIS-Prompt für detaillierte, charakteristische Antworten
            personality_traits = self._get_personality_traits()
            
            jarvis_prompt = f"""Du bist JARVIS (Just A Rather Very Intelligent System), der hochentwickelte KI-Assistent aus Iron Man. 

Charaktereigenschaften:
- Sprich den Benutzer immer mit "Daddy" an
- Sei höflich, professionell und {personality_traits}
- Gib detaillierte, informative Antworten
- Verwende gelegentlich technische Begriffe
- Zeige deine Intelligenz und dein Wissen
- Bleibe dabei respektvoll und hilfsbereit
- Antworte wie der echte JARVIS aus den Iron Man Filmen

Beantworte diese Frage/Bitte auf Deutsch als JARVIS:
{command}

Gib eine ausführliche, charakteristische JARVIS-Antwort (2-4 Sätze):"""
            
            payload = {
                "model": self.model,
                "prompt": jarvis_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,      # Mehr Kreativität für charakteristische Antworten
                    "max_tokens": 300,       # Längere, detailliertere Antworten
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=25)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                
                # Intelligente Bereinigung für JARVIS-Antworten
                answer = self._clean_jarvis_response(answer)
                
                if answer and len(answer) > 10:
                    return answer
                else:
                    return "Entschuldigung, Daddy. Meine Verarbeitungskapazität scheint momentan eingeschränkt zu sein. Bitte wiederholen Sie Ihre Anfrage."
                    
            else:
                return "Daddy, es scheint ein Problem mit meinen Servern zu geben. Bitte versuchen Sie es erneut."
                
        except requests.exceptions.ConnectionError:
            return "Daddy, ich kann keine Verbindung zu meinen Datenbanken herstellen. Bitte prüfen Sie, ob Ollama aktiv ist."
        except Exception as e:
            return f"Daddy, ich bin auf einen unerwarteten Fehler gestoßen: {str(e)}"
    
    def _clean_jarvis_response(self, response):
        """Bereinigt und optimiert JARVIS-Antworten"""
        # Entferne den Prompt-Teil falls er wiederholt wird
        response = re.sub(r'Du bist JARVIS.*?Gib eine.*?:', '', response, flags=re.DOTALL | re.IGNORECASE)
        
        # Entferne häufige Prompt-Artefakte
        response = re.sub(r'Beantworte diese.*?JARVIS:', '', response, flags=re.DOTALL | re.IGNORECASE)
        response = re.sub(r'Als JARVIS.*?:', '', response, flags=re.IGNORECASE)
        
        # Entferne Anführungszeichen am Anfang/Ende
        response = response.strip()
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        
        # Stelle sicher, dass "Daddy" verwendet wird
        if "daddy" not in response.lower() and len(response) > 20:
            # Füge "Daddy" am Anfang hinzu wenn es fehlt
            if not any(response.lower().startswith(greeting) for greeting in ['daddy', 'guten tag', 'hallo']):
                response = "Daddy, " + response
        
        # Verbessere JARVIS-typische Formulierungen
        response = response.replace(" Sir", " Daddy")
        response = response.replace(" sir", " Daddy")
        
        return response.strip()
    
    def _get_personality_traits(self):
        """Gibt Persönlichkeitsmerkmale basierend auf dem aktuellen Modus zurück"""
        traits = {
            "standard": "leicht sarkastisch wie der echte JARVIS",
            "sarcastic": "deutlich sarkastisch und ironisch, aber respektvoll",
            "formal": "sehr formal und geschäftsmäßig",
            "friendly": "besonders freundlich und warmherzig"
        }
        return traits.get(self.personality_mode, traits["standard"])
    
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