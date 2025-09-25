"""
Jarvis AI Assistant - Main Application
"""

import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QTextEdit, QFrame, QProgressBar)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QPropertyAnimation, QRect, Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush, QLinearGradient
import pyttsx3
import speech_recognition as sr
from .ai import AIAssistant
from .windows_integration import WindowsIntegration

class VoiceController(QObject):
    command_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.listening = False
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
                    text = self.recognizer.recognize_google(audio).lower()
                    if self.activation_word in text:
                        self.speak("Yes, sir?")
                        self.command_received.emit(text.replace(self.activation_word, "").strip())
                        break
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    continue
    
    def start_listening(self):
        self.listening = True
        threading.Thread(target=self.listen_for_activation, daemon=True).start()
    
    def stop_listening(self):
        self.listening = False

class JarvisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S - Just A Rather Very Intelligent System")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0a0a0a, stop: 1 #1a1a1a);
                color: #00d4ff;
                border: 2px solid #00d4ff;
            }
            QLabel {
                color: #00d4ff;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #004d66, stop: 1 #002633);
                color: #00d4ff;
                border: 2px solid #00d4ff;
                border-radius: 15px;
                padding: 10px 20px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0066cc, stop: 1 #003366);
                border: 2px solid #66ddff;
                color: #66ddff;
            }
            QPushButton:pressed {
                background: #001a33;
            }
            QTextEdit {
                background: rgba(0, 20, 40, 0.8);
                color: #00d4ff;
                border: 2px solid #00d4ff;
                border-radius: 10px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                selection-background-color: #004d66;
            }
            QFrame {
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid #00d4ff;
                border-radius: 15px;
            }
            QProgressBar {
                background: rgba(0, 20, 40, 0.8);
                border: 2px solid #00d4ff;
                border-radius: 10px;
                text-align: center;
                color: #00d4ff;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00d4ff, stop: 1 #66ddff);
                border-radius: 8px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header Frame
        header_frame = QFrame()
        header_frame.setFixedHeight(120)
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("J.A.R.V.I.S")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 5px;
        """)
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Just A Rather Very Intelligent System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #66ddff;
            font-style: italic;
        """)
        header_layout.addWidget(subtitle_label)
        
        # Status with animated indicator
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            color: #00ff00;
            font-size: 20px;
            margin-right: 10px;
        """)
        self.status_label = QLabel("System Online - Ready for Commands")
        self.status_label.setStyleSheet("""
            color: #00ff00;
            font-size: 14px;
            font-weight: bold;
        """)
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        header_layout.addLayout(status_layout)
        
        main_layout.addWidget(header_frame)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # AI Status
        ai_status_label = QLabel("AI STATUS")
        ai_status_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(ai_status_label)
        
        self.ai_status_bar = QProgressBar()
        self.ai_status_bar.setRange(0, 100)
        self.ai_status_bar.setValue(85)
        self.ai_status_bar.setFormat("Neural Network: 85%")
        left_layout.addWidget(self.ai_status_bar)
        
        # Voice Control Section
        voice_label = QLabel("VOICE CONTROL")
        voice_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        left_layout.addWidget(voice_label)
        
        self.voice_button = QPushButton("🎤 ACTIVATE VOICE")
        self.voice_button.setFixedHeight(50)
        self.voice_button.clicked.connect(self.toggle_voice)
        left_layout.addWidget(self.voice_button)
        
        # System Controls
        system_label = QLabel("SYSTEM CONTROLS")
        system_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        left_layout.addWidget(system_label)
        
        self.diagnostic_button = QPushButton("🔧 RUN DIAGNOSTICS")
        self.diagnostic_button.setFixedHeight(40)
        self.diagnostic_button.clicked.connect(self.run_diagnostics)
        left_layout.addWidget(self.diagnostic_button)
        
        self.settings_button = QPushButton("⚙️ SETTINGS")
        self.settings_button.setFixedHeight(40)
        left_layout.addWidget(self.settings_button)
        
        left_layout.addStretch()
        content_layout.addWidget(left_panel)
        
        # Right panel - Main interface
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Output area
        output_label = QLabel("SYSTEM OUTPUT")
        output_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(350)
        self.output_text.append("JARVIS v1.0 - System Initialized")
        self.output_text.append("All systems operational. Awaiting instructions...")
        right_layout.addWidget(self.output_text)
        
        # Input area
        input_label = QLabel("COMMAND INPUT")
        input_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        right_layout.addWidget(input_label)
        
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(80)
        self.input_text.setPlaceholderText("Enter your command here...")
        right_layout.addWidget(self.input_text)
        
        # Send button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.send_button = QPushButton("⚡ EXECUTE COMMAND")
        self.send_button.setFixedHeight(45)
        self.send_button.setFixedWidth(200)
        self.send_button.clicked.connect(self.send_command)
        button_layout.addWidget(self.send_button)
        button_layout.addStretch()
        right_layout.addLayout(button_layout)
        
        content_layout.addWidget(right_panel)
        main_layout.addLayout(content_layout)
        
        # Initialize components
        self.ai = AIAssistant()
        self.windows_int = WindowsIntegration()
        self.voice = VoiceController()
        self.voice.command_received.connect(self.handle_voice_command)
        
        # Animation timer for status indicator
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.animate_status)
        self.blink_timer.start(1000)
        self.blink_state = True
        
        # Status update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
    
    def send_command(self):
        command = self.input_text.toPlainText().strip()
        if command:
            self.process_command(command)
            self.input_text.clear()
    
    def toggle_voice(self):
        if self.voice.listening:
            self.voice.stop_listening()
            self.voice_button.setText("🎤 ACTIVATE VOICE")
            self.voice_button.setStyleSheet(self.voice_button.styleSheet().replace("#00ff00", "#00d4ff"))
            self.status_label.setText("System Online - Voice Control Disabled")
            self.status_label.setStyleSheet("color: #00d4ff; font-size: 14px; font-weight: bold;")
            self.status_indicator.setStyleSheet("color: #00d4ff; font-size: 20px; margin-right: 10px;")
        else:
            self.voice.start_listening()
            self.voice_button.setText("🔴 VOICE ACTIVE")
            self.voice_button.setStyleSheet(self.voice_button.styleSheet().replace("#00d4ff", "#00ff00"))
            self.status_label.setText("System Online - Listening for 'Jarvis'")
            self.status_label.setStyleSheet("color: #00ff00; font-size: 14px; font-weight: bold;")
            self.status_indicator.setStyleSheet("color: #00ff00; font-size: 20px; margin-right: 10px;")
    
    def handle_voice_command(self, command):
        self.output_text.append(f"<span style='color: #66ddff;'>[VOICE INPUT]</span> {command}")
        self.process_command(command)
    
    def process_command(self, command):
        self.output_text.append(f"<span style='color: #00d4ff;'>[USER]</span> {command}")
        self.output_text.append("<span style='color: #ffaa00;'>[PROCESSING]</span> Analyzing command...")
        
        # Simulate processing delay
        QApplication.processEvents()
        
        response = self.ai.process_command(command)
        self.output_text.append(f"<span style='color: #00ff00;'>[JARVIS]</span> {response}")
        self.voice.speak(response)
        
        # Windows integration
        self.windows_int.execute_command(command)
        
        # Scroll to bottom
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
    
    def run_diagnostics(self):
        self.output_text.append("<span style='color: #ffaa00;'>[DIAGNOSTIC]</span> Running system diagnostics...")
        self.ai_status_bar.setValue(95)
        self.ai_status_bar.setFormat("Neural Network: 95%")
        self.output_text.append("<span style='color: #00ff00;'>[DIAGNOSTIC]</span> All systems nominal.")
    
    def animate_status(self):
        if self.blink_state:
            self.status_indicator.setStyleSheet("color: #00ff00; font-size: 20px; margin-right: 10px;")
        else:
            self.status_indicator.setStyleSheet("color: #004400; font-size: 20px; margin-right: 10px;")
        self.blink_state = not self.blink_state
    
    def update_status(self):
        # Update status based on AI and voice status
        if not self.voice.listening:
            self.status_label.setText("System Online - Ready for Commands")
        
        # Simulate AI processing load
        import random
        current_load = self.ai_status_bar.value()
        new_load = max(75, min(100, current_load + random.randint(-5, 5)))
        self.ai_status_bar.setValue(new_load)
        self.ai_status_bar.setFormat(f"Neural Network: {new_load}%")

def main():
    app = QApplication(sys.argv)
    window = JarvisGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()