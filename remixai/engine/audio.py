import subprocess
import os


def convert_to_wav(input_path: str, output_path: str = None):
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".wav"
    cmd = ["ffmpeg", "-y", "-i", input_path, "-acodec", "pcm_s16le", "-ar", "44100", output_path]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def get_duration(input_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        input_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def trim(input_path: str, output_path: str, start: float = 0, duration: float = 30):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ss", str(start),
        "-t", str(duration),
        "-acodec", "libmp3lame", "-q:a", "2",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
