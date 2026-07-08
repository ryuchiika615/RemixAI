@echo off
chcp 65001 > nul
title RemixAI - PC起動時に自動起動

echo ============================================
echo   RemixAI - PC起動時に自動起動させる
echo ============================================
echo.

:: スタートアップフォルダに登録
set STARTUP="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set SCRIPT="%STARTUP%\RemixAI.bat"

echo スタートアップに登録します...
echo @echo off > %SCRIPT%
echo chcp 65001 ^> nul >> %SCRIPT%
echo start /b "" "C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\Users\ryuch\RemixAI\run_server.py" >> %SCRIPT%

if exist %SCRIPT% (
    echo ✅ 登録完了！
    echo PCを起動すると自動でRemixAIがバックグラウンド起動します
    echo.
    echo いつでも http://127.0.0.1:7860 にアクセスすれば使えます
) else (
    echo ❌ 登録に失敗しました
)

echo.
pause
