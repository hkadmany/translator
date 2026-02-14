import whisper
import tempfile
import subprocess
import os


def extract_audio(video_path: str) -> str:
    """Extract audio from video file to a temporary WAV file."""
    audio_path = tempfile.mktemp(suffix=".wav")
    subprocess.run(
        [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            audio_path, "-y"
        ],
        check=True,
        capture_output=True,
    )
    return audio_path


def transcribe(video_path: str, model_size: str = "base") -> list[dict]:
    """Transcribe video speech to timestamped text segments.

    Returns list of dicts with keys: start, end, text
    """
    audio_path = extract_audio(video_path)
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)
        segments = [
            {"start": seg["start"], "end": seg["end"], "text": seg["text"].strip()}
            for seg in result["segments"]
        ]
        return segments
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
