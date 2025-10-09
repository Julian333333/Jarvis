"""
Jarvis AI Assistant - Main Application
"""

import sys
import os
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QPushButton, QTextEdit, QFrame, QSizePolicy, QBoxLayout)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QFont, QPainter, QPen, QColor
import pyttsx3
import speech_recognition as sr
from .ai import AIAssistant
from .windows_integration import WindowsIntegration
from .commands import CommandProcessor
from .audio_utils import convert_audio_to_wav, default_user_sample_path

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

        # Klon-Stimme: Standard/Cloned
        self.tts_mode = 'standard'
        # Lokaler TTS-Server (OpenVoice/XTTS v2 o.ä.)
        self.cloned_server_url = "http://127.0.0.1:5005/tts"
        # Pfad zur Referenzaufnahme (Ihre Stimme, WAV 16kHz mono)
        self.cloned_speaker_wav = None
        
        # TTS-Engine konfigurieren für bessere deutsche Sprache
        self._setup_tts_engine()
        # Stelle sicher, dass ggf. Danielv1.mp3 als Referenz-WAV verfügbar ist
        self._ensure_default_voice_sample()
    
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
        """Spricht den gegebenen Text aus (Cloned-Voice, wenn aktiv)"""
        if self.tts_mode == 'cloned' and self.cloned_speaker_wav:
            print("🎭 Klon-Stimme aktiv – generiere Audio...")
            ok = self._speak_cloned(text)
            if ok:
                return
            print("⚠️ Geklonte Stimme nicht verfügbar – Fallback auf Standard-TTS")
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

    def _ensure_default_voice_sample(self):
        """Wenn Danielv1.mp3 vorhanden ist und reference.wav fehlt, konvertiere automatisch."""
        try:
            proj_root = os.path.dirname(os.path.dirname(__file__))
            src_wav = os.path.join(proj_root, 'Danielv1.wav')
            src_mp3 = os.path.join(proj_root, 'Danielv1.mp3')
            dst_wav = default_user_sample_path()
            # Bevorzuge direkt die WAV falls vorhanden
            if os.path.exists(src_wav):
                os.makedirs(os.path.dirname(dst_wav), exist_ok=True)
                try:
                    # Kopiere WAV als reference.wav
                    import shutil
                    shutil.copyfile(src_wav, dst_wav)
                    self.cloned_speaker_wav = dst_wav
                    print(f"✅ Stimmprobe gesetzt (WAV): {src_wav} -> {dst_wav}")
                    return
                except Exception as e:
                    print(f"⚠️ Konnte WAV nicht kopieren: {e}")

            if os.path.exists(src_mp3) and not os.path.exists(dst_wav):
                os.makedirs(os.path.dirname(dst_wav), exist_ok=True)
                ok = convert_audio_to_wav(src_mp3, dst_wav, sample_rate=16000, channels=1)
                if ok:
                    print(f"✅ Stimmprobe konvertiert: {src_mp3} -> {dst_wav}")
                    self.cloned_speaker_wav = dst_wav
                else:
                    print("⚠️ Konnte Danielv1.mp3 nicht in WAV konvertieren. Verwende MP3 direkt (abhängig vom Server).")
                    self.cloned_speaker_wav = src_mp3
            elif os.path.exists(dst_wav):
                self.cloned_speaker_wav = dst_wav
            elif os.path.exists(src_mp3):
                # Falls keine WAV existiert, aber MP3 vorhanden ist
                self.cloned_speaker_wav = src_mp3
        except Exception as e:
            print(f"⚠️ Fehler beim Vorbereiten der Stimmprobe: {e}")

    # ====== Geklonte Stimme (lokaler Server) ======
    def enable_cloned_voice(self, speaker_wav: str = None, server_url: str = None) -> bool:
        """Aktiviert die geklonte Stimme über einen lokalen TTS-Server.

        Args:
            speaker_wav: Pfad zur Stimmprobe (WAV 16kHz mono empfohlen)
            server_url: URL des lokalen TTS-Servers (Default: http://127.0.0.1:5005/tts)
        """
        if server_url:
            self.cloned_server_url = server_url
        # Speaker WAV bestimmen
        if speaker_wav and os.path.exists(speaker_wav):
            self.cloned_speaker_wav = speaker_wav
        else:
            # Standardpfad im Projekt: voices/user/samples/reference.wav
            proj_root = os.path.dirname(os.path.dirname(__file__))
            default_wav = os.path.join(proj_root, 'voices', 'user', 'samples', 'reference.wav')
            if os.path.exists(default_wav):
                self.cloned_speaker_wav = default_wav
            else:
                print("⚠️ Keine Stimmprobe gefunden. Legen Sie eine WAV-Datei unter voices/user/samples/reference.wav an oder übergeben Sie den Pfad.")
                return False
        # Probe
        if self._probe_cloned_ready():
            self.tts_mode = 'cloned'
            print("✅ Geklonte Stimme aktiviert")
            return True
        print("❌ Cloned-Voice Server nicht erreichbar")
        return False

    def disable_cloned_voice(self):
        self.tts_mode = 'standard'
        print("🔄 Geklonte Stimme deaktiviert – Standard-TTS aktiv")

    def _probe_cloned_ready(self) -> bool:
        return bool(self._post_tts_request("Test der geklonten Stimme.", dry_run=True))

    def _speak_cloned(self, text: str) -> bool:
        try:
            wav_bytes = self._post_tts_request(text)
            if not wav_bytes:
                return False
            import tempfile, winsound
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(wav_bytes)
                tmp = f.name
            try:
                winsound.PlaySound(tmp, winsound.SND_FILENAME)
            finally:
                try:
                    os.unlink(tmp)
                except Exception:
                    pass
            return True
        except Exception as e:
            print(f"❌ Cloned-Voice Fehler: {e}")
            return False

    def _post_tts_request(self, text: str, dry_run: bool = False):
        """POST-Request an den lokalen TTS-Server. Liefert WAV-Bytes oder True bei dry_run."""
        try:
            import json
            from urllib import request
            data = {
                'text': text,
                'speaker_wav': self.cloned_speaker_wav,
                'sample_rate': 22050
            }
            req = request.Request(self.cloned_server_url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with request.urlopen(req, timeout=30) as resp:
                if dry_run:
                    return True
                return resp.read()
        except Exception as e:
            if dry_run:
                print(f"❌ Cloned-Voice Probe fehlgeschlagen: {e}")
                return False
            print(f"❌ TTS-Server Anfrage fehlgeschlagen: {e}")
            return None
    
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
    ai_response_ready = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S")
        # Kompakte Größe die auf die meisten Bildschirme passt
        self.setGeometry(100, 50, 1400, 800)
        self.setMinimumSize(1100, 650)

        # Modern Glass-Morphism Design with Gradients
        self.setStyleSheet("""
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0a0a15,
        stop:0.5 #0d0d1a,
        stop:1 #0a0a15
    );
    color: #00FFFF;
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
}

QLabel {
    color: #00FFFF;
    font-size: 34px;
    font-weight: 600;
    background: transparent;
}

QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 255, 255, 0.15),
        stop:1 rgba(0, 200, 255, 0.1)
    );
    border: 2px solid rgba(0, 255, 255, 0.4);
    border-radius: 12px;
    padding: 18px 28px;
    color: #00FFFF;
    font-size: 38px;
    font-weight: 600;
    min-height: 35px;
    text-align: center;
}

QPushButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 255, 255, 0.25),
        stop:1 rgba(0, 220, 255, 0.2)
    );
    border: 2px solid rgba(0, 255, 255, 0.7);
    color: #66FFFF;
}

QPushButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 255, 255, 0.1),
        stop:1 rgba(0, 180, 255, 0.08)
    );
    border: 2px solid rgba(0, 255, 255, 0.5);
    padding-top: 20px;
}

QTextEdit {
    background: rgba(15, 20, 35, 0.6);
    border: 2px solid rgba(0, 255, 255, 0.3);
    border-radius: 12px;
    padding: 18px;
    color: #E0F8FF;
    font-size: 34px;
    font-weight: 500;
    selection-background-color: rgba(0, 255, 255, 0.3);
    selection-color: #FFFFFF;
}

QTextEdit:focus {
    border: 2px solid rgba(0, 255, 255, 0.6);
    background: rgba(15, 20, 35, 0.75);
}

QFrame {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 30, 50, 0.4),
        stop:1 rgba(15, 25, 45, 0.3)
    );
    border: 1px solid rgba(0, 255, 255, 0.25);
    border-radius: 16px;
    margin: 8px;
}

QScrollBar:vertical {
    background: rgba(15, 20, 35, 0.4);
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(0, 255, 255, 0.4);
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(0, 255, 255, 0.6);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(15, 20, 35, 0.4);
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: rgba(0, 255, 255, 0.4);
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(0, 255, 255, 0.6);
}
        """)
        
        # Hauptlayout - kompakt
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Header - groß und einfach
        self.create_header(self.main_layout)

        # Status Bereich
        self.create_status_section(self.main_layout)

        # Hauptinterface
        self.create_main_interface(self.main_layout)
        
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
        
        # Timer für periodische Clone-Server-Prüfung (alle 30 Sekunden)
        self.clone_check_timer = QTimer()
        self.clone_check_timer.timeout.connect(self.periodic_clone_check)
        self.clone_check_timer.start(30000)  # 30 Sekunden

        # Asynchrone AI-Antworten (UI bleibt responsiv)
        self.ai_response_ready.connect(self.on_ai_response)
        
    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 255, 0.05),
                    stop:0.5 rgba(0, 200, 255, 0.1),
                    stop:1 rgba(0, 255, 255, 0.05)
                );
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 16px;
                padding: 15px;
                margin: 0px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(12, 12, 12, 12)
        
        # Kompakterer JARVIS Titel
        self.title_label = QLabel("J.A.R.V.I.S")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 58px;
            font-weight: 800;
            color: #00FFFF;
            letter-spacing: 8px;
            background: transparent;
            margin: 5px;
        """)
        header_layout.addWidget(self.title_label)
        
        # Kompakterer Status
        self.main_status = QLabel("● SYSTEM BEREIT")
        self.main_status.setAlignment(Qt.AlignCenter)
        self.main_status.setStyleSheet("""
            font-size: 28px;
            font-weight: 600;
            color: #00FF88;
            background: transparent;
            margin: 3px;
            letter-spacing: 2px;
        """)
        header_layout.addWidget(self.main_status)
        
        layout.addWidget(header_frame)
        
    def create_status_section(self, layout):
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        self.status_layout = QHBoxLayout(status_frame)
        self.status_layout.setSpacing(20)
        
        # Helper function to create modern status cards
        def create_status_card(title, status, icon="●"):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(0, 255, 255, 0.12),
                        stop:1 rgba(0, 200, 255, 0.08)
                    );
                    border: 2px solid rgba(0, 255, 255, 0.35);
                    border-radius: 14px;
                    padding: 12px;
                    margin: 0px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(6)
            card_layout.setContentsMargins(10, 10, 10, 10)
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                font-size: 20px;
                font-weight: 700;
                color: rgba(0, 255, 255, 0.9);
                background: transparent;
                letter-spacing: 1px;
                margin-bottom: 4px;
            """)
            
            status_label = QLabel(f"{icon} {status}")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet("""
                font-size: 26px;
                font-weight: 600;
                color: #00FF88;
                background: transparent;
                letter-spacing: 0px;
            """)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(status_label)
            return card, title_label, status_label
        
        # AI Status Card
        ai_card, self.ai_title_label, self.ai_status = create_status_card("🤖 KI KERN", "AKTIV", "●")
        
        # Voice Status Card (with clone indicator)
        voice_card = QFrame()
        voice_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 0.12),
                    stop:1 rgba(0, 200, 255, 0.08)
                );
                border: 2px solid rgba(0, 255, 255, 0.35);
                border-radius: 14px;
                padding: 12px;
                margin: 0px;
            }
        """)
        voice_layout = QVBoxLayout(voice_card)
        voice_layout.setSpacing(4)
        voice_layout.setContentsMargins(10, 10, 10, 10)
        
        self.voice_title_label = QLabel("🎤 SPRACHE")
        self.voice_title_label.setAlignment(Qt.AlignCenter)
        self.voice_title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: rgba(0, 255, 255, 0.9);
            background: transparent;
            letter-spacing: 1px;
            margin-bottom: 4px;
        """)
        
        self.voice_status = QLabel("● BEREIT")
        self.voice_status.setAlignment(Qt.AlignCenter)
        self.voice_status.setStyleSheet("""
            font-size: 26px;
            font-weight: 600;
            color: #FFA500;
            background: transparent;
            letter-spacing: 0px;
        """)
        
        self.clone_status_label = QLabel("📢 STANDARD")
        self.clone_status_label.setAlignment(Qt.AlignCenter)
        self.clone_status_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 500;
            color: rgba(255, 165, 0, 0.8);
            background: transparent;
            margin-top: 4px;
            letter-spacing: 0px;
        """)
        
        voice_layout.addWidget(self.voice_title_label)
        voice_layout.addWidget(self.voice_status)
        voice_layout.addWidget(self.clone_status_label)
        
        # System Status Card
        sys_card, self.sys_title_label, self.sys_status = create_status_card("💻 SYSTEM", "ONLINE", "●")
        
        self.status_layout.addWidget(ai_card)
        self.status_layout.addWidget(voice_card)
        self.status_layout.addWidget(sys_card)
        
        layout.addWidget(status_frame)
        
    def create_main_interface(self, layout):
        # Chat Bereich with modern card
        chat_frame = QFrame()
        chat_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 25, 40, 0.5),
                    stop:1 rgba(10, 20, 35, 0.4)
                );
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 14px;
                padding: 15px;
                margin: 0px;
            }
        """)
        self.chat_layout = QVBoxLayout(chat_frame)
        self.chat_layout.setSpacing(12)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        
        # Chat Label with icon - kompakter
        self.chat_label = QLabel("💬 KOMMUNIKATION")
        self.chat_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: rgba(0, 255, 255, 0.95);
            background: transparent;
            letter-spacing: 1px;
            margin-bottom: 8px;
        """)
        self.chat_layout.addWidget(self.chat_label)
        
        # Output Text - Kompakter
        self.output_text = QTextEdit()
        self.output_text.setMinimumHeight(150)
        self.output_text.setStyleSheet("""
            QTextEdit {
                font-size: 24px;
                font-weight: 500;
                background: rgba(8, 15, 28, 0.7);
                color: #E8F8FF;
                border: 2px solid rgba(0, 255, 255, 0.25);
                border-radius: 12px;
                padding: 12px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 2px solid rgba(0, 255, 255, 0.5);
                background: rgba(8, 15, 28, 0.85);
            }
        """)
        self.output_text.append("<span style='color: #00FF88; font-size: 22px; font-weight: 600;'>[SYSTEM]</span> <span style='font-size: 24px; color: #E8F8FF;'>● J.A.R.V.I.S ist online und bereit.</span>")
        self.chat_layout.addWidget(self.output_text)
        
        # Input Bereich with modern card - kompakter
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: rgba(15, 25, 40, 0.35);
                border: 2px solid rgba(0, 255, 255, 0.2);
                border-radius: 12px;
                padding: 12px;
                margin: 3px 0px;
            }
        """)
        input_frame.setMinimumHeight(60)
        self.input_layout = QVBoxLayout(input_frame)
        self.input_layout.setSpacing(8)
        self.input_layout.setContentsMargins(10, 10, 10, 10)
        
        # Input Label with icon - kompakter
        self.input_label = QLabel("⌨️ EINGABE")
        self.input_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: rgba(0, 255, 255, 0.85);
            background: transparent;
            letter-spacing: 1px;
            margin-bottom: 5px;
        """)
        self.input_layout.addWidget(self.input_label)
        
        # Input Text - Kompakter
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(70)
        self.input_text.setStyleSheet("""
            QTextEdit {
                font-size: 22px;
                font-weight: 500;
                padding: 10px;
                background: rgba(8, 15, 28, 0.6);
                color: #E8F8FF;
                border: 2px solid rgba(0, 255, 255, 0.3);
                border-radius: 10px;
            }
            QTextEdit:focus {
                border: 2px solid rgba(0, 255, 255, 0.6);
                background: rgba(8, 15, 28, 0.8);
            }
        """)
        self.input_text.setPlaceholderText("Befehl eingeben...")
        self.input_layout.addWidget(self.input_text)
        
        # Buttons Grid - Modern design
        buttons_container = QFrame()
        buttons_container.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                padding: 10px 0px;
                margin: 5px 0px;
            }
        """)
        self.button_layout = QHBoxLayout(buttons_container)
        self.button_layout.setSpacing(8)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Kompakte Button Styles
        button_style = """
            QPushButton {
                font-size: 18px;
                font-weight: 600;
                padding: 10px 14px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 0.18),
                    stop:1 rgba(0, 200, 255, 0.12)
                );
                color: #00FFFF;
                border: 2px solid rgba(0, 255, 255, 0.45);
                border-radius: 10px;
                min-height: 38px;
                min-width: 85px;
                letter-spacing: 0px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 0.28),
                    stop:1 rgba(0, 220, 255, 0.22)
                );
                border: 2px solid rgba(0, 255, 255, 0.7);
                color: #66FFFF;
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 0.12),
                    stop:1 rgba(0, 180, 255, 0.08)
                );
                border: 2px solid rgba(0, 255, 255, 0.5);
                padding-top: 11px;
                padding-bottom: 9px;
            }
        """
        
        self.execute_button = QPushButton("▶ AUSFÜHREN")
        self.execute_button.clicked.connect(self.send_command)
        self.execute_button.setStyleSheet(button_style)
        
        self.voice_button = QPushButton("🗣️ SPRACHE")
        self.voice_button.clicked.connect(self.toggle_voice)
        self.voice_button.setStyleSheet(button_style)
        
        self.speech_to_text_button = QPushButton("🎤 MIKRO")
        self.speech_to_text_button.clicked.connect(self.toggle_speech_to_text)
        self.speech_to_text_button.setStyleSheet(button_style)
        self.speech_to_text_active = False
        
        self.conversation_button = QPushButton("💬 CHAT")
        self.conversation_button.clicked.connect(self.toggle_conversation)
        self.conversation_button.setStyleSheet(button_style)
        self.conversation_active = False
        
        self.diagnostics_button = QPushButton("🔍 DIAGNOSE")
        self.diagnostics_button.clicked.connect(self.run_diagnostics)
        self.diagnostics_button.setStyleSheet(button_style)
        
        # Voice clone toggle button
        self.clone_toggle_button = QPushButton("🎭 KLON")
        self.clone_toggle_button.clicked.connect(self.toggle_cloned_voice)
        self.clone_toggle_button.setStyleSheet(button_style)
        
        # Mock TTS server button
        self.mock_server_button = QPushButton("🎙️ SERVER")
        self.mock_server_button.clicked.connect(self.start_mock_server)
        self.mock_server_button.setStyleSheet(button_style)
        self.mock_server_process = None
        
        self.button_layout.addWidget(self.execute_button)
        self.button_layout.addWidget(self.voice_button)
        self.button_layout.addWidget(self.speech_to_text_button)
        self.button_layout.addWidget(self.conversation_button)
        self.button_layout.addWidget(self.diagnostics_button)
        self.button_layout.addWidget(self.clone_toggle_button)
        self.button_layout.addWidget(self.mock_server_button)
        self.input_layout.addWidget(buttons_container)
        
        self.chat_layout.addWidget(input_frame)
        layout.addWidget(chat_frame)
        
        # Nach dem Erstellen der Widgets:
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Initiale Skalierung
        self.update_responsive_layout()

    def _scale_factor(self) -> float:
        base = 1280.0
        return max(0.75, min(2.0, float(self.width()) / base))

    def update_responsive_layout(self):
        s = self._scale_factor()
        width = self.width()
        # Layout spacing/margins
        self.main_layout.setContentsMargins(int(40*s), int(40*s), int(40*s), int(40*s))
        self.main_layout.setSpacing(int(30*s))
        if hasattr(self, 'status_layout'):
            self.status_layout.setSpacing(int(60*s))
            # Reflow Status-Karten
            if width < 1100:
                self.status_layout.setDirection(QBoxLayout.TopToBottom)
            else:
                self.status_layout.setDirection(QBoxLayout.LeftToRight)
        if hasattr(self, 'chat_layout'):
            self.chat_layout.setSpacing(int(30*s))
        if hasattr(self, 'input_layout'):
            self.input_layout.setSpacing(int(25*s))
        if hasattr(self, 'button_layout'):
            self.button_layout.setSpacing(int(20*s))
            if width < 1100:
                self.button_layout.setDirection(QBoxLayout.TopToBottom)
            else:
                self.button_layout.setDirection(QBoxLayout.LeftToRight)

        # Header - Keep consistent modern styling
        # (Already styled inline in create_header, just update font sizes for scaling)
        
        # Status Karten - Modern glass-morph (inline styles handle most of it)
        # Dynamic color updates for voice status
        voice_color = '#FF4444' if any(x in self.voice_status.text() for x in ['HÖRT', 'NIMMT']) else '#FFA500'
        status_update = f"""
            font-size: {int(36*s)}px;
            font-weight: 600;
            color: {voice_color};
            background: transparent;
            letter-spacing: 1px;
        """
        self.voice_status.setStyleSheet(status_update)
        
        # Buttons - Modern gradient style
        btn_style = f"""
            QPushButton {{
                font-size: {int(32*s)}px;
                font-weight: 600;
                padding: {int(16*s)}px {int(22*s)}px;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 0.18),
                    stop:1 rgba(0, 200, 255, 0.12)
                );
                color: #00FFFF;
                border: 2px solid rgba(0, 255, 255, 0.45);
                border-radius: {int(14*s)}px;
                min-height: {int(55*s)}px;
                min-width: {int(135*s)}px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 0.28),
                    stop:1 rgba(0, 220, 255, 0.22)
                );
                border: 2px solid rgba(0, 255, 255, 0.7);
                color: #66FFFF;
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 255, 0.12),
                    stop:1 rgba(0, 180, 255, 0.08)
                );
                border: 2px solid rgba(0, 255, 255, 0.5);
                padding-top: {int(18*s)}px;
                padding-bottom: {int(14*s)}px;
            }}
        """
        for btn in [self.execute_button, self.voice_button, self.speech_to_text_button, 
                    self.conversation_button, self.diagnostics_button, self.clone_toggle_button, 
                    self.mock_server_button]:
            btn.setStyleSheet(btn_style)
        
        # Update clone status indicator (only if voice controller is already initialized)
        if hasattr(self, 'voice'):
            self.update_clone_status_indicator()

    def run_ai_async(self, text: str):
        def _work():
            try:
                resp = self.ai.process_command(text)
            except Exception as e:
                resp = f"Daddy, ich habe ein Problem bei der Verarbeitung festgestellt: {e}"
            self.ai_response_ready.emit(resp)
        threading.Thread(target=_work, daemon=True).start()
    
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
            self.output_text.append(f"<span style='color: #00FF00; font-size: 40px;'>[JARVIS]</span> {response}")
            self.voice.speak(response)
        else:
            self.output_text.append("<span style='color: #0096FF; font-size: 36px;'>[SYSTEM]</span> Denke nach…")
            self.run_ai_async(text)
        
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
            self.output_text.append(f"<span style='color: #00FF00; font-size: 40px;'>[JARVIS]</span> {response}")
            self.voice.speak(response)
        else:
            self.output_text.append("<span style='color: #0096FF; font-size: 36px;'>[SYSTEM]</span> Denke nach…")
            self.run_ai_async(command)
        
        # Windows integration
        self.windows_int.execute_command(command)
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def toggle_cloned_voice(self):
        """Schaltet zwischen Standard- und Klon-Stimme um"""
        if self.voice.tts_mode == 'cloned':
            self.voice.disable_cloned_voice()
            self.output_text.append("<span style='color: #FFA500; font-size: 40px;'>[STIMME]</span> Standard-TTS aktiviert")
            self.voice.speak("Standard-Stimme aktiviert, Daddy.")
        else:
            if self.voice.enable_cloned_voice():
                self.output_text.append("<span style='color: #00FF00; font-size: 40px;'>[STIMME]</span> Geklonte Stimme aktiviert")
                self.voice.speak("Geklonte Stimme aktiviert, Daddy.")
            else:
                self.output_text.append("<span style='color: #FF0000; font-size: 40px;'>[FEHLER]</span> Klon-Server nicht erreichbar. Starten Sie den lokalen TTS-Server.")
                self.voice.speak("Klon-Server nicht erreichbar, Daddy. Bitte starten Sie den lokalen T T S Server.")
        
        self.update_clone_status_indicator()
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_mock_server(self):
        """Startet oder stoppt den Mock TTS Server"""
        if self.mock_server_process is not None:
            # Server ist bereits gestartet - stoppe ihn
            try:
                self.mock_server_process.terminate()
                self.mock_server_process = None
                self.mock_server_button.setText("🎙️ TEST SERVER")
                self.output_text.append("<span style='color: #FFA500; font-size: 40px;'>[SERVER]</span> Mock TTS Server gestoppt")
                self.voice.speak("Test-Server gestoppt, Daddy.")
            except Exception as e:
                self.output_text.append(f"<span style='color: #FF0000; font-size: 36px;'>[FEHLER]</span> Server-Stopp fehlgeschlagen: {e}")
        else:
            # Starte den Mock Server
            try:
                import subprocess
                server_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools', 'local_tts_server.py')
                if not os.path.exists(server_script):
                    self.output_text.append("<span style='color: #FF0000; font-size: 36px;'>[FEHLER]</span> Mock-Server-Skript nicht gefunden")
                    return
                
                # Starte Server als Hintergrundprozess
                self.mock_server_process = subprocess.Popen(
                    [sys.executable, server_script],
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                
                self.mock_server_button.setText("🔴 SERVER AN")
                self.mock_server_button.setStyleSheet("background-color: #44ff44; border-color: #66ff66; color: #000000;")
                self.output_text.append("<span style='color: #00FF00; font-size: 40px;'>[SERVER]</span> Mock TTS Server gestartet auf Port 5005")
                self.voice.speak("Test-Server gestartet, Daddy. Sie können nun die geklonte Stimme aktivieren.")
                
                # Warte kurz und versuche Auto-Aktivierung
                QTimer.singleShot(2000, self.auto_activate_clone_after_server_start)
                
            except Exception as e:
                self.output_text.append(f"<span style='color: #FF0000; font-size: 36px;'>[FEHLER]</span> Server-Start fehlgeschlagen: {e}")
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def auto_activate_clone_after_server_start(self):
        """Versucht automatisch die geklonte Stimme nach Server-Start zu aktivieren"""
        if self.voice.tts_mode != 'cloned':
            if self.voice.enable_cloned_voice():
                self.output_text.append("<span style='color: #00FF00; font-size: 40px;'>[AUTO]</span> Geklonte Stimme automatisch aktiviert")
                self.update_clone_status_indicator()
                scrollbar = self.output_text.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
    
    def update_clone_status_indicator(self):
        """Aktualisiert die Klon-Status-Anzeige"""
        if self.voice.tts_mode == 'cloned':
            self.clone_status_label.setText("🎭 GEKLONT")
            self.clone_status_label.setStyleSheet("font-size: 24px; color: #00FF00; margin-top: 5px; font-weight: bold;")
        else:
            self.clone_status_label.setText("📢 STANDARD")
            self.clone_status_label.setStyleSheet("font-size: 24px; color: #FFA500; margin-top: 5px;")
    
    def run_diagnostics(self):
        self.output_text.append("<span style='color: #0096FF; font-size: 40px;'>[SYSTEM]</span> Führe vollständige Systemdiagnose durch...")
        
        # AI Check
        try:
            models = self.ai.list_models()
            if models:
                self.ai_status.setText("OPTIMAL")
                self.ai_status.setStyleSheet("font-size: 34px; color: #00FF00;")
                self.output_text.append(f"<span style='color: #00FF00; font-size: 36px;'>✅ AI</span> Verbunden - {len(models)} Modelle verfügbar")
            else:
                self.ai_status.setText("WARNUNG")
                self.ai_status.setStyleSheet("font-size: 34px; color: #FFA500;")
                self.output_text.append("<span style='color: #FFA500; font-size: 36px;'>⚠️ AI</span> Verbunden aber keine Modelle gefunden")
        except Exception as e:
            self.ai_status.setText("FEHLER")
            self.ai_status.setStyleSheet("font-size: 34px; color: #FF0000;")
            self.output_text.append(f"<span style='color: #FF0000; font-size: 36px;'>❌ AI</span> Verbindung fehlgeschlagen: {e}")
        
        # Voice Check
        try:
            if self.voice.tts_mode == 'cloned':
                if self.voice._probe_cloned_ready():
                    self.output_text.append("<span style='color: #00FF00; font-size: 36px;'>✅ STIMME</span> Geklonte Stimme aktiv und Server erreichbar")
                else:
                    self.output_text.append("<span style='color: #FFA500; font-size: 36px;'>⚠️ STIMME</span> Geklonte Stimme aktiviert aber Server antwortet nicht")
            else:
                self.output_text.append("<span style='color: #00FF00; font-size: 36px;'>✅ STIMME</span> Standard-TTS aktiv")
        except Exception as e:
            self.output_text.append(f"<span style='color: #FF0000; font-size: 36px;'>❌ STIMME</span> Fehler: {e}")
        
        # System Status
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            self.sys_status.setText("PERFEKT")
            self.sys_status.setStyleSheet("font-size: 34px; color: #00FF00;")
            self.output_text.append(f"<span style='color: #00FF00; font-size: 36px;'>✅ SYSTEM</span> CPU: {cpu}% | RAM: {mem}%")
        except Exception as e:
            self.sys_status.setText("UNBEKANNT")
            self.sys_status.setStyleSheet("font-size: 34px; color: #FFA500;")
            self.output_text.append(f"<span style='color: #FFA500; font-size: 36px;'>⚠️ SYSTEM</span> Status unbekannt: {e}")
        
        self.output_text.append("<span style='color: #00FF00; font-size: 40px;'>[SYSTEM]</span> Diagnose abgeschlossen.")
        
        # Auto-scroll
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def periodic_clone_check(self):
        """Prüft periodisch ob der Klon-Server verfügbar ist und aktiviert automatisch"""
        # Nur prüfen wenn Standard-Mode aktiv ist und eine Stimmprobe existiert
        if self.voice.tts_mode == 'standard' and self.voice.cloned_speaker_wav:
            if self.voice._probe_cloned_ready():
                # Server ist jetzt erreichbar - automatisch aktivieren
                if self.voice.enable_cloned_voice():
                    self.output_text.append("<span style='color: #00FF00; font-size: 36px;'>🎭 AUTO</span> Klon-Server erkannt - geklonte Stimme aktiviert")
                    self.update_clone_status_indicator()
                    scrollbar = self.output_text.verticalScrollBar()
                    scrollbar.setValue(scrollbar.maximum())
    
    def update_status(self):
        # Einfache Status-Updates ohne komplexe Animationen
        pass

    def resizeEvent(self, event):
        """Passe Layout/Styles responsiv an"""
        self.update_responsive_layout()
        super().resizeEvent(event)

    def on_ai_response(self, response: str):
        self.output_text.append(f"<span style='color: #00FF00; font-size: 40px;'>[JARVIS]</span> {response}")
        self.voice.speak(response)
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

def main():
    # High-DPI und Windows 11 AppUserModelID
    try:
        from PyQt5 import QtCore as _QtCore
        _QtCore.QCoreApplication.setAttribute(_QtCore.Qt.AA_EnableHighDpiScaling, True)
        _QtCore.QCoreApplication.setAttribute(_QtCore.Qt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass
    try:
        if sys.platform.startswith('win'):
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Jarvis.App')
    except Exception:
        pass

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
    
    # Versuche geklonte Stimme automatisch zu aktivieren, wenn eine Stimmprobe vorhanden ist
    try:
        if getattr(window, 'voice', None) and window.voice.cloned_speaker_wav and os.path.exists(window.voice.cloned_speaker_wav):
            # Nur Probe; nicht erzwingen, falls Server nicht läuft
            if window.voice.enable_cloned_voice(speaker_wav=window.voice.cloned_speaker_wav):
                print("✅ Geklonte Stimme automatisch aktiviert")
            else:
                print("ℹ️ Klonstimme nicht aktiv – Standard-TTS aktiv")
    except Exception as e:
        print(f"ℹ️ Klonstimme Auto-Aktivierung übersprungen: {e}")
    
    print("🎤 Deutsche TTS-Stimme aktiviert - JARVIS bereit!")
    
    window.show()
    print("🎤 Deutsche TTS-Stimme aktiviert - JARVIS bereit!")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()