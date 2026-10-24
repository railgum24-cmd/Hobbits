"""
Автоматизированный интеграционный тест:
1. Проверка API афиш мероприятий (создание, чтение, удаление)
2. Проверка подачи диплома через Telegram-бот и мгновенного появления на сайте
3. Проверка работы фонового HTTP API сервера
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
import threading

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from server import load_db, save_db, PortalHandler, PORT
from http.server import ThreadingHTTPServer
import bot.telegram_bot as bot_module

def run_tests():
    print("=" * 60)
    print("🧪 ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ: АФИШИ + ТЕЛЕГРАМ-БОТ + API")
    print("=" * 60)

    # 1. Запуск тестового HTTP-сервера на порту 8000 (если не запущен)
    server_started = False
    try:
        test_server = ThreadingHTTPServer(("0.0.0.0", 8000), PortalHandler)
        t = threading.Thread(target=test_server.serve_forever, daemon=True)
        t.start()
        server_started = True
        print("✓ Локальный API сервер успешно запущен на порту 8000")
    except OSError:
        print("✓ Порт 8000 уже активен (сервер уже работает)")

    time.sleep(0.5)

    # 2. Проверка GET /api/db
    req = urllib.request.Request("http://localhost:8000/api/db")
    with urllib.request.urlopen(req, timeout=5) as resp:
        db_data = json.loads(resp.read().decode("utf-8"))
    assert "users" in db_data, "Нет пользователей в ответе /api/db"
    assert "achievements" in db_data, "Нет достижений в ответе /api/db"
    assert "events" in db_data, "Нет афиш в ответе /api/db"
    print(f"✓ GET /api/db успешен. Найдено афиш: {len(db_data['events'])}, достижений: {len(db_data['achievements'])}")

    # 3. Проверка GET /api/events
    req = urllib.request.Request("http://localhost:8000/api/events")
    with urllib.request.urlopen(req, timeout=5) as resp:
        events = json.loads(resp.read().decode("utf-8"))
    assert isinstance(events, list), "Ответ /api/events не является списком"
    print(f"✓ GET /api/events успешен. Текущие афиши: {[e['title'] for e in events]}")

    # 4. Проверка создания новой афиши админом (POST /api/events)
    test_event_payload = {
        "title": "Тестовый Хакатон Лицея 2026",
        "category": "informatics",
        "level": "Региональный",
        "date": "2026-11-25",
        "place": "ИТ-Парк Казань",
        "pointsAward": "до +45 баллов",
        "badgeText": "ХАКАТОН",
        "description": "Тестовое соревнование по созданию цифровых сервисов",
        "registrationLink": "https://t.me/HobbitBot"
    }
    post_data = json.dumps(test_event_payload).encode("utf-8")
    req = urllib.request.Request("http://localhost:8000/api/events", data=post_data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        created_ev = json.loads(resp.read().decode("utf-8"))
    assert created_ev["title"] == test_event_payload["title"], "Название афиши не совпадает"
    created_id = created_ev["id"]
    print(f"✓ POST /api/events успешен. Создана афиша: id={created_id}, title='{created_ev['title']}'")

    # 5. Проверка подачи диплома через Telegram-бот
    # Симулируем авторизацию ученика user-1 (Гумеров Раиль)
    test_chat_id = 999888777
    s_data = bot_module.load_sessions()
    s_data["user_sessions"][str(test_chat_id)] = {
        "userId": "user-1",
        "name": "Гумеров Раиль",
        "class": "9Б",
        "login": "Rail"
    }
    bot_module.save_sessions(s_data)
    
    # Шаг 1: /submit
    bot_module.process_message({"chat": {"id": test_chat_id}, "text": "/submit", "from": {"first_name": "Раиль"}})
    
    # Шаг 2: Название олимпиады
    ach_test_title = f"ВсОШ по физике Автотест {int(time.time())}"
    bot_module.process_message({"chat": {"id": test_chat_id}, "text": ach_test_title, "from": {"first_name": "Раиль"}})
    
    # Шаг 3: Выбор категории (sub_cat_physics)
    bot_module.process_callback_query({"id": "cq1", "message": {"chat": {"id": test_chat_id}}, "data": "sub_cat_physics", "from": {"first_name": "Раиль"}})
    
    # Шаг 4: Выбор уровня (sub_lvl_region)
    bot_module.process_callback_query({"id": "cq2", "message": {"chat": {"id": test_chat_id}}, "data": "sub_lvl_region", "from": {"first_name": "Раиль"}})
    
    # Шаг 5: Выбор результата (sub_res_winner)
    bot_module.process_callback_query({"id": "cq3", "message": {"chat": {"id": test_chat_id}}, "data": "sub_res_winner", "from": {"first_name": "Раиль"}})

    # 6. Проверяем, что поданная заявка мгновенно появилась в базе данных и видна через /api/db для сайта!
    req = urllib.request.Request("http://localhost:8000/api/db")
    with urllib.request.urlopen(req, timeout=5) as resp:
        updated_db = json.loads(resp.read().decode("utf-8"))
    
    found_ach = next((a for a in updated_db.get("achievements", []) if a.get("title") == ach_test_title), None)
    assert found_ach is not None, f"Заявка '{ach_test_title}' не найдена в /api/db после подачи через бота!"
    assert found_ach["status"] == "pending", f"Статус заявки не pending: {found_ach['status']}"
    assert found_ach["userId"] == "user-1", f"userId не совпадает: {found_ach['userId']}"
    assert found_ach["points"] == 35, f"Баллы за регионального победителя не 35: {found_ach['points']}"
    print(f"✓ Заявка из Telegram-бота мгновенно появилась на сервере API: id={found_ach['id']}, статус={found_ach['status']}, баллы=+{found_ach['points']}")

    # 7. Проверка команды бота «📢 Афиша олимпиад»
    events_text, events_markup = bot_module.format_events_message()
    assert "АФИША МЕРОПРИЯТИЙ" in events_text, "Заголовок афиши отсутствует в боте"
    assert "Тестовый Хакатон Лицея 2026" in events_text, "Созданная афиша не отобразилась в боте!"
    print("✓ Telegram-бот успешно отображает афиши мероприятий из единой базы!")

    # 8. Проверка удаления афиши (DELETE /api/events?id=...)
    req = urllib.request.Request(f"http://localhost:8000/api/events?id={created_id}", method="DELETE")
    with urllib.request.urlopen(req, timeout=5) as resp:
        del_res = json.loads(resp.read().decode("utf-8"))
    assert del_res.get("deleted") is True, f"Удаление афиши не удалось: {del_res}"
    print(f"✓ DELETE /api/events успешен. Тестовая афиша id={created_id} удалена.")

    # Удаляем тестовое достижение
    updated_db["achievements"] = [a for a in updated_db["achievements"] if a.get("title") != ach_test_title]
    save_db(updated_db)
    print("✓ Тестовое достижение очищено из базы.")

    print("\n" + "=" * 60)
    print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! СИНХРОНИЗАЦИЯ РАБОТАЕТ БЕЗУПРЕЧНО!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
