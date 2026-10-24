@echo off
cd /d "%~dp0"
cls
echo ==============================================================
echo       Lyceum Portal: Unified Web Server and Telegram-Bot
echo ==============================================================
echo.

if exist "C:\Users\siado\.local\bin\python3.15.exe" (
    "C:\Users\siado\.local\bin\python3.15.exe" server.py
    goto done
)

python server.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python not found or failed to start.
    pause
)

:done
pause
