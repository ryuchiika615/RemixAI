import librosa
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def detect_bpm(y, sr):
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
    return float(np.round(float(tempo), 1))


def detect_key(y, sr):
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    major_corrs = [np.correlate(chroma_mean, np.roll(MAJOR_PROFILE, i))[0] for i in range(12)]
    minor_corrs = [np.correlate(chroma_mean, np.roll(MINOR_PROFILE, i))[0] for i in range(12)]

    major_max = max(major_corrs)
    minor_max = max(minor_corrs)
    major_idx = major_corrs.index(major_max)
    minor_idx = minor_corrs.index(minor_max)

    if major_max >= minor_max:
        return f"{NOTE_NAMES[major_idx]} major"
    else:
        return f"{NOTE_NAMES[minor_idx]} minor"


def analyze(file_path):
    y, sr = librosa.load(file_path, sr=None, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    return {
        "bpm": detect_bpm(y, sr),
        "key": detect_key(y, sr),
        "duration": round(duration, 2),
        "sample_rate": sr,
    }
