@echo off
chcp 65001 > nul
title RemixAI - 公開共有

echo ============================================
echo   RemixAI - 公開共有モード
echo ============================================
echo.
echo 公開URLを生成します...（30秒くらい待ってね）
echo URLが表示されたら友達に教えてあげて！
echo.

"C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\Users\ryuch\RemixAI\run_server.py" --share

echo.
pause
