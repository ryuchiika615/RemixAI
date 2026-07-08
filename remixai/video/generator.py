import subprocess
import os
import json
from PIL import Image, ImageDraw, ImageFont
import math


ORIENTATIONS = {
    "vertical": (1080, 1920),
    "horizontal": (1920, 1080),
}


def generate_waveform_video(
    audio_path: str,
    output_path: str,
    orientation: str = "vertical",
    bg_color: str = "#0a0a0a",
    wave_color: str = "#00ff88",
    wave_mode: str = "line",
    fps: int = 30,
    bar_count: int = 64,
    fast: bool = False,
):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    width, height = ORIENTATIONS.get(orientation, ORIENTATIONS["vertical"])
    if fast:
        width //= 2
        height //= 2
        fps = 24
        bar_count = 32

    bg_hex = bg_color.lstrip("#")
    filter_complex = (
        f"color=c=0x{bg_hex}:s={width}x{height}:d={fps}[bg];"
        f"[0:a]showwaves=mode={wave_mode}:s={width}x{height}:n={bar_count}:"
        f"colors={wave_color}|{wave_color}|{wave_color}[wave];"
        f"[bg][wave]overlay=format=auto[v]"
    )

    preset = "ultrafast" if fast else "fast"
    crf = "28" if fast else "23"

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", crf,
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def generate_particle_video(
    audio_path: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
    bg_color: str = "#0a0a0a",
    particle_color: str = "#00ff88",
    fps: int = 30,
):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    bg_hex = bg_color.lstrip("#")
    pc_hex = particle_color.lstrip("#")

    filter_complex = (
        f"color=c=0x{bg_hex}:s={width}x{height}:d={fps}[bg];"
        f"[0:a]showwaves=mode=cline:s={width}x{height}:n=128:"
        f"colors=0x{pc_hex}@0.8|0x{pc_hex}@0.4|0x{pc_hex}@0.2[wave];"
        f"[bg][wave]overlay=format=auto,"
        f"drawbox=x=(w-2)/2:y=0:w=2:h=h:color=0x{pc_hex}@0.15:t=fill[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def _escape_ffmpeg_text(text: str) -> str:
    text = text.replace("'", "'\\\\''")
    text = text.replace(":", "\\:")
    text = text.replace("%", "\\\\%")
    return text


def add_metadata_text(
    video_path: str,
    output_path: str,
    title: str = "",
    channel: str = "",
    bpm: float = 0,
    font_path: str = None,
):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    drawtext_filter = []
    line_y = 100
    if title:
        safe = _escape_ffmpeg_text(title)
        drawtext_filter.append(
            f"drawtext=text='{safe}':fontcolor=white:fontsize=48:"
            f"x=(w-text_w)/2:y={line_y}:"
            f"box=1:boxcolor=black@0.4:boxborderw=10"
        )
        line_y += 80

    if channel:
        safe = _escape_ffmpeg_text(channel)
        drawtext_filter.append(
            f"drawtext=text='{safe}':fontcolor=white@0.6:fontsize=24:"
            f"x=20:y=20:"
            f"box=1:boxcolor=black@0.3:boxborderw=8"
        )

    if bpm:
        drawtext_filter.append(
            f"drawtext=text='{bpm} BPM':fontcolor=white@0.5:fontsize=32:"
            f"x=w-200:y=h-80"
        )

    if not drawtext_filter:
        return video_path

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", ",".join(drawtext_filter),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def generate_thumbnail(
    output_path: str,
    title: str = "Remix",
    channel: str = "AI de Pon!",
    bpm: float = 0,
    key: str = "",
    width: int = 1280,
    height: int = 720,
    bg_color: str = "#0a0a0a",
    accent_color: str = "#00ff88",
):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("arial.ttf", 56)
        font_medium = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 22)
        font_brand = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
        font_brand = font_large

    accent_rgb = tuple(int(accent_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    # ブランドバー - 上部
    bar_h = 50
    for x in range(0, width, 2):
        t = x / width
        r = int(accent_rgb[0] * (1 - t) + 0)
        g = int(accent_rgb[1] * (1 - t) + accent_rgb[1] * t)
        b = int(accent_rgb[2] * (1 - t) + 255 * t)
        draw.rectangle([x, 0, x + 2, bar_h], fill=(r, g, b, 200))

    # チャンネル名 (左上)
    bb = draw.textbbox((0, 0), f"♪ {channel}", font=font_brand)
    draw.text(
        (20, (bar_h - (bb[3] - bb[1])) // 2),
        f"♪ {channel}", fill="white", font=font_brand,
    )

    # 波形ライン (下部)
    bar_height = 6
    for i in range(0, width, 16):
        h = max(2, bar_height + int(math.sin(i * 0.04 + 1) * 8))
        alpha = max(80, min(220, 150 + int(math.sin(i * 0.08) * 60)))
        color = tuple(int(c * alpha // 255) for c in accent_rgb)
        y0 = height - 80 - h
        y1 = height - 80
        if y0 < y1:
            draw.rectangle([i, y0, i + 6, y1], fill=color)

    # 曲名 (中央)
    words = title.split()
    if len(words) > 2:
        line1 = " ".join(words[:len(words)//2])
        line2 = " ".join(words[len(words)//2:])
    else:
        line1 = title
        line2 = ""

    bb = draw.textbbox((0, 0), line1, font=font_large)
    draw.text(
        ((width - (bb[2] - bb[0])) // 2, height // 2 - 80),
        line1, fill="white", font=font_large,
    )
    if line2:
        bb = draw.textbbox((0, 0), line2, font=font_large)
        draw.text(
            ((width - (bb[2] - bb[0])) // 2, height // 2 + 10),
            line2, fill="white", font=font_large,
        )

    # BPM / Key
    meta_parts = []
    if bpm:
        meta_parts.append(f"{bpm} BPM")
    if key:
        meta_parts.append(key)
    meta = "  |  ".join(meta_parts)
    if meta:
        bb = draw.textbbox((0, 0), meta, font=font_small)
        draw.text(
            ((width - (bb[2] - bb[0])) // 2, height // 2 + 90),
            meta, fill="#aaaaaa", font=font_small,
        )

    # 再生ボタン
    btn_w, btn_h = 120, 40
    bx0 = (width - btn_w) // 2
    bx1 = bx0 + btn_w
    by0 = height - 150
    by1 = by0 + btn_h
    draw.rounded_rectangle(
        [bx0, by0, bx1, by1],
        radius=20, fill=accent_color,
    )
    bb = draw.textbbox((0, 0), "▶", font=font_medium)
    draw.text(
        ((width - (bb[2] - bb[0])) // 2, by0 + (btn_h - (bb[3] - bb[1])) // 2),
        "▶", fill="black", font=font_medium,
    )

    # フッター
    bb = draw.textbbox((0, 0), channel, font=font_small)
    draw.text(
        ((width - (bb[2] - bb[0])) // 2, height - 35),
        channel, fill="#666666", font=font_small,
    )

    img.save(output_path, quality=95)
    return output_path
