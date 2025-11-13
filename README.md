# JARVIS - WinUI 3 AI Assistant# 🤖 JARVIS - Your Ultimate AI Assistant



Eine moderne Windows 11 Desktop-Anwendung, entwickelt mit **WinUI 3** und **.NET 8**, mit Fluent Design System.<div align="center">



![WinUI 3](https://img.shields.io/badge/WinUI-3-blue)![JARVIS](https://img.shields.io/badge/JARVIS-Ultimate%20Edition-00FFFF?style=for-the-badge)

![.NET 8](https://img.shields.io/badge/.NET-8-purple)![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)

![Windows 11](https://img.shields.io/badge/Windows-11-0078D6)![Windows](https://img.shields.io/badge/Windows-11-0078D6?style=for-the-badge&logo=windows)

![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ Features

**Ein KI-Assistent nach dem Vorbild von Iron Man's JARVIS**

- 🎨 **Modernes Fluent Design** - Native Windows 11 UI mit Acrylic Effekten

- 🤖 **AI Integration Ready** - Vorbereitet für Ollama/OpenAI Integration*Intelligent • Responsive • Privacy-First • Offline-fähig*

- 🎤 **Voice Input** - Unterstützung für Spracherkennung (geplant)

- ⚡ **Schnelle Performance** - Native .NET 8 Kompilierung[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

- 🌓 **Dark/Light Mode** - Automatische Theme-Unterstützung

</div>

## 🚀 Schnellstart

---

### ✅ Build erfolgreich!

## 🎯 Was ist JARVIS?

Das Projekt wurde bereits **erfolgreich kompiliert** und ist bereit zur Ausführung!

JARVIS ist Ihr persönlicher AI-Assistent für Windows 11 - inspiriert von Tony Stark's legendärem JARVIS aus Iron Man. Mit lokaler AI, erweiterten Sprachfunktionen und einer futuristischen UI bringt JARVIS die Sci-Fi-Erfahrung auf Ihren Desktop.

```powershell

# App starten### 🌟 Warum JARVIS?

cd JarvisApp

dotnet run -c Release /p:Platform=x64- **🔒 100% Privat**: Läuft komplett lokal - keine Cloud, keine Datenübertragung

```- **🎭 Ihre Stimme**: Lokale Stimm-Klonierung für persönliche TTS

- **🧠 Intelligent**: Powered by Ollama mit modernsten AI-Modellen

### Voraussetzungen- **⚡ Schnell**: Responsive UI, asynchrone Verarbeitung

- **🎨 Modern**: High-DPI, Windows 11 native Integration

- **Windows 11** (Build 22000 oder höher empfohlen)- **🗣️ Flexibel**: Drei Sprach-Modi für jeden Anwendungsfall

- **.NET 8 SDK** ✅ (bereits installiert)

- **Visual Studio 2022** (optional, für XAML Designer)## ✨ Features



### Mit Visual Studio 2022### 🎤 **Erweiterte Sprachsteuerung**

- **Mikrofon-Modus**: Kontinuierliche Sprach-zu-Text Eingabe

```powershell- **Sprachsteuerung**: Klassischer Aktivierungswort-Modus ("Jarvis")

# Solution öffnen- **Gesprächsmodus**: Natürliche kontinuierliche Konversation

start JarvisApp.sln

```### 🎭 **Lokale Stimm-Klonierung**

- Ein-Klick Aktivierung

Dann in Visual Studio: **F5** drücken oder auf ▶️ "JarvisApp" klicken- Auto-Erkennung wenn Server verfügbar

- Automatischer Fallback zu Standard-TTS

## 📁 Projektstruktur- Echtzeit-Status-Indikator



```### 🤖 **Intelligente AI**

Jarvis/- Ollama Integration (llama3.2:3b, deepseek-r1:1.5b, etc.)

├── JarvisApp/              # WinUI 3 Hauptprojekt- Komplett offline

│   ├── Assets/             # Icons und Ressourcen- Asynchrone Verarbeitung (UI bleibt responsive)

│   ├── MainWindow.xaml     # Haupt-UI (Fluent Design)- Kontextbewusste Antworten

│   ├── App.xaml            # Application Definition

│   └── JarvisApp.csproj    # Projektdatei### 📱 **Responsive Modern UI**

├── JarvisApp.sln           # Visual Studio Solution- Dynamische Skalierung

└── README.md               # Diese Datei- High-DPI Support (4K ready)

```- Windows 11 native Integration

- Reflow für verschiedene Bildschirmgrößen

## 🎨 UI Übersicht

### 🔧 **System-Integration**

Die App enthält:- Windows Anwendungs-Steuerung

- System-Informationen und -Steuerung

- **Moderne Titelleiste** mit Windows 11 Accent Color- Web-Suche (Google, YouTube, Wikipedia)

- **Eingabefeld** für Benutzeranfragen- Vollständige Diagnose-Tools

- **Response-Bereich** für AI-Antworten

- **Statusleiste** mit Echtzeit-Feedback### 🎯 **Smart Features**

- **Fluent Design System** Komponenten- Auto-Recovery für TTS-Server

- Periodische Verfügbarkeits-Prüfung

## 🛠️ Entwicklung- Performance-Monitoring

- Graceful Error Handling

### Projekt kompilieren

## 🚀 Installation

```powershell

cd JarvisApp### Voraussetzungen

dotnet build -c Release /p:Platform=x64- Windows 10/11

```- Python 3.8 oder höher

- Mikrofon (für Spracheingabe)

**Erfolgreich kompiliert!** ✅

```### Schnell-Start

Build succeeded.

    1 Warning(s)```powershell

    0 Error(s)# 1. Repository klonen

Time Elapsed 00:00:08.58git clone https://github.com/Julian333333/Jarvis.git

```cd Jarvis



### App ausführen# 2. Dependencies installieren

pip install -r requirements.txt

```powershell

dotnet run -c Release /p:Platform=x64# 3. Ollama installieren (für lokale AI)

```winget install Ollama.Ollama



### Mit Hot Reload# 4. Ollama starten und Modell laden

ollama serve  # In einem Terminal

```powershellollama pull llama3.2:3b  # In einem anderen Terminal

dotnet watch run /p:Platform=x64

```# 5. JARVIS starten

python -m jarvis.main

## 🔧 Konfiguration```



### RuntimeIdentifiers Warnung beheben### Optional: Test-Server für Stimm-Klonierung



Die Warnung `NETSDK1206` kann ignoriert werden, oder in `JarvisApp.csproj` beheben:```powershell

# Im JARVIS UI auf "🎙️ TEST SERVER" klicken

```xml# Oder manuell starten:

<PropertyGroup>python tools/local_tts_server.py

    <RuntimeIdentifiers>win-x64;win-arm64</RuntimeIdentifiers>```

</PropertyGroup>

```## 🎮 Usage



## 📦 Deployment### Grundlegende Bedienung



### Portable EXE erstellen1. **Text-Befehle**: 

   - Tippen Sie Ihren Befehl ins Eingabefeld

```powershell   - Klicken Sie "AUSFÜHREN"

cd JarvisApp

dotnet publish -c Release -r win-x64 --self-contained /p:Platform=x64 /p:PublishSingleFile=true2. **Sprach-Modi**:

```   - **🎤 MIKROFON**: Für Diktat und längere Texte

   - **🗣️ SPRACHSTEUERUNG**: Aktivierungswort-Modus

Output:   - **💬 GESPRÄCH**: Natürliche Konversation

```

JarvisApp\bin\x64\Release\net8.0-windows10.0.19041.0\win-x64\publish\JarvisApp.exe3. **Diagnose**: 

```   - Klicken Sie "DIAGNOSE" für vollständigen System-Check



### MSIX Package (mit Visual Studio)### Beliebte Befehle



1. Rechtsklick auf Projekt → **Publish**```

2. **Create App Packages**"Zeit" / "Datum" - Aktuelle Zeit/Datum

3. Wähle **Sideloading**"Systeminfo" - CPU und RAM Status

4. **Create**"Öffne Browser/Rechner/Notepad"

"Suche [Begriff]" - Google Suche

## 🚨 Fehlerbehebung"Diagnose" - System-Check

"Klonstatus" - Stimm-Status prüfen

### App startet nicht```



1. **Prüfe Windows Version:**### Stimm-Klonierung nutzen

   ```powershell

   winver1. **Test-Server starten**: Klick auf "🎙️ TEST SERVER"

   ```2. **Auto-Aktivierung**: JARVIS erkennt Server automatisch

   Benötigt: Build 17763 oder höher3. **Manuell umschalten**: "🎭 KLON AN/AUS" Button



2. **Lösche Build-Artefakte:**Status sehen Sie am Indikator:

   ```powershell- 🎭 **GEKLONT** (grün) = Ihre Stimme aktiv

   cd JarvisApp- 📢 **STANDARD** (orange) = Deutsche TTS

   Remove-Item -Recurse bin, obj -Force

   dotnet build /p:Platform=x64## 📚 Documentation

   ```

### Vollständige Dokumentation

### XAML Designer lädt nicht- 📖 [ULTIMATE_FEATURES.md](ULTIMATE_FEATURES.md) - Komplette Feature-Liste

- 🎙️ [LOCAL_VOICE_CLONE_SETUP.md](LOCAL_VOICE_CLONE_SETUP.md) - Stimm-Klonierung Setup

- **Lösung:** Installiere Visual Studio 2022 mit UWP Workload- 🤖 [OLLAMA_SETUP.md](OLLAMA_SETUP.md) - Ollama Installation und Konfiguration

- Alternative: Bearbeite XAML direkt (Hot Reload funktioniert)

### Projekt-Struktur

## 🔮 Nächste Schritte

```

Das Projekt ist **einsatzbereit**! Mögliche Erweiterungen:Jarvis/

├── jarvis/

### 1. Ollama AI Integration│   ├── main.py              # Haupt-Anwendung und GUI

│   ├── ai.py                # Ollama AI Integration

```csharp│   ├── commands.py          # Befehls-Verarbeitung

// In MainWindow.xaml.cs│   ├── audio_utils.py       # Audio-Konvertierung

private async Task<string> GetAIResponseAsync(string prompt)│   └── windows_integration.py

{├── tools/

    using var client = new HttpClient();│   └── local_tts_server.py  # Mock TTS Server

    var response = await client.PostAsJsonAsync(├── voices/

        "http://localhost:11434/api/generate",│   └── user/samples/        # Stimm-Proben

        new { model = "llama2", prompt = prompt }├── requirements.txt

    );└── README.md

    return await response.Content.ReadAsStringAsync();```

}

```## 🛠️ Entwicklung



### 2. Voice Recognition### Building Windows App



```csharp```powershell

// Windows Speech Recognitionpip install pyinstaller

using Windows.Media.SpeechRecognition;pyinstaller --onefile --windowed --name JARVIS jarvis/main.py

```

var recognizer = new SpeechRecognizer();

var result = await recognizer.RecognizeAsync();### Eigene Befehle hinzufügen

string spokenText = result.Text;

```Bearbeiten Sie `jarvis/commands.py`:



### 3. Einstellungen-Panel```python

def your_command(self, command: str) -> str:

Erstelle `SettingsWindow.xaml` für Konfiguration:    # Ihr Code hier

- API Keys    return "Befehl ausgeführt, Daddy."

- Theme Auswahl

- Voice Einstellungen# In _initialize_commands():

'ihr befehl': self.your_command,

## 📊 Status```



| Feature | Status |### Eigenes AI-Modell

|---------|--------|

| WinUI 3 Setup | ✅ Komplett |```python

| Modern UI Design | ✅ Implementiert |# In jarvis/ai.py

| .NET 8 Build | ✅ Erfolgreich |self.model = "ihr-modell:tag"

| Basic Interaktion | ✅ Funktioniert |```

| AI Integration | ⏳ Bereit (nicht implementiert) |

| Voice Input | ⏳ Bereit (nicht implementiert) |## 🔥 Advanced Features

| Packaging | ⏳ Bereit |

### Echte Stimm-Klonierung (XTTS v2)

## 📄 Technische Details

Für echte Stimm-Klonierung (nicht nur Test-Ton):

- **Framework:** .NET 8.0-windows10.0.19041.0

- **Min Windows Version:** 10.0.17763.0 (Windows 10 1809)1. Installieren Sie Coqui TTS oder XTTS v2

- **Target Platform:** x64, ARM642. Konfigurieren Sie Endpunkt auf `http://127.0.0.1:5005/tts`

- **Packages:**3. Legen Sie Ihre Stimmprobe unter `voices/user/samples/reference.wav` ab

  - Microsoft.WindowsAppSDK 1.5.240802000

  - Microsoft.Windows.SDK.BuildTools 10.0.22621.3233### Performance-Tuning



## 🤝 Contributing```python

# Für niedrigere CPU-Nutzung:

1. Fork das Projekt# - Verwenden Sie kleinere AI-Modelle (1.5b statt 3b)

2. Erstelle einen Feature Branch# - Deaktivieren Sie nicht benötigte Sprach-Modi

3. Committe deine Änderungen# - Reduzieren Sie die Auto-Check-Frequenz

4. Pushe zum Branch```

5. Öffne einen Pull Request

## 🐛 Troubleshooting

## 📞 Support

### Häufige Probleme

- [WinUI 3 Dokumentation](https://learn.microsoft.com/windows/apps/winui/winui3/)

- [.NET 8 Dokumentation](https://learn.microsoft.com/dotnet/core/whats-new/dotnet-8)**Problem**: KI antwortet nicht  

- [Windows App SDK](https://github.com/microsoft/WindowsAppSDK)**Lösung**: 

```powershell

---ollama list  # Prüfe verfügbare Modelle

ollama serve  # Starte Ollama neu

**Status:** ✅ **Projekt erfolgreich erstellt und kompiliert!**```



Entwickelt mit ❤️ und **WinUI 3****Problem**: Mikrofon funktioniert nicht  

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