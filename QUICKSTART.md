# ⚡ JARVIS Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (2 minutes)
```powershell
cd "C:\Users\julia\OneDrive\Dokumente\GitHub\Jarvis"
pip install -r requirements.txt
```

### Step 2: Start Ollama (1 minute)
```powershell
# In Terminal 1
ollama serve
```

### Step 3: Launch JARVIS (30 seconds)
```powershell
# In Terminal 2 (or the same after Ollama is running)
python -m jarvis.main
```

### Step 4: Try Voice Cloning (1 minute)
1. In the JARVIS window, click **"🎙️ TEST SERVER"**
2. Wait 2 seconds - voice will auto-activate
3. Or click **"🎭 KLON AN/AUS"** to toggle manually

### Step 5: Start Talking! (30 seconds)
- **Type a command** → Click "AUSFÜHREN"
- **Or click "💬 GESPRÄCH"** → Talk naturally, JARVIS responds automatically!

---

## 🎯 Essential Commands

### Quick Commands
```
"Zeit" - What time is it?
"Datum" - What's the date?
"Systeminfo" - System status
"Diagnose" - Full system check
"Klonstatus" - Voice clone status
```

### Open Apps
```
"Öffne Browser"
"Öffne Rechner"
"Öffne Notepad"
"Öffne Explorer"
```

### Web Search
```
"Suche Python Tutorial"
"YouTube funny cats"
"Wikipedia Iron Man"
```

---

## 🎙️ Voice Modes Explained

### 🎤 **MIKROFON** (Dictation Mode)
- **Use for**: Typing long texts
- **How**: Click button, speak, text appears in input field
- **Finish**: Click "AUSFÜHREN" when done

### 🗣️ **SPRACHSTEUERUNG** (Voice Command Mode)
- **Use for**: Classic "Hey Jarvis" experience
- **How**: Click button, say "Jarvis" + your command
- **Example**: "Jarvis, open browser"

### 💬 **GESPRÄCH** (Conversation Mode)
- **Use for**: Natural back-and-forth conversation
- **How**: Click button, just talk naturally
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
