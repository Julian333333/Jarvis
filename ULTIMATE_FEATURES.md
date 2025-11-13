# 🚀 JARVIS - Ultimate Features Guide

## 🎯 Was macht JARVIS besonders?

JARVIS ist Ihr persönlicher KI-Assistent nach dem Vorbild von Iron Man's JARVIS - entwickelt für maximale Funktionalität, Privatsphäre und Benutzerfreundlichkeit auf Windows 11.

## ✨ Haupt-Features

### 🎭 **Erweiterte Sprachsteuerung**

#### 1. **Drei Modi der Spracherkennung**
- **🎤 MIKROFON-MODUS**: Kontinuierliche Sprach-zu-Text Eingabe
  - Perfekt zum Diktieren längerer Texte
  - Text erscheint live im Eingabefeld
  - Drücken Sie "AUSFÜHREN" wenn fertig

- **🗣️ SPRACHSTEUERUNG**: Aktivierungswort "Jarvis"
  - Wartet auf das Wort "Jarvis" und führt dann Befehle aus
  - Klassischer Jarvis-Modus wie im Film

- **💬 GESPRÄCH**: Kontinuierlicher Konversationsmodus
  - Natürliche Unterhaltung ohne Aktivierungswort
  - JARVIS hört kontinuierlich zu und antwortet automatisch
  - Ideal für längere Interaktionen

### 🎙️ **Lokale Stimm-Klonierung**

#### Ihre Stimme - Ihre Privatsphäre
- **100% offline**: Keine Cloud, keine externen Server
- **Einfache Aktivierung**: Ein Knopfdruck
- **Auto-Erkennung**: Wenn der lokale TTS-Server läuft, aktiviert sich die geklonte Stimme automatisch
- **Fallback**: Wechselt automatisch zu Standard-TTS falls Server nicht verfügbar

#### So funktioniert's:
1. **Test-Server starten**: Klicken Sie auf "🎙️ TEST SERVER"
2. **Auto-Aktivierung**: JARVIS erkennt den Server und aktiviert Ihre Stimme automatisch
3. **Manuelle Steuerung**: Mit "🎭 KLON AN/AUS" zwischen Modi wechseln

#### Status-Anzeige:
- 🎭 **GEKLONT** (grün): Ihre geklonte Stimme ist aktiv
- 📢 **STANDARD** (orange): Standard deutsche TTS

### 🤖 **Intelligente KI-Integration**

#### Lokales Ollama
- Läuft komplett auf Ihrem PC
- Keine Internet-Verbindung nötig
- Unterstützt mehrere Modelle (llama3.2:3b, deepseek-r1:1.5b, etc.)
- **Asynchrone Verarbeitung**: UI bleibt responsive während die KI nachdenkt

#### Persönlichkeit
- Spricht Sie als "Daddy" an (wie Tony Stark)
- Kontextbewusste Antworten basierend auf Tageszeit
- Professionell und hilfsbereit

### 📱 **Responsive Modernes UI**

#### Dynamische Anpassung
- **Automatische Skalierung**: Passt sich Ihrer Bildschirmgröße an
- **Reflow-Logik**: Elemente ordnen sich vertikal an bei schmalen Fenstern
- **High-DPI Support**: Perfekt für 4K und moderne Displays
- **Windows 11 Integration**: Native Taskleisten-Gruppierung

#### Echtzeit-Status
- **KI KERN**: Status der AI-Verbindung
- **SPRACHE**: Aktuelle Spracherkennungs-Modi
- **SYSTEM**: CPU und RAM Überwachung

### 🔧 **Erweiterte Befehle**

#### System-Steuerung
```
"Zeit" / "Datum" - Aktuelle Zeit/Datum mit kontextbezogener Begrüßung
"Systeminfo" - Detaillierte Performance-Analyse
"Herunterfahren" / "Neustart" - System-Steuerung
"Diagnose" - Vollständige System-Diagnose
```

#### Anwendungen
```
"Öffne Browser/Rechner/Notepad/Explorer"
"Starte Chrome/Firefox/PowerShell"
```

#### Web & Suche
```
"Suche [Begriff]" - Google Suche
"YouTube [Begriff]" - YouTube Suche
"Wikipedia [Begriff]" - Wikipedia Artikel
```

#### Stimm-Klonierung
```
"Stimme klonen" - Aktiviert geklonte Stimme
"Klonstimme deaktivieren" - Zurück zu Standard
"Klonstatus" - Zeigt detaillierten Status
"Stimmprobe abspielen" - Spielt Ihr Stimm-Sample ab
```

### 🎯 **Intelligente Features**

#### Auto-Recovery
- **Periodische Server-Prüfung**: Alle 30 Sekunden
- **Auto-Aktivierung**: Geklonte Stimme aktiviert sich automatisch wenn Server verfügbar wird
- **Graceful Fallback**: Wechselt zu Standard-TTS bei Problemen

#### Performance-Optimierung
- **Asynchrone AI-Calls**: UI friert nie ein
- **Thread-basierte Sprachausgabe**: Blockiert nicht die Hauptanwendung
- **Effiziente Speicherverwaltung**: Minimal CPU/RAM Verbrauch

#### Diagnose-System
- **AI-Check**: Verbindung und verfügbare Modelle
- **Voice-Check**: TTS-Status und Server-Erreichbarkeit
- **System-Check**: CPU, RAM und Performance-Metriken

## 🚀 Quick Start

### 1. Installation
```powershell
cd "C:\Users\julia\OneDrive\Dokumente\GitHub\Jarvis"
pip install -r requirements.txt
```

### 2. Ollama Setup (für lokale KI)
```powershell
# Installiere Ollama
winget install Ollama.Ollama

# Starte Ollama Service
ollama serve

# Lade ein Modell (in neuem Terminal)
ollama pull llama3.2:3b
```

### 3. JARVIS starten
```powershell
python -m jarvis.main
```

### 4. (Optional) Test-Server für geklonte Stimme
Klicken Sie im JARVIS UI auf "🎙️ TEST SERVER" oder:
```powershell
python tools/local_tts_server.py
```

## 🎮 Verwendung

### Grundlegende Interaktion
1. **Text eingeben**: Tippen Sie Ihren Befehl und klicken "AUSFÜHREN"
2. **Spracheingabe**: Aktivieren Sie einen der drei Sprach-Modi
3. **Diagnose**: Klicken Sie "DIAGNOSE" für vollständigen System-Check

### Stimm-Klonierung nutzen
1. Ihre Stimmprobe liegt bereits als `Danielv1.wav` im Projekt
2. Klicken Sie "🎙️ TEST SERVER" um den Mock-Server zu starten
3. JARVIS aktiviert automatisch die geklonte Stimme
4. Mit "🎭 KLON AN/AUS" können Sie manuell umschalten

### Konversationsmodus
1. Klicken Sie "💬 GESPRÄCH"
2. Sprechen Sie natürlich - kein Aktivierungswort nötig
3. JARVIS antwortet automatisch
4. Sagen Sie "Stopp" oder "Beenden" zum Ausschalten

## 🔥 Fortgeschrittene Features

### Eigene Stimme nutzen
1. Nehmen Sie 10-30 Sekunden klare Sprache auf (WAV, 16kHz mono bevorzugt)
2. Speichern Sie als `voices/user/samples/reference.wav`
3. JARVIS erkennt die neue Datei automatisch beim nächsten Start

### Echter TTS-Server (für echte Stimm-Klonierung)
Der Test-Server generiert nur einen Ton. Für echte Stimm-Klonierung:
1. Installieren Sie Coqui TTS oder XTTS v2
2. Konfigurieren Sie einen Endpunkt auf `http://127.0.0.1:5005/tts`
3. JARVIS verbindet sich automatisch

### Modell wechseln
```
"Modell wechseln zu deepseek-r1:1.5b"
"Verfügbare Modelle"
```

## 📊 Status-Indikatoren

### Farb-Codes
- 🟢 **Grün**: Optimal/Aktiv
- 🟠 **Orange**: Bereit/Standby
- 🔴 **Rot**: Aktiv/Hört zu
- 🔵 **Blau**: System-Nachrichten

### Chat-Nachrichten
- `[SYSTEM]` - System-Status (blau)
- `[BENUTZER]` - Ihre Eingabe (cyan)
- `[JARVIS]` - JARVIS Antwort (grün)
- `[SPRACHE]` - Sprachbefehl (orange)
- `[MIKROFON]` - Diktierte Eingabe (orange)
- `[SIE]` - Im Konversationsmodus (rot-orange)
- `[STIMME]` - Stimm-Status (orange)
- `[AUTO]` - Automatische Aktionen (grün)
- `[SERVER]` - Server-Status (grün/orange)

## 🛠️ Fehlerbehebung

### KI antwortet nicht
1. Prüfen Sie ob Ollama läuft: `ollama list`
2. Klicken Sie "DIAGNOSE"
3. Starten Sie Ollama neu wenn nötig

### Geklonte Stimme funktioniert nicht
1. Prüfen Sie "Klonstatus" Befehl oder den Status-Indikator
2. Starten Sie den Test-Server: "🎙️ TEST SERVER"
3. Warten Sie 2 Sekunden für Auto-Aktivierung
4. Oder klicken Sie "🎭 KLON AN/AUS"

### Mikrofon wird nicht erkannt
1. Prüfen Sie Windows Mikrofon-Berechtigungen
2. Stellen Sie sicher, dass das richtige Mikrofon als Standard eingestellt ist
3. Testen Sie mit Windows Sprachrekorder

### UI zu klein/groß
- JARVIS passt sich automatisch an Fenstergröße an
- Ziehen Sie das Fenster auf gewünschte Größe
- Schriftgrößen skalieren automatisch

## 💡 Tipps & Tricks

### Beste Spracherkennung
- Sprechen Sie klar und deutlich
- Vermeiden Sie Hintergrundgeräusche
- Verwenden Sie ein gutes Mikrofon

### Optimale Performance
- Schließen Sie andere ressourcen-intensive Programme
- Verwenden Sie SSD für schnellere Ladezeiten
- 16GB RAM empfohlen für große AI-Modelle

### Persönlichkeit anpassen
Die AI lernt aus Ihren Unterhaltungen. Je mehr Sie mit JARVIS interagieren, desto besser passt sich die Persönlichkeit an Ihren Stil an.

## 🎬 Wie im Film

JARVIS ist inspiriert von Tony Stark's legendärem AI-Assistenten:
- ✅ Spricht Sie respektvoll als "Daddy" an
- ✅ Kontextbewusste, intelligente Antworten
- ✅ Proaktive Hilfe und Vorschläge
- ✅ Vollständige Systemkontrolle
- ✅ Futuristische UI mit High-Tech Ästhetik
- ✅ Lokale Privatsphäre (keine Stark Industries Server nötig!)

## 🚧 Roadmap

### Geplante Features
- [ ] Integration mit mehr lokalen AI-Modellen
- [ ] Erweiterte Gesichtserkennung
- [ ] Smart Home Integration
- [ ] E-Mail und Kalender Management
- [ ] Code-Generierung und Entwickler-Tools
- [ ] Musik-Steuerung
- [ ] Erweiterte Windows-Integration
- [ ] Plugin-System für eigene Befehle

## 📝 Lizenz & Credits

Entwickelt mit ❤️ für alle Iron Man Fans da draußen.

**Technologien:**
- PyQt5 - UI Framework
- Ollama - Lokale AI
- pyttsx3 - Text-to-Speech
- SpeechRecognition - Spracherkennung
- FastAPI - Optional TTS Server

---

**"Sometimes you gotta run before you can walk."** - Tony Stark

Viel Spaß mit Ihrem persönlichen JARVIS! 🚀
