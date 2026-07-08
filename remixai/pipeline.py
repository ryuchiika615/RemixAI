import os
import re
import json
from pathlib import Path
from .engine import analyze, apply_effects, get_theme_effects, trim
from .video import generate_waveform_video, add_metadata_text, generate_thumbnail, ORIENTATIONS


CHANNEL_NAME = "AI de Pon!"
CHANNEL_SUB = "AIでポン！ ～自動リミックスチャンネル～"
IS_HF_SPACE = os.environ.get("SPACE_ID") is not None


def safe_stem(path: str) -> str:
    stem = Path(path).stem
    stem = re.sub(r'[\\/*?:"<>|\x00-\x1f]', "", stem)
    stem = re.sub(r'\s+', " ", stem).strip()
    if not stem:
        stem = "audio"
    return stem


def safe_print(text: str):
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        print(text.encode("utf-8", errors="replace").decode("utf-8", errors="replace"), flush=True)


def run_pipeline(
    input_path: str,
    theme: str = "original",
    output_dir: str = "output",
    short_duration: int = 30,
    orientation: str = "vertical",
    start_offset: float = 0,
    on_progress=None,
):
    os.makedirs(output_dir, exist_ok=True)
    stem = safe_stem(input_path)

    def report(step, msg, pct):
        full = f"[{step}/6] {msg}"
        safe_print(full)
        if on_progress:
            on_progress(pct, full)

    report(1, "解析中...", 0.05)
    info = analyze(input_path)
    safe_print(f"  BPM: {info['bpm']}, Key: {info['key']}, Duration: {info['duration']}s")

    report(2, f"テーマ適用: {theme}", 0.2)
    fx = get_theme_effects(theme)
    remixed_path = os.path.join(output_dir, f"{stem}_remixed.mp3")
    apply_effects(input_path, remixed_path, fx)

    report(3, f"トリミング: {short_duration}秒 (開始位置: {start_offset}秒)", 0.35)
    trimmed_path = os.path.join(output_dir, f"{stem}_trimmed.mp3")
    trim(remixed_path, trimmed_path, start=start_offset, duration=short_duration)

    report(4, "動画生成中...", 0.5)
    video_path = os.path.join(output_dir, f"{stem}_video.mp4")

    palette_map = {
        "club": ("#0a001a", "#ff00ff"),
        "lofi": ("#1a1a2e", "#e2b714"),
        "night_drive": ("#000814", "#00d4ff"),
        "summer_fes": ("#001a0a", "#ff6600"),
        "edm": ("#0a0a00", "#ff0044"),
        "vaporwave_80s": ("#1a0020", "#ff69b4"),
        "citypop": ("#1a0a00", "#ffa500"),
        "nightcore": ("#0a0010", "#ff1493"),
        "phonk": ("#0a0000", "#8b0000"),
        "jazz_hiphop": ("#0a0a05", "#d4a574"),
        "original": ("#0a0a0a", "#00ff88"),
    }
    bg_color, wave_color = palette_map.get(theme, palette_map["original"])

    generate_waveform_video(
        trimmed_path, video_path,
        orientation=orientation,
        bg_color=bg_color, wave_color=wave_color,
        fast=IS_HF_SPACE,
    )

    report(5, "メタデータ追加中...", 0.75)
    labeled_path = os.path.join(output_dir, f"{stem}_final.mp4")
    title_display = stem.replace("_", " ").replace("-", " ")
    title_display = title_display[:80] if len(title_display) > 80 else title_display
    add_metadata_text(
        video_path, labeled_path,
        title=title_display,
        channel=CHANNEL_NAME,
        bpm=info["bpm"],
    )

    report(6, "サムネイル生成中...", 0.9)
    thumb_path = os.path.join(output_dir, f"{stem}_thumb.png")
    generate_thumbnail(
        thumb_path,
        title=title_display,
        channel=CHANNEL_NAME,
        bpm=info["bpm"],
        key=info["key"],
        bg_color=bg_color,
        accent_color=wave_color,
    )

    result = {
        "title": title_display,
        "bpm": info["bpm"],
        "key": info["key"],
        "duration": info["duration"],
        "theme": theme,
        "orientation": orientation,
        "video": labeled_path,
        "thumbnail": thumb_path,
        "remixed_audio": remixed_path,
    }

    info_path = os.path.join(output_dir, f"{stem}_info.json")
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    if on_progress:
        on_progress(1.0, "Done!")

    safe_print(f"\nDone! Output:")
    for k, v in result.items():
        safe_print(f"  {k}: {v}")

    return result
