import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["GRADIO_QUIET"] = "True"

from remixai.webui import create_ui

app = create_ui()
app.queue()
app.launch(server_name="0.0.0.0", server_port=7860)
