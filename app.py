import sys, os, shutil, subprocess, urllib.request, tarfile, glob, stat, time
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["GRADIO_QUIET"] = "True"


def _ensure_ffmpeg():
    if shutil.which("ffmpeg"):
        return
    print("ffmpeg not found, downloading static build...", flush=True)
    bin_dir = os.path.join(os.path.dirname(__file__), "bin")
    os.makedirs(bin_dir, exist_ok=True)
    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    tar_path = os.path.join(bin_dir, "ffmpeg.tar.xz")
    urllib.request.urlretrieve(url, tar_path)
    with tarfile.open(tar_path) as tar:
        tar.extractall(path=bin_dir)
    os.remove(tar_path)
    for d in glob.glob(os.path.join(bin_dir, "ffmpeg-*-static")):
        for f in ["ffmpeg", "ffprobe"]:
            src = os.path.join(d, f)
            dst = os.path.join(bin_dir, f)
            shutil.copy2(src, dst)
            os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
    print("ffmpeg ready!", flush=True)


_ensure_ffmpeg()

from remixai.webui import create_ui

app = create_ui()
app.queue()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.launch(server_name="0.0.0.0", server_port=port)
