"""
Minimaler lokaler TTS-Testserver (Mock), kompatibel mit JARVIS' /tts Schnittstelle.
- Erzeugt eine einfache Sine-Wave-WAV-Datei als Platzhalter (keine echte Sprachsynthese).
- Dient dazu zu prüfen, ob JARVIS korrekt gegen einen lokalen Server spricht.

Starten:
  python tools/local_tts_server.py

Danach in JARVIS sagen: "Klonstatus" oder "Stimme klonen"

Hinweis: Dies ist nur ein Dummy. Für echte Stimm-Klon-Ausgabe einen echten Server (OpenVoice/XTTS v2) verwenden.
"""

from fastapi import FastAPI, Response  # type: ignore
from pydantic import BaseModel  # type: ignore
import numpy as np  # type: ignore
import io
import wave

app = FastAPI()

class TTSRequest(BaseModel):
    text: str
    speaker_wav: str | None = None
    sample_rate: int | None = 22050


def generate_tone_wav(text: str, sr: int = 22050) -> bytes:
    # Generiert 0.8 Sekunden Sinuston – Platzhalter
    duration = 0.8
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    freq = 440 if len(text) % 2 == 0 else 523
    audio = (0.2 * np.sin(2*np.pi*freq*t)).astype(np.float32)

    # In 16-bit WAV kodieren
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        # float32 -> int16
        pcm = (audio * 32767).astype(np.int16).tobytes()
        wf.writeframes(pcm)
    return buf.getvalue()

@app.post('/tts')
def tts(req: TTSRequest):
    wav_bytes = generate_tone_wav(req.text, req.sample_rate or 22050)
    return Response(content=wav_bytes, media_type='audio/wav')

if __name__ == '__main__':
    import uvicorn  # type: ignore
    uvicorn.run(app, host='127.0.0.1', port=5005)
