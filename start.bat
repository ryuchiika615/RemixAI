@echo off
chcp 65001 > nul
title RemixAI

echo ============================================
echo   RemixAI - 音楽動画自動生成ツール
echo ============================================
echo.

:: 自分のIPアドレス取得 (PowerShell使用)
for /f "usebackq tokens=*" %%a in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like '192.*' -or $_.IPAddress -like '10.*' -or $_.IPAddress -like '172.*' } | Select-Object -First 1).IPAddress"`) do set IP=%%a
if "%IP%"=="" set IP=127.0.0.1

:: 既に起動してるかチェック
netstat -ano | findstr ":7860 " > nul
if %errorlevel% equ 0 (
    echo ✅ RemixAI は既に起動しています
    echo.
    echo   自分のPC:     http://127.0.0.1:7860
    echo   友達から:     http://%IP%:7860
    echo.
    start http://127.0.0.1:7860
    goto :end
)

echo 🚀 サーバーを起動しています...
echo.

:: サーバー起動 (0.0.0.0でバインド → LANからもアクセス可能)
start /b "" "C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\Users\ryuch\RemixAI\run_server.py"

:: 起動待ち
set WAIT_COUNT=0
:Loop
timeout /t 1 /nobreak > nul
netstat -ano | findstr ":7860 " > nul
if %errorlevel% equ 0 goto :OpenBrowser
set /a WAIT_COUNT+=1
if %WAIT_COUNT% lss 15 goto :Loop

echo ⚠️ サーバーの起動に時間がかかっています...
echo しばらく待ってからアクセスしてください
goto :end

:OpenBrowser
echo ✅ 起動完了！
echo.
echo ================ アクセス方法 ================
echo.
echo   自分のPCで開く場合:
echo     http://127.0.0.1:7860
echo.
echo   同じWi-Fiの友達が開く場合:
echo     http://%IP%:7860
echo.
echo   ※ 友達のブラウザに上記URLを教えてね
echo   ※ ファイアウォールの警告が出たら「許可」を押して
echo.
echo =============================================
echo.
start http://127.0.0.1:7860

:end
echo.
echo 終了するにはこのウィンドウを閉じてください
echo.
pause
