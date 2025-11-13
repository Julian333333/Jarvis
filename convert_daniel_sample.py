import os
from jarvis.audio_utils import convert_audio_to_wav, default_user_sample_path

def main():
    project_root = os.path.dirname(__file__)
    src = os.path.join(project_root, 'Danielv1.mp3')
    dst = default_user_sample_path()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    ok = convert_audio_to_wav(src, dst, sample_rate=16000, channels=1)
    if ok:
        print(f"✓ Konvertiert: {src} -> {dst}")
    else:
        print("❌ Konvertierung fehlgeschlagen. Bitte ffmpeg installieren oder eine WAV-Datei bereitstellen.")

if __name__ == '__main__':
    main()
