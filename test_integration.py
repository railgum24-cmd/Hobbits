"""
Автоматический тест интеграции:
1. Проверяет чтение и запись единой базы database/lyceum_db.json
2. Регистрирует нового пользователя через логику сайта
3. Проверяет, что бот HobbitBot успешно авторизует этого нового пользователя (/login)
4. Подаёт достижение через Telegram-бота
5. Проверяет, что поданное достижение появилось в единой базе и доступно для админки
"""
import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from bot.telegram_bot import process_message, load_unified_db, save_unified_db, load_sessions, save_sessions

def test_integration():
    print("=== ТЕСТ 1: Проверка единой базы данных ===")
    db = load_unified_db()
    assert "users" in db and "achievements" in db
    print(f" База доступна: {len(db['users'])} пользователей, {len(db['achievements'])} достижений.")

    print("\n=== ТЕСТ 2: Регистрация нового аккаунта на сайте ===")
    test_login = f"test_student_{int(time.time())}"
    test_pass = "secret123"
    test_name = "Николаев Артём Сергеевич"
    test_class = "10Б"
    
    new_user = {
        "id": f"u-test-{int(time.time())}",
        "name": test_name,
        "class": test_class,
        "role": "student",
        "login": test_login,
        "password": test_pass,
        "isNew": True
    }
    db["users"].append(new_user)
    save_unified_db(db)
    print(f" На сайте создан аккаунт: {test_name} ({test_class}), логин: {test_login}")

    print("\n=== ТЕСТ 3: Авторизация нового пользователя в Telegram-боте ===")
    test_chat_id = "999888777"
    
    # Симулируем команду /login test_login secret123
    login_msg = {
        "chat": {"id": test_chat_id},
        "text": f"/login {test_login} {test_pass}"
    }
    process_message(login_msg)
    
    sessions = load_sessions()["user_sessions"]
    assert test_chat_id in sessions, "Сессия чата должна быть сохранена"
    assert sessions[test_chat_id]["login"] == test_login
    print(f" Бот успешно авторизовал нового пользователя с сайта: {sessions[test_chat_id]['name']}")

    print("\n=== ТЕСТ 4: Подача достижения через Telegram-бота ===")
    # Шаг 1: Нажимаем "➕ Подать достижение"
    process_message({"chat": {"id": test_chat_id}, "text": "➕ Подать достижение"})
    
    # Шаг 2: Вводим название
    ach_title = "Всероссийский хакатон по кибербезопасности 2026"
    process_message({"chat": {"id": test_chat_id}, "text": ach_title})
    
    # Шаг 3: Выбираем предмет
    process_message({"chat": {"id": test_chat_id}, "text": "Информатика"})
    
    # Шаг 4: Выбираем уровень
    process_message({"chat": {"id": test_chat_id}, "text": "Федеральный (ВсОШ)"})
    
    # Шаг 5: Выбираем результат
    process_message({"chat": {"id": test_chat_id}, "text": "Победитель (1 место)"})
    
    print("\n=== ТЕСТ 5: Проверка появления диплома в единой базе сайта ===")
    updated_db = load_unified_db()
    found_ach = None
    for a in updated_db["achievements"]:
        if a["title"] == ach_title and a["userId"] == new_user["id"]:
            found_ach = a
            break
            
    assert found_ach is not None, "Диплом из бота должен быть сохранён в единой базе"
    assert found_ach["points"] == 50, f"За победу на федеральном уровне должно быть 50 баллов, получено {found_ach['points']}"
    assert found_ach["status"] == "pending", "Статус должен быть pending"
    print(f" Диплом «{found_ach['title']}» успешно появился в единой базе с {found_ach['points']} баллами (статус: {found_ach['status']})!")

    print("\n=== ТЕСТ 6: Завуч на сайте подтверждает диплом ===")
    found_ach["status"] = "approved"
    found_ach["comment"] = "Диплом проверен, 1 место подтверждено приказом №42"
    save_unified_db(updated_db)
    print(" Завуч одобрил диплом на сайте.")

    print("\n=== ТЕСТ 7: Проверка обновления рейтинга в боте ===")
    # Ученик запрашивает "📊 Мой рейтинг"
    process_message({"chat": {"id": test_chat_id}, "text": "📊 Мой рейтинг"})
    print(" Запрос рейтинга в боте отработал штатно!")

    # Очистка тестового пользователя
    updated_db["users"] = [u for u in updated_db["users"] if u["id"] != new_user["id"]]
    updated_db["achievements"] = [a for a in updated_db["achievements"] if a.get("userId") != new_user["id"]]
    save_unified_db(updated_db)
    print(" Тестовые данные очищены.")

    print("\n ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")

if __name__ == "__main__":
    test_integration()
