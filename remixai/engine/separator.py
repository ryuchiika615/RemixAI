import subprocess
import os
from pathlib import Path


def is_demucs_available():
    try:
        subprocess.run(["demucs", "--help"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False


def separate_stems(input_path: str, output_dir: str, model="htdemucs"):
    os.makedirs(output_dir, exist_ok=True)
    cmd = ["demucs", "-n", model, "-o", output_dir, input_path]
    subprocess.run(cmd, check=True)
    stem_dir = os.path.join(output_dir, model, Path(input_path).stem)
    return {
        "vocals": os.path.join(stem_dir, "vocals.wav"),
        "drums": os.path.join(stem_dir, "drums.wav"),
        "bass": os.path.join(stem_dir, "bass.wav"),
        "other": os.path.join(stem_dir, "other.wav"),
    }
