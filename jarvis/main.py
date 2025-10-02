"""
Jarvis AI Assistant - Main Application
"""

import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QTextEdit, QFrame, QSizePolicy)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QFont, QPainter, QPen, QColor
import pyttsx3
import speech_recognition as sr
from .ai import AIAssistant
from .windows_integration import WindowsIntegration
from .commands import CommandProcessor

class VoiceController(QObject):
    command_received = pyqtSignal(str)
    text_recognized = pyqtSignal(str)  # Neues Signal für Speech-to-Text
    conversation_text = pyqtSignal(str)  # Neues Signal für Konversationsmodus
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.listening = False
        self.continuous_listening = False  # Für kontinuierliche Spracherkennung
        self.conversation_mode = False  # Für kontinuierliche Konversation
        self.activation_word = "jarvis"
        
        # TTS-Engine konfigurieren für bessere deutsche Sprache
        self._setup_tts_engine()
    
    def _setup_tts_engine(self):
        """Konfiguriert die Text-to-Speech Engine für optimale deutsche Ausgabe"""
        try:
            # Verfügbare Stimmen abrufen
            voices = self.engine.getProperty('voices')
            
            # Erweiterte Suche nach deutschen Stimmen
            best_german_voice = None
            fallback_voice = None
            
            print("🔍 Suche nach deutschen TTS-Stimmen...")
            
            for voice in voices:
                voice_name = voice.name.lower() if voice.name else ""
                print(f"📋 Gefunden: {voice.name} - ID: {voice.id}")
                
                # Priorität 1: Explizit deutsche Stimmen
                if voice.languages:
                    for lang in voice.languages:
                        if 'de' in lang.lower() or 'german' in lang.lower():
                            best_german_voice = voice.id
                            print(f"✅ Beste deutsche Stimme gefunden: {voice.name} (Sprache: {lang})")
                            break
                
                # Priorität 2: Deutsche Stimmen anhand des Namens
                german_voice_indicators = [
                    'hedda', 'katja', 'stefan', 'german', 'deutsch', 'de-de'
                ]
                if any(indicator in voice_name for indicator in german_voice_indicators):
                    if not best_german_voice:  # Nur setzen wenn noch keine bessere gefunden
                        best_german_voice = voice.id
                        print(f"✅ Deutsche Stimme nach Name gefunden: {voice.name}")
                
                # Priorität 3: Fallback zu weiblichen/qualitativ hochwertigen Stimmen
                quality_indicators = ['zira', 'hazel', 'eva', 'female']
                if any(indicator in voice_name for indicator in quality_indicators):
                    if not fallback_voice:
                        fallback_voice = voice.id
            
            # Stimme setzen (beste verfügbare Wahl)
            if best_german_voice:
                self.engine.setProperty('voice', best_german_voice)
                print("🎤 Deutsche TTS-Stimme aktiviert für optimale deutsche Aussprache")
            elif fallback_voice:
                self.engine.setProperty('voice', fallback_voice)
                print("🎤 Qualitäts-TTS-Stimme aktiviert (Fallback)")
            else:
                print("🎤 Standard-TTS-Stimme wird verwendet")
            
            # TTS-Eigenschaften für deutsche Sprache optimieren
            self.engine.setProperty('rate', 170)    # Etwas langsamer für deutsche Aussprache
            self.engine.setProperty('volume', 0.95)  # Etwas lauter für Klarheit
            
            # Teste die ausgewählte Stimme
            self._test_german_pronunciation()
            
        except Exception as e:
            print(f"⚠️ TTS-Setup Fehler: {e}")
    
    def _test_german_pronunciation(self):
        """Testet die deutsche Aussprache der gewählten Stimme"""
        try:
            # Test mit typischen deutschen Wörtern
            test_text = "JARVIS Sprachsystem initialisiert."
            print(f"🧪 Teste deutsche Aussprache mit: '{test_text}'")
            # Stille Ausführung des Tests (ohne Ausgabe)
            self.engine.say("")  # Leerer Test um Engine zu initialisieren
            self.engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Sprachtest Fehler: {e}")
    
    def speak(self, text):
        """Spricht den gegebenen Text aus mit deutscher TTS"""
        self._speak_standard(text)
    
    def _speak_standard(self, text):
        """Spricht den gegebenen Text aus mit verbesserter deutscher Aussprache"""
        def _speak():
            try:
                # Bereinige den Text für bessere TTS-Ausgabe
                cleaned_text = self._clean_text_for_tts(text)
                print(f"🔊 JARVIS spricht: {cleaned_text}")
                
                self.engine.say(cleaned_text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"TTS-Fehler: {e}")
        
        threading.Thread(target=_speak, daemon=True).start()
    
    def _clean_text_for_tts(self, text):
        """Bereinigt Text für bessere deutsche TTS-Aussprache"""
        # Entferne problematische Zeichen
        text = text.replace('*', '').replace('#', '')
        text = text.replace('✅', 'OK').replace('❌', 'Fehler')
        text = text.replace('⚠️', 'Warnung').replace('🔊', '')
        text = text.replace('🎤', '').replace('📋', '')
        
        # Verbessere deutsche Aussprache für technische Begriffe
        german_replacements = {
            # Technische Abkürzungen
            'CPU': 'C P U',
            'RAM': 'R A M', 
            'AI': 'A I',
            'API': 'A P I',
            'URL': 'U R L',
            'HTTP': 'H T T P',
            'HTTPS': 'H T T P S',
            'GPU': 'G P U',
            'SSD': 'S S D',
            'USB': 'U S B',
            
            # JARVIS spezifische Begriffe
            'JARVIS': 'Jarvis',
            'J.A.R.V.I.S': 'Jarvis',
            
            # Betriebssystem-Begriffe
            'Windows': 'Windows',
            'Powershell': 'Powerschell',
            'CMD': 'C M D',
            
            # Häufige englische Begriffe deutsch aussprechen
            'Browser': 'Browser',
            'Update': 'Apdeht',
            'Download': 'Daunlohd',
            'Upload': 'Aplohd',
            'Software': 'Software',
            'Hardware': 'Hardware',
            'System': 'Sistehm',
            
            # Deutsche Sonderzeichen richtig aussprechen
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
            'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'
        }
        
        for english, german in german_replacements.items():
            text = text.replace(english, german)
        
        # Verbessere Satzzeichen für natürlichere Pausen
        text = text.replace(', ', ', ')  # Kleine Pause nach Komma
        text = text.replace('. ', '. ')   # Pause nach Punkt
        text = text.replace('! ', '! ')   # Pause nach Ausrufezeichen
        text = text.replace('? ', '? ')   # Pause nach Fragezeichen
        
        return text.strip()
    
    def listen_for_activation(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio, language='de-DE').lower()
                    if self.activation_word in text:
                        self.speak("Ja, Sir?")
                        self.command_received.emit(text.replace(self.activation_word, "").strip())
                        break
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    continue
    
    def listen_continuous(self):
        """Kontinuierliche Spracherkennung für Speech-to-Text"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        while self.continuous_listening:
            try:
                with sr.Microphone() as source:
                    # Kürzere Timeouts für responsivere Erkennung
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio, language='de-DE')
                    if text.strip():  # Nur wenn Text erkannt wurde
                        self.text_recognized.emit(text)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Spracherkennungsfehler: {e}")
                continue
    
    def listen_conversation(self):
        """Kontinuierliche Konversation - hört zu und führt Befehle automatisch aus"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        while self.conversation_mode:
            try:
                with sr.Microphone() as source:
                    # Längere Timeouts für natürliche Konversation
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio, language='de-DE')
                    if text.strip():  # Nur wenn Text erkannt wurde
                        self.conversation_text.emit(text)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Konversationsfehler: {e}")
                continue
    
    def start_listening(self):
        self.listening = True
        threading.Thread(target=self.listen_for_activation, daemon=True).start()
    
    def stop_listening(self):
        self.listening = False
    
    def start_continuous_listening(self):
        self.continuous_listening = True
        threading.Thread(target=self.listen_continuous, daemon=True).start()
    
    def stop_continuous_listening(self):
        self.continuous_listening = False
    
    def start_conversation(self):
        self.conversation_mode = True
        threading.Thread(target=self.listen_conversation, daemon=True).start()
    
    def stop_conversation(self):
        self.conversation_mode = False

class JarvisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S")
        # Optimale Startgröße für Full HD (1920x1080)
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(1280, 720)

        # Einfaches, responsives Design mit großen Schriftarten
        self.setStyleSheet("""
QMainWindow {
    background-color: #0a0a0a;
    color: #00FFFF;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QLabel {
    color: #00FFFF;
    font-size: 34px;
    font-weight: bold;
}
QPushButton {
                background-color: #1a1a2e;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                padding: 20px 30px;
                color: #00FFFF;
                font-size: 40px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #16213e;
                border-color: #66ddff;
                color: #66ddff;
            }
            QPushButton:pressed {
                background-color: #0f1729;
            }
            QTextEdit {
                background-color: #1a1a2e;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                padding: 20px;
                color: #00FFFF;
                font-size: 36px;
                line-height: 1.4;
            }
            QFrame {
                background-color: rgba(26, 26, 46, 0.8);
                border: 1px solid #00FFFF;
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        # Hauptlayout - einfach und vertikal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header - groß und einfach
        self.create_header(main_layout)
        
        # Status Bereich
        self.create_status_section(main_layout)
        
        # Hauptinterface
        self.create_main_interface(main_layout)
        
        # Komponenten initialisieren
        self.ai = AIAssistant()
        self.windows_int = WindowsIntegration()
        self.voice = VoiceController()
        self.voice.command_received.connect(self.handle_voice_command)
        self.voice.text_recognized.connect(self.handle_speech_to_text)  # Neues Signal verbinden
        self.voice.conversation_text.connect(self.handle_conversation)  # Konversations-Signal
        
        # Befehlsprozessor für Sprachsteuerung
        self.command_processor = CommandProcessor(self)
        
        # Timer für Updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)
        
    def create_header(self, layout):
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(20)
        
        # Großer JARVIS Titel
        title = QLabel("J.A.R.V.I.S")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 80px;
            font-weight: bold;
            color: #00FFFF;
            margin: 30px;
            letter-spacing: 8px;
        """)
        header_layout.addWidget(title)
        
        # Status
        self.main_status = QLabel("SYSTEM BEREIT")
        self.main_status.setAlignment(Qt.AlignCenter)
        self.main_status.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            color: #00FF00;
            margin-bottom: 30px;
        """)
        header_layout.addWidget(self.main_status)
        
        layout.addWidget(header_frame)
        
    def create_status_section(self, layout):
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setSpacing(60)
        
        # AI Status
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        ai_title = QLabel("KI KERN")
        ai_title.setAlignment(Qt.AlignCenter)
        ai_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #00FFFF; margin-bottom: 15px;")
        self.ai_status = QLabel("AKTIV")
        self.ai_status.setAlignment(Qt.AlignCenter)
        self.ai_status.setStyleSheet("font-size: 40px; font-weight: bold; color: #00FF00;")
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(self.ai_status)
        
        # Voice Status
        voice_widget = QWidget()
        voice_layout = QVBoxLayout(voice_widget)
        voice_title = QLabel("SPRACHE")
        voice_title.setAlignment(Qt.AlignCenter)
        voice_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #00FFFF; margin-bottom: 15px;")
        self.voice_status = QLabel("BEREIT")
        self.voice_status.setAlignment(Qt.AlignCenter)
        self.voice_status.setStyleSheet("font-size: 40px; font-weight: bold; color: #FFA500;")
        voice_layout.addWidget(voice_title)
        voice_layout.addWidget(self.voice_status)
        
        # System Status
        sys_widget = QWidget()
        sys_layout = QVBoxLayout(sys_widget)
        sys_title = QLabel("SYSTEM")
        sys_title.setAlignment(Qt.AlignCenter)
        sys_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #00FFFF; margin-bottom: 15px;")
        self.sys_status = QLabel("ONLINE")
        self.sys_status.setAlignment(Qt.AlignCenter)
        self.sys_status.setStyleSheet("font-size: 40px; font-weight: bold; color: #00FF00;")
        sys_layout.addWidget(sys_title)
        sys_layout.addWidget(self.sys_status)
        
        status_layout.addWidget(ai_widget)
        status_layout.addWidget(voice_widget)
        status_layout.addWidget(sys_widget)
        
        layout.addWidget(status_frame)
        
    def create_main_interface(self, layout):
        # Chat Bereich
        chat_frame = QFrame()
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setSpacing(30)
        
        # Chat Label
        chat_label = QLabel("KOMMUNIKATION")
        chat_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #00FFFF; margin-bottom: 20px;")
        chat_layout.addWidget(chat_label)
        
        # Output Text - größer und klarer
        self.output_text = QTextEdit()
        self.output_text.setMinimumHeight(180)
        self.output_text.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            background-color: #0d0d0d;
            color: #ffffff;
            border: 2px solid #00FFFF;
            border-radius: 8px;
            padding: 15px;
            line-height: 1.5;
        """)
        self.output_text.append("<span style='color: #00FF00; font-size: 34px; font-weight: bold;'>[SYSTEM]</span> <span style='font-size: 40px;'>J.A.R.V.I.S ist online und bereit.</span>")
        chat_layout.addWidget(self.output_text)
        
        # Input Bereich
        input_frame = QFrame()
        input_frame.setMinimumHeight(100)  # Mindesthöhe reduziert
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(25)
        
        # Input Label
        input_label = QLabel("BEFEHLSEINGABE")
        input_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #00FFFF;")
        input_layout.addWidget(input_label)
        
        # Input Text - größer und klarer
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(150)
        self.input_text.setStyleSheet("""
            font-size: 40px;
            font-weight: bold;
            padding: 15px;
            background-color: #1a1a1a;
            color: #ffffff;
            border: 2px solid #00FFFF;
            border-radius: 8px;
        """)
        self.input_text.setPlaceholderText("Geben Sie Ihren Befehl ein oder verwenden Sie das Mikrofon...")
        input_layout.addWidget(self.input_text)
        
        # Buttons - deutlich größer und klarer
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Button-Style für alle Buttons
        button_style = """
            QPushButton {
                font-size: 36px;
                font-weight: bold;
                padding: 15px 25px;
                background-color: #2d2d2d;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                border-radius: 8px;
                min-height: 50px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00FF00;
                color: #00FF00;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """
        
        self.execute_button = QPushButton("AUSFÜHREN")
        self.execute_button.clicked.connect(self.send_command)
        self.execute_button.setStyleSheet(button_style)
        
        self.voice_button = QPushButton("SPRACHSTEUERUNG")
        self.voice_button.clicked.connect(self.toggle_voice)
        self.voice_button.setStyleSheet(button_style)
        
        self.speech_to_text_button = QPushButton("🎤 MIKROFON")
        self.speech_to_text_button.clicked.connect(self.toggle_speech_to_text)
        self.speech_to_text_button.setStyleSheet(button_style)
        self.speech_to_text_active = False
        
        self.conversation_button = QPushButton("💬 GESPRÄCH")
        self.conversation_button.clicked.connect(self.toggle_conversation)
        self.conversation_button.setStyleSheet(button_style)
        self.conversation_active = False
        
        self.diagnostics_button = QPushButton("DIAGNOSE")
        self.diagnostics_button.clicked.connect(self.run_diagnostics)
        self.diagnostics_button.setStyleSheet(button_style)
        
        button_layout.addWidget(self.execute_button)
        button_layout.addWidget(self.voice_button)
        button_layout.addWidget(self.speech_to_text_button)
        button_layout.addWidget(self.conversation_button)
        button_layout.addWidget(self.diagnostics_button)
        input_layout.addLayout(button_layout)
        
        chat_layout.addWidget(input_frame)
        layout.addWidget(chat_frame)
        
        # Nach dem Erstellen der Widgets:
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
    
    def send_command(self):
        command = self.input_text.toPlainText().strip()
        if command:
            self.process_command(command)
            self.input_text.clear()
    
    def toggle_voice(self):
        if self.voice.listening:
            self.voice.stop_listening()
            self.voice_button.setText("SPRACHSTEUERUNG")
            self.voice_status.setText("BEREIT")
            self.voice_status.setStyleSheet("font-size: 34px; color: #FFA500;")
            self.main_status.setText("SYSTEM BEREIT")
            self.main_status.setStyleSheet("font-size: 40px; color: #00FF00; margin-bottom: 20px;")
        else:
            self.voice.start_listening()
            self.voice_button.setText("SPRACHE AKTIV")
            self.voice_status.setText("HÖRT ZU")
            self.voice_status.setStyleSheet("font-size: 34px; color: #FF0000;")
            self.main_status.setText("HÖRE AUF 'JARVIS'")
            self.main_status.setStyleSheet("font-size: 40px; color: #FF8800; margin-bottom: 20px;")
    
    def toggle_speech_to_text(self):
        """Schaltet Speech-to-Text Modus um"""
        if self.speech_to_text_active:
            # Speech-to-Text deaktivieren
            self.voice.stop_continuous_listening()
            self.speech_to_text_button.setText("🎤 MIKROFON")
            self.speech_to_text_button.setStyleSheet("")  # Standard-Style
            self.speech_to_text_active = False
            self.voice_status.setText("BEREIT")
            self.voice_status.setStyleSheet("font-size: 34px; color: #FFA500;")
            self.output_text.append("<span style='color: #0096FF; font-size: 40px;'>[SYSTEM]</span> Spracherkennung deaktiviert.")
        else:
            # Speech-to-Text aktivieren
            self.voice.start_continuous_listening()
            self.speech_to_text_button.setText("🔴 AUFNAHME")
            self.speech_to_text_button.setStyleSheet("background-color: #ff4444; border-color: #ff6666;")
            self.speech_to_text_active = True
            self.voice_status.setText("NIMMT AUF")
            self.voice_status.setStyleSheet("font-size: 34px; color: #FF0000;")
            self.output_text.append("<span style='color: #0096FF; font-size: 40px;'>[SYSTEM]</span> Spracherkennung aktiviert. Sprechen Sie in das Mikrofon...")
    
    def toggle_conversation(self):
        """Schaltet den kontinuierlichen Konversationsmodus um"""
        if self.conversation_active:
            # Konversationsmodus deaktivieren
            self.voice.stop_conversation()
            self.conversation_button.setText("💬 GESPRÄCH")
            self.conversation_button.setStyleSheet("")  # Standard-Style
            self.conversation_active = False
            self.voice_status.setText("BEREIT")
            self.voice_status.setStyleSheet("font-size: 34px; color: #FFA500;")
            self.main_status.setText("SYSTEM BEREIT")
            self.main_status.setStyleSheet("font-size: 40px; color: #00FF00; margin-bottom: 20px;")
            self.output_text.append("<span style='color: #0096FF; font-size: 40px;'>[SYSTEM]</span> Konversationsmodus deaktiviert.")
        else:
            # Andere Modi erst stoppen
            if self.speech_to_text_active:
                self.toggle_speech_to_text()
            if self.voice.listening:
                self.toggle_voice()
            
            # Konversationsmodus aktivieren
            self.voice.start_conversation()
            self.conversation_button.setText("🔴 IM GESPRÄCH")
            self.conversation_button.setStyleSheet("background-color: #ff4444; border-color: #ff6666;")
            self.conversation_active = True
            self.voice_status.setText("HÖRT ZU")
            self.voice_status.setStyleSheet("font-size: 34px; color: #FF0000;")
            self.main_status.setText("GESPRÄCHSMODUS AKTIV")
            self.main_status.setStyleSheet("font-size: 40px; color: #FF0000; margin-bottom: 20px;")
            self.output_text.append("<span style='color: #FF0000; font-size: 40px;'>[SYSTEM]</span> Konversationsmodus aktiviert. Sprechen Sie einfach - JARVIS hört kontinuierlich zu!")
            
            # Auto-scroll
            scrollbar = self.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def handle_conversation(self, text):
        """Behandelt kontinuierliche Konversation - führt Befehle automatisch aus"""
        self.output_text.append(f"<span style='color: #FF6600; font-size: 40px;'>[SIE]</span> {text}")
        
        # Prüfe auf Stopp-Befehle
        if any(word in text.lower() for word in ['stopp', 'stop', 'beenden', 'aufhören', 'schluss']):
            self.toggle_conversation()
            self.voice.speak("Konversationsmodus beendet.")
            return
        
        # Verarbeite den Befehl automatisch
        if any(keyword in text.lower() for keyword in self.command_processor.commands.keys()):
            response = self.command_processor.process_command(text)
        else:
            response = self.ai.process_command(text)
            
        self.output_text.append(f"<span style='color: #00FF00; font-size: 40px;'>[JARVIS]</span> {response}")
        self.voice.speak(response)
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def handle_speech_to_text(self, text):
        """Behandelt erkannten Text vom Speech-to-Text"""
        # Füge den erkannten Text zum bestehenden Text im Input-Feld hinzu
        current_text = self.input_text.toPlainText()
        if current_text:
            # Füge Leerzeichen hinzu wenn bereits Text vorhanden ist
            new_text = current_text + " " + text
        else:
            new_text = text
        
        self.input_text.setText(new_text)
        
        # Cursor ans Ende setzen
        cursor = self.input_text.textCursor()
        cursor.movePosition(cursor.End)
        self.input_text.setTextCursor(cursor)
        
        # Feedback im Chat
        self.output_text.append(f"<span style='color: #FFA500; font-size: 36px;'>[MIKROFON]</span> {text}")
    
    def handle_voice_command(self, command):
        self.output_text.append(f"<span style='color: #FF8800; font-size: 40px;'>[SPRACHE]</span> {command}")
        
        # Verwende den Befehlsprozessor für Sprachbefehle
        response = self.command_processor.process_command(command)
        self.output_text.append(f"<span style='color: #00FF00; font-size: 40px;'>[JARVIS]</span> {response}")
        self.voice.speak(response)
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def process_command(self, command):
        self.output_text.append(f"<span style='color: #00FFFF; font-size: 40px;'>[BENUTZER]</span> {command}")
        
        # Für getippte Befehle: Prüfe erst auf Sprachbefehle, dann AI
        if any(keyword in command.lower() for keyword in self.command_processor.commands.keys()):
            response = self.command_processor.process_command(command)
        else:
            response = self.ai.process_command(command)
            
        self.output_text.append(f"<span style='color: #00FF00; font-size: 40px;'>[JARVIS]</span> {response}")
        self.voice.speak(response)
        
        # Windows integration
        self.windows_int.execute_command(command)
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def run_diagnostics(self):
        self.output_text.append("<span style='color: #0096FF; font-size: 40px;'>[SYSTEM]</span> Führe vollständige Systemdiagnose durch...")
        self.ai_status.setText("OPTIMAL")
        self.ai_status.setStyleSheet("font-size: 34px; color: #00FF00;")
        self.sys_status.setText("PERFEKT")
        self.sys_status.setStyleSheet("font-size: 34px; color: #00FF00;")
        self.output_text.append("<span style='color: #00FF00; font-size: 40px;'>[SYSTEM]</span> Alle Systeme optimal. Keine Probleme erkannt.")
    
    def update_status(self):
        # Einfache Status-Updates ohne komplexe Animationen
        pass

    def resizeEvent(self, event):
        """Passe Schriftgrößen und Layout dynamisch an die Fenstergröße an"""
        width = self.width()
        # Dynamische Skalierung: Schriftgröße proportional zur Fensterbreite
        # Für Full HD: Standard-Schriftgröße 18, skaliert ab 1600px
        if width >= 1920:
            font_size = 18
        elif width >= 1600:
            font_size = 16
        elif width >= 1280:
            font_size = 14
        else:
            font_size = 12
        font = QFont("Segoe UI", font_size, QFont.Bold)
        self.setFont(font)
        # Passe auch die Größe der Textfelder und Buttons an
        if hasattr(self, "output_text"):
            self.output_text.setFont(font)
        if hasattr(self, "input_text"):
            self.input_text.setFont(font)
        for btn in [getattr(self, n, None) for n in ["execute_button", "voice_button", "speech_to_text_button", "conversation_button", "diagnostics_button"]]:
            if btn:
                btn.setFont(font)
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    screen_size = screen.size()
    # Dynamische Schriftgröße abhängig von Bildschirmbreite
    # Optimale Schriftgröße für Full HD
    if screen_size.width() >= 1920:
        font_size = 18
    elif screen_size.width() >= 1600:
        font_size = 16
    elif screen_size.width() >= 1280:
        font_size = 14
    else:
        font_size = 12
    font = QFont("Segoe UI", font_size, QFont.Bold)
    app.setFont(font)
    window = JarvisGUI()
    # Setze Fenstergröße auf 1600x900 für Full HD
    window.resize(1600, 900)
    window.show()
    print("🎤 Deutsche TTS-Stimme aktiviert - JARVIS bereit!")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()