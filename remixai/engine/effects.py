import subprocess
import os
import json
from pathlib import Path
from tempfile import NamedTemporaryFile


DEFAULT_EFFECTS = {
    "reverb": 0.0,
    "bass_boost": 0.0,
    "high_boost": 0.0,
    "low_cut": 0,
    "high_cut": 0,
    "tempo": 1.0,
    "pitch": 0,
    "volume": 1.0,
}


def build_filter_chain(effects: dict) -> list:
    filters = []

    if effects.get("low_cut", 0) > 0:
        filters.append(f"highpass=f={effects['low_cut']}")
    if effects.get("high_cut", 0) > 0:
        filters.append(f"lowpass=f={effects['high_cut']}")

    if effects.get("bass_boost", 0) > 0:
        filters.append(f"equalizer=f=100:t=q:w=1:g={effects['bass_boost']}")
    if effects.get("high_boost", 0) > 0:
        filters.append(f"equalizer=f=8000:t=q:w=1:g={effects['high_boost']}")

    if effects.get("reverb", 0) > 0:
        r = effects["reverb"]
        delay = int(200 * r)
        filters.append(f"aecho=0.8:0.88:{delay}|{delay+100}:0.4|0.3")

    tempo = effects.get("tempo", 1.0)
    pitch = effects.get("pitch", 0)
    if tempo != 1.0 or pitch != 0:
        if pitch != 0:
            pitch_factor = 2 ** (pitch / 12)
            filters.append(f"rubberband=tempo={tempo}:pitch={pitch_factor}:pitchq=quality")
        else:
            filters.append(f"atempo={tempo}")

    vol = effects.get("volume", 1.0)
    if vol != 1.0:
        filters.append(f"volume={vol}")

    return filters


def apply_effects(input_path: str, output_path: str, effects: dict = None):
    if effects is None:
        effects = DEFAULT_EFFECTS.copy()

    merged = DEFAULT_EFFECTS.copy()
    merged.update(effects)

    filters = build_filter_chain(merged)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
    ]

    if filters:
        cmd += ["-af", ",".join(filters)]

    cmd += ["-acodec", "libmp3lame", "-q:a", "2", output_path]

    subprocess.run(cmd, check=True, capture_output=True)

    return output_path


def apply_effects_to_segments(input_path: str, segments: list[dict], output_dir: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    outputs = []
    for i, seg in enumerate(segments):
        out = os.path.join(output_dir, f"segment_{i:03d}.mp3")
        apply_effects(input_path, out, seg.get("effects"))
        outputs.append(out)
    return outputs


THEME_MAP = {
    "original": {},
    "club": {
        "bass_boost": 6,
        "high_boost": 3,
        "low_cut": 30,
        "reverb": 0.3,
        "tempo": 1.15,
    },
    "lofi": {
        "low_cut": 50,
        "high_cut": 8000,
        "reverb": 0.4,
        "tempo": 0.85,
    },
    "night_drive": {
        "bass_boost": 8,
        "low_cut": 25,
        "reverb": 0.2,
        "tempo": 0.95,
    },
    "summer_fes": {
        "high_boost": 4,
        "bass_boost": 3,
        "tempo": 1.1,
        "reverb": 0.15,
    },
    "edm": {
        "bass_boost": 10,
        "high_boost": 5,
        "low_cut": 20,
        "tempo": 1.2,
        "reverb": 0.25,
    },
    "vaporwave_80s": {
        "low_cut": 40,
        "high_cut": 12000,
        "reverb": 0.5,
        "tempo": 0.8,
        "pitch": -2,
    },
    "citypop": {
        "bass_boost": 4,
        "high_boost": 2,
        "reverb": 0.25,
        "tempo": 1.02,
    },
    "nightcore": {
        "tempo": 1.3,
        "pitch": 4,
        "bass_boost": 2,
    },
    "phonk": {
        "bass_boost": 12,
        "low_cut": 15,
        "high_cut": 10000,
        "tempo": 1.25,
        "reverb": 0.15,
    },
    "jazz_hiphop": {
        "low_cut": 50,
        "high_cut": 9000,
        "reverb": 0.3,
        "tempo": 0.88,
    },
}

THEMES = list(THEME_MAP.keys())


def get_theme_effects(theme: str) -> dict:
    return THEME_MAP.get(theme, THEME_MAP["original"])
