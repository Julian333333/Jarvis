"""
Befehlssystem für JARVIS Sprachsteuerung
"""

import os
import subprocess
import webbrowser
import datetime
import psutil
from typing import Dict, Callable, List, Tuple

class CommandProcessor:
    def __init__(self, jarvis_gui=None):
        self.jarvis_gui = jarvis_gui
        self.commands = self._initialize_commands()
    
    def _initialize_commands(self) -> Dict[str, Callable]:
        """Initialisiert alle verfügbaren Befehle"""
        return {
            # System Befehle
            'zeit': self.get_time,
            'datum': self.get_date,
            'systeminfo': self.get_system_info,
            'herunterfahren': self.shutdown_system,
            'neustart': self.restart_system,
            'lautstärke': self.control_volume,
            
            # Anwendungen
            'öffne': self.open_application,
            'starte': self.open_application,
            'schließe': self.close_application,
            'browser': self.open_browser,
            'notepad': self.open_notepad,
            'rechner': self.open_calculator,
            'explorer': self.open_explorer,
            
            # Web Suche
            'suche': self.web_search,
            'google': self.google_search,
            'youtube': self.youtube_search,
            'wikipedia': self.wikipedia_search,
            
            # JARVIS Steuerung
            'hilfe': self.show_help,
            'befehle': self.list_commands,
            'diagnose': self.run_diagnostics,
            'status': self.show_status,
            'modell': self.change_ai_model,
            'ai modell': self.show_available_models,
            'verfügbare modelle': self.show_available_models,
            'reset': self.reset_conversation,
            'neustart gespräch': self.reset_conversation,
            'stopp': self.stop_listening,
            'stop': self.stop_listening,
            'aufhören': self.stop_listening,
            'schluss': self.stop_listening,
            'beenden': self.exit_jarvis,

            # Stimme klonen (lokal)
            'stimme klonen': self.enable_cloned_voice,
            'klonstimme aktivieren': self.enable_cloned_voice,
            'klonstimme deaktivieren': self.disable_cloned_voice,
            'stimmprobe setzen': self.set_voice_sample,
            'stimmprobe abspielen': self.play_voice_sample,
            'klon status': self.clone_status,
            'klonstatus': self.clone_status,
            
            # Datei Operationen
            'erstelle': self.create_file,
            'lösche': self.delete_file,
            'öffne datei': self.open_file,
            
            # Multimedia
            'musik': self.play_music,
            'video': self.play_video,
            'screenshot': self.take_screenshot,
        }
    
    def process_command(self, command_text: str) -> str:
        """Verarbeitet einen Sprachbefehl"""
        command_text = command_text.lower().strip()
        
        # Suche nach passendem Befehl
        for keyword, function in self.commands.items():
            if keyword in command_text:
                try:
                    return function(command_text)
                except Exception as e:
                    return f"Fehler beim Ausführen des Befehls '{keyword}': {str(e)}"
        
        # Fallback: Standard AI Antwort
        return self._default_response(command_text)
    
    def _default_response(self, command: str) -> str:
        """Standard-Antwort für unbekannte Befehle"""
        return f"Ich verstehe den Befehl '{command}' nicht. Sagen Sie 'Hilfe' für verfügbare Befehle."
    
    # System Befehle
    def get_time(self, command: str) -> str:
        now = datetime.datetime.now()
        hour = now.hour
        # Iron Man style responses based on time of day
        if 5 <= hour < 12:
            greeting = "Guten Morgen, Daddy. "
        elif 12 <= hour < 18:
            greeting = "Daddy, "
        elif 18 <= hour < 22:
            greeting = "Guten Abend, Daddy. "
        else:
            greeting = "Daddy, es ist spät. "
        return f"{greeting}Es ist {now.strftime('%H:%M')} Uhr."
    
    def get_date(self, command: str) -> str:
        now = datetime.datetime.now()
        weekday = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'][now.weekday()]
        return f"Heute ist {weekday}, der {now.strftime('%d.%m.%Y')}, Daddy."
    
    def get_system_info(self, command: str) -> str:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Performance assessment
        if cpu_percent < 50 and memory.percent < 60:
            status = "Alle Systeme laufen optimal, Daddy."
        elif cpu_percent < 75 and memory.percent < 80:
            status = "Systeme arbeiten im normalen Bereich, Daddy."
        else:
            status = "Hohe Systemauslastung erkannt, Daddy."
        
        return f"{status} CPU: {cpu_percent}%, RAM: {memory.percent}% belegt."
    
    def shutdown_system(self, command: str) -> str:
        subprocess.Popen("shutdown /s /t 10", shell=True)
        return "Verstanden, Daddy. System fährt in 10 Sekunden herunter. Bis bald."
    
    def restart_system(self, command: str) -> str:
        subprocess.Popen("shutdown /r /t 10", shell=True)
        return "Neustart eingeleitet, Daddy. System startet in 10 Sekunden neu."
    
    def control_volume(self, command: str) -> str:
        if 'hoch' in command or 'lauter' in command:
            subprocess.run("nircmd.exe changesysvolume 6553", shell=True)
            return "Lautstärke erhöht."
        elif 'runter' in command or 'leiser' in command:
            subprocess.run("nircmd.exe changesysvolume -6553", shell=True)
            return "Lautstärke verringert."
        elif 'stumm' in command or 'mute' in command:
            subprocess.run("nircmd.exe mutesysvolume 1", shell=True)
            return "Ton stummgeschaltet."
        else:
            return "Sagen Sie: Lautstärke hoch, runter oder stumm."
    
    # Anwendungen
    def open_application(self, command: str) -> str:
        apps = {
            'notepad': ('notepad.exe', 'Texteditor'),
            'editor': ('notepad.exe', 'Texteditor'),
            'rechner': ('calc.exe', 'Rechner'),
            'taschenrechner': ('calc.exe', 'Rechner'),
            'calculator': ('calc.exe', 'Rechner'),
            'explorer': ('explorer.exe', 'Datei-Explorer'),
            'browser': ('msedge.exe', 'Browser'),
            'edge': ('msedge.exe', 'Edge Browser'),
            'chrome': ('chrome.exe', 'Chrome'),
            'firefox': ('firefox.exe', 'Firefox'),
            'paint': ('mspaint.exe', 'Paint'),
            'cmd': ('cmd.exe', 'Kommandozeile'),
            'terminal': ('cmd.exe', 'Terminal'),
            'powershell': ('powershell.exe', 'PowerShell'),
        }
        
        for app_name, (exe_name, display_name) in apps.items():
            if app_name in command:
                try:
                    subprocess.Popen(exe_name, shell=True)
                    return f"{display_name} gestartet, Daddy."
                except Exception:
                    return f"Konnte {display_name} nicht öffnen, Daddy. Möglicherweise nicht installiert."
        
        return "Anwendung nicht gefunden, Daddy. Sagen Sie 'Hilfe' für verfügbare Befehle."
    
    def close_application(self, command: str) -> str:
        # Vereinfachte Version - könnte erweitert werden
        return "Zum Schließen von Anwendungen verwenden Sie Alt+F4, Daddy, oder ich kann eine Prozessverwaltung für Sie implementieren."
    
    def open_browser(self, command: str) -> str:
        webbrowser.open('https://www.google.com')
        return "Browser geöffnet, Daddy. Navigiere zu Google."
    
    def open_notepad(self, command: str) -> str:
        subprocess.Popen('notepad.exe')
        return "Texteditor bereit, Daddy."
    
    def open_calculator(self, command: str) -> str:
        subprocess.Popen('calc.exe')
        return "Rechner geöffnet, Daddy. Benötigen Sie weitere Berechnungen?"
    
    def open_explorer(self, command: str) -> str:
        subprocess.Popen('explorer.exe')
        return "Datei-Explorer geöffnet, Daddy."
    
    # Web Suche
    def web_search(self, command: str) -> str:
        # Extrahiere Suchbegriff nach "suche"
        if 'suche' in command:
            search_term = command.split('suche', 1)[1].strip()
            if search_term:
                url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Durchsuche das Internet nach '{search_term}' für Sie, Daddy."
        return "Wonach soll ich suchen, Daddy?"
    
    def google_search(self, command: str) -> str:
        return self.web_search(command.replace('google', 'suche'))
    
    def youtube_search(self, command: str) -> str:
        if 'youtube' in command:
            search_term = command.split('youtube', 1)[1].strip()
            if search_term:
                url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Suche nach '{search_term}' auf YouTube, Daddy. Einen Moment."
        return "Was möchten Sie auf YouTube finden, Daddy?"
    
    def wikipedia_search(self, command: str) -> str:
        if 'wikipedia' in command:
            search_term = command.split('wikipedia', 1)[1].strip()
            if search_term:
                url = f"https://de.wikipedia.org/wiki/{search_term.replace(' ', '_')}"
                webbrowser.open(url)
                return f"Rufe Wikipedia-Artikel zu '{search_term}' auf, Daddy."
        return "Zu welchem Thema soll ich Wikipedia öffnen, Daddy?"
    
    # JARVIS Steuerung
    def show_help(self, command: str) -> str:
        help_text = """
Verfügbare Befehle:

SYSTEM:
- Zeit/Datum - Aktuelle Zeit oder Datum
- Systeminfo - CPU und RAM Status
- Herunterfahren/Neustart - System steuern
- Lautstärke hoch/runter/stumm

ANWENDUNGEN:
- Öffne/Starte [App] - Anwendung starten
- Browser/Notepad/Rechner/Explorer

WEB:
- Suche [Begriff] - Google Suche
- YouTube [Begriff] - YouTube Suche
- Wikipedia [Begriff] - Wikipedia Suche

JARVIS:
- Hilfe - Diese Hilfe anzeigen
- Befehle - Alle Befehle auflisten
- Diagnose - Systemdiagnose
- Status - Systemstatus
- Stopp/Beenden - JARVIS stoppen
        """
        return help_text.strip()
    
    def list_commands(self, command: str) -> str:
        commands = list(self.commands.keys())
        return f"Verfügbare Befehle: {', '.join(commands)}"
    
    def run_diagnostics(self, command: str) -> str:
        if self.jarvis_gui:
            self.jarvis_gui.run_diagnostics()
        return "Systemdiagnose wurde ausgeführt."
    
    def show_status(self, command: str) -> str:
        return "Alle Systeme operational. JARVIS ist bereit."
    
    def change_ai_model(self, command: str) -> str:
        """Ändert das AI-Modell"""
        if self.jarvis_gui and hasattr(self.jarvis_gui, 'ai'):
            # Extrahiere Modellname aus dem Befehl
            parts = command.lower().split()
            if len(parts) > 1:
                model_name = " ".join(parts[1:])  # Alles nach "modell"
                self.jarvis_gui.ai.set_model(model_name)
                return f"AI-Modell wurde zu '{model_name}' geändert."
            else:
                current_model = self.jarvis_gui.ai.model
                return f"Aktuelles Modell: {current_model}. Sagen Sie 'Modell [Name]' zum Ändern."
        return "Fehler beim Zugriff auf AI-System."
    
    def show_available_models(self, command: str) -> str:
        """Zeigt verfügbare AI-Modelle"""
        if self.jarvis_gui and hasattr(self.jarvis_gui, 'ai'):
            models = self.jarvis_gui.ai.get_available_models()
            current_model = self.jarvis_gui.ai.model
            model_list = "\n".join([f"{'✓' if model == current_model else '-'} {model}" for model in models])
            return f"Verfügbare AI-Modelle:\n{model_list}\n\n✓ = aktuell verwendet"
        return "Fehler beim Abrufen der verfügbaren Modelle."
    
    def reset_conversation(self, command: str) -> str:
        """Setzt die Konversationshistorie zurück"""
        if self.jarvis_gui and hasattr(self.jarvis_gui, 'ai'):
            self.jarvis_gui.ai.clear_history()
            return "Konversationshistorie wurde zurückgesetzt. Frischer Start!"
        return "Fehler beim Zurücksetzen der Konversation."
    
    def stop_listening(self, command: str) -> str:
        if self.jarvis_gui:
            self.jarvis_gui.toggle_voice()  # Sprachsteuerung stoppen
        return "Sprachsteuerung wurde gestoppt."
    
    def exit_jarvis(self, command: str) -> str:
        if self.jarvis_gui:
            self.jarvis_gui.close()
        return "JARVIS wird beendet."

    # Geklonte Stimme (lokaler Server)
    def enable_cloned_voice(self, command: str) -> str:
        """Aktiviert die geklonte Stimme. Optional mit Pfad: 'Stimme klonen C:\\Pfad\\zu\\sample.wav'"""
        speaker_wav = None
        parts = command.split()
        if len(parts) > 2:
            speaker_wav = command.split(' ', 2)[2].strip().strip('"')
        if self.jarvis_gui and hasattr(self.jarvis_gui, 'voice'):
            ok = self.jarvis_gui.voice.enable_cloned_voice(speaker_wav=speaker_wav)
            if ok:
                return "Geklonte Stimme aktiviert."
            return "Konnte geklonte Stimme nicht aktivieren. Stellen Sie sicher, dass der lokale TTS-Server läuft und eine Stimmprobe vorhanden ist."
        return "Kein Voice-Controller gefunden."

    def disable_cloned_voice(self, command: str) -> str:
        if self.jarvis_gui and hasattr(self.jarvis_gui, 'voice'):
            self.jarvis_gui.voice.disable_cloned_voice()
            return "Geklonte Stimme deaktiviert. Standard-TTS aktiv."
        return "Kein Voice-Controller gefunden."

    def set_voice_sample(self, command: str) -> str:
        """Setzt den Pfad zur Stimmprobe: 'Stimmprobe setzen C:\\Pfad\\sample.wav'"""
        if self.jarvis_gui and hasattr(self.jarvis_gui, 'voice'):
            parts = command.split(' ', 2)
            if len(parts) >= 3:
                path = parts[2].strip().strip('"')
                if os.path.exists(path):
                    self.jarvis_gui.voice.cloned_speaker_wav = path
                    return f"Stimmprobe gesetzt: {path}"
                return "Pfad existiert nicht."
            return "Bitte Pfad zur Stimmprobe angeben."
        return "Kein Voice-Controller gefunden."

    def play_voice_sample(self, command: str) -> str:
        """Spielt die aktuelle Stimmprobe lokal ab."""
        if not (self.jarvis_gui and hasattr(self.jarvis_gui, 'voice')):
            return "Kein Voice-Controller gefunden."
        sample = getattr(self.jarvis_gui.voice, 'cloned_speaker_wav', None)
        if not sample or not os.path.exists(sample):
            return "Keine Stimmprobe gefunden. Setzen Sie zuerst eine Datei mit 'Stimmprobe setzen ...'."
        try:
            # winsound spielt nur WAV direkt ab; für MP3 den Standardplayer nutzen
            if sample.lower().endswith('.mp3'):
                os.startfile(sample)  # Öffnet mit Standard-App unter Windows
                return f"Stimmprobe (MP3) mit Standardplayer geöffnet: {sample}"
            import winsound
            winsound.PlaySound(sample, winsound.SND_FILENAME)
            return f"Stimmprobe (WAV) abgespielt: {sample}"
        except Exception as e:
            return f"Konnte Stimmprobe nicht abspielen: {e}"

    def clone_status(self, command: str) -> str:
        """Zeigt den Status der geklonten Stimme und Server-Erreichbarkeit."""
        if not (self.jarvis_gui and hasattr(self.jarvis_gui, 'voice')):
            return "Kein Voice-Controller gefunden."
        v = self.jarvis_gui.voice
        sample = v.cloned_speaker_wav or "(keine)"
        # Probe ohne Fehler durchzureichen
        reachable = False
        try:
            reachable = bool(v._probe_cloned_ready())
        except Exception:
            reachable = False
        mode = getattr(v, 'tts_mode', 'standard')
        return f"Klonstatus: Modus={mode}, Server={'erreichbar' if reachable else 'nicht erreichbar'}, Stimmprobe={sample}"
    
    # Datei Operationen
    def create_file(self, command: str) -> str:
        # Vereinfachte Version
        return "Dateierstellung über Sprachbefehl nicht implementiert."
    
    def delete_file(self, command: str) -> str:
        return "Dateilöschung über Sprachbefehl aus Sicherheitsgründen nicht verfügbar."
    
    def open_file(self, command: str) -> str:
        return "Datei öffnen über Sprachbefehl nicht implementiert."
    
    # Multimedia
    def play_music(self, command: str) -> str:
        # Öffne Standard-Musik-App
        subprocess.Popen('msedge.exe https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        return "Musik wird abgespielt."
    
    def play_video(self, command: str) -> str:
        webbrowser.open('https://www.youtube.com')
        return "YouTube wurde geöffnet."
    
    def take_screenshot(self, command: str) -> str:
        # Screenshot mit Windows Snipping Tool
        subprocess.Popen('snippingtool.exe')
        return "Screenshot-Tool wurde geöffnet."