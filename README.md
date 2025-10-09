# 🤖 JARVIS - Your Ultimate AI Assistant

<div align="center">

![JARVIS](https://img.shields.io/badge/JARVIS-Ultimate%20Edition-00FFFF?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Windows](https://img.shields.io/badge/Windows-11-0078D6?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Ein KI-Assistent nach dem Vorbild von Iron Man's JARVIS**

*Intelligent • Responsive • Privacy-First • Offline-fähig*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---

## 🎯 Was ist JARVIS?

JARVIS ist Ihr persönlicher AI-Assistent für Windows 11 - inspiriert von Tony Stark's legendärem JARVIS aus Iron Man. Mit lokaler AI, erweiterten Sprachfunktionen und einer futuristischen UI bringt JARVIS die Sci-Fi-Erfahrung auf Ihren Desktop.

### 🌟 Warum JARVIS?

- **🔒 100% Privat**: Läuft komplett lokal - keine Cloud, keine Datenübertragung
- **🎭 Ihre Stimme**: Lokale Stimm-Klonierung für persönliche TTS
- **🧠 Intelligent**: Powered by Ollama mit modernsten AI-Modellen
- **⚡ Schnell**: Responsive UI, asynchrone Verarbeitung
- **🎨 Modern**: High-DPI, Windows 11 native Integration
- **🗣️ Flexibel**: Drei Sprach-Modi für jeden Anwendungsfall

## ✨ Features

### 🎤 **Erweiterte Sprachsteuerung**
- **Mikrofon-Modus**: Kontinuierliche Sprach-zu-Text Eingabe
- **Sprachsteuerung**: Klassischer Aktivierungswort-Modus ("Jarvis")
- **Gesprächsmodus**: Natürliche kontinuierliche Konversation

### 🎭 **Lokale Stimm-Klonierung**
- Ein-Klick Aktivierung
- Auto-Erkennung wenn Server verfügbar
- Automatischer Fallback zu Standard-TTS
- Echtzeit-Status-Indikator

### 🤖 **Intelligente AI**
- Ollama Integration (llama3.2:3b, deepseek-r1:1.5b, etc.)
- Komplett offline
- Asynchrone Verarbeitung (UI bleibt responsive)
- Kontextbewusste Antworten

### 📱 **Responsive Modern UI**
- Dynamische Skalierung
- High-DPI Support (4K ready)
- Windows 11 native Integration
- Reflow für verschiedene Bildschirmgrößen

### 🔧 **System-Integration**
- Windows Anwendungs-Steuerung
- System-Informationen und -Steuerung
- Web-Suche (Google, YouTube, Wikipedia)
- Vollständige Diagnose-Tools

### 🎯 **Smart Features**
- Auto-Recovery für TTS-Server
- Periodische Verfügbarkeits-Prüfung
- Performance-Monitoring
- Graceful Error Handling

## 🚀 Installation

### Voraussetzungen
- Windows 10/11
- Python 3.8 oder höher
- Mikrofon (für Spracheingabe)

### Schnell-Start

```powershell
# 1. Repository klonen
git clone https://github.com/Julian333333/Jarvis.git
cd Jarvis

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Ollama installieren (für lokale AI)
winget install Ollama.Ollama

# 4. Ollama starten und Modell laden
ollama serve  # In einem Terminal
ollama pull llama3.2:3b  # In einem anderen Terminal

# 5. JARVIS starten
python -m jarvis.main
```

### Optional: Test-Server für Stimm-Klonierung

```powershell
# Im JARVIS UI auf "🎙️ TEST SERVER" klicken
# Oder manuell starten:
python tools/local_tts_server.py
```

## 🎮 Usage

### Grundlegende Bedienung

1. **Text-Befehle**: 
   - Tippen Sie Ihren Befehl ins Eingabefeld
   - Klicken Sie "AUSFÜHREN"

2. **Sprach-Modi**:
   - **🎤 MIKROFON**: Für Diktat und längere Texte
   - **🗣️ SPRACHSTEUERUNG**: Aktivierungswort-Modus
   - **💬 GESPRÄCH**: Natürliche Konversation

3. **Diagnose**: 
   - Klicken Sie "DIAGNOSE" für vollständigen System-Check

### Beliebte Befehle

```
"Zeit" / "Datum" - Aktuelle Zeit/Datum
"Systeminfo" - CPU und RAM Status
"Öffne Browser/Rechner/Notepad"
"Suche [Begriff]" - Google Suche
"Diagnose" - System-Check
"Klonstatus" - Stimm-Status prüfen
```

### Stimm-Klonierung nutzen

1. **Test-Server starten**: Klick auf "🎙️ TEST SERVER"
2. **Auto-Aktivierung**: JARVIS erkennt Server automatisch
3. **Manuell umschalten**: "🎭 KLON AN/AUS" Button

Status sehen Sie am Indikator:
- 🎭 **GEKLONT** (grün) = Ihre Stimme aktiv
- 📢 **STANDARD** (orange) = Deutsche TTS

## 📚 Documentation

### Vollständige Dokumentation
- 📖 [ULTIMATE_FEATURES.md](ULTIMATE_FEATURES.md) - Komplette Feature-Liste
- 🎙️ [LOCAL_VOICE_CLONE_SETUP.md](LOCAL_VOICE_CLONE_SETUP.md) - Stimm-Klonierung Setup
- 🤖 [OLLAMA_SETUP.md](OLLAMA_SETUP.md) - Ollama Installation und Konfiguration

### Projekt-Struktur

```
Jarvis/
├── jarvis/
│   ├── main.py              # Haupt-Anwendung und GUI
│   ├── ai.py                # Ollama AI Integration
│   ├── commands.py          # Befehls-Verarbeitung
│   ├── audio_utils.py       # Audio-Konvertierung
│   └── windows_integration.py
├── tools/
│   └── local_tts_server.py  # Mock TTS Server
├── voices/
│   └── user/samples/        # Stimm-Proben
├── requirements.txt
└── README.md
```

## 🛠️ Entwicklung

### Building Windows App

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name JARVIS jarvis/main.py
```

### Eigene Befehle hinzufügen

Bearbeiten Sie `jarvis/commands.py`:

```python
def your_command(self, command: str) -> str:
    # Ihr Code hier
    return "Befehl ausgeführt, Daddy."

# In _initialize_commands():
'ihr befehl': self.your_command,
```

### Eigenes AI-Modell

```python
# In jarvis/ai.py
self.model = "ihr-modell:tag"
```

## 🔥 Advanced Features

### Echte Stimm-Klonierung (XTTS v2)

Für echte Stimm-Klonierung (nicht nur Test-Ton):

1. Installieren Sie Coqui TTS oder XTTS v2
2. Konfigurieren Sie Endpunkt auf `http://127.0.0.1:5005/tts`
3. Legen Sie Ihre Stimmprobe unter `voices/user/samples/reference.wav` ab

### Performance-Tuning

```python
# Für niedrigere CPU-Nutzung:
# - Verwenden Sie kleinere AI-Modelle (1.5b statt 3b)
# - Deaktivieren Sie nicht benötigte Sprach-Modi
# - Reduzieren Sie die Auto-Check-Frequenz
```

## 🐛 Troubleshooting

### Häufige Probleme

**Problem**: KI antwortet nicht  
**Lösung**: 
```powershell
ollama list  # Prüfe verfügbare Modelle
ollama serve  # Starte Ollama neu
```

**Problem**: Mikrofon funktioniert nicht  
**Lösung**: 
- Prüfen Sie Windows Mikrofon-Berechtigungen
- Stellen Sie das Mikrofon als Standard-Gerät ein

**Problem**: UI zu klein/groß  
**Lösung**: 
- Fenster resizen - UI passt sich automatisch an
- Für High-DPI Displays bereits optimiert

## 🤝 Contributing

Contributions sind willkommen! 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Credits

**Inspiriert von**: Iron Man's JARVIS  
**Entwickelt mit**: Python, PyQt5, Ollama, pyttsx3  
**Für**: Alle Iron Man Fans und Tech-Enthusiasten

---

<div align="center">

**"Sometimes you gotta run before you can walk."** - Tony Stark

Made with ❤️ and ☕

[⭐ Star this repo](https://github.com/Julian333333/Jarvis) • [🐛 Report Bug](https://github.com/Julian333333/Jarvis/issues) • [💡 Request Feature](https://github.com/Julian333333/Jarvis/issues)

</div>