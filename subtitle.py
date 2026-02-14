import subprocess
import tempfile
import os
import arabic_reshaper


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(segments: list[dict], output_path: str) -> str:
    """Write translated segments to an SRT subtitle file with RTL support."""
    RLE = "\u202B"  # Right-to-Left Embedding
    PDF = "\u202C"  # Pop Directional Formatting
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            reshaped = arabic_reshaper.reshape(seg["text"])
            f.write(f"{i}\n")
            f.write(f"{_format_srt_time(seg['start'])} --> {_format_srt_time(seg['end'])}\n")
            f.write(f"{RLE}{reshaped}{PDF}\n\n")
    return output_path


def burn_subtitles(
    video_path: str,
    srt_path: str,
    output_path: str,
    font_size: int = 24,
    bg_color: str = "#80000000",
    logo_path: str | None = None,
    logo_scale: int = 15,
    logo_opacity: float = 1.0,
    logo_position: str = "Top-Left",
) -> str:
    """Burn SRT subtitles into video using ffmpeg, optionally with a logo overlay.

    Args:
        video_path: Path to source video.
        srt_path: Path to SRT file.
        output_path: Path for output video.
        font_size: Subtitle font size.
        bg_color: Background color hex string.
        logo_path: Optional path to logo image.
        logo_scale: Logo width as percentage of video width.
        logo_opacity: Logo opacity (0.0 to 1.0).
        logo_position: One of Top-Left, Top-Right, Bottom-Left, Bottom-Right.
    """
    ass_bg = _hex_to_ass(bg_color)
    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    style = (
        f"FontName=Arial,"
        f"FontSize={font_size},"
        f"BackColour={ass_bg},"
        f"BorderStyle=4,"
        f"Outline=0,"
        f"Shadow=0,"
        f"MarginV=30"
    )

    subtitle_filter = f"subtitles='{srt_escaped}':force_style='{style}'"

    if logo_path:
        logo_escaped = logo_path.replace("\\", "/").replace(":", "\\:")
        # Position mapping (10px padding from edges)
        positions = {
            "Top-Left": "x=10:y=10",
            "Top-Right": "x=W-w-10:y=10",
            "Bottom-Left": "x=10:y=H-h-10",
            "Bottom-Right": "x=W-w-10:y=H-h-10",
        }
        pos = positions.get(logo_position, "x=10:y=10")

        # Build filter: scale logo, apply opacity, overlay on video, then add subtitles
        # [1:v] is the logo input
        scale_filter = f"[1:v]scale=iw*{logo_scale}/100:-1"
        if logo_opacity < 1.0:
            scale_filter += f",format=rgba,colorchannelmixer=aa={logo_opacity}"
        scale_filter += "[logo]"

        filter_complex = (
            f"{scale_filter};"
            f"[0:v][logo]overlay={pos}[vid];"
            f"[vid]{subtitle_filter}"
        )

        subprocess.run(
            [
                "ffmpeg", "-i", video_path, "-i", logo_path,
                "-filter_complex", filter_complex,
                "-c:a", "copy",
                output_path, "-y"
            ],
            check=True,
            capture_output=True,
        )
    else:
        subprocess.run(
            [
                "ffmpeg", "-i", video_path,
                "-vf", subtitle_filter,
                "-c:a", "copy",
                output_path, "-y"
            ],
            check=True,
            capture_output=True,
        )
    return output_path


def _hex_to_ass(hex_color: str) -> str:
    """Convert #RRGGBB or #RRGGBBAA hex color to ASS &HAABBGGRR format.

    ASS alpha is inverted: 00 = fully opaque, FF = fully transparent.
    Input alpha: 00 = transparent, FF = opaque (standard).
    """
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = h[0:2], h[2:4], h[4:6]
        a_int = 128  # default semi-transparent
    elif len(h) == 8:
        r, g, b = h[0:2], h[2:4], h[4:6]
        a_int = int(h[6:8], 16)
    else:
        return "&H80000000"  # fallback
    # Invert alpha for ASS format
    ass_alpha = 255 - a_int
    return f"&H{ass_alpha:02X}{b.upper()}{g.upper()}{r.upper()}"
