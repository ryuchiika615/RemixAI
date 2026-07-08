import sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["GRADIO_QUIET"] = "True"

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.chdir(os.path.dirname(__file__))

from remixai.webui import main

share = "--share" in sys.argv
main(share=share)
