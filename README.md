# Jarvis AI Assistant

A local AI assistant inspired by Iron Man's Jarvis, built as a Windows application with voice control and GUI.

## Features

- Local AI integration via API (e.g., Ollama)
- Voice input and output with activation word "Jarvis"
- Modern minimalist GUI dashboard
- Windows program integration
- Runs as a standalone Windows app

## Installation

1. Clone the repository
2. Install Python 3.8+
3. Install dependencies: `pip install -r requirements.txt`
4. Install a local AI (e.g., Ollama with llama2 model)
5. Run: `python -m jarvis`

## Building Windows App

Use PyInstaller to create an executable:

```
pip install pyinstaller
pyinstaller --onefile --windowed jarvis/__main__.py
```

## Usage

- Launch the app
- Use the GUI to send commands
- Say "Jarvis" followed by your command for voice control
- The AI will respond via voice and text

## Configuration

- Change AI model in `ai.py`
- Adjust activation word in `voice.py`
- Add more Windows integrations in `windows_integration.py`