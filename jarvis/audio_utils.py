"""
Audio Utilities for JARVIS
- Convert arbitrary audio (e.g., MP3) to 16kHz mono WAV for voice cloning.
"""

import os
import shutil
import subprocess
from typing import Optional


def convert_audio_to_wav(input_path: str, output_path: str, sample_rate: int = 16000, channels: int = 1) -> bool:
    """Convert audio file to WAV 16kHz mono using ffmpeg; fallback to torchaudio if ffmpeg not found.

    Returns True on success, False otherwise.
    """
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Try ffmpeg first
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        cmd = [ffmpeg, '-y', '-i', input_path, '-ac', str(channels), '-ar', str(sample_rate), output_path]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            pass

    # Fallback to torchaudio + soundfile
    try:
        import torchaudio  # type: ignore
        import torch  # type: ignore
        import soundfile as sf  # type: ignore

        waveform, sr = torchaudio.load(input_path)  # shape: [channels, samples]
        # Convert to mono
        if waveform.ndim == 2 and waveform.size(0) > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        # Resample if needed
        if sr != sample_rate:
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=sample_rate)
            waveform = resampler(waveform)
            sr = sample_rate
        # Ensure correct channels
        if channels == 1 and waveform.size(0) != 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        # Save as WAV
        wav_np = waveform.squeeze(0).cpu().numpy()
        sf.write(output_path, wav_np, sr, subtype='PCM_16')
        return True
    except Exception:
        return False


def default_user_sample_path() -> str:
    """Return default path where we store user's reference sample WAV."""
    here = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(here, 'voices', 'user', 'samples', 'reference.wav')
