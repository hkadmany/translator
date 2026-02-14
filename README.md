# Video Subtitle Translator

Upload an English video and get it back with burned-in Arabic subtitles.

## Prerequisites

- **Python 3.10+**
- **FFmpeg** installed and on PATH:
  - **Windows**: `winget install Gyan.FFmpeg` (restart terminal after install)
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `sudo apt install ffmpeg`

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

1. Upload a video (mp4, mkv, avi, mov)
2. Choose Whisper model size (tiny = fast, large = accurate)
3. Adjust subtitle font size and background opacity
4. Click **Generate Subtitled Video**
5. Download the result

## Tech Stack

- **Streamlit** — browser-based UI
- **OpenAI Whisper** — local speech-to-text
- **Deep Translator** — English to Arabic translation
- **FFmpeg** — subtitle burning into video
