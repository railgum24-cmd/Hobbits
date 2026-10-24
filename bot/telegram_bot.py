"""
Telegram-бот HobbitBot для Портала достижений лицея (9-11 классы).
Версия 2.5 Perspective Edition.

Особенности:
- Единая база данных с веб-порталом (database/lyceum_db.json и SQLite)
- Красивый, дружелюбный и структурированный интерфейс
- Поддержка Reply и Inline-кнопок
- Автоматический расчёт баллов и прогресса стипендии
- Интерактивный мастер подачи дипломов
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

# Токен бота
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8920672030:AAFid6V1wkNGorYeo8KGnTLD8E_vDL5kO2U")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_JSON_PATH = os.path.join(BASE_DIR, "database", "lyceum_db.json")
SESSIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.json")

# Официальная шкала баллов лицея
POINTS_RULES = {
    "federal": {"winner": 50, "prize": 40, "participant": 20},
    "region":  {"winner": 35, "prize": 25, "participant": 10},
    "city":    {"winner": 20, "prize": 15, "participant": 5},
    "school":  {"winner": 15, "prize": 10, "participant": 3}
}

CAT_MAP = {
    "physics": {"name": "Физика", "icon": "⚛️"},
    "math": {"name": "Математика", "icon": "📐"},
    "informatics": {"name": "Информатика", "icon": "💻"},
    "project": {"name": "Проекты & Наука", "icon": "🚀"},
    "volunteering": {"name": "Волонтёрство", "icon": "🤝"}
}

LEVEL_NAMES = {
    "federal": "Федеральный (ВсОШ / НТИ)",
    "region": "Региональный этап",
    "city": "Городской / Муниципальный",
    "school": "Школьный / Лицейский"
}

RESULT_NAMES = {
    "winner": "🥇 1 место (Победитель)",
    "prize": "🥈 2–3 место (Призёр)",
    "participant": "📜 Сертификат участника"
}

def load_unified_db():
    """Загрузка единой базы данных (синхронной с сайтом)"""
    if os.path.exists(DB_JSON_PATH):
        try:
            with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[BOT] Ошибка чтения единой базы: {e}")
    return {"users": [], "achievements": []}

def save_unified_db(db):
    """Сохранение единой базы данных (сразу доступно на сайте)"""
    try:
        with open(DB_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[BOT] Ошибка сохранения единой базы: {e}")

def load_sessions():
    """Загрузка сохранённых сессий Telegram чатов"""
    if os.path.exists(SESSIONS_PATH):
        try:
            with open(SESSIONS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"user_sessions": {}, "pending_submissions": {}}

def save_sessions(data):
    """Сохранение сессий Telegram чатов"""
    try:
        with open(SESSIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[BOT] Ошибка сохранения сессий: {e}")

def send_request(method, payload):
    """Отправка HTTP-запроса к Telegram Bot API"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"[DEMO SIMULATION] Метод: {method}, Payload: {payload}")
        return {"ok": True}
        
    url = f"{API_URL}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return send_request("sendMessage", payload)

def answer_callback(callback_query_id, text=None):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    return send_request("answerCallbackQuery", payload)

def render_progress_bar(current, target=60, length=10):
    """Создаёт красивый визуальный прогресс-бар"""
    ratio = min(1.0, max(0.0, current / target)) if target > 0 else 1.0
    filled = int(round(ratio * length))
    empty = length - filled
    bar = "▰" * filled + "▱" * empty
    percent = int(ratio * 100)
    return f"<code>{bar}</code> {current}/{target} б. (<b>{percent}%</b>)"

def get_main_keyboard():
    """Приятная клавиатура быстрого доступа"""
    return {
        "keyboard": [
            [{"text": "📊 Мой профиль"}, {"text": "🏆 Рейтинг лицея"}],
            [{"text": "➕ Подать диплом"}, {"text": "📢 Афиша олимпиад"}],
            [{"text": "📜 Мои заявки"}, {"text": "📋 Регламент баллов"}],
            [{"text": "🌐 Веб-портал"}, {"text": "🚪 Выход"}]
        ],
        "resize_keyboard": True
    }

def format_events_message():
    """Форматирует афиши ближайших мероприятий и олимпиад из базы данных"""
    db = load_unified_db()
    events = db.get("events", [])
    if not events:
        return (
            "📢 <b>АФИША МЕРОПРИЯТИЙ И ОЛИМПИАД</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "На данный момент активных анонсов нет. Завуч скоро опубликует новые события!"
        ), None

    lines = [
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈",
        "  📢 <b>АФИША МЕРОПРИЯТИЙ И ОЛИМПИАД</b>",
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n"
    ]

    inline_keyboard = []

    for idx, ev in enumerate(events[:5], 1):
        title = ev.get("title", "Мероприятие")
        cat = CAT_MAP.get(ev.get("category"), {}).get("name", "Общее")
        lvl = ev.get("level", "Лицей")
        date = ev.get("date", "Уточняется")
        place = ev.get("place", "Лицей")
        pts = ev.get("pointsAward", "+20 б.")
        desc = ev.get("description", "")
        reg = ev.get("registrationLink", "")

        lines.append(f"<b>{idx}. {title}</b>")
        lines.append(f"🗓 <b>Дата:</b> {date}  |  📍 {place}")
        lines.append(f"📚 <b>Предмет:</b> {cat} ({lvl})")
        lines.append(f"⭐ <b>Награда:</b> <code>{pts}</code> в рейтинг")
        if desc:
            lines.append(f"📝 <i>{desc}</i>")
        lines.append("────────────────────")

        if reg and reg.startswith("http"):
            short_t = title[:24] + "..." if len(title) > 24 else title
            inline_keyboard.append([{"text": f"🔗 Регистрация: {short_t}", "url": reg}])

    lines.append("\n💡 <i>После участия загрузите диплом через кнопку «➕ Подать диплом»!</i>")

    markup = {"inline_keyboard": inline_keyboard} if inline_keyboard else None
    return "\n".join(lines), markup

def format_profile_message(user_session):
    """Форматирует красивый профиль ученика"""
    user_id = user_session["userId"]
    db = load_unified_db()
    achs = db.get("achievements", [])
    approved = [a for a in achs if a.get("userId") == user_id and a.get("status") == "approved"]
    pending = [a for a in achs if a.get("userId") == user_id and a.get("status") == "pending"]
    
    total_pts = sum(a.get("points", 0) for a in approved)
    pending_pts = sum(a.get("points", 0) for a in pending)
    
    # Баллы по категориям
    cats_pts = {}
    for a in approved:
        c = a.get("category", "other")
        cats_pts[c] = cats_pts.get(c, 0) + a.get("points", 0)
    
    # Расчёт ранга в общем рейтинге
    all_students = [u for u in db.get("users", []) if u.get("role") == "student"]
    scores = []
    for s in all_students:
        s_approved = [a for a in achs if a.get("userId") == s["id"] and a.get("status") == "approved"]
        scores.append((s["id"], sum(a.get("points", 0) for a in s_approved)))
    scores.sort(key=lambda x: x[1], reverse=True)
    
    rank = 1
    for i, (sid, pts) in enumerate(scores):
        if sid == user_id:
            rank = i + 1
            break

    prog_bar = render_progress_bar(total_pts, 60, 10)
    
    cat_lines = []
    for cat_code, cat_info in CAT_MAP.items():
        pts = cats_pts.get(cat_code, 0)
        cat_lines.append(f"  {cat_info['icon']} {cat_info['name']}: <b>{pts} б.</b>")

    scholarship_text = (
        "  ✨ <b>Статус:</b> 🎓 <i>Стипендия назначена!</i>" if total_pts >= 60
        else f"  ✨ <b>Статус:</b> До академической стипендии: <b>+{max(0, 60 - total_pts)} б.</b>"
    )

    pending_info = f"\n⏳ <i>В проверке завучем: {len(pending)} нагр. (+{pending_pts} б.)</i>" if pending else ""

    text = (
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n"
        "  <b>ЛИЧНЫЙ ПРОФИЛЬ ЛИЦЕИСТА</b>\n"
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n\n"
        f"👤 <b>ФИО:</b> {user_session['name']}\n"
        f"🏫 <b>Класс:</b> {user_session.get('class', 'Лицеист')}\n"
        f"🏅 <b>Место в лицее:</b> <b>#{rank}</b> из {len(all_students)}\n"
        f"⭐ <b>Подтверждено баллов:</b> <b>{total_pts}</b>\n\n"
        f"🎓 <b>Прогресс стипендии (от 60 б.):</b>\n"
        f"{prog_bar}\n"
        f"{scholarship_text}\n\n"
        "📚 <b>Баллы по предметам:</b>\n" +
        "\n".join(cat_lines) +
        f"{pending_info}\n\n"
        "<i>Данные синхронизированы в реальном времени с реестром лицея.</i>"
    )

    inline_markup = {
        "inline_keyboard": [
            [
                {"text": "➕ Подать диплом", "callback_data": "cmd_submit"},
                {"text": "📜 Мои заявки", "callback_data": "cmd_my_achs"}
            ],
            [
                {"text": "🏆 Топ-10 лицея", "callback_data": "cmd_top"},
                {"text": "🔄 Обновить данные", "callback_data": "cmd_refresh_me"}
            ]
        ]
    }

    return text, inline_markup

def format_top10_message(current_user_id):
    """Форматирует красивый подиум лидеров лицея"""
    db = load_unified_db()
    achs = db.get("achievements", [])
    students = [u for u in db.get("users", []) if u.get("role") == "student"]
    
    leaderboard = []
    for s in students:
        s_approved = [a for a in achs if a.get("userId") == s["id"] and a.get("status") == "approved"]
        total = sum(a.get("points", 0) for a in s_approved)
        leaderboard.append({
            "id": s["id"],
            "name": s["name"],
            "class": s.get("class", ""),
            "total": total,
            "count": len(s_approved)
        })
    
    leaderboard.sort(key=lambda x: x["total"], reverse=True)
    top10 = leaderboard[:10]
    
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = []
    for i, item in enumerate(top10, start=1):
        m = medals.get(i, f"<b>{i}.</b>")
        is_me = " 👈 <b>(Вы)</b>" if item["id"] == current_user_id else ""
        lines.append(f"{m} <b>{item['name']}</b> ({item['class']}) — <b>{item['total']} б.</b> ({item['count']} нагр.){is_me}")

    text = (
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n"
        "  <b>ОБЩЕЛИЦЕЙСКИЙ ТОП-10 (РЕЙТИНГ)</b>\n"
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n\n" +
        "\n".join(lines) +
        "\n\n💡 <i>Баллы начисляются автоматически после верификации грамот завучем.</i>"
    )

    inline_markup = {
        "inline_keyboard": [
            [
                {"text": "📊 Мой результат", "callback_data": "cmd_me"},
                {"text": "🔄 Обновить рейтинг", "callback_data": "cmd_refresh_top"}
            ]
        ]
    }

    return text, inline_markup

def format_my_achievements(user_id):
    """Форматирует список поданных дипломов и статус их проверки"""
    db = load_unified_db()
    achs = db.get("achievements", [])
    my_achs = [a for a in achs if a.get("userId") == user_id]
    
    if not my_achs:
        text = (
            "📋 <b>Ваш реестр дипломов пуст.</b>\n\n"
            "Вы можете отправить грамоту или сертификат на проверку через кнопку:\n"
            "<b>➕ Подать диплом</b>"
        )
        markup = {"inline_keyboard": [[{"text": "➕ Подать диплом", "callback_data": "cmd_submit"}]]}
        return text, markup

    status_labels = {
        "approved": "✅ <b>ПОДТВЕРЖДЕНО</b>",
        "pending": "⏳ <b>НА ПРОВЕРКЕ</b>",
        "rejected": "❌ <b>ОТКЛОНЕНО</b>"
    }

    lines = []
    for i, a in enumerate(reversed(my_achs), start=1):
        st = status_labels.get(a.get("status"), a.get("status"))
        cat_info = CAT_MAP.get(a.get("category"), {"name": a.get("category", "Предмет"), "icon": "📚"})
        pts_str = f"+{a.get('points', 0)} б." if a.get("status") == "approved" else f"({a.get('points', 0)} б. в ожидании)"
        comment_str = f"\n   💬 <i>Заметка завуча: {a['comment']}</i>" if a.get("comment") else ""
        
        lines.append(
            f"<b>{i}. {a.get('title')}</b>\n"
            f"   {cat_info['icon']} {cat_info['name']} | {st} — <b>{pts_str}</b>{comment_str}"
        )

    text = (
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n"
        "  <b>ВАШИ ДИПЛОМЫ И ГРАМОТЫ</b>\n"
        "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n\n" +
        "\n\n".join(lines[:10]) +
        "\n\n<i>Все подтверждённые дипломы доступны для мгновенного скачивания на веб-сайте.</i>"
    )

    markup = {
        "inline_keyboard": [
            [
                {"text": "➕ Подать ещё диплом", "callback_data": "cmd_submit"},
                {"text": "🔄 Обновить список", "callback_data": "cmd_refresh_achs"}
            ]
        ]
    }
    return text, markup

def start_submission_flow(chat_id):
    """Запуск мастера подачи диплома"""
    sessions_data = load_sessions()
    pending = sessions_data.setdefault("pending_submissions", {})
    pending[chat_id] = {"step": "waiting_title"}
    save_sessions(sessions_data)

    text = (
        "📝 <b>МАСТЕР ПОДАЧИ ДОСТИЖЕНИЯ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Шаг 1 из 4 // Название состязания</b>\n"
        "Введите точное название олимпиады, хакатона или турнира сообщением в чат:\n\n"
        "<i>Например: Всероссийская олимпиада школьников по физике (регион)</i>"
    )
    send_message(chat_id, text)

def process_message(msg):
    chat_id = str(msg["chat"]["id"])
    text = msg.get("text", "").strip()

    sessions_data = load_sessions()
    sessions = sessions_data.setdefault("user_sessions", {})
    pending = sessions_data.setdefault("pending_submissions", {})

    # Команда /start
    if text in ("/start", "/menu"):
        if chat_id in sessions:
            u_info = sessions[chat_id]
            body, markup = format_profile_message(u_info)
            send_message(
                chat_id,
                f"👋 <b>С возвращением в HobbitBot, {u_info['name']}!</b>\n\n"
                "Используйте кнопки меню внизу для быстрого доступа к реестру лицея:",
                get_main_keyboard()
            )
            send_message(chat_id, body, markup)
        else:
            welcome_text = (
                "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n"
                "  <b>РЕЕСТР ДОСТИЖЕНИЙ ЛИЦЕЯ</b>\n"
                "  <i>Telegram-шлюз HobbitBot V2.5</i>\n"
                "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n\n"
                "👋 <b>Добро пожаловать в официальный бот Инженерного лицея!</b>\n\n"
                "Бот объединён в <b>единую сквозную базу</b> с веб-порталом лицея.\n\n"
                "🔑 <b>Для авторизации отправьте:</b>\n"
                "<code>/login логин пароль</code>\n\n"
                "<i>Пример: /login Rail 2026</i>\n"
                "<i>(Или логин и пароль, которые вы создали при регистрации на сайте)</i>"
            )
            send_message(chat_id, welcome_text)
        return

    # Вход в систему: /login <логин> <пароль>
    if text.startswith("/login"):
        parts = text.split()
        if len(parts) < 3:
            send_message(
                chat_id,
                "⚠️ <b>Неверный формат команды!</b>\n\n"
                "Отправьте команду в виде:\n"
                "<code>/login ваш_логин ваш_пароль</code>\n\n"
                "<i>Пример: /login Rail 2026</i>"
            )
            return
        
        login_in, pass_in = parts[1].strip(), parts[2].strip()
        
        # Свежая проверка из единой базы данных
        db = load_unified_db()
        users = db.get("users", [])
        
        found_user = None
        for u in users:
            if u.get("login", "").strip().lower() == login_in.lower() and str(u.get("password", "")).strip() == pass_in:
                found_user = u
                break
        
        if found_user:
            sessions[chat_id] = {
                "userId": found_user["id"],
                "name": found_user["name"],
                "class": found_user.get("class", ""),
                "login": found_user["login"]
            }
            save_sessions(sessions_data)
            
            cls_str = f" • Класс {found_user['class']}" if found_user.get("class") else ""
            success_text = (
                "✅ <b>АВТОРИЗАЦИЯ УСПЕШНО ВЫПОЛНЕНА!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Ученик: <b>{found_user['name']}</b>{cls_str}\n"
                f"🔐 Доступ: <b>Синхронизирован с сайтом лицея</b>\n\n"
                "Выберите нужный раздел в меню ниже:"
            )
            send_message(chat_id, success_text, get_main_keyboard())
            
            # Сразу показываем карточку профиля
            p_text, p_markup = format_profile_message(sessions[chat_id])
            send_message(chat_id, p_text, p_markup)
        else:
            send_message(
                chat_id,
                "❌ <b>Ошибка входа: неверный логин или пароль.</b>\n\n"
                "Проверьте данные. Если вы только что зарегистрировались на сайте, используйте этот же логин и пароль."
            )
        return

    # Проверка сессии
    if chat_id not in sessions:
        send_message(
            chat_id,
            "⚠️ <b>Вы не авторизованы.</b>\n\n"
            "Пожалуйста, выполните вход:\n"
            "<code>/login логин пароль</code>\n\n"
            "<i>(Или зарегистрируйтесь на главной странице веб-сайта)</i>"
        )
        return

    user_session = sessions[chat_id]
    user_id = user_session["userId"]

    # 📊 Мой профиль / рейтинг
    if text in ("📊 Мой профиль", "📊 Мой рейтинг", "/me"):
        body, markup = format_profile_message(user_session)
        send_message(chat_id, body, markup)
        return

    # 🏆 Топ-10 лицея
    if text in ("🏆 Рейтинг лицея", "🏆 Топ-10 лицея", "/top"):
        body, markup = format_top10_message(user_id)
        send_message(chat_id, body, markup)
        return

    # 📜 Мои заявки
    if text in ("📜 Мои заявки", "/diplomas"):
        body, markup = format_my_achievements(user_id)
        send_message(chat_id, body, markup)
        return

    # ➕ Подать диплом
    if text in ("➕ Подать диплом", "➕ Подать достижение", "/submit"):
        start_submission_flow(chat_id)
        return

    # 📢 Афиша олимпиад и мероприятий
    if text in ("📢 Афиша олимпиад", "📢 Афиша мероприятий", "📢 Афиша", "/events", "Афиша"):
        body, markup = format_events_message()
        send_message(chat_id, body, markup)
        return

    # 📋 Регламент баллов
    if text in ("📋 Регламент баллов", "📋 Регламент и баллы", "/rules"):
        rules_text = (
            "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n"
            "  <b>РЕГЛАМЕНТ НАЧИСЛЕНИЯ БАЛЛОВ</b>\n"
            "◈ ━━━━━━━━━━━━━━━━━━━━ ◈\n\n"
            "🥇 <b>Федеральный уровень (ВсОШ / НТИ):</b>\n"
            "• Победитель (1 место): <b>+50 баллов</b>\n"
            "• Призёр (2–3 место): <b>+40 баллов</b>\n"
            "• Сертификат участника: <b>+20 баллов</b>\n\n"
            "🥈 <b>Региональный этап:</b>\n"
            "• Победитель: <b>+35 баллов</b>\n"
            "• Призёр: <b>+25 баллов</b>\n"
            "• Сертификат участника: <b>+10 баллов</b>\n\n"
            "🥉 <b>Муниципальный / Городской этап:</b>\n"
            "• Победитель: <b>+20 баллов</b>\n"
            "• Призёр: <b>+15 баллов</b>\n"
            "• Сертификат участника: <b>+5 баллов</b>\n\n"
            "🏫 <b>Школьный / Лицейский турнир:</b>\n"
            "• Победитель: <b>+15 баллов</b>\n"
            "• Призёр: <b>+10 баллов</b>\n"
            "• Сертификат участника: <b>+3 балла</b>\n\n"
            "🎓 <b>Повышенная стипендия лицея</b> присуждается автоматически при наборе <b>от 60 баллов</b>."
        )
        send_message(chat_id, rules_text)
        return

    # 🌐 Веб-портал
    if text in ("🌐 Веб-портал", "/web"):
        web_text = (
            "🌐 <b>ВЕБ-ПОРТАЛ ДОСТИЖЕНИЙ ЛИЦЕЯ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Сайт доступен в локальной сети лицея:\n"
            "🔗 <a href='http://localhost:8000'>http://localhost:8000</a>\n\n"
            "На сайте вы можете:\n"
            "• Скачать портфолио в PDF\n"
            "• Получить персональный диплом с SHA-256 хэшем в PNG\n"
            "• Изучить детальный рейтинг всех классов"
        )
        send_message(chat_id, web_text)
        return

    # 🚪 Выход
    if text in ("🚪 Выход", "/logout"):
        if chat_id in sessions:
            del sessions[chat_id]
            save_sessions(sessions_data)
        send_message(
            chat_id,
            "🚪 <b>Вы успешно вышли из учётной записи.</b>\n\n"
            "Для повторного входа отправьте команду:\n"
            "<code>/login логин пароль</code>"
        )
        return

    # Обработка текстового шага (Шаг 1: Название мероприятия)
    if chat_id in pending and pending[chat_id].get("step") == "waiting_title":
        pending[chat_id]["title"] = text
        pending[chat_id]["step"] = "waiting_category"
        save_sessions(sessions_data)

        cat_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "⚛️ Физика", "callback_data": "sub_cat_physics"},
                    {"text": "📐 Математика", "callback_data": "sub_cat_math"}
                ],
                [
                    {"text": "💻 Информатика", "callback_data": "sub_cat_informatics"},
                    {"text": "🚀 Проекты", "callback_data": "sub_cat_project"}
                ],
                [
                    {"text": "🤝 Волонтёрство", "callback_data": "sub_cat_volunteering"}
                ]
            ]
        }
        send_message(
            chat_id,
            f"📌 Состязание: <b>{text}</b>\n\n"
            "<b>Шаг 2 из 4 // Категория предмета</b>\n"
            "Выберите предметную область нажатием кнопки ниже:",
            cat_keyboard
        )
        return

    # Поддержка текстового ответа для категории
    if chat_id in pending and pending[chat_id].get("step") == "waiting_category":
        for cat_k, cat_v in CAT_MAP.items():
            if cat_v["name"].lower() in text.lower() or cat_k in text.lower():
                process_callback_query({"id": "0", "message": {"chat": {"id": chat_id}}, "data": f"sub_cat_{cat_k}"})
                return

    # Поддержка текстового ответа для уровня
    if chat_id in pending and pending[chat_id].get("step") == "waiting_level":
        for lvl_k, lvl_v in LEVEL_NAMES.items():
            if lvl_v.lower() in text.lower() or lvl_k in text.lower() or ("федерал" in text.lower() and lvl_k == "federal") or ("регион" in text.lower() and lvl_k == "region"):
                process_callback_query({"id": "0", "message": {"chat": {"id": chat_id}}, "data": f"sub_lvl_{lvl_k}"})
                return

    # Поддержка текстового ответа для результата
    if chat_id in pending and pending[chat_id].get("step") == "waiting_result":
        if "победител" in text.lower() or "1" in text.lower():
            process_callback_query({"id": "0", "message": {"chat": {"id": chat_id}}, "data": "sub_res_winner"})
            return
        elif "приз" in text.lower() or "2" in text.lower() or "3" in text.lower():
            process_callback_query({"id": "0", "message": {"chat": {"id": chat_id}}, "data": "sub_res_prize"})
            return
        else:
            process_callback_query({"id": "0", "message": {"chat": {"id": chat_id}}, "data": "sub_res_participant"})
            return

    send_message(
        chat_id,
        "Выберите действие в меню внизу или отправьте команду из списка.",
        get_main_keyboard()
    )

def process_callback_query(cq):
    """Обработка нажатий на интерактивные Inline-кнопки"""
    cq_id = cq["id"]
    chat_id = str(cq["message"]["chat"]["id"])
    data = cq.get("data", "")

    sessions_data = load_sessions()
    sessions = sessions_data.setdefault("user_sessions", {})
    pending = sessions_data.setdefault("pending_submissions", {})

    if chat_id not in sessions:
        answer_callback(cq_id, "Пожалуйста, авторизуйтесь через /login")
        return

    user_session = sessions[chat_id]
    user_id = user_session["userId"]

    # Навигационные коллбэки
    if data in ("cmd_me", "cmd_refresh_me"):
        answer_callback(cq_id, "Данные профиля обновлены")
        body, markup = format_profile_message(user_session)
        send_message(chat_id, body, markup)
        return

    if data in ("cmd_top", "cmd_refresh_top"):
        answer_callback(cq_id, "Рейтинг обновлён")
        body, markup = format_top10_message(user_id)
        send_message(chat_id, body, markup)
        return

    if data in ("cmd_my_achs", "cmd_refresh_achs"):
        answer_callback(cq_id, "Список дипломов обновлён")
        body, markup = format_my_achievements(user_id)
        send_message(chat_id, body, markup)
        return

    if data == "cmd_submit":
        answer_callback(cq_id)
        start_submission_flow(chat_id)
        return

    # Шаги мастера подачи через Inline кнопки
    if data.startswith("sub_cat_"):
        cat_code = data.replace("sub_cat_", "")
        if chat_id in pending:
            pending[chat_id]["category"] = cat_code
            pending[chat_id]["step"] = "waiting_level"
            save_sessions(sessions_data)

            answer_callback(cq_id, f"Выбрано: {CAT_MAP.get(cat_code, {}).get('name')}")

            lvl_keyboard = {
                "inline_keyboard": [
                    [{"text": "🏛 Федеральный (ВсОШ / НТИ)", "callback_data": "sub_lvl_federal"}],
                    [{"text": "🥈 Региональный этап", "callback_data": "sub_lvl_region"}],
                    [{"text": "🥉 Городской / Муниципальный", "callback_data": "sub_lvl_city"}],
                    [{"text": "🏫 Школьный / Лицейский", "callback_data": "sub_lvl_school"}]
                ]
            }
            send_message(
                chat_id,
                f"📚 Предмет: <b>{CAT_MAP.get(cat_code, {}).get('name')}</b>\n\n"
                "<b>Шаг 3 из 4 // Уровень состязания</b>\n"
                "Выберите статус мероприятия:",
                lvl_keyboard
            )
        return

    if data.startswith("sub_lvl_"):
        lvl_code = data.replace("sub_lvl_", "")
        if chat_id in pending:
            pending[chat_id]["level"] = lvl_code
            pending[chat_id]["step"] = "waiting_result"
            save_sessions(sessions_data)

            answer_callback(cq_id, f"Уровень: {LEVEL_NAMES.get(lvl_code)}")

            res_keyboard = {
                "inline_keyboard": [
                    [{"text": "🥇 1 место (Победитель)", "callback_data": "sub_res_winner"}],
                    [{"text": "🥈 2–3 место (Призёр)", "callback_data": "sub_res_prize"}],
                    [{"text": "📜 Сертификат участника", "callback_data": "sub_res_participant"}]
                ]
            }
            send_message(
                chat_id,
                f"🏛 Уровень: <b>{LEVEL_NAMES.get(lvl_code)}</b>\n\n"
                "<b>Шаг 4 из 4 // Занятое место</b>\n"
                "Укажите ваш результат:",
                res_keyboard
            )
        return

    if data.startswith("sub_res_"):
        res_code = data.replace("sub_res_", "")
        if chat_id in pending:
            draft = pending[chat_id]
            title = draft.get("title", "Олимпиада лицея")
            cat_code = draft.get("category", "informatics")
            lvl_code = draft.get("level", "city")

            # Расчёт баллов
            pts = POINTS_RULES.get(lvl_code, {}).get(res_code, 15)

            # Сохраняем в единую базу данных
            db = load_unified_db()
            achs = db.setdefault("achievements", [])
            new_id = f"ach-{int(time.time())}"

            new_ach = {
                "id": new_id,
                "userId": user_id,
                "title": title,
                "category": cat_code,
                "type": "olympiad",
                "level": lvl_code,
                "result": res_code,
                "points": pts,
                "date": time.strftime("%Y-%m-%d"),
                "status": "pending",
                "verifiedBy": None,
                "verifiedAt": None,
                "comment": "",
                "description": f"Подано через Telegram-бот HobbitBot ({user_session['name']})"
            }
            achs.append(new_ach)
            save_unified_db(db)
            print(f"[ЕДИНАЯ БАЗА] Новая заявка из Telegram: '{title}' от ученика {user_session['name']} (+{pts} б.)")

            del pending[chat_id]
            save_sessions(sessions_data)

            answer_callback(cq_id, f"Заявка подана! +{pts} б.")

            confirm_text = (
                "✅ <b>ЗАЯВКА УСПЕШНО ВНЕСЕНА В РЕЕСТР ЛИЦЕЯ!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 <b>Мероприятие:</b> {title}\n"
                f"📚 <b>Предмет:</b> {CAT_MAP.get(cat_code, {}).get('name')}\n"
                f"🏛 <b>Уровень:</b> {LEVEL_NAMES.get(lvl_code)}\n"
                f"🏅 <b>Результат:</b> {RESULT_NAMES.get(res_code)}\n"
                f"⭐ <b>Ожидаемые баллы:</b> <b>+{pts} баллов</b>\n"
                f"⏳ <b>Статус:</b> <i>На верификации завучем</i>\n\n"
                "👨‍🏫 Завуч уже видит вашу заявку в админ-панели на сайте. После одобрения баллы зачислятся автоматически!"
            )
            send_message(chat_id, confirm_text, get_main_keyboard())
        return

def run_bot_polling():
    """Основной цикл опроса Telegram Bot API"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[BOT] Токен не настроен, опрос Telegram отключён.")
        return

    # Настройка профиля бота
    try:
        from bot.setup_bot_profile import setup
        setup()
    except Exception:
        pass

    offset = 0
    print("[BOT] HobbitBot V2.5 запущен и ожидает сообщения Telegram...")
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
                        print(f"[Telegram HobbitBot] Сообщение от {u_name}: {u_text}")
                        process_message(msg)
                    elif "callback_query" in update:
                        cq = update["callback_query"]
                        u_name = cq.get("from", {}).get("first_name", "User")
                        cq_data = cq.get("data", "")
                        print(f"[Telegram HobbitBot] Нажатие кнопки от {u_name}: {cq_data}")
                        process_callback_query(cq)
        except Exception as e:
            time.sleep(2)

def start_local_server_thread():
    """Запуск локального HTTP API сервера на порту 8000 в фоновом потоке"""
    try:
        from http.server import ThreadingHTTPServer
        import threading
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        from server import PortalHandler, PORT
        server = ThreadingHTTPServer(("0.0.0.0", PORT), PortalHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True, name="ApiServerThread")
        server_thread.start()
        print(f"[СЕРВЕР] Встроенный API-сервер активен на http://localhost:{PORT}")
    except OSError as e:
        # Порт 8000 уже занят (например, server.py уже запущен в соседнем терминале)
        print(f"[СЕРВЕР] API-сервер уже запущен на порту 8000.")
    except Exception as e:
        print(f"[СЕРВЕР] Предупреждение: фоновый API-сервер не запущен: {e}")

def main():
    print("=" * 60)
    print("🤖 Telegram-бот HobbitBot: V2.5 Perspective Edition")
    print("=" * 60)
    # Автоматически стартуем HTTP API сервер для сайта
    start_local_server_thread()
    run_bot_polling()

if __name__ == "__main__":
    main()
