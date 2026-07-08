import sys, os, re, threading, time
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["GRADIO_QUIET"] = "False"

URL_FILE = os.path.join(os.path.dirname(__file__), "public_url.txt")

def monitor_output(pipe, url_file):
    url_pattern = re.compile(r"https://[\w.-]+\.gradio\.live")
    with open(url_file, "w") as f:
        pass
    for line in iter(pipe.readline, ""):
        print(line, end="", flush=True)
        m = url_pattern.search(line)
        if m:
            with open(url_file, "w") as f:
                f.write(m.group())
            print(f"\n{'='*55}", flush=True)
            print(f"  🌐 公開URL: {m.group()}", flush=True)
            print(f"  このURLを友達に教えてね！", flush=True)
            print(f"  ※ PCが起動してる間だけ使えるよ", flush=True)
            print(f"{'='*55}", flush=True)

import subprocess, sys
proc = subprocess.Popen(
    [sys.executable, "run_server.py", "--share"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

t = threading.Thread(target=monitor_output, args=(proc.stdout, URL_FILE), daemon=True)
t.start()

proc.wait()
