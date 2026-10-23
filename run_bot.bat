@echo off
cd /d "%~dp0"
cls
echo ==============================================================
echo       Telegram-Bot HobbitBot: Lyceum Achievements Portal
echo ==============================================================
echo.

if exist "C:\Users\siado\.local\bin\python3.15.exe" (
    "C:\Users\siado\.local\bin\python3.15.exe" bot\telegram_bot.py
    goto done
)

python bot\telegram_bot.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python not found or failed to start.
    pause
)

:done
pause
