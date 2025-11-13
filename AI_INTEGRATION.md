# 🤖 JARVIS AI Integration - Anleitung

## ✅ Die AI-Integration ist fertig!

Die JARVIS App kann jetzt mit Ollama kommunizieren und intelligente Antworten generieren.

## 🚀 Schnellstart

### 1. Ollama installieren und starten

```powershell
# Ollama herunterladen von: https://ollama.ai
# Nach Installation:

# Ollama Server starten
ollama serve

# In einem neuen Terminal: Modell herunterladen
ollama pull llama2
# oder ein anderes Modell:
ollama pull mistral
ollama pull codellama
```

### 2. JARVIS starten

```powershell
.\Start-JarvisApp.ps1
```

### 3. Mit der AI chatten

- **Frage eingeben** in das große Textfeld
- **Enter drücken** oder auf "Send" klicken
- **Live-Streaming** der Antwort sehen
- **Shift+Enter** für neue Zeile ohne Senden

## 🎯 Features

### ✅ Implementiert

- **Ollama-Integration** - Verbindung zu lokalem Ollama Server (localhost:11434)
- **Streaming-Antworten** - Echtzeit-Token-Generierung
- **Modell-Erkennung** - Zeigt verfügbare Modelle an
- **Status-Anzeige** - Prüft ob Ollama läuft
- **Keyboard-Shortcuts** - Enter zum Senden, Shift+Enter für neue Zeile
- **Clear-Funktion** - Konversation zurücksetzen
- **Fehlerbehandlung** - Zeigt verständliche Fehlermeldungen

### 🎨 UI-Elemente

```
┌─────────────────────────────────┐
│  JARVIS AI Assistant            │
├─────────────────────────────────┤
│                                 │
│  [Eingabefeld]                  │
│  Shift+Enter für neue Zeile     │
│                                 │
│  [Send]  [Clear]                │
│                                 │
│  ┌───────────────────────────┐  │
│  │ AI Antwort erscheint      │  │
│  │ hier in Echtzeit...       │  │
│  └───────────────────────────┘  │
│                                 │
│  Status: ✅ Ollama verbunden    │
└─────────────────────────────────┘
```

## 📝 Code-Struktur

### AIService.cs

```csharp
// Hauptklasse für AI-Kommunikation
- IsOllamaRunningAsync()      // Prüft Verbindung
- GetAvailableModelsAsync()    // Listet Modelle
- GenerateStreamingResponseAsync()  // Streaming-Chat
```

### MainWindow.xaml.cs

```csharp
// Event-Handler
- CheckOllamaStatusAsync()     // Status-Check beim Start
- SendButton_Click()           // Sendet Anfrage
- InputTextBox_KeyDown()       // Enter-Taste Handler
- ClearButton_Click()          // Löscht Konversation
```

## 🔧 Konfiguration

### Modell ändern

In `AIService.cs`:

```csharp
private const string DefaultModel = "llama2";  // Hier ändern
```

Verfügbare Modelle:
- `llama2` (Standard, gut für Chat)
- `mistral` (Schneller, kleiner)
- `codellama` (Programmier-Spezialist)
- `phi` (Sehr klein, schnell)

### Ollama-URL ändern

```csharp
private readonly string _ollamaUrl = "http://localhost:11434";
```

## 🐛 Fehlerbehebung

### "⚠️ Ollama nicht gefunden"

**Problem:** Ollama Server läuft nicht

**Lösung:**
```powershell
ollama serve
```

### "Fehler: No connection could be made"

**Problem:** Ollama ist nicht installiert oder läuft auf anderem Port

**Lösung:**
1. Installiere Ollama: https://ollama.ai
2. Starte: `ollama serve`
3. Prüfe Port: Sollte 11434 sein

### Modell nicht gefunden

**Problem:** Modell wurde nicht heruntergeladen

**Lösung:**
```powershell
ollama list          # Zeige installierte Modelle
ollama pull llama2   # Lade Modell herunter
```

### App reagiert nicht

**Problem:** Großes Modell braucht lange zum Antworten

**Lösung:**
- Warte ab (erste Token können 5-10 Sek dauern)
- Nutze kleineres Modell: `ollama pull phi`
- Prüfe CPU/RAM Auslastung

## 💡 Tipps

### Bessere Antworten

**Kontext geben:**
```
Ich bin ein Python-Entwickler. Erkläre mir async/await in C#.
```

**Rolle definieren:**
```
Du bist ein Windows-Experte. Wie optimiere ich WinUI 3 Performance?
```

**Schrittweise fragen:**
```
1. Was ist MVVM?
2. Zeige mir ein Beispiel
3. Wie nutze ich es in WinUI 3?
```

### Performance optimieren

**Schnelleres Modell verwenden:**
```powershell
ollama pull phi      # Sehr schnell, 2.7B Parameter
```

**GPU beschleunigen:**
- Ollama nutzt automatisch NVIDIA GPU falls verfügbar
- AMD/Intel: CPU-Only aber immer noch schnell

**Mehrere Modelle gleichzeitig:**
```powershell
# Terminal 1
ollama serve

# Terminal 2
ollama pull llama2 mistral phi codellama
```

## 📊 Beispiel-Konversation

```
USER: Erkläre mir WinUI 3 in einem Satz

JARVIS: WinUI 3 ist Microsofts modernes UI-Framework für 
Windows-Apps mit Fluent Design und nativer Performance.

USER: Zeige mir ein Hello World Beispiel

JARVIS: Hier ist ein einfaches WinUI 3 Hello World:

<Window
    x:Class="HelloWorld.MainWindow"
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">
    <StackPanel HorizontalAlignment="Center" 
                VerticalAlignment="Center">
        <TextBlock Text="Hello, World!" 
                   Style="{StaticResource TitleTextBlockStyle}"/>
    </StackPanel>
</Window>
```

## 🎯 Nächste Schritte

Mögliche Erweiterungen:

- [ ] **Conversation History** - Speichere Chat-Verlauf
- [ ] **Multiple Models** - Wechsel zwischen Modellen in UI
- [ ] **Voice Input** - Spracherkennung hinzufügen
- [ ] **System Prompts** - Vordefinierte Persönlichkeiten
- [ ] **Export Chat** - Konversationen als Markdown speichern
- [ ] **Dark/Light Mode Toggle** - Theme-Umschaltung

---

## ✅ Status

**AI-Integration:** ✅ Vollständig funktionsfähig!

**Getestet mit:**
- Ollama 0.1.x
- Models: llama2, mistral, phi
- Windows 11 + .NET 8

**Ready to use!** 🎉
