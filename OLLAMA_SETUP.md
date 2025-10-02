# Ollama Setup für Windows

## Voraussetzungen
- Windows 10 oder neuer
- Administratorrechte

## Installation
1. Lade das Ollama-Installationsprogramm für Windows von der offiziellen Website herunter:
	[https://ollama.com/download](https://ollama.com/download)
2. Führe die heruntergeladene Datei aus und folge den Installationsanweisungen.
3. Nach der Installation kannst du im Terminal prüfen, ob Ollama korrekt installiert wurde:
	```powershell
	ollama --version
	```

## Automatisiertes Setup (Batch-Skript)
Alternativ kannst du das mitgelieferte Skript `install_ollama.bat` ausführen, um die Installation zu starten:
```powershell
./install_ollama.bat
```
Das Skript öffnet die Ollama-Downloadseite im Browser.

---
Weitere Informationen findest du in der offiziellen [Ollama Dokumentation](https://ollama.com/docs/).
# Ollama Integration Anleitung

## Schritt 1: Ollama Server starten

Öffnen Sie ein neues Terminal/PowerShell-Fenster und führen Sie aus:

```powershell
# Falls Ollama nicht im PATH ist, verwenden Sie den vollständigen Pfad:
& "C:\Users\julia\AppData\Local\Programs\Ollama\ollama.exe" serve

# Oder falls im PATH verfügbar:
ollama serve
```

Dies startet den Ollama-Server auf `localhost:11434`

## Schritt 2: Modell verwenden

Ihr JARVIS ist bereits konfiguriert für:
- **Modell**: `deepseek-r1:1.5b`
- **API**: `http://localhost:11434/api/generate`

## Schritt 3: Verfügbare Befehle

### AI-Modell verwalten:
- **"Verfügbare Modelle"** - Zeigt alle installierten Modelle
- **"Modell [Name]"** - Wechselt zu einem anderen Modell
- **"AI Modell"** - Zeigt verfügbare Modelle

### Beispiele:
```
"Verfügbare Modelle"
"Modell llama2"
"Modell deepseek-r1:1.5b"
```

## Schritt 4: Testen

1. Starten Sie JARVIS: `python -m jarvis`
2. Aktivieren Sie den Gesprächsmodus: "💬 GESPRÄCH" Button
3. Sprechen Sie: "Hallo JARVIS, wie geht es dir?"

## Fehlerbehebung

### Fehler: "Ollama ist nicht erreichbar"
- Stellen Sie sicher, dass `ollama serve` läuft
- Prüfen Sie, ob Port 11434 frei ist

### Fehler: "Modell nicht gefunden"
- Prüfen Sie installierte Modelle: `ollama list`
- Installieren Sie Ihr Modell: `ollama pull deepseek-r1:1.5b`

### Langsame Antworten
- Das ist normal bei lokalen Modellen
- Kleinere Modelle sind schneller
- GPU-Beschleunigung verbessert Performance

## Modell-Empfehlungen

**Für bessere Performance:**
- `deepseek-r1:1.5b` (Ihr aktuelles, gut für Deutsche Sprache)
- `llama3.2:1b` (Schneller, weniger Speicherverbrauch)
- `phi3:3.8b` (Guter Kompromiss)

**Für bessere Qualität (aber langsamer):**
- `llama3.2:3b`
- `deepseek-r1:7b` (falls Sie genug RAM haben)

## Status prüfen

JARVIS zeigt beim Start automatisch:
- ✅ Ollama-Verbindung
- 📋 Verfügbare Modelle
- ⚙️ Aktuelles Modell