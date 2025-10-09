# Lokales Voice-Cloning für JARVIS (Datenschutzfreundlich)

Dieses Setup ermöglicht es, deine eigene Stimme lokal zu klonen und in JARVIS zu verwenden – ohne Cloud.

## Überblick
- Du startest einen lokalen TTS-Server (z.B. OpenVoice oder XTTS v2 Wrapper) auf http://127.0.0.1:5005/tts
- JARVIS sendet Text + Pfad zu deiner Stimmprobe (WAV) und erhält ein WAV zurück
- Fallback auf deutsche Microsoft Hedda TTS, wenn der Server nicht läuft

## Dateien/Endpoints
- Erwarteter Endpoint: POST http://127.0.0.1:5005/tts
- Request-Body (JSON):
  {
    "text": "Hallo Welt",
    "speaker_wav": "C:\\Pfad\\zu\\deiner_stimme.wav",
    "sample_rate": 22050
  }
- Response: WAV-Bytes (audio/wav)

## Stimmprobe aufnehmen (Windows)
1. Öffne die Sprachrekorder-App oder nutze PowerShell:
```powershell
# 10 Sekunden Aufnahme (benötigt ffmpeg in PATH)
ffmpeg -f dshow -i audio="Mikrofon (dein Gerät)" -t 10 -ac 1 -ar 16000 reference.wav
```
2. Lege die Datei unter:
   Jarvis/voices/user/samples/reference.wav

## JARVIS-Befehle
 - "stimmprobe abspielen" — Spielt die aktuelle Probe lokal ab
 - "klonstatus" — Zeigt Modus, Erreichbarkeit des Servers und die aktuelle Stimmprobe


## Schneller Funktionstest (Mock-Server)
Wenn du nur prüfen willst, ob JARVIS korrekt mit einem lokalen /tts-Endpoint spricht, starte den eingebauten Dummy-Server:

1) Abhängigkeiten installieren (falls noch nicht vorhanden): fastapi, uvicorn, numpy
2) Starten:
  python tools/local_tts_server.py
3) In JARVIS sagen: "klonstatus" oder "stimme klonen" – es sollte ein kurzer Ton abgespielt werden.
## Hinweise
- Stelle sicher, dass der lokale TTS-Server läuft, bevor du "stimme klonen" sagst
- Empfohlen: 16kHz, Mono WAV als Stimmprobe
- Bei Fehlern nutzt JARVIS automatisch die Standard-TTS

## Beispiel-Server (Info)
- OpenVoice (MMS): https://github.com/myshell-ai/OpenVoice
- Coqui XTTS v2 Webserver Wrapper

(Die eigentliche Modell-Installation geschieht separat; JARVIS benötigt nur den laufenden Server.)
