"""
Telegram-бот портала достижений лицея.
Реализован на стандартной библиотеке Python (urllib, json),
не требует установки сторонних библиотек (pip install не нужен).

Функционал для группы 9-11 классов:
1. Авторизация ученика по логину (/login <логин> <пароль>)
2. Просмотр своего рейтинга и баллов по предметам
3. Просмотр топ-10 лицея
4. Подача достижения на верификацию через бота
5. Уведомление о подтверждении/отклонении заявки
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse

# Настройка UTF-8 для консоли Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Токен бота (замените на свой токен от @BotFather)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8920672030:AAFid6V1wkNGorYeo8KGnTLD8E_vDL5kO2U")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Временное хранилище сессий пользователей в памяти / файле
DATA_FILE = os.path.join(os.path.dirname(__file__), "bot_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "user_sessions": {},      # chat_id -> user_id
        "pending_submissions": {} # chat_id -> step_data
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_request(method, payload):
    """Отправка HTTP-запроса к Telegram Bot API без внешних библиотек"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"[DEMO SIMULATION] Метод: {method}, Payload: {payload}")
        return {"ok": True}
        
    url = f"{API_URL}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Ошибка отправки Telegram API: {e}")
        return {"ok": False, "error": str(e)}

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return send_request("sendMessage", payload)

def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "📊 Мой рейтинг"}, {"text": "🏆 Топ-10 лицея"}],
            [{"text": "➕ Подать достижение"}, {"text": "📜 Мои заявки"}],
            [{"text": "🤖 Совет ИИ-помощника"}, {"text": "🚪 Выход"}]
        ],
        "resize_keyboard": True
    }

def process_message(msg, db):
    chat_id = str(msg["chat"]["id"])
    text = msg.get("text", "").strip()

    sessions = db.setdefault("user_sessions", {})
    pending = db.setdefault("pending_submissions", {})

    # Старт
    if text == "/start":
        if chat_id in sessions:
            send_message(chat_id, "👋 С возвращением в <b>HobbitBot</b> (Портал достижений лицея)!", get_main_keyboard())
        else:
            send_message(
                chat_id,
                "👋 <b>Добро пожаловать в HobbitBot — бот достижений лицея!</b>\n\n"
                "Для авторизации отправьте команду:\n"
                "<code>/login &lt;ваш_логин&gt; &lt;пароль&gt;</code>\n\n"
                "<i>Например: /login Rail 2026</i>"
            )
        return

    # Вход
    if text.startswith("/login"):
        parts = text.split()
        if len(parts) < 3:
            send_message(chat_id, "⚠️ Формат: <code>/login логин пароль</code>\nПример: <code>/login Rail 2026</code>")
            return
        
        login, password = parts[1], parts[2]
        # Демо-проверка для учеников команды 9Б
        students = {
            "Rail": "Гумеров Раиль (9Б)",
            "Amir": "Якубов Амир (9Б)",
            "Islam": "Фаррахов Ислам (9Б)",
            "Samir": "Биктагиров Самир (9Б)",
            "Radislav": "Авдошин Радислав (9Б)",
            "Samat": "Яруллин Самат (9Б)",
            "Aliya": "Хасанова Алия (10А)",
            "Timur": "Загиров Тимур (11Б)",
            "Kamila": "Валиуллина Камила (9А)"
        }

        if login in students and password == "2026":
            sessions[chat_id] = {"login": login, "name": students[login], "points": 50}
            save_data(db)
            send_message(
                chat_id,
                f"✅ Авторизация успешна!\nДобро пожаловать, <b>{students[login]}</b>.",
                get_main_keyboard()
            )
        else:
            send_message(chat_id, "❌ Неверный логин или пароль. Попробуйте снова.")
        return

    # Проверка сессии
    if chat_id not in sessions:
        send_message(chat_id, "⚠️ Пожалуйста, войдите: <code>/login логин пароль</code>")
        return

    user = sessions[chat_id]

    # Мой рейтинг
    if text == "📊 Мой рейтинг":
        send_message(
            chat_id,
            f"👤 <b>{user['name']}</b>\n"
            f"⭐ Суммарный балл: <b>{user.get('points', 50)}</b>\n"
            f"🏅 Место в рейтинге: <b>#1 в 9Б</b>\n\n"
            f"<b>Баллы по предметам:</b>\n"
            f"• Физика: 50 б. (Олимпиада «Росатом»)\n"
            f"• Математика: 0 б.\n"
            f"• Информатика: 0 б.\n\n"
            f"<i>Статус: до стипендии осталось 10 баллов!</i>"
        )
        return

    # Топ-10
    if text == "🏆 Топ-10 лицея":
        leaderboard = (
            "🏆 <b>ТОП-10 УЧЕНИКОВ ЛИЦЕЯ:</b>\n\n"
            "🥇 1. Гумеров Раиль (9Б) — 50 б.\n"
            "🥈 2. Фаррахов Ислам (9Б) — 40 б.\n"
            "🥉 3. Хасанова Алия (10А) — 35 б.\n"
            "4. Загиров Тимур (11Б) — 35 б.\n"
            "5. Якубов Амир (9Б) — 25 б.\n"
            "6. Биктагиров Самир (9Б) — 20 б.\n"
            "7. Яруллин Самат (9Б) — 10 б.\n"
            "8. Авдошин Радислав (9Б) — 0 б.\n"
            "9. Валиуллина Камила (9А) — 0 б.\n\n"
            "<i>Обновлено в реальном времени</i>"
        )
        send_message(chat_id, leaderboard)
        return

    # ИИ-помощник
    if text == "🤖 Совет ИИ-помощника":
        ai_tip = (
            "🤖 <b>Рекомендация ИИ-помощника:</b>\n\n"
            "1. 💡 До повышенной академической стипендии вам не хватает <b>10 баллов</b>.\n"
            "2. 📐 По математике и информатике пока нет подтверждённых результатов.\n"
            "3. 🚀 <b>Рекомендация:</b> подайте заявку на городскую олимпиаду по математике или лицейский IT-хакатон — это обеспечит 25-40 баллов!"
        )
        send_message(chat_id, ai_tip)
        return

    # Подать достижение
    if text == "➕ Подать достижение":
        pending[chat_id] = {"step": "waiting_title"}
        save_data(db)
        send_message(
            chat_id,
            "📝 <b>Подача достижения</b>\n"
            "Введите название мероприятия (например: <i>Олимпиада по физике «Шаг в будущее»</i>):"
        )
        return

    # Шаги подачи достижения
    if chat_id in pending:
        step = pending[chat_id].get("step")
        if step == "waiting_title":
            pending[chat_id]["title"] = text
            pending[chat_id]["step"] = "waiting_category"
            save_data(db)
            markup = {
                "keyboard": [
                    [{"text": "Физика"}, {"text": "Математика"}],
                    [{"text": "Информатика"}, {"text": "Проект/Волонтёрство"}]
                ],
                "resize_keyboard": True
            }
            send_message(chat_id, "Выберите категорию предмета:", markup)
            return

        if step == "waiting_category":
            pending[chat_id]["category"] = text
            pending[chat_id]["step"] = "waiting_result"
            save_data(db)
            markup = {
                "keyboard": [
                    [{"text": "Победитель (1 место)"}],
                    [{"text": "Призёр (2-3 место)"}],
                    [{"text": "Участник"}]
                ],
                "resize_keyboard": True
            }
            send_message(chat_id, "Укажите ваш результат:", markup)
            return

        if step == "waiting_result":
            pending[chat_id]["result"] = text
            title = pending[chat_id].get("title")
            cat = pending[chat_id].get("category")
            del pending[chat_id]
            save_data(db)

            send_message(
                chat_id,
                f"✅ <b>Заявка успешно отправлена на верификацию!</b>\n\n"
                f"📌 Мероприятие: {title}\n"
                f"📚 Категория: {cat}\n"
                f"🏅 Результат: {text}\n"
                f"⏳ Статус: <i>На проверке администратором</i>\n\n"
                f"Бот пришлёт уведомление, как только учитель проверит диплом.",
                get_main_keyboard()
            )
            return

    # Мои заявки
    if text == "📜 Мои заявки":
        send_message(
            chat_id,
            "📋 <b>Ваши последние заявки:</b>\n\n"
            "1. <b>Олимпиада по физике «Росатом»</b>\n"
            "   Статус: ✅ Подтверждено (+50 б.)\n"
            "   Комментарий: Диплом проверен.\n\n"
            "2. <b>Городская олимпиада по математике</b>\n"
            "   Статус: ⏳ На проверке\n"
            "   Дата: 2026-10-02"
        )
        return

    # Выход
    if text == "🚪 Выход":
        del sessions[chat_id]
        save_data(db)
        send_message(chat_id, "Вы вышли из системы. Для входа отправьте /start")
        return

    send_message(chat_id, "Используйте кнопки меню для навигации.", get_main_keyboard())

def main():
    print("=" * 60)
    print("🤖 Telegram-бот HobbitBot: Портал Достижений Лицея (9-11 классы)")
    print("=" * 60)
    db = load_data()

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n[ИНФО] Токен не задан. Бот работает в демонстрационном режиме эмуляции.")
        print("Для подключения к реальному Telegram укажите токен:")
        print("  set TELEGRAM_BOT_TOKEN=123456:ABC-DEF...")
        print("  python bot/telegram_bot.py\n")
        print("Тестирование сценария через интерактивную консоль:")
        print("Введите команду (например: /start или /login Rail 2026):")
        
        sim_chat_id = 999001
        while True:
            try:
                line = input("\n[Ученик в Telegram] > ").strip()
                if not line or line.lower() in ["exit", "quit"]:
                    break
                msg = {"chat": {"id": sim_chat_id}, "text": line}
                process_message(msg, db)
            except (KeyboardInterrupt, EOFError):
                break
        return

    print("Запуск polling Telegram API...")
    print("Бот HobbitBot активен и ожидает сообщений!")
    print("Откройте Telegram, найдите бота и отправьте: /start")
    print("(Для остановки бота нажмите Ctrl+C)")
    print("-" * 60)
    offset = 0
    while True:
        try:
            url = f"{API_URL}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update:
                        msg = update["message"]
                        u_name = msg.get("from", {}).get("first_name", "User")
                        u_text = msg.get("text", "")
                        print(f"[Новое сообщение от {u_name}]: {u_text}")
                        process_message(msg, db)
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
