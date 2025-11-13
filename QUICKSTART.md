# 🚀 JARVIS WinUI 3 App - Schnellstart# ⚡ JARVIS Quick Start Guide



## ✅ Die App läuft jetzt!## 🚀 Get Started in 5 Minutes



## So startest du die App:### Step 1: Install Dependencies (2 minutes)

```powershell

### Option 1: Start-Skript (Empfohlen) ⭐cd "C:\Users\julia\OneDrive\Dokumente\GitHub\Jarvis"

pip install -r requirements.txt

**PowerShell:**```

```powershell

.\Start-JarvisApp.ps1### Step 2: Start Ollama (1 minute)

``````powershell

# In Terminal 1

**Batch (Doppelklick):**ollama serve

```batch```

Start-JarvisApp.bat

```### Step 3: Launch JARVIS (30 seconds)

```powershell

### Option 2: Manuell# In Terminal 2 (or the same after Ollama is running)

python -m jarvis.main

```powershell```

# 1. Kompilieren

cd JarvisApp### Step 4: Try Voice Cloning (1 minute)

dotnet build -c Release /p:Platform=x641. In the JARVIS window, click **"🎙️ TEST SERVER"**

2. Wait 2 seconds - voice will auto-activate

# 2. Starten3. Or click **"🎭 KLON AN/AUS"** to toggle manually

Start-Process "bin\x64\Release\net8.0-windows10.0.19041.0\JarvisApp.exe"

```### Step 5: Start Talking! (30 seconds)

- **Type a command** → Click "AUSFÜHREN"

## ⚠️ Wichtiger Hinweis- **Or click "💬 GESPRÄCH"** → Talk naturally, JARVIS responds automatically!



**WinUI 3 Apps können NICHT mit `dotnet run` gestartet werden!**---



❌ **Funktioniert NICHT:**## 🎯 Essential Commands

```powershell

dotnet run   # Fehler: "Unable to load DLL 'Microsoft.ui.xaml.dll'"### Quick Commands

``````

"Zeit" - What time is it?

❓ **Warum?**"Datum" - What's the date?

WinUI 3 benötigt zusätzliche Runtime-DLLs, die nur im Build-Output-Verzeichnis verfügbar sind."Systeminfo" - System status

"Diagnose" - Full system check

✅ **Funktioniert:**"Klonstatus" - Voice clone status

- ✅ `Start-JarvisApp.ps1` oder `Start-JarvisApp.bat````

- ✅ EXE direkt aus `bin/` Ordner starten

- ✅ Visual Studio F5### Open Apps

```

## 🎨 Was die App zeigt"Öffne Browser"

"Öffne Rechner"

- Moderne Windows 11 Fluent Design UI"Öffne Notepad"

- Eingabefeld für Benutzeranfragen"Öffne Explorer"

- Response-Bereich für Antworten```

- Statusleiste mit Echtzeit-Feedback

- Automatisches DPI Scaling (4K ready)### Web Search

```

## 🔧 Schnelle Problemlösung"Suche Python Tutorial"

"YouTube funny cats"

### Fehler: "Unable to load DLL 'Microsoft.ui.xaml.dll'""Wikipedia Iron Man"

```

**Lösung:** Verwende das Start-Skript:

```powershell---

.\Start-JarvisApp.ps1

```## 🎙️ Voice Modes Explained



### App startet nicht### 🎤 **MIKROFON** (Dictation Mode)

- **Use for**: Typing long texts

```powershell- **How**: Click button, speak, text appears in input field

# Clean und Rebuild- **Finish**: Click "AUSFÜHREN" when done

cd JarvisApp

dotnet clean### 🗣️ **SPRACHSTEUERUNG** (Voice Command Mode)

dotnet build -c Release /p:Platform=x64- **Use for**: Classic "Hey Jarvis" experience

.\Start-JarvisApp.ps1- **How**: Click button, say "Jarvis" + your command

```- **Example**: "Jarvis, open browser"



---### 💬 **GESPRÄCH** (Conversation Mode)

- **Use for**: Natural back-and-forth conversation

✅ **App erfolgreich gestartet!** Viel Spaß mit JARVIS!- **How**: Click button, just talk naturally

- **Stop**: Say "Stopp" or click button again

---

## 🎭 Voice Cloning Quick Guide

### Test Server (Simple)
1. Click **"🎙️ TEST SERVER"** in JARVIS
2. Status changes to **🟢 SERVER AN**
3. Voice automatically activates (🎭 GEKLONT)
4. Test: Say something and hear the cloned voice!

### Check Status Anytime
- **Visual**: Look at status section → **🎭 GEKLONT** (green) or **📢 STANDARD** (orange)
- **Command**: Type "Klonstatus" for detailed info

### Manual Toggle
- Click **"🎭 KLON AN/AUS"** to switch between voice modes

---

## 🔧 Troubleshooting (30 seconds each)

### ❌ "KI antwortet nicht"
```powershell
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

### ❌ "Mikrofon funktioniert nicht"
1. Windows Settings → Privacy → Microphone
2. Enable for Python/JARVIS
3. Set your mic as default device

### ❌ "Geklonte Stimme nicht verfügbar"
1. Check if test server is running (button shows **🔴 SERVER AN**)
2. If not, click **"🎙️ TEST SERVER"**
3. Or type "Klonstatus" for details

### ❌ "UI zu klein/groß"
- Just resize the window! UI scales automatically
- Works on any screen from 1280x720 to 4K

---

## 💡 Pro Tips

### Best Audio Quality
- Use a good microphone
- Quiet environment
- Speak clearly and at normal pace

### Faster Responses
- Use smaller AI models for speed
- Close unused applications
- Ensure SSD for faster loading

### Most Useful Features
1. **Conversation Mode** - Most natural interaction
2. **Diagnose Button** - Check everything at once
3. **Voice Clone Toggle** - Switch modes on the fly
4. **Test Server** - Validate voice cloning instantly

---

## 📱 Button Overview

### Main Controls
- **AUSFÜHREN** - Execute typed command
- **SPRACHSTEUERUNG** - Toggle "Jarvis" activation mode
- **🎤 MIKROFON** - Toggle dictation mode
- **💬 GESPRÄCH** - Toggle conversation mode
- **DIAGNOSE** - Run full system diagnostics

### Voice Controls
- **🎭 KLON AN/AUS** - Toggle cloned voice
- **🎙️ TEST SERVER** - Start/stop mock TTS server

---

## 🎯 Your First 5 Minutes

### Minute 1: Basic Command
1. Type: `Zeit`
2. Click: **AUSFÜHREN**
3. JARVIS tells you the time!

### Minute 2: Try Voice
1. Click: **💬 GESPRÄCH**
2. Say: "Hallo Jarvis"
3. JARVIS responds!

### Minute 3: Open Something
1. Say: "Öffne Browser"
2. Browser opens!

### Minute 4: Search the Web
1. Say: "Suche Python Tutorial"
2. Google opens with results!

### Minute 5: Try Voice Clone
1. Click: **🎙️ TEST SERVER**
2. Click: **🎭 KLON AN/AUS** (if not auto-activated)
3. Say anything → hear the cloned voice!

---

## 🎬 You're Ready!

You now have:
- ✅ JARVIS running
- ✅ Voice modes working
- ✅ Commands responding
- ✅ Optional voice cloning

**Next:** Check out [ULTIMATE_FEATURES.md](ULTIMATE_FEATURES.md) for advanced features!

---

**"I am Iron Man."** - Tony Stark

Made with ❤️ | Questions? Check the full [README.md](README.md)
