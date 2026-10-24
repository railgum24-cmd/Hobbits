@echo off
cd /d "%~dp0"
cls
echo ==============================================================
echo       Telegram-Bot HobbitBot + HTTP API Web Server (Port 8000)
echo ==============================================================
echo.
echo [ИНФО] Запуск бота и встроенного API сервера...
echo [САЙТ] Доступен по адресу: http://localhost:8000
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
