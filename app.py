import streamlit as st
import tempfile
import os

from transcriber import transcribe
from translator import translate_segments
from subtitle import generate_srt, burn_subtitles

st.set_page_config(page_title="Video Subtitle Translator", layout="centered")
st.title("Video Subtitle Translator")
st.write("Upload an English video, and get it back with burned-in Arabic subtitles.")

# --- Sidebar controls ---
with st.sidebar:
    st.header("Settings")
    model_size = st.selectbox(
        "Whisper model size",
        ["tiny", "base", "small", "medium", "large"],
        index=1,
        help="Smaller = faster, larger = more accurate",
    )
    font_size = st.slider("Subtitle font size", 16, 48, 24)
    bg_color = st.color_picker("Subtitle background color", "#000000")
    bg_opacity = st.slider("Background opacity %", 0, 100, 50, help="0 = fully transparent, 100 = fully solid")

    st.header("Logo")
    logo_file = st.file_uploader("Upload logo (PNG)", type=["png", "jpg", "jpeg"], key="logo")
    logo_scale = st.slider("Logo size %", 5, 50, 15, help="Percentage of video width")
    logo_opacity = st.slider("Logo opacity %", 10, 100, 100)
    logo_position = st.selectbox("Logo position", ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"])

# --- Main area ---
uploaded = st.file_uploader("Upload a video", type=["mp4", "mkv", "avi", "mov"])

if uploaded and st.button("Generate Subtitled Video"):
    # Save uploaded file to temp location
    suffix = os.path.splitext(uploaded.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        input_path = tmp.name

    srt_path = None
    output_path = None
    logo_path = None

    try:
        # Save logo if provided
        if logo_file:
            logo_suffix = os.path.splitext(logo_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=logo_suffix) as tmp_logo:
                tmp_logo.write(logo_file.read())
                logo_path = tmp_logo.name
        # Step 1: Transcribe
        with st.status("Transcribing speech...", expanded=True) as status:
            segments = transcribe(input_path, model_size)
            st.write(f"Found {len(segments)} segments.")
            status.update(label="Transcription complete", state="complete")

        # Step 2: Translate
        with st.status("Translating to Arabic...", expanded=True) as status:
            translated = translate_segments(segments)
            status.update(label="Translation complete", state="complete")

        # Step 3: Generate SRT
        srt_path = tempfile.mktemp(suffix=".srt")
        generate_srt(translated, srt_path)

        # Step 4: Burn subtitles
        output_path = tempfile.mktemp(suffix=".mp4")
        # Convert 0-100% opacity to 0-255 alpha value
        alpha = int(bg_opacity * 255 / 100)
        hex_with_alpha = f"{bg_color}{alpha:02x}"

        with st.status("Burning subtitles into video...", expanded=True) as status:
            burn_subtitles(
                input_path, srt_path, output_path, font_size, hex_with_alpha,
                logo_path=logo_path,
                logo_scale=logo_scale,
                logo_opacity=logo_opacity / 100,
                logo_position=logo_position,
            )
            status.update(label="Video processing complete", state="complete")

        # Step 5: Offer download
        st.success("Done! Your video is ready.")
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Subtitled Video",
                data=f,
                file_name=f"subtitled_{uploaded.name}",
                mime="video/mp4",
            )

    finally:
        # Cleanup temp files
        for path in [input_path, srt_path, output_path, logo_path]:
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass
