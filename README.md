# JARVIS WinUI 3 Application

Ein moderner Windows 11 AI-Assistent mit WinUI 3 und Windows App SDK.

## 🎯 Features

- ✨ Native Windows 11 Fluent Design
- 🎨 Mica Backdrop und moderne UI-Elemente
- 💬 Chat-Interface für AI-Interaktion
- 🌗 Automatische Dark/Light Mode Unterstützung
- 📱 Responsive Design mit 4K DPI-Skalierung

## 🛠️ Voraussetzungen

### Erforderlich:
- **Windows 11** (Build 22000 oder höher für Mica)
- **Visual Studio 2022** (Version 17.0 oder höher)
- **.NET 8.0 SDK**

### Visual Studio Workloads:
1. **.NET Desktop Development**
2. **Universal Windows Platform development**
3. **Windows App SDK C# Templates**

## 🚀 Installation & Setup

### Option 1: Visual Studio 2022 (Empfohlen)

```powershell
# 1. Visual Studio 2022 Community installieren
winget install Microsoft.VisualStudio.2022.Community

# 2. Solution öffnen
start JarvisApp.sln
```

**In Visual Studio:**
1. Wähle die Konfiguration: **Debug** / **x64**
2. Drücke **F5** zum Starten
3. Die App wird kompiliert und gestartet

### Option 2: .NET CLI (Eingeschränkt)

```powershell
# Pakete wiederherstellen
dotnet restore JarvisApp.sln

# Kompilieren (funktioniert möglicherweise nicht ohne Visual Studio Build Tools)
dotnet build JarvisApp.sln -c Debug /p:Platform=x64
```

**⚠️ Wichtig:** Der XAML Compiler benötigt Visual Studio Build Tools!

## 📁 Projektstruktur

```
JarvisApp/
├── JarvisApp/
│   ├── Assets/              # Bilder und Icons
│   ├── Properties/          # Assembly-Eigenschaften
│   ├── App.xaml            # Application-Definition
│   ├── App.xaml.cs         # Application Code-Behind
│   ├── MainWindow.xaml     # Hauptfenster UI
│   ├── MainWindow.xaml.cs  # Hauptfenster Logik
│   ├── app.manifest        # Windows Manifest (DPI-Aware)
│   └── JarvisApp.csproj    # Projektdatei
└── JarvisApp.sln           # Visual Studio Solution
```

## 💻 Verwendung

### Erste Schritte:

1. **Starte die App** in Visual Studio (F5)
2. **Gib eine Nachricht ein** im Textfeld
3. **Klicke auf "Send"** für eine Demo-Antwort

### Die Benutzeroberfläche:

- **Titelleiste**: Zeigt "JARVIS AI Assistant"
- **Welcome Card**: Willkommensnachricht
- **Input Section**: Textfeld für Eingaben
- **Response Section**: Zeigt AI-Antworten
- **Status Bar**: Zeigt aktuellen Status und Technologie-Info

## 🔧 Entwicklung

### Konfiguration bearbeiten:

Die `.csproj` Datei enthält:
- **TargetFramework**: `net8.0-windows10.0.19041.0`
- **Platforms**: `x64` und `ARM64`
- **Windows App SDK**: Version `1.5.240802000`

### XAML anpassen:

Bearbeite `MainWindow.xaml` für UI-Änderungen:
```xml
<!-- Beispiel: Farbe ändern -->
<Grid Background="{ThemeResource SystemAccentColor}">
```

### Code-Behind erweitern:

Bearbeite `MainWindow.xaml.cs`:
```csharp
private void SendButton_Click(object sender, RoutedEventArgs e)
{
    // Füge hier deine Logik hinzu
}
```

## 🎨 Design-System

Die App verwendet das Windows 11 Fluent Design System:

- **Mica Backdrop**: Durchscheinendes Material
- **Acrylic**: Glaseffekt für Panels
- **Theme-aware Colors**: Automatische Dark/Light Mode Anpassung
- **Rounded Corners**: Moderne abgerundete Ecken
- **Typography**: Native Windows 11 Schriftarten

## 🐛 Fehlerbehebung

### Problem: "XAML Compiler Error"

**Lösung:**
```powershell
# 1. Lösche Build-Ausgaben
Remove-Item -Recurse JarvisApp\bin, JarvisApp\obj

# 2. NuGet-Pakete neu installieren
dotnet restore JarvisApp.sln

# 3. In Visual Studio: Build → Rebuild Solution
```

### Problem: "Platform x64 not found"

**Lösung:**
- In Visual Studio: Build → Configuration Manager
- Stelle sicher, dass **x64** ausgewählt ist
- Falls nicht vorhanden: Neue Platform erstellen

### Problem: "Windows App SDK not found"

**Lösung:**
```powershell
# NuGet-Cache leeren
dotnet nuget locals all --clear

# Pakete neu installieren
dotnet restore JarvisApp.sln
```

## 📦 Deployment

### Debug-Build:
```powershell
dotnet build JarvisApp.sln -c Debug /p:Platform=x64
```

### Release-Build:
```powershell
dotnet build JarvisApp.sln -c Release /p:Platform=x64
```

### Veröffentlichen:
```powershell
dotnet publish JarvisApp\JarvisApp.csproj -c Release /p:Platform=x64 -o publish
```

## 🔄 Nächste Schritte

### Geplante Features:

1. **AI-Integration**
   - Ollama API-Anbindung
   - Streaming-Antworten
   - Context-Management

2. **Voice Recognition**
   - Windows Speech Recognition
   - Sprachbefehle
   - Text-to-Speech

3. **System Commands**
   - Datei-Operationen
   - Anwendungen starten
   - System-Informationen

4. **Settings Page**
   - Theme-Auswahl
   - API-Konfiguration
   - Tastenkombinationen

## 📚 Ressourcen

- [WinUI 3 Documentation](https://docs.microsoft.com/windows/apps/winui/winui3/)
- [Windows App SDK](https://docs.microsoft.com/windows/apps/windows-app-sdk/)
- [.NET 8 Documentation](https://docs.microsoft.com/dotnet/)

## 📄 Lizenz

Dieses Projekt ist ein Demonstrationsprojekt für WinUI 3 Entwicklung.

---

**Entwickelt mit ❤️ für Windows 11**
