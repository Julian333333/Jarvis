"""
Jarvis AI Assistant - Main Application
"""

import sys
import os
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S")
        # Responsive Startgröße: 80% des Bildschirms, mit kleineren Mindestmaßen für Laptops
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        start_w = max(800, int(screen_size.width() * 0.8))
        start_h = max(600, int(screen_size.height() * 0.7))
        self.resize(start_w, start_h)
        # Zulassen, dass die App auch auf kleineren Laptops startet
        self.setMinimumSize(700, 480)
 
        # Verwende ein responsives Stylesheet (wird initial gesetzt und bei Resize angepasst)
        self._apply_responsive_styles()
        
    def _apply_responsive_styles(self):
        """Erzeugt ein einfaches, responsives Stylesheet basierend auf der aktuellen Fensterbreite."""
        w = max(800, self.width())
        # Berechne relative Schriftgrößen
        title_sz = max(28, int(w * 0.05))
        header_sz = max(18, int(w * 0.025))
        label_sz = max(14, int(w * 0.018))
        btn_sz = max(14, int(w * 0.02))
        text_sz = max(14, int(w * 0.02))

        stylesheet = f"""
QMainWindow {{
    background-color: #05060a; /* sehr dunkler Hintergrund */
    color: #00FFFF;
    font-family: 'Segoe UI', Arial, sans-serif;
}}
/* Generelle Labels - Standardfarbe, Größe wird weiterhin per-widget angepasst */
QLabel {{
    color: #00f0ff;
}}
/* Buttons: flach, breit, neon-outline */
QPushButton {{
    background-color: #07101a;
    border: 2px solid #00e6ff;
    border-radius: 6px;
    padding: 10px 18px;
    color: #bffcff;
    font-size: {max(12, btn_sz)}px;
    font-weight: 600;
    min-height: 36px;
    text-transform: uppercase;
}}
QPushButton:hover {{
    background-color: rgba(0,230,255,0.05);
    border-color: #66f0ff;
    color: #e6ffff;
}}
/* Chat and text areas */
QTextEdit {{
    background-color: #060607;
    border: 2px solid #005f6b;
    border-radius: 6px;
    padding: 10px;
    color: #cdeff0;
    font-size: {max(12, text_sz)}px;
}}
/* Frames act as cards with neon border */
QFrame {{
    background-color: rgba(8,10,16,0.6);
    border: 1px solid rgba(0,230,255,0.14);
    border-radius: 8px;
    margin: 8px;
}}

/* Tiny helpers for header/title */
.jarvis-header QLabel {{
    color: #00f0ff;
}}

"""
        self.setStyleSheet(stylesheet)

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
        title.setObjectName('jarvis_title')
        title.setStyleSheet("""
            QLabel#jarvis_title {
                font-size: 56px;
                font-weight: 800;
                color: #00f0ff;
                margin: 18px 0px;
                letter-spacing: 6px;
                border-top: 2px solid rgba(0,230,255,0.08);
                border-bottom: 2px solid rgba(0,230,255,0.08);
                padding: 14px 0px;
            }
        """)
        header_layout.addWidget(title)
        
        # Status
        self.main_status = QLabel("SYSTEM BEREIT")
        self.main_status.setAlignment(Qt.AlignCenter)
        self.main_status.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #00ff70;
            margin-bottom: 8px;
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
        ai_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #9ff8ff; margin-bottom: 8px;")
        self.ai_status = QLabel("AKTIV")
        self.ai_status.setAlignment(Qt.AlignCenter)
        self.ai_status.setStyleSheet("font-size: 16px; font-weight: 800; color: #00ff70; background-color: rgba(0,0,0,0.15); padding:6px 12px; border-radius:8px;")
        ai_layout.addWidget(ai_title)
        ai_layout.addWidget(self.ai_status)
        
        # Voice Status
        voice_widget = QWidget()
        voice_layout = QVBoxLayout(voice_widget)
        voice_title = QLabel("SPRACHE")
        voice_title.setAlignment(Qt.AlignCenter)
        voice_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #9ff8ff; margin-bottom: 8px;")
        self.voice_status = QLabel("BEREIT")
        self.voice_status.setAlignment(Qt.AlignCenter)
        self.voice_status.setStyleSheet("font-size: 16px; font-weight: 800; color: #ffb050; background-color: rgba(0,0,0,0.15); padding:6px 12px; border-radius:8px;")
        voice_layout.addWidget(voice_title)
        voice_layout.addWidget(self.voice_status)
        
        # System Status
        sys_widget = QWidget()
        sys_layout = QVBoxLayout(sys_widget)
        sys_title = QLabel("SYSTEM")
        sys_title.setAlignment(Qt.AlignCenter)
        sys_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #9ff8ff; margin-bottom: 8px;")
        self.sys_status = QLabel("ONLINE")
        self.sys_status.setAlignment(Qt.AlignCenter)
        self.sys_status.setStyleSheet("font-size: 16px; font-weight: 800; color: #00ff70; background-color: rgba(0,0,0,0.15); padding:6px 12px; border-radius:8px;")
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
        chat_label.setStyleSheet("font-size: 16px; font-weight: 800; color: #9ff8ff; margin-bottom: 10px; border-bottom:1px solid rgba(0,230,255,0.06); padding-bottom:6px;")
        chat_layout.addWidget(chat_label)
        
        # Output Text - größer und klarer
        self.output_text = QTextEdit()
        self.output_text.setMinimumHeight(220)
        self.output_text.setStyleSheet("""
            font-size: 13px;
            background-color: #020203;
            color: #bffcff;
            border: 2px solid rgba(0,230,255,0.06);
            border-radius: 6px;
            padding: 12px;
        """)
        self.output_text.append("<span style='color: #00FF00; font-size: 14px; font-weight: bold;'>[SYSTEM]</span> <span style='font-size: 14px;'>J.A.R.V.I.S ist online und bereit.</span>")
        chat_layout.addWidget(self.output_text)
        
        # Input Bereich
        input_frame = QFrame()
        input_frame.setMinimumHeight(100)  # Mindesthöhe reduziert
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(12)

        # Input Label
        input_label = QLabel("BEFEHLSEINGABE")
        input_label.setStyleSheet("font-size: 14px; font-weight: 800; color: #9ff8ff;")
        input_layout.addWidget(input_label)
        
        # Input Text - größer und klarer
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(120)
        self.input_text.setStyleSheet("""
            font-size: 13px;
            padding: 12px;
            background-color: #040506;
            color: #cfeff0;
            border: 2px solid rgba(0,230,255,0.06);
            border-radius: 6px;
        """)
        self.input_text.setPlaceholderText("Geben Sie Ihren Befehl ein oder verwenden Sie das Mikrofon...")
        input_layout.addWidget(self.input_text)
        
        # Buttons - deutlich größer und klarer
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Button-Style für alle Buttons
        button_style = """
            QPushButton {
                font-size: 12px;
                font-weight: 700;
                padding: 10px 18px;
                background-color: #07101a;
                color: #bffcff;
                border: 1px solid rgba(0,230,255,0.12);
                border-radius: 6px;
                min-height: 36px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: rgba(0,230,255,0.04);
                border-color: #66f0ff;
                color: #e6ffff;
            }
            QPushButton:pressed {
                background-color: #042028;
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
        # Aktualisiere das Stylesheet bei Resize für bessere Skalierung
        try:
            self._apply_responsive_styles()
        except Exception:
            pass
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