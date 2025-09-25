"""
Voice Control Module
Handles speech recognition and text-to-speech
"""

import speech_recognition as sr
import pyttsx3
import threading

class VoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.listening = False
        self.activation_word = "jarvis"
        
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen_for_command(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text = self.recognizer.recognize_google(audio).lower()
                    return text
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    continue
        return None
    
    def start_listening(self):
        self.listening = True
    
    def stop_listening(self):
        self.listening = False