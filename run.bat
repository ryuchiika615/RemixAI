@echo off
chcp 65001 > nul
if "%1"=="--web" (
    echo Starting RemixAI Web UI...
    echo Open http://127.0.0.1:7860 in your browser
    "C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe" -c "import sys; sys.path.insert(0, '%~dp0'); from remixai.webui import main; main()"
) else (
    "C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m remixai %*
)
