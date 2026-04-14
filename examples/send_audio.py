"""
examples/send_audio.py
=======================
Send any audio file to the AI red team server and print the result.

Supported tasks:
    speech-to-text      — transcribe spoken audio (Whisper, Wav2Vec2)
    audio-classification — classify audio events (MIT AST)

Usage:
    python3 examples/send_audio.py recording.wav
    python3 examples/send_audio.py recording.wav --model whisper-small
    python3 examples/send_audio.py recording.wav --model audio-classifier
    python3 examples/send_audio.py recording.wav --host http://18.142.180.40:8000
    python3 examples/send_audio.py recording.wav --host http://18.142.180.40:8000 --model whisper-small
"""

import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


def main():
    parser = argparse.ArgumentParser(
        description="Send an audio file to the AI red team server"
    )
    parser.add_argument("audio",            help="Path to audio file (.wav, .mp3, .flac etc.)")
    parser.add_argument("--host",   default="http://localhost:8000")
    parser.add_argument("--model",  default="whisper-base",
                        help="Model key from models.yaml (default: whisper-base)")
    args = parser.parse_args()

    audio_path = Path(args.audio)

    if not audio_path.exists():
        print(f"Error: file not found: {audio_path}")
        sys.exit(1)

    if audio_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"Warning: '{audio_path.suffix}' may not be supported. "
              f"Recommended formats: {', '.join(SUPPORTED_EXTENSIONS)}")

    print(f"Sending  : {audio_path.name} ({audio_path.stat().st_size // 1024} KB)")
    print(f"Model    : {args.model}")
    print(f"Host     : {args.host}")
    print()

    with open(audio_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model":        args.model,
        "audio_base64": b64,
    }

    data = json.dumps(payload).encode()
    req  = urllib.request.Request(
        f"{args.host.rstrip('/')}/inference",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"Server error {e.code}: {e.read().decode()}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}")
        print(f"Is the server running at {args.host}?")
        sys.exit(1)

    print(f"model  : {result['model']}")
    print(f"task   : {result['task']}")
    print(f"device : {result['device']}")
    print(f"output : {result['output']}")


if __name__ == "__main__":
    main()
