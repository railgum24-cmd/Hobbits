"""
Скрипт настройки профиля Telegram-бота HobbitBot:
- Устанавливает официальное описание бота (setMyDescription)
- Устанавливает краткое описание для превью (setMyShortDescription)
- Настраивает команды бота в меню Telegram (setMyCommands)
"""

import os
import json
import urllib.request

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8920672030:AAFid6V1wkNGorYeo8KGnTLD8E_vDL5kO2U")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def call_api(method, payload):
    url = f"{API_URL}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            return res
    except Exception as e:
        return {"ok": False, "error": str(e)}

def setup():
    print(f"Настройка профиля HobbitBot...")

    # 1. Полное описание бота (отображается при первом открытии)
    desc = (
        "🤖 Официальный бот реестра академических и олимпиадных достижений Инженерного лицея (9–11 классы).\n\n"
        "✨ Возможности HobbitBot:\n"
        "• Просмотр личного рейтинга, баллов и статуса стипендии\n"
        "• Мгновенная подача дипломов и грамот на верификацию завучу\n"
        "• Открытый общелицейский лидерборд\n"
        "• Сквозная синхронизация с сайтом лицея\n\n"
        "Для авторизации отправьте: /login логин пароль"
    )
    r1 = call_api("setMyDescription", {"description": desc})
    print(f" setMyDescription: {r1}")

    # 2. Краткое описание (bio)
    short_desc = "Официальный реестр олимпиад и рейтинга Инженерного лицея 2025/2026."
    r2 = call_api("setMyShortDescription", {"short_description": short_desc})
    print(f" setMyShortDescription: {r2}")

    # 3. Список команд в меню
    commands = [
        {"command": "start", "description": "🚀 Главное меню и статус профиля"},
        {"command": "me", "description": "📊 Мой рейтинг, баллы и стипендия"},
        {"command": "top", "description": "🏆 Общелицейский топ-10"},
        {"command": "submit", "description": "➕ Подать диплом на верификацию"},
        {"command": "diplomas", "description": "📜 Мои поданные заявки"},
        {"command": "rules", "description": "📋 Регламент начисления баллов"},
        {"command": "logout", "description": "🚪 Выйти из учётной записи"}
    ]
    r3 = call_api("setMyCommands", {"commands": commands})
    print(f" setMyCommands: {r3}")

if __name__ == "__main__":
    setup()
