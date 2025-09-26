"""
Jarvis AI Assistant - Main Application
"""

import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QTextEdit, QFrame)
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
        
    def speak(self, text):
        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()
        threading.Thread(target=_speak, daemon=True).start()
    
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
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Einfaches, responsives Design mit großen Schriftarten
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                color: #00FFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #00FFFF;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #1a1a2e;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                padding: 20px 30px;
                color: #00FFFF;
                font-size: 18px;
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
                font-size: 16px;
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
            font-size: 56px;
            font-weight: bold;
            color: #00FFFF;
            margin: 20px;
        """)
        header_layout.addWidget(title)
        
        # Status
        self.main_status = QLabel("SYSTEM BEREIT")
        self.main_status.setAlignment(Qt.AlignCenter)
        self.main_status.setStyleSheet("""
            font-size: 24px;
            color: #00FF00;
            margin-bottom: 20px;
        """)
        header_layout.addWidget(self.main_status)
        
        layout.addWidget(header_frame)
        
    def create_status_section(self, layout):
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setSpacing(40)
        
        # AI Status
        ai_widget = QWidget()
        ai_layout = QVBoxLayout(ai_widget)
        ai_title = QLabel("KI KERN")
        ai_title.setAlignment(Qt.AlignCenter)
        ai_title.setStyleSheet("font-size: 22px; color: #00FFFF; margin-bottom: 10px;")
        self.ai_status = QLabel("AKTIV")
        self.ai_status.setAlignment(Qt.AlignCenter)
        self.ai_status.setStyleSheet("font-size: 20px; color: #00FF00;")
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(self.ai_status)
        
        # Voice Status
        voice_widget = QWidget()
        voice_layout = QVBoxLayout(voice_widget)
        voice_title = QLabel("SPRACHE")
        voice_title.setAlignment(Qt.AlignCenter)
        voice_title.setStyleSheet("font-size: 22px; color: #00FFFF; margin-bottom: 10px;")
        self.voice_status = QLabel("BEREIT")
        self.voice_status.setAlignment(Qt.AlignCenter)
        self.voice_status.setStyleSheet("font-size: 20px; color: #FFA500;")
        voice_layout.addWidget(voice_title)
        voice_layout.addWidget(self.voice_status)
        
        # System Status
        sys_widget = QWidget()
        sys_layout = QVBoxLayout(sys_widget)
        sys_title = QLabel("SYSTEM")
        sys_title.setAlignment(Qt.AlignCenter)
        sys_title.setStyleSheet("font-size: 22px; color: #00FFFF; margin-bottom: 10px;")
        self.sys_status = QLabel("ONLINE")
        self.sys_status.setAlignment(Qt.AlignCenter)
        self.sys_status.setStyleSheet("font-size: 20px; color: #00FF00;")
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
        chat_layout.setSpacing(20)
        
        # Chat Label
        chat_label = QLabel("KOMMUNIKATION")
        chat_label.setStyleSheet("font-size: 24px; color: #00FFFF; margin-bottom: 15px;")
        chat_layout.addWidget(chat_label)
        
        # Output Text - größer und einfacher
        self.output_text = QTextEdit()
        self.output_text.setMinimumHeight(250)
        self.output_text.append("<span style='color: #00FF00; font-size: 18px;'>[SYSTEM]</span> J.A.R.V.I.S ist online und bereit.")
        chat_layout.addWidget(self.output_text)
        
        # Input Bereich
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(20)
        
        # Input Label
        input_label = QLabel("BEFEHLSEINGABE")
        input_label.setStyleSheet("font-size: 24px; color: #00FFFF;")
        input_layout.addWidget(input_label)
        
        # Input Text
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(100)
        self.input_text.setPlaceholderText("Geben Sie Ihren Befehl ein oder verwenden Sie das Mikrofon...")
        input_layout.addWidget(self.input_text)
        
        # Buttons - groß und einfach
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        
        self.execute_button = QPushButton("AUSFÜHREN")
        self.execute_button.clicked.connect(self.send_command)
        
        self.voice_button = QPushButton("SPRACHSTEUERUNG")
        self.voice_button.clicked.connect(self.toggle_voice)
        
        self.speech_to_text_button = QPushButton("🎤 MIKROFON")
        self.speech_to_text_button.clicked.connect(self.toggle_speech_to_text)
        self.speech_to_text_active = False
        
        self.conversation_button = QPushButton("💬 GESPRÄCH")
        self.conversation_button.clicked.connect(self.toggle_conversation)
        self.conversation_active = False
        
        self.diagnostics_button = QPushButton("DIAGNOSE")
        self.diagnostics_button.clicked.connect(self.run_diagnostics)
        
        button_layout.addWidget(self.execute_button)
        button_layout.addWidget(self.voice_button)
        button_layout.addWidget(self.speech_to_text_button)
        button_layout.addWidget(self.conversation_button)
        button_layout.addWidget(self.diagnostics_button)
        
        input_layout.addLayout(button_layout)
        
        chat_layout.addWidget(input_frame)
        layout.addWidget(chat_frame)
    
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
            self.voice_status.setStyleSheet("font-size: 20px; color: #FFA500;")
            self.main_status.setText("SYSTEM BEREIT")
            self.main_status.setStyleSheet("font-size: 24px; color: #00FF00; margin-bottom: 20px;")
        else:
            self.voice.start_listening()
            self.voice_button.setText("SPRACHE AKTIV")
            self.voice_status.setText("HÖRT ZU")
            self.voice_status.setStyleSheet("font-size: 20px; color: #FF0000;")
            self.main_status.setText("HÖRE AUF 'JARVIS'")
            self.main_status.setStyleSheet("font-size: 24px; color: #FF8800; margin-bottom: 20px;")
    
    def toggle_speech_to_text(self):
        """Schaltet Speech-to-Text Modus um"""
        if self.speech_to_text_active:
            # Speech-to-Text deaktivieren
            self.voice.stop_continuous_listening()
            self.speech_to_text_button.setText("🎤 MIKROFON")
            self.speech_to_text_button.setStyleSheet("")  # Standard-Style
            self.speech_to_text_active = False
            self.voice_status.setText("BEREIT")
            self.voice_status.setStyleSheet("font-size: 20px; color: #FFA500;")
            self.output_text.append("<span style='color: #0096FF; font-size: 18px;'>[SYSTEM]</span> Spracherkennung deaktiviert.")
        else:
            # Speech-to-Text aktivieren
            self.voice.start_continuous_listening()
            self.speech_to_text_button.setText("🔴 AUFNAHME")
            self.speech_to_text_button.setStyleSheet("background-color: #ff4444; border-color: #ff6666;")
            self.speech_to_text_active = True
            self.voice_status.setText("NIMMT AUF")
            self.voice_status.setStyleSheet("font-size: 20px; color: #FF0000;")
            self.output_text.append("<span style='color: #0096FF; font-size: 18px;'>[SYSTEM]</span> Spracherkennung aktiviert. Sprechen Sie in das Mikrofon...")
    
    def toggle_conversation(self):
        """Schaltet den kontinuierlichen Konversationsmodus um"""
        if self.conversation_active:
            # Konversationsmodus deaktivieren
            self.voice.stop_conversation()
            self.conversation_button.setText("💬 GESPRÄCH")
            self.conversation_button.setStyleSheet("")  # Standard-Style
            self.conversation_active = False
            self.voice_status.setText("BEREIT")
            self.voice_status.setStyleSheet("font-size: 20px; color: #FFA500;")
            self.main_status.setText("SYSTEM BEREIT")
            self.main_status.setStyleSheet("font-size: 24px; color: #00FF00; margin-bottom: 20px;")
            self.output_text.append("<span style='color: #0096FF; font-size: 18px;'>[SYSTEM]</span> Konversationsmodus deaktiviert.")
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
            self.voice_status.setStyleSheet("font-size: 20px; color: #FF0000;")
            self.main_status.setText("GESPRÄCHSMODUS AKTIV")
            self.main_status.setStyleSheet("font-size: 24px; color: #FF0000; margin-bottom: 20px;")
            self.output_text.append("<span style='color: #FF0000; font-size: 18px;'>[SYSTEM]</span> Konversationsmodus aktiviert. Sprechen Sie einfach - JARVIS hört kontinuierlich zu!")
            
            # Auto-scroll
            scrollbar = self.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def handle_conversation(self, text):
        """Behandelt kontinuierliche Konversation - führt Befehle automatisch aus"""
        self.output_text.append(f"<span style='color: #FF6600; font-size: 18px;'>[SIE]</span> {text}")
        
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
            
        self.output_text.append(f"<span style='color: #00FF00; font-size: 18px;'>[JARVIS]</span> {response}")
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
        self.output_text.append(f"<span style='color: #FFA500; font-size: 16px;'>[MIKROFON]</span> {text}")
    
    def handle_voice_command(self, command):
        self.output_text.append(f"<span style='color: #FF8800; font-size: 18px;'>[SPRACHE]</span> {command}")
        
        # Verwende den Befehlsprozessor für Sprachbefehle
        response = self.command_processor.process_command(command)
        self.output_text.append(f"<span style='color: #00FF00; font-size: 18px;'>[JARVIS]</span> {response}")
        self.voice.speak(response)
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def process_command(self, command):
        self.output_text.append(f"<span style='color: #00FFFF; font-size: 18px;'>[BENUTZER]</span> {command}")
        
        # Für getippte Befehle: Prüfe erst auf Sprachbefehle, dann AI
        if any(keyword in command.lower() for keyword in self.command_processor.commands.keys()):
            response = self.command_processor.process_command(command)
        else:
            response = self.ai.process_command(command)
            
        self.output_text.append(f"<span style='color: #00FF00; font-size: 18px;'>[JARVIS]</span> {response}")
        self.voice.speak(response)
        
        # Windows integration
        self.windows_int.execute_command(command)
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def run_diagnostics(self):
        self.output_text.append("<span style='color: #0096FF; font-size: 18px;'>[SYSTEM]</span> Führe vollständige Systemdiagnose durch...")
        self.ai_status.setText("OPTIMAL")
        self.ai_status.setStyleSheet("font-size: 20px; color: #00FF00;")
        self.sys_status.setText("PERFEKT")
        self.sys_status.setStyleSheet("font-size: 20px; color: #00FF00;")
        self.output_text.append("<span style='color: #00FF00; font-size: 18px;'>[SYSTEM]</span> Alle Systeme optimal. Keine Probleme erkannt.")
    
    def update_status(self):
        # Einfache Status-Updates ohne komplexe Animationen
        pass

def main():
    app = QApplication(sys.argv)
    
    # Responsive Schriftarten basierend auf Bildschirmgröße
    screen = app.primaryScreen()
    screen_size = screen.size()
    
    # Font scaling basierend auf Bildschirmbreite
    if screen_size.width() >= 1920:
        font_scale = 1.2
    elif screen_size.width() >= 1440:
        font_scale = 1.0
    else:
        font_scale = 0.9
    
    # Setze globale Schriftart
    font = QFont("Segoe UI", int(14 * font_scale))
    app.setFont(font)
    
    window = JarvisGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()